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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt,squeeze_dt, slm_set_zernike, image_dt
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    
    if TRAP_NUM == 1:
        slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY)
    if TRAP_NUM == 2:
        slm.two_traps(target_sep=TRAP_SEPARATION, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, alpha=TRAP_ALPHA)
    if TRAP_NUM == 3:
        slm.array_traps(phase_pattern_file=ARR_FILE, phase_pattern_folder=ARR_FOLDER, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS, alpha=TRAP_ALPHA)
    slm_set_zernike()
    slm.clip_circle(clip_circle_bool=CLIP_SLM_BOOL, px_ring=CLIP_RING_PIXELS)
    
    t=0

    start()

    sidetrap_770_ad9959.jump_frequency(t, "AOD0", AOD_CENTER_FREQ + AOD_DIFFERENCE_FREQ_START/2)
    sidetrap_770_ad9959.jump_frequency(t, "AOD1", AOD_CENTER_FREQ - AOD_DIFFERENCE_FREQ_START/2)
    sidetrap_770_ad9959.amplitude_dict[sidetrap_770_ad9959.channel_mappings["AOD0"]] = AOD_CHANNEL0_AMP
    sidetrap_770_ad9959.amplitude_dict[sidetrap_770_ad9959.channel_mappings["AOD1"]] = AOD_CHANNEL1_AMP
    
    t+= load_mot(t, 1)#1)

    t += mloop_compress_mot(t, 40e-3)
    # t += compress_mot(t, 50e-3)



    repump_aom_switch.disable(t)
    motl_aom_switch.disable(t + 500e-6)
    utils.jump_from_previous_value(motl_aom_power, t, 0)
    utils.jump_from_previous_value(repump_aom_power, t + 500e-6, 0)


    zero_B_fields(t, duration = 5e-3)

    t+= 10e-3

    t += hold_dt(t, duration=DT_WAIT_DURATION)
    # t+= squeeze_dt(t, duration=50e-3,  freq_start = AOD_DIFFERENCE_FREQ_START, freq_end = AOD_DIFFERENCE_FREQ_END)


### Squeeze traps sequence BEGIN
    motl_repump_ad9959.jump_frequency(t, "MOT", DTWAITING_MOT_FREQ)
    motl_repump_ad9959.jump_frequency(t, "Repump", DTWAITING_REPUMP_FREQ)
    # repump_aom_switch.disable(start_time)
    # motl_aom_switch.disable(start_time)
    utils.jump_from_previous_value(motl_aom_power, t, 0)
    utils.jump_from_previous_value(repump_aom_power, t, 0)
    t += 20e-3

    # utils.ramp_from_previous_value(dt808_aom_power, t, 10e-3, SLM_IMG_TRAP_POWER, samplerate=COIL_SAMPLE_RATE)

    # utils.ramp_from_previous_value(dt785_aom_power, t, 10e-3, 0.22, samplerate=COIL_SAMPLE_RATE)
    # utils.ramp_from_previous_value(dt770_aom_power, t, 10e-3, 2.0, samplerate=COIL_SAMPLE_RATE)
    utils.jump_from_previous_value(dt770_aom_power, t, 2.0)
    dt770_aom_switch.enable(t)

    final_difference_freq = AOD_DIFFERENCE_FREQ_END#0.5e6
    n_steps = 40

    freq_step = (AOD_DIFFERENCE_FREQ_START - final_difference_freq)/(2*n_steps)

    # ramp time + wait time
    total_time = 30e-3
    step_time = 500e-6

    # track ramp time
    ramp_time = 0

    for i in range(n_steps):
        t += step_time/2
        ramp_time += step_time/2
        sidetrap_770_ad9959.jump_frequency(t, "AOD0", AOD_CENTER_FREQ + AOD_DIFFERENCE_FREQ_START/2 - (i+1) * freq_step)

        t += step_time/2
        ramp_time += step_time/2
        sidetrap_770_ad9959.jump_frequency(t, "AOD1", AOD_CENTER_FREQ - AOD_DIFFERENCE_FREQ_START/2 + (i+1) * freq_step)

        if i == n_steps-1:

            print('low freq: ' + str(AOD_CENTER_FREQ + AOD_DIFFERENCE_FREQ_START/2 - (i+1) * freq_step))
            print('high freq: ' + str(AOD_CENTER_FREQ - AOD_DIFFERENCE_FREQ_START/2 + (i+1) * freq_step))

    wait_time = total_time - ramp_time
    t += wait_time
    print('wait time: ' + str(wait_time))

    # for i in range(10):
    #     t += 5e-4
    #     sidetrap_770_ad9959.jump_frequency(t, "AOD0", AOD_CENTER_FREQ + AOD_DIFFERENCE_FREQ/2 - (i+1) * 10e4)
        
    #     t += 5e-4
    #     sidetrap_770_ad9959.jump_frequency(t, "AOD1", AOD_CENTER_FREQ - AOD_DIFFERENCE_FREQ/2 + (i+1) * 10e4)

    #     if i == 9:

    #         print('low freq: ' + str( AOD_CENTER_FREQ + AOD_DIFFERENCE_FREQ/2 - (i+1) * 10e4))
    #         print('high freq: ' + str(AOD_CENTER_FREQ - AOD_DIFFERENCE_FREQ/2 + (i+1) * 10e4))
    # t+=20e-3


    # turn on repump at the end of this long sequence to bring atoms back from F=1 state:
    repump_atoms_to_F2 =  True
    if repump_atoms_to_F2:
        utils.jump_from_previous_value(repump_aom_power, t , 2)
        repump_aom_switch.enable(t)
        repump_aom_switch.disable(t+ 100e-6)
        utils.jump_from_previous_value(repump_aom_power,t + 100e-6, 0)
    
    t +=100e-6
## Squeeze traps sequence END

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
    

    t += image_cmot(t, control=False, traps_off = False, repump = True, control_duration =50e-6, control_power = 2.0, duration=60e-3)
    # t += image_dt(t, repump = True,duration=60e-3)

    t += reset_mot(t)

    stop(t)