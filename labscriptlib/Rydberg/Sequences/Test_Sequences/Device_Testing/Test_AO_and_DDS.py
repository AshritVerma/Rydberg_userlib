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

# This script is to test the analog output and Arduino dds controller

import numpy as np
from labscript import (
    start,
    stop,
)

import time
import labscript as lab
# from labscript_utils import import_or_reload
#
# # Connection_Table
#
# import_or_reload(r"C:\Users\12566\PycharmProjects\SineWaveTest\SineWaveCxnTable.py")

from labscriptlib.Rydberg.connection_table import cxn_table
if __name__ == '__main__':
    cxn_table()
    rate = 1e6
    MOT_freq_list = [5, 4, 3, 2, 1, 0.5]

    MOTRepump.program_freq("MOT", MOT_freq_list)


    start()
    # For some reason this is required to make the PB trigger
    #pb_digital_out.go_high(0)

    t=0.1

    duration = 1e-4
    analog1.constant(t, .3)

    analog1.constant(t+duration, 0)

    step_duration = 0.1
    t+=2
    MOT_step.trigger_next_freq(t+step_duration)

    MOT_step.trigger_next_freq(t+2*step_duration)

    MOT_step.trigger_next_freq(t+3*step_duration)

    MOT_step.trigger_next_freq(t+4*step_duration)

    MOT_step.trigger_next_freq(t+5*step_duration)

    stop(t + 6*step_duration)