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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt, reshape_dt_3traps, reshape_dt_3traps_try2
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    slm_set_zernike()
    
    # mirror_controller.set_position('spcm_close', horizontal_position=16321, vertical_position=9950)
    
    t=0

    start()
    
    t+= load_mot(t, 1)

    t += mloop_compress_mot(t, 40e-3)

    zero_B_fields(t, duration = 5e-3)

    # # set MOT and repump frequency to off-resonant values and turn these lasers off
    # motl_repump_ad9959.jump_frequency(t, "MOT", DTWAITING_MOT_FREQ)
    # motl_repump_ad9959.jump_frequency(t, "Repump", DTWAITING_REPUMP_FREQ)
    # repump_aom_switch.disable(t)
    # motl_aom_switch.disable(t)
    # utils.jump_from_previous_value(motl_aom_power, t, 0)
    # utils.jump_from_previous_value(repump_aom_power, t, 0)

    # # hold in top trap for 20ms, then slowly turn down the power of top trap in next 20ms while increasing side DT power, hold crossed for the rest of the duration
    # #utils.jump_from_previous_value(dt785_aom_power, start_time, 0)
    # dt808_aom_switch.enable(t)
    # dt785_aom_switch.enable(t)
    # CMOT_OFF_TIME = 50e-3
    # TOP_RAMP = 150e-3 #80e-3
    # SIDE_RAMP = 150e-3 #100e-3
    # utils.ramp_from_previous_value(dt808_aom_power, t+ CMOT_OFF_TIME + SIDE_RAMP*1.5, TOP_RAMP, RESHAPE_TOP_LEVEL, samplerate=COIL_SAMPLE_RATE)
    # #utils.ramp_from_previous_value(dt785_aom_power, t+CMOT_OFF_TIME + TOP_RAMP, SIDE_RAMP, RESHAPE_SIDE_LEVEL_785, samplerate=COIL_SAMPLE_RATE)
    # utils.ramp_from_previous_value(dt852_aom_power, t+CMOT_OFF_TIME , SIDE_RAMP, RESHAPE_SIDE_LEVEL_852, samplerate=COIL_SAMPLE_RATE)
    # utils.ramp_from_previous_value(dt785_aom_power, t+CMOT_OFF_TIME , SIDE_RAMP, RESHAPE_SIDE_LEVEL_785, samplerate=COIL_SAMPLE_RATE)
    # #utils.ramp_from_previous_value(dt808_aom_power, t+ CMOT_OFF_TIME + SIDE_RAMP*1.7, TOP_RAMP, RESHAPE_TOP_LEVEL, samplerate=COIL_SAMPLE_RATE)
    # utils.ramp_from_previous_value(dt852_aom_power, t+ CMOT_OFF_TIME + SIDE_RAMP*2.5, TOP_RAMP, RESHAPE_SIDE_LEVEL_852-0.03, samplerate=COIL_SAMPLE_RATE)
    # utils.ramp_from_previous_value(dt785_aom_power,t+ CMOT_OFF_TIME + SIDE_RAMP*2.5, TOP_RAMP, RESHAPE_SIDE_LEVEL_785-0.03, samplerate=COIL_SAMPLE_RATE)
    
    # utils.ramp_from_previous_value(dt852_aom_power, t+ CMOT_OFF_TIME + SIDE_RAMP*2.5+TOP_RAMP, 20e-3, RESHAPE_SIDE_LEVEL_852+0.1, samplerate=COIL_SAMPLE_RATE)
    # utils.ramp_from_previous_value(dt785_aom_power,t+ CMOT_OFF_TIME + SIDE_RAMP*2.5+TOP_RAMP, 20e-3, RESHAPE_SIDE_LEVEL_785+0.1, samplerate=COIL_SAMPLE_RATE)
    # utils.ramp_from_previous_value(dt808_aom_power, t+ CMOT_OFF_TIME + SIDE_RAMP*2.5+TOP_RAMP*1.3, 20e-3, RESHAPE_TOP_LEVEL+0.35, samplerate=COIL_SAMPLE_RATE)

    # # when we control side traps with commertial AOM we can just set the power to 0 to disable traps:
    # t += DT_WAIT_DURATION
    #t += hold_dt(t, duration=DT_WAIT_DURATION)
    #t += reshape_dt_3traps(t, duration=DT_WAIT_DURATION)
    t += reshape_dt_3traps_try2(t, duration=DT_WAIT_DURATION)

    

    ## Add on-resonant light:
    # Ramp up the B field if we need it to push atoms with resonant light
    utils.jump_from_previous_value(z_coil, t, 5.0)
    t+= 10e-3

    ## adding side imaging for cleaning up tails
    #utils.jump_from_previous_value(sacher_aom_power, t, 0.08) # 0.6
    # imaging_aom_power.constant(t, 2.0)
    # imaging_aom_switch.enable(t)
    # t+=15e-3
    # imaging_aom_switch.disable(t)
    # imaging_aom_power.constant(t, 0.0)
    # t+= 2e-6

    # utils.jump_from_previous_value(sacher_aom_power, t, 1.0) # 0.6
    # sacher_aom_switch.enable(t) 
    # t+= 100e-6
    # utils.jump_from_previous_value(sacher_aom_power, t, 0.0) # 0.6
    # sacher_aom_switch.disable(t) 
    
    t += 1e-6
    # I temporarily put the repump back to an optimal value for imaging. We should put this in the imaging code instead
    motl_repump_ad9959.jump_frequency(t, "Repump", MOT_REPUMP_FREQ)
    t += image_cmot(t, control=False, repump = True, control_duration = 5e-6, control_power = 2.0, duration=60e-3)
    #t += image_dt(t, repump = True, duration=60e-3)


    t += reset_mot(t)

    stop(t)