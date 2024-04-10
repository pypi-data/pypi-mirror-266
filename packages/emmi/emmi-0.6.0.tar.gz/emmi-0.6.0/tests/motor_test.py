#!/usr/bin/python3

import pytest
import time
from emmi.eda import MotorEngine, MockMotor

import sys

def test_mock_motor():
    tslice = 1.0
    motor = MockMotor(mock_timeslice=tslice, limits={'lo': -3.0, 'hi': +2.0})

    # initial state should be "stopped"
    assert motor.moves() == False

    # moving by dynamic speed, always takes tslice seconds,
    # and .moves() is True during the motion phase
    motor.goto(-2.0)
    assert motor.moves()
    t0 = time.time()
    while motor.moves():
        time.sleep(0.01)
    td = time.time()-t0

    assert motor.moves() == False
    assert td > tslice*0.8
    assert td < tslice*1.2

    # motor stops at lower limit and signals flag.
    motor.goto(-4.0)
    while motor.moves():
        time.sleep(0.01)
    
    assert "lo" in motor.flags
    assert motor.where() < -2.9
    assert motor.where() > -4.1

def test_engine():
    '''
    Very rudimentary test of the engine, using a Mock motor:
      - Initial state is INIT or IDLE
      - After setting position we're BUSY for a while, then IDLE
      - After setting and stopping we're going back to IDLE
    '''
   
    e = MotorEngine(motor=MockMotor(mock_timeslice=1.0))
    assert e.step() in [ "INIT", "IDLE" ]

    # Setting the position.
    # Will need 1 second to move, may or may not need 1 second to stop (?)
    e.go(3.14)
    end = time.time()+2.5
    while time.time() < end:
        time.sleep(0.1)
        assert e.step() in [ "BUSY", "IDLE", "STOP" ]

    e.go(10.0)
    assert e.step() == "BUSY"
    
    e.stop()
    assert e.step() == "STOP"

    end = time.time()+1.5
    while time.time() < end:
        time.sleep(0.1)
        s = e.step()
        
    assert e.step() == "IDLE"

    ## Also need to test that setting a position while already
    ## moving results in ignoring the command.
