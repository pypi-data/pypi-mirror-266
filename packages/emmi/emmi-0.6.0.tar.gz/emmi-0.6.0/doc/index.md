# EMMI Concepts and Components

EMMI is separated in different layers of which either can be used
for specific types of integrations, ranging from rapid "Monday morning"
hacks for attaching an existing non-EPICS capable device to a beamline,
to a writing full-fledged EPICS-IOC support for your device:

  - [The EMMI Application Support (APP)](#emmi-application) offers
    abstract "boilerplate" base classes for commonly used tasks when
	building an IOC application. These are centered around the current
	Python IOC framework we're using (currently
	[pythonSoftIOC](https://github.com/dls-controls/pythonSoftIOC),
	in the slow process of moving to
	[CAproto](https://github.com/caproto/caproto)).
	
  - [The EMMI IOC Support (API)](#emmi-ioc-api) mostly goes hand in
    hand with with [the application API](#emmi-application). It
    implements a YAML API for defining IOC variable access of different
	types (simple input/output of values, or higher-level support like
	motors) for existing Python objects. In contrast to existing toolkits
	like PythonSoftIOC or CAproto, this explores the possibility of
	rapidly creating a (limtied) IOC given an already existing
	Python object / device interface, instead of building a Python device
	interface from scratch around the idea of evolving it into an IOC.

  - [The EMMI Device Architecture (EMA)](./eda.md) offers
    abstraction layers for access to commonly used types of hardware
	(currently mostly motors), signals and switches. It implements a number
	of boilerplate organisational mechanisms (like state automata / state
	machines for safe operation), and mock-up devices (e.g. mock positioners)
	intended as a basis for writing more elaborate unit tests for
	the final IOC.
  	
  - [Various infrastructure modules](#emmi-support-modules) are available
    for common tasks, e.g. MagicSCPI for easier pyVISA-based support
	to SCPI-like devices, CA-reader module for common CA-client tasks,
	etc.
  
  - [EMMIdaemon](#emmi-daemon) is (planned to be) a stand-alone application
    that runs and presents an ad-hoc IOC on one side, with a REST-like HTTPS
	API support on the other side. Although this was one of the 
	driving ideas behind EMMI, this currently still is "vaporware",
	i.e. non-existent.
