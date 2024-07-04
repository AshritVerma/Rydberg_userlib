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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt,setup_slm
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
    #     slm.array_traps(phase_pattern_file=ARR_FILE, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS, alpha=TRAP_ALPHA)
    setup_slm()
    slm_set_zernike()
    
    # Set the params that do not change over course of expt
    utils.set_static_parameters()
    agilent_awg1.program_gated_sine(PARAMETRIC_HEATING_FREQ, PARAMETRIC_HEATING_AMPL, PARAMETRIC_HEATING_OFFSET)
    
    t=0

    start()
    agilent_awg1.trigger(t, duration=5e-3+DT_WAIT_DURATION+50e-3+23e-3+1)
    t+= load_mot(t, 1)#1)

    t += mloop_compress_mot(t, 40e-3)
    # t += compress_mot(t, 50e-3)

    
    #repump_aom_switch.disable(t)
    #motl_aom_switch.disable(t + 500e-6)
    #utils.jump_from_previous_value(motl_aom_power, t, 0)
    #utils.jump_from_previous_value(repump_aom_power, t + 500e-6, 0)

    #utils.jump_from_previous_value(motl_aom_power, t, 0)
    #utils.jump_from_previous_value(repump_aom_power, t, 0)

    zero_B_fields(t, duration = 5e-3)
    
    #t += mloop_hold_dt(t, duration=DT_WAIT_DURATION)


    # utils.jump_from_previous_value(z_coil, t, 5.0)
    t+= 10e-3
    # agilent_awg1.trigger(t+DT_WAIT_DURATION -20e-3+6e-3, duration=20e-3)
    t += hold_dt(t, duration=DT_WAIT_DURATION)


    #t += 2e-6
    # I temporarily put the repump back to an optimal value for imaging. We should put this in the imaging code instead
    motl_repump_ad9959.jump_frequency(t, "Repump", MOT_REPUMP_FREQ)
    
    #t += image_cmot(t, control=False, traps_off = True, repump = True, control_duration =5e-6, control_power = 2.0, duration=60e-3)
    t += image_dt(t, repump = True,duration=60e-3)

    t += reset_mot(t)

    stop(t)