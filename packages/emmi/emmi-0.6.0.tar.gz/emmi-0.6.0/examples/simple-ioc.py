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
app.addFlatConfig(environ, prefix='MYIOC')

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
