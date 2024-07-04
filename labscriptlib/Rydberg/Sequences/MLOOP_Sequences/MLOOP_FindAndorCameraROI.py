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
import numpy as np

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    # smc_sg1.set_freq_amp(CONTROL_FREQ,19) # freq in Hz, pow in dBm
    exposure_andor = 50e-6#50e-6 #50e-6#0.05e-3 #ANDOR_EXPOSURE_TIME #20e-3
    camera_attributes_single= {
            'acquisition': 'single',
            'trigger': 'external',
            'preamp': True,
            'preamp_gain': 4.0,
            'xbin': 1,
            'ybin': 1,
            'height': 130, #100, #150, #150,
            'width': 200, #100, #150, #150,
            'left_start': 410, #350, #540,
            'bottom_start': 550, #530, #400,
            'vertical_shift_speed': 3,
            'horizontal_shift_speed': 2, # 0 is fastest but sensitivity is better at lower speed
            'int_shutter_mode': 'auto',
            'shutter_t_open': 10, #10,
            'shutter_t_close': 10, #10,
            'exposure_time': exposure_andor,
        }


        
    camera_attributes_single_fullimage= {
            'acquisition': 'single',
            'trigger': 'external',
            'preamp': True,
            'preamp_gain': 4.0,
            'xbin': 1,
            'ybin': 1,
            'height': 1024, #150,
            'width': 1024, #150,
            'left_start': 1,
            'bottom_start': 1,
            'vertical_shift_speed': 1,
            'horizontal_shift_speed': 2, # 0 is fastest but sensitivity is better at lower speed
            'int_shutter_mode': 'perm_open',#
            'exposure_time': exposure_andor,
            
        }

    number_kinetics = 2
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
            'exposure_time': exposure_andor,
            'int_shutter_mode': 'auto',
            'shutter_t_open': 10, #10,
            'shutter_t_close': 10, #10,
        }

    number_kinetics_fast = 3
    exposed_rows = 150 #150
    camera_attributes_fastkinetics_debug= {
            'acquisition': 'fast_kinetics',
            'trigger': 'external',
            'preamp': True,
            'preamp_gain': 4.0, #4.0,
            'xbin': 1,
            'ybin': 1,
            'width': 1024,
            'left_start': 1, #600,
            'number_kinetics': number_kinetics_fast,
            'int_shutter_mode': 'perm_open',
            'v_offset': 400, #400,#900,
            'exposed_rows': exposed_rows,
            'height': int(number_kinetics_fast*exposed_rows),
            'vertical_shift_speed': 0,
            'horizontal_shift_speed': 2,# 0 is fastest but sensitivity is better at lower speed
            'exposure_time': 50e-6,

        }
    andor.set_attribute_dict(camera_attributes_single)
    # andor.set_attribute_dict(camera_attributes_kinetic)
    # andor.set_attribute_dict(camera_attributes_fastkinetics_debug)
    t=0
    
    start()
    # andor_shutter.enable(t)
    t+= load_mot(t, 1)
    t += mloop_compress_mot(t, 40e-3)
    zero_B_fields(t, duration = 5e-3)
    t += hold_dt(t, duration=DT_WAIT_DURATION)

    # ## Single scan example
    andor_shutter.enable(t)
    # t += 0.1
    t += ANDOR_EXTERNAL_SHUTTER_DELAY
    utils.jump_from_previous_value(sacher_aom_power, t, 0.1) # 0.6
    sacher_aom_switch.enable(t) 
    # andor_shutter.enable(t- ANDOR_EXTERNAL_SHUTTER_DELAY-5e-3)
    # andor_shutter.disable(t- ANDOR_EXTERNAL_SHUTTER_DELAY + ANDOR_EXTERNAL_SHUTTER_DURATION)
    andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = exposure_andor)#50e-6)
    t += exposure_andor#50e-6
    sacher_aom_switch.disable(t)
    t+= 10e-6 #0.04 #0.04 #0.06
    sacher_aom_power.constant(t, 0)
    andor_shutter.disable(t)
    # ###################################
    

# Kinetics example
    # t += 10e-6
    # utils.jump_from_previous_value(sacher_aom_power, t, 0.5) # 0.6
    # for i in np.arange(number_kinetics):
    #     sacher_aom_switch.enable(t)
    #     # andor_shutter.enable(t- ANDOR_EXTERNAL_SHUTTER_DELAY-5e-3)
    #     # andor_shutter.disable(t- ANDOR_EXTERNAL_SHUTTER_DELAY + ANDOR_EXTERNAL_SHUTTER_DURATION)
    #     andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = exposure_andor)#50e-6)
    #     t += exposure_andor#50e-6
    #     sacher_aom_switch.disable(t)

    #     t+= 0.3#0.06#0.06 #0.04 #0.06
    # sacher_aom_power.constant(t, 0)
    # t+=200e-3
    ##################################

    # ## Fast Kinetics example
    # op_aom_power.constant(t, 0.4)
    # andor_shutter.enable(t- ANDOR_EXTERNAL_SHUTTER_DELAY )
    # for i in np.arange(number_kinetics_fast):
    #     op_aom_switch.enable(t)
    #     andor.expose(t - CAM_DELAY, name="absorption", frametype='atoms', trigger_duration = exposure_andor)#50e-6)
    #     t += exposure_andor#50e-6
    #     op_aom_switch.disable(t)

    #     t+= 0.001 #0.04 #0.06
    # andor_shutter.disable(t- ANDOR_EXTERNAL_SHUTTER_DELAY + ANDOR_EXTERNAL_SHUTTER_DURATION + 0.001*number_kinetics )
    # op_aom_power.constant(t, 0)

    # t += 1
    t += reset_mot(t)


    stop(t)