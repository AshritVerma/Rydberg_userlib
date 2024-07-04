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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    slm_set_zernike()

    #for i in range(11):
    #freq_sub = -CONTROL_STEP_SIZE*i/10 + CONTROL_STEP_SIZE
    #smc_sg1.set_freq_amp(CONTROL_FREQ,19)
        # time.sleep(0.1)

    t=0

    start()
    
    t+= load_mot(t, 1)

    t += mloop_compress_mot(t, 40e-3)

    zero_B_fields(t, RSC=True, duration = 5e-3)
    t += hold_dt(t, duration=10e-3, repump_atoms_to_F2=True) # gradient coils take ~5ms of time to turn off
    
    #utils.jump_from_previous_value(small_z_coil, t, RSC_Z_COIL)
    utils.jump_from_previous_value(z_coil, t, 0.125)
    t+= 10e-3

    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+= 300e-6
    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    
    # # Add optical pumping:
    t+=100e-6
    utils.jump_from_previous_value(op_aom_power, t, 0.6)
    op_aom_switch.enable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+= 2e-3 #6e-3
    utils.jump_from_previous_value(op_aom_power, t, 0)
    op_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)
    #t+=200e-6
    t+=100e-6 # add this time to allow for AOM to turn off

    
    ######
    motl_repump_ad9959.jump_frequency(t, "Repump", MOT_REPUMP_FREQ)
    t+=1e-3

    t += image_cmot(t, control=False, repump = True, control_duration =10e-6, control_power = 2.0, duration=60e-3)

    t += reset_mot(t)

    stop(t)