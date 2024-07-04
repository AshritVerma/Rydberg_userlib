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
    utils.jump_from_previous_value(sacher_aom_power, t+0.1, 0)
    hrm.acquire_data(0.1, 1e-3, dummy_6738, trigger_increment=1e-5)
    t = 0.1
    dt1 = 1e-5
    for i in range(5):
        dummy_6738.constant(t, 4)
        t+= dt1
        dummy_6738.constant(t, 0)
        t+= dt1
    
    dt2 = 2e-5
    for i in range(50):
        dummy_6738.constant(t, 4)
        t+= dt2
        dummy_6738.constant(t, 0)
        t+= dt2
    
    t+=0.3


    stop(max(t, 1))