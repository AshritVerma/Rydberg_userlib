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
    probe_duration = 30e-6 #100e-6#100e-6#300e-6#300e-6 #50e-6 #150e-6
    GATE_TIME = 180e-3
    ##################################

    number_kinetics = 3
    camera_attributes_kinetic= {
            'acquisition': 'kinetic_series',
            'trigger': 'external',
            'preamp': True,
            'preamp_gain': 4.0,
            'xbin': 1,
            'ybin': 1,
            'height': 130, #100, #150, #150,
            'width': 200, #100, #150, #150,
            'left_start': 410, #350, #540,
            'bottom_start': 550, #530, #400,
            'number_kinetics': number_kinetics,
            'vertical_shift_speed': 3, # 0 is fastest
            'horizontal_shift_speed': 2, # 0 is fastest but sensitivity is better at lower speed
            'exposure_time': probe_duration,
            'int_shutter_mode':  'auto', #'perm_closed',
            'shutter_t_open': 10, #10,
            'shutter_t_close': 10, #10,
        }


    andor.set_attribute_dict(camera_attributes_kinetic)
    pts_probe.program_single_freq(PROBE_FREQ)#(1145)
    smc_sg1.set_freq_amp(CONTROL_FREQ,19)
    # agilentE8257D.set_freq_amp(MW_PREP_FREQ,16) # set MW freq in GHz, pow in dBm
    # agilent_sg1.set_freq_amp(PREPARATION_FREQ*10**6/16,10) # assuming preparation frequency is in MHz

    # agilent_awg1.program_gated_sine(PARAMETRIC_HEATING_FREQ, PARAMETRIC_HEATING_AMPL, PARAMETRIC_HEATING_OFFSET)

    # Chis's mirrors:
    # mirror_controller.set_position("spcm_close", 10295, 35488) # example

    if TRAP_NUM == 1:
        slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    if TRAP_NUM == 2:
        slm.two_traps(target_sep=TRAP_SEPARATION, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, alpha=TRAP_ALPHA)
    if TRAP_NUM == 3:
        slm.array_traps(phase_pattern_file=ARR_FILE, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS, alpha=TRAP_ALPHA)
    slm_set_zernike()


    t=0

    start()
    
    # agilent_awg1.trigger(t, duration=5e-3+50e-3+23e-3+0.5)
    # agilent_awg1.trigger(t, duration=25e-3+DT_WAIT_DURATION+45e-3+0.1)

    ## is it top control or side control:
    is_it_top_control.enable(t)

    t+= load_mot(t, 0.1) # load_mot(t, 1)

    t += mloop_compress_mot(t, 40e-3)

    mot_shutter.disable(t) # close MOT shutter

    zero_B_fields(t, duration = 5e-3)
    t += hold_dt(t, duration=DT_WAIT_DURATION)

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

    ## Add preparation light from the side and try to measure the loss and check if this matches what we expect
    # utils.jump_from_previous_value(probe_aom_power, t, 0.3)#1.2)# 0.4)#1)#1.2)#0.6)#0.4) # 0.07 #0.6
    # probe_aom_switch.enable(t)
    # t+=2e-3
    # utils.jump_from_previous_value(probe_aom_power, t, 0.0)#1.2)# 0.4)#1)#1.2)#0.6)#0.4) # 0.07 #0.6
    # probe_aom_switch.disable(t)
    
    # Add optical pumping:
    t+=100e-6
    utils.jump_from_previous_value(op_aom_power, t, 2.0)#0.6)
    op_aom_switch.enable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0.5)#2)
    repump_aom_switch.enable(t)
    t+= 2e-3 #2e-3 #200e-6#4.4e-3
    utils.jump_from_previous_value(op_aom_power, t, 0)
    op_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)

    repump_shutter.disable(t) # close repump shutter


    t += 10e-3 #1e-3

    # # ramp down the final trap power
    # ramp_duration = 10e-3
    # utils.ramp_from_previous_value(dt808_aom_power, t, duration=ramp_duration, final_value=SLM_FINAL_TRAP_POWER, samplerate=COIL_SAMPLE_RATE)
    # t += ramp_duration
    # t += 2e-6

    traps_off_img = False

    ###### Take an actual image with atoms:
    if traps_off_img:
        dt808_aom_switch.disable(t)
        dt785_aom_switch.disable(t)
        utils.jump_from_previous_value(dt785_aom_power, t, 0.0)
        utils.jump_from_previous_value(dt852_aom_power, t, 0.0)
        utils.jump_from_previous_value(dt808_aom_power, t, 0.0)
        #t += DT_TRAP_OFF_TIME_ANDOR ### for TOF

    else:
        #utils.jump_from_previous_value(dt808_aom_power, t, SLM_IMG_TRAP_POWER)
        utils.ramp_from_previous_value(dt808_aom_power, t, duration=20e-6, final_value=SLM_IMG_TRAP_POWER, samplerate=COIL_SAMPLE_RATE*20)
        t += 20e-6

    # with RC filter, takes 50us for AOM to respond for 0V, 200us from 4.7V to 4.3V

########## test atom loss:
    # test_duration = 35e-6 #probe_duration
    # utils.jump_from_previous_value(control_aom_power, t, 0.3)# 2.0) #2.0)
    # control_aom_switch.enable(t)
    # utils.jump_from_previous_value(sacher_aom_power, t, 1.2)#0.5)#1.2)# 0.4)#1)#1.2)#0.6)#0.4) # 0.07 #0.6
    # sacher_aom_switch.enable(t)
    # t+= test_duration #probe_duration
    # utils.jump_from_previous_value(sacher_aom_power, t, 0.0)# 0.4)#1)#1.2)#0.6)#0.4) # 0.07 #0.6
    # sacher_aom_switch.disable(t)
    # control_aom_switch.disable(t+test_duration)
    # utils.jump_from_previous_value(control_aom_power, t+test_duration, 0.0)

    # # utils.jump_from_previous_value(repump_aom_power, t, 2)
    # # repump_aom_switch.enable(t)
    # # t+= 300e-6
    # # repump_aom_switch.disable(t)
    # # utils.jump_from_previous_value(repump_aom_power, t, 0)
    # t+=10e-3
############



    control_duration = probe_duration #10e-6
    utils.jump_from_previous_value(control_aom_power, t, 0.3)# 2.0) #2.0)
    control_aom_switch.enable(t)
        
    control_aom_switch.disable(t+control_duration)
    utils.jump_from_previous_value(control_aom_power, t+control_duration, 0.0)

    #agilent_awg2.trigger(t, duration=2e-6) # turn on MW field

    # ###### TURN OFF TRAPS BEFORE IMAGING
    # dt808_aom_switch.disable(t)
    # dt785_aom_switch.disable(t)
    # utils.jump_from_previous_value(dt785_aom_power, t, 0.0)
    # utils.jump_from_previous_value(dt852_aom_power, t, 0.0)
    # utils.jump_from_previous_value(dt808_aom_power, t, 0.0)
    # t += DT_TRAP_OFF_TIME_ANDOR

    utils.jump_from_previous_value(sacher_aom_power, t, 1.2)#0.5)#1.2)# 0.4)#1)#1.2)#0.6)#0.4) # 0.07 #0.6
    sacher_aom_switch.enable(t)

    andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = probe_duration)#50e-6)

    t += probe_duration#50e-6

    sacher_aom_switch.disable(t)
    
    #t += 20e-6
    utils.jump_from_previous_value(z_coil, t, 0)

    ######## Use this when DT is on in img
    # get rid of atoms before the no atoms image
    dt808_aom_switch.disable(t)
    dt785_aom_switch.disable(t)
    utils.jump_from_previous_value(dt785_aom_power, t, 0.0)
    utils.jump_from_previous_value(dt852_aom_power, t, 0.0)
    utils.jump_from_previous_value(dt808_aom_power, t, 0.0)
    t += DT_TRAP_OFF_TIME_ANDOR
    t += GATE_TIME # add time between different kinetic shots

    #####################################################################################

    ### Take no atoms image

    sacher_aom_switch.enable(t) 
    #t += 5e-6
    andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = probe_duration)#50e-6)
    t += probe_duration#50e-6
    utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    sacher_aom_switch.disable(t)
    # utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    
    t += GATE_TIME
    #######################################################################################

    ### Take background image:
    andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = probe_duration)#50e-6)
    t += probe_duration#50e-6
    #######################################################################################

    mot_shutter.disable(t) # close MOT shutter
    repump_shutter.enable(t) # close MOT shutter

    t += reset_mot(t)
    #t += 5e-6

    stop(t)