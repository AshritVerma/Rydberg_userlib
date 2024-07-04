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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_cmot_cut,image_dt, setup_slm
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

  # Import and define the global variables for devices
    cxn_table()

    #slm_set_zernike()

    t=0

    # if TRAP_NUM == 1:
    #   slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    # if TRAP_NUM == 2:
    #     slm.two_traps(target_sep=TRAP_SEPARATION, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, alpha=TRAP_ALPHA)
    # if TRAP_NUM == 3:
    #     slm.array_traps(phase_pattern_file=ARR_FILE, phase_pattern_folder=ARR_FOLDER, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS, alpha=TRAP_ALPHA)
    # slm_set_zernike()
    # slm.clip_circle(clip_circle_bool=CLIP_SLM_BOOL, px_ring=CLIP_RING_PIXELS)
    setup_slm()


    start()


    
    t+= load_mot(t, 1)

    # is_it_top_control.enable(t) # use if you want top control

    # utils.jump_from_previous_value(control_aom_power, t, 2.0)
    # control_aom_switch.enable(t)

    # t+=200e-3
    # ##temporary code
    # utils.jump_from_previous_value(control_aom_power, t, 2.0)
    # control_aom_switch.enable(t)
    # t+=10e-3
    # utils.jump_from_previous_value(control_aom_power, t, 0.0)
    # control_aom_switch.disable(t)
    
    t += mloop_compress_mot(t, 40e-3)

    repump_aom_switch.disable(t)
    motl_aom_switch.disable(t + 500e-6)
    utils.jump_from_previous_value(motl_aom_power, t, 0)
    utils.jump_from_previous_value(repump_aom_power, t + 500e-6, 0)

    zero_B_fields(t, duration = 5e-3)
    t += 0.7e-3
    # I temporarily put the repump back to an optimal value for imaging. We should put this in the imaging code instead
    motl_repump_ad9959.jump_frequency(t, "Repump", MOT_REPUMP_FREQ)

    # t += 20e-3
    #t += hold_dt(t, duration=DT_WAIT_DURATION)


    # exposure_time = 500e-6
    # sacher_aom_power.constant(t, 3)
    # sacher_aom_switch.enable(t)
    # sacher_aom_switch.disable(t+exposure_time)
    # t += exposure_time

    # t += 1e-3

    ##temporary code
    # utils.jump_from_previous_value(control_aom_power, t, 2.0)
    # control_aom_switch.enable(t)
    # t+=2e-3
    # utils.jump_from_previous_value(control_aom_power, t, 0.0)
    # control_aom_switch.disable(t)

    # utils.jump_from_previous_value(sacher_aom_power, t, 2.0)
    # sacher_aom_switch.enable(t)
    # t+= 50e-6
    # utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    # sacher_aom_switch.disable(t)

    # t+= 5e-3
    # motl_aom_switch.enable(t + 500e-6)
    t += image_cmot(t, control=False, repump=True, control_duration =100e-6, control_power = 2.0, duration=60e-3)
    # t += image_cmot_cut(t,deplete_atoms_time = 100e-6, duration=60e-3)

    t += reset_mot(t)

    stop(t)