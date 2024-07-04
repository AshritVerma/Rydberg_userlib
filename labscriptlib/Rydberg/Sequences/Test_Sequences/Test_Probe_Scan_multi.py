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

    # # Set the MOT and Repump frequencies at the beginning
    # motl_freq_list = [MOT_MOTL_FREQ, CMOT_MOTL_FREQ, DTWAITING_MOT_FREQ, MOT_MOTL_FREQ]
    # repump_freq_list = [MOT_REPUMP_FREQ,CMOT_REPUMP_FREQ, DTWAITING_REPUMP_FREQ, MOT_REPUMP_FREQ]
    # motl_repump_ad9959.program_freq("MOT", motl_freq_list)
    # motl_repump_ad9959.program_freq("Repump", repump_freq_list)

    # # Set the params that do not change over course of expt
    # utils.set_static_parameters()
    pts_probe.program_single_freq(PROBE_FREQ)
    smc_sg1.set_freq_amp(CONTROL_FREQ,19)

    # If we are using MW in EIT:
    #agilent_awg2.program_gated_TTL(0.002,50e-6,1000) # MW DC input into mixer, input parameters: voltage, pulse duration, keep frequency input high


    t=0.0

    start()
    
    t+= load_mot(t, 1)

    t += compress_mot(t, 50e-3)

    zero_B_fields(t, duration=5e-3)
    #t += hold_dt(t, duration = DT_WAIT_DURATION)
    t += reshape_dt(t, duration = DT_WAIT_DURATION)

    add_time_marker(t, "RAMP_UP_B_FIELD")
    utils.jump_from_previous_value(big_z_coil, t, 5.0)
    t+= 10e-3

    # turn on repump right before imaging. In real sequence we should have OP in this place.
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+= 300e-6
    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    
    # Add optical pumping:
    t+=100e-6
    utils.jump_from_previous_value(op_aom_power, t, 2.0)
    op_aom_switch.enable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+=3000e-6
    utils.jump_from_previous_value(op_aom_power, t, 0)
    op_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)
    t+=100e-6 # add this time to allow for AOM to turn off


    ############# temp code
    ## turn off B during imaging for testing purpose
    utils.jump_from_previous_value(big_z_coil, t, 5.0)
    t+= 2e-3

    #add side imaging beam + control beam for depleting atoms


    #t += probe_with_spcm(t,probe_duration = 10e-6)
    #pts_probe.program_single_freq(PROBE_FREQ)
    #t+= 100e-6
    probe_duration = 5e-6 #150e-6

    for _ in range(20):
        dt852_aom_switch.disable(t)
        dt785_aom_switch.disable(t)
        utils.jump_from_previous_value(control_aom_power, t, 2.0)
        control_aom_switch.enable(t)
        t+=2e-6
        utils.jump_from_previous_value(sacher_aom_power, t, 0.09) # 0.6
        sacher_aom_switch.enable(t) 
        t+=2e-6
        spcm_on_trigger.trigger(t, duration=(probe_duration))
        t += probe_duration+200e-9
        dt852_aom_switch.enable(t)
        dt785_aom_switch.enable(t)
        utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
        sacher_aom_switch.disable(t)
        t+=2e-6
        utils.jump_from_previous_value(control_aom_power, t, 0.0)
        utils.jump_from_previous_value(op_aom_power, t, 2.0)
        op_aom_switch.enable(t)
        utils.jump_from_previous_value(repump_aom_power, t, 2.0)
        repump_aom_switch.enable(t)
        t+=20e-6
        utils.jump_from_previous_value(op_aom_power, t, 0)
        op_aom_switch.disable(t)
        utils.jump_from_previous_value(repump_aom_power, t, 0)
        repump_aom_switch.disable(t)

    #[start_time + probe_duration + 4e-6 + extra_SPCM_time])
    #spcm_counter.acquire(t + 5e-6, 2e-6)
    spcm_counter.acquire(t, 2e-6)
    #spcm_counter.trigger(t, 100e-6)
        
    #sacher_aom_switch.disable(t + 4e-6)
    sacher_aom_switch.disable(t)
    control_aom_switch.disable(t)

    t += 100e-6

    #t += hrm.fake_triggers(t, spcm_on_trigger)

    # if we want to have side imaging after:
    #t += image_cmot(t, control=False, duration=60e-3)
    t += 100e-6

    #utils.jump_from_previous_value(big_z_coil, t, 0)
    t += reset_mot(t)

    stop(t)