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
from user_devices.Rydberg.AD9959ArduinoComm.labscript_devices import AD9959ArduinoComm

if __name__ == '__main__':

    # Import and define the global variables for devices
    t = 0
    cxn_table()
    start()
    # ZL_NB_ad9959.program_freq('ZLC0', [12])
    # ZL_NB_ad9959.jump_frequency(t, "ZLC0", 20e6)
    # t += 1e-1
    freq = 12e6
    for i in range(100):
        if 1:#i%1 == 0:
            ZL_NB_ad9959.jump_frequency(t, "ZLC0", freq)
            freq += 5e4
        
        t += 1 * 1e-2

    stop(t)