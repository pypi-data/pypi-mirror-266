#!/usr/bin/python3

#    EPICS SCPI Control Plane Integration -- Access SCPI devices.
#    Copyright (C) 2022 Florin Boariu and Matthias Roessle.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import pyvisa
import logging
import parse
import asyncio

logger = logging.getLogger(__name__)

from os import environ as env

class PropertyTimeoutError(RuntimeError):
    pass

class PropertyTimeoutRetry(RuntimeError):
    pass


class PropertyNodeSlot:
        ''' Wrapper to access a sub-structure of a PropertyNode value.

        See documentation to `PropertyNode` about what it does and how it's
        structure first.

        Some property nodes have multiple values -- "arrays". When the
        parsing format strings contain named values (e.g. "{foo:d}, {bar:s}"),
        we're using the designated variable names to expose the corresponding
        part of `parse.Result` as a read-only namespace object.

        This class implements one specific part of this functionality by
        restricting the `.get()` answer to a specific key. The writing
        ability is removed.

        FIXME: not sure this is a good idea. This would enable higher-layers
        to query one property(-slot) at a time when they're actually meant
        to be queried together. This could induce consistency issues.
        '''

        def __init__(self, node, slot):
            self._node = node
            self._slot = slot

        def get(self):
            data = self._node.get()
            if not isinstance(data, parser.Result):
                raise RuntimeError(f'Expected a parser result for {self._node.name},'
                                   ' got {data} instead')
            return result[self._slot]

        def __call__(self):
            return self.get()


class PropertyNode(object):
    '''
    The SCPI protocol is in many details a hierachical
    one -- commands are being built by extending on a base string
    with sub-branches. For instance:

      - `FUNC <name>` enables a specific function, but
        `FUNC:<name> <param>` sets a specific parameter
         of that function.

      - `BURST:STATE` sets the burst state, `BURST:NCYCLES` sets
        the number of burst cycles, etc.

    This object handles pyVISA communication for one particular SCPI-like
    property. "SCPI-like" here means that the structure is the same as
    with SCPI, but we allow for syntactic differences to be able to cover
    a broader set of pyVISA dialogue (for instance as used in Huber motion
    controllers, which will happily communicate via TCP/IP, USB or GPIB
    via pyVISA, but with a language that differs slightly from SCPI.
    
    For instance, this initializes a property called "burst" on the
    pyVISA device `kdev`:
    ```
       In [1]: bc = PropertyNode(kdev, 'burst:ncycles')
    ```

    Whether it's case sensitive or not ("burst" vs "BURST") is a matter
    of what the device is willing to accept. The underlying Python code
    retains string case.

    Setting and reading properties is done via the functions `.set()` and
    `.get()`, or optionally using the `.__call__()` operator. For instance,
    any of these lines would send the string "off" to be set as
    the number of burst cycles property:
    
    ```
       In [2]: bc("12")

       In [3]: bc.set("12")
    ```

    Reading, conversely:
    
    ```
       In [4]: bc
       Out[4]: "12"

       In [5]: bc.get()
       Out[5]: "12"
    ```

    So far these have been simple examples for simple values. The
    complications arise in two classes:

      - Data conversion: pyVISA is all about strings -- data is read
        and written as strings. Any higher-level data format (integers,
        doubles, booleans etc) need to be done by Python. In addition,
        some commands accept boolean-state strings ("ON" / "OFF"),
        but return integer states (0 / 1). We want those translated
        to and from proper boolean Python data (True / False), for
        instance.

      - Data is not always scalar -- SCPI allows for multiple-parameter
        commands (e.g. "SET:STUFF 1,2,3,4"). He we want multiple things.
        For one, we want to be able to set multiple parameters at once,
        e.g. by using lists or arrays (`.set(1, 2, 3, 4)` or `.set([...])`.
        For another, we want to be able to refer at *one* specific
        parameter out of several (e.g. `PropertyNode(..., 'stuff').set(3)`
        to set and query *only* the 3rd parameter of 'set:stuff').

        On top of all of this, the considerations for data conversion
        (see the first point) also apply.

    This would return the result of the `"BURST:STATE OFF" command.
    Any strings sent are converted to upper case. Any boolean parameters
    (True/False) are converted to "ON" / "OFF".

    In returning values, the class tries first to convert "ON"/"OFF" to
    boolean, than any integer values in might encounter, then floating
    points. If all fail, a regular Python string is returned.

    The specific functions `get()` and `set()` act directly on the root
    command, e.g. this would result in setting the function "FUNC SIN",
    then requesting the function name again (`FUNC?`):
    ```
       p = PropertyBranch(kdev, 'func`)
       p("sin")
       p ## --> 'SIN'
    ```

    The functions `enable()` and `disable()` are shortcuts for `set("ON")`
    and `set("OFF")`, respectively.

    '''

    def __init__(self,
                 dev,
                 name,
                 lock=None,
                 nxerror=None,
                 is_root_subclass=False,
                 
                 getter_fmt="{name:s}?",
                 setter_fmt="{name:s} {data:s}",
                 branch_fmt="{root:s}:{node:s}",
                 
                 unwrap="auto", ## always, never, auto
                 cast="auto", ## auto, none, {...}, lambda, ({...}, lambda, ...)
                 pack="auto", ## auto, none, {...}, lambda, ({...}, lambda, ...)
                 
                 separator=",",
                 ):
        
        ''' Initializes access to one specific property node.

        Only `dev`, `name`, `nxerror` and `is_root_subclass` are actually
        processed here, all other parameters serve as defaults for the
        getter / setter functions `.get()`, respectively `.set()`, or the
        `__call__` operator.

        Args:
            dev: The VISA resource (device) to use for communication. We
              defer all communication to that device, and pass this on
              to sub-properties, if necessary.
        
            name: The full string for this SCPI property node. Typical
              SCPI properties are key names (as strings). They can be
              hieararchical, in which case the string consists of
              sections delimited by a character, e.g. ":".
              The name here is specified without the trailing separator
              (e.g. `BURST` or `FUNC`, instead of `BURST:` or `FUNC:`).

            lock: `asyncio.lock.Lock` object to use for protecting async
              access to the device. If not specified, one is created. In
              that case, no other `PropertyNode` should access the same
              VISA device.

            nxerror: If this is anything other than `None`,
              the property is read at least once, and `nxerror` is raised
              if the underlying subsystem fails to fetch a value (...typically
              raises `pyvisa.VisaIOError` instead).
              If this is set to `None` (the default), then no check is performed,
              and this class may be erronously initialized, meaning that
              it will raise an error when first used (e.g. on first attempt
              to read or write the property value).

            is_root_subclass: This is mainly intended for subclassing. For
              the default setting (`False`), the class displays behaviour of
              a "normal" node in a tree of properties. This means in particular
              that subnodes (e.g. when invoking `.branch()` or `__getattr__()`)
              will have the same type as this instance.
        
              When this is `True`, the class will instantiate subnodes using
              the type of its superclass instead of its own.

              This behavior can be further tuned / overridden by explicitly
              setting the `._subnode_class` property to a data type to use
              as subnode type.

            getter_fmt: Format for building the getter query. The format
              keyword `name` will be used for the full property
              specification. Will be used by the `.get(...)` function.
              If this is set to `None`, then the property is considered
              write-only and the getter will fail (FIXME: how?)

            setter_fmt: Analogous, format for building the property setter
              query. Keys `{name}` and `{data}` may be used for the
              property name, respectively the data string (!).
              Unnamed formatters (`{}...`) can be used for the argument
              list, corresponding to their data type, as passed to `.set(...)`.
              If this is set to `None`, the property is considered read-only.

           branch_fmt: Indication of how to build sub-branches, given a base
              property name (us) and a subnode (specified). This is used on
              `.__getattr__()`, i.e. when a class attribute is requested
              which doesn't exist, and is then interpreted as a sub-branch.

           unwrap: Defines the unwrapping strategy or procedure. "Unwrapping"
              is the act of transforming device responses packed in arrays
              into individual items.
        
              `unwrap` can either be a callable, or a strategy keyword
              "always", "single", "never", "auto" (the default).

              If `unwrap` is a callable, then it is expected to be a
              single-argument function which takes the response (as string)
              and returns an unwrapped tuple of values (as strings).
              The contents of the `separator` argument (see below) are
              ignored.

              If it's one of the strategy keywords, then the unwrapping
              is an algorithm supplied by default, which is essentially
              variations of a `str.split(separator)` -- depending on the
              strategy setting:

                - "never" doesn't do any kind of array unwrapping, data is
                  returned as-is, as a string. `None` is the same as "never".

                - "single" is similar to "never", except that the value is
                  *required* to always be a single value; if it's an array
                  (i.e. it contains the `separator` substring anywhere), the
                  getter will raise `ValueError.
        
                - with strategy "always", the value received from the device
                  is always assumed to be in array from, and a tuple is
                  returned -- containing a single value (`(val,)`) if there
                  was no array. The array items are strings, stripped by
                  leading and trailing white spaces.
        
                - with "auto", the unwrapper behaves as "single" if there is
                  no separator, or as "always" otherwise. This measn it
                  returns single values directly, and arrays as tuples.

           cast: Determines how a (every) single value is transformed before
              returning. Can be either "auto", "none", a callable, a format
              string, or a tuple containing any of the previous four for every
              of its elements.

              For "none", or `None` no parsing or casting is done -- the
              plain string is retained.

              A callable (e.g. a lambda expression) is expected to take the
              value as its single argument and return a transformed value to
              replace it.

              A format string (`{...}`) is applied to the data and the result
              is returned. Note that this allows to parse the data into
              complex data containers like dictionaries.

              "auto" offers a simple an internal algorithm, whereby the data
              is first interpreted as `int`, then `float`, then returned
              as `str` if all else failed.

              If a tuple is specified, it's required to have the same number
              of elements as the data array, and every tuple element is
              applied to its corresponding array value.

            pack: The opposite of `cast`, determines how every single value
              is to be transformed into a string before sending to the device.
              Possible settings are "auto", "none", a callable, a format string,
              or a tuple which's elements are one of the above. The meaning of
              each setting is mostly  similar to `cast`: a callable is called to
              translate, a format string is used for formatting, and the tuple
              elemetns are used for each value element.

              In a necessary adaptation, "none" or `None` uses the type's
              built-in string casting (`str(...)` -- *some* transformation
              always needs to take place for non-string data), and "auto"
              looks up the corresponding `cast` entry for a format string,
              so that the same format string needs to be specified only once.

            separator: Character or string to use for separating individual
              values of an array. This is used for both incoming and outgoing
              data. Defaults to `","` which turns out to be a sensible setting
              for most SCPI-esque protocols.
              
        '''

        # check if the attribute exists, raise an nxerror otherwise
        self.name  = name
        self.kdev  = dev

        # parser_conf is the configuration base, and it is what we will pass on
        # to sub-properties; parser_ovrd is initially the same as parser_conf,
        # but it is updated by the named parameters of __init__, and it will
        # only be used internally.
        self.parser_conf = {
            'getter_fmt': getter_fmt,
            'setter_fmt': setter_fmt,
            'branch_fmt': branch_fmt,
            'cast': cast,
            'pack': pack,
            'separator': separator,
            'unwrap': unwrap
        }
        
        self.parser_ovrd = self.parser_conf.copy()

        self.__check_store_notexists(nxerror)
        
        self.__propcache = {}

        # What kind of type should we use in __getattr__(), when we're required
        # to descend down subtrees of properties?
        # Generally, we want this to be the same as us (i.e. `PropertyNode`,
        # or a subclass thereof if we're subclassing). But sometimes we don't,
        # e.g. when subclassing explicitly to create top-level (root) nodes
        # (MagicVisaChat, for instance). In that case, the subclass will have
        # to override this method.
        self._subnode_class = self.__class__ \
            if not is_root_subclass \
            else self.__class__.__base__

        logger.debug('Subnode class for <%s>: %r' % (self.name, self._subnode_class))

        if lock is None:
            self.device_lock = asyncio.Lock()
            logger.debug(f'Async lock created: {self.device_lock}')
        else:
            logger.debug(f'Reusing lock: {lock}')
            self.device_lock = lock


    def __check_store_notexists(self, nxerror):
        '''
        If `nxerror` is not None, raises `nxerror` if the property can't be read.
        '''
        if nxerror is not None:
            try:
                kdev.read()
            except pyvisa.VisaIOError:
                raise nxerror

        self.__nxerror = nxerror


    def __unwrap_proc(self, unwrap, separator):
        # need this for unwrap "single"
        def _local_raise(x):
            raise x

        return unwrap if hasattr(unwrap, "__call__") else {
            'always': lambda s: tuple([i.strip() for i in \
                                       s.split(separator)]),
            'never': lambda s: s,

            None: lambda s: s,

            'auto': lambda s: s if -1 == s.find(separator)
            else tuple([i.strip() for i in s.split(separator)]),

            'single': lambda s: s if -1 == s.find(separator)
            else _local_raise (ValueError(f'{s} is expected to be a single value'))
        }[unwrap]


    def can_get(self):
        ''' Returns True if the node has a getter capability defined.
        
        Even if this returns `False`, a call to `.get()` can still be successful
        if the `fmt` parameter of `.get()` is explicitly specified.
        '''
        return self.parser_ovrd['getter_fmt'] is not None

    def can_set(self):
        ''' Returns True if the node has a setter capability.
        
        Even if this returns `False`, a call to `.set()` can still be successful
        if the `fmt` parameter of `.set()` is explicitly specified.
        '''
        return self.parser_ovrd['setter_fmt'] is not None

    
    def local_override(self, key, value):
        ''' Sets `.parser_ovrd` key to `value`.

        This effectively changes the behavior of the parser for this Node object
        only. Changes will not be propagated to sub-nodes (those will inherit
        the initial parser settings of `.__init__()`.
        '''
        if key not in self.parser_ovrd is None:
            raise RuntimeError(f'No parser-override property "{key}"')
        self.parser_ovrd[key] = value


    def convert_from_device(self, s, cast=None):
        ''' Converts an SCPI value string into a Python value according to `cast`. '''
        
        if cast == "auto":
            try:
                return int(s)
            except (TypeError, ValueError):
                try:
                    return float(s)
                except (TypeError, ValueError):
                    return s

        elif cast in [None, "none"]:
            return s
                
        elif hasattr(cast, "__call__"):
            return cast(s)
        
        elif isinstance(cast, str):
            return parse.parse(cast, s)

        raise ValueError(f'Cannot parse {s} as {cast}')


    def convert_to_device(self, val, pack=None):
        ''' Converts a Python type into a string suitable for an SCPI device. '''

        if pack is None or pack in [ "", "auto", "none" ]:
            return str(val)

        elif hasattr(pack, "__call__"):
            return pack(val)

        else:
            return pack.format(val)

        raise RuntimeError(f"Don't know how to format {val} with {pack}")


    def read(self, *args, **kw):
        '''
        Wrapper around `self.kdev.read()`. This is typically the "nice" PyVISA
        `.read()` version (now), but might be changed in the future to mean
        whatever we think is most appropriate for `MagicScpi`.
        '''
        r = self.kdev.read(*args, **kw)
        logger.debug(f'<< {r}')
        return r


    def write(self, cmd, *args, **kw):
        '''
        Writes data to the underlying VISA device. This is currently a wrapper
        around `self.kdev.write()`, which in turn goes directly to PyVISA device's
        `.write()` function. But in the future it will be changed to mean whatever
        we think is most appropriate for this class.
        '''
        logger.debug(f'>> {cmd}')
        nr = self.kdev.write(cmd, *args, **kw)
        assert nr == len(cmd)+len(self.kdev.write_termination)


    def query(self, qstr):
        '''
        Executes a query on self.kdev
        '''
        logger.debug(f'>> {qstr}')
        r = self.kdev.query(qstr)
        logger.debug(f'<< {r}')
        return r


    async def async_read(self, end="auto", split=None, timeout="auto",
                         lock=True, granularity=0.001, encoding='utf-8',
                         min_wait_bytes=0,
                         poll_timeout=0,
                         max_bytes_poll=None):
        '''
        Async version of `.read()`.

        As far as PyVISA is concerned, this works on a "high level" -- i.e. we're
        actually setting the timeout value of the device to 0, and switching to
        raw reading until we either hit the end-of-line marker, or a hard timeout
        specifically passed on to `.async_read()`.

        Reading is difficult business: we actually don't *know* when to stop receiving
        data. There are several posibilities:
        
          - When a specific marker is reached (e.g. end-of-line, or end-of-message)

          - When no more data is arriving within a reasonable time frame (timeout).

          - When a specific number of items is read (e.g. lines)

        The last item is really just a generalization of the first, and is primarily
        of interest when reading full messages (e.g. the reply to a query command).
        We'll be ignoring it here and will be dealing with it primarily in
        `.async_query()` instead.

        There's no generic method of how to determine the end of a read cycle
        -- PyVISA's original `.read()` is strongly line-oriented; but all of its
        other `.read_...()` functions are a lot less straight-forward for this
        specific reason.
        
        Args:

            end: a.k.a. "end-of-message" -- if something other than `None`, this
              single-handedly ends reception (i.e. read buffer is returned
              immediately). If this is set to `"auto"`, then the device's
              `.read_termination` is used.

            split: if not `None`, then the result will be split by the specified
              character and the resulting list will be returned. White spaces for
              each item are stripped.

            timeout: number of seconds to wait since the last transmission until
              no more data is expected. This is `None` by default. The behavior
              then depends on `separator`: if the latter is set to anything
              other than the empty string, then `timeout=None` will default
              to the `.timeout` device property. Otherwise it will block forever,
              i.e. until a separator or `eom` is encountered.

            lock: if set to `True`, an internaly asyncio lock is used for access
              to the PyVISA resource. If set to `False` or `None`, no lock is used
              (you _really_ should know what you're doing then!). If it's anything
              else, it's assumed to be a lock object that can be used with
              `with ...:`.

            granularity: how long to sleep between read attempts
              (defaults to 0.001 seconds).

            encoding: how to encode/decode binary data to/from text. Default is 'utf-8'.

            min_wait_bytes: minimum number of bytes to wait for in an interface
              before a readout is attempted. This is to circumvent broken equipment
              and pyVISA code that will break when attempting to read with a timeout
              of 0.

            poll_timeout: polling timeout to use instead of 0, to facilitate "async"
              readout. Note that true "async" readout is only available when poll_timeout
              is 0 (default), but there is broken equipment / pyVISA code that
              will swallow bytes when it encounters timeouts. This is in seconds.

            max_bytes_poll: how many bytes to attempt to read per polling round.
              Default (`None`) will use `.read_raw()` from pyVISA and will read
              whatever is available. That works well e.g. with TCP/IP instruments.
              If this is a numberical value, then `.read_bytes()` will be used
              instead. Set this to 1 for safe reading e.g. of serial devices.

        Returns: A list with either strings or objects, one for each line encountered:
          if `parser` is `None`, then a string is returned for each line
          encountered. Otherwise it's the object returned by the `parser` callable.
        '''

        if lock in (None, False):
            # fake lock used only here, should not block
            lock = asyncio.Lock()

        if lock in ("auto", True):
            lock = self.device_lock

        data = b''
        mark = time.time()

        # _end is a bytes() version of 'end'
        if end == "auto":
            _end = self.kdev.read_termination.encode(encoding)        
        elif end is not None:
            _end = end.encode(encoding)
        else:
            _end = None
            
        if timeout == "auto":
            timeout = self.kdev.timeout*0.001            

        save_timeout = self.kdev.timeout
        save_term = self.kdev.read_termination

        #print(" r: line end:", _end)
        #print(" r: timeout:", timeout)

        async with lock:
            while True:
                try:
                    self.kdev.timeout = poll_timeout*1000.0

                    try:
                        if hasattr(self.kdev, "bytes_in_buffer") and \
                           (self.kdev.bytes_in_buffer < min_wait_bytes):
                            raise PropertyTimeoutRetry()
                    except TypeError as e:
                        logger.error(str(e))
                        raise RuntimeError(f'This is a bug in pyvisa-sim that prevents '
                                           f'you from using ASRL devices with async-SCPI')

                    if max_bytes_poll is not None and max_bytes_poll > 0:
                        r = self.kdev.read_bytes(1)
                    else:
                        r = self.kdev.read_raw()
                    #logger.debug(f'Have {len(r)} bytes: {r}')
                    data += r

                    #print(f" r: testing data {data} against end {_end}")
                    if (_end is not None) and data[-len(_end):] == _end:
                        data = data[:-len(_end)]
                        break

                    mark = time.time()

                except (pyvisa.errors.VisaIOError, PropertyTimeoutRetry) as e:
                    elapsed = time.time() - mark
                    if (timeout is not None) and (elapsed > timeout):
                        if len(data) > 0:
                            break
                        raise PropertyTimeoutError(str(e))
                    else:
                        # short timeout, not finished yet
                        await asyncio.sleep(granularity)
                        continue

                finally:
                    #pass
                    self.kdev.timeout = save_timeout

            if split is not None:
                return tuple([i.strip() for i in data.decode(encoding).split(split)])
            else:
                return data.decode(encoding).strip()


    async def async_write(self, cmd, *args, lock=True, **kw):
        '''
        "Async version" of .write(). For all we know, writes are always non-blocking,
        so we just assume this magically works...
        '''
        if lock in (None, False):
            lock = asyncio.Lock() # fake lock

        if lock in ("auto", True):
            lock = self.device_lock

        async with lock:
            nr = self.kdev.write(cmd, *args, **kw)
            assert nr == len(cmd)+len(self.kdev.write_termination)
            return nr


    async def async_query(self,
                          qstr,
                          lines=1,
                          ignore_lines=0,
                          line_end=None,
                          end="auto",
                          parser=None,
                          lock=True,
                          encoding='utf-8',
                          **read_args):
        '''
        Executes an async query on `self.kdev` and returns the answer.

        Like `.async_read()`, the logic for detemrining when a message from
        the device is finished is a bit convoluted. In addition to the typical
        `.async_read()` parameters (`end`, `timeout`) here we also have
        to consider that the message may be multi-line.
        
        Some very, *very* brain-damaged protocols (looking at you, Huber!)
        deviate significatnly from the standard case (SCPI). For instance:
        by replying with a single-line, a single-line with multiple items,
        multiple-lines, multiple-lines with multiple-items, or mult-lines
        with a specific number of nonsensical lines ("comments") that are
        to be ignored. Yay! m(

        The logic is therefore this:
        
          - the `end` parameter here is expected to demark the end of the
            *message*, i.e. the full reply of the VISA device to the command.

          - `line_end` demarks the end of a line, and never the end of a
            message (unless we only expect 1 line). If this is `"auto"`,
            we use the value of `self.kdev.read_termination`. If set to `None`,
            we ignore any line-based logic and wait only for `end` or `timeout`.

          - if `end` is not defined, then the number of lines is to determine
            the end of messaage. We need to know in advance how many lines
            we're expecting (`lines`, `ignore_lines`), and we'll wait for
            all of them...

          - ...up to `timeout` seconds. If this is `None`, we'll wait forever.
            If this is `"auto"`, we'll take the value of `self.kdev.timeout`
            (ACHTUNG, that one is in milliseconds! We do the transformation.)

        Args:
            end: ends reading if this is encountered anywhere in the message
              *after* splitting the message in lines. If set to `None`, there
              is no dedicated end-of-message string, and reading continues
              until the desired number of lines is extracted (`lines` + `ignore_lines`),
              or `timeout` is surpassed. Setting this to the empty string `""`
              will be treated as a special case: the reading will end when an
              empty line is received.
        
            lines: if specified, this number of lines is retrieved. Defaults to 1.
              If this is set to `None`, then an infinite number of lines
              is read, until `end` is encountered as part of the message.

            ignore_lines: if this is set to anything larger than 0, then an additional
              number of lines is expected before the message is completed. However,
              only the first `lines` lines are returned.

            line_end: this is the end-of-line separator. If set to `None`,
              then line-based logic (`lines` or `ignore_lines`) is ignored completely
              and only `end` or `timeout` can end transmission. If set to `"auto"`,
              or the empty string, then the device's `.read_termination` string is used.

            parser: this is expected to be a callable, or an enumerable. If it is
              a callable, it takes a single line (or "item") as argument and expects
              to return a data type. If it is an enumerable, each item is used to
              parse the corresponding line.

            lock: asyncio lock object to use for device access synchronisation.
              Don't use unless you know what you're doing.

            encoding: how to decode the message. Defaults to 'utf-8'

        Returns: A list with each line, filtered through `parse()`.
        '''

        if lock in (None, False):
            lock = asyncio.Lock() # fake lock

        if lock in ("auto", True):
            lock = self.device_lock

        # parser is either:
        #  - a callable
        #  - `None` (in which case we use lambda x: x),
        #  - an iterable;
        # We transform all of that to an iterable, which we'll use
        # cyclically.
        parser_list = (parser,) if hasattr(parser, "__call__") else \
                parser if parser is not None \
                else (lambda x: x,)

        # preparing read-args dictionary. Some parameters we have to override.
        r_args = read_args.copy()
        r_args['lock'] = False
        if 'split' in r_args:
                del r_args['split']

        if end == "auto":
            end = self.kdev.read_termination

        class PropertyQueryDone(Exception):
                pass

        async with lock:
            await self.async_write(qstr, lock=False)
            await asyncio.sleep(self.kdev.query_delay)

            data = []
            parse_errors = []

            cur_line = 0
            parser_iter = iter(parser_list)
            
            while cur_line < lines+ignore_lines:
                # On multiline messages, a single read operation is not guaranteed
                # to end on a line boundary; we try to receive as close to single-lines
                # as possible (which is why we specify `end==line_end`), but we also
                # want to split the message into its individual parts of there is
                # more than one line waiting in the buffer (`split=line_end`).
                # Generally, this means that `result` will be a list, and it will
                # possibly contain more than one line.
                try:
                    splitter = (line_end or end)

                    # lock=... has already been passed in r_args
                    result = await self.async_read(end=splitter, split=splitter, **r_args)
                    
                    # Taking the lines one by one, parsing, checking for end-of-transmission.
                    # Note that if split=None, .async_read() will return a single line instead
                    # of a list!
                    for r in (result if splitter is not None else (result,)):

                        # determine parser function (wrap-over iteration)
                        try:
                            parser_func = next(parser_iter)
                        except StopIteration:
                            parser_iter = iter(parser_list)
                            parser_func = next(parser_iter)

                        # end-of-message if 'end' is specified and part of the message
                        if (end == "" and end == r) or ((end is not None) and (end in r)):
                            raise PropertyQueryDone()

                        # keep the line
                        if (lines is None) or (cur_line < lines):
                            d = parser_func(r)
                            if d is None:
                                parse_errors.append(f'{cmmd}: cannot parse {r}')
                            else:
                                data.append(d)

                        # cound the line (note that ignored lines are also counted!)
                        cur_line += 1

                        # end-of-message if we have all lines
                        if (line_end is not None) and \
                           (lines is not None) and \
                           (cur_line >= lines+ignore_lines):
                            raise PropertyQueryDone()


                except PropertyTimeoutError:
                    if (line_end is not None) and (end is not None):
                        raise
                    break ## "normal" exit 
            
                except PropertyQueryDone:
                    break

            if len(parse_errors) > 0:
                for e in parse_errors:
                    logger.error(e)
                raise RuntimeError(f'Error parsing result for: {cmd}')

            if line_end is not None:
                return tuple(data)
            else:
                if len(data) != 1:
                    logger.error(f'Expected 1 line, got {len(data)} lines')
                    raise RuntimeError(f'Expected 1 line, got {len(data)} lines')
                return next(iter(data))


    def _get_prepare_query(self, getter_fmt=None, fmt=None):
        '''
        Helper for .get() and .async_get(): prepares the query string, the string.
        '''

        if len(self.name) == 0:
            raise RuntimeError('Root subclass cannot get value')

        if fmt is None:
            fmt = getter_fmt or self.parser_ovrd['getter_fmt']

        if fmt is None:
            raise RuntimeError(f'Property {self.name} is write-only')
            
        q = fmt.format(**{
            'name': self.name,
        })

        return q


    def _get_parse_reply(self, r, unwrap=None, cast="", separator=""):
        '''
        Helper for .get() and .async_get().
        Accepts a query reply in `r` and returns the proper answer as per
        .get() documentation.
        '''
        
        if separator == "":
            separator = self.parser_ovrd['separator']

        if unwrap is None:
            unwrap = self.parser_ovrd['unwrap']

        if cast == "":
            cast = self.parser_ovrd['cast']

        # catch a common error: we don't accept lists, we really
        # want this to be either tuples or useful values
        assert not isinstance(cast, list)

        if r is None:
            raise RuntimeError(f'Reply to getter query was "{r}". '
                               'This likely means no such property '
                               'exists for this device.')

        # array unwrap options: always, never, single, auto
        # note that cast can be a single value, or a tuple

        #if not hasattr(unwrap, "__call__"):
        #assert unwrap in ("always", "never", "single", "auto")

        # When parsing values, we want simple things to stay simple
        # (i.e. {} shoult return a single, usable value), but complex
        # things to be possible (i.e. '{name} and {} has {fruit}' to
        # return arrays, dictionaries, or parsing results)
        def select_parsed_value(result, default=None):
            
            if result is None:
                if default is None:
                    raise ValueError(f'Parse error')
                return default

            if not hasattr(result, "fixed"):
                return result
            
            if result.fixed is not None and result.named is None:
                return result.fixed[0] if len(result.fixed)==1 else result.fixed

            if result.fixed is None and result.named is not None:
                return result.named

            return result


        values = self.__unwrap_proc(unwrap,separator)(r)

        # return single value
        if not isinstance(values, tuple):
            assert not isinstance(cast, tuple)
            try:
                return select_parsed_value(self.convert_from_device(values, cast))
            except:
                logger.error(f'Cannot parse return string: "{values}"')
                raise

        # return tuple / array
        if not isinstance(cast, tuple):
            cast = (cast,)
            
        return tuple([
                select_parsed_value(self.convert_from_device(v, cast[i%len(cast)] )) \
                for i,v in enumerate(values)
        ])



    def get(self, unwrap=None, cast="", separator="", getter_fmt=None, fmt=None):
        ''' Executes a reading query on the pyVISA resource.

        Sends a parameter request formatted for querying (as specified by
        `getter_fmt` or its alias `fmt`), and returns the result, possibly
        processed as specified by the parameters `unwrap`, `cast` and
        `separator`.

        To understand processing, it's important to consider that all
        responses received from the device are strings. They represent
        either single values, which can be numerical (`int` or `float`),
        boolean (represented as 0 or 1, or as mutually exclusive strings
        like `"ON"` or `"OFF"`), or plain strings. Additionally, they can
        also be lists of parameters as strings (e.g. `"1,jinkies,OFF"`)
        of which each item, in turn, can be interpreted of a specific
        type.

        When the result is a list, then, `.get()` must obviously
        return a tuple of the individual items. But when it's a single
        value, there's a API-philosophical competition between returning
        what requires less boilerplate to work with (i.e. a single value,
        preferrably in its native Python format), or something that's
        more predictable for all cases (i.e.  a tuple with a single item
        in it).
        
        `unpack` and `cast` allow fine-tuning that preference.

        All arguments (`getter_fmt`, `cast`, `unpack` and `separator`)
        are set to defaults here which make them inherit their values
        from was specified in `.__init__()`. Please additionally look
        up their meaning in the documentation for `__init__()` above.
        Overriding the values supplied with `__init__` will have only
        temporary effect, for this call only.

        Args:
            separator: This is expected to be a string by which to attempt
              to split the result, if it is a list and `unpack` says we
              should. The default here is the empty separator (`""`),
              which inherits the value supplied to `.__init__()`, and which,
              in turn, typically defaults to `","`.
        
            unwrap: Dictates whether and how array-like query results
              are to be parsed and interpreted. `None` (the default here)
              inherits from the parameter of the same name passed to
              `.__init__()`.

            cast: This is applied to each item individually. The default
              value of anb empty string `""` here inherits from the
              `.__init__()` parameter of the same name.

            getter_fmt: Temporarily overrides the parameter of the same
              name supplied to `__init__`. `fmt` is an alias for this.

            fmt: An alias for `getter_fmt`.
        
        Returns: The result of the `.query()` call, processed as specified
          by the `parse`, `unpack` and `separator` items. This means that
          the bandwidth of possible results is:
        
            - a single plain string, representing an unparsed value
              (e.g. `"3.14"`), or an unparsed list of values
              (e.g. `"3.14,jinkies"`)

            - a single parsed value (e.g. `3.14`)

            - a tuple of unparsed string values (e.g. `("3.14", "jinkies")`)

            - a tuple of parsed values (e.g. `(3.14, "jinkies")`)

            - may raise an exception (`ValueError`) if a single value
              is requeted (e.g. by setting `unpack=False`), but a list
              of values is found, or any other exception which a parser may
              raise if applied to a string it cannot parse.

        Raises: see above.
        '''
        q = self._get_prepare_query(getter_fmt, fmt)
        r = self.query(q)
        logger.debug(f'Getting: {q} -> {r}')
        return self._get_parse_reply(r, unwrap, cast, separator)


    async def async_get(self, unwrap=None, cast="", separator="", getter_fmt=None, fmt=None, **read_args):
        '''
        Async version of `.get()`. See documentation of `.get()` for details.
        '''
        q = self._get_prepare_query(getter_fmt, fmt)
        r = await self.async_query(q, **read_args)
        logger.debug(f'Getting: {q} -> {r}')        
        return self._get_parse_reply(r, unwrap, cast, separator)


    def set(self, *values, pack="", separator="", setter_fmt=None, fmt=None):
        ''' Sets values to the property represented by this object.

        The command to write data is taken from the `setter_fmt`
        (or its alias `fmt`). All named parameters temporarily
        override keys of the same name previously supplied to
        `.__init__()`.
        
        The data can be a single value, or multiple values each as their
        own positional argument.

        Args:
            *values: one or more arguments (values) to set. If more
              than one argument is specified, they are all arranged
              in a single string using the separator `separator` first.

            pack: Formatter for each individual value, or for all values.
              The empty string `""` inherits from the parameter passed to
              `.__init__()` by the same name.

            separator: Separator character or string to use when glueing
              several values together into one string. The default here
              (empty string `""`) inherits the value of the
              same name form `.__init__()`.

            setter_fmt: The format string used to write the data.

            fmt: Alias for `setter_fmt`.
        '''

        if len(self.name) == 0:
            raise RuntimeError('Root subclass cannot set value')        

        if pack == "":
            pack = self.parser_ovrd["pack"]

        if separator == "":
            separator = self.parser_ovrd["separator"]

        if fmt is None:
            fmt = setter_fmt or self.parser_ovrd["setter_fmt"]

        if fmt is None:
            raise RuntimeError(f'Property {self.name} is read-only')            

        if len(values) == 0:
            raise ValueError("Need a value to set, none passed")

        if len(values) == 1:
            datastr = self.convert_to_device(values[0], pack if not isinstance(pack, tuple) \
                                       else pack[0])

        if len(values) > 1:
            if isinstance(pack, tuple):
                if len(pack) != len(values):
                    raise RuntimeError('Need as many values as packers')
                vv = [self.convert_to_device(v, p) for v,p in zip(values,pack)]
            else:
                vv = [self.convert_to_device(v, pack) for v in values]

            datastr = separator.join(vv)

        cmd = fmt.format(*values,
                         **{
                             'name': self.name,
                             'data': datastr
                         })

        logger.debug(f"Setting: {cmd}")
        
        ret = self.kdev.write(cmd)
        
        if ret != (len(cmd)+len(self.kdev.write_termination)):
            raise IOError("Error writing: %s (sent %d bytes, "
                          "should be %d)" % (cmd, ret, len(cmd)))

        
    async def async_set(self, *args, lock=True, **kwargs):
        ''' Asynchronous version of `.set()`.

        This isn't truly asynchronous (there's no simple way to do that
        in pyVISA, unlike with `.get()` -- but writing operations are
        pretty much only operating on the cache, so as long as they're
        short (few KB), they should be non-blocking anyway.

        Args:
            *args: passed on to `.set()`.
        
            **kwargs: passed on to `.set()`.

            lock: if set to `True` or "auto", uses the internal async
              locking object to protect access to device. If set to
              `None` or False, uses a single-use locking object (meaning
              that essentially no useful locking takes place).
              You can also pass your own `asyncio.lock.Lock` object to this.
              Do not mess with this unless you really, *really* know
              what you're doing.
        '''

        if lock in (None, False):
            lock = asyncio.Lock() # fake lock

        if lock in ("auto", True):
            lock = self.device_lock
            
        async with lock:
            r = self.set(*args, **kwargs)
            return r


    def __call__(self, *args, **kw):
        ''' Calls `.get()` if there are no `*args`, `.set()` otherwise. '''
        if len(args) == 0:
            return self.get(**kw)
        self.set(*args, **kw)


    def __getattr__(self, node):
        ''' Conveniently redirects to `.branch()`. '''
        return self.branch(node)

 
    def branch(self, node, fmt=None, branch_fmt=None, parser_conf=None):
        ''' Returns a subclass branch.

        Args:
        
            node: The local name of the subnode branch (i.e. only
              from this point onward; the full name for the subnode
              will be constructed using `fmt` or `branch_fmt`).

            fmt: Format for the full subnode name. Defaults to
              whatever was specified with `__init__`. Can contain
              the following keys:
                - root: the root node name (i.e. *this* class's name)
                - node: the local branch name (i.e. this funcion's
                  `node` parameter).

            branch_fmt: same as `fmt`.

        Returns: A `PropertyNode` object or similar. The actual type
          of the object is determined by the `is_root_subclass` parameter
          that was passed to `__init__`, and by the `._subnode_class`
          contents.
        '''

        #print(self.name, "branching into:", node, "as:", self._subnode_class)
        
        if fmt is None:
            fmt = branch_fmt or self.parser_ovrd["branch_fmt"]

        if fmt is None:
            raise RuntimeError(f'Property {self.name} can\'t branch')

        sub = fmt.format(**{
            'root': self.name,
            'node': node
        })

        logger.debug(f'Descending to {sub}')

        #print("Subclass:", self._subnode_class)

        pconf = { k:v for k,v in self.parser_conf.items() }
        if parser_conf is not None:
                pconf.update(parser_conf)

        prop = self.__propcache.setdefault(node, self._subnode_class(
            self.kdev, name=sub, nxerror=self.__nxerror,
            **pconf
        ))
        
        return prop
    

class MagicVisaChat(PropertyNode):
    '''
    Wrapper for VISA based communication with SCPI-enabled devices.
    The API is in many aspects very similar to `easy-scpi`, but differs
    in some implementation details that make this more suitable to work
    with `emmi` subsystems (in particular the EPICS export stuff).

    Usage example, e.g. for setting a function type on a function generator
    (query "FUNC..."), then setting and querying the current frequency
    (query "FREQyency") and voltage offset (query "VOLTage:AMPLitude"):
    ```
      from emmi.scpi import MagicScpi
    
      dev = MagicScpi(device="TCPIP::10.0.0.61::INSTR")
    
      dev.FUNC("SIN")   ## -> sends "FUNC SIN" to the device
      dev.FREQ("200")   ## -> sends "FREQ 200" to the device
      print ("Current frequency is", dev.FREQ())  ## -> queries "FREQ?" from device

      dev.VOLT.AMPL("3")
      print ("Current voltage amplitude is", dev.VOLT.AMPL())
    ```

    See `escpi` for an example on how to make an EPICS-IOC of a SCPI device.

    This class is actually a more general version, able to speak languages
    that are structurally similar to SCPI, but differ in small parsing
    details (e.g. spacers and separators).
    '''

    def __init__(self, device=None,
                 resource_manager='@py',
                 device_conf=None,
                 **kwargs):
        ''' Generic interface for SCPI-compatible devices via PyVISA.
        
        Default device is `None`, which means the address will be read from the
        `MAGICSCPI_ADDRESS` environment variable.

        Args:
            device: The pyVISA device to use.
              This can either be a full pyVISA device (in which case it
              is used as-is, and the `resource_manager` argument is ignored),
              or a string representing a
              [VISA resouce address](https://pyvisa.readthedocs.io/en/latest/introduction/names.html)
              to connect to.

              As a resource address this could be something along the lines of
              `TCPIP::10.0.0.17::INSTR` for a VISA/SCPI device connected
              via TCP/IP.
              If this parameter is `None`, then a string taken from the
              `MAGICSCPI_ADDRESS` environment variable is used.

            resource_manager: VISA resource manager to use (default is `"@py"`),
              as a string, or as an object. If this is a string, then a resource
              manager object is created using `pyvisa.ResourceManager()`.

            device_conf: A dictionary containing additional configuration keys
              for the VISA resource. If `device` is an address string, then
              `device_conf` defaults to this, which appears to be
              a useful setting for TCP/IP VISA devices:
              ```
                { "timeout": 3.0,
                  "read_termination": "\n",
                  "write_termination": "\n" }
              ```

              If `device` is a pyVISA device object, then `device_conf`
              defaults to an empty dictionary (i.e. no parameters are being
              implicitly altered).
        
              Additional keys are accepted and passed as properties/attributes
              the specific [resource class](https://pyvisa.readthedocs.io/en/latest/api/resources.html).

            **kwargs: Arguments for the superclass (likely `PropertyNode`, in which
              case these are parser options).
        '''

        dev = self.__open_device(device, resource_manager, device_conf)

        super().__init__(dev=dev, name="", is_root_subclass=True,
                         nxerror=None, **kwargs)

        # This is not necessary in *this* class (i.e. MagicVisaChat), since
        # super().__init__() will automatically point to its base class.
        # However, if we subclass this, we end up with MagicVisaChat as a base
        # class, and the PropertyNode heuristics of dealing with this goes
        # out the window :-(
        #
        # So we need to actually set the subnode class explicitly. Subclass
        # can still change it after they call this __init__(), if they want.
        self._subnode_class = PropertyNode

        logger.debug("Device open: %s" % self.port)

        # This will avoid prepending a colon at the beginning of the root node
        # (i.e. no ":FOO:BAR", only "FOO:BAR").
        self.local_override('branch_fmt', '{node}')        


    def __open_device(self, device, resource_manager, device_conf):
        # Returns a usable pyVISA device. Makes sure self.port and
        # self.rman exist, but are both set to None if the device
        # was already a visa device.
        
        if isinstance(device, str) or device is None:

            if device_conf is None:
                device_conf = dict()
                device_conf.update({
                    "timeout": 3000,
                    "read_termination": "\n",
                    "write_termination": "\n"
                })
            
            if device is None:
                try:
                    device = env['MAGICSCPI_ADDRESS']
                except KeyError:
                    logger.error("No SCPI port specified and no MAGICSCPI_ADDRESS available")
                    raise
                
            self.port = device
            self.rman = pyvisa.ResourceManager(resource_manager) \
                if isinstance(resource_manager, str) \
                   else resource_manager

            logger.debug(f"Available resources: {self.rman.list_resources()}")
            
            dev = self.rman.open_resource(self.port)
        
        else:

            if device_conf is None:
                device_conf = dict()
            
            self.port = device.resource_name
            self.rman = None
            dev = device

        for k,v in device_conf.items():
            setattr(dev, k, v)

        return dev


class MagicScpi(MagicVisaChat):
    ''' VISA Chat specialization with parser set up for the the SCPI protocol. '''

    # Most defaults of MagicVisaChat are already suitable for SCPI.
    def idn(self):
        ''' Return self-reported identification string. '''
        return self.kdev.query('*IDN?')
    

class MagicHuber(MagicVisaChat):
    ''' Visa Chat class for the Huber SCM class of motion controllers.

    They're usually connected via GPIB, serial or TCP/IP and speak a
    query-response language that isn't SCPI. However, it's close enough
    that we can actually make this work with relatively few tweaks to
    the formatting constants.
    '''
    def __init__(self, device=None, resource_manager=None, **kwargs):

        args = []
        
        if device is not None:
            args.append(device)

        if resource_manager is not None:
            args.append(resource_manager)

        # ACHTUNG, the Huber language is very convoluted and chaotic.
        # Most queries ar of the form "?command". Most answers return
        # ":" as a separator, but some are two-dimensional: they
        # return ";" as the first level unwrap separator, and ":" as
        # the second level.
        # Some queries (e.g. "?status" or "?err") may return multi-line
        # answers, which is impossible to model with MagicVisaChat.
        # There are many commands which are setter-only / getter-only.

        kwargs['getter_fmt'] = "?{name:s}"
        kwargs['setter_fmt'] = "{name:s}{data:s}" # mostly
        kwargs['branch_fmt'] = None # no branching
        kwargs['separator'] = ":"   # mostly
        
        kwargs.setdefault('device_conf', dict())
        kwargs['device_conf']['write_termination'] = '\r'
        kwargs['device_conf']['read_termination'] = '\r\n'
        
        super().__init__(*args, **kwargs)

        hello = self.kdev.read()
        logger.info(f'Huber self-reporting: {hello}')

        logger.debug("Hello: %r" % (self.kdev.read(),))

    def idn(self):
        ''' Return self-reported identification string.
        (Huber is not a SCPI protocol, but they do have this *IDN? thing...)
        '''
        return self.kdev.query('*IDN?')        


class MagicPharos(MagicVisaChat):
    ''' Visa Chat class for the Pharos (Light Conversion?) laser control devices.

    Typically engaged via serial lines, they speak a query-response language.
    The devil is in the details here, as the language has some degree of
    self-introspection: almost all replies are multi-value, but they don't
    typically just return "arrays", they return specific well-documented data
    types. Each reply (except for transmission and error control like "Ok"),
    has an initial string stating which data type it contains.
    '''

    def __init__(self, *args, **kwargs):
        kwargs['getter_fmt'] = '{name:s}'
        kwargs['unwrap'] = self._pharos_unwrap
        kwargs['device_conf'] = {
                'read_termination': '\n\r',
                'write_termination': '\r',
                'baud_rate': 57600,
        }
        
        super().__init__(*args, **kwargs)


    def _pharos_unwrap(self, s):
        # Checks for format "<STRING>: ..."
        # Returns a tuple when there are more than one element(s),
        # a single value otherwise.
        
        i = s.find(': ')
        if i > -1:
            t = s[:i]
            logger.debug(f'Pharos: received type {t} data')
            split = [x.strip() for x in s[i+2:].split(',')]
            
            #return tuple(split) if len(split)>1 else split[0]
            return tuple(split + [s[0:i]])

        # Fall back to single value (string) if everything else fails.
        # Should check Pharos docs whether we'd rather raise an error here...
        return s.strip()


class MockPropertyBranch(object):
    '''
    Accepts any property.
    '''
    def __init__(self, *args, **kwargs):
        self._val = 3.14
        self.__pcache = {}

    def __call__(self, *args):
        if len(args) == 0:
            return self._val
        else:
            self._val = args[0] 

    def __getattr__(self, name):
        return self.__pcache.setdefault(name, MockPropertyBranch())


class MockScpi(object):
    '''
    Mocking class for Keith3390. Has some defauls for
    the explicit attributes (output, waveform, ...)
    '''

    def __init__(self, *args, **kwargs):
        self.__pcache = {}

    def id(self):
        return "Mock SCPI Device"

    def __getattr__(self, name):
        return self.__pcache.setdefault(name, MockPropertyBranch())
    
