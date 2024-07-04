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
from tkinter import N
from labscript import (
    start,
    stop,
)
import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt, reshape_dt_3traps_try2
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()
    
    if TRAP_NUM == 1:
        slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    if TRAP_NUM == 2:
        slm.two_traps(target_sep=TRAP_SEPARATION, alpha=TRAP_ALPHA, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    slm_set_zernike()
    
    pts_probe.program_single_freq(1120.0)

    # mirror_controller.set_position('spcm_close', horizontal_position=16321, vertical_position=9950)
    
    t=0

    start()
    
    t+= load_mot(t, 0.1)

    t += mloop_compress_mot(t, 40e-3)
    # t += compress_mot(t, 50e-3)

    repump_aom_switch.disable(t)
    motl_aom_switch.disable(t + 500e-6)
    utils.jump_from_previous_value(motl_aom_power, t, 0)
    utils.jump_from_previous_value(repump_aom_power, t + 500e-6, 0)

    zero_B_fields(t, duration = 5e-3)
    
    #t += mloop_reshape_dt(t)#, duration = MLOOP_RESHAPE_TIME00+ MLOOP_RESHAPE_TIME01+ MLOOP_RESHAPE_TIME02+ MLOOP_RESHAPE_TIME03+ MLOOP_RESHAPE_TIME04+5e-6)
    #t += mloop_hold_dt(t, duration=DT_WAIT_DURATION)
    #utils.jump_from_previous_value(dt785_aom_power, t, 0)
    #t += reshape_dt(t, duration=DT_WAIT_DURATION)
    t += reshape_dt_3traps_try2(t, duration=DT_WAIT_DURATION)

    # # get rid of the tails:
    #t_off = 30e-6
    #rounds = 14
    #for i in range(rounds):
        #dt785_aom_switch.enable(t)
        #dt808_aom_switch.disable(t)
        #t+=t_off
        #dt785_aom_switch.disable(t)
        #dt808_aom_switch.enable(t)
        #t+=t_off
        #dt785_aom_switch.enable(t)
        #dt808_aom_switch.enable(t)
        #t+=t_off

        # turn both on/off together
        # dt785_aom_switch.disable(t)
        # dt808_aom_switch.disable(t)
        # t+=t_off
        # dt785_aom_switch.enable(t)
        # dt808_aom_switch.enable(t)
        # t+=t_off
    
    t += 1e-6

    ## turn on-resonant light on to get rid of atoms in the wings:
    # utils.jump_from_previous_value(sacher_aom_power, t, 0.3) # 0.6
    # sacher_aom_switch.enable(t) 
    # t +=100e-6
    # utils.jump_from_previous_value(sacher_aom_power, t, 0.00) # 0.6
    # sacher_aom_switch.disable(t) 


    # I temporarily put the repump back to an optimal value for imaging. We should put this in the imaging code instead
    motl_repump_ad9959.jump_frequency(t, "Repump", MOT_REPUMP_FREQ)
    #t += image_cmot(t, control=False, repump = True, control_duration = 5e-6, control_power = 2.0, duration=60e-3)
    t += image_dt(t, repump = True,duration=60e-3)

    t += reset_mot(t)

    stop(t)