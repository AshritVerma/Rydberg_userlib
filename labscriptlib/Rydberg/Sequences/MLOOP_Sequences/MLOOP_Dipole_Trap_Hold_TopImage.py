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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt, setup_slm, image_cmot_hamamatsu
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()
    ## Setup Hamamatsu camera
    hamamatsu.camera_attributes['exposure'] = HC_EXPOSURE_TIME_CMOT
    hamamatsu.camera_attributes['subarrayHsize'] = HC_HSIZE_CMOT
    hamamatsu.camera_attributes['subarrayVsize'] = HC_VSIZE_CMOT
    hamamatsu.camera_attributes['subarrayHpos'] = HC_HPOS_CMOT
    hamamatsu.camera_attributes['subarrayVpos'] = HC_VPOS_CMOT
    hamamatsu.camera_attributes['subarrayMode'] = 2
    ## Setup frequency for Hamamatsu imaging
    pts_probe.program_single_freq(1140.0)#(PROBE_FREQ)
    ## Setup slm:
    setup_slm()
    
    t=0

    start()
    
    t+= load_mot(t, 1)#1)

    t += mloop_compress_mot(t, 40e-3)
    # t += compress_mot(t, 50e-3)



    repump_aom_switch.disable(t)
    motl_aom_switch.disable(t + 500e-6)
    utils.jump_from_previous_value(motl_aom_power, t, 0)
    utils.jump_from_previous_value(repump_aom_power, t + 500e-6, 0)

    #utils.jump_from_previous_value(motl_aom_power, t, 0)
    #utils.jump_from_previous_value(repump_aom_power, t, 0)

    zero_B_fields(t, duration = 5e-3)
    
    #t += mloop_hold_dt(t, duration=DT_WAIT_DURATION)


    # utils.jump_from_previous_value(z_coil, t, 5.0)
    t+= 10e-3

    #turn on mot to start from F=1:
    # utils.jump_from_previous_value(repump_aom_power, t, 0)
    # repump_aom_switch.disable(t)
    # utils.jump_from_previous_value(motl_aom_power, t , 2)
    # motl_aom_switch.enable(t)
    # motl_aom_switch.disable(t+ 100e-6)
    # utils.jump_from_previous_value(motl_aom_power,t+ 100e-6, 0)
    # t+=100e-6


    # ########
    # #add_time_marker(t, "RAMP_UP_B_FIELD")
    # utils.jump_from_previous_value(z_coil, t, 5.0)
    # t+= 10e-3

    #utils.jump_from_previous_value(z_coil, t, 5.0)
    #t+= 1e-3

    
    # # # Add optical pumping:
    # t+=100e-6
    # utils.jump_from_previous_value(op_aom_power, t, 1.0)
    # op_aom_switch.enable(t)
    # utils.jump_from_previous_value(repump_aom_power, t, 0.05)
    # repump_aom_switch.enable(t)
    # t+= 1.5e-3#OP_OPTIMIZATION_TIME #2e-3 #6e-3
    # utils.jump_from_previous_value(op_aom_power, t, 0)
    # op_aom_switch.disable(t)
    # utils.jump_from_previous_value(repump_aom_power, t, 0)
    # repump_aom_switch.disable(t)
    # #t+=200e-6
    # t+=100e-6 # add this time to allow for AOM to turn off

    t += hold_dt(t, duration=DT_WAIT_DURATION)

    # sidetrap_770_ad9959.jump_frequency(t, "AOD0", 91e6)
    # t += 5e-4
    # sidetrap_770_ad9959.jump_frequency(t, "AOD1", 88.5e6)
    # t += 5e-4
    # for i in range(2):
    #     sidetrap_770_ad9959.jump_frequency(t, "AOD0", 91e6 - i * 5e5)
    #     t += 10e-4
    #     sidetrap_770_ad9959.jump_frequency(t, "AOD1", 88.5e6 + i * 5e5)
    #     t += 10e-4

    # t += reshape_dt(t, duration=DT_WAIT_DURATION)


    ##temporary code
    # utils.jump_from_previous_value(control_aom_power, t, 2.0)
    # # control_aom_switch.enable(t)
    # t+=10e-3
    # utils.jump_from_previous_value(control_aom_power, t, 0.0)
    # control_aom_switch.disable(t)

    t += 2e-6
    # I temporarily put the repump back to an optimal value for imaging. We should put this in the imaging code instead
    motl_repump_ad9959.jump_frequency(t, "Repump", MOT_REPUMP_FREQ)
    
    ### DELETE ME
    # motl_repump_ad9959.jump_frequency(t, "Repump", REPUMP_TEST_RESONANCE_FREQ)
    # t += 1e-3
    # motl_repump_ad9959.jump_frequency(t, "MOT", MOT_TEST_RESONANCE_FREQ+266e6)
    # t += 1e-3

    # utils.jump_from_previous_value(motl_aom_power, t, 2)
    # motl_aom_switch.enable(t)
    # time_on = 100e-6
    # utils.jump_from_previous_value(motl_aom_power, t+time_on, 0)
    # motl_aom_switch.disable(t+time_on)
    # t+=time_on
    # t+= 1e-3

    # utils.jump_from_previous_value(repump_aom_power, t, 0.2)
    # repump_aom_switch.enable(t)
    # time_on = 10e-6
    # utils.jump_from_previous_value(repump_aom_power, t+time_on, 0)
    # repump_aom_switch.disable(t+time_on)
    # t+=time_on
    # t+= 1e-3
    ###


    # is_it_top_control.enable(t) # use if you want top control
    # t += image_cmot(t, control=False, traps_off = False, repump = True, control_duration =50e-6, control_power = 2.0, duration=60e-3)
    # t += image_dt(t, repump = True,duration=60e-3)
    t += image_cmot_hamamatsu(t, control=False, repump=True, control_duration =100e-6, control_power = 2.0, duration=60e-3)


    t += reset_mot(t)

    stop(t)