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

from re import T
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

    #agilent_awg1.program_gated_sine(PARAMETRIC_HEATING_FREQ, PARAMETRIC_HEATING_AMPL, PARAMETRIC_HEATING_OFFSET)

    #for i in range(11):
    #freq_sub = -CONTROL_STEP_SIZE*i/10 + CONTROL_STEP_SIZE
    #smc_sg1.set_freq_amp(CONTROL_FREQ,19)
        # time.sleep(0.1)

    t=0

    start()
    #rsc_aom_switch.enable(t)
    #agilent_awg1.trigger(t, duration=5e-3+RSC_COOL_DURATION+60e-3+1)

    # # turn on lattice
    # utils.jump_from_previous_value(rsc_aom_power, t, RSC_LATTICE_POWER)
    # rsc_aom_switch.enable(t)

    t+= load_mot(t, 1)

    # ##turn on lattice
    # utils.jump_from_previous_value(rsc_aom_power, t, 0)
    # utils.ramp_from_previous_value(rsc_aom_power, t, duration=RSC_LATTICE_RAMP_DURATION, final_value=RSC_LATTICE_POWER, samplerate=RSC_LASER_SAMPLE_RATE)
    # rsc_aom_switch.enable(t)

    # t+= RSC_LATTICE_RAMP_DURATION


    t += mloop_compress_mot(t, 40e-3)


    zero_B_fields(t, RSC= True, duration = 5e-3)
    utils.jump_from_previous_value(small_z_coil, t, RSC_Z_COIL)
    utils.jump_from_previous_value(z_coil, t+0.3e-3, ZERO_Z_COIL)

    

    ## add additional lines from hold dt sequence:
    #    t += hold_dt(t, duration=DT_WAIT_DURATION)
    #t += hold_dt(t, duration= 0.5e-3, repump_atoms_to_F2=True)
    #t += reshape_dt(t, duration=DT_WAIT_DURATION)

    #t+=10e-3
    
    # turn on mot to start from F=1:
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(motl_aom_power, t , 2)
    motl_aom_switch.enable(t)
    motl_aom_switch.disable(t+ 100e-6)
    utils.jump_from_previous_value(motl_aom_power,t+ 100e-6, 0)
    t+=100e-6

    t += hold_dt(t, duration=DT_WAIT_DURATION)
  
    ### RSC sequence
    #jump repump frequency and setup z coil. Wait at least 500us so that repump lock adjusts
    motl_repump_ad9959.jump_frequency(t, "Repump", RSC_REPUMP_FREQ)
    t += 1e-3




    # turn on cooling light
    # t += 10e-3
    # utils.jump_from_previous_value(op_aom_power, t, RSC_REPUMP_POWER)
    # #utils.jump_from_previous_value(motl_aom_power, t , 0.15)
    # motl_aom_switch.enable(t)
    # op_aom_switch.enable(t)

    # t+= RSC_COOL_DURATION

    # # turn off cooling light
    # utils.jump_from_previous_value(op_aom_power, t, 0)
    # op_aom_switch.disable(t)

    # motl_aom_switch.disable(t)
    # utils.jump_from_previous_value(motl_aom_power,t, 0)
    # utils.jump_from_previous_value(small_z_coil, t, 0)


    ######
    motl_repump_ad9959.jump_frequency(t, "Repump", MOT_REPUMP_FREQ)
    t+=1e-3

    #turn off lattice
    #utils.ramp_from_previous_value(rsc_aom_power, t, duration=RSC_LATTICE_RAMP_DURATION, final_value=0, samplerate=RSC_LASER_SAMPLE_RATE)
    #t += RSC_LATTICE_RAMP_DURATION
    #rsc_aom_switch.disable(t)

    #t+=50e-3
    

    #t += image_cmot(t, control=False, repump = True, control_duration =10e-6, control_power = 2.0, duration=60e-3)
    #t += image_dt(t, duration=60e-3, repump=True, RSC=True) # for measuring TOF
    t += image_dt(t, repump = True,duration=60e-3)
    t += reset_mot(t)

    stop(t)