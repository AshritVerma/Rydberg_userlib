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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    slm_set_zernike()

    pts_probe.program_single_freq(PROBE_FREQ)
    
    mirror_controller.set_position('spcm_close', horizontal_position=16325, vertical_position=9950)
    
    t=0

    start()
    
    t+= load_mot(t, 1)

    t += mloop_compress_mot(t, 40e-3)

    zero_B_fields(t, duration = 5e-3)


    #add_time_marker(t, "RAMP_UP_B_FIELD")
    utils.jump_from_previous_value(z_coil, t, 5.0)
    t+= 10e-3
    
    #t += mloop_reshape_dt(t)#, duration = MLOOP_RESHAPE_TIME00+ MLOOP_RESHAPE_TIME01+ MLOOP_RESHAPE_TIME02+ MLOOP_RESHAPE_TIME03+ MLOOP_RESHAPE_TIME04+5e-6)
    #t += mloop_hold_dt(t, duration=DT_WAIT_DURATION)
    #utils.jump_from_previous_value(dt785_aom_power, t, 0)
    #t += reshape_dt(t, duration=DT_WAIT_DURATION)

    # set MOT and repump frequency to off-resonant values and turn these lasers off
    motl_repump_ad9959.jump_frequency(t, "MOT", DTWAITING_MOT_FREQ)
    motl_repump_ad9959.jump_frequency(t, "Repump", DTWAITING_REPUMP_FREQ)
    repump_aom_switch.disable(t)
    motl_aom_switch.disable(t)
    utils.jump_from_previous_value(motl_aom_power, t, 0)
    utils.jump_from_previous_value(repump_aom_power, t, 0)

    # hold in top trap for 20ms, then slowly turn down the power of top trap in next 20ms while increasing side DT power, hold crossed for the rest of the duration
    #utils.jump_from_previous_value(dt785_aom_power, start_time, 0)
    CMOT_OFF_TIME = 80e-3
    dt808_aom_switch.enable(t)
    t+= CMOT_OFF_TIME
    #utils.ramp_from_previous_value(dt785_aom_power, t, 50e-3, RESHAPE_SIDE_LEVEL, samplerate=AOM_SAMPLE_RATE)
    TOP_RAMP_DOWN = 20e-3
    utils.ramp_from_previous_value(dt808_aom_power, t, TOP_RAMP_DOWN, RESHAPE_TOP_LEVEL, samplerate=AOM_SAMPLE_RATE)
    t+= TOP_RAMP_DOWN + 1e-3
    SIDE_RAMP_UP = 20e-3
    dt785_aom_switch.enable(t)
    utils.ramp_from_previous_value(dt785_aom_power, t, SIDE_RAMP_UP, RESHAPE_SIDE_LEVEL, samplerate=AOM_SAMPLE_RATE)
    t+=SIDE_RAMP_UP + 1e-3


    # turn on repump at the end of this long sequence to bring atoms back from F=1 state:
    # utils.jump_from_previous_value(repump_aom_power, t + DT_WAIT_DURATION - 200e-6 , 2)
    # repump_aom_switch.enable(t + DT_WAIT_DURATION - 200e-6)
    # repump_aom_switch.disable(t + DT_WAIT_DURATION - 100e-6)
    # utils.jump_from_previous_value(repump_aom_power, t + DT_WAIT_DURATION - 100e-6, 0)

    t += DT_WAIT_DURATION - CMOT_OFF_TIME -TOP_RAMP_DOWN

    ## Add on-resonant light:
    # utils.jump_from_previous_value(sacher_aom_power, t, 1.0) # 0.6
    # sacher_aom_switch.enable(t) 
    # t+= 10e-6
    # utils.jump_from_previous_value(sacher_aom_power, t, 0.0) # 0.6
    # sacher_aom_switch.disable(t) 
    
    t += 1e-6
    # I temporarily put the repump back to an optimal value for imaging. We should put this in the imaging code instead
    motl_repump_ad9959.jump_frequency(t, "Repump", MOT_REPUMP_FREQ)
    t += image_cmot(t, control=False, repump = True, control_duration = 5e-6, control_power = 2.0, duration=60e-3)
    #t += image_dt(t, repump = True, duration=60e-3)

    t += reset_mot(t)

    stop(t)