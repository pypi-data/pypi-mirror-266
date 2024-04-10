#!/usr/bin/python3

import pytest
from emmi import scpi

import pyvisa

import parse

@pytest.fixture
def huber_device():
    ''' Returns a test device to use. '''

    # Virtual device
    return { 'resource_manager': 'tests/pytest_dev.yaml@sim',
             'device': 'ASRL4::INSTR' }

    # Real device
    #return { 'resource_manager': '@py',
    #         'dev': 'TCPIP::192.168.136.216::INSTR' }

    
def test_pharos(huber_device):

    dev = scpi.MagicHuber(**huber_device)
    
    #assert "Huber" in dev.idn()
    
    node = scpi.PropertyNode(dev, 'OSC_OUT_STATE')
    with pytest.raises(RuntimeError):
        print("getter 2:", node())

#    print("shutter:", dev.query('SHUTTER_STATE'))

#    shut = scpi.PropertyNode(dev, 'SHUTTER_STATE',
#                             getter_fmt='{name:s}',
#                             #unwrap='never',
#                             #cast='SHUTTER_CTRL: {:d}, {:d}, {:d}')#
#
#
#                             unwrap='always',
#                             cast=('SHUTTER_CTRL: {:d}', '{:d}', '{:d}'))
#                             
#                             #unwrap='never',
#                             #cast=lambda s: parse.parse('{ignore}{:d}, {:d}, {:d}', s).fixed )
#    
#    print("shutter:", shut())
#
#    print(shut()[0], shut()[1], shut()[2])    
#
#    #print(shut()[0][0], shut()[1][0], shut()[2][0])
