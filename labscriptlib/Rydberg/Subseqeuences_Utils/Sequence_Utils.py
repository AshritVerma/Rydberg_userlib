# This file contains helper functions for sequences. Many are inspired/directly lifted from Zak's code

# Dictionary to keep track of past channel outputs to allow ramping from
# previous values.
_previous_values = {}


def set_static_parameters():
    """Configure things that do not change during the sequence.

    This function is intended to have all the sequence-specific code that does
    things to configure the machine before running the sequence.
    """

    # Currently these are set in the main sequence file now since each file will in theory use different parameters
    # # Here we program an arduino to set the frequencies of the MOT and repump lasers
    # # we put the motl and repump MOT freqs at the end of the list for resetting to the first value we program in at the end of the sequenece
    # if MOT_ONLY:
    #     motl_freq_list = [MOT_MOTL_FREQ, IMG_MOTL_FREQ, MOT_MOTL_FREQ]
    #     repump_freq_list = [MOT_REPUMP_FREQ, MOT_REPUMP_FREQ]

    # elif CMOT_ONLY:
    #     motl_freq_list = [MOT_MOTL_FREQ, CMOT_MOTL_FREQ, IMG_MOTL_FREQ, MOT_MOTL_FREQ]
    #     repump_freq_list = [MOT_REPUMP_FREQ, MOT_REPUMP_FREQ]
    
    # motl_repump_ad9959.program_freq("MOT", motl_freq_list)
    # motl_repump_ad9959.program_freq("Repump", repump_freq_list)

def turn_off_critical_devices():
    pass


def set_previous_value(output, value):
    """Record the last output value of a channel.

    Use this method to update the record of what value was last output on a
    channel. This is necessary in order to be able to use the
    ramp_from_previous_value() function, as it has to know what value was last
    output. Labscript doesn't have built-in functionality for that as of this
    writing, so we must keep track of the last output manually. This can be used
    for any kind of output, but is primarily helpful for analog outputs.

    It is not necessary to call this function directly when using
    ramp_from_previous_value(), jump_from_previous_value() or other similar
    functions defined in this module because those functions call this function
    automatically. However, if the output is changed without using one of those
    functions, then make sure to call this method in order to keep track of the
    output.

    Note that the way that this keeping track of previous values works assumes
    that the outputs ser set in the labscript in the actual order that they will
    be output. In other words ensure that the code specifying a ramp at t=1 is
    defined in the labscript before a ramp that occurs at t=2 to ensure that
    the previous value actually corresponds to the previous ramp.

    Args:
        output (labscript.AnalogOut or similar): The object representing the
            output channel. This should be something from the connection table.
        value (any, usually float): The value that the channel was last set to.
    """
    # Labscript creates new instances of the output classes each time a shot is
    # compiled, but _previous_values still contains references to old instances
    # from past shot compilations. Because they are in the dictionary, they
    # won't be garbage collected, which leads to a memory leak because the old
    # output class instances (and anything they reference, which is a lot) never
    # get deleted. To work around that, this function makes sure to delete old
    # output class instances whenver a new one for the same physical output is
    # used. The names of the outputs are unique, so if a new output instance has
    # the same name attribute as one already in the dictionary, then the one in
    # the dictionary is old and should be deleted. Note that just keying by
    # output.name rather than by output itself isn't ideal because then if
    # get_previous_value() were called before set_previous_value() it would then
    # just return the last entry in _previous_values from the previous shot,
    # which probably isn't what we want.
    if output not in _previous_values:
        # This output instance isn't in the _previous_values dict yet; see if
        # there's an old output instance for the same output (which should have
        # the same .name attribute) and if so delete it. Use .copy() to avoid
        # editing the original dictionary while looping over it.
        for existing_output in _previous_values.copy().keys():
            if existing_output.name == output.name:
                # Found a match. Delete the entry for the old instance.
                del _previous_values[existing_output]

    # Finally actually store the value.
    _previous_values[output] = value


def get_previous_value(output):
    """Return the previous value output on the specified output.

    This function uses the data from set_previous_value(), so see that
    function's documentation for more information. In particular, note that this
    function is not a built-in labscript feature and it assumes that output
    changes are defined in the labscript in the order in which they actually
    occur in the sequence, and it assumes that set_previous_value() was called
    appropriately.

    Args:
        output (labscript.AnalogOut or similar): The object representing the
            output channel. This should be something from the connection table.

    Returns:
        value (any, usually float): The value that the channel was last set to,
            according to the record stored with set_previous_value().
    """
    return _previous_values[output]


def jump_from_previous_value(output, time, value):
    """Change an output to a new value without ramping.

    This function is like ramp_from_previous_value(), except it suddenly jumps
    outputs to a new value instead of ramping them. It simply calls the output's
    constant() method and then calls set_previous_value() to ensure that we keep
    track of the output's last value.

    It is only necessay to use this function when using outputs for which
    ramp_from_previous_value() is used at other points in the sequence. For
    channels that don't use that function, it is fine to simply call the
    output's constant() method directly.

    Args:
        output (labscript.AnalogOut or similar): The object representing the
            output channel. This should be something from the connection table.
        time (float): (seconds) Time in the sequence at which to change the
            output.
        value (any, usually float): The value to change the output to.
    """
    # Set the output to the instructed value.
    output.constant(time, value)

    # Update previous value.
    set_previous_value(output, value)


def ramp_from_previous_value(output, start_time, duration, final_value,
                             samplerate, initial_value=None,
                             truncation=1.0):
    """Ramp an output to a new value from its previous value.

    This function uses output.ramp() to ramp the output from its previous value
    to final_value starting at start_time and occuring over a time set by
    duration. This is primarily a thin wrapper around the output.ramp(), except
    that it uses get_previous_value() to automatically find the initial value
    for the ramp. Note that this implies that the past calls to program the
    channel's output have used set_previous_value() (either directly or
    indirectly) appropriately. Typically that is done by programming the output
    mainly using jump_from_previous_value(), ramp_from_previous_value(), and
    other similar functions from this module which call set_previous_value()
    automatically. If the channel's output is ever configured without using one
    of those functions, make sure to call set_previous_value() directly.

    Also note that, as mentioned in the documentation for set_previous_value(),
    the output changes for thsi output must be programmed in the labscript in
    the same order in which they will occur in the sequence. That isn't
    generally required by labscript, but it is required when using the functions
    defined here for keeping track of and using the previous channel values.

    Optionally, the input value can be specified. This allows ramping from a
    given value instead of the previous value. The advantage of still using this
    function when doing that rather than calling the output's ramp() method
    directly is that using this function still automatically calls
    set_previous_value().

    Args:
        output (labscript.AnalogOut or similar): The object representing the
            output channel. This should be something from the connection table.
        start_time (float): (seconds) Time in the sequence at which to start the
            ramp.
        duration (float): The duration of the full ramp. The actual duration
            will be less if truncation is set to something less than one.
        final_value (float): The ending value of the full ramp. The actual final
            value of the ramp will be different if truncation is set to
            something other than 1.
        initial_value (float, optional): (Default=None) The initial value to use
            for the start of the ramp. If set to None, the channel's previous
            output value will be used as the initial value for the ramp, which
            is what gives this function its name. Note that the previous output
            value used here will only be correct if the output has been
            programmed correctly, as discussed in the docstrings of this
            function and set_previous_value().
        samplerate (float, optional): (Default=None) (hertz) The sample rate of
            the analog cards used while performing the ramp. If set to None,
            then the value of the default_ramp_samplerate will be used.
        truncation (float, optional): (Default=1.0) The fraction of the ramp to
            actually do, which should be a number from 0 to 1. A value of 1
            implies that the full ramp will be done.

    Returns:
        actual_duration (float): (seconds) Time needed to do the ramp. This will
            be different than the input duration if truncation isn't set to 1.
        actual_final_value (float): The final value at the end of the ramp. Note
            that this will be different than the input final_value if truncation
            isn't set to 1.
    """
    # Set default input values if necessary.
    if initial_value is None:
        initial_value = get_previous_value(output)

    # Perform the ramp.
    actual_duration = output.ramp(
        start_time,
        duration,
        initial_value,
        final_value,
        samplerate,
        truncation=truncation,
    )

    # Calculate the actual final value given truncation.
    if truncation == 1.0:
        # Even though the formula for truncation != 1 works for this simple case
        # as well, we'll treat it specially to avoid rounding errors.
        actual_final_value = final_value
    else:
        ramp_change = truncation * (final_value - initial_value)
        actual_final_value = initial_value + ramp_change

    # Update previous value.
    set_previous_value(output, actual_final_value)

    return actual_duration, actual_final_value

def exp_ramp_from_previous_value(output, start_time, duration, final_value,
                             samplerate, initial_value=None,
                             truncation=None):
    """See above, but for exp ramping"""

    # Set default input values if necessary.
    if initial_value is None:
        initial_value = get_previous_value(output)

    # Perform the ramp.
    actual_duration = output.exp_ramp(
        start_time,
        duration,
        initial_value,
        final_value,
        samplerate,
        truncation=truncation,
    )

    # Update previous value.
    set_previous_value(output, final_value)

    return actual_duration

def piecewise_linear_ramp(channel_object, start_time, durations, values):
    """Program a channel to output a series of ramps.

    This function programs the channel channel_object to start at the first
    value in values at time start_time, then ramp to the following value in
    values over a time specified by the first element in durations. Then, the
    channel ramps from there to the subsequent value in values over a time
    specified by the second element of durations, and so on.

    Explained another way, this function outputs a piecewise linear ramp on the
    specified channel. The end points of each linear piece are specified in
    values and the duration of each piece is specified by the elements of
    durations. Each piece has the same end values as the ajoining pieces so that
    the ramp is continuous.

    Note that the length of the list of values should be one element longer
    than the length of the list of durations. Intrinsicly this is because a
    ramp needs a start point and an end point. Extra entries in values are
    just ignored, but if there are too many entries in durations.

    This function calls set_previous_value() appropriately to keep track of
    output values.

    Args:
        channel_object (labscript.AnalogOut): An analog channel from the
            connection table which will be used to output the values.
        start_time (float): (seconds) The time at which to start the first
            output created by this function.
        durations (list of floats): (seconds) A list, with each element
            specifying how long each piece of the piecewise linear ramp should
            be.
        values (list of floats): A list of values specifying the endpoints of
            pieces of the ramp. Note that the length of this list should be one
            longer than the length of durations. This comes from that fact that
            a ramp needs both a starting point and an end point.

    Raises:
        ValueError: If the length of values isn't one longer than the length of
            durations, then a ValueError is raised.

    Returns:
        duration (float): (seconds) The length of the full duration of the
            output programmed by this function, equal to the sum of the entries
            in durations.
    """
    # Check that the lengths of durations and values match up.
    values_length = len(values)
    durations_length = len(durations)
    if values_length != (durations_length + 1):
        message = (f"values (length {values_length}) must have one more "
                   f"element than durations (length {durations_length}).")
        raise ValueError(message)

    # Iterate over the pieces of the piecewise ramp.
    t_local = start_time
    for j, duration in enumerate(durations):
        ramp_from_previous_value(
            channel_object,
            t_local,
            duration,
            final_value=values[j + 1],
            initial_value=values[j],
        )
        t_local += duration

    # Calculate the total time taken.
    duration = t_local - start_time
    return duration


def piecewise_constant_ramp(channel_object, start_time, durations, values):
    """Program a channel to output a series of constant values.

    This is akin to the piecewise_linear_ramp() function, except that the output
    is held constant during each piece instead of being ramped. This means that
    in general the ramp isn't continuous, as it is stepped between values.

    Note that the number of entries in durations and in values should be the
    same. However, an error will only be thrown if there are more entries in
    durations than in values.

    Args:
        channel_object (labscript.AnalogOut): An analog channel from the
            connection table which will be used to output the values.
        start_time (float): (seconds) The time at which to start the first
            output created by this function.
        durations (list of floats): (seconds) A list, with each element
            specifying how long each output in values should be held before
            moving to the next.
        values (list of floats): A list of values that will be output
            through channel_object, in order. Note that the length of this list
            must be the same as the length of the durations list.

    Raises:
        ValueError: If the length of values isn't the same as the length of
            durations, then a ValueError is raised.

    Returns:
        duration (float): (seconds) The length of the full duration of the
            output programmed by this function, equal to the sum of the
            entries in durations.
    """
    # Check that the lengths of durations and values match up.
    values_length = len(values)
    durations_length = len(durations)
    if values_length != durations_length:
        message = (f"values (length {values_length}) must be the same length "
                   f"as durations (length {durations_length}).")
        raise ValueError(message)

    # Iterate over the outputs.
    t_local = start_time
    for duration, value in zip(durations, values):
        jump_from_previous_value(channel_object, t_local, value)
        t_local += duration

    # Calculate the total time taken.
    duration = t_local - start_time
    return duration

def aom_pulse(aom_name, time_start, duration, power_level):
    """A sequence to turn on an aom for a specified duration at time_start, then automatically turn it off
    we made this function because it's exhausting to constantly to on/off both the power and the switches

    Args:
        aom_name (string): the name of the aom. Case is important!!
        time_start (float): the time at which to turn it on
        duration (float): the duration to turn on the aom
        power_level (float): the analog card output voltage
    """
    eval(aom_name + "_aom_switch").enable(time_start)    
    eval(aom_name + "_aom_power").constant(time_start, power_level)  

    eval(aom_name + "_aom_switch").disable(time_start + duration)    
    eval(aom_name + "_aom_power").constant(time_start + duration, 0)  


def open_shuttered_beam(
        time, aom_power_value, shutter_object,
        aom_power_object, aom_digital_object=None,
        headroom=5e-3, aom_power_off_value=0.,
        **kwargs):
    """Intelligently turn on a beam that has a shutter and an AOM.

    This function is intended to be used when a beam's AOM is on to stay warm
    but its light is blocked with a shutter. This function turns off the AOM,
    then opens the shutter, then turns the AOM back on to have a fast and
    well-defined edge for the beam to turn on.

    This function assumes that setting the aom_analog output to 0 will turn off
    the AOM. This assumption is not necessary if aom_digital is provided.

    Switching the AOM off/on with the digital channel only can be achieved by
    setting aom_power_off_value to the same value as aom_power_value, in which
    case aom_digital_object should be provided.

    This is not a stage in the sequence, but rather a helper function. For that
    reason it does NOT return a 'duration'.

    Take care if calling close_shuttered_beam() before open_shuttered_beam(). If
    the difference in times between the two calls is less than the sum of the
    values for headroom provided to the two, then the shutter may be opened then
    closed again before the AOM is even turned on. Calling open_shuttered_beam()
    before close_shuttered_beam() would NOT lead to such a probblem.

    Args:
        time (float): (seconds) Time in the sequence (in seconds) at which the
            beam should be turned on.
        aom_power_value (float): The power setting for the AOM when it is turned
            on.
        shutter_object (labscript.Shutter): The shutter object representing the
            channel that controls the beam's shutter.
        aom_power_object (labscript.AnalogOut): The analog output object
            representing the channel that controls the aom's drive amplitude.
        aom_digital_object (labscript.DigitalOut, optional): (Default=None) The
            digital output object representing the channel that controls a
            digital on/off switch for the AOM. If set to None, the AOM will be
            turned off/on only using its analog controls.
        headroom (float, optional): (Default=5e-3) (seconds) Extra time provided
            to ensure that the shutter has fully opened. This delay is added on
            top of the shutter's calibrated opening time specified in the
            connectiontable.
        aom_power_off_value (float, optional): (Defaults=0) The power setting
            for the analog aom control when the aom is set to be off.
        **kwargs: additional keyword arguments, e.g. units="V" are passed to the
            function aom_power_object.constant() when turning the AOM on/off.
    """
    # Get the calibrated shutter delay
    open_delay = shutter_object.open_delay

    # Turn aom off at same time as shutter starts to move
    aom_off_time = (time - open_delay - headroom)
    aom_power_object.constant(aom_off_time, aom_power_off_value, **kwargs)
    if aom_digital_object:
        # Use enable/disable instead of go_low/go_high so that we account for if
        # the channel has inverted=True.
        aom_digital_object.disable(aom_off_time)

    # Open shutter early enough to have some headroom
    shutter_object.open(time - headroom)  # already accounts for open_delay

    # Turn on AOM
    aom_power_object.constant(time, aom_power_value, **kwargs)
    if aom_digital_object:
        aom_digital_object.enable(time)

    return


def close_shuttered_beam(
        time, aom_power_warm_value, shutter_object,
        aom_power_object, aom_digital_object=None,
        headroom=5e-3, aom_power_off_value=0.,
        **kwargs):
    """Intelligently turn off a beam that has a shutter and an AOM.

    This function is intended to be used to turn off a beam then keep its AOM
    warm. This function turns off a beam suddenly with its AOM to have a fast
    and well-defined edge, then closes its shutter, then turns the AOM on again
    to keep it warm.

    This function assumes that setting the aom_analog output to 0 will turn off
    the AOM. This assumption is not necessary if aom_digital is provided.

    Switching the AOM off/on with the digital channel only can be achieved by
    setting aom_power_off_value to the be the same as the channel's previous
    value, in which case aom_digital_object should be provided.

    This is not a stage in the sequence, but rather a helper function. For that
    reason it does NOT return a 'duration'.

    Take care if calling close_shuttered_beam() before open_shuttered_beam(). If
    the difference in times between the two calls is less than the sum of the
    values for headroom provided to the two, then the shutter may be opened then
    closed again before the AOM is even turned on. Calling open_shuttered_beam()
    before close_shuttered_beam() would NOT lead to such a probblem.

    Args:
        time (float): (seconds) Time in the sequence at which the beam should be
            turned off.
        aom_power_warm_value (float): The power setting for the AOM when it is
            turned on to stay warm after the shutter is closed. Note that this
            isn't necessarily the power setting of the AOM right before the beam
            is turned off.
        shutter_object (labscript.Shutter): The shutter object representing the
            channel that controls the beam's shutter.
        aom_power_object (labscript.AnalogOut): The analog output object
            representing the channel that controls the aom's drive amplitude.
        aom_digital_object (labscript.DigitalOut, optional): (Default=None) The
            digital output object representing the channel that controls a
            digital on/off switch for the AOM. If set to None, the AOM will be
            turned off/on only using its analog controls.
        headroom (float, optional): (Default=5e-3) (seconds) Extra time provided
            to ensure that the shutter has fully closed. This delay is added on
            top of the shutter's calibrated closing time specified in the
            connectiontable.
        aom_power_off_value (float, optional): (Default=0) The power setting for
            the analog aom control when the aom is briefly set to be off. Note
            that this is NOT the power setting used after the shutter is closed
            to keep the AOM warm; that is set with aom_power_warm_value.
        **kwargs: additional keyword arguments, e.g. units="V" are passed to the
            function aom_power_object.constant() when turning the AOM on/off.
    """
    # Turn aom off at desired time
    aom_power_object.constant(time, aom_power_off_value, **kwargs)
    if aom_digital_object:
        # Use enable/disable instead of go_low/go_high so that we account for if
        # the channel has inverted=True.
        aom_digital_object.disable(time)

    # Start closing the shutter at the same time. Delay its nominal off time by
    # its calibrated close_time to avoid possibly blocking the beam with the
    # shutter before the AOM is turned off.
    close_delay = shutter_object.close_delay
    # already accounts for close_delay
    shutter_object.close(time + close_delay)

    # Turn on AOM to keep it warm
    aom_on_time = time + close_delay + headroom
    aom_power_object.constant(aom_on_time, aom_power_warm_value, **kwargs)
    if aom_digital_object:
        aom_digital_object.enable(aom_on_time)

    return


def indexed_globals_values(global_name):
    """Get a list of values of globals with the same name appended by an index.

    This method looks through the globals for ones the start with global_name
    and end with an underscore followed by an index. For example, if global_name
    is set to 'cmot_master_freq' and there are globals named
    'cmot_master_freq_0' and 'cmot_master_freq_1', then their values will be
    included in the returned list. The returned list will be sorted such that
    the values of the globals with the lowest indices appear first. So in this
    example, the value of 'cmot_master_freq_0' would be first in the list,
    followed by the value of 'cmot_master_freq_1'. Note that the values (not the
    names of the globals) are returned.

    The global variable names must start with global_name followed immediately
    by an underscore then an index, which consists of one or more of the
    characters 0 through 9. If they do not follow this format, then this method
    will not return their values.

    Note: As far as I (Zak) can tell, there is no way to distinguish the globals
    injected by runmanager apart from the other globals, such as the ones built
    into python (run "import builtins; dir(builtins)" for a list). In practice
    this shouldn't be an issue though as the other globals presumably won't
    follow the strict format required for this function to include their values
    in the output.

    This function is particuarly helpful when using the M-LOOP Lyse integration.
    It lets you create a bunch of globals to be optimized in runmanager, then
    automatically bring them all into one list in the sequence's labscript.

    Args:
        global_name (str): The name of the globals (without the underscored or
            index at the end) whose values should be included

    Returns:
        values_list (list): The values of all of the globals that matched
            global_name, ordered by their index.
    """
    # Unfortunately the below also grabs a lot of actual built-in python things,
    # not just the runmanager globals. I haven't found a good way to just get
    # the list of globals that were injected by runmanager.
    global_names = dir(builtins)

    # We'll use the regular expression "match" function, which ensures that the
    # pattern is matched at the beginning of the string (so no "^" is
    # necessary).
    # The \d+ matches one or more digits (characters 0 to 9). Putting that
    # inside of (?P<index>\d+) puts them together into a group called "index".
    # The (?P<>) part is special python syntax for naming the group.
    # The "$" means the match must end at the end of the string.
    regex = re.compile(global_name + r'_(?P<index>\d+)$')

    # Find the globals that match the regular expression.
    match_list = []
    for name in global_names:
        match = regex.match(name)
        if match:
            index = int(match.group('index'))
            match_list.append((index, name))

    # Ensure that the globals are ordered by their index
    match_list.sort()

    # Get a list of the values of the globals
    values_list = [getattr(builtins, entry[1]) for entry in match_list]
    return values_list
