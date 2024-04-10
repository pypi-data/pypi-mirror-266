#!/usr/bin/python3

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
from xarray import DataArray

from caproto.sync import client as ca_client
#from caproto.sync import server as ca_server

from prometheus_client import start_http_server, Summary, Counter, Gauge

import argparse
import logging
import math
import xarray

from emmi.ca.reader import GuidedPvReader, PvRetry

class LiveDisplay:
    '''
    Uses Matplotlib to visualize numpy arrays (one or several?)
    '''
    def __init__(self, panels=None):
        '''
        Intialises a Matplotlib figure with the named panels.
        
        Parameters:
          - `panels`: A string array with panel reference names,
            or optionally a dictionary with reference and a displayable
            description.
        '''

        self.panelNames = panels or { "default": "Default display" }

        rows = int(round(math.sqrt(len(self.panelNames))))
        cols = int(math.ceil(len(self.panelNames)/rows))

        logging.info("Starting plotting interface")

        # We have a figure with NxM subplots (i.e. axes), each subplot hosting
        # one lineplot (for now), each referenced by name.
        self.figure = plt.figure()
        self.axes = { k: self.figure.add_subplot(rows, cols, i+1) for i,k in enumerate(self.panelNames) }
        self.lines = { k: x.plot([])[0] for k, x in zip(self.panelNames, self.figure.axes) }

        # caching some data array metrics for autoscaling
        self.last_update = {k:time.time() for k in self.panelNames }
        
        self.figure.show(True)
        

    def update(self, panel, data=None, xaxis=None, xlabel=None, ylabel=None, text=None):
        '''
        Updates data on the panel named `panel` using the data from `data`.
        `data` should preferrably be an `xarray.DataArray` container, in
        which case all metadata will be used extracted from there.
        Otherwise axis scalind and labeling will be used from the named
        arguments.

        The panels will upscale the X and Y ranges to fit all the data
        dynamics, but will never scale down.
        '''

        try:
            ax = self.axes[panel]
        except KeyError:
            logging.error("%s: no such display panel" % panel)
            return

        if xlabel:
            ax.set_xlabel(xlabel)
            
        if ylabel:
            ax.set_ylabel(ylabel)

        if data is None:
            return
        
        #if len(data) != self.xlen[panel]:
        #    self.xlen[panel] = len(data)
        #xlen = len(data)

        if xaxis is None:
            xaxis = data.coords[data.dims[0]].values if isinstance(data, xarray.DataArray) \
                else np.array([i for i in range(len(data))])

        xlim = np.array([xaxis[0], xaxis[-1]])
        if (xlim != ax.get_xlim()).all():
            logging.info("Adjusting X axis to %r" % xlim)
            ax.set_xlim(*xlim)

        ylim = ax.get_ylim()
        dlim = np.array([data.min(), data.max()])
        #print(data)
        if (dlim[0] < ylim[0]) or (dlim[1] > ylim[1]):
            logging.info("Adjusting Y range to %r" % dlim)
            ax.set_ylim(min(dlim[0], ylim[0]), max(dlim[1], ylim[1]))

        self.lines[panel].set_data(xaxis, data)
        self.figure.canvas.draw_idle()

        # just for benchmarking.
        tnow = time.time()
        tdiff = tnow - self.last_update[panel]
        self.last_update[panel] = time.time()

        #text.set_text("acquisition: %2.2f Hz | flags: %r | counts: %d" % \
        #              (1.0/(tnow-t0),
        #               [], # f for f in hdev.flags
        #               data.sum()))

        
    def handle_events(self):
        self.figure.canvas.flush_events()
        
        

def old_histo_loop(fig, aqtime=0.1, axis_index=0, line_index=0, channel=0):
    '''
    Loops endlessly reading histogram and displaying it into the
    specified Matplotlib plot, while also serving the GUI event loop.
    '''
    
    print("Starting plotting interface")
    ax = fig.axes[axis_index] if len(fig.axes)>0 else fig.add_subplot(1, 1, 1)
    line = ax.lines[line_index] if len(ax.lines)>0 else ax.plot([])[0]
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Intensity (counts)')
    text  = ax.text(0, 0.0, "Jinkies")
    fig.show(False)

    devPrefix = "KMC3:XPP:HARP:"
    chPrefix = devPrefix+"CH%d_" % channel

    #ca.write(devPrefix+"ACQUISITIONTIME", 0.5)
    
    # For auto-scaling
    xlen = 0
    ymax = 0
    t0 = time.time()

    while True:

        # wait for acquisition to end
        while True:
            try:
                v = ca_client.read(devPrefix+"ACQUIRINGRBV")
                #print("Waiting for acquisition to end... (%r)" % v.data)
                if v.data[0].decode('utf-8') == "OFF":
                    break
            except Exception as e:
                print("Error:", e)
            fig.canvas.flush_events()
            time.sleep(0.1)

        try:
            data = np.array(ca_client.read(chPrefix+"HISTOGRAM_SIGNAL").data)
            offs = ca_client.read(chPrefix+"HISTOGRAM_OFFSET").data[0]
            delta = ca_client.read(chPrefix+"HISTOGRAM_DELTA").data[0]
            reach = offs+delta*len(data)
            xaxis = np.array([offs+delta*i for i in range(len(data))])
            #xdata = DataArray(data=data, dims=["delay"], coords=[xaxis])
        except Exception as e:
            print("Error:", e)

        print ("Acquisition finished:", data.shape, data, offs, delta, data[[i!=0 for i in data]])

            
        if len(data) != xlen:
            xlen = len(data)
            ax.set_xlim(offs, reach)

        ## Some random noise, for testing
        #data[np.random.randint(xlen)] = np.random.randint(100)
        
        dmax = data.max()
        if ymax < dmax:
            print ("Adjusting Y range")
            ymax = dmax
            ax.set_ylim(-1, dmax+1)

        tnow = time.time()
        text.set_text("acquisition: %2.2f Hz | flags: %r | counts: %d" % \
                      (1.0/(tnow-t0),
                       [], # f for f in hdev.flags
                       data.sum()))
        t0 = tnow

        print ("Updating plot (heartbeat: %r, max %d @ %d)" % \
               (ca_client.read(devPrefix+"heartbeat").data[0], dmax, -1))
        line.set_data(xaxis, data)
        fig.canvas.draw_idle()
        fig.canvas.flush_events()

        # This turns on the acquisition
        #ca.write(devPrefix+"ACQUIRINGVAL", "ON")
        
        while True:
            try:
                v = ca_client.read(devPrefix+"ACQUIRINGRBV").data
                #print("Waiting for acquisiton to start... (%r)" % v)
                if v.data[0].decode('utf-8') == "ON":
                    break
            except Exception as e:
                print("Error:", e)
            fig.canvas.flush_events()
            time.sleep(0.1)

        print ("Acquiring...")
    

class FifoArrayWrapper:
    '''
    Quick 'n Dirty wrapper 
    '''
    def __init__(self, length, *args, **kw):
        self.data = np.zeros(length)

    def push_value(self, val):
        current = (self.data[1:]).copy()
        self.data[:-1] = current[:]
        self.data[-1] = val


def save_me(dataMap):
    pass

def save_array(path, data):
    print ("Saving:", path)
    with open(path, "w") as f:
        f.write(" ".join([str(i) for i in data]))


def histo_loop(display, reader=None):
    '''
    This is where the magic happens.
    '''
    
    countRate    = FifoArrayWrapper(512)
    #roi1         = FifoArrayWrapper(512)
    #roi2         = FifoArrayWrapper(512)
    #roi3         = FifoArrayWrapper(512)
    #roi4         = FifoArrayWrapper(512)
    #ratio_roi12  = FifoArrayWrapper(512) 

    # about xarray:
    
    hstack = None
    
    while True:
        try:
            dataMap = reader.retr()

            #save_me(dataMap)

            print("Have:", dataMap)

            countRate.push_value(dataMap['CH0_COUNTRATE'])
            
            display.update('histo', dataMap['CH0_HISTOGRAM_SIGNAL'], xlabel='Time (s)', ylabel='Counts')

            # Saving data
            #filebase = '/tmp/histo'
            #tstamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())+("%.2f"%(time.time()%1))[1:]  
            #save_array(filebase+"-"+tstamp, dataMap['CH0_HISTOGRAM_SIGNAL'].values)
            
            #if hstack is None:
            #	hstack = dataMap['CH0_HISTOGRAM_SIGNAL'].copy()
            #else:
            #	hstack += dataMap['CH0_HISTOGRAM_SIGNAL']
            #    
            #display.update('hstack', hstack, xlabel='Time (s)', ylabel='Counts')
            
            # Check out documentation for 'xarray' on indexing these containers
            #roi1_data = hstack.sel(x=slice(1e-11, 5e-8))
            #roi2_data = hstack.sel(x=slice(1e-7, 1e-6))
            #roi3_data = hstack.sel(x=slice(1e-6, 1e-5))
            #roi4_data = hstack.sel(x=slice(1e-8, 1e-7))
            #sum_data = hstack.sel(x=slice(0, 2e-6))
            #print(sum_data.sum())
            #print(np.any(np.isnan(dataMap['CH0_HISTOGRAM_SIGNAL'].values)))
            
            #roi1.push_value(roi1_data.sum())
            #roi2.push_value(roi2_data.sum())
            #roi3.push_value(roi3_data.sum())
            #roi4.push_value(roi4_data.sum())
            #if roi2_data.sum() == 0:
            #    ratio_roi12.push_value(0)
            #else:
            #    ratio_roi12.push_value((roi2_data.sum()-roi1_data.sum())/roi2_data.sum())
            
            #ca_client.write("KMC3:XPP:HARP:ACQUIRINGVAL", "ON")
            
            display.update('rate', countRate.data, ylabel='Count rate')
            #display.update('roi1', roi1.data, ylabel='ROI 1 (sum counts)')
            #display.update('roi2', roi2.data, ylabel='ROI 2 (sum counts)')
            #display.update('roi3', roi3.data, ylabel='ROI 3 (sum counts)')
            #display.update('roi4', roi4.data, ylabel='ROI 4 (sum counts)')
            #display.update('ratio_roi12', ratio_roi12.data, ylabel='ratio (ROI2-ROI1)/ROI2')
            
        except PvRetry:
            time.sleep(0.05)
            
        except Exception as e:
            print(e)
            time.sleep(3)
            
        except:
            logging.error("You broke it.")
            time.sleep(10)
            
        display.handle_events()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="capeek", description="EPICS Channel Access data peek utility")
    parser.add_argument('-l', '--loglevel', action='store', default='INFO')
    parser.add_argument('--legacy', action='store_true', default=False)
    parser.add_argument('-p', '--mport', action='store', default=31415,
                        help='Port where to export summaries of data for Prometheus monitoring')
    parser.add_argument('-P', '--ioc-prefix', action='store', default='',
                        help='Prefix to use for all IOC variables')
    parser.add_argument('-H', '--ioc-heartbeat', action='store', default='heartbeat',
                        help='Heartbeat variable suffix')

    opts = parser.parse_args()

    level = getattr(logging, (opts.loglevel or 'INFO').upper(), None)
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=level)
    
    heartbeat = Counter((opts.ioc_prefix+opts.ioc_heartbeat).lower().replace(':', '_'),
                        'IOC master heartbeat for %s' % opts.ioc_prefix)

    start_http_server(opts.mport)

    if opts.legacy:
        logging.info("Starting legacy display")
        old_histo_loop(plt.figure())
        
    else:
        logging.info("New and improved, but broken, display")

        reader = GuidedPvReader(prefix="KMC3:XPP:HARP:",
                                guides={ "ACQUIRINGRBV": "OFF" },
                                pv=["CH0_HISTOGRAM_SIGNAL",
                                    "CH0_COUNTRATE"])
        
        displ = LiveDisplay(panels=['histo', 'rate'])
        
        histo_loop(displ, reader)
