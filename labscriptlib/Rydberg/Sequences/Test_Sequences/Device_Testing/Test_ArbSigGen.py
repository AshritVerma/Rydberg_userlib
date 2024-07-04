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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import load_mot, mot_image, reset_mot
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    # Set the MOT and Repump frequencies at the beginning
    #agilent_A.program_gated_sine(AWG_FREQ, 2.0, 0.0)
    agilent_A.program_DC(1)
    t=0

    start()

    t += 1e-3
    utils.jump_from_previous_value(big_x_coil, t, 0)
    agilent_A.trigger(t, 1)

    t += 1.5

    stop(t)