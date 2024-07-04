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

import time
import numpy as np
from scipy import signal
from labscript import (
    start,
    stop,
)
import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt, reshape_dt_3traps,reshape_dt_3traps_try2
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    # ## from sequence
    # t_total = 3.5e-6
    # amplitude = 0.8 # in V
    # offset = 0.0 # in V
    # carr_freq = 18.0*10**6 # 19.0*10**6
    # sweep_freq = 4.0*10**6/t_total #2.0*10**6/t_total
    # Total_points = 400#400
    # total_time = np.linspace(0,t_total,Total_points)
    # # wfm = amplitude*np.sin(2.0*np.pi*(carr_freq+sweep_freq/2.0*total_time)*total_time) + offset
    # wfm = amplitude*np.sin(2.0*np.pi*(carr_freq+sweep_freq*total_time)*total_time) + offset
    # wf_time = t_total
    # agilent_awg1.send_wf(total_time=wf_time,voltages=wfm)

    ## MW PULSE SHAPING:
    t_total = 10e-6
    amplitude = 0.8 # in V
    offset = 0.0 # in V
    carr_freq = 18.0*10**6 # 19.0*10**6
    sweep_freq = 4.0*10**6/t_total #2.0*10**6/t_total
    Total_points = 1000#485 #400#50000#int(400/3.5e-6*t_total)#400#400
    total_time = np.linspace(0,t_total,Total_points)
    # wfm = amplitude*np.sin(2.0*np.pi*(carr_freq+sweep_freq/2.0*total_time)*total_time) + offset
    wfm = amplitude*np.sin(2.0*np.pi*(carr_freq+sweep_freq/2*total_time)*total_time) + offset
    wf_time = t_total

    if PROGRAM_AWG2 == True:
        agilent_awg2.send_wf(total_time=wf_time,voltages=wfm)
    else: 
        agilent_awg2.send_memory()

    if PROGRAM_AWG3 == True:
        agilent_awg3.send_wf(total_time=wf_time,voltages=wfm)
    else: 
        agilent_awg3.send_memory()
    ##################################

    slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)

    t=0

    start()

    t+= load_mot(t, 0.1) # load_mot(t, 1)

    # agilent_awg2.trigger(t, duration=2e-6) # turn on MW field for preparation
    agilent_awg3.trigger(t , duration=2e-6) # turn on MW field for preparation

    t += reset_mot(t)
    t +=0.1
    stop(t)