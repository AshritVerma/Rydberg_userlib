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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import load_mot
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    t=0
    start()

    utils.jump_from_previous_value(big_x_coil, t+1e-3, 0.0)
    #time_start, min_freq, max_freq, step_freq, trigger_spacing
    t+=1
    t += pts_probe.program_ramp_freq(time_start=t, min_freq=1100, max_freq=1200, step_freq=1, trigger_spacing=.01)


    stop(t+1e-3)