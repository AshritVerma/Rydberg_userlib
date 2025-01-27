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

    #### DEFINE PROBE DURATION:
    probe_duration = 50e-6 #150e-6
    ##################################

    number_kinetics = 3
    camera_attributes_kinetic= {
            'acquisition': 'kinetic_series',
            'trigger': 'external',
            'preamp': True,
            'preamp_gain': 4.0,
            'xbin': 1,
            'ybin': 1,
            'height': 150, #150, #150,
            'width': 150, #150, #150,
            'left_start': 320, #540,
            'bottom_start': 500, #400,
            'number_kinetics': number_kinetics,
            'vertical_shift_speed': 0, # 0 is fastest
            'horizontal_shift_speed': 2, # 0 is fastest but sensitivity is better at lower speed
            'exposure_time': probe_duration,
            'int_shutter_mode': 'auto',
            'shutter_t_open': 10, #10,
            'shutter_t_close': 10, #10,
        }


    andor.set_attribute_dict(camera_attributes_kinetic)
    pts_probe.program_single_freq(1145)#(1145)
    #smc_sg1.set_freq_amp(CONTROL_FREQ,19)

    slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    slm_set_zernike()

    t=0

    start()
    
    t+= load_mot(t, 0.1) # load_mot(t, 1)

    t += mloop_compress_mot(t, 40e-3)

    zero_B_fields(t, duration = 5e-3)
    t += hold_dt(t, duration=DT_WAIT_DURATION)

    #utils.aom_pulse("control", t, 50e-6, 2.0)

    ########
    #add_time_marker(t, "RAMP_UP_B_FIELD")
    utils.jump_from_previous_value(z_coil, t, 5.0)
    t+= 10e-3

    # Put atoms in F=2 before optical pumping
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

    # ### Open andor external shutter:
    # andor_shutter.enable(t)
    # t += ANDOR_EXTERNAL_SHUTTER_DELAY

    # ### Take a background image with andor (no light)
    # andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = probe_duration)
    # t += probe_duration

    # t += 500e-6 # add time between different shots

    ###### Take an actual image with atoms:
    dt808_aom_switch.disable(t)
    dt785_aom_switch.disable(t)
    utils.jump_from_previous_value(dt785_aom_power, t, 0.0)
    utils.jump_from_previous_value(dt852_aom_power, t, 0.0)
    utils.jump_from_previous_value(dt808_aom_power, t, 0.0)

    #utils.jump_from_previous_value(control_aom_power, t, 2.0)
    #control_aom_switch.enable(t)
    #agilent_awg2.trigger(t, duration=2e-6) # turn on MW field
    t+=2e-6

    utils.jump_from_previous_value(sacher_aom_power, t, 0.5) # 0.6
    sacher_aom_switch.enable(t) 
    andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = probe_duration)#50e-6)
    t += probe_duration#50e-6
    sacher_aom_switch.disable(t)
    # control_aom_switch.disable(t)
    # utils.jump_from_previous_value(control_aom_power, t, 0.0)
    t += 20e-6
    utils.jump_from_previous_value(z_coil, t, 0)
    t += 200e-3 # add time between different kinetic shots

    #####################################################################################

    ### Take no atoms image
    sacher_aom_switch.enable(t) 
    andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = probe_duration)#50e-6)
    t += probe_duration#50e-6
    sacher_aom_switch.disable(t)
    utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    
    t += 200e-3
    #######################################################################################

    ### Take background image:
    andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = probe_duration)#50e-6)
    t += probe_duration#50e-6
    #######################################################################################

    t += reset_mot(t)
    #t += 5e-6

    stop(t)