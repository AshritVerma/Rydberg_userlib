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

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    t=5e-3

    start()
    
    utils.jump_from_previous_value(big_x_coil, t, 0)
    dt=20e-3
    t += dt
    utils.jump_from_previous_value(big_x_coil, t, 2)
    t += dt
    utils.jump_from_previous_value(big_x_coil, t, -0.1)
    t += dt
    utils.jump_from_previous_value(big_x_coil, t, 0)
    t+=0.5



    stop(t)