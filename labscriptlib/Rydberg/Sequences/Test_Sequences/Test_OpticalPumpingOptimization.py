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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, hold_dt, reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    #for i in range(11):
    #freq_sub = -CONTROL_STEP_SIZE*i/10 + CONTROL_STEP_SIZE
    # smc_sg1.set_freq_amp(CONTROL_FREQ,19)
        # time.sleep(0.1)

    t=0

    start()
    
    t+= load_mot(t, 1)

    t += compress_mot(t, 50e-3)

    zero_B_fields(t, duration = 5e-3)
    t += hold_dt(t, duration=DT_WAIT_DURATION)
    #t +=reshape_dt(t, duration=DT_WAIT_DURATION)

    #utils.aom_pulse("control", t, 50e-6, 2.0)

    ########
    #add_time_marker(t, "RAMP_UP_B_FIELD")
    utils.jump_from_previous_value(big_z_coil, t, 5.0)
    t+= 10e-3

    # turn on repump right before imaging. In real sequence we should have OP in this place.
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+= 300e-6
    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    
    # Add optical pumping:
    t+=100e-6
    utils.jump_from_previous_value(op_aom_power, t, 2.0)
    op_aom_switch.enable(t)
    #utils.jump_from_previous_value(repump_aom_power, t, 2)
    #repump_aom_switch.enable(t)
    t+=6e-3
    utils.jump_from_previous_value(op_aom_power, t, 0)
    op_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)
    #t+=200e-6
    t+=100e-6 # add this time to allow for AOM to turn off

    # utils.jump_from_previous_value(repump_aom_power, t, 2)
    # repump_aom_switch.enable(t)
    # t+= 15e-6
    # repump_aom_switch.disable(t)
    # utils.jump_from_previous_value(repump_aom_power, t, 0)

    utils.jump_from_previous_value(big_z_coil, t, 1.0)
    t+= 2e-3

    ######

    t += image_cmot(t, control=False, repump = False, control_duration =10e-6, control_power = 2.0, duration=60e-3)

    t += reset_mot(t)

    stop(t)