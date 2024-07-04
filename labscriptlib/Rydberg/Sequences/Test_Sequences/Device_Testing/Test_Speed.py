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

from labscriptlib.Rydberg.Speedy_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    t=25e-3

    start()
    
    y_coil.constant(t, 4.0)
    t+=25e-3
    y_coil.constant(t, -4.0)
    t+=25e-3
    y_coil.constant(t, 0.0)
    t+=25e-3
    stop(t)