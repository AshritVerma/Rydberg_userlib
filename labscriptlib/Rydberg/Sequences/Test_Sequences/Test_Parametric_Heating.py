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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, hold_dt, slm_set_zernike, image_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_compress_mot

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    slm_set_zernike()

    # Set the params that do not change over course of expt
    utils.set_static_parameters()
    agilent_awg1.program_gated_sine(PARAMETRIC_HEATING_FREQ, PARAMETRIC_HEATING_AMPL, PARAMETRIC_HEATING_OFFSET)

    t=0

    start()
    agilent_awg1.trigger(t, duration=5e-3+DT_WAIT_DURATION+50e-3+1)
    t+= load_mot(t, 1)
    

    t += mloop_compress_mot(t, 40e-3)
    zero_B_fields(t, duration = 5e-3)
    t += hold_dt(t, duration = DT_WAIT_DURATION)

    #t += image_cmot(t, duration=60e-3)
    t += image_cmot(t, control=False, traps_off = True, repump = True, control_duration =5e-6, control_power = 2.0, duration=60e-3)

    #t += image_dt(t, repump = True,duration=60e-3)

    t += reset_mot(t)

    stop(t)