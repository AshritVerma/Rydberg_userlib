#####################################################################
#                                                                   #
# /example.py                                                       #
#                                                                   #
# Copyright 2013, Monash University                                 #
#                                                                   #
# This file is part of the program labscript, in the labscript      #
# suite (see http://labscriptsuite.org), and is licensed under the  #
# Simplified BSD License. See the license.txt file in the root of   #
# the project for the full license.                                 #
#                                                                   #
#####################################################################


from labscript import (
    start,
    stop,
)
import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import *
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table
import matplotlib.pyplot as plt

import numpy as np
from scipy import signal

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    # amp = 1
    # t_total = 1e-3

    # n_pt = 100

    # carr_freq = 1.3e4
    # total_time = np.linspace(0,t_total,n_pt)
    # wfm = np.sin(2*np.pi*(carr_freq*total_time))

    # wfm = Max_ctrl*np.array([0.0] + [first_pulse_fraction]*int(Num_first_flat)+list(first_pulse_fraction*signal.gaussian(2*Num_first_gauss,0.25*Num_first_gauss)[Num_first_gauss:2*Num_first_gauss]) + [off_fraction]*int(Num_off) +  [second_pulse_fraction]*int(Num_second_flat)+10*[0.0]) 
    # wfm = wfm - np.min(wfm)
    # wf_time = (t_total)*10**-6 # in seconds
    Max_ctrl = 0.4 

    first_pulse_fraction = 0.25 
    second_pulse_fraction = 3.5 
    off_fraction= 0.0 

    Total_points = 470

    t_second_flat = 23.0+20
    t_first_flat = 2.7 
    t_first_gauss = 2.25 
    t_off = 2.0 
    t_total = t_second_flat+t_first_flat+t_off +t_first_gauss 

    Num_second_flat = int(Total_points*t_second_flat/t_total) 
    Num_first_gauss = int(Total_points*t_first_gauss/t_total) 
    Num_first_flat = int(Total_points*t_first_flat/t_total) 
    Num_off = int(Total_points*t_off/t_total) 

    carr_freq = 1.3e6
    total_time = np.linspace(0,t_total,Total_points)
    wfm = np.sin(2*np.pi*(carr_freq*total_time))

    wfm = Max_ctrl*np.array([0.0] + [first_pulse_fraction]*int(Num_first_flat)+list(first_pulse_fraction*signal.gaussian(2*Num_first_gauss,0.25*Num_first_gauss)[Num_first_gauss:2*Num_first_gauss]) + [off_fraction]*int(Num_off) +  [second_pulse_fraction]*int(Num_second_flat)+10*[0.0]) 
    wfm = wfm - np.min(wfm)
    wf_time = (t_total)*10**-6 # in seconds
    print(len(wfm))

    #wfm, wf_time = agilent_awg1.sample_control_wf()
    #agilent_awg3.send_wf(total_time=wf_time,load=50.0,voltages=wfm)
    agilent_awg3.send_wf(total_time=wf_time,voltages=wfm)


    #agilent_awg2.program_DC(1.3)

    # plt.plot(wfm)
    # plt.show()

    t=0
    
    start()
    utils.jump_from_previous_value(big_x_coil, t+1e-3, 0.0)

    agilent_awg3.trigger(t+1e-3, duration=1e-3)
    t += 1.0

    stop(t)