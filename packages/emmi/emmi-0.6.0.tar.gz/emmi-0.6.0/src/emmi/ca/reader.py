#!/usr/bin/python3

import asyncio, time, logging

from caproto.sync import client as ca_client
from caproto.asyncio.client import Context
from caproto import CaprotoTimeoutError
import numpy as np

from xarray import DataArray

class PvRetry(RuntimeError):
    '''
    Raised by GuidedPvReader when the PVs are not yet ready / guide does
    not yet signal readiness for signal readout.
    '''
    def __init__(self, *p, **kw):
        super().__init__(*p, **kw)


#def pv2xa(pvname, unpackScalar=False):
#    '''
#    '''
#    ca_client.read(self.prefix+k)    
#    pass


class GuidedPvReader:
    '''
    Observes a "guide" variable to determine when a specific EPICS PV signal is
    available, then collects the PV signal (which can come in a list of other PVs).
    '''

    def __init__(self, pv=None, guides=None, prefix='', auto_xarray=True):
        '''Initialises the reader.

        Args:
        
            pv: A single PV, or a list of PVs, to read out. If not
              specified here, it can be specified later.
        
            guides: A dicitonary of guide variable(s) and their respective
              value to use. The `pv` values will be acquired on the first occasion
              when *all* of the guides' values have changed *to* the value specified    ctx = Context()


              in the dictionary. If the dictionary value is a callable, it will be
              called with the current (i.e. new) guide values as its sole
              parameters and the `pv` value will be obtained the first time the
              return value changes to `True`.

            prefix: If specified, it will be prepended to all of the
              PVs' and guides' EPICS names.
        '''
        
        self.prefix = prefix or ''
            

        # PVs get a special treatment (e.g. extending _SIGNAL to also acquire the
        # corresponding _OFFSET and _DELTA PVs, if available)
        self.pv = [pv,] if isinstance(pv, str) else [i for i in (pv or []) ]
        if auto_xarray:
            for p in self.pv:
                if p.endswith("_SIGNAL"):
                    self.pv.append(p.replace("_SIGNAL", "_OFFSET"))
                    self.pv.append(p.replace("_SIGNAL", "_DELTA"))
        self.pv = tuple(self.pv)
    
        
        self.guides = {} if guides is None \
            else { prefix+k: v if hasattr(v, "__call__") else lambda x: x == v \
                   for k,v in guides.items() }

        # map EPICS name -> current True/False  evaluation of the guide signal.
        # Note that this is _not_ the guide trigger evaluation, i.e. the condition
        # of whether the waiting for this guide is finished and we're ready to
        # return data! For the latter to be fulfilled, the corresponding
        # guide_eval needs to be changing from 'False' to 'True'!
        self.guide_evals = { k:None for k in self.guides }

        
    def extract_data(self, response, pvName=None, others=None):
        '''
        Extracts "useful" data out of a response telegram.
        '''

        if response is None:
            return None

        if others is None:
            others = {}

        # Channel types can be: CHAR, DOUBLE, FLOAT, STRING, ENUM, LONG, INT.
        # The intention is to get an automatic useful native Python data type,
        # scalar or array. This means different things for different data
        # types.
        # In addition, we implement some heuristics to decorate waveforms
        # (== arrays) if our obscure array markers are present (shape, dimensions,
        # axis scaling -- to be documented ;-) )
        
        if response.data_type in (ca_client.ChannelType.STRING,):
            return response.data[0].decode('utf-8')
        
        elif response.data_type in (ca_client.ChannelType.DOUBLE,
                                    ca_client.ChannelType.FLOAT,
                                    ca_client.ChannelType.LONG,
                                    ca_client.ChannelType.INT,
                                    ca_client.ChannelType.ENUM):
            
            if len(response.data) == 1:
                return response.data[0]

            if not pvName or not pvName.endswith("_SIGNAL"):
                return response.data
            
            # If we have an array and it ends on _SIGNAL, we also try to
            # load _OFFSET and _DELTA for intrinsic scaling information
            o_name = pvName.replace("_SIGNAL", "_OFFSET")
            d_name = pvName.replace("_SIGNAL", "_DELTA")

            if o_name in others:
                offs = self.extract_data(others.get(o_name, 0))
                del others[o_name]
                #print("Removed:", o_name)
            else:
                offs = 0

            if d_name in others:
                dlta = self.extract_data(others.get(d_name, 1))
                del others[d_name]
                #print("Removed:", d_name)
            else:
                dlta = 1
                
            axis = offs+np.array(range(len(response.data)))*dlta
                
            return DataArray(data=response.data, dims=["x"], coords=[axis])

        # else: how to handle ENUM / CHAR?
            
        else:
            logging.warning ("Unhandled data type: %r" % (response.data_type,))
            return response.data[0]

    
    def retr(self, pv=None, raiseRetry=True):
        ''' Synchronously checks the guides for readiness and retrieves the PV values.
        
        If `pv` is not `None`, they will be retrieved in addition to the ones
        already specified at the initialisation of the class. If `prefix` is
        specified (not `None`), it will override whatever was specified at the
        initialisation of the class, but only for the PVs specified here.
        '''

        good_guides = 0

        for (k,v) in self.guides.items():
            data = self.extract_data(ca_client.read(k))
            if v(data) and (not self.guide_evals[k]):
                good_guides += 1
            self.guide_evals[k] = v(data)

        if good_guides == len(self.guides):
            pv = [k for k in (pv or {}) ]
            pv.extend([k for k in self.pv])
            return { k: self.extract_data(ca_client.read(self.prefix+k), pvName=self.prefix+k) \
                     for k in pv }

        raise PvRetry()


    async def value(self, timeout=-1, pollPeriod=0.001):
        '''
        Asynchronousluy waits for retr() to deliver a valid dataset.
        Cancels after `timeout` seconds (if timeout >= 0).

        Note that this is _very_ inefficient,, as it essentially
        wraps a (slow) synchronous client in an async loop.
        '''
        tstart = time.time()
        while True:
            try:
                return self.retr()
            except PvRetry:
                if (timeout > 0) and (time.time()-tstart >= timeout):
                    raise
            await asyncio.sleep(pollPeriod)


class GuidedAsyncReader(GuidedPvReader):
    ''' Similar to GuidedPvreader but uses the asyncio caproto client.

    To get as efficient as possible, this implementation actually
    uses subscriptions to the guide variables, and reacts on
    those. Calling .value() will wait asynchronously for the guide
    conditions to be fulflled, and this will be fairly efficient.

    But the most efficient way will be to subscribe a data
    processing callback using .subscribe(), which will be called
    only when all guide conditions are fulfilled and all data
    is available.
    '''
    
    def __init__(self, ctx, *args, subscribe=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctx = ctx

        self.data_pvs = None        
        self.guide_pvs = None
        self.subscribe = subscribe
        self.incoming_hooks = []


    def subscribe_incoming(self, proc):
        ''' Registers a hook for processing incoming data.
        The hook will receive a dictionary with full PV
        name(s) as keys, and data as values.
        '''
        self.incoming_hooks.append(proc)

        
    async def connect(self, ctx=None):
        
        if ctx is not None:
            self.ctx = ctx
            
        if self.ctx is None:
            logging.info("Initializing CA client context...")
            self.ctx = Context()
        else:
            logging.info(f"Using context: {self.ctx}")
        
        guides = [k for k in self.guides.keys()]
        pvnames = [self.prefix+k for k in self.pv ]

        # map EPICS name -> Context PV, for all guide variables
        self.guide_pvs = await self.ctx.get_pvs(*guides)

        # map EPICS name -> Context PV, for all non-guide variables
        self.data_pvs = await self.ctx.get_pvs(*pvnames)
            
        #  map EPICS name -> Subscription obj, for all guides
        self.guide_subscriptions = {}
        self.data_subscriptions = {}

        if self.subscribe:
            for g in self.guide_pvs:
                logging.info(f'Subscribing to guide: {g.name}')
                self.guide_subscriptions[g.name] = g.subscribe()
                self.guide_subscriptions[g.name].add_callback(self._guide_changed)

            for d in self.data_pvs:
                logging.info(f'Subscribing to data: {d.name}')
                self.data_subscriptions[d.name] = d.subscribe()
                self.data_subscriptions[d.name].add_callback(self._data_changed)
        

        # map EPICS name -> trigger-condition-fulfilled, for all guides.
        # When all of these are True, that's when we need to read
        # all the non-guide data.
        # Each of these becomes True when the guide changes value _to_
        # whatever was specified. It switches to False again when a data
        # readout is performed, or when it swithces value away _from_
        # whatever was specified.
        #
        # Note that this is subtly different from self.guide_evals!
        # While guide_evals is a True/False value per guide, representing
        # the current condition evaluation, the guide_trigger truth value
        # also indicates the *changing* to the True value.
        #
        # Also important to note: keeping this accurate for _all_ guides
        # at once is difficult when more than one guide is involved (values
        # will change with a slight delay). Hence the policy: once a guide
        # is considered triggered, it _stays_ triggered for as long as
        # its value doesn't chance, or data isn't read.
        self.guide_trigger = {k:False for k in self.guides.keys()}

        self._incoming_data = {k:None for k in self.pv}


    async def wait_for_guides(self, PVs, timeout=-1):
        ''' Waits for the internal list of PVs '''
        guides = await asyncio.gather(*[v.read() for v in PVs ])
        for (k,v),data in zip(self.guides.items(),guides):
            self._guide_changed(None,data,pv_name=k)
            if all(self.guide_trigger.values()):
                return len(self.guide_trigger)
        return 0


    def _guide_changed(self, sub, response, pv_name=None):
        ''' Called when a guide value changes. '''

        if pv_name is None:
            pv_name = sub.pv.name

        d = self.extract_data(response)
        eval_result = self.guides[pv_name](d)
        
        #print(f'got {pv_name}: {d}, '
        #      f'eval: {eval_result} <- {self.guide_evals[pv_name]}, '
        #      f'trigger: {self.guide_trigger[pv_name]}')

        if eval_result:
            if not self.guide_evals[pv_name]:
                # on eval switch False -> True: trigger!
                self.guide_trigger[pv_name] = True
        else:
            # eval False always kills the trigger
            self.guide_trigger[pv_name] = False
            
        self.guide_evals[pv_name] = eval_result

        # check whether we can do a data readout (all triggers must be True)
        if not all(self.guide_trigger.values()):
            return

        # If we don't have any hooks, we ignore this part; the data
        # is likely to be retrieved by other means (e.g. by polling
        # in .value()).
        if len(self.incoming_hooks):
            data = self._get_incoming()
            for proc in self.incoming_hooks:
                proc(data)


    def _data_changed(self, sub, response):
        ''' Called when new non-guide data arrives. '''
        self._incoming_data[sub.pv.name] = response

    
    def _get_incoming(self):
        ''' Returns the currently incoming data (from subscriptions)
        and clears everything for the next run.
        '''
        
        for k in self.guide_trigger:
            self.guide_trigger[k] = False
            
        data = { k:self.extract_data(v, k, others=self._incoming_data) \
                 for k,v in self._incoming_data.items() if v is not None}

        # FIXME: should we clear incoming data, too?...
        
        return data

    
    async def wait_for_incoming(self):
        ''' Waits for incoming data -- this is similar to .value(),
        only this uses the subscription mechanism.
        '''
        await self.wait_for_guides(self.guide_pvs)
        return self._get_incoming()
        

    async def read_data(self):
        ''' Unconditionally reads all (non-guide) data and returns a dictionary.

        Should only be used in a subscription-less mode, after .wait_for_guides().
        '''

        if self.subscribe:
            RuntimeError(f'This is a subscription-based reader; '
                         f'you shouldn\'t use .read_data() here.'
                         f'Use .wait_for_incoming() or '
                         f'.subscribe_incoming() instead.')

        async def read_wrapper(pv):
            try:
                return (pv.name, await pv.read())
            except CaprotoTimeoutError as e:
                logging.info(f'Timeout: {e}')
            
        dataMap = dict(await asyncio.gather(*[read_wrapper(v) for v in self.data_pvs ]))
        
        if not all(self.guide_trigger.values()):
            logging.warning(f'Some triggers were already inactive by the end of readout')
            
        for k in self.guide_trigger:
            self.guide_trigger[k] = False

        return { k:self.extract_data(v, k, others=dataMap) for k,v in dataMap.items() }

    
    async def value(self, timeout=-1, pollPeriod=0.001, autoconnect=True):
        
        if (self.guide_pvs is None) and \
           (self.data_pvs is None) and \
           autoconnect:
            await self.connect()

        if self.subscribe:
            raise RuntimeError(f'This is a subscription-based reader; '
                               f'you shouldn\'t use .value() here.'
                               f'Use .wait_for_incoming() or '
                               f'.subscribe_incoming() instead.')

        tstart = time.time()

        while True:

            # FIXME: should change this to subscriptions!
            if (await self.wait_for_guides(self.guide_pvs)):
                return await self.read_data()

            if (timeout > 0) and (time.time()-tstart >= timeout):
                raise PvRetry()

            await asyncio.sleep(pollPeriod)

            
    def retr(self):
        raise NotImplemented("retr() not available in async mode")


class AsyncMonitorMany:
    ''' Monitors a number of EPICS variables and calls a callback when any one changes.
    '''

    def __init__(self, ctx=None, pvs=None, prefix='', subscribe=True):
        '''Initialises the monitor.

        Args:
        
            pvs: A list of PVs (strings)
      
            prefix: If specified, it will be prepended to all of the
              PVs' and guides' EPICS names.

            subscribe: Monitor using EPICS subscription if True.
        '''
        
        self.prefix = prefix or ''
        self.ctx = ctx
        self.subscribe = subscribe

        # PVs get a special treatment (e.g. extending _SIGNAL to also acquire the
        # corresponding _OFFSET and _DELTA PVs, if available)
        self.pv_names = [pvs,] if isinstance(pvs, str) else [i for i in (pvs or []) ]
        self.pv_names = tuple(self.pv_names)
        
        self.data_pvs = None
        self.incoming_hooks = []
        

    def subscribe_incoming(self, proc):
        ''' Registers a hook for processing incoming data.
        The hook will receive a dictionary with full PV
        name(s) as keys, and data as values.
        '''
        self.incoming_hooks.append(proc)


    async def connect(self, ctx=None):
        
        if ctx is not None:
            self.ctx = ctx
            
        if self.ctx is None:
            logging.info("Initializing CA client context...")
            self.ctx = Context()
        else:
            logging.info(f"Using context: {self.ctx}")

        pvnames = [self.prefix+k for k in self.pv_names ]
        self.data_pvs = await self.ctx.get_pvs(*pvnames)

        self.data_subscriptions = {}

        if self.subscribe:
            for d in self.data_pvs:
                logging.info(f'Subscribing to data: {d.name}')
                self.data_subscriptions[d.name] = d.subscribe()
                self.data_subscriptions[d.name].add_callback(self._data_changed)

        self._incoming_data = {k:None for k in self.pv_names}
        

    def _data_changed(self, sub=None, response=None, name=None):
        ''' Called when new data arrives. '''

        pv_name = sub.pv.name if sub is not None else name   
        #logger.debug(f'New data for {pv_name}: {response}')
        
        self._incoming_data[pv_name] = response
        if len(self.incoming_hooks):
            data = self._get_incoming()
            for proc in self.incoming_hooks:
                proc(data)

    
    def _get_incoming(self):
        ''' Returns the currently incoming data (from subscriptions)
        and clears everything for the next run.
        '''
        
        data = { k:v for k,v in self._incoming_data.items() if v is not None }
        return data


    async def wait_for_incoming(self, PVs):
        ''' Waits for incoming data. '''
        try:
            responses = await asyncio.gather(*[v.read() for v in PVs ])
            for pv,res in zip(PVs,responses):
                self._data_changed(sub=None, response=res, name=pv.name)
            
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            self.do_run = False


    async def monitor_loop(self, period=0.01):
        self.do_run = True
        try:
            while self.do_run:
                await self.wait_for_incoming(self.data_pvs)
                await asyncio.sleep(period)
                
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            #self.do_run = False

        logging.error("Oops. Blew it.")
