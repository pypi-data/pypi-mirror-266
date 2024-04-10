
#!/usr/bin/python3

import time
import asyncio
import logging

from functools import partial

logger = logging.getLogger(__name__)

class MockMotor(object):
    '''
    The simplest of the simplest motors: can only move, report position and stop.

    Also exports `.errors` and `.flags`. The first is expected to be an empty
    list when the motor state is "ok" (i.e. no error), or a list with one
    or several objects (e.g. strings) when errors with the motor persit.
    Calling `.clear()` clears the error list.

    The `.flags` member is expected to be an enumerable data type (list,
    tuple, dictionary, set or something similar) to convey supplementary
    information about motor events, e.g. triggering of low / high switch
    limits etc.

    With the exception of limit switches (see `.__init__()`), `MockMotor`
    does not intrinsically handle or simulate any other switches.
    '''

    def __init__(self, *args, **kwargs):
        ''' Creates a mock-up of an EDA Motor.

        Accepts all args as a courtesy of being a good mock-up class,
        but ignores most of them. A number of arguments are specific
        to the mock class. They are listed below.

        Args:
            mock_timeslice: a measure of how "fast" a mock motor is moving.
              Every `.goto()` call on a mock motor will execute a movement
              of the specified distance in exactly `mock_timeslice` seconds,
              regardless of the distance.

            limits: tuple of `(low, high)` to simulate the lower,
              respectively higher hardware limits. If any of those
              is reached in the mocking position, `.flags` will contain
              `"LLIM"` or `"HLIM"`, respectively. Alternatively, this can
              also be a dictionary with two or three items. If it's two
              items, it's used as the low/high limits, and the
              keys are used in `.flags` instead of `"HLIM"`/`"LLIM"`.
            
        '''
        self.mock_timeslice = kwargs.get('mock_timeslice', 5.0)
        self.start = 0.0
        self.target = 0.0
        self.tstamp = 0.0
        self.errors = []
        self._limits = kwargs.get('limits', None)
    
    def where(self):
        '''
        Returns current position -- that is the position that we'd be currently
        having if we'd wanted to go from "current" towards "target" within
        the timeslice "mock_timeslice"
        '''
        tdelta = (time.time()-self.tstamp)
        if tdelta > self.mock_timeslice:
            tdelta = self.mock_timeslice
        dist = self.target-self.start
        return self.start + dist * (tdelta/self.mock_timeslice)

    def goto(self, val):
        '''
        Sends command to move to position (doesn't wait)
        '''
        self.start = self.where()
        self.target = val
        self.tstamp = time.time()

    def stop(self):
        '''
        Sends command to stop (doesn't wait). Technically, we'll be still
        in state "moving" for a while after this, but we'd be moving
        towards the position we're already onto.
        '''
        if self.moves():
            self.goto(self.where())

    def moves(self):
        '''
        Returns True if the motor moves. We fake this by testing whether
        we're still within the "timeslice". This has the added benefit
        that sometimes moves() returns False right away (i.e. if we weren't
        moving in the first place), and sometimes still returns False
        for a considerate amount of time (i.e. until the end of the current
        slice) if we were moving and just received a stop() command.
        '''
        now = time.time()
        return (now - self.tstamp) <= self.mock_timeslice

    def clear(self):
        '''
        Clears all outstanding error flags (they may pop up again).
        '''
        self.errors = []

    @property
    def flags(self):
        ''' Check for HLIM / LLIM and return the appropriate strings.

        Strings are either default "HLIM", "LLIM" respectively, or
        the keys of the `._limits` parameter.
        '''
        if self._limits is None:
            return set()

        f = set()

        lk = [k for k in self._limits.keys()]

        low = ('LLIM', self._limits[0]) if not isinstance(self._limits, dict) \
            else (lk[0], self._limits[lk[0]])

        high = ('HLIM', self._limits[-1]) if not isinstance(self._limits, dict) \
            else (lk[-1], self._limits[lk[-1]])

        p = self.where()
        
        if p <= low[1]:
            f.add(low[0])

        if p >= high[1]:
            f.add(high[0])

        return f
    

class MotorEngine(object):
    '''
    Generic motor engine class. Essentially cycles through the states
    as it should, and serves the most basic properties `position` and
    `position_relative` correctly. It's based on generic True/False
    conditional procedures to decide when to switch.

    In its default incarnation, the conditionals are just generic waiting
    functions (1 second for anything), so it can be used as a mock-up for
    unit testing. But if you replace the conditionals by things that do
    "real stuff", it's actually usable for production.
    '''
    
    def __init__(self, motor=None):
        
        self.__motor = motor or MockMotor()

        # current state
        self.__state = "INIT"
        self.__old_state = None

        # sub-type of the "BUSY" state
        self.__business = None

        # When this is not None, it is expected to hold a tuple
        # (name, go_callable, busy_callable) that triggers a new BUSY state.
        self.__scheduled_go = None

        # This is the similar to "__scheduled_go", only that the name is "STOP",
        # the go-callable is motor.stop(), and busy_check is motor.moves().
        # It's necessary to keep this separate from __scheduled_go because this
        # is actually supposed to be able to preemt __scheduled_go at any time.
        # This needs for special handling in the code.
        self.__scheduled_stop = None


    @property
    def business(self):
        if self.__state in [ "BUSY", "STAGING" ]:
            return self.__business
        else:
            return None
    

    @property
    def errors(self):
        return self.__motor.errors


    def state_INIT(self, state):
        # ...put init stuff here.
        return "IDLE"


    # STOP state: trigger STOP hardware command, stay here while hardware is moving
    def state_enter_STOP(self, state):
        if self.__scheduled_stop:
            self.__scheduled_stop[1]()
        return state

    def state_STOP(self, state):
        if self.__scheduled_stop and self.__scheduled_stop[2]():
            return "STOP"
        self.__scheduled_go = None
        self.__scheduled_stop = None
        return "IDLE"


    # BUSY state: trigger busy action, stay here while action not done
    def state_enter_STAGING(self, state):
        
        if self.__scheduled_stop: # STOP trumps everything
            logger.info(f'STAGING: {self.__scheduled_go[0]} requested, but also have a stop request pending')            
            return "STOP"
        
        logger.info(f'STAGING: {self.__scheduled_go[0]}')
        self.__scheduled_go[1]()
        return state

    def state_STAGING(self, state):
        if self.__scheduled_go[2]() == True:
            return "BUSY"


    def state_BUSY(self, state):
        
        if len(self.errors) > 0:
            return "STOP"
        
        if self.__scheduled_stop is not None:
            return "STOP"
        
        if self.__scheduled_go[2]() == False:
            return "STOP"
    

    # IDLE state: stay here until there is work scheduled.
    def state_IDLE(self, state):
        
        if len(self.errors) > 0:
            logger.debug(f'Have {len(self.errors)}, STOP-ing motor')
            return "STOP"
        
        if self.__scheduled_go is not None:
            self.__business = self.__scheduled_go[0] or "(default)"
            logger.info(f'Going BUSY, business {self.__business}')
            return 'STAGING'


    def state_ERROR(self, state):
        '''
        The only way we can leave ERROR is by clearing/going to IDLE
        '''
        if len(self.errors == 0):
            return "IDLE"


    # There's no escape from death.
    def state_FAIL(self, state):
        pass
             

    ## State procedures -- execute the current state procedure.
    ## If the state (just) switched, execute "state_enter_{state}" instead.    
    def state_proc(self):

        state = self.__state

        # BUSY state needs some special treatment -- it may be of the form 'BUSY.{}'
        s_proc_name = state if not state.startswith("BUSY.") else state[:4]
        s_proc = getattr(self, f'state_{s_proc_name}')

        #print(f"State run: {self.__old_state} {state}")

        # If we just entered the current state, maybe there's a dedicated state_enter_{...}
        if state != self.__old_state:
            logger.info ("State: %s -> %s" % (self.__old_state, state))
            try:
                s_proc = getattr(self, f'state_enter_{state}')
            except AttributeError:
                pass

        new_state = s_proc(state)
            
        self.__old_state = state

        if new_state is not None:
            self.__state = new_state

        return self.__state


    async def run(self, period=0.01, stop_on_fail=True):
        '''
        Async function to run the Motor Engine
        '''
        if self.__state == "FAIL":
            raise RuntimeError("Attempted to start a motor engine in a failed state")

        while (self.__state not in [ "FAIL" ]) or (not stop_on_fail):
            try:
                self.state_proc(self.__state)
                await asyncio.sleep(period)
            except Exception as e:
                logger.error(f'Motor engine failed: {str(e)}')
                self.__state == "FAIL"

        logger.error("Motor engine in FAIL state")

        
    @property
    def state(self):
        '''
        Returns the current state
        '''
        return self.__state

    
    def step(self):
        '''
        Returns the current state after having performed one state-step.
        '''
        return self.state_proc()
    
    
    # Current position -- getter reads out the hardware, setter
    # is a bit more complicated because we have to acknowledge
    # the current state (i.e. can't just override current states).
    @property
    def position(self):
        return self.__motor.where()
    
    @position.setter
    def position(self, val):
        self.go(val)

    
    def stop(self):
        '''
        Triggers an exit from any BUSY state into stop.
        '''        
        self.__scheduled_stop = ("stop",
                                 lambda: self.__motor.stop(),
                                 lambda: self.__motor.moves())
        logger.debug(f"Stop requested, current state is {self.state}")
        
        
    def go(self, call, *call_args,
           name=None,
           done_flag=None,
           busy_flag=None,
           busy_check=None,
           **call_kwargs):
        '''
        Triggers a work session / BUSY round.

        Args:
        
            call: work task. If it's a callable, it's called as it is.
              If it's a string, it is interpreted to be a member of the motor instance
              that the Engine was passed, and is called with `*call_args` and `**call_kwargs`
              as parameters. `call` can be omitted altogether, in which case the
              motor's `.goto()` function is assumed.

            name: if not `None`, then the full state will be `BUSY.{name}`. Otherwise
              it's just `BUSY` if `call` is a true callable, or `BUSY.{call}` if `call`
              was passed as a string.

            done_flag: if not `None`, the presence of this flag in `motor.flags` indicates
              that the work has finished.

            busy_flag: if not `None`, the presence of this flag in `motor.flags` indicates
              that the device is still busy performing this task.

            busy_check: if not `None`, it is expected to be a callable which returns `True`
              while the device is still busy peforming the task.

            *call_args, **call_kwargs: named and unnamed arguments to pass to `call`.

        Returns: the result of the `call` call.
        '''

        # go call
        if hasattr(call, "__call__"):
            # callable is an explicit lambda or similar
            callable = call
            
        elif isinstance(call, str):
            # callable is a string-named member of the motor
            callable = getattr(self.__motor, call)
            if name is None:
                name = call

        else:
            # default parameter 'call' is a number, callable is suppsoed to be 'goto',
            # and we need to place the number in front of the call_args list, in fact.
            callable = self.__motor.goto
            call_args = tuple([call] + list(call_args))
            name = "goto"

        # busy call
        if hasattr(busy_check, "__call__"):
            busy_callable = busy_check
            
        elif done_flag is not None:
            busy_callable = lambda: done_flag not in self.__motor.flags
            
        elif busy_flag is not None:

            # we'll stay in busy as long as this returs True
            #def moo():
            #    print(f"looking for {busy_flag} in {self.__motor.flags}")
            #    return busy_flag in self.__motor.flags
            #busy_callable = moo
            
            busy_callable = lambda: busy_flag in self.__motor.flags
            
        else:
            busy_callable = self.__motor.moves

        self.__scheduled_go = (name,
                               partial(callable, *call_args, **call_kwargs),
                               busy_callable)

        logger.debug("New go:", self.__scheduled_go)




class WorkerObject(object):
    '''
    Interface for a worker object to be managed by a WorkerEngine.
    '''
    def work(self, params):
        pass

    def abort(self):
        pass

    def clear(self):
        pass

    def isBusy(self):
        pass


class WorkerEngine(object):
    '''
    This models an EPICS device that "does something." It's the precursor of
    a positioner (e.g. a Motor) in the sense that it has a simple state
    diagram which shows whether the device is currently busy performing a
    task ("BUSY"), or free to accept tasks ("IDLE").

    The complete state diagram is as follows:

      - INIT: starting up, ends up in IDLE

      - IDLE: waiting for tasks, can exit through BUSY or ERROR

      - BUSY: currently performing, can exit through DONE or ERROR

      - DONE: done performing, cleaning up / waiting to go to IDLE

      - ERROR: error, user needs to acknowledge

      - FAIL: irrecoverable error

    The state names are configurable.
    '''
    
    def __init__(self, stateNames=None):

        self.states = stateNames or {
            'INIT': 'INIT',
            'IDLE': 'IDLE',
            'BUSY': 'BUSY',
            'DONE': 'DONE',
            'ERROR': 'ERROR',
            'FAIL': 'FAIL'
        }

        # All should return the 
        self.state_workers = {
            'INIT': self.state_INIT,
            'IDLE': self.state_IDLE,
            'BUSY': self.state_BUSY,
            'DONE': self.state_DONE,
            'ERROR': self.state_ERROR,
            'FAIL': self.state_FAIL
        }

        # Initial work do be done when entering a state -- no return value.
        self.state_entries = {
            'INIT': self.enter_state_INIT,
            'IDLE': self.enter_state_IDLE,
            'BUSY': self.enter_state_BUSY,
            'DONE': self.enter_state_DONE,
            'ERROR': self.enter_state_ERROR,
            'FAIL': self.enter_state_FAIL
        }

        self.__state = self.states["INIT"]
        self.__do_run = True
        

    def enter_state_generic(self):
        pass

    # Ignore INIT for now, jump straight to IDLE
    enter_state_INIT = enter_state_generic
    def state_INIT(self):
        return "IDLE"
    
    # FAIL is easy, it does nothing.
    def enter_state_FAIL(self):
        log.error("Entered FAIL -- tttthat's all, folks!")
    def state_FAIL(self):
        return "FAIL"

    # The rest... just wait.
    enter_state_IDLE = enter_state_generic
    enter_state_BUSY = enter_state_generic
    enter_state_DONE = enter_state_generic
    enter_state_ERROR = enter_state_generic

    async def run(self, period=0.1):
        while self.__do_run:
            tstart = time.time()
            current_state = self.__state
            new_state = self.state_workers[current_state]()
            if new_state != current_state:
                logger.info("State: %r -> %r" % (current_state, new_state))
                self.__state = new_state
                self.state_entries[new_state]()
            tdiff = time.time()-tstart
            await asyncio.sleep(tdiff)
        
