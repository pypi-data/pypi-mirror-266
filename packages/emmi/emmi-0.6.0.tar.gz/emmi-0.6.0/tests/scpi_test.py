#!/usr/bin/python3

import pytest
from emmi import scpi

import pyvisa

import asyncio

@pytest.fixture
def visa_scpi_device():
    ''' Returns a test device to use. '''

    # Virtual device
    return { 'resource_manager': 'tests/pytest_dev.yaml@sim',
             'device': 'ASRL3::INSTR' }

    # Real device
    return { 'resource_manager': '@py',
             'device': 'TCPIP::192.168.136.216::INSTR' }

    
def test_property_node_get(visa_scpi_device):
    # Testing the PropertyNode object. Essentially, we want to know that
    # naming is correct, get() / set() work as expected with all associated
    # parsing, etc.
    
    rm = pyvisa.ResourceManager(visa_scpi_device['resource_manager'])
    dev = rm.open_resource(visa_scpi_device['device'],
                           read_termination='\n',
                           write_termination='\n' )

    #print("Available devices:", rm.list_resources())
    #print("Dev ID:", dev.query("*IDN?"))

    # single number parameter, current value is "100"
    n1 = scpi.PropertyNode(dev, "DISP:BACK")
    assert n1.name == "DISP:BACK"
    
    # array (2 elements), current value is "-0.0004, -0.0004"
    n2 = scpi.PropertyNode(dev, "FUNC:GVAL")
    assert n2.name == "FUNC:GVAL"

    # default behavior: automatic, "conservative" casting
    assert type(n1()) == int
    assert n1() == 100
    assert len(n2()) == 2
    assert type(n2()[0]) == float

    # unwrapping: single, never, always
    print("N1:", n1(unwrap="always"))
    assert type(n1(unwrap="always")) == tuple
    assert len(n1(unwrap="always")) == 1
    assert n1(unwrap="single") == 100
    with pytest.raises(ValueError):
        n2(unwrap="single")
    assert type(n2(unwrap="never")) == str

    # casting: int, float, callable
    assert type(n1(cast=None)) == str
    assert type(n1(cast="none")) == str
    assert type(n1(cast="auto")) == int
    with pytest.raises(ValueError):
        # cannot parse "100" as float
        assert type(n1(cast="{:f}")) == float
    assert n1(cast=lambda v: "large" if int(v) > 50 else "small") == "large"

    # tuple-casting
    t = n2(unwrap="auto", cast=(float, str))
    assert len(t) == 2
    assert type(t[0]) == float
    assert type(t[1]) == str

    # complex parsing
    cm = n2(unwrap="never", cast="{first}, {second:f}")
    assert type(cm['first']) == str
    assert type(cm['second']) == float


@pytest.mark.asyncio
async def test_async_query(visa_scpi_device):
    rm = pyvisa.ResourceManager(visa_scpi_device['resource_manager'])
    dev = rm.open_resource(visa_scpi_device['device'],
                           read_termination='\n',
                           write_termination='\n' )

    n1 = scpi.PropertyNode(dev, "DISP:BACK") # single number (int, mostly)
    n2 = scpi.PropertyNode(dev, "FUNC:GVAL") # two floats (formatter is {})

    print(f'Sync read: {n1.get()}, {n2.get()}')

    #v1 = await n1.async_get()
    #v2 = await n2.async_get()

    #del n1
    #del n2
    #print("deleted")

    #print(f'Async read: {v1}, {v2}')
    
    

def test_property_node_set(visa_scpi_device):
    # Testing the PropertyNode object.
    
    rm = pyvisa.ResourceManager(visa_scpi_device['resource_manager'])
    dev = rm.open_resource(visa_scpi_device['device'],
                           read_termination='\n',
                           write_termination='\n' )

    n1 = scpi.PropertyNode(dev, "DISP:BACK") # single number (int, mostly)
    n2 = scpi.PropertyNode(dev, "FUNC:GVAL") # two floats (formatter is {})

    n1(37)
    assert n1() == 37

    n2(3.14e-4, 7.62e-4)
    assert len(n2()) == 2
    assert n2()[0] < 3.15e-4 and n2()[0] > 3.13e-4

    #n2(

    
def test_scpi_node_branch(visa_scpi_device):
    # Testing branching off

    rm = pyvisa.ResourceManager(visa_scpi_device['resource_manager'])
    dev = rm.open_resource(visa_scpi_device['device'],
                           read_termination='\n',
                           write_termination='\n' )

    # test device has property DISP:BACK.
    # we start off in DISP, and try to branch off into BACK.
    
    n1 = scpi.PropertyNode(dev, "DISP")

    assert isinstance(n1.BACK, scpi.PropertyNode)

    assert type(n1.BACK()) == int

    
def test_scpi_open(visa_scpi_device):

    # initialize
    device = scpi.MagicScpi(**visa_scpi_device)
    assert isinstance(device.idn(), str)

    # testing first-level subnode
    assert isinstance(device.DISP, scpi.PropertyNode)
    assert isinstance(device.DISP.BACK, scpi.PropertyNode)

    #assert type(device.DISP.BACK()) == int

    assert device.DISP.BACK.name == "DISP:BACK"

    assert type(device.DISP.BACK()) == int
    
    # test error
    with pytest.raises(KeyError) as e:
        getattr(*(scpi.MagicScpi()))
        assert str(e.value) == 'MAGICSCPI_ADDRESS'


#def test_mock_MockPropertyBranch():
#    
#    foo = scpi.MockPropertyBranch()
#    
#    assert type(foo()) is float
#  
#    foo(2.72)
#    assert foo() == 2.72
#    
#    
#def test_MockScpi(): 
#
#    mock = scpi.MockScpi()
#    assert mock.id() == "Mock SCPI Device"
