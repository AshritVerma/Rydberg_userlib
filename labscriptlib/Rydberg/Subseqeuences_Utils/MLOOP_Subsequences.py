"""A library of parts of sequences that are common to many sequences.

This module is intended to be used to store functions that generate parts of
sequences. In particular, this module is intended to store common subsequences
that will be used in many sequences, such as those for loading the MOT or doing
absorption imaging. More unique/specific subsequences should be stored
elsewhere, possibly in the same file as the sequence that uses it. Additionally,
helper functions and the like that control outputs but that don't quite qualify
as making subsequences are stored in sequence_utils.py. For example, the
function open_shuttered_beam() which turns off a beam's AOM, opens its shutter,
then turns on the AOM at the desired time is stored in sequence_utils.py. On the
other hand, the function load_mot() has all of the code that sets all of the
outputs to load the MOT, so it is stored here. Note that some functions from
sequence_utils.py are imported directly into the namespace of this module with
the "from bar import foo" style syntax (e.g.open_shuttered_beam()), which means
that they are actually accessible by importing this module just as if they were
defined in this module.
"""
# parts lifted from Zak's code

from tracemalloc import start
import warnings

import numpy as np

import labscript as lab
import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils

def mloop_compress_mot(start_time, duration, marker_name="MLOOP_CMOT"):
    """Here we load the MOT using parameters set in the globals file

    Args:
        start_time (float): the time at which the mot loading begins
        duration (float): length of the mot loading time in seconds
        enable_mot (bool, optional): whether or not to open the shutters (currently we have no shutters). Defaults to True.
        reset (bool, optional): We use this parameter to reset the MOT parameters as preparation for the start of the next sequence. When true, this functions acts to reset the MOT at the end of the sequence. Defaults to False.
        marker_name (str, optional): Name of the marker to put in runviewer. Defaults to "MOT".

    Returns:
        float: the length of the load_mot duration in seconds
    """
    lab.add_time_marker(start_time, marker_name)
    # optimize with MLOOP the coils and detuning frequencies
    num_points = MLOOP_NUM_POINTS
    cur_time = start_time
    for i in range(num_points):
        interval_time = eval("MLOOP_TIME_INTERVAL{:02d}".format(i))
        utils.ramp_from_previous_value(x_coil, cur_time, duration=interval_time,
            final_value=eval("MLOOP_CMOT_X_COIL{:02d}".format(i)), samplerate=COIL_SAMPLE_RATE)
        utils.ramp_from_previous_value(z_coil, cur_time, duration=interval_time, 
            final_value=eval("MLOOP_CMOT_Z_COIL{:02d}".format(i)), samplerate=COIL_SAMPLE_RATE)
        utils.ramp_from_previous_value(y_coil, cur_time, duration=interval_time, 
            final_value=eval("MLOOP_CMOT_Y_COIL{:02d}".format(i)), samplerate=COIL_SAMPLE_RATE)
        motl_repump_ad9959.jump_frequency(cur_time, "MOT", eval("MLOOP_CMOT_MOTL_FREQ{:02d}".format(i)))
        motl_repump_ad9959.jump_frequency(cur_time, "Repump", eval("MLOOP_CMOT_REPUMP_FREQ{:02d}".format(i)))
        utils.ramp_from_previous_value(motl_aom_power, cur_time, interval_time, eval("MLOOP_CMOT_MOTL_POWER{:02d}".format(i)), samplerate=COIL_SAMPLE_RATE)
        utils.ramp_from_previous_value(repump_aom_power, cur_time, interval_time, eval("MLOOP_CMOT_REPUMP_POWER{:02d}".format(i)), samplerate=COIL_SAMPLE_RATE)
        cur_time = cur_time + interval_time

    utils.ramp_from_previous_value(gradient_coil, start_time, duration=cur_time-start_time, 
            final_value=eval("MLOOP_CMOT_GRADIENT_COIL".format(i)), samplerate=COIL_SAMPLE_RATE)

    motl_repump_ad9959.jump_frequency(cur_time, "MOT", MLOOP_CMOT_MOTL_END)
    motl_repump_ad9959.jump_frequency(cur_time, "Repump", MLOOP_CMOT_REPUMP_END)

    # we want the duration to be AT LEAST duration + 1 ms, otherwise things get wonky
    end_duration = max(duration, cur_time - start_time) + 1e-3

    repump_aom_switch.disable(start_time+end_duration)
    motl_aom_switch.disable(start_time+end_duration)

    return end_duration

def mloop_hold_dt(start_time, duration, marker_name="MLOOP_Hold_DT"):
    """Here we load the MOT using parameters set in the globals file

    Args:
        start_time (float): the time at which the mot loading begins
        duration (float): length of the mot loading time in seconds
        enable_mot (bool, optional): whether or not to open the shutters (currently we have no shutters). Defaults to True.
        reset (bool, optional): We use this parameter to reset the MOT parameters as preparation for the start of the next sequence. When true, this functions acts to reset the MOT at the end of the sequence. Defaults to False.
        marker_name (str, optional): Name of the marker to put in runviewer. Defaults to "MOT".

    Returns:
        float: the length of the load_mot duration in seconds
    """
    lab.add_time_marker(start_time, marker_name)

    
    repump_aom_switch.disable(start_time)
    motl_aom_switch.disable(start_time)
    utils.jump_from_previous_value(motl_aom_power, start_time, 0)
    utils.jump_from_previous_value(repump_aom_power, start_time, 0)

    # turn on repump at the end of this long sequence to bring atoms back from F=1 state:
    utils.jump_from_previous_value(repump_aom_power, start_time + duration - 200e-6 , 2)
    repump_aom_switch.enable(start_time + duration - 200e-6)
    repump_aom_switch.disable(start_time + duration - 100e-6)
    utils.jump_from_previous_value(repump_aom_power, start_time + duration - 100e-6, 0)


    return duration

def mloop_reshape_dt(start_time, duration=DT_WAIT_DURATION, marker_name="MLOOP_Reshape_DT"):
    """Here we load the MOT using parameters set in the globals file

    Args:
        start_time (float): the time at which the mot loading begins
        duration (float): length of the mot loading time in seconds
        enable_mot (bool, optional): whether or not to open the shutters (currently we have no shutters). Defaults to True.
        reset (bool, optional): We use this parameter to reset the MOT parameters as preparation for the start of the next sequence. When true, this functions acts to reset the MOT at the end of the sequence. Defaults to False.
        marker_name (str, optional): Name of the marker to put in runviewer. Defaults to "MOT".

    Returns:
        float: the length of the load_mot duration in seconds
    """
    lab.add_time_marker(start_time, marker_name)

    repump_aom_switch.disable(start_time)
    motl_aom_switch.disable(start_time)
    utils.jump_from_previous_value(motl_aom_power, start_time, 0)
    utils.jump_from_previous_value(repump_aom_power, start_time, 0)
    utils.jump_from_previous_value(dt785_aom_power, start_time, 0)


    # num_time_params = 1
    # cur_time = start_time + HOLD_TIME
    # test_785 = [RESHAPE_SIDE_LEVEL]
    # test_808 = [RESHAPE_TOP_LEVEL]
    # ramp_time = RAMP_TIME
    # dt785_aom_switch.enable(cur_time)
    # for n in range(num_time_params):
    #     utils.ramp_from_previous_value(dt785_aom_power, cur_time, ramp_time, test_785[n], samplerate=COIL_SAMPLE_RATE)
    #     utils.ramp_from_previous_value(dt808_aom_power, cur_time, ramp_time,  test_808[n], samplerate=COIL_SAMPLE_RATE)
    #     cur_time += ramp_time

    cur_time = start_time
    dt785_aom_switch.enable(cur_time)
    for n in range(NUM_RESHAPE_PARAMS):
        utils.ramp_from_previous_value(dt785_aom_power, cur_time, 
                                        eval("MLOOP_RESHAPE_TIME{:02d}".format(n)), 
                                        eval("MLOOP_RESHAPE_DT785_POWER{:02d}".format(n)), 
                                        samplerate=COIL_SAMPLE_RATE)
        utils.ramp_from_previous_value(dt808_aom_power, cur_time, 
                                         eval("MLOOP_RESHAPE_TIME{:02d}".format(n)), 
                                         eval("MLOOP_RESHAPE_DT808_POWER{:02d}".format(n)),  
                                         samplerate=COIL_SAMPLE_RATE)
        cur_time += eval("MLOOP_RESHAPE_TIME{:02d}".format(n))

    # # turn on repump at the end of this long sequence to bring atoms back from F=1 state:
    utils.jump_from_previous_value(repump_aom_power, start_time + duration - 200e-6 , 2)
    repump_aom_switch.enable(start_time + duration - 200e-6)
    repump_aom_switch.disable(start_time + duration - 100e-6)
    utils.jump_from_previous_value(repump_aom_power, start_time + duration - 100e-6, 0)

    return max(duration, cur_time-start_time) + 1e-3
