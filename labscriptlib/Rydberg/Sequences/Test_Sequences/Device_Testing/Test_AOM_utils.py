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
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    t = 0.5
    cxn_table()
    start()

    # Turn on the aom at t = 0.1 for 0.7 seconds, and set the power to 1. 
    # You can measure that this actually turns it on and off with the power meter
    test_trigger.trigger(t, 0.1)
    utils.aom_pulse("control", time_start=0.1, duration=0.7, power_level=1)
    t += 1.5

    stop(t)