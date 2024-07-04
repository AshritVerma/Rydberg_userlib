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
)
import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_dt, load_mot, compress_mot, reset_mot, image_cmot
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    # Set the MOT and Repump frequencies at the beginning
    motl_freq_list = [MOT_MOTL_FREQ, CMOT_MOTL_FREQ, DTWAITING_MOT_FREQ, IMG_MOTL_FREQ,MOT_MOTL_FREQ]
    repump_freq_list = [MOT_REPUMP_FREQ, CMOT_REPUMP_FREQ, DTWAITING_REPUMP_FREQ, MOT_REPUMP_FREQ]
    motl_repump_ad9959.program_freq("MOT", motl_freq_list)
    motl_repump_ad9959.program_freq("Repump", repump_freq_list)

    # Set the params that do not change over course of expt
    utils.set_static_parameters()
    t=0

    start()
    
    t+= load_mot(t, 1)

    t += compress_mot(t, 50e-3)

    # set up coils
    utils.jump_from_previous_value(big_x_coil, t, 0.005)
    utils.jump_from_previous_value(big_z_coil, t, 0)
    #utils.jump_from_previous_value(small_x_coil, start_time, MOT_SMALL_X_COIL)
    utils.jump_from_previous_value(small_y_coil, t, 0.05)
    utils.jump_from_previous_value(small_z_coil, t, 0.23)
    utils.jump_from_previous_value(gradient_coil, t, 0)
    gradient_coil_switch.constant(t, 0)

    # set up laser AOMs
    repump_trigger.trigger_next_freq(t)
    motl_trigger.trigger_next_freq(t)
    repump_aom_switch.disable(t)
    motl_aom_switch.disable(t)
    utils.jump_from_previous_value(motl_aom_power, t, 0)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    utils.jump_from_previous_value(dt852_aom_power, t, 2)
    utils.jump_from_previous_value(dt1064_aom_power, t, 0)

    t += DT_WAIT_DURATION

    t += image_dt(t, duration=60e-3)

    t += reset_mot(t)

    stop(t)