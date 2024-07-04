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
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import load_mot

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    t=20e-3

    start()
    d=.01
    t+= load_mot(t, .1)
    for i in range(7):
        test_6534_21.go_high(t)
        t+=d
        test_6534_21.go_low(t)
        t+=d



    stop(t)