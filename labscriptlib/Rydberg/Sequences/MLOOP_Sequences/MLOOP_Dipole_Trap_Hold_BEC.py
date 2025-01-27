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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt, setup_slm
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    
    # if TRAP_NUM == 1:
    #     slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    # if TRAP_NUM == 2:
    #     slm.two_traps(target_sep=TRAP_SEPARATION, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, alpha=TRAP_ALPHA)
    # if TRAP_NUM == 3:
    #     slm.array_traps(phase_pattern_file=ARR_FILE, phase_pattern_folder=ARR_FOLDER, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS, alpha=TRAP_ALPHA)
    # slm.clip_circle(clip_circle_bool=CLIP_SLM_BOOL, px_ring=CLIP_RING_PIXELS)
    setup_slm()
    # slm_set_zernike()
    
    t=0

    start()
    
    t+= load_mot(t, 1)#1)

    t += mloop_compress_mot(t, 40e-3)

    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    motl_aom_switch.disable(t + 500e-6)
    utils.jump_from_previous_value(motl_aom_power, t + 500e-6, 0)


    utils.jump_from_previous_value(z_coil, t, 5.0)
    zero_B_fields(t, duration = 5e-3)
    t+= 10e-3

    #turn on mot to start from F=1:
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(motl_aom_power, t , 2)
    motl_aom_switch.enable(t)
    motl_aom_switch.disable(t+ 100e-6)
    utils.jump_from_previous_value(motl_aom_power,t+ 100e-6, 0)
    t+=100e-6

    # motl_repump_ad9959.jump_frequency(t, "MOT", DTWAITING_MOT_FREQ)
    # motl_repump_ad9959.jump_frequency(t, "Repump", DTWAITING_REPUMP_FREQ)
    # t+=10e-3
    # Put atoms in F=2 before optical pumping
    # utils.jump_from_previous_value(repump_aom_power, t, 0.5)
    # repump_aom_switch.enable(t)
    # t+= 50e-6
    # repump_aom_switch.disable(t)
    # utils.jump_from_previous_value(repump_aom_power, t, 0)


    # ########
    #add_time_marker(t, "RAMP_UP_B_FIELD")
    utils.jump_from_previous_value(z_coil, t, 5.0)
    t+= 10e-3

    t += hold_dt(t, repump_atoms_to_F2 = False, duration=DT_WAIT_DURATION)
    # t += hold_dt(t, duration=DT_WAIT_DURATION)

    # Put atoms in F=2 before optical pumping
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+= 300e-6
    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)

    # # # Add optical pumping:
    t+=100e-6
    utils.jump_from_previous_value(op_aom_power, t, 0.8)#0.6)
    op_aom_switch.enable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0.5)#2)
    repump_aom_switch.enable(t)
    t+= 0.5e-3 #OP_OPTIMIZATION_TIME
    utils.jump_from_previous_value(op_aom_power, t, 0)
    op_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)

    t+=100e-6
    # dt_ramp_down_time = 1e-3
    # utils.ramp_from_previous_value(dt808_aom_power, t, duration=dt_ramp_down_time, final_value=3.0, samplerate=COIL_SAMPLE_RATE*20)
    # t += dt_ramp_down_time
    
    
    ### DELETE ME
    # motl_repump_ad9959.jump_frequency(t, "Repump", REPUMP_TEST_RESONANCE_FREQ)
    # t += 1e-3
    # motl_repump_ad9959.jump_frequency(t, "MOT", MOT_TEST_RESONANCE_FREQ+266e6)
    # t += 1e-3

    # utils.jump_from_previous_value(motl_aom_power, t, 2)
    # motl_aom_switch.enable(t)
    # time_on = 100e-6
    # utils.jump_from_previous_value(motl_aom_power, t+time_on, 0)
    # motl_aom_switch.disable(t+time_on)
    # t+=time_on
    # t+= 1e-3

    # utils.jump_from_previous_value(repump_aom_power, t, 0.2)
    # repump_aom_switch.enable(t)
    # time_on = 10e-6
    # utils.jump_from_previous_value(repump_aom_power, t+time_on, 0)
    # repump_aom_switch.disable(t+time_on)
    # t+=time_on
    # t+= 1e-3
    ###

    ### Once atoms are optically pump switch from Z B field to Y B field
    coil_ramping_time = 1e-3
    utils.ramp_from_previous_value(y_coil, t,coil_ramping_time, 7, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(z_coil, t,coil_ramping_time, 0, samplerate=COIL_SAMPLE_RATE) 
    t +=coil_ramping_time

    t += 2e-6
    # I temporarily put the repump back to an optimal value for imaging. We should put this in the imaging code instead
    motl_repump_ad9959.jump_frequency(t, "Repump", MOT_REPUMP_FREQ)

    # t += image_cmot(t, control=False, traps_off = False, repump = True, control_duration =50e-6, control_power = 2.0, duration=60e-3)
    t += image_dt(t, repump = True, repump_during_img = False,duration=60e-3)

    t += reset_mot(t)

    stop(t)