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
    add_time_marker
)
import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import load_mot, compress_mot, reset_mot, image_cmot, zero_B_fields, hold_dt, probe_with_spcm, reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    # # Set the params that do not change over course of expt
    # utils.set_static_parameters()
    pts_probe.program_single_freq(PROBE_FREQ)
    smc_sg1.set_freq_amp(CONTROL_FREQ,19)


    ## PROBE PULSE SHAPING:
    probe_duration = 60e-6 #150e-6

    Max_photonRate = 0.025   # percentage relative to photon rate at 2V
    first_pulse_fraction = 0.0
    second_pulse_fraction = 5.0
    off_fraction = 0.0

            
    Total_points = 1000
    t_second_flat = probe_duration*10**6
    t_first_flat = 0.0
    t_off = 0.0 
    t_first_gauss = 0.0
    t_second_gauss = 1.0
    t_total = t_second_flat+t_first_flat+t_first_gauss + t_off + t_second_gauss 
    Num_first_gauss = int(Total_points*t_first_gauss/t_total)
    Num_second_gauss = int(Total_points*t_second_gauss/t_total)
    Num_second_flat = int(Total_points*t_second_flat/t_total)
    Num_first_flat = int(Total_points*t_first_flat/t_total)
    Num_off = int(Total_points*t_off/t_total)

            
    wfm = Max_photonRate*np.array([0.0] +list(first_pulse_fraction*signal.gaussian(2*Num_first_gauss,0.25*Num_first_gauss)[0:Num_first_gauss]) + [first_pulse_fraction]*int(Num_first_flat)+ [off_fraction]*int(Num_off)+list(second_pulse_fraction*signal.gaussian(2*Num_second_gauss,0.25*Num_second_gauss)[0:Num_second_gauss])+[second_pulse_fraction]*int(Num_second_flat))
    wfm = wfm - np.min(wfm)
    wf_time = t_total*10**-6
    agilent_awg1.send_wf(total_time=wf_time,voltages=wfm)

    ## CONTROL PULSE SHAPING:
    Max_ctrl = 0.4
    first_pulse_fraction = 0.0 #0.14
    second_pulse_fraction = 3.5
    off_fraction= 0.0
            
    Total_points = 390
    t_second_flat = probe_duration*10**6
    t_first_flat = 0.0
    t_first_gauss = 0.0
    t_second_gauss = 1.0
    t_off = 0.0
    t_total = t_second_flat+t_first_flat+t_off +t_first_gauss+t_second_gauss
    Num_second_flat = int(Total_points*t_second_flat/t_total)
    Num_first_gauss = int(Total_points*t_first_gauss/t_total)
    Num_second_gauss = int(Total_points*t_second_gauss/t_total)
    Num_first_flat = int(Total_points*t_first_flat/t_total)
    Num_off = int(Total_points*t_off/t_total)
            
    #wfm = Max_ctrl*np.array([0.0] + [first_pulse_fraction]*int(Num_first_flat)+list(first_pulse_fraction*signal.gaussian(2*Num_first_gauss,0.25*Num_first_gauss)[Num_first_gauss:2*Num_first_gauss]) + [off_fraction]*int(Num_off) + list(second_pulse_fraction*signal.gaussian(2*Num_second_gauss,0.25*Num_second_gauss)[0:Num_second_gauss]) + [second_pulse_fraction]*int(Num_second_flat)+10*[0.0])
    wfm = Max_ctrl*np.array([0.0] + [first_pulse_fraction]*int(Num_first_flat) + [off_fraction]*int(Num_off) + list(second_pulse_fraction*signal.gaussian(2*Num_second_gauss,0.25*Num_second_gauss)[0:Num_second_gauss]) + [second_pulse_fraction]*int(Num_second_flat)+10*[0.0])
    wfm = wfm - np.min(wfm)
    wf_time = t_total*10**-6
    agilent_awg3.send_wf(total_time=wf_time,voltages=wfm)

################### SEQUENCE STARTS HERE ###################
    t=0.0

    start()
    
    t+= load_mot(t, 1)

    t += compress_mot(t, 50e-3)

    zero_B_fields(t, duration=5e-3)
    #t += hold_dt(t, duration = DT_WAIT_DURATION)
    t += reshape_dt(t, duration = DT_WAIT_DURATION)

    add_time_marker(t, "RAMP_UP_B_FIELD")
    utils.jump_from_previous_value(big_z_coil, t, 5)
    t+= 10e-3

    # turn on repump right before imaging. In real sequence we should have OP in this place.
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+= 300e-6
    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    
    # Add optical pumping:
    t+=10e-6
    utils.jump_from_previous_value(op_aom_power, t, 1)
    op_aom_switch.enable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+=400e-6
    utils.jump_from_previous_value(op_aom_power, t, 0)
    op_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)
    t+=100e-6 # add this time to allow for AOM to turn off



    # turn off DT and turn on control light 2us before probing
    agilent_awg3.trigger(t, duration=1e-3) # control shaping
    control_aom_switch.enable(t)
    #dt852_aom_switch.disable(t)
    #dt785_aom_switch.disable(t)
    t+=2e-6

    agilent_awg1.trigger(t, duration=1e-3) # probe shaping
    #utils.jump_from_previous_value(sacher_aom_power, t, 0.4)
    sacher_aom_switch.enable(t) 
    t+=2e-6

    #sacher_aom_switch.enable(t + 4e-6)
    #dt852_aom_switch.disable(t+4e-6)
    #spcm_on_trigger.trigger(t, duration=(probe_duration + 4.5e-6))
    #t += 50e-6
    #t += 500e-6
    #dt852_aom_switch.disable(t)
    #dt785_aom_switch.disable(t)
    
    spcm_on_trigger.trigger(t, duration=(probe_duration))
    t += probe_duration

    dt852_aom_switch.enable(t)
    dt785_aom_switch.enable(t)

    #dt852_aom_switch.enable(t)
    #utils.jump_from_previous_value(sacher_aom_power, t + 6e-6, 0.0)
    utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    t+=2e-6
    utils.jump_from_previous_value(control_aom_power, t, 0)
    spcm_counter.acquire(t, 2e-6)
    #spcm_counter.trigger(t, 100e-6)
        
    #sacher_aom_switch.disable(t + 4e-6)
    sacher_aom_switch.disable(t)
    control_aom_switch.disable(t)


    t += 100e-6
    # if we want to have side imaging after:
    #t += image_cmot(t, control=False, duration=60e-3)
    t += 100e-6

    utils.jump_from_previous_value(big_z_coil, t, 0)
    t += reset_mot(t)

    stop(t)