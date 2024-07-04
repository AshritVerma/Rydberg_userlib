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

    t=0

    start()
    
    t+= 10e-3
    slm.set_zernike([.0, 0, .0])
    y_coil.constant(t, 1)
    x_coil.constant(t, 1)
    t+=0.3


    stop(max(t, 1))