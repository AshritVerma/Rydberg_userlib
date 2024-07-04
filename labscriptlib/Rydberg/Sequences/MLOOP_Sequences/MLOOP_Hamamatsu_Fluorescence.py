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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, zero_E_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt, reshape_dt_3traps,reshape_dt_3traps_try2, setup_slm
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    #### DEFINE PROBE, CONTROL DURATION:
    probe_duration = FLUORESCENCE_DURATION #2e-3 #100e-6 #5e-6 #15e-6#10e-6#5e-6#30e-6#300e-6 #30e-6 #100e-6#300e-6#300e-6 #50e-6 #150e-6
    control_duration = probe_duration #10e-6
    preparation_duration = MW_PREP_DURATION # #1.5e-6#5e-6
    time_btw_prep_detect = 3e-6
    N_repeat = 1 #PREP_SEQ_REPEAT
    repeat_dead_time = 5e-6
    GATE_TIME = 10e-3
    ##################################

    #### SETUP CAMERA PROPERTIES:

    hamamatsu.camera_attributes['exposure'] = (probe_duration+ time_btw_prep_detect + preparation_duration + repeat_dead_time )*N_repeat+1e-3
    hamamatsu.camera_attributes['subarrayMode'] = 2
    hamamatsu.camera_attributes['subarrayHsize'] = HC_HSIZE
    hamamatsu.camera_attributes['subarrayVsize'] = HC_VSIZE
    hamamatsu.camera_attributes['subarrayHpos'] = HC_HPOS
    hamamatsu.camera_attributes['subarrayVpos'] = HC_VPOS
    # hamamatsu.camera_attributes['readoutMode'] = 1
    ##################################

    ### SETUP LASER FREQUENCY OF PREPARATION, SACHER AND CONTROL:
    pts_probe.program_single_freq(PROBE_FREQ)#(1145)
    smc_sg1.set_freq_amp(CONTROL_FREQ,19)
    agilent_sg1.set_freq_amp(PREPARATION_FREQ*10**6/16,10) # assuming preparation frequency is in MHz
    agilentE8257D.set_freq_amp(MW_PREP_FREQ, -2.0)#4.0)#-2.0)# MW_RF_POW)#-2) # set MW freq in GHz, pow in dBm
    ##################################

    # # Parametric heating:
    # agilent_awg1.program_gated_sine(PARAMETRIC_HEATING_FREQ, PARAMETRIC_HEATING_AMPL, PARAMETRIC_HEATING_OFFSET)

    # Chis's mirrors:
    # mirror_controller.set_position("spcm_close", 10295, 35488) # example

    ### SETUP SLM:
    # if TRAP_NUM == 1:
    #     slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    # if TRAP_NUM == 2:
    #     slm.two_traps(target_sep=TRAP_SEPARATION, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, alpha=TRAP_ALPHA)
    # if TRAP_NUM == 3:
    #     slm.array_traps(phase_pattern_file=ARR_FILE, phase_pattern_folder=ARR_FOLDER, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS, alpha=TRAP_ALPHA)
    # slm.clip_circle(clip_circle_bool=CLIP_SLM_BOOL, px_ring=CLIP_RING_PIXELS)
    # slm_set_zernike()
    setup_slm()
    ##################################

   
    ##################################


    t=0

    start()

    # # Parametric heating 
    # agilent_awg1.trigger(t, duration=0.3264)#5e-3+DT_WAIT_DURATION+50e-3+23e-3+1)

    ## USE TOP OR SIDE CONTOL
    # is_it_top_control.enable(t) # use if you want top control
    is_it_top_control.disable(t) # use if you want side control
    
    #####################################################################################
    ### MOT LOADING AND DT TRAPPING STAGE
    t+= load_mot(t, 0.1) # load_mot(t, 1)
    t += mloop_compress_mot(t, 40e-3)
    mot_shutter.disable(t) # close MOT shutter
    zero_B_fields(t, duration = 5e-3)

    # values optimized 12/14/2022
    zero_E_fields(t, Vx = VX_VOLTAGE, Vy = VY_VOLTAGE, Vz = VZ_VOLTAGE, duration = 5e-3)
    # zero_E_fields(t, Vx = 0.23, Vy = 0.41, Vz = -0.24, duration = 5e-3)
    # zero_E_fields(t, Vx = 0.0, Vy = 0.0, Vz = 0.0, duration = 5e-3)

    # t += hold_dt(t, duration=DT_WAIT_DURATION)
    t += reshape_dt(t, duration=DT_WAIT_DURATION)
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
    utils.jump_from_previous_value(op_aom_power, t, OP_OPTIMIZATION_POWER )#2.0 )#0.5)#0.8)#0.6)
    op_aom_switch.enable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0.5)#2)
    repump_aom_switch.enable(t)
    t+= OP_OPTIMIZATION_TIME
    utils.jump_from_previous_value(op_aom_power, t, 0)
    op_aom_switch.disable(t)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    repump_aom_switch.disable(t)


    # ## Add preparation light from the side and try to measure the loss and check if this matches what we expect
    # t+=1e-3
    # utils.jump_from_previous_value(probe_aom_power, t, 2.0)#1.2)# 0.4)#1)#1.2)#0.6)#0.4) # 0.07 #0.6
    # probe_aom_switch.enable(t)
    # t+= PREP_TIME_RATE_MEASUREMENT #300e-6 #2e-3
    # utils.jump_from_previous_value(probe_aom_power, t, 0.0)#1.2)# 0.4)#1)#1.2)#0.6)#0.4) # 0.07 #0.6
    # probe_aom_switch.disable(t)

    repump_shutter.disable(t) # close repump shutter

    t += 30e-3 #20e-3 #1e-3
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

    ### ADD THIS TO TEST IF HAMAMATSU GETS SOME CRAP FROM MOT FLUORESCENCE EVEN THOUGH IT SHOULD NOT..
    hamamatsu.expose(t - HC_CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = ((probe_duration+ time_btw_prep_detect + preparation_duration + repeat_dead_time )*N_repeat+1e-3))#50e-6)
    t+=GATE_TIME

    #####################################################################################
    ### PREPARATION STAGE
    hamamatsu.expose(t - HC_CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = ((probe_duration+ time_btw_prep_detect + preparation_duration + repeat_dead_time )*N_repeat+1e-3))#50e-6)
    #andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = (probe_duration + repeat_dead_time )*N_repeat)#50e-6)

    for i in np.arange(N_repeat):
        # ##### agilent_awg2.trigger(t + 1.8e-6, duration=2e-6) # turn on MW field for preparation
        # if MW_TTL_ENABLE:
        #     agilent_awg2.trigger(t + 1.8e-6, duration=2e-6) # turn on MW field for preparation
        #     MW_TTL.enable(t + 1.8e-6)
        # utils.jump_from_previous_value(control_aom_power, t, CONTROL_PREP_VOLT) #0.4)# for side use:0.1)#0.05)#0.1)# 0.3)#0.2)# 2.0) #2.0)
        # control_aom_switch.enable(t)
        # agilent_awg3.trigger(t+ 1.0e-6,duration = 2e-6) # turn on preparation beam AWG
        # probe_aom_switch.enable(t-2e-6)
        # t += preparation_duration # DEFINE DURATION OF PREPARATION PULSE
        # MW_TTL.disable(t + 1.8e-6)
        # control_aom_switch.disable(t + 0.6e-6)
        # probe_aom_switch.disable(t+3e-6)
        # ##
        # t+=time_btw_prep_detect 


        ## IMAGING STAGE
        ###### TURN OFF TRAPS BEFORE IMAGING
        # dt808_aom_switch.disable(t)
        # dt785_aom_switch.disable(t)
        # dt770_aom_switch.disable(t)
        # utils.jump_from_previous_value(dt785_aom_power, t, 0.0)
        # utils.jump_from_previous_value(dt852_aom_power, t, 0.0)
        # utils.jump_from_previous_value(dt808_aom_power, t, 0.0)
        # utils.jump_from_previous_value(dt770_aom_power, t, 0.0)
        # t += DT_TRAP_OFF_TIME_ANDOR

        # utils.jump_from_previous_value(control_aom_power, t, 2.0)# for side use:0.2)#0.2)#0.3)# 2.0) #2.0)
        # control_aom_switch.enable(t) 
        control_aom_switch.disable(t+control_duration+3e-6)
        utils.jump_from_previous_value(control_aom_power, t+control_duration+3e-6, 0.0)
        # utils.jump_from_previous_value(sacher_aom_power, t, PROBE_RATE)#0.45)#0.45)#0.7)#0.6)#0.4)#0.5)#0.6)#0.8)# 0.6)#0.2)#1.2)# 0.4)#1)#1.2)#0.6)#0.4) # 0.07 #0.6
        utils.jump_from_previous_value(probe_aom_power, t, 2.0)
        probe_aom_switch.enable(t + 1.5e-6)
        t += probe_duration#50e-6
        probe_aom_switch.disable(t+ 1.5e-6)
        MW_TTL.disable(t+ 1.5e-6)
        t += repeat_dead_time
    
    #t += 20e-6
    utils.jump_from_previous_value(z_coil, t, 0)

    ######## Use this when DT is on in img
    # get rid of atoms before the no atoms image
    dt808_aom_switch.disable(t)
    dt770_aom_switch.disable(t)
    dt785_aom_switch.disable(t)
    utils.jump_from_previous_value(dt785_aom_power, t, 0.0)
    utils.jump_from_previous_value(dt852_aom_power, t, 0.0)
    utils.jump_from_previous_value(dt808_aom_power, t, 0.0)
    utils.jump_from_previous_value(dt770_aom_power, t, 0.0)
    t += DT_TRAP_OFF_TIME_ANDOR
    t += GATE_TIME # add time between different kinetic shots
    #####################################################################################

    #####################################################################################
    ### TAKE NO ATOMS IMAGE
    hamamatsu.expose(t - HC_CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = ((probe_duration+ time_btw_prep_detect + preparation_duration + repeat_dead_time )*N_repeat+1e-3))# trigger_duration = ((probe_duration + repeat_dead_time )*N_repeat+1e-3))#50e-6)
    for i in np.arange(N_repeat):
        # sacher_aom_switch.enable(t+1.5e-6) 
        #t += 5e-6
        t += probe_duration#50e-6
        # sacher_aom_switch.disable(t+1.5e-6)
        t += repeat_dead_time

    utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    sacher_aom_switch.disable(t)
    # utils.jump_from_previous_value(sacher_aom_power, t, 0.0)
    t += GATE_TIME
    #######################################################################################

    #####################################################################################
    ### TAKE BACKGROUND IMAGE:
    hamamatsu.expose(t - HC_CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = ((probe_duration+ time_btw_prep_detect + preparation_duration + repeat_dead_time )*N_repeat+1e-3))# trigger_duration = ((probe_duration + repeat_dead_time )*N_repeat+1e-3))#50e-6)
    for i in np.arange(N_repeat):
        t += probe_duration#50e-6
        t += repeat_dead_time
    # andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = probe_duration)#50e-6)
    # t += probe_duration#50e-6
    #######################################################################################

    t += reset_mot(t)
    #t += 5e-6

    stop(t)