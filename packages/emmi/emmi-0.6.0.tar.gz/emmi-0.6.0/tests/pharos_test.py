#!/usr/bin/python3

import pytest
from emmi import scpi

import pyvisa

import parse

@pytest.fixture
def pharos_device():
    ''' Returns a test device to use. '''

    # Virtual device
    return { 'resource_manager': 'tests/pytest_dev.yaml@sim',
             'device': 'ASRL1::INSTR' }

    # Real device
    #return { 'resource_manager': '@py',
    #         'dev': 'TCPIP::192.168.136.216::INSTR' }

    
def test_pharos(pharos_device):

    dev = scpi.MagicPharos(**pharos_device)
    
    #rm = pyvisa.ResourceManager(pharos_device['resource_manager'])
    #dev = rm.open_resource(pharos_device['dev'],
    #                       read_termination='\n',
    #                       write_termination='\r')

    assert "PHAROS UART" in dev.kdev.query('VERSION')

    node = dev.OSC_OUT_STATE

    print("Version:", dev.kdev.query('VERSION'))
    print("Query:", dev.kdev.query('OSC_OUT_STATE'))
    print("Node:", node())

    assert type(node()) == int

    #print ("getter 1:", dev.query('OSC_OUT_STATE'))

    #node = scpi.PropertyNode(dev, 'OSC_OUT_STATE',
    #                         getter_fmt='{name:s}',
    #                         unwrap='always',
    #                         cast='OSC_OUT_CTRL: {:d}')

    #print("getter 2:", node())

    #print("shutter:", dev.query('SHUTTER_STATE'))

    #shut = scpi.PropertyNode(dev, 'SHUTTER_STATE',
    #                         getter_fmt='{name:s}',
    #                         #unwrap='never',
    #                         #cast='SHUTTER_CTRL: {:d}, {:d}, {:d}')
    #
    #                         unwrap='always',
    #                         cast=('SHUTTER_CTRL: {:d}', '{:d}', '{:d}'))
    #                         
    #                         #unwrap='never',
    #                         #cast=lambda s: parse.parse('{ignore}{:d}, {:d}, {:d}', s).fixed )
    # 
    #print("shutter:", shut())
    #
    #print(shut()[0], shut()[1], shut()[2])    
    #
    ##print(shut()[0][0], shut()[1][0], shut()[2][0])
