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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import load_mot, image_mot, reset_mot, image_cmot
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    # # Set the MOT and Repump frequencies at the beginning
    # motl_freq_list = [MOT_MOTL_FREQ, IMG_MOTL_FREQ, MOT_MOTL_FREQ]
    # repump_freq_list = [MOT_REPUMP_FREQ, MOT_REPUMP_FREQ]
    # motl_repump_ad9959.program_freq("MOT", motl_freq_list)
    # motl_repump_ad9959.program_freq("Repump", repump_freq_list)

    # # Set the params that do not change over course of expt
    # utils.set_static_parameters()

    t=0

    start()
    

    t+= load_mot(t, 1)

    t += image_mot(t, duration=60e-3)

    t += reset_mot(t)

    stop(t)