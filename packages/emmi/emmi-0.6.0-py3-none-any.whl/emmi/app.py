#!/usr/bin/python3

import asyncio, time, logging
import logging

from os import environ

from emmi.api.exports import ExportObjectFromDict

'''
Base modules for easier development of EPICS
'''

def cfgFromFlat(flatCfg, prefix='', splitChar='_'):
    '''
    Returns a (possibly nested) configuration dictionary from a flat
    list of key-value pairs `flatCfg`. The initial list can for instance
    be a list of environment variables.

    Only entries where the key matches a specific prefix are considered.
    `prefix`, however, may be an empty string, which leads to accepting
    the list as given.
    
    Splits variable names at `splitChar` and adds a new dictionary
    level for each split.
    '''

    if not isinstance(prefix, str):
        return {}

    env = {}

    for k,v in flatCfg.items():
        if not k.startswith(prefix):
            continue
        
        parts = k.split(splitChar)

        current_dict = env
        for p in parts[:-1]:
            current_dict = current_dict.setdefault(p, {})
        current_dict[parts[-1]] = v
        
    if len(prefix):
        return env.get(prefix, {})
    else:
        return env


def cfgUnify(*cfgs, mangle_case=True):
    '''
    Returns a unified configuration object by consecutively applying
    dictionary values from `cfgs`. The individual configuration
    dictionaries in `cfgs` can be recursive.

    If `mangle_case` is enabled (default), then a special handling
    of key string case is perfomed, as follows.

    Quite generally, the preferred format of key names is
    all-lower-case ("likethis") or camel-case ("likeThis"), without
    dashes or underscores, and the typical usage case for this function
    is to put together configuration information from different sources,
    e.g. config files (e.g. YAML hierarchies) and environment variables.
    It is acknowledged that some configuration sources (e.g. environment
    variables) have their typical case customs (e.g. ALL_UPPER_CASE_IN_ENV_VARS).

    For this reason, when encountering all-caps keys, corresponding
    existing keys are searched in previous configuration dictionaries.
    If those are found, then the new ALL-CAPS key is interpreted to
    update one of the existing variables. For instance an environment
    variable `APPLICATIONNAME` will overwrite a previous config setting
    `applicationName`.

    If no case-sensitive keys with the same name exist, then new keys are
    created from scratch. But if the newly to-be-created key is all-caps,
    then instead of using it verbatim, it is converted to lower-case (!),
    to keep the style of lower-case variable names consistend.

    Note that while this gives well-defined results, it may not behave as
    expected if configuration keys use camel-case and are expected; for
    instance, "FOOBAR" would be translated to "foobar" if "fooBar"
    doesn't already exist.
    
    Defining camel-case variables in environment variables works, though:
    "$fooBar=application" would be translated to a configuration variable
    "fooBar='application' regardless of where it is found.
    '''

    #print ("Unify:", *cfgs)
    
    cfg = dict()
    for c in cfgs:
        if c is None:
            continue

        # Map of:  CAMELCASEKEY -> camelCaseKey  for the existing dict ('cfg')
        if mangle_case:
            keysCaseMap = { k.upper(): k for k in cfg.keys() }
            if len(keysCaseMap) != len(cfg):
                raise RuntimeError("Oops. You probably have several camel-case configKey items in your "
                                   "config settings that each map to the same all-caps CONFIGKEY. "
                                   "You can't to that.")
            
        for input_k,v in c.items():

            if mangle_case and input_k.isupper():
                # case-mangling: if we have an all-caps input key, we need
                # to find a corresponding cammel-case key to it.
                try:
                    k = keysCaseMap[input_k]
                except KeyError:
                    k = input_k.lower()
            else:
                # no key-case-mangling
                k = input_k
                
            cfg[k] = v if not isinstance(v, dict) \
                else cfgUnify(cfg.get(k, None), v)
            
    return cfg


class IocApplication(object):
    '''
    Specialized application model for EPICS IOCs.
    
    While frameworks like `pythonSoftIOC` bring a lot of initialization
    code to the table, generally writing a robust application with useful
    features for production concerns itself with more detals, as for
    instance:
    
      - Configuration parameters -- EPICS prefix, timing and polling
        defaults etc.

      - Additional flow variables -- heartbeat and kill switch PVs

      - Keeping track of PV objects (e.g. as created by pythonSoftIOC's
        `builder.aIn/aOut` methods).

      - Ability to rapidly invoke features offered by `emmi.api.exports`,
        e.g. add PVs for the properties of a custom object, possibly based
        on an declarative configuration, e.g. as with
        `emmi.api.exports.ExportObjectFromDict`).

    In creating a "smooth application experience", all these different
    roles have subtle interactions, which are none the less quite generic,
    universal and repetitive for essentially any Python-based IOC.

    This object offers a convenient interface of juggling these requirements.
    
    One of the main premises of the application, beyond the obvious fact that
    it's an IOC, is that every configuration aspect may come from more several
    sources with differing priorites. For instance:
    
       - Default settings with lowest priorites inside the Python code itself

       - On-disk configuration files (e.g. in JSON or YAML format)

       - Environment variables with a specific naming scheme (e.g. prefixed
         by the name of the application), overriding any config file settings

       - Command line arguments, being used with highest priority and overriding
         even enviroment variable settings.

    For this, `IocApplication` holds an internal nested configuration dictionary,
    accessible in the `.conf` attribute. It is of course possible to update the
    dictionary directly. But also the helper functions `addFlatConfig()` and
    `addNestedConfig()` are intended to merge new values form a higher-priority
    dictionary, overriding existing settings where necessary.

    The `.conf` attribute is meant as well for internal use by `IocApplication`
    as for external use and reference by objects that aren't managed by a
    specific `IocApplication` instance.

    Here is a non-exhaustive list of `.conf` variables that `IocApplication`
    reacts to (using the hierarchical sytax for `option.suboption` to reflect
    to entries within the nested dicitonary `.conf["option"]["subobtion"]`):

      - `epics.prefix`: The EPICS PV prefix to use. Ultimately this is used
        by `setupIoc()`, but the latter may be triggered from `__init__()`.

      - `epics.heartbeat`: The interval at which the "::heartbeat" PV is
        updated (see `setupIoc()` for details)

      - `epics.killSwitch`: Whether or not to export a kill switch PV which
        has the ability to shut down the entire IOC remotely (note that there
        may be security implications with this).

      - `epics.defaults`: Default settings for various Connectors (from
        `emmi.api.exports`) that will be passed on from within the
        `exportObject()`  method. See `emmi.api.exports.ExportObjectFromDict()`
        for details, that's what `exportObject()` uses under the hood.

    Configuration settings that aren't used by `IocApplication` are entirely
    the IOC programmer's responsibility. We suggest, however, that one or more
    sub-sections are created within `.conf` to host such settings (e.g.
    `.conf["harp"]` as used by `miniquant-ioc`, an EMMI-based IOC for the
    HydraHarp 400 photon counter by PicoQuant; or `.conf["scpi"]', as used
    by `escpi` a generic SCPI-to-EPICS brige that is built using EMMI and
    `IocApplication`.)

    A minimal `IocApplication` which exports properties of `MyDeviceObject`
    might look like this:

    ```
    #!/usr/bin/python3
    
    from emmi.app import IocApplication
    from emmi.scpi import MagicScpi
    from os import environ
    from json import load as jsn_load

    # very simple example for an object containing a property/attribute
    # that we want to export access to via EPICS PVs in a python IOC
    class MyDeviceObject:
        theProperty = 3.14

    dev = MyDeviceObject()

    # This one might for example contain something like:
    #   { 'epics': { 'prefix': 'BAR' } }
    cfg = jsn_load(open("./simple-ioc.json"))

    # Initialize with default EPICS prefix of FOO.
    # Also suppress the initialisation of the IOC for now, because
    # we may want to load even more configuration options.
    app = IocApplication (prefix="FOO", setupIoc=False)

    # We want to use the settings from JSON file. These will override
    # existing settings with the same key; e.g. after this, the
    # EPICS prefix might actually be set on track for "BAR".
    app.addNestedConfig(cfg)

    # Add support for magic configuration by environment variables.
    # For instance, after this, the variable MYIOC_EPICS_PREFIX=MOO
    # will actually override the PV prefix defined at runtime from "FOO",
    # or "BAR" defined in the config file, to "MOO" defined in the env-var.
    app.addFlatConfig(os.environ, prefix='MYIOC')

    # Initialization of IOC. This will already create a 'FOO::heartbeat'
    # and 'FOO::killSwitch` PV.
    app.setupIoc(killSwitch=True)

    # Add our object-specific PVs -- in this case, for the
    # MyDeviceObject.theProperty attribute.
    app.exportObject(dev, settings={ 'recordType': 'property',
                                     'property': { 'name': 'theProperty',
                                                   'kind': 'analog' } })

    # Finally run the IOC. After this, the PVs are available on
    # the network to be used and abused with caget/caput.
    app.runIoc()
    ```

    This application is actually available verbatim form the `examples/`
    subdirectory of the main `emmi` sources tree -- you are encouraged
    to try this out!

    `IocApplication` works hand in hand with `emmi.api.exports` to make
    it easy to use a declarative interface for which properties/attributes
    to be exported as PVs.
    '''
    
    def __init__(self, prefix=None, cfg=None, setupIoc=False):
        '''
        Initialize an IOC application based on pythonSoftIOC.
        
        Parameters:
        
          - `prefix`: the variable / device prefix to use for the EPICS device
        
          - `cfg`: a (possibly nested) configuartion dictionary. Currently, the
            following keys are used:
            - `epics.prefix`: the IOC variable / device prefix. If present, this
              overrides the `prefix` parameter from `__init__()`.

          - `setupIoc`: if set to `True`, this will automatically call the
            `setupIoc()` method with default parameters, which needs to be done
            before the IOC is ready to accept `exportObject()` and execute.
            However, generally you don't want to do that if you have multiple
            configuration sources (e.g. YAML files, environment variables etc)
            to be loaded in additio to `cfg`, and which may not yet be available
            at the point at which your `IocApplication` is being defined.
        '''
        
        self.conf = cfg or dict({})

        if prefix is not None:
            self.conf.setdefault('epics', {}).setdefault('prefix', prefix)

        if setupIoc:
            self.setupIoc()
                 

    def addNestedConfig(self, cfg):
        self.conf = cfgUnify(self.conf, cfg)


    def addFlatConfig(self, cfg, prefix='', separator='_', subsection=None):
        nested = cfgFromFlat(cfg, prefix, separator)
        self.addNestedConfig(nested if subsection is None else {subsection: nested})


    def testModeRequested(self):
        '''
        Returns True if test mode was requested of the IocApplication.
        The application itself does not behave differently, but external
        modules (e.g. hardware initialisation) might.

        NOTE: This should be obsolete pretty soon. It's not a good idea
        for code to differentiate its behavior depending on whether
        it's supposed to be in test mode or not.
        '''
        return self.conf['epics']['prefix'].endswith('TEST')        
        

    def setupIoc(self, prefix=None, heartbeat=1.0, killSwitch=True):
        '''
        Initializes the IOC part of the application. If `prefix` is specified,
        it overrides whatever prefix was set in the configuration system.
        Note that only one PV is initialized here -- the obligatory 'heartbeat'
        PV that every EMMI IocApplication has and which just implements an
        ever-incrementing counter with a fixed frequency (default: 1 second).
        '''

        # If prefix is not 'None', override the cfg.epics.prefix.
        if prefix is not None:
            self.conf.setdefault('epics', {})['prefix'] = prefix

        # Set some defaults if they're not specified in cfg.epics
        self.conf.setdefault('epics', {}).setdefault('heartbeat', heartbeat)
        self.conf.setdefault('epics', {}).setdefault('killSwitch', killSwitch)

        self.epicsPrefix = self.conf['epics']['prefix']
        logging.info("Using EPICS device prefix: %s" % self.epicsPrefix)
        
        # the epics part
        from softioc import softioc, builder, asyncio_dispatcher

        self.softioc = softioc
        self.iocBuilder = builder
        self.iocDispatch = asyncio_dispatcher.AsyncioDispatcher()
        self.iocBuilder.SetDeviceName(self.epicsPrefix)

        # the device property part
        self.pv = {}

        if self.conf['epics']['heartbeat'] is not None:
            self.pv['heartbeat'] = self.iocBuilder.aIn('heartbeat', initial_value=0)

        if self.conf['epics']['killSwitch']:
            self.pv['killSwitch'] = self.iocBuilder.boolOut('killSwitch', initial_value=False,
                                                            on_update=self.die)

        self.prefix = self.conf['epics']['prefix']            


    def die(self, really=True):
        '''
        Turns off the runLoop variable if `really` is `True`. This is needed
        for the killSwitch option of the application (which, once activated,
        should be impossible to stop).
        '''
        if really:
            self.runLoop = False


    async def heartbeat(self):
        '''
        This is the "heartbeat" loop of the application.
        '''
        self.runLoop = True
        counter = 0
        while self.runLoop:
            self.pv['heartbeat'].set(counter)
            counter += 1
            await asyncio.sleep(self.conf['epics']['heartbeat'])
        self.running = False


    def startIoc(self):
        '''
        Starts the IOC. In the pythonSoftIOC implementation, this just registers
        our own `heartbeat()` loop with the dispatcher and initialises the
        IOC (see `pythonSoftIOC.iocInit()`).
        '''
        self.iocBuilder.LoadDatabase()
        self.iocDispatch(self.heartbeat)
        self.softioc.iocInit(self.iocDispatch)
        self.running = True


    def stopIoc(self):
        '''
        Signalizes the heartbeat loop that it has to stop. This in turn will make
        the main loop of `runIoc()` stop.
        '''
        self.runLoop = False
    

    def runIoc(self, exit=True):
        '''
        Calls startIoc() and waits for it to return (which may be never).
        If `exit` is set to `True` (the default), the pythonSoftIOC `exit()`
        method is called, which kills the application.
        '''
        
        self.startIoc()
        
        while self.running:
            time.sleep(0.1)

        if exit:
            self.softioc.exit()


    def exportObject(self, device_obj, settings):
        '''
        Takes properties of object `device_object` and generates EPICS PVs
        according to the dicitonary `settings`. `settings` is a (usually YAML-generated)
        declarative format as defined in `emmi.api.exports`.
        This is actually just a wrapper for `emmi.api.exports.ExportObjectFromDict()`.
        '''
        defaults = self.conf.get('epics', {}).get('defaults', None)
        return ExportObjectFromDict(self.iocDispatch, device_obj, settings,
                                    recordTypeDefaults=defaults)
