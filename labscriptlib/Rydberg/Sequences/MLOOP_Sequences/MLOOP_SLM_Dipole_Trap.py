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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, image_dt, load_mot, compress_mot, reset_mot, zero_B_fields, hold_dt, reshape_dt, slm_set_zernike
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':
    
    # Import and define the global variables for devices
    cxn_table()
    
    if TRAP_NUM == 1:
        slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    if TRAP_NUM == 2:
        slm.two_traps(target_sep=TRAP_SEPARATION, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, alpha=TRAP_ALPHA)
    if TRAP_NUM == 3:
        slm.array_traps(phase_pattern_file=ARR_FILE, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS, alpha=TRAP_ALPHA)
    slm_set_zernike()
    
    t=0

    start()
    
    t+= load_mot(t, 1)

    # t += compress_mot(t, 50e-3)

    # zero_B_fields(t, duration = 5e-3)

 #___________________________________________________________________________   
    t += mloop_compress_mot(t, 40e-3)



    zero_B_fields(t, duration = 5e-3)

    
    #turn on mot to start from F=1:
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(motl_aom_power, t , 2)
    motl_aom_switch.enable(t)
    motl_aom_switch.disable(t+ 100e-6)
    utils.jump_from_previous_value(motl_aom_power,t+ 100e-6, 0)
    t+=100e-6

    # t+=10e-3
    
    t += hold_dt(t, duration=DT_WAIT_DURATION)

    t += 2e-6
    motl_repump_ad9959.jump_frequency(t, "Repump", MOT_REPUMP_FREQ)
#_____________________________________________________
    # t += image_cmot(t, control=False, repump = False, control_duration =20e-6, control_power = 2.0, duration=60e-3)
    t += image_dt(t, duration=60e-3)
    
    t += reset_mot(t)

    stop(t)