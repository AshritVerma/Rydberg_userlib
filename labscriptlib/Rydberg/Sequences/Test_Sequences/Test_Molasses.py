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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot,zero_B_fields, molasses
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    # Set the MOT and Repump frequencies at the beginning
    motl_freq_list = [MOT_MOTL_FREQ, CMOT_MOTL_FREQ, MOLASSES_MOTL_FREQ, IMG_MOTL_FREQ, MOT_MOTL_FREQ]
    repump_freq_list = [MOT_REPUMP_FREQ, CMOT_REPUMP_FREQ, MOLASSES_REPUMP_FREQ, MOT_REPUMP_FREQ]
    motl_repump_ad9959.program_freq("MOT", motl_freq_list)
    motl_repump_ad9959.program_freq("Repump", repump_freq_list)

    # Set the params that do not change over course of expt
    utils.set_static_parameters()
    t=0

    start()
    
    t+= load_mot(t, 1)

    t += compress_mot(t, 50e-3)

    zero_B_fields(t, duration=5e-3)
    
    molasses_duration = 5e-3
    t +=  molasses(t, duration = molasses_duration)

    t += image_cmot(t, duration=60e-3)

    t += reset_mot(t)

    stop(t)