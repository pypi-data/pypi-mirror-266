#!/usr/bin/python

from schema import *
from softioc import builder as IocBuilder

from pprint import pprint
from functools import partial, reduce

import time, asyncio, logging, inspect, sys
logger = logging.getLogger(__name__)

from softioc.softioc import safeEpicsExit as softioc_exit

import numpy as np

import traceback

'''
Validators are a concept that allow us to filter, translate and validate
data (values) from one ecosystem (e.g. EPICS) into another (e.g. SCIP).
Each validator needs to have at least:

  - one setup() function which receives named arguments with the necessary
    data for validating; arguments names will be directly accepted/visible
    in the YAML files, so choose wisely.

  - one __getitem__() function which returns the translated value, or
    raises ValueError if the value is out of the permissible conditions.
'''
        
class MappingValidator(object):
    '''
    Translates a value from one set to another
    '''
    def __init__(self, values={}):
        self.setup(values)

    def setup(self, values={}):
        self.trmap = values

    def __getitem__(self, val):
        if val in self.trmap:
            return self.trmap.get(val)
        
        raise ValueError("%r: invalid value" % val)


class SetValidator(object):
    '''
    Accepts only objects form a specific set.
    '''
    def __init__(self, **kwargs):
        self.setup(**kwargs)

    def setup(self, values=[]):
        self.vset = values

    def __getitem__(self, val):
        if val in self.vset:
            return val
        else:
            raise ValueError("%r: value not in set %r" % (val, self.vset))


class BoundaryValidator(object):
    '''
    Accepts only values within specified boundaries
    '''
    def __init__(self, **kwargs):
        self.setup(**kwargs)

    def setup(self, limits=[None, None], inclusive=[True, True], invert=False):
        self.lim = limits
        self.incl = inclusive
        self.inv = invert

    def __getitem__(self, val):
        err = ValueError("%r: outside of range" % val)
        if ((self.lim[0] is not None) and (self.incl[0] and val < self.lim[0])) == (not self.inv):
            raise err
        if ((self.lim[1] is not None) and (self.incl[1] and val > self.lim[1])) == (not self.inv):
            raise err
        if ((self.lim[0] is not None) and (not self.incl[0] and val <= self.lim[0])) == (not self.inv):
            raise err
        if ((self.lim[1] is not None) and (not self.incl[1] and val >= self.lim[1])) == (not self.inv):
            raise err
        return val

    
class SliceValidator(object):
    '''
    Returns only specified slice of an (iterable/indexable) value.
    '''
    def __init__(self, **kwargs):
        self.setup(**kwargs)
        
    def setup(self, start=None, stop=None, step=None):
        self.sobj = slice(start, stop, step)

    def __getitem__(self, val):
        return val[self.sobj]

    
class IdentityValidator(object):
    ''' Lets everything through '''

    def setup(self):
        pass
    
    def __getitem__(self, val):
        return val



class PropertySetter(object):
    '''
    Wrapper that sets a property -- we need this because
    we want to build most of our API based on properties
    (insted of callable setter functions), but at several
    points in the involved APIs (softioc.Builder, for instance)
    callables are required.
    '''

    def __init__(self, name, setter, validator=None):
        self.name = name
        self.setter = setter
        self.validator = validator or IdentityValidator()
        self.validation_failed = False

    async def __call__(self, value):
        try:
            valid = self.validator[value]            
            #logger.info("Value %r validates to %r (by %r)" % (value, valid, self.validator))
            
            self.validation_failed = False
            
            try:
                await self.setter(valid)
                
            except TypeError as t:
                #logger.error(traceback.format_exc())
                self.setter(valid)

            except OverflowError:
                raise
                
        except ValueError as e:
            if not self.validation_failed:
                logger.error("Failed to set %s: %r" % (self.name, e))
                self.validation_failed = True

        except Exception as e:
            logger.error("%s: Setting value failed: %r" % (self.name, e))
            logger.error(traceback.format_exc())
                
        except:
            logger.error("%s: Setting value failed" % (self.name,))


class PropertyUpdater(object):
    '''
    A callable object which loops indefinitely reading out a property via `getter`
    and publishing it on EPICS process-variable `pv`. The waiting
    time on every loop run is such that a full run is as close
    as possible to `period`.
    '''
    
    def __init__(self, name, pv, pollPeriod, getter, validator=None, kill_on_error=False):
        self.name   = name
        self.pv     = pv
        self.period = pollPeriod
        self.getter = getter
        self.validator = validator or IdentityValidator()
        self.kill_on_error = kill_on_error

    def set_period(self, val):
        self.period = val

    async def __call__(self):
        logger.debug("%s: Updater running for PV %r" % (self.name, self.pv))
        available = True
        while True:
            tstart = time.time()
            try:
                val = self.getter()
                
                if (val is not None):
                    cur = self.pv.get()
                    vv = self.validator[val]                    

                    try:
                        is_same = (np.array(cur) == np.array(vv)).all()
                    except Exception as e:
                        logger.error(f'{self.name}: Error comparing current value '
                                     f'{cur} to new value {vv}: {str(e)}, {traceback.format_exc()}')
                        logger.error(f'If this error does not reoccur, you can safely ignore it.')
                        is_same = False

                    if not is_same:
                        self.pv.set(vv)

                if not available:
                    logger.info("%s: has become available again" % self.name)
                    available = True
                
            except Exception as e:
                if self.kill_on_error:
                    logger.error(f"{self.name}: property error and IOC termination requested")
                    logger.error(f"{self.name}: {str(e)}")
                    softioc_exit()
                
                # We're not going to exit on PV setting problems (may be
                # intermittent), but at least we'll get loud about it.
                if available:
                    logger.error("%s: property became unavailable, reason: %r" % (self.name, e))
                    logger.error(f"{self.name}: traceback: {traceback.format_exc()}")
                    logger.error("%s: further errors will be silenced" % self.name)
                    logger.info("%s: Getter object was: %r" % (self.name, self.getter,))
                available = False
            
            except e:
                logger.error("%s: unknown exception %r. You _should_ be worried." % e)
                
            finally:
                tdiff = time.time()-tstart
                await asyncio.sleep(self.period - tdiff)

            
'''
List of connector kinds we support. "in"/"out" should return the
correct builder function (lambda parameter being the softioc builder
object itself), and "args" is a list of initial arguments for the
builder function. Typically you'd want to set default values,
and/or sizes, and/or data types.
'''
ConnectorKinds = {
    "analog": {
        "in": IocBuilder.aIn,
        "out": IocBuilder.aOut,
        "create": { "initial_value": 0.0 },
        "to-epics": IdentityValidator(),
        "from-epics": IdentityValidator() },
    
    "switch": {
        "in": IocBuilder.boolIn,
        "out": IocBuilder.boolOut,
        "create": { 'ZNAM': 'OFF', 'ONAM': 'ON' },
        "to-epics": MappingValidator(values={"ON": 1, True: 1, 1: 1,
                                             "OFF": 0, False: 0, 0: 0}),
        "from-epics": MappingValidator(values={1: "ON",
                                               0: "OFF"}) },

    "strings": {
        "in": IocBuilder.stringIn,
        "out": IocBuilder.stringOut,
        "create": { },
        "to-epics": SetValidator,
        "from-epics": SetValidator },

    "waveform": {
        "in": IocBuilder.WaveformIn,
        "out": IocBuilder.WaveformOut,
        "create": { },
        "to-epics": IdentityValidator(),
        "from-epics": IdentityValidator()
    },

    # untested:
    
    "text":  {
        "in": IocBuilder.stringIn,
        "out": IocBuilder.stringOut,
        "create": { },
        "to-epics": SliceValidator(stop=39),
        "from-epics": IdentityValidator() },

    "map": {
        "in": IocBuilder.stringIn,
        "out": IocBuilder.stringOut,
        "create": { "initial_value": "n/a" },
        "to-epics": MappingValidator,
        "from-epics": MappingValidator },

    "values": {
        "in": IocBuilder.longIn,
        "out": IocBuilder.longOut,
        "create": { "initial_value": 0 },
        "to-epics": SetValidator,
        "from-epics": SetValidator },

    "integer": {
        "in": IocBuilder.longIn,
        "out": IocBuilder.longOut,
        "create": { "initial_value": 0 },
        "to-epics": IdentityValidator(),
        "from-epics": IdentityValidator() },
}

class SignalConnector(object):
    '''
    Connects a sensoric signal (i.e. a reading of a measurement) to an
    EPICS PV. The data is retrieved from either a Python property or
    from a getter function.
    '''

    argnames = { "suffix": str,
                 "name": str,
                 "kind": str,
                 "access": object,
                 "create": dict,
                 "validator": dict,
                 "pollPeriod": float,
                 "killOnError": bool }

    schema = Schema({Optional(k):v for k,v in argnames.items()})

    def __init__(self, ioc_dispatch, **kw):
        '''
        Parameters:
          - `ioc_dispatch`: dipatcher to use

          - `name`: Used to recognize stuff throughout the application,
            also serves as default to `suffix`.

          - `suffix`: PV name to use; defaults to `name`.
        
          - `access`: Callable or (obj, propname) tuple of a Python
            property to set or get data from.

          - `kind`: one of the `eda.ConnectorKinds` keys

          - `pollPeriod`: poll period for the data to publish (i.e.
            calling of `access`)

          - `validator`: If not `None`, this is a dict that will be used to
            initialize the validator of the property.

          - `create`: Supplementary arguments to pass on when creating the
            PV class. This is highly specific to the underlying EPICS
            framework being used.
        '''
        
        if not set(kw).issubset(set(self.argnames)):
            raise TypeError("Unknown arguments: %r" % set(kw).difference(self.argnames))
        
        k = ConnectorKinds[kw.get('kind')]

        suffix = kw.get('suffix') or kw.get('name')

        pv_create_args = k.get('create', {})
        pv_create_args.update(kw.get('create', {}))
        RecordType = k["in"]
        self.pv = RecordType(suffix, **(pv_create_args))

        if hasattr(kw.get('access', None), "__call__"):
            access = kw['access']
        else:
            access = partial(getattr, *(kw['access']))

        # sometimes the validator in ConnectorKinds is an explicit
        # instance (which we can use right away); sometimes it's just
        # a class type, which we have to instantiate first
        valdtr = k['to-epics'](**(kw.get('validator', {}))) if type(k['to-epics']) == type \
            else k['to-epics']

        getter = PropertyUpdater(name=kw.get('name', suffix),
                                 validator=valdtr,
                                 pv=self.pv,
                                 pollPeriod=kw.get('pollPeriod', 1.0),
                                 getter=access,
                                 kill_on_error=kw.get('killOnError', False))

        if ioc_dispatch:
            ioc_dispatch(getter)

        logger.info("Signal: %s, kind='%s', access=%r" % (suffix, kw.get('kind'), kw.get('access')))
        

class ActorConnector(object):
    '''
    Connects an action signal (i.e. button, knob, setting etc) to an EPICS PV.
    '''

    argnames = { "suffix": str,
                 "name": str,
                 "kind": str,
                 "access": object,
                 "validator": object }

    schema = Schema({Optional(k):v for k,v in argnames.items()})

    
    def __init__(self, ioc_dispatch, **kw):
        '''
        Parameters:

          - `ioc_dispatch`: The pythonSoftIOC async dispatcher. Ignored here,
            but we need this for API uniformity with the other connectors.

          - `name`: Name of the ActorConnector (used internally for displaying
            purposes, and as a default for `suffix` if the latter is not specified).
        
          - `suffix`: PV name to use
        
          - `access`: Reference to a Python property (either callable or writable),
            for setting data.

          - `kind`: one of the `eda.ConnectorKinds` keys

          - `validator`: property dictionary for kind-specific validator
            configuration.

          - `create`: Supplementary arguments to pass on when creating the
            PV class. This is highly specific to the underlying EPICS
            framework being used.        
        '''

        if not set(kw).issubset(set(self.argnames)):
            raise TypeError("Unknown arguments: %r" % set(kw).difference(self.argnames))
        
        k = ConnectorKinds[kw.get('kind')]

        suffix = kw.get('suffix') or kw.get('name')
        
        if hasattr(kw['access'], "__call__"):
            access = kw['access']
        else:
            access = partial(setattr, *(kw['access']))

        if  k['from-epics'] is None:
            validator = None
            
        elif type(k['from-epics']) == type:
            # Instantiate from explicit type
            validator = k['from-epics'](**(kw.get('validator', {})))
            
        elif kw.get('validator') is not None:
            # There's already an instance, but there's an override list
            # of paramters for a re-initialisation available
            validator = k['from-epics'].__class__(**(kw['validator']))
            
        else:
            # If we got here, k['from-epics'] must already be an instance,
            # so we use it.
            validator = k['from-epics']

        setter = PropertySetter(name=suffix, validator=validator, setter=access)

        pv_create_args = k.get('create', {})
        pv_create_args.update(kw.get('create', {}))
        RecordType = k["out"]
        self.pv = RecordType(suffix, always_update=True, on_update=setter, **pv_create_args)
        
        logger.info("Actor %s: kind='%s' actor, access=%r" % (suffix, kw['kind'], access))
    
        
class PropertyConnector(object):
    '''
    Conenctor for a get/set type of property; uses `eda.SignalConnector`
    and `eda.ActorConnector` under the hood to export two PVs, one for
    setting, one for reading back the property. By default the variable
    names end in "VAL" (for setting), respectively "RBV" (for reading).

    A `sync()` method is available to programatically set the
    "VAL" part to its current readback value "RBV".
    '''

    # Using this for validation. For once it's needed in __init__(),
    # and then it's also used in parsing YAML files.
    argnames = { "suffix": str,
                 "name": str,
                 "kind": str,
                 "access": object,
                 "validator": object,
                 "signal": dict,
                 "actor": dict }

    schema = Schema({Optional(k):v for k,v in argnames.items()})

    def __init__(self, ioc_dispatcher, **kw):
        '''
        Parameters:
          - `ioc_dispatcher`: connection to pythonSoftIOC to use.

          - `prefix`: PV prefix, will be prepended to the variable names. By
            default the variable names end in "VAL" (for setting), respectively
            "RBV" (for reading), but they can be overridden by using the `sensor`
            and `actor` parameters. Defaults to `name`.

          - `access`: Access method or (obj, prop) to use for both reading and
            writing. If there are different methods for reading and writing,
            this should be set to `None` and the appropriate methods should
            be set via the `sensor` and `actor` dictionaries.

          - `kind`: The kind of signal to use; must be one of the `eda.ConnectorKinds`
            items.
        
          - `signal`: Dictionary with optional variables to pass on to
            `eda.SignalConnenctor` for the reading part.
        
          - `actor`: Dictionary with optional variables to pass on to
             `eda.ActorConnector` for the setting part.
        '''

        if not set(kw).issubset(set(self.argnames.keys())):
            raise TypeError("Unknown arguments: %r" % list(set(self.argnames.keys()).difference(kw)))

        #print ("Intermediate 1.2: %r" % (kw['access'],))
        
        ad = {}
        ad.update(kw.get('actor', {}))
        ad.setdefault("kind", kw['kind'])

        #if 'access' in ad:
        #    # Subconnector has its own 'access' information -- we need to use that.
        #    if isinstance(ad['access'], str):
        #        # If it's a plain string, we intepret that to be a (sub-)property
        #        # relative to the base class already specified in kw['access'].
        #        # If kw['access'] doesn't have anything, we're out of luck anyway,
        #        # because we don't have access to a base class here.
        #        ad['access'] = FindAccess(kw['access'], ad['access'])
        #    elif hasattr(ad['access'], "__len__") \
        #         and len(ad['access']) == 2 \
        #         and isinstance(str, ad['access'][1]):
        #        # ...may be a tuple (obj, "attribute")?
        #        ad['access'] = FindAccess(*(ad['access']))
        #    else:
        #        raise RuntimeError("Unsupported sub-access type %r for property connector")
        #else:
        #    # Regular
        #    ad['access'] = kw['access']
        ad['access'] = self.descend_access(kw['access'], ad.get('access', None))
            
        
        ad.setdefault("validator", kw.get('validator', None))
        ad.setdefault("suffix", (kw.get('suffix') or kw.get('name'))+"VAL")
        self.val = ActorConnector(ioc_dispatcher, **ad)

        sd = {}
        sd.update(kw.get('signal', {}))
        sd.setdefault("kind", kw['kind'])

        #if 'access' in sd:
        #    if isinstance(sd['access'], str):
        #        sd['access'] = FindAccess(kw['access'], sd['access'])
        #    elif hasattr(sd['access'], "__len__") \
        #         and len(sd['access']) == 2 \
        #         and isinstance(str, sd['access'][1]):
        #        # ...may be a tuple (obj, "attribute")?
        #        sd['access'] = FindAccess(*(sd['access']))
        #    else:
        #        raise RuntimeError("Unsupported sub-access type %r for property connector")                
        #else:
        sd['access'] = self.descend_access(kw['access'], sd.get('access', None))
                
        #print ("Intermediate 1.7: %r" % (sd['access'],))
        
        sd.setdefault("validator", kw.get('validator', None))
        sd.setdefault("suffix", (kw.get('suffix') or kw.get('name'))+"RBV")
        self.rbv = SignalConnector(ioc_dispatcher, **sd)

        logger.info ("Registering property: %s" % (kw.get('suffix') or kw.get('name')))


    def descend_access(self, top_access, sub_access):
        '''
        Given an existing access object in `top_access` and (possibly)
        a specification for a sub-property access, this returns a merged
        access object to be used.
        '''
        
        if sub_access is None:
            # Nothing to do, there is no sub-access.
            return top_access
            
        if isinstance(sub_access, str):
            # Sub-access is a plain method name (possibly nested).
            # We interpret that to be relative to the top-access object.
            # The top-access object is either directly a Python object,
            # or a (base, "prop") sub-object itself.
            if isinstance(top_access, tuple) \
               and len(top_access)==2 \
               and isinstance(top_access[1], str):
                # top-access is a (base, "prop") notation, so we need
                # to compute the actual property first.
                obj = getattr(*(top_access))
                print("sub-tuple:", obj)
            else:
                # top_access is direct object (callable?), sub-access is just
                # a member nane
                obj = top_access
                print("direct:", obj)
            return FindAccess(obj, sub_access)
        
        elif hasattr(sub_access, "__len__") \
             and len(sub_access) == 2 \
             and isinstance(str, sub_access[1]):
            # Sub-access is a tuple (obj, "attribute"), so we ignore the
            # top-access completely and just build a new access object.
            return FindAccess(*(sub_access['access']))

        # How did we get here?
        raise RuntimeError("Unsupported sub-access type %r for property connector")
    
#
# Validating YAML input for EPICS exports. General YAML format of an export
# record list is like this:
#
#   exports:  # ...or whatever, this isn't regulated (yet)
#
#   - recordType: signal  # indicates essentially "how" this data flows and behaves, can
#                         # be any of the ExportRecordTypes.
#
#     pvName: "PV"  # optional; if not available, then the connector-type entry must have one
#
#     signal:       # depending on the connector type
#
#     - pvName:     # optional; if not available, the one from parent plus a default suffix will be used.
#
#       kind: "analog"  # ...or any other of the ConnectorKinds
#
#       pollPeriod: 0.1 # typical key for "signal" here, other recordTypes may have other fields
#
#
# Schemata for the YAML EPICS-PV "exports" section. General format considerations:
#
#  - `recordType` tells the direction of the data flow and some structural
#    information. Generally there are two basic types -- `signal` (for reading data
#    from external device), and `actor` (for writing data into an external device).
#    Each of these types exports a PV on its own: an OUT, respectively IN semantics
#    of EPICS.
# 
#    A joint type that can do both is `property`: it uses a Signal and an Actor to
#    export two variables, one for reading and one for writing: a "_VAL" and a "_RBV"
#    one.
#
#    Several higher-level types are possible to implement here, for instance a "motor"
#    (usually a positioner / "actor" that has a working state).
#
#
#  - `name`: This is the sine-qua-non. It's the name of the Python object property
#    we're exporting / working on. If the property is a callable, it will be
#    called without an argument (i.e. `obj.prop()`) to read a value, and with
#    one single argument to set a value (`obj.prop(23)`). Otherwise the property
#    will be read and set as if it were a static value (`obj.prop = 23`).
#
#
#  - 'pvSuffix' is an optional suffix for the corresponding EPICS variable;
#    if not set, it defaults to 'name' (with the dots 'n all).
#
#
#  - `format`: Sometimes data comes out of the Python end as a string, containing
#    undesired components (e.g. `"session 1, garble 42.37 yadda"`, and we're
#    actually only interested in `42.37` here). If that's the case with your application,
#    you can specify an explicit format string (here, for instance,
#    `"session {moo}, garble {value} {word}"`) which contains the formatter `{value}`
#    somewhere inside. If that is specified, that will be used for accessing the data.
#
#
#  - `kind` is a hint as to how the data is to be interpreted: it affects two
#    distinct subsystems: on one end, the EPICS PVs that are exported have specific
#    types (aOut/aIn, stringOut/strinIn etc). So specific "kinds" are mapped to
#    specific EPICS PV types.
#    On the other end, the data going in/out, between EPICS/Python (<- which is, to
#    say, the device), also has a may need to be translated to specific Python types.
#    Within Python code, this is done by Validators (somewhat misnamed, they actually
#    also do a great deal of converting).
#
#    Now, with specific `kind` settings come also specific preconfigured validators.
#
#
#  - (FXIME: need to talk about validator settings like `values` etc).
#
#
#  - Reading and writing -- normally reading and writing is done using the same
#    property, in a symmetric manner. For instance: if the property of object `obj`
#    is `prop`, then reading vs. writing is `obj.prop()` vs `obj.prop(...)`, or
#    `obj.prop` vs `obj.prop=...` (if the property is non-callable), or `format(str)`
#    vs. `str.format(...)` if a format is specified, etc. But never, say,
#    `obj.prop()` for reading and `obj.set_prop(42)` for writing.
#
#    Yet sometimes different approaches are necessary.
#
#    For this reason, when using higher-level "recortType" objects like `property`,
#    their lower-level constituents (e.g. `signal` and `actor`), which actually control
#    the reading and writing, mirror the options `name`, `format`, `pvSuffix`.
#    If these are set, they overwrite their conterparts from the supersection.



def FindAccess(obj, name, separators=['.', ':']):
    '''
    Recursively finds a property of object instance `obj`.
    Returns a tuple `(instance, "name")`, where `"name"` is
    the name of the final Python property to be used and
    `instance` is an object instance that owns said property.
    Generally, if `name` is a nested property, then `instance`
    is *not* the same as `obj`.
    '''

    # Pick a separator from the list -- the first one we find.
    for sep in separators:
        if sep in name:
            break
    
    ref = obj
    chain = name.split(sep) if sep in name else [name]
    
    for p in chain[:-1:]:
        ref = getattr(ref, p)
        if ref is None:
            logger.error(f'Property required for "{p}" is None')
            raise RuntimeError(f'Property required for "{p}" is None')
    
    prop = (ref, chain[-1])
    attr = getattr(*prop)
    
    if hasattr(attr, "__call__"):
        return attr
    else:
        return prop


ExportRecordTypes = {
    "signal": SignalConnector,
    "actor": ActorConnector,
    "property": PropertyConnector
}

def ExportObjectFromDict(ioc_dispatch, parent, data,
                         suffixMangle=lambda x: x,
                         recordTypeDefaults=None):
    '''
    Creates an export object (i.e. one of the `ExportObjectTypes`) from
    a data dictionary as specified by the `scm_export_record` and
    kindred schemata. The `parent` is the object to which all properties
    named within `data` relate.
    Parameters:

      - `ioc_dispatch: a pythonSoftIOC dispatch object to use for the
        Signal-type connectors (essentially, those run an asyncio-based
        polling loop, and ioc_dispatch takes care of actually dispatching it)

      - `parent`: The object to which all the properties are refering to

      - `data`: A configuration dictionary cotaining, among others, the
        name of the property to export

      - `suffixMangle`: A callable to optionally do some name mangling on
        the final PV suffix that we'll send to the pythonSoftIOC builder.
        This is typically used e.g. to change case of the variable names,
        or to add more suffixes/prefixes/interfixes as needed.
        This is necessary because we actually want to hide the details of
        the configuration format within `data` to higher layers -- only
        `ExportObjectFromDict()` and functions below it need to know the
        details. Another reason is that details, in particular of variable
        naming, are pretty ofuscated -- naming can be done at high level,
        or may be delegated down to sub-objects, and we don't want higher
        level to have to deal with that. So, in essence: if you need to
        mangle the name, use this function! ;-)
    '''

    # For creating EPICS PV exports delaratively, i.e. from YAML,
    # we start with a 'recordType' (e.g. "signal" or "property"):
    scm_dict = { 'recordType': Or(*(ExportRecordTypes.keys())) }
    
    # The bulk of the parameters may then be specified in sub-dictionaries
    # (see above). Each Connector type class needs to bring its own schema:
    scm_dict.update({ Optional(k):v.schema for k,v in ExportRecordTypes.items() })
    
    # Some record types are primitives ("actor" and "signal"), others are
    # composed ("property"). Things get increasingly nested ("motor" holds
    # several "property" records, for instance). We specify parameters in
    # the order in which they're encapsulated (e.g. "property" accepts dicts
    # for "signal" and "actor" which it's made of).
    # 
    # For convenience, at the top level we also accept parameters common to
    # all subsets (e.g. "name" or "suffix").
    #common_args = reduce(lambda x, y: x&y,
    #                     [set(v.argnames.items()) for k,v in ExportRecordTypes.items()])
    #scm_dict.update({Optional(k):v for k,v in common_args})
    #pprint(scm_dict)
    
    scm = Schema(scm_dict)
    logger.debug("Export schema: %r" % scm)
    data = scm.validate(data)

    # ACHTUNG: This whole passing-arguments-down-to-encapsulated-subtypes shebang
    # only works as long as there is only *one* specific subtype of each being
    # encapsulated, and the corresponding YAML subsection has exactly the same
    # name as the subtype itself. E.g. this works well:
    #
    #  - recordType: property
    #    signal:
    #      ...
    #    actor:
    #      ...
    #
    # This doesn't work:
    #
    # - recordType: motor
    #   signalUpperLimit:
    #     ...
    #   signalLowerLimit:
    #     ...
    #
    
    recType = data['recordType']

    recParams = ((recordTypeDefaults or {}).get(recType) or {}).copy()
    recParams.update(data[recType])

    try:
        recParams['access'] = FindAccess(parent, recParams.get('access') or recParams.get('name'))
    except Exception as e:
        # 'name' may not necessarily be a valid property of the object.
        # So if we fail finding one, we just ignore it, and 'access' will
        # be undefined. It will be up to lower layers to provide a proper
        # access method.
        logger.info('No access for %r defined at top-level' % data.get('name'))
        pass

    # Here's the name mangling. Note that this will only mangle suffix naming
    # at the top level, not at the sub-levels. For that, we're stuck with whatever
    # functionality the Connector objects already implement.
    # The obvious (and possibly the only good) solution to this would be to pass
    # the name-mangling callable down to the Connector types (here: `ExportRecordTypes[]`)
    # constructor itself. For that to work, we'd probably have to derive all Connector
    # classes from a common base class that does handle these types of common tasks
    # (like calling a name mangling lambda).
    recParams['suffix'] = suffixMangle(recParams.get('suffix') or recParams.get('name'))
    
    logger.debug("Building connector %r, settings %r" % (recType, recParams))

    #print ("Intermediate 1: %r" % (recParams['access'],))
    obj = ExportRecordTypes[recType](ioc_dispatch, **recParams)

    return obj
