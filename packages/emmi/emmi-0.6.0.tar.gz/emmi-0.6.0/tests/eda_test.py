#!/usr/bin/python3

import pytest, time, asyncio
from emmi.api.exports import ConnectorKinds, SignalConnector, ActorConnector, \
    PropertyConnector  
    
    
class TestSoftIOC(object):
    '''
    Quick'n Dirty way of setting up an IOC and for testing.
    '''
    def __init__(self, prefix):
        from softioc import softioc, builder, asyncio_dispatcher
        self.builder = builder
        self.dispatcher = asyncio_dispatcher.AsyncioDispatcher()
        self.builder.SetDeviceName(prefix)

        self.exit = softioc.epicsExit

        self.prefix = prefix

        from epics import caget, caput, cainfo
        self.caget = caget
        self.caput = caput
        self.cainfo = cainfo

    def start(self):
        from softioc import softioc
        self.builder.LoadDatabase()
        softioc.iocInit(self.dispatcher)

    def pv(self, name):
        return "%s:%s" % (self.prefix, name)


class ValueAccess(object):
    '''
    Trick class that documents when a getter was called.
    User for unit testing.
    '''
    def __init__(self, val):
        self.tstart = time.time()
        self.count = 0
        self.value = val

    @property
    def age(self):
        return time.time()-self.tstart
        
    def __call__(self, *args):
        self.count += 1
        if len(args) == 0:
            return self.value
        else:
            self.value = args[0]

    def valid(self, mincount=1, age=3.0):
        while self.age < age:
            if self.count >= mincount:
                return True
        return False


@pytest.fixture
def random_value():
    import random
    return random.random()

@pytest.mark.skip(reason="not working yet")
def test_jump_through_hoops(random_value):
    ioc = TestSoftIOC("EMMI_UNITTEST")
    
    a1 = ValueAccess(random_value)
    sen = SignalConnector(ioc.dispatcher, name="signal", kind='analog', access=a1, pollPeriod=0.1)

    a2 = ValueAccess(random_value)
    act = ActorConnector(suffix="actor", access=a2, kind='analog')

    a3 = ValueAccess(0.0)
    prop = PropertyConnector(ioc.dispatcher, name="prop_", kind='analog', access=a3)
    
    ioc.start()
    
    assert a1.valid(mincount=5, age=3.0)

    act.pv.set(3.14)
    time.sleep(1.0)
    assert a2.value == 3.14

    prop.val.pv.set(random_value)
    time.sleep(1.0)
    assert a3.value == random_value

