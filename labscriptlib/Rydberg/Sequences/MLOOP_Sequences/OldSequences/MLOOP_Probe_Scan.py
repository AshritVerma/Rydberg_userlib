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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt, reshape_dt_3traps,reshape_dt_3traps_try2
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    pts_probe.program_single_freq(PROBE_FREQ)
    #smc_sg1.set_freq_amp(CONTROL_FREQ,19)

    slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    slm_set_zernike()

    t=0

    start()
    
    t+= load_mot(t, 0.1) # load_mot(t, 1)

    t += mloop_compress_mot(t, 40e-3)

    zero_B_fields(t, duration = 5e-3)
    t += hold_dt(t, duration=DT_WAIT_DURATION)
    #t += reshape_dt(t, duration=DT_WAIT_DURATION)
    #t += reshape_dt_3traps(t, duration = DT_WAIT_DURATION)
    # t += reshape_dt_3traps_try2(t, duration = DT_WAIT_DURATION)

    #utils.aom_pulse("control", t, 50e-6, 2.0)

    ########
    #add_time_marker(t, "RAMP_UP_B_FIELD")
    utils.jump_from_previous_value(z_coil, t, 5.0)
    t+= 10e-3

    # turn on repump right before imaging. In real sequence we should have OP in this place.
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+= 300e-6
    repump_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    
    # Add optical pumping:
    t+=100e-6
    utils.jump_from_previous_value(op_aom_power, t, 0.6)
    op_aom_switch.enable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 2)
    repump_aom_switch.enable(t)
    t+= 2e-3 #200e-6#4.4e-3
    utils.jump_from_previous_value(op_aom_power, t, 0)
    op_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)
    #t+=200e-6
    t+=100e-6 # add this time to allow for AOM to turn off

    # utils.jump_from_previous_value(repump_aom_power, t, 2)
    # repump_aom_switch.enable(t)
    # t+= 15e-6
    # repump_aom_switch.disable(t)
    # utils.jump_from_previous_value(repump_aom_power, t, 0)

    # code for changing the quantization B field
    #utils.jump_from_previous_value(y_coil, t, 7.0)
    #utils.jump_from_previous_value(z_coil, t, 0.0)
    #t+=5e-3


    ###### probe
    
    #t += probe_with_spcm(t,probe_duration = 10e-6)
    #pts_probe.program_single_freq(PROBE_FREQ)
    #t+= 100e-6
    probe_duration = 60e-6 #150e-6

    dt808_aom_switch.disable(t)
    dt785_aom_switch.disable(t)
    utils.jump_from_previous_value(dt785_aom_power, t, 0.0)
    utils.jump_from_previous_value(dt852_aom_power, t, 0.0)
    utils.jump_from_previous_value(dt808_aom_power, t, 0.0)

    utils.jump_from_previous_value(control_aom_power, t, 2.0)
    control_aom_switch.enable(t)
    #agilent_awg2.trigger(t, duration=2e-6) # turn on MW field
    t+=2e-6
    # t+=500e-6
    # utils.jump_from_previous_value(control_aom_power, t, 0.0)
    # control_aom_switch.disable(t)

    # control power enable
    #control_aom_switch.enable(t)


    #sacher_aom_switch.disable(t)

    #t+=300e-6
    #sacher_aom_switch.enable(t)

    # ## adding side imaging for cleaning up tails
    # #utils.jump_from_previous_value(sacher_aom_power, t, 0.08) # 0.6
    # imaging_aom_power.constant(t, 2.0)
    # imaging_aom_switch.enable(t)
    # t+=3e-6
    # imaging_aom_switch.disable(t)
    # imaging_aom_power.constant(t, 0.0)

    utils.jump_from_previous_value(sacher_aom_power, t, 0.02) # 0.6
    sacher_aom_switch.enable(t) 
    t+=2e-6
 
    #t+=100e-6


    #sacher_aom_switch.enable(t + 4e-6)
    #dt852_aom_switch.disable(t+4e-6)
    #spcm_on_trigger.trigger(t, duration=(probe_duration + 4.5e-6))
    #t += 50e-6
    #t += 500e-6
    
    spcm_on_trigger.trigger(t, duration=(probe_duration))
    # acquiring with HRM takes a longer time than the probe duration
    t += probe_duration
    t += 2e-6
    dt808_aom_switch.enable(t)
    dt785_aom_switch.enable(t)


    #dt852_aom_switch.enable(t)
    #utils.jump_from_previous_value(sacher_aom_power, t + 6e-6, 0.0)
    utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    t+=2e-6
    # utils.jump_from_previous_value(control_aom_power, t, 0.0)
    #[start_time + probe_duration + 4e-6 + extra_SPCM_time])
    #spcm_counter.acquire(t + 5e-6, 2e-6)
    spcm_counter.acquire(t, 2e-6)
    #spcm_counter.trigger(t, 100e-6)
        
    #sacher_aom_switch.disable(t + 4e-6)
    sacher_aom_switch.disable(t)
    control_aom_switch.disable(t)
    t += 100e-6

    utils.jump_from_previous_value(control_aom_power, t, 0.0)
    utils.jump_from_previous_value(z_coil, t, 0)
    t += 5e-6

    #t += image_cmot(t, control=False, duration=60e-3)
    #t += 100e-6

    #t += image_dt(t, duration=60e-3)


    #t += image_cmot(t, control=False, repump = False, control_duration =10e-6, control_power = 2.0, duration=60e-3)

    t += reset_mot(t)
    #t += 5e-6

    stop(t)