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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_cmot_cut,image_dt
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

  # Import and define the global variables for devices
    cxn_table()

    #slm_set_zernike()

    t=0

    slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    slm_set_zernike()
    
    start()


    t+= load_mot(t, 1)

    t += mloop_compress_mot(t, 40e-3)

    repump_aom_switch.disable(t)
    motl_aom_switch.disable(t + 500e-6)
    utils.jump_from_previous_value(motl_aom_power, t, 0)
    utils.jump_from_previous_value(repump_aom_power, t + 500e-6, 0)

    zero_B_fields(t, duration = 5e-3)
    t += 0.7e-3
    # I temporarily put the repump back to an optimal value for imaging. We should put this in the imaging code instead
    motl_repump_ad9959.jump_frequency(t, "Repump", MOT_REPUMP_FREQ)

    # utils.jump_from_previous_value(sacher_aom_power, t, 2)
    # sacher_aom_switch.enable(t)

    #t += 50e-3
    #t += hold_dt(t, duration=DT_WAIT_DURATION)


    # exposure_time = 500e-6
    # sacher_aom_power.constant(t, 3)
    # sacher_aom_switch.enable(t)
    # sacher_aom_switch.disable(t+exposure_time)
    # t += exposure_time

    #t += image_cmot(t, control=True, repump = True, control_duration =60e-6, control_power = 2.0, duration=60e-3)
    t += image_cmot_cut(t,deplete_atoms_time = 100e-6, duration=60e-3)

    t += reset_mot(t)

    stop(t)