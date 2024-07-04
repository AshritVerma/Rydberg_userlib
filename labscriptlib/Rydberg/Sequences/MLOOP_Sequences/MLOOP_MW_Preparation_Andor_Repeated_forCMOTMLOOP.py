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
import numpy as np
from scipy import signal
from labscript import (
    start,
    stop,
)
import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt, reshape_dt_3traps,reshape_dt_3traps_try2,setup_slm
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    #### DEFINE PROBE, CONTROL DURATION:
    probe_duration = 10e-6 #15e-6#10e-6#5e-6#30e-6#300e-6 #30e-6 #100e-6#300e-6#300e-6 #50e-6 #150e-6
    control_duration = probe_duration #10e-6
    preparation_duration = 3.5e-6#MW_PREP_DURATION #1.5e-6#5e-6
    time_btw_prep_detect = 3e-6
    N_repeat = PREP_SEQ_REPEAT
    repeat_dead_time = 5e-6
    GATE_TIME = 180e-3
    ##################################

    #### SETUP CAMERA PROPERTIES:
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
            'exposure_time':  (probe_duration+ time_btw_prep_detect + preparation_duration + repeat_dead_time )*N_repeat+1e-3,#probe_duration,
            'int_shutter_mode': 'auto', #'perm_closed', #
            'shutter_t_open': 10, #10,
            'shutter_t_close': 10, #10,
        }
    andor.set_attribute_dict(camera_attributes_kinetic)
    ##################################

    ### SETUP LASER FREQUENCY OF PREPARATION, SACHER AND CONTROL:
    pts_probe.program_single_freq(PROBE_FREQ)#(1145)
    ##################################

    # Chis's mirrors:
    # mirror_controller.set_position("spcm_close", 10295, 35488) # example

    ### SETUP SLM:
    # if TRAP_NUM == 1:
    #     slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS)
    # if TRAP_NUM == 2:
    #     slm.two_traps(target_sep=TRAP_SEPARATION, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS, alpha=TRAP_ALPHA)
    # if TRAP_NUM == 3:
    #     slm.array_traps(phase_pattern_file=ARR_FILE, phase_pattern_folder=ARR_FOLDER, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS, alpha=TRAP_ALPHA)
    # slm_set_zernike()
    # slm.clip_circle(clip_circle_bool=CLIP_SLM_BOOL, px_ring=CLIP_RING_PIXELS)
    setup_slm()
    ##################################

    t=0

    start()

    ## USE TOP OR SIDE CONTOL

    #####################################################################################
    ### MOT LOADING AND DT TRAPPING STAGE
    t+= load_mot(t, 0.1) # load_mot(t, 1)
    t += mloop_compress_mot(t, 40e-3)
    mot_shutter.disable(t) # close MOT shutter
    zero_B_fields(t, duration = 5e-3)
    t += hold_dt(t, duration=DT_WAIT_DURATION)
    #####################################################################################

    #####################################################################################
    ### B FIELD RAMPING AND OPTICAL PUMPING STAGE
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
    utils.jump_from_previous_value(op_aom_power, t, 0.5)#0.6)
    op_aom_switch.enable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0.5)#2)
    repump_aom_switch.enable(t)
    t+= 2e-3 #2e-3 #200e-6#4.4e-3
    utils.jump_from_previous_value(op_aom_power, t, 0)
    op_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)


    ## Add preparation light from the side and try to measure the loss and check if this matches what we expect
    # t+=1e-3
    # utils.jump_from_previous_value(probe_aom_power, t, 2.0)#1.2)# 0.4)#1)#1.2)#0.6)#0.4) # 0.07 #0.6
    # probe_aom_switch.enable(t)
    # t+=PREP_TIME_RATE_MEASUREMENT #300e-6 #2e-3
    # utils.jump_from_previous_value(probe_aom_power, t, 0.0)#1.2)# 0.4)#1)#1.2)#0.6)#0.4) # 0.07 #0.6
    # probe_aom_switch.disable(t)

    repump_shutter.disable(t) # close repump shutter

    t += 20e-3 #1e-3
    #####################################################################################

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

    #####################################################################################
    ### PREPARATION STAGE
    andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = ((probe_duration+ time_btw_prep_detect + preparation_duration + repeat_dead_time )*N_repeat+1e-3))#50e-6)
    #andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = (probe_duration + repeat_dead_time )*N_repeat)#50e-6)

    for i in np.arange(N_repeat):

        ### IMAGING STAGE
        # ###### TURN OFF TRAPS BEFORE IMAGING
        # dt808_aom_switch.disable(t)
        # dt785_aom_switch.disable(t)
        # utils.jump_from_previous_value(dt785_aom_power, t, 0.0)
        # utils.jump_from_previous_value(dt852_aom_power, t, 0.0)
        # utils.jump_from_previous_value(dt808_aom_power, t, 0.0)
        # t += DT_TRAP_OFF_TIME_ANDOR

        utils.jump_from_previous_value(sacher_aom_power, t, PROBE_RATE)#0.45)#0.45)#0.7)#0.6)#0.4)#0.5)#0.6)#0.8)# 0.6)#0.2)#1.2)# 0.4)#1)#1.2)#0.6)#0.4) # 0.07 #0.6
        sacher_aom_switch.enable(t + 1.5e-6)
        t += probe_duration#50e-6
        sacher_aom_switch.disable(t+ 1.5e-6)
        t += repeat_dead_time
    
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

    #####################################################################################
    ### TAKE NO ATOMS IMAGE
    andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = ((probe_duration+ time_btw_prep_detect + preparation_duration + repeat_dead_time )*N_repeat+1e-3))# trigger_duration = ((probe_duration + repeat_dead_time )*N_repeat+1e-3))#50e-6)
    for i in np.arange(N_repeat):
        sacher_aom_switch.enable(t+1.5e-6) 
        #t += 5e-6
        t += probe_duration#50e-6
        sacher_aom_switch.disable(t+1.5e-6)
        t += repeat_dead_time

    utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    sacher_aom_switch.disable(t)
    # utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    t += GATE_TIME
    #######################################################################################

    #####################################################################################
    ### TAKE BACKGROUND IMAGE:
    andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = ((probe_duration+ time_btw_prep_detect + preparation_duration + repeat_dead_time )*N_repeat+1e-3))# trigger_duration = ((probe_duration + repeat_dead_time )*N_repeat+1e-3))#50e-6)
    for i in np.arange(N_repeat):
        t += probe_duration#50e-6
        t += repeat_dead_time
    # andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = probe_duration)#50e-6)
    # t += probe_duration#50e-6
    #######################################################################################

    t += reset_mot(t)
    #t += 5e-6

    stop(t)