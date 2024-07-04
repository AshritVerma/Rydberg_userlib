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

from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    t=100e-3

    start()
    
    control_aom_power.constant(t+1e-6, 2.0)
    control_aom_switch.enable(t+1.25e-6)
    control_aom_power.constant(t+2.3e-6, 1.0)
    # control_aom_power.constant(t+1e-3, 0)
    # control_aom_power.constant(t+1.5e-3, 1.0)
    control_aom_power.constant(t+2e-3, 0)

    stop(2)