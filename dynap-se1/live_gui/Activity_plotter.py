#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 17 17:53:45 2021

@author: dzenn
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from threading import Thread

from time import sleep, time
from numba import njit

import numpy as np

import tkinter as tk

class ActivityPlot():
    
    def __init__(self, sink_node=None, refresh_rate=500, y_range=None):
        
        self.sink_node = sink_node
        self.refresh_rate = refresh_rate
        self.raster_y_range = y_range
        
        self.main = tk.Tk()
        self.main.geometry("520x520+100+50")
        self.main.title("Activity gui")
        
        self.activity_dt = 0.01
        
        evts = self.sink_node.get_events()
        evts_n = np.array([[evt.timestamp, evt.neuron_id] for evt in evts])
        
        self.raster_x = evts_n[:,0]*1e-06
        self.raster_y = evts_n[:,1]
        
        self.start_timestamp = self.raster_x[0]
        self.start_time = time()
        # self.timestamp_delta = 
        
        
        self.raster_fig, axes = plt.subplots(2,1, figsize=(8,8), dpi = 100)
        self.raster_ax = axes[0]
        self.activity_ax = axes[1]
        
                
        self.raster_plot, = self.raster_ax.plot(self.raster_x, self.raster_y, '|')
        self.raster_ax.set_xlabel("time (s)")
        self.raster_ax.set_ylabel("neuron_id")
        
             
        self.activity_x, self.activity_y = get_activity(0, self.raster_x, self.start_timestamp,
                                                        self.raster_x[-1], self.activity_dt)
        
        
        self.activity_plot, = self.activity_ax.plot(self.activity_x, self.activity_y)
        self.activity_ax.set_xlabel("time (s)")
        self.activity_ax.set_ylabel("core activity")
        self.raster_fig.tight_layout()
        
        self.raster_tk = FigureCanvasTkAgg(self.raster_fig, self.main)
        self.raster_tk.get_tk_widget().pack()
            
            
        
        self.main.after(self.refresh_rate, self.update_plot)
        self.main.mainloop()
        
        
    def update_plot(self):
        
        evts = self.sink_node.get_events()
        
        if len(evts) != 0:
            evts_n = np.array([[evt.timestamp, evt.neuron_id] for evt in evts])
            
            # plt.plot(evts_n[:,0], evts_n[:,1], '.')
            activity_x, activity_y = get_activity(self.activity_y[-1], evts_n[:,0]*1e-06, self.raster_x[-1],
                                                  evts_n[-1,0]*1e-06, self.activity_dt)
            
            self.activity_x = np.concatenate((self.activity_x, activity_x))
            self.activity_y = np.concatenate((self.activity_y, activity_y))
            
            select_mask = (self.activity_x[-1] - self.activity_x) < 5
            
            self.activity_x = self.activity_x[select_mask]
            self.activity_y = self.activity_y[select_mask]
            
            self.activity_plot.set_xdata(self.activity_x)
            self.activity_plot.set_ydata(self.activity_y)
            self.activity_ax.set_xlim((self.activity_x.min(), self.activity_x.max()))
            self.activity_ax.set_ylim((0, self.activity_y.max()+10))
            
            
            
            self.raster_x = np.concatenate((self.raster_x, evts_n[:,0]*1e-06))
            self.raster_y = np.concatenate((self.raster_y, evts_n[:,1]))
            
            select_mask = (self.raster_x[-1] - self.raster_x) < 5
            
            self.raster_x = self.raster_x[select_mask]
            self.raster_y = self.raster_y[select_mask]
            # self.x.append(self.x[-1] + 1)
            # self.y.append(random.random()*50)
            
            self.raster_plot.set_xdata(self.raster_x)
            self.raster_plot.set_ydata(self.raster_y)
            self.raster_ax.set_xlim((self.raster_x.min(), self.raster_x.max()))
            if self.raster_y_range is None:
                self.raster_ax.set_ylim((self.raster_y.min(), self.raster_y.max()))
            else:
                self.raster_ax.set_ylim(self.raster_y_range)
            self.raster_tk.draw()
            self.raster_tk.flush_events()
            
        else:
            print("No events to plot!")
            
            
        self.main.after(self.refresh_rate, self.update_plot)

@njit        
def get_activity(last_activity_value, spiketimes, t_start, t_end, dt):
    
    x = []
    y = []
    
    t_current = t_start
    activity_current = last_activity_value
    activity_prev = last_activity_value
    spike_id=0
    spike_id_last=len(spiketimes)
    
    for t_current in np.arange(t_start+dt, t_end, dt):
        activity_current = relaxate(activity_prev, 1, dt)
        while(spike_id<spike_id_last and spiketimes[spike_id] < t_current):
            activity_current += 1
            spike_id += 1
        x.append(t_current)
        y.append(activity_current)
        activity_prev = activity_current
        
    return x, y

@njit         
def relaxate(A, tau, delta_t):
    return A*np.exp(-delta_t/tau)

# def plot_activity():
        
#     x = [1,2,3,4,5,6,7,8,9,10]
#     y = [30,32,34,32,33,31,29,32,35,45]
    
#     fig = plt.figure()        
#     p1, = plt.plot(x, y)
    
#     for i in range(20):
#         x = x[1:]
#         y = y[1:]
    
#         x.append(x[-1] + 1)
#         y.append(random.random()*50)
        
#         p1.set_xdata(x)
#         p1.set_ydata(y)
#         fig.canvas.draw()
#         fig.canvas.flush_events()
#         plt.xlim((x[0], x[-1]))
#         plt.ylim((min(y), max(y)))
        
#         sleep(0.5)
        
#         print(x)
        
def run_gui(sink_node, refresh_rate, y_range):
    
    gui = ActivityPlot(sink_node, refresh_rate, y_range)
    
def run_plotting_thread(sink_node, refresh_rate, y_range=None):
    
    import threading
    
    gui_thread = threading.Thread(target=run_gui, args=(sink_node, refresh_rate,y_range, ))
    gui_thread.start()  
    
    
      

# if __name__ == '__main__':
    
    
#     # plot_activity()
#     # t1 = Thread(target = plot_activity)
#     # t1.start()
    
#     # run_plotting_thread()