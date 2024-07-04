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

    ### CHOOSE PROBE DURATION ###
    probe_duration = 40e-6 #150e-6
    preparation_duration = 20e-6
    time_btw_prep_detect = 2e-6

    pts_probe.program_single_freq(PROBE_FREQ)
    smc_sg1.set_freq_amp(CONTROL_FREQ,19) # Control EOM frequency
    #agilent_awg2.program_gated_TTL(1.0,preparation_duration,1000) # MW DC input into mixer, input parameters: voltage, pulse duration, keep frequency input high
    agilent_awg2.program_gated_TTL(1.0,80e-6,1000) # MW DC input into mixer, input parameters: voltage, pulse duration, keep frequency input high
    #agilentE8257D.set_freq_amp(MW_PREP_FREQ,16) # set MW freq in GHz, pow in dBm

    ## PREPARATION PULSE SHAPING:
    Max_photonRate = 1.0   # percentage relative to photon rate at 2V
    first_pulse_fraction = 2.0
    second_pulse_fraction = 0.0
    off_fraction = 0.0

            
    Total_points = 200
    t_second_flat = 0.0
    t_first_flat = preparation_duration*10**6 - 1.0
    t_off = time_btw_prep_detect*10**6
    t_first_gauss = 1.0
    t_second_gauss = 0.0#probe_duration*10**6
    t_total = t_second_flat+t_first_flat+t_first_gauss + t_off + t_second_gauss 
    Num_first_gauss = int(Total_points*t_first_gauss/t_total)
    Num_second_gauss = int(Total_points*t_second_gauss/t_total)
    Num_second_flat = int(Total_points*t_second_flat/t_total)
    Num_first_flat = int(Total_points*t_first_flat/t_total)
    Num_off = int(Total_points*t_off/t_total)

            
    wfm = Max_photonRate*np.array([0.0] + list(first_pulse_fraction*signal.gaussian(2*Num_first_gauss,0.25*Num_first_gauss)[0:Num_first_gauss]) + [first_pulse_fraction]*int(Num_first_flat)+ [off_fraction]*int(Num_off)+list(second_pulse_fraction*signal.gaussian(2*Num_second_gauss,0.25*Num_second_gauss)[0:Num_second_gauss])+[second_pulse_fraction]*int(Num_second_flat))
    wfm = wfm - np.min(wfm)
    wf_time = t_total*10**-6
    agilent_awg1.send_wf(total_time=wf_time,voltages=wfm)



   ## CONTROL PULSE SHAPING:
    Max_ctrl = 1.0
    first_pulse_fraction = 2.0 #0.14
    second_pulse_fraction = 0.7
    off_fraction= 0.0
            
    Total_points = 470
    t_second_flat = probe_duration*10**6 - 1.0
    t_first_flat = preparation_duration*10**6 -0.5
    t_first_gauss = 0.5
    t_second_gauss = 1.0
    t_off = time_btw_prep_detect*10**6
    t_total = t_second_flat+t_first_flat+t_off +t_first_gauss+t_second_gauss
    Num_second_flat = int(Total_points*t_second_flat/t_total)
    Num_first_gauss = int(Total_points*t_first_gauss/t_total)
    Num_second_gauss = int(Total_points*t_second_gauss/t_total)
    Num_first_flat = int(Total_points*t_first_flat/t_total)
    Num_off = int(Total_points*t_off/t_total)
            
    wfm = Max_ctrl*np.array([first_pulse_fraction]*int(Num_first_flat)+list(first_pulse_fraction*signal.gaussian(2*Num_first_gauss,0.25*Num_first_gauss)[Num_first_gauss:2*Num_first_gauss]) + [off_fraction]*int(Num_off) + list(second_pulse_fraction*signal.gaussian(2*Num_second_gauss,0.25*Num_second_gauss)[0:Num_second_gauss]) + [second_pulse_fraction]*int(Num_second_flat)+10*[0.0])
    #wfm = Max_ctrl*np.array([0.0] + [first_pulse_fraction]*int(Num_first_flat) + [off_fraction]*int(Num_off) + list(second_pulse_fraction*signal.gaussian(2*Num_second_gauss,0.25*Num_second_gauss)[0:Num_second_gauss]) + [second_pulse_fraction]*int(Num_second_flat)+10*[0.0])
    wfm = wfm - np.min(wfm)
    wf_time = t_total*10**-6
    agilent_awg3.send_wf(total_time=wf_time,voltages=wfm)



########## START SEQUENCE #############
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

    # Turn on REPUMP after holding atoms for some time
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+= 300e-6
    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    ######################################################
    

    ###### OPTICAL PUMPING STAGE ########################
    t+=10e-6
    utils.jump_from_previous_value(op_aom_power, t, 2.0)
    op_aom_switch.enable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+=300e-6
    utils.jump_from_previous_value(op_aom_power, t, 0)
    op_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)
    t+=100e-6 # add this time to allow for AOM to turn off
    ######################################################


    ###### PREPARE RYDBERG STATE ##########################
    #agilent_awg2.trigger(t, duration=2e-6) # turn on MW field for preparation
    agilent_awg3.trigger(t-1.0e-6,duration = 2e-6) # turn on control field AWG
    #control_aom_switch.enable(t-0.5e-6)
    #agilent_awg1.trigger(t-0.7e-6,duration = 2e-6) # turn on preparation beam AWG
    #probe_aom_switch.enable(t-0.5e-6)
    t += preparation_duration # DEFINE DURATION OF PREPARATION PULSE
    control_aom_switch.disable(t)
    probe_aom_switch.disable(t)
    ######################################################

    t += time_btw_prep_detect # add some spacing between preparation and readout


    ###### READOUT PREPARED STATE ##########################
    control_aom_switch.enable(t)
    dt852_aom_switch.disable(t)
    dt785_aom_switch.disable(t)
    t+=2e-6
    utils.jump_from_previous_value(sacher_aom_power, t, 2.0) # 0.6
    sacher_aom_switch.enable(t) 
    #t+=2e-6
    spcm_on_trigger.trigger(t, duration=(probe_duration))
    t += probe_duration
    dt852_aom_switch.enable(t)
    dt785_aom_switch.enable(t)

    utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    t+=2e-6
    spcm_counter.acquire(t, 2e-6)
    sacher_aom_switch.disable(t)
    control_aom_switch.disable(t)
    t += 100e-6
    #t += hrm.fake_triggers(t, spcm_on_trigger)
    ######################################################

    # if we want to have side imaging after:
    #t += image_cmot(t, control=False, duration=60e-3)
    t += 100e-6

    t += reset_mot(t)

    stop(t)