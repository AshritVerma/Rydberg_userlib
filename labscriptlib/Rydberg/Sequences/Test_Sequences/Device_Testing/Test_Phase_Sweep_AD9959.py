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
from labscriptlib.Rydberg.connection_table import cxn_table
from user_devices.Rydberg.AD9959ArduinoComm.labscript_devices import AD9959ArduinoComm

if __name__ == '__main__':

    # Import and define the global variables for devices
    t = 0
    cxn_table()

    MOTRepump.program_freq('ch0', [10])
    MOTRepump.program_freq('ch1', [10])
    MOTRepump.program_phase('ch0', 0)
    MOTRepump.program_phase('ch1', 0)
    start()
    stop(1)