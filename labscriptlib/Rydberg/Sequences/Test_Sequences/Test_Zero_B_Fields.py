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

    # # Set the params that do not change over course of expt
    # utils.set_static_parameters()
    pts_probe.program_single_freq(PROBE_FREQ)
    smc_sg1.set_freq_amp(CONTROL_FREQ,19)


    t=0.0

    start()
    
    t+= load_mot(t, 1)

    t += compress_mot(t, 50e-3)

    zero_B_fields(t, duration=5e-3)
    t += hold_dt(t, duration = 5e-3)

    add_time_marker(t, "RAMP_UP_B_FIELD")
    utils.jump_from_previous_value(big_z_coil, t, 0.2) # choose how big of quantization we want
    t+= 10e-3

    # turn on repump right before imaging. In real sequence we should have OP in this place.
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+= 300e-6
    
    # Add optical pumping:
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

    probe_duration = 60e-6 #150e-6

    utils.jump_from_previous_value(sacher_aom_power, t, 0.35) # 0.6
    sacher_aom_switch.enable(t) 
    t+=2e-6
    
    spcm_on_trigger.trigger(t, duration=(probe_duration))
    # acquiring with HRM takes a longer time than the probe duration
    t += probe_duration
    #dt852_aom_switch.enable(t)
    #dt785_aom_switch.enable(t)

    #dt852_aom_switch.enable(t)
    #utils.jump_from_previous_value(sacher_aom_power, t + 6e-6, 0.0)
    utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    t+=2e-6
    spcm_counter.acquire(t, 2e-6)
        
    sacher_aom_switch.disable(t)
    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)

    t += 100e-6

    utils.jump_from_previous_value(big_z_coil, t, 0)
    t += reset_mot(t)

    stop(t)