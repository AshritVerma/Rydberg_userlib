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

    t=0

    start()
    
    t+= load_mot(t, 1)

    #control_aom_switch.enable(t)
    times_to_trigger = pts_probe.program_ramp_freq(min_freq=SPCM_MIN_FREQ, max_freq=SPCM_MAX_FREQ, step_freq=SPCM_STEP_FREQ)
    probe_duration = 2.0 #30e-6
    spcm_on_trigger.trigger(t, duration=probe_duration*times_to_trigger)
    t += probe_duration
    for _ in range(times_to_trigger):
        pts_probe.trigger(t, 1e-6)
        spcm_counter.acquire(t, 1e-6)
        t += probe_duration

    # Trigger again to move the last value from the buffer
    t += 3e-6
    sacher_aom_switch.disable(t)
    #control_aom_switch.disable(t)
    utils.jump_from_previous_value(sacher_aom_power, t, 0)
    #utils.jump_from_previous_value(control_aom_power, t, 0)
    utils.jump_from_previous_value(big_z_coil, t, 0)

    t += reset_mot(t)

    stop(t)