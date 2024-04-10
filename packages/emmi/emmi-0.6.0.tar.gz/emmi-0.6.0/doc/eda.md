# EMMI Device Architecture

## The Motor State Machine

EMMI uses a simple yet extensible motor interface. The philosophy is that
we're considering an *ideal* motor in our model. We don't concern ourselves
with backlash compensation, acclereation ramps etc. We care about ***what** the
motor is supposed to do*, as opposed to ***how** it is going to do it*.

For this, we consider the following properties:
  
  - `position`: R/W property which returns the current motor values,
    respectively moves to the specified absolute value when written to

  - `state`: a R/W property that indicates the current state of the
    (abstract) motor device; can be explicitly set within specific
	parameters to advance to specific states.
	
The state diagram of a motor looks like this in its most simple form:
```
          ┌──────────┐
          │   INIT   ├┄┄┄┄┄┄┄┄┄┄┄┄►┄┄┐
          └────┬─────┘               ┊
               ▼                     ┊
          ┌────┴─────┐               ┊
          │          ├┄┄┄┄┄┄┄┄┄┄┄┄►┄┄┤
  ┌───►───│   IDLE   ├┄┄┄┄┄►┄┄┐      ┊
  │       └────┬─────┘        ┊      ┊
  │            ▼              ┊      ┊
  │   ┌┈┈┈┈┈┈┈┈┴┈┈┈┈┈┈┈┈┈┐    ┊      ┊
  │   ┊                  ├┄┄┄┄┄┄┄┄►┄┄┤
  │   ┊     STAGING      ┊    ┊      ┊
  │	  ┊                  ┊    ┊      ┊
  │   └┈┈┈┈┈┈┈┈┬┈┈┈┈┈┈┈┈┈┘    ┊      ┊
  │            ▼              ┊      ┊
  │   ┌┈┈┈┈┈┈┈┈┴┈┈┈┈┈┈┈┈┈┐    ┊      ┊
  │   ┊                  ├┄┄┄┄┄┄┄┄►┄┄┤
  │   ┊     BUSY...      ┊    ┊      ┊
  │   ┊                  ┊    ┊      ┊
  │   └┈┈┈┈┈┈┈┈┬┈┈┈┈┈┈┈┈┈┘    ┊      ┊
  │            ▼              ┊      ┊
  │       ┌────┴─────┐        ┊      ┊
  ├───◄───┤          ├┄┄┄┄┄◄┄┄┘      ┊
  │       │   STOP   ├┄┄┄┄┄┄┄┄┄┄┄┄►┄┄┤
  │       └────┬─────┘               ┊
  │            ▼                     ▼
  │       ┌────┴─────┐           ┌───┴────┐
  └───◄───┤  ERROR   ├┄┄┄┄┄┄┄┄►┄┄┤  FAIL  │
          └──────────┘           └────────┘
```

Which translates to:

  - `INIT` is the initial states after startup, device is undergoing
    custom configuration and is not ready yet.

  - `IDLE` device is ready to perform according to commands
	 
  - `BUSY` is the state in which device is performing, most likely moving.
    `STAGING` is a helper state for `BUSY`, in which we're starting to
	do useful work, but not all aspects of the underlying hardware yet
	reflect the state of doing that.
  
  - `STOP` is the state in which the device is decelerating with the
    intention of coming to a standstill. This can be part of a regular
    `IDLE`-`BUSY` cycle (i.e. returning to `IDLE` once standstill is reached),
	or can be an intermediate state towards an `ERROR` state, ensuring
	that the device is stopped for handling of errors.
    
  - `ERROR` is a well-defined state which represents the device *not*
    peforming, but which is still part of the "well defined" behavior of
	the device. Such a state, for instance, is reaching hardware limits
	or impossibility to execute a command (e.g. because coordinates are
	outside of allowed range). The device is always in a standstill
	when in `ERROR`, which is ensured by the fact that `ERROR` is only
	entered through `STOP`. `ERROR` can be entered from all "regular"
	operational states (`IDLE`, `BUSY` or `STOP`), but not from `INIT`
	-- initialisation errors result in `FAIL`.
    
  - `FAIL` is the state of a fatal error, incompatible with "defined
    behavior" of the device. It is a terminal state, meaning that there
	is no system-supported from this state. A complete reinitialisation,
	typically encompanied by a power cycle or hardware reset is the
	action to be performed to advance from `FAIL`. It can be entered
	from any other state.

## Modeling Busy States

The `BUSY` state deserves extra explanation, as it's the main mechanism
for extending the functionality of a motor.

In its most simple form, a motor has only one task: to move an (abstract)
axis to a specified value. However, slightly more complex real-world
applications may differentiate more strictly on the type of movement
to be performed:

  - a **slewing** movement is performed autonomously with maximum
    speed within parameters, towards a specific target;

  - a **jogging** movement, e.g. triggered by a joystick, is performed
    with a predefined speed as long as a condition (button press)
	actively persists;
	
  - a **tracking** movement is a movement that is bound to time
    constraints, e.g. hitting specific coordinates at specific times;
	
  - a **homing** movement may be used to define a slewing towards
    a hard-coded parking position;
	
  - a **dialing** or **tweaking** movement may be a manual correction
    on top of a predefined tracking path, etc.

Even more complex moves require several stacked types of movements
(e.g. a *tracking* requires a *slewing* into position first, and
accept *tweaking* input while performing the actual tracking).

As far as EMMI is concerned, we don't care about the complexity of
the movement itself, we only care about representing high-level
states of operation at an EPICS interface level -- roughly speaking,
to us, the motor "does" or "doesn't do" anything. To model this,
we allow splitting the `BUSY` state into sub-states, hiearchically
denoted (e.g. `BUSY.SLEW` or `BUSY.TRACK`...). The restriction is
that they all must either end in `STOP`, before returning to `IDLE`
or entering `ERROR`, or must definitively fail directly into `FAIL`.

Sometimes when triggering a `BUSY` state the underlying hardware
flags do not (yet) reflect that, and this may interfere with the
duration of the `BUSY` state. For instance, a typical interaction
with a motor would be to trigger a "move", then stay in `BUSY` for
as long as a specific hardware flag indicates "moving", and leave
`BUSY` for `STOP` when the flag doesn't indicate "moving" anymore.
Now if the "moving" flag takes a while to appear, we risk entering
`STOP` even before the `BUSY` action started propertly.

This is what the `STAGING` state is for: to wait until all the 
state details of the underlying hardware are consistent with the
expected `BUSY` state. For all intents and purposes, `STAGING`
is to be treated as `BUSY` by the upper application.

There is supplementary state that may be controlled by variables
and properties
which EMMI will happily manage and pass through to the EPICS interface,
but will not understand or touch -- e.g. speed limits, accelerations,
homing coordinates etc.

## Custom Actions and Custom Busy States

As it is customary with EPICS, EMMI can manage designated
boolean PVs to trigger these states and indicate the successful
performance of the action. This allows to a certain degree easy
implementation of the "HOMF/D", "TWF/D" or "JOG" class of commands of
an
[EPICS motor record](https://epics.anl.gov/bcda/synApps/motor/R7-1/motorRecord.html) by means of specialized `BUSY` states.

[FXIME: explain `.addBusy()`!]

## Motor Control Layers

This results in a 4-layer architecture that leads from the hardware
controls to the EPICS variables:
 
  - The **Axis Control** is the layer (within Python) which
    directly serves the hardware interface API, e.g. typically a 
	lass wrapped around a pySerial interface.
	
  - The **Engine** is a layer which enforces an API compatible
    the state diagram above, with the most prominent properties
	`position` and `state` as described.

  - The **Connector** is a translator between the motor engine and 
    a generic EPICS IOC generator, e.g. as provided by pythonSoftIOC.
	
  - The **IOC Generator** is a library that does the actual EPICS work.
  
The first two are part of EDA, the EMMI Device Architecture, while
the latter two are documented in the [EMMI Export API](./api.md),
respectively the [EMMI Application API](./app.md).
  
In the spirit of "rapid integration", we acknowledge that typically the
first layer has already been written, and there is legitimate concern 
to reuse it.
The only restriction EMMI imposes is for the *Axis Control*
to not block.

For the last layer, EMMI (currently) makes heavy use of pythonSoftIOC,
but it's intended to be fairly independent of the underlying IOC
mechanism
	
What remains is the *Engine* and *Connector*, which EMMI
implements in the classes [`MotorEngine`]() and [`MotorConnector`]()
within [`emmi.eda`](../src/emmi/eda.py).

## Hardware Access through `MotorConnector`

Typically, `MotorConnector` needs to specifically dock to user-supplied
*Axis Control* code. The peferred way to do this is to write
one from scratch, duck-type compatible with EMMI's `MotorConnector`.
As such, it needs to implement the following API:
	 
The alternative is to write your own *Motor Controller* from scratch,
paying attention to reflect the *Engine* API, as described above.
	 
As a side note, this architecture also gives a natural layer at which
to attach useful, yet hardware-independent, unit testing: by replacing
the `MotorConnector` with a mock-up class that behaves as it's supposed
to, all the layers between there and the EPICS interface can be tested
in a suitable, automated CI/CD environment.
