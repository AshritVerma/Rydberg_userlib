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
import numpy as np

import labscript as lab
import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils

def zero_B_fields(start_time, RSC = False, duration=5e-3, marker_name="Zero B Fields"):
    """Zero all of the B fields (their MOT values)

    Args:
        start_time ([type]): [description]
        duration ([type], optional): [description]. Defaults to 5e-3.
        marker_name (str, optional): [description]. Defaults to "Zero B Fields".
    """
    lab.add_time_marker(start_time, "zero B fields")
    if not RSC:
        utils.jump_from_previous_value(x_coil, start_time, ZERO_X_COIL)
        utils.jump_from_previous_value(z_coil, start_time, ZERO_Z_COIL)
        utils.jump_from_previous_value(y_coil, start_time, ZERO_Y_COIL)
        utils.jump_from_previous_value(gradient_coil, start_time, 0)
        gradient_coil_switch.disable(start_time)

    if RSC:
        utils.jump_from_previous_value(x_coil, start_time, RSC_ZERO_X_COIL)
        utils.jump_from_previous_value(y_coil, start_time, RSC_ZERO_Y_COIL)
        utils.jump_from_previous_value(gradient_coil, start_time, 0)
        gradient_coil_switch.disable(start_time)

    return duration

def zero_E_fields(start_time, Vx=0.0,Vy=0.0,Vz=0.0, duration=5e-3, marker_name="Zero E Fields"):
    """Zero all of the E fields (their MOT values)

    Args:
        start_time ([type]): [description]
    """
    lab.add_time_marker(start_time, "zero E fields")
    V_V1 = Vx + Vy - Vz
    V_V2 = Vx - Vy - Vz
    V_V3 = - Vx + Vy -Vz
    V_V4 = - Vx - Vy - Vz
    V_V5 = Vx + Vy + Vz
    V_V6 = Vx - Vy + Vz
    V_V7 = -Vx + Vy + Vz
    V_V8 = -Vx - Vy + Vz

    utils.jump_from_previous_value(V1, start_time, V_V1)
    utils.jump_from_previous_value(V2, start_time, V_V2)
    utils.jump_from_previous_value(V3, start_time, V_V3)
    utils.jump_from_previous_value(V4, start_time, V_V4)
    utils.jump_from_previous_value(V5, start_time, V_V5)
    utils.jump_from_previous_value(V6, start_time, V_V6)
    utils.jump_from_previous_value(V7, start_time, V_V7)
    utils.jump_from_previous_value(V8, start_time, V_V8)

    return duration


def load_mot(start_time, duration, enable_mot=True, reset=False,
             marker_name="MOT"):
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
    # give the cards time to reset
    extra_time = 20e-3
    if not reset:
        start_time += extra_time
    lab.add_time_marker(start_time, marker_name)

    # for the first time we enter this function, we don't want to trigger
    # since our inital frequency is correct
    # we do, however, want to trigger on a reset
    motl_repump_ad9959.jump_frequency(start_time, "MOT", MOT_MOTL_FREQ, trigger=reset)
    motl_repump_ad9959.jump_frequency(start_time, "Repump", MOT_REPUMP_FREQ, trigger=reset)
    repump_shutter.enable(start_time) # repump shutter needs to be high to open the shutter
    mot_shutter.enable(start_time) # mot shutter needs to be high to open the shutter

    # set up coils
    utils.jump_from_previous_value(x_coil, start_time, MOT_X_COIL)
    utils.jump_from_previous_value(z_coil, start_time, MOT_Z_COIL)
    utils.jump_from_previous_value(y_coil, start_time, MOT_Y_COIL)
    utils.jump_from_previous_value(small_z_coil, start_time, 0.0)
    utils.jump_from_previous_value(gradient_coil, start_time, MOT_GRADIENT_COIL)

    if MOT_GRADIENT_SWITCH:
        gradient_coil_switch.enable(start_time)

    # set up laser AOMs
    utils.jump_from_previous_value(motl_aom_power, start_time, MOT_MOTL_POWER)
    utils.jump_from_previous_value(repump_aom_power, start_time, MOT_REPUMP_POWER)
    utils.jump_from_previous_value(dt808_aom_power, start_time, MOT_DT808_POWER)
    utils.jump_from_previous_value(dt785_aom_power, start_time, MOT_DT785_POWER)
    utils.jump_from_previous_value(dt852_aom_power, start_time, MOT_DT852_POWER) # when on commertial AOM we don't need the switch to turn it on
    utils.jump_from_previous_value(dt770_aom_power, start_time, MOT_DT770_POWER) 
    # utils.jump_from_previous_value(rsc_aom_power, start_time, 0)
    # rsc_aom_switch.disable(start_time)

    if MOT_MOTL_SWITCH:
        motl_aom_switch.enable(start_time)
    if MOT_REPUMP_SWITCH:
        repump_aom_switch.enable(start_time)
    if MOT_DT808_SWITCH:
        dt808_aom_switch.enable(start_time)
    if MOT_DT785_SWITCH:
        dt785_aom_switch.enable(start_time)
    if MOT_DT770_SWITCH:
        dt770_aom_switch.enable(start_time)

    # make sure other laser beams are off
    utils.jump_from_previous_value(op_aom_power, start_time, 0)
    op_aom_switch.disable(start_time)
    utils.jump_from_previous_value(sacher_aom_power, start_time, 0)
    sacher_aom_switch.disable(start_time)
    utils.jump_from_previous_value(imaging_aom_power, start_time, 0)
    imaging_aom_switch.disable(start_time)

    detection_shutter.enable(start_time + duration)

    #TODO: If enable=false turn off shutters (once we have shutters)

    return duration + extra_time

def reset_mot(start_time, reset_mot_duration=30e-3, marker_name="Reset MOT"):#reset_mot_duration=6e-3, marker_name="Reset MOT"):
    """Set the outputs to their MOT values to prepare for the next shot.

    This subsequence should be run at the end of a shot. It sets the outputs of all of the channels to their MOT
    values so that everything is ready for the next shot.

    If the global `enable_mot_between_shots` is `True` then this will turn on
    the MOT and start loading atoms. If it is `False` then all of the outputs
    will go to their MOT values

    Args:
        start_time (float): (seconds) Time in the sequence at which to start
            resetting the MOT outputs. Note that the MOT coil will actually be
            instructed to start turning on sooner than this though; see the
            notes above.
        reset_mot_duration (float): (seconds) the time between resetting the MOT and ending the sequence
        marker_name (str): (Default="Reset MOT") The name of the marker to use
            in runviewer for this subsequence.

    Returns:
        duration (float): (seconds) Time needed to reset the outputs to their
            MOT values.
    """

    # Call load_mot() with the appropriate arguments, which takes care of the
    # other outputs.
    duration = load_mot(
        start_time,
        reset_mot_duration,
        enable_mot=True,
        reset=True,
        marker_name=marker_name,
    )

    # Ensure that the last edge isn't cut off by the end of the sequence by
    # adding one more millisecond.
    utils.jump_from_previous_value(sacher_aom_power, start_time + duration, 2)
    sacher_aom_switch.enable(start_time + duration)
    detection_shutter.disable(start_time + duration-14e-3) # shutter delay is ~12-13ms
    duration = duration + 1e-3

    return duration

def compress_mot(start_time, duration, marker_name="CMOT"):
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

    # # set up coils
    utils.ramp_from_previous_value(x_coil, start_time, duration=10e-3, final_value=CMOT_X_COIL, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(z_coil, start_time, duration=30e-3, final_value=CMOT_Z_COIL, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(y_coil, start_time, duration=30e-3, final_value=CMOT_Y_COIL, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(gradient_coil, start_time, duration=10e-3, final_value=CMOT_GRADIENT_COIL, samplerate=COIL_SAMPLE_RATE)

    # set up laser AOMs
    utils.ramp_from_previous_value(motl_aom_power, start_time, 30e-3, CMOT_MOTL_POWER, samplerate=COIL_SAMPLE_RATE)
    utils.jump_from_previous_value(repump_aom_power, start_time+10e-3, CMOT_REPUMP_POWER)
    utils.jump_from_previous_value(dt808_aom_power, start_time, CMOT_DT808_POWER)
    utils.jump_from_previous_value(dt785_aom_power, start_time, CMOT_DT785_POWER)

    motl_repump_ad9959.jump_frequency(start_time, "MOT", CMOT_MOTL_FREQ)
    motl_repump_ad9959.jump_frequency(start_time, "Repump", CMOT_REPUMP_FREQ)

    motl_aom_switch.disable(start_time + duration - 500e-6)
    motl_aom_power.constant(start_time + duration - 500e-6, 0)


    # uncomment if you want capability to turn these off after the MOT stage
    # if CMOT_MOTL_SWITCH:
    #     motl_aom_switch.enable(start_time)
    # if CMOT_REPUMP_SWITCH:
    #     repump_aom_switch.enable(start_time)
    # if CMOT_DT808_SWITCH:
    #     dt808_aom_switch.enable(start_time)
    # if CMOT_DT785_SWITCH:
    #     dt785_aom_switch.enable(start_time)


    return duration

def hold_dt(start_time, duration, repump_atoms_to_F2 = True,  marker_name="Hold_DT"):
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

    # set MOT and repump frequency to off-resonant values and turn these lasers off
    motl_repump_ad9959.jump_frequency(start_time, "MOT", DTWAITING_MOT_FREQ)
    motl_repump_ad9959.jump_frequency(start_time, "Repump", DTWAITING_REPUMP_FREQ)
    # repump_aom_switch.disable(start_time)
    # motl_aom_switch.disable(start_time)
    utils.jump_from_previous_value(motl_aom_power, start_time, 0)
    utils.jump_from_previous_value(repump_aom_power, start_time, 0)

    # turn on repump at the end of this long sequence to bring atoms back from F=1 state:
    if repump_atoms_to_F2:
        utils.jump_from_previous_value(repump_aom_power, start_time + duration - 200e-6 , 2)
        repump_aom_switch.enable(start_time + duration - 200e-6)
        repump_aom_switch.disable(start_time + duration - 100e-6)
        utils.jump_from_previous_value(repump_aom_power, start_time + duration - 100e-6, 0)


    return duration


def squeeze_dt(start_time, duration, wait_after_cmot = 20e-3, repump_atoms_to_F2 = True, freq_start = AOD_DIFFERENCE_FREQ_START, freq_end = AOD_DIFFERENCE_FREQ_END,   marker_name="Hold_DT"):
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

    # set MOT and repump frequency to off-resonant values and turn these lasers off
    motl_repump_ad9959.jump_frequency(start_time, "MOT", DTWAITING_MOT_FREQ)
    motl_repump_ad9959.jump_frequency(start_time, "Repump", DTWAITING_REPUMP_FREQ)
    # repump_aom_switch.disable(start_time)
    # motl_aom_switch.disable(start_time)
    utils.jump_from_previous_value(motl_aom_power, start_time, 0)
    utils.jump_from_previous_value(repump_aom_power, start_time, 0)

    total_time_now = 0
    total_time_now += wait_after_cmot

    utils.ramp_from_previous_value(dt808_aom_power, start_time + total_time_now , 10e-3, 2.9, samplerate=COIL_SAMPLE_RATE)
    # utils.ramp_from_previous_value(dt785_aom_power, t, 10e-3, 0.22, samplerate=COIL_SAMPLE_RATE)
    # utils.ramp_from_previous_value(dt770_aom_power, t, 10e-3, 2.0, samplerate=COIL_SAMPLE_RATE)
    utils.jump_from_previous_value(dt770_aom_power, start_time + total_time_now, 2.0)
    dt770_aom_switch.enable(start_time + total_time_now)

    n_steps = 40

    freq_step = (freq_start - freq_end)/(2*n_steps)

    # ramp time + wait time
    # total_time = 30e-3
    step_time = 500e-6

    # track ramp time
    ramp_time = 0

    for i in range(n_steps):
        total_time_now += step_time/2
        sidetrap_770_ad9959.jump_frequency(start_time + total_time_now, "AOD0", AOD_CENTER_FREQ + freq_start/2 - (i+1) * freq_step)

        total_time_now += step_time/2
        sidetrap_770_ad9959.jump_frequency(start_time + total_time_now, "AOD1", AOD_CENTER_FREQ - freq_start/2 + (i+1) * freq_step)

    # turn on repump at the end of this long sequence to bring atoms back from F=1 state:
    if repump_atoms_to_F2:
        utils.jump_from_previous_value(repump_aom_power, start_time + duration - 200e-6 , 2)
        repump_aom_switch.enable(start_time + duration - 200e-6)
        repump_aom_switch.disable(start_time + duration - 100e-6)
        utils.jump_from_previous_value(repump_aom_power, start_time + duration - 100e-6, 0)


    return duration # this should be cmot_waiting time and ramping time so 50ms when we first tested this in August

def reshape_dt(start_time, duration, marker_name="Reshape_DT"):
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

    # set MOT and repump frequency to off-resonant values and turn these lasers off
    motl_repump_ad9959.jump_frequency(start_time, "MOT", DTWAITING_MOT_FREQ)
    motl_repump_ad9959.jump_frequency(start_time, "Repump", DTWAITING_REPUMP_FREQ)
    repump_aom_switch.disable(start_time)
    motl_aom_switch.disable(start_time)
    utils.jump_from_previous_value(motl_aom_power, start_time, 0)
    utils.jump_from_previous_value(repump_aom_power, start_time, 0)

    # hold in top trap for 20ms, then slowly turn down the power of top trap in next 20ms while increasing side DT power, hold crossed for the rest of the duration
    #utils.jump_from_previous_value(dt785_aom_power, start_time, 0)
    #dt852_aom_switch.enable(start_time + 20e-3)
    # utils.ramp_from_previous_value(dt852_aom_power, start_time+30e-3, 20e-3, RESHAPE_SIDE_LEVEL_852, samplerate=COIL_SAMPLE_RATE)
    # utils.ramp_from_previous_value(dt785_aom_power, start_time+30e-3, 20e-3, RESHAPE_SIDE_LEVEL_785, samplerate=COIL_SAMPLE_RATE)
    # utils.ramp_from_previous_value(dt808_aom_power, start_time+30e-3, 20e-3, RESHAPE_TOP_LEVEL, samplerate=COIL_SAMPLE_RATE)

    utils.ramp_from_previous_value(dt852_aom_power, start_time+RESHAPE_START_TIME, RESHAPE_RAMP_DURATION, RESHAPE_SIDE_LEVEL_852, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(dt785_aom_power, start_time+RESHAPE_START_TIME, RESHAPE_RAMP_DURATION, RESHAPE_SIDE_LEVEL_785, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(dt808_aom_power, start_time+RESHAPE_START_TIME, RESHAPE_RAMP_DURATION, RESHAPE_TOP_LEVEL, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(dt770_aom_power, start_time+RESHAPE_START_TIME, RESHAPE_RAMP_DURATION, RESHAPE_TOP_LEVEL_770, samplerate=COIL_SAMPLE_RATE)

    # turn on repump at the end of this long sequence to bring atoms back from F=1 state:
    utils.jump_from_previous_value(repump_aom_power, start_time + duration - 200e-6 , 2)
    repump_aom_switch.enable(start_time + duration - 200e-6)
    repump_aom_switch.disable(start_time + duration - 100e-6)
    utils.jump_from_previous_value(repump_aom_power, start_time + duration - 100e-6, 0)


    return duration
def reshape_dt_3traps(start_time, duration, marker_name="Reshape_DT"):
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

    # set MOT and repump frequency to off-resonant values and turn these lasers off
    motl_repump_ad9959.jump_frequency(start_time, "MOT", DTWAITING_MOT_FREQ)
    motl_repump_ad9959.jump_frequency(start_time, "Repump", DTWAITING_REPUMP_FREQ)
    repump_aom_switch.disable(start_time)
    motl_aom_switch.disable(start_time)
    utils.jump_from_previous_value(motl_aom_power, start_time, 0)
    utils.jump_from_previous_value(repump_aom_power, start_time, 0)

    # hold in top trap for 20ms, then slowly turn down the power of top trap in next 20ms while increasing side DT power, hold crossed for the rest of the duration
    #utils.jump_from_previous_value(dt785_aom_power, start_time, 0)
    dt785_aom_switch.enable(start_time + 50e-3)
    utils.ramp_from_previous_value(dt808_aom_power, start_time+50e-3, 20e-3, RESHAPE_TOP_LEVEL, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(dt785_aom_power, start_time+70e-3, 20e-3, RESHAPE_SIDE_LEVEL_785, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(dt852_aom_power, start_time+70e-3, 20e-3, RESHAPE_SIDE_LEVEL_852, samplerate=COIL_SAMPLE_RATE)


    # turn on repump at the end of this long sequence to bring atoms back from F=1 state:
    utils.jump_from_previous_value(repump_aom_power, start_time + duration - 200e-6 , 2)
    repump_aom_switch.enable(start_time + duration - 200e-6)
    repump_aom_switch.disable(start_time + duration - 100e-6)
    utils.jump_from_previous_value(repump_aom_power, start_time + duration - 100e-6, 0)


    return duration

def reshape_dt_3traps_try2(start_time, duration, marker_name="Reshape_DT"):
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

    motl_repump_ad9959.jump_frequency(start_time, "MOT", DTWAITING_MOT_FREQ)
    motl_repump_ad9959.jump_frequency(start_time, "Repump", DTWAITING_REPUMP_FREQ)
    repump_aom_switch.disable(start_time)
    motl_aom_switch.disable(start_time)
    utils.jump_from_previous_value(motl_aom_power, start_time, 0)
    utils.jump_from_previous_value(repump_aom_power, start_time, 0)

    # hold in top trap for 20ms, then slowly turn down the power of top trap in next 20ms while increasing side DT power, hold crossed for the rest of the duration
    #utils.jump_from_previous_value(dt785_aom_power, start_time, 0)
    dt808_aom_switch.enable(start_time)
    dt785_aom_switch.enable(start_time)
    CMOT_OFF_TIME = 10e-3
    TOP_RAMP = 10e-3 #80e-3
    SIDE_RAMP = 10e-3 #100e-3
    utils.ramp_from_previous_value(dt808_aom_power, start_time+ CMOT_OFF_TIME - SIDE_RAMP*0.5, TOP_RAMP, RESHAPE_TOP_LEVEL, samplerate=COIL_SAMPLE_RATE)
    #utils.ramp_from_previous_value(dt785_aom_power, t+CMOT_OFF_TIME + TOP_RAMP, SIDE_RAMP, RESHAPE_SIDE_LEVEL_785, samplerate=COIL_SAMPLE_RATE)
    #utils.ramp_from_previous_value(dt852_aom_power, start_time+CMOT_OFF_TIME , SIDE_RAMP, RESHAPE_SIDE_LEVEL_852, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(dt785_aom_power, start_time+CMOT_OFF_TIME , SIDE_RAMP, RESHAPE_SIDE_LEVEL_785, samplerate=COIL_SAMPLE_RATE)
    #utils.ramp_from_previous_value(dt808_aom_power, t+ CMOT_OFF_TIME + SIDE_RAMP*1.7, TOP_RAMP, RESHAPE_TOP_LEVEL, samplerate=COIL_SAMPLE_RATE)
    #utils.ramp_from_previous_value(dt852_aom_power, start_time+ CMOT_OFF_TIME + SIDE_RAMP*2.0, TOP_RAMP, RESHAPE_SIDE_LEVEL_852-0.02, samplerate=COIL_SAMPLE_RATE)
    #utils.ramp_from_previous_value(dt785_aom_power,start_time+ CMOT_OFF_TIME + SIDE_RAMP*2.0, TOP_RAMP, RESHAPE_SIDE_LEVEL_785-0.1, samplerate=COIL_SAMPLE_RATE)
    
    #utils.ramp_from_previous_value(dt852_aom_power, start_time+ CMOT_OFF_TIME + SIDE_RAMP*2.5+TOP_RAMP, 40e-3, RESHAPE_SIDE_LEVEL_852+0.1, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(dt785_aom_power,start_time+ CMOT_OFF_TIME + SIDE_RAMP*2.5+TOP_RAMP, 40e-3, RESHAPE_SIDE_LEVEL_785+0.0, samplerate=COIL_SAMPLE_RATE)
    utils.ramp_from_previous_value(dt808_aom_power, start_time+ CMOT_OFF_TIME + SIDE_RAMP*2.5+TOP_RAMP*1.3, 40e-3, RESHAPE_TOP_LEVEL+0.0, samplerate=COIL_SAMPLE_RATE)

    # turn on repump at the end of this long sequence to bring atoms back from F=1 state:
    utils.jump_from_previous_value(repump_aom_power, start_time + duration - 200e-6 , 2)
    repump_aom_switch.enable(start_time + duration - 200e-6)
    repump_aom_switch.disable(start_time + duration - 100e-6)
    utils.jump_from_previous_value(repump_aom_power, start_time + duration - 100e-6, 0)


    return duration


def probe_with_spcm(start_time, probe_duration, extra_SPCM_time = 1.1e-6, marker_name="Probe_with_SPCM"):
    """Here we probe one ensemble and detect it with SPCM 
       We first turn on SPCM enable trigger, then after 4us we turn on the probing light for 
       probe_duration time. Then we disable the SPCM and trigger NI counter card to send the counts it collected into
       the buffer so that we can read it.

        start_time (float): the time at which the probing with SPCM stage begins
        duration (float): length of the mot loading time in seconds        
        marker_name (str, optional): Name of the marker to put in runviewer. Defaults to "PROBE_WITH_SPCM".
    """
    lab.add_time_marker(start_time, marker_name)

    # set MOT and repump frequency to off-resonant values and turn these lasers off
    utils.jump_from_previous_value(sacher_aom_power, start_time, 0.5)
    sacher_aom_switch.enable(start_time + 4e-6)
    sacher_aom_switch.disable(start_time+ 4e-6 + probe_duration)
    utils.jump_from_previous_value(sacher_aom_power, start_time + probe_duration + 4e-6 + extra_SPCM_time, 0.0)
    spcm_counter.acquire(start_time, [start_time + probe_duration + 4e-6 + extra_SPCM_time])
    spcm_on_trigger.trigger(start_time, duration = (probe_duration + 4e-6 + extra_SPCM_time))


    return probe_duration + 4e-6 + extra_SPCM_time

def molasses(start_time, duration, marker_name="molasses"):
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

    # set MOT and repump frequency to off-resonant values and turn these lasers off
    motl_repump_ad9959.jump_frequency(start_time, "MOT", DTWAITING_MOT_FREQ)
    motl_repump_ad9959.jump_frequency(start_time, "Repump", DTWAITING_REPUMP_FREQ)
    repump_aom_switch.disable(start_time + duration - 0.1e-3)
    motl_aom_switch.disable(start_time + duration - 0.5e-3)
    utils.jump_from_previous_value(motl_aom_power, start_time, 1)
    utils.jump_from_previous_value(motl_aom_power, start_time + duration - 0.5e-3, 0)
    utils.jump_from_previous_value(repump_aom_power, start_time, 0.25)
    utils.jump_from_previous_value(dt808_aom_power, start_time, 2)
    utils.jump_from_previous_value(dt785_aom_power, start_time, 0)


    return duration

def optical_pumping(start_time, duration, marker_name="Optical_pumping"):
    """Sequence for optical pumping. Both repump and OP beam are turned on

    Args:
        start_time (float): time to start
        duration (float): length of the sequence in seconds
        marker_name (str, optional): [description]. Defaults to "Optical_Pumping".

    Returns:
        float: duration of the sequence
    """
    lab.add_time_marker(start_time, marker_name)
    utils.jump_from_previous_value(op_aom_power, start_time, 1)
    op_aom_switch.enable(start_time)
    utils.jump_from_previous_value(repump_aom_power, start_time, 2)
    repump_aom_switch.enable(start_time)


    return duration

def image_mot(start_time, duration, repump = True, marker_name='MOT_image'):
    """Here is the code to take a MOT image. Values are currently hardcoded,
    but when we get a better handle on labscript we should change them so that
    we read things in from a globals file and also optimize the ramping

    Args:
        start_time (float): the time the image begins
        duration (float): the time the imaging sequence ends. Added an extra 0.0005s to ensure values were reached in requisite amount of time
        marker_name (str, optional): The name of the image sequence in runviewer. Defaults to 'MOT_image'.

    Returns:
        float: duration of the sequence in seconds
    """

    lab.add_time_marker(start_time, marker_name)

    if IMAGE_MODE == "SIDE":
        utils.jump_from_previous_value(y_coil, start_time+100e-6, 7.0) #1.0)
        utils.jump_from_previous_value(y_coil, start_time+32e-3, MOT_Y_COIL) #0.3)
        utils.ramp_from_previous_value(z_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
        utils.ramp_from_previous_value(small_z_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
        utils.ramp_from_previous_value(x_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 

        utils.jump_from_previous_value(gradient_coil, start_time, 0)
        gradient_coil_switch.disable(start_time)

        #utils.ramp_from_previous_value(gradient_coil, start_time+0.01, 0.05, 1.68, samplerate=SAMPLE_RATE)
        #gradient_coil_switch.constant(start_time+10e-3, 5)

        motl_repump_ad9959.jump_frequency(start_time, "MOT", IMG_MOTL_FREQ)

        imaging_aom_power.constant(start_time, IMAGING_POWER_SIDE)
        basler.expose(start_time+MOT_ATOM_IMAGE_TIME - CAMERA_DEADTIME, name="absorption", frametype='atoms', trigger_duration=EXPOSURE_TIME_CMOT)
        imaging_aom_switch.enable(start_time+MOT_ATOM_IMAGE_TIME)
        imaging_aom_switch.disable(start_time+MOT_ATOM_IMAGE_TIME+EXPOSURE_TIME_CMOT)

        imaging_aom_switch.enable(start_time+NO_ATOM_IMAGE_TIME)
        basler.expose(start_time+NO_ATOM_IMAGE_TIME - CAMERA_DEADTIME, name="absorption", frametype='no_atoms', trigger_duration=EXPOSURE_TIME_CMOT)
        imaging_aom_switch.disable(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME_CMOT)
        imaging_aom_power.constant(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME_CMOT, 0)

        motl_aom_power.constant(start_time, 0)
        motl_aom_switch.disable(start_time)

        if repump:
            repump_aom_power.constant(start_time, 2)
            repump_aom_switch.disable(start_time)
            repump_aom_switch.enable(start_time+500e-6)
            repump_aom_switch.disable(start_time+700e-6)

    if IMAGE_MODE == "TOP":
        # The firebrain701b has no buffer so we can only take one image per sequence

        utils.jump_from_previous_value(z_coil, start_time, 5)
        utils.jump_from_previous_value(z_coil, start_time+duration, 0)

        utils.jump_from_previous_value(gradient_coil, start_time, 0)
        gradient_coil_switch.disable(start_time)

        # required to be consistent with above
        motl_repump_ad9959.jump_frequency(start_time, "MOT", IMG_MOTL_FREQ)

        sacher_aom_power.constant(start_time, IMAGING_POWER_TOP)
        firebrain701b.expose(start_time+MOT_ATOM_IMAGE_TIME, name="absorption", frametype='atoms', trigger_duration=EXPOSURE_TIME)
        sacher_aom_switch.enable(start_time+MOT_ATOM_IMAGE_TIME)
        sacher_aom_switch.disable(start_time+MOT_ATOM_IMAGE_TIME+EXPOSURE_TIME)

        motl_aom_power.constant(start_time, 0)
        motl_aom_switch.disable(start_time)

        if repump:
            repump_aom_power.constant(start_time, 2)
            repump_aom_switch.disable(start_time)
            repump_aom_switch.enable(start_time+500e-6)
            repump_aom_switch.disable(start_time+700e-6)


    return duration

def image_cmot(start_time, duration, traps_off = True, control=False, repump = True, control_duration = EXPOSURE_TIME ,control_power =2.0, marker_name='CMOT_image'):
    """Here is the code to take a CMOT image. Values are currently hardcoded,
    but when we get a better handle on labscript we should change them so that
    we read things in from a globals file and also optimize the ramping

    Args:
        start_time (float): the time the image begins
        duration (float): the time the imaging sequence ends. Added an extra 0.0005s to ensure values were reached in requisite amount of time
        marker_name (str, optional): The name of the image sequence in runviewer. Defaults to 'CMOT_image'.

    Returns:
        float: duration of the sequence in seconds
    """
    lab.add_time_marker(start_time, marker_name)
    if IMAGE_MODE == "SIDE":

        utils.ramp_from_previous_value(z_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
        utils.ramp_from_previous_value(small_z_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
        utils.ramp_from_previous_value(x_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
        # can make this bad code into a piecewise linear ramp from zak's utils functions 
        utils.ramp_from_previous_value(y_coil, start_time+100e-6, 400e-6, 7.0, samplerate=COIL_SAMPLE_RATE) # 1.0)
        utils.ramp_from_previous_value(y_coil, start_time+32e-3, 28e-3, MOT_Y_COIL, samplerate=COIL_SAMPLE_RATE)

        utils.jump_from_previous_value(gradient_coil, start_time, 0)
        gradient_coil_switch.disable(start_time)

        #gradient_coil_switch.constant(start_time+10e-3, 5)

        motl_repump_ad9959.jump_frequency(start_time, "MOT", IMG_MOTL_FREQ)

        #dt808_aom_switch.disable(start_time)

        imaging_aom_power.constant(start_time, IMAGING_POWER_SIDE)
        if traps_off:
            dt808_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME-0.000)
            utils.jump_from_previous_value(dt785_aom_power, start_time+CMOT_ATOM_IMAGE_TIME, 0)
            utils.jump_from_previous_value(dt852_aom_power, start_time+CMOT_ATOM_IMAGE_TIME, 0)
            dt785_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME-0.000)
            dt770_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME-0.000)
            utils.jump_from_previous_value(dt785_aom_power, start_time+CMOT_ATOM_IMAGE_TIME, 0)
            utils.jump_from_previous_value(dt852_aom_power, start_time+CMOT_ATOM_IMAGE_TIME, 0)


        basler.expose(start_time+CMOT_ATOM_IMAGE_TIME - CAMERA_DEADTIME_CMOT,  'absorption', 'atoms', EXPOSURE_TIME_CMOT)
        imaging_aom_switch.enable(start_time+CMOT_ATOM_IMAGE_TIME)
        imaging_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME+EXPOSURE_TIME_CMOT)




        # If we want to add control light to imaging sequence:
        if control:
            utils.jump_from_previous_value(control_aom_power, start_time+CMOT_ATOM_IMAGE_TIME - 1e-3, control_power)
            control_aom_switch.enable(start_time+CMOT_ATOM_IMAGE_TIME)
            control_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME+control_duration)
            utils.jump_from_previous_value(control_aom_power, start_time+CMOT_ATOM_IMAGE_TIME+control_duration, 0)

        imaging_aom_switch.enable(start_time+NO_ATOM_IMAGE_TIME)
        basler.expose(start_time+NO_ATOM_IMAGE_TIME - CAMERA_DEADTIME_CMOT, 'absorption', 'no_atoms', EXPOSURE_TIME_CMOT)
        imaging_aom_switch.disable(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME_CMOT)
        imaging_aom_power.constant(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME_CMOT, 0)
        
        if repump:
            repump_aom_power.constant(start_time, 2)
            repump_aom_switch.disable(start_time)
            repump_aom_switch.enable(start_time+500e-6)
            repump_aom_switch.disable(start_time+700e-6)
            repump_aom_power.constant(start_time+700e-6, 0)

    if IMAGE_MODE == "TOP":

        utils.jump_from_previous_value(z_coil, start_time, 5)
        utils.jump_from_previous_value(z_coil, start_time+duration, 0)

        utils.jump_from_previous_value(gradient_coil, start_time, 0)
        gradient_coil_switch.disable(start_time)

        # required to be consistent with above
        motl_repump_ad9959.jump_frequency(start_time, "MOT", IMG_MOTL_FREQ)

        dt808_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME,)
        dt785_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME,)


        sacher_aom_power.constant(start_time, IMAGING_POWER_TOP)
        firebrain701b.expose(start_time+CMOT_ATOM_IMAGE_TIME-CAMERA_DEADTIME_TOP, name="absorption", frametype='atoms', trigger_duration=EXPOSURE_TIME_TOP)
        sacher_aom_switch.enable(start_time+CMOT_ATOM_IMAGE_TIME)
        sacher_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME+EXPOSURE_TIME_TOP)

        if control:
            # If we want to add control light to imaging sequence:
            utils.jump_from_previous_value(control_aom_power, start_time+CMOT_ATOM_IMAGE_TIME - 1e-3, control_power)
            control_aom_switch.enable(start_time+CMOT_ATOM_IMAGE_TIME)
            control_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME+control_duration)
            utils.jump_from_previous_value(control_aom_power, start_time+CMOT_ATOM_IMAGE_TIME+control_duration, 0)

        motl_aom_power.constant(start_time, 0)
        motl_aom_switch.disable(start_time)

        if repump:
            repump_aom_power.constant(start_time, 2)
            repump_aom_switch.disable(start_time)
            repump_aom_switch.enable(start_time+500e-6)
            repump_aom_switch.disable(start_time+700e-6)

    return duration

def image_cmot_hamamatsu(start_time, duration, traps_off = True, control=False, repump = True, control_duration = EXPOSURE_TIME ,control_power =2.0, marker_name='CMOT_image'):
    """Here is the code to take a CMOT image. Values are currently hardcoded,
    but when we get a better handle on labscript we should change them so that
    we read things in from a globals file and also optimize the ramping

    Args:
        start_time (float): the time the image begins
        duration (float): the time the imaging sequence ends. Added an extra 0.0005s to ensure values were reached in requisite amount of time
        marker_name (str, optional): The name of the image sequence in runviewer. Defaults to 'CMOT_image'.

    Returns:
        float: duration of the sequence in seconds
    """
    lab.add_time_marker(start_time, marker_name)

    utils.ramp_from_previous_value(y_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
    utils.ramp_from_previous_value(small_z_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
    utils.ramp_from_previous_value(x_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
    # can make this bad code into a piecewise linear ramp from zak's utils functions 
    utils.ramp_from_previous_value(z_coil, start_time+100e-6, 400e-6, 5.0, samplerate=COIL_SAMPLE_RATE) # 1.0)
    utils.ramp_from_previous_value(z_coil, start_time+32e-3, 28e-3, MOT_Z_COIL, samplerate=COIL_SAMPLE_RATE)

    utils.jump_from_previous_value(gradient_coil, start_time, 0)
    gradient_coil_switch.disable(start_time)

    #gradient_coil_switch.constant(start_time+10e-3, 5)

    motl_repump_ad9959.jump_frequency(start_time, "MOT", IMG_MOTL_FREQ)

    #dt808_aom_switch.disable(start_time)

    sacher_aom_power.constant(start_time, HC_IMAGING_POWER_CMOT)
    if traps_off:
        dt808_aom_switch.disable(start_time+HC_CMOT_ATOM_IMAGE_TIME-0.000)
        utils.jump_from_previous_value(dt785_aom_power, start_time+HC_CMOT_ATOM_IMAGE_TIME, 0)
        utils.jump_from_previous_value(dt852_aom_power, start_time+HC_CMOT_ATOM_IMAGE_TIME, 0)
        dt785_aom_switch.disable(start_time+HC_CMOT_ATOM_IMAGE_TIME-0.000)
        dt770_aom_switch.disable(start_time+HC_CMOT_ATOM_IMAGE_TIME-0.000)
        utils.jump_from_previous_value(dt785_aom_power, start_time+HC_CMOT_ATOM_IMAGE_TIME, 0)
        utils.jump_from_previous_value(dt852_aom_power, start_time+HC_CMOT_ATOM_IMAGE_TIME, 0)


    hamamatsu.expose(start_time+HC_CMOT_ATOM_IMAGE_TIME - HC_CAMERA_DEADTIME_CMOT,  'absorption', 'atoms', HC_EXPOSURE_TIME_CMOT)
    sacher_aom_switch.enable(start_time+HC_CMOT_ATOM_IMAGE_TIME)
    sacher_aom_switch.disable(start_time+HC_CMOT_ATOM_IMAGE_TIME+HC_EXPOSURE_TIME_CMOT)

    # If we want to add control light to imaging sequence:
    if control:
        utils.jump_from_previous_value(control_aom_power, start_time+HC_CMOT_ATOM_IMAGE_TIME - 1e-3, control_power)
        control_aom_switch.enable(start_time+HC_CMOT_ATOM_IMAGE_TIME)
        control_aom_switch.disable(start_time+HC_CMOT_ATOM_IMAGE_TIME+control_duration)
        utils.jump_from_previous_value(control_aom_power, start_time+HC_CMOT_ATOM_IMAGE_TIME+control_duration, 0)

    sacher_aom_switch.enable(start_time+ HC_NO_ATOM_IMAGE_TIME)
    hamamatsu.expose(start_time+HC_NO_ATOM_IMAGE_TIME - HC_CAMERA_DEADTIME_CMOT, 'absorption', 'atoms', HC_EXPOSURE_TIME_CMOT)
    sacher_aom_switch.disable(start_time+HC_NO_ATOM_IMAGE_TIME+HC_EXPOSURE_TIME_CMOT)
    sacher_aom_power.constant(start_time+HC_NO_ATOM_IMAGE_TIME+HC_EXPOSURE_TIME_CMOT, 0)

    hamamatsu.expose(start_time+HC_BCKG_ATOM_IMAGE_TIME - HC_CAMERA_DEADTIME_CMOT, 'absorption', 'atoms', HC_EXPOSURE_TIME_CMOT)
    
    if repump:
        repump_aom_power.constant(start_time, 2)
        repump_aom_switch.disable(start_time)
        repump_aom_switch.enable(start_time+500e-6)
        repump_aom_switch.disable(start_time+700e-6)
        repump_aom_power.constant(start_time+700e-6, 0)

    return duration



def image_cmot_cut(start_time, duration, control=False, repump = True, control_duration = EXPOSURE_TIME ,control_power =2.0, deplete_atoms_time = 500e-6, marker_name='CMOT_image'):
    """Here is the code to take a CMOT image. Values are currently hardcoded,
    but when we get a better handle on labscript we should change them so that
    we read things in from a globals file and also optimize the ramping

    Args:
        start_time (float): the time the image begins
        duration (float): the time the imaging sequence ends. Added an extra 0.0005s to ensure values were reached in requisite amount of time
        marker_name (str, optional): The name of the image sequence in runviewer. Defaults to 'CMOT_image'.

    Returns:
        float: duration of the sequence in seconds
    """
    lab.add_time_marker(start_time, marker_name)
    if IMAGE_MODE == "SIDE":

        utils.ramp_from_previous_value(z_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
        # can make this bad code into a piecewise linear ramp from zak's utils functions 
        utils.ramp_from_previous_value(y_coil, start_time+100e-6, 400e-6, 7.0, samplerate=COIL_SAMPLE_RATE) # 1.0)
        utils.ramp_from_previous_value(y_coil, start_time+32e-3, 28e-3, MOT_Y_COIL, samplerate=COIL_SAMPLE_RATE)

        utils.jump_from_previous_value(gradient_coil, start_time, 0)
        gradient_coil_switch.disable(start_time)

        #gradient_coil_switch.constant(start_time+10e-3, 5)

        motl_repump_ad9959.jump_frequency(start_time, "MOT", IMG_MOTL_FREQ)

        #dt808_aom_switch.disable(start_time)

        imaging_aom_power.constant(start_time, IMAGING_POWER_SIDE)

        # sacher_aom_power.constant(start_time+CMOT_ATOM_IMAGE_TIME-deplete_atoms_time, 3)
        # sacher_aom_switch.enable(start_time+CMOT_ATOM_IMAGE_TIME-deplete_atoms_time)
        # sacher_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME)
        # sacher_aom_power.constant(start_time+CMOT_ATOM_IMAGE_TIME, 0)
        
        probe_aom_power.constant(start_time+CMOT_ATOM_IMAGE_TIME-deplete_atoms_time, 2)
        probe_aom_switch.enable(start_time+CMOT_ATOM_IMAGE_TIME-deplete_atoms_time)
        probe_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME)
        probe_aom_power.constant(start_time+CMOT_ATOM_IMAGE_TIME, 0)

        dt808_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME-0.000)
        dt785_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME-0.000)
        basler.expose(start_time+CMOT_ATOM_IMAGE_TIME- CAMERA_DEADTIME_CMOT,  'absorption', 'atoms', EXPOSURE_TIME)
        imaging_aom_switch.enable(start_time+CMOT_ATOM_IMAGE_TIME)
        imaging_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME+EXPOSURE_TIME)

        # If we want to add control light to imaging sequence:
        if control:
            utils.jump_from_previous_value(control_aom_power, start_time+CMOT_ATOM_IMAGE_TIME - 1e-3, control_power)
            control_aom_switch.enable(start_time+CMOT_ATOM_IMAGE_TIME)
            control_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME+control_duration)
            utils.jump_from_previous_value(control_aom_power, start_time+CMOT_ATOM_IMAGE_TIME+control_duration, 0)

        imaging_aom_switch.enable(start_time+NO_ATOM_IMAGE_TIME)
        basler.expose(start_time+NO_ATOM_IMAGE_TIME- CAMERA_DEADTIME_CMOT, 'absorption', 'no_atoms', EXPOSURE_TIME)
        imaging_aom_switch.disable(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME)
        imaging_aom_power.constant(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME, 0)
        
        if repump:
            repump_aom_power.constant(start_time, 2)
            repump_aom_switch.disable(start_time)
            repump_aom_switch.enable(start_time+500e-6)
            repump_aom_switch.disable(start_time+700e-6)
            repump_aom_power.constant(start_time+700e-6, 0)

    if IMAGE_MODE == "TOP":

        utils.jump_from_previous_value(z_coil, start_time, 5)
        utils.jump_from_previous_value(z_coil, start_time+duration, 0)

        utils.jump_from_previous_value(gradient_coil, start_time, 0)
        gradient_coil_switch.disable(start_time)

        # required to be consistent with above
        motl_repump_ad9959.jump_frequency(start_time, "MOT", IMG_MOTL_FREQ)

        dt808_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME,)
        dt785_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME,)

        sacher_aom_power.constant(start_time, IMAGING_POWER_TOP)
        firebrain701b.expose(start_time+CMOT_ATOM_IMAGE_TIME, name="absorption", frametype='atoms', trigger_duration=EXPOSURE_TIME)
        sacher_aom_switch.enable(start_time+CMOT_ATOM_IMAGE_TIME)
        sacher_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME+EXPOSURE_TIME)

        if control:
            # If we want to add control light to imaging sequence:
            utils.jump_from_previous_value(control_aom_power, start_time+CMOT_ATOM_IMAGE_TIME - 1e-3, control_power)
            control_aom_switch.enable(start_time+CMOT_ATOM_IMAGE_TIME)
            control_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME+control_duration)
            utils.jump_from_previous_value(control_aom_power, start_time+CMOT_ATOM_IMAGE_TIME+control_duration, 0)

        motl_aom_power.constant(start_time, 0)
        motl_aom_switch.disable(start_time)

        if repump:
            repump_aom_power.constant(start_time, 2)
            repump_aom_switch.disable(start_time)
            repump_aom_switch.enable(start_time+500e-6)
            repump_aom_switch.disable(start_time+700e-6)

    return duration



def image_dt(start_time, duration, repump=True, repump_during_img = False,  RSC=False,marker_name='DT_image'):
    """Here is the code to take a DT image. Values are currently hardcoded,
    but when we get a better handle on labscript we should change them so that
    we read things in from a globals file and also optimize the ramping

    Args:
        start_time (float): the time the image begins
        duration (float): the time the imaging sequence ends. Added an extra 0.0005s to ensure values were reached in requisite amount of time
        marker_name (str, optional): The name of the image sequence in runviewer. Defaults to 'DT_image'.

    Returns:
        float: duration of the sequence in seconds
    """
    lab.add_time_marker(start_time, marker_name)
    if IMAGE_MODE == "SIDE":

        
        utils.ramp_from_previous_value(z_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
        utils.ramp_from_previous_value(small_z_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
        utils.ramp_from_previous_value(x_coil, start_time+100e-6,400e-6, 0, samplerate=COIL_SAMPLE_RATE) 
        # can make this bad code into a piecewise linear ramp from zak's utils functions 
        utils.ramp_from_previous_value(y_coil, start_time+100e-6, 400e-6, 7.0, samplerate=COIL_SAMPLE_RATE) # 1.0)
        utils.ramp_from_previous_value(y_coil, start_time+32e-3, 28e-3, MOT_Y_COIL, samplerate=COIL_SAMPLE_RATE)

        # motl_repump_ad9959.jump_frequency(start_time, "MOT", IMG_MOTL_FREQ)
        # dt808_aom_switch.disable(start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME)
        # dt785_aom_switch.disable(start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME)
        # #utils.jump_from_previous_value(dt808_aom_power, start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME-400e-6, DT_RAMP_POWER)
        # utils.jump_from_previous_value(dt808_aom_power, start_time + DT_ATOM_IMAGE_TIME- DT_TRAP_OFF_TIME, 0)
        # utils.jump_from_previous_value(dt785_aom_power, start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME, 0)
        # utils.jump_from_previous_value(dt852_aom_power, start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME, 0) 

        # imaging_aom_power.constant(start_time, IMAGING_POWER_SIDE)
        # basler.expose(start_time+DT_ATOM_IMAGE_TIME,  'absorption', 'atoms', EXPOSURE_TIME)
        # imaging_aom_switch.enable(start_time+DT_ATOM_IMAGE_TIME)
        # imaging_aom_switch.disable(start_time+DT_ATOM_IMAGE_TIME+EXPOSURE_TIME)

        # imaging_aom_switch.enable(start_time+NO_ATOM_IMAGE_TIME)
        # basler.expose(start_time+NO_ATOM_IMAGE_TIME, 'absorption', 'no_atoms', EXPOSURE_TIME)
        # imaging_aom_switch.disable(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME)
        # imaging_aom_power.constant(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME, 0)
        # print(start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME + CAMERA_DEADTIME)
        motl_repump_ad9959.jump_frequency(start_time, "MOT", IMG_MOTL_FREQ)
        #utils.ramp_from_previous_value(dt808_aom_power, start_time+ DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME -2e-3, 1e-3, DT_RAMP_POWER, samplerate=COIL_SAMPLE_RATE)
        dt808_aom_switch.disable(start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME)
        dt785_aom_switch.disable(start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME)
        dt770_aom_switch.disable(start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME)
        #utils.jump_from_previous_value(dt808_aom_power, start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME-400e-6-50e-3, DT_RAMP_POWER)
        utils.jump_from_previous_value(dt808_aom_power, start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME, 0)
        utils.jump_from_previous_value(dt785_aom_power, start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME, 0)
        utils.jump_from_previous_value(dt852_aom_power, start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME, 0) 
        utils.jump_from_previous_value(dt770_aom_power, start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME, 0)


        imaging_aom_power.constant(start_time, IMAGING_POWER_SIDE)
        basler.expose(start_time+DT_ATOM_IMAGE_TIME- CAMERA_DEADTIME,  'absorption', 'atoms', EXPOSURE_TIME)
        imaging_aom_switch.enable(start_time+DT_ATOM_IMAGE_TIME)
        imaging_aom_switch.disable(start_time+DT_ATOM_IMAGE_TIME+EXPOSURE_TIME)

        imaging_aom_switch.enable(start_time+NO_ATOM_IMAGE_TIME)
        basler.expose(start_time+NO_ATOM_IMAGE_TIME- CAMERA_DEADTIME, 'absorption', 'no_atoms', EXPOSURE_TIME)
        imaging_aom_switch.disable(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME)
        imaging_aom_power.constant(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME, 0)

        if repump_during_img:
            repump_aom_power.constant(start_time, 0.5)
            repump_aom_switch.enable(start_time+DT_ATOM_IMAGE_TIME)
            repump_aom_switch.disable(start_time+DT_ATOM_IMAGE_TIME+EXPOSURE_TIME)

            repump_aom_switch.enable(start_time+NO_ATOM_IMAGE_TIME)
            repump_aom_switch.disable(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME)
            repump_aom_power.constant(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME, 0)

        if repump:
            repump_aom_power.constant(start_time, 2)
            repump_aom_switch.disable(start_time)
            repump_aom_switch.enable(start_time+500e-6)
            repump_aom_switch.disable(start_time+700e-6)

        if RSC:
            utils.jump_from_previous_value(rsc_aom_power, start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME, 0)
            utils.ramp_from_previous_value(rsc_aom_power, start_time + DT_ATOM_IMAGE_TIME-RSC_LATTICE_RAMP_DURATION - DT_TRAP_OFF_TIME, duration=RSC_LATTICE_RAMP_DURATION, final_value=0, samplerate=RSC_LASER_SAMPLE_RATE)
            rsc_aom_switch.disable(start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME)


    if IMAGE_MODE == "TOP":

        utils.jump_from_previous_value(z_coil, start_time, 5)
        utils.jump_from_previous_value(z_coil, start_time+duration, 0)

        utils.jump_from_previous_value(gradient_coil, start_time, 0)
        gradient_coil_switch.disable(start_time)

        # required to be consistent with above
        motl_repump_ad9959.jump_frequency(start_time, "MOT", IMG_MOTL_FREQ)
        # don't turn off traps in top image cause atoms fly away
        #dt808_aom_switch.disable(start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME)
        #dt785_aom_switch.disable(start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME)
        #utils.jump_from_previous_value(dt785_aom_power, start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME, 0)
        #utils.jump_from_previous_value(dt852_aom_power, start_time + DT_ATOM_IMAGE_TIME - DT_TRAP_OFF_TIME, 0) 


        sacher_aom_power.constant(start_time, IMAGING_POWER_TOP)
        firebrain701b.expose(start_time+DT_ATOM_IMAGE_TIME - CAMERA_DEADTIME_TOP, name="absorption", frametype='atoms', trigger_duration=EXPOSURE_TIME_TOP)
        sacher_aom_switch.enable(start_time+DT_ATOM_IMAGE_TIME)
        sacher_aom_switch.disable(start_time+DT_ATOM_IMAGE_TIME+EXPOSURE_TIME_TOP)

        motl_aom_power.constant(start_time, 0)
        motl_aom_switch.disable(start_time)

        if repump:
            repump_aom_power.constant(start_time, 2)
            repump_aom_switch.disable(start_time)
            repump_aom_switch.enable(start_time+500e-6)
            repump_aom_switch.disable(start_time+700e-6)

    return duration

def image_dt_TOF(start_time, duration, dt_off_duration = 1e-6, repump = True, marker_name='CMOT_image'):
    """Here is the code to take a CMOT image. Values are currently hardcoded,
    but when we get a better handle on labscript we should change them so that
    we read things in from a globals file and also optimize the ramping

    Args:
        start_time (float): the time the image begins
        duration (float): the time the imaging sequence ends. Added an extra 0.0005s to ensure values were reached in requisite amount of time
        marker_name (str, optional): The name of the image sequence in runviewer. Defaults to 'CMOT_image'.

    Returns:
        float: duration of the sequence in seconds
    """
    lab.add_time_marker(start_time, marker_name)
    if IMAGE_MODE == "SIDE":

        # can make this bad code into a piecewise linear ramp from zak's utils functions 
        utils.ramp_from_previous_value(y_coil, start_time+100e-6, 400e-6, 1, samplerate=COIL_SAMPLE_RATE)
        utils.ramp_from_previous_value(y_coil, start_time+32e-3, 28e-3, 0.3, samplerate=COIL_SAMPLE_RATE)

        utils.jump_from_previous_value(gradient_coil, start_time, 0)
        gradient_coil_switch.disable(start_time)

        gradient_coil_switch.enable(start_time+10e-3)

        motl_repump_ad9959.jump_frequency(start_time, "MOT", IMG_MOTL_FREQ)

        imaging_aom_power.constant(start_time, IMAGING_POWER_SIDE)
        basler.expose(start_time+CMOT_ATOM_IMAGE_TIME,  'absorption', 'atoms', EXPOSURE_TIME)
        imaging_aom_switch.enable(start_time+CMOT_ATOM_IMAGE_TIME)
        imaging_aom_switch.disable(start_time+CMOT_ATOM_IMAGE_TIME+EXPOSURE_TIME)
        dt808_aom_switch.disable(start_time + CMOT_ATOM_IMAGE_TIME - dt_off_duration)
        dt785_aom_switch.disable(start_time + CMOT_ATOM_IMAGE_TIME - dt_off_duration)
        dt808_aom_switch.enable(start_time + CMOT_ATOM_IMAGE_TIME)
        dt785_aom_switch.enable(start_time + CMOT_ATOM_IMAGE_TIME)


        # If we want to add control light to imaging sequence:

        imaging_aom_switch.enable(start_time+NO_ATOM_IMAGE_TIME)
        basler.expose(start_time+NO_ATOM_IMAGE_TIME, 'absorption', 'no_atoms', EXPOSURE_TIME)
        imaging_aom_switch.disable(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME)
        imaging_aom_power.constant(start_time+NO_ATOM_IMAGE_TIME+EXPOSURE_TIME, 0)

        
        if repump:
            repump_aom_power.constant(start_time, 2)
            repump_aom_switch.disable(start_time)
            repump_aom_switch.enable(start_time+500e-6)
            repump_aom_switch.disable(start_time+700e-6)

    return duration

def slm_set_zernike():

    # Add zernike correction
    if MLOOP_CORR_UPDATE:

        # name of the polynomial is in noll's index
        start_order = 2
        zernike_array = [0]*(start_order-1)

        for i in range(start_order, start_order+MLOOP_NUM_POLYNOMIALS):
            zernike_array.append(eval("MLOOP_ZERNIKE{:02d}".format(i)))
        slm.add_zernike(zernike_array)

    # if boolean is False, ignore the globals
    else:
        slm.add_zernike([0]*MLOOP_NUM_POLYNOMIALS)

def setup_slm():
    '''unified code to set up the parameters for SLM'''

    if TRAP_NUM == 1:
        slm.one_trap(shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS)
    if TRAP_NUM == 2:
        slm.two_traps(target_sep=TRAP_SEPARATION, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS, alpha=TRAP_ALPHA)
    if TRAP_NUM == 3:
        slm.array_traps(phase_pattern_file=ARR_FILE, phase_pattern_folder=ARR_FOLDER, shiftx=TRAP_SHIFTX, shifty=TRAP_SHIFTY, defocus=TRAP_DEFOCUS, alpha=TRAP_ALPHA)

    slm.clip_circle(clip_circle_bool=CLIP_SLM_BOOL, px_ring=CLIP_RING_PIXELS, clip_shiftx=CLIP_SHIFTX, clip_shifty=CLIP_SHIFTY)
    slm.add_bob_circle(bob_bool=BOB_BOOL, rad_shift=BOB_RADIUS, bob_shiftx=BOB_SHIFTX, bob_shifty=BOB_SHIFTY, bob_defocus=BOB_DEFOCUS)

    # this causes things to change position because we are somehow wavefront correcting at slightly different position
    # slm.add_wf_correction(wf_corr_bool=WF_CORR_BOOL, wf_corr_file=WF_CORR_FILE)

    # slm_set_zernike() # not using this anymore since we added wavefront corrections
