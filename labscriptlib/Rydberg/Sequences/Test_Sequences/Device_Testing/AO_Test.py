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

import numpy as np
from labscript import (
    start,
    stop,
)

import labscript as lab
# from labscript_utils import import_or_reload
#
# # Connection_Table
#
# import_or_reload(r"C:\Users\12566\PycharmProjects\SineWaveTest\SineWaveCxnTable.py")

from labscriptlib.Rydberg.connection_table import cxn_table
if __name__ == '__main__':

    cxn_table()
    rate = 1e3
    start()

    t=0.1

    step_duration = 1
    analog1.constant(t, 1)

    # interval=5.6e-6
    # t+=step_duration + interval

    # analog1.constant(t, 1)

    # analog1.constant(t+step_duration, 0)

    
    t+=step_duration

    t+= analog1.sine(
    t=t,
    duration=1,
    amplitude=1.,
    angfreq=1e5 *2* np.pi,
    phase=0,
    dc_offset=0.0,
    samplerate=rate,
)


    stop(5)