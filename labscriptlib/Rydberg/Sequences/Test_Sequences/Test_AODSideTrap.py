# #####################################################################
# #                                                                   #
# # /example.py                                                       #
# #                                                                   #
# # Copyright 2013, Monash University                                 #
# #                                                                   #
# # This file is part of the program labscript, in the labscript      #
# # suite (see http://labscriptsuite.org), and is licensed under the  #
# # Simplified BSD License. See the license.txt file in the root of   #
# # the project for the full license.                                 #
# #                                                                   #
# #####################################################################

# import time
# import numpy as np
# from scipy import signal
# from labscript import (
#     start,
#     stop,
# )
# import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils
# from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
# from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table
# from user_devices.Rydberg.AD9959ArduinoComm.labscript_devices import AD9959ArduinoComm

# if __name__ == '__main__':

#     # Import and define the global variables for devices
#     cxn_table()

#     t=0

#     start()

#     t+= load_mot(t, 0.1)

#     AOD0_init_freq = 86e6 #89e6
    
#     t += 0.01
#     sidetrap_770_ad9959.jump_frequency(t, "AOD0", AOD0_init_freq)
#     dds_step = 0.5 #0.01
#     dds_gap = dds_step / 2
#     for i in range(5):
#         t += dds_step
#         freq = AOD0_init_freq + 1e6 * i
#         sidetrap_770_ad9959.jump_frequency(t, "AOD0", freq)# * i)
#         # sidetrap_770_ad9959.jump_frequency(t + dds_gap, "AOD1", AOD1_init_freq - 10e6 * i, trigger=True)# * i)
        
#     t += dds_step

#     stop(t)

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


from labscript import (
    start,
    stop,
)
# from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import load_mot
import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table
from user_devices.Rydberg.AD9959ArduinoCommSpecial.labscript_devices import AD9959ArduinoCommSpecial

from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_cmot_cut,image_dt
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table
if __name__ == '__main__':

    # Import and define the global variables for devices
    t = 0
    cxn_table()
    start()
    t+= load_mot(t, 0.1)

    ch0_startfreq = 60e6-1e6
    ch0_endfreq = 40e6

    ch1_startfreq = 60e6+1e6
    ch1_endfreq = 100e6

    # ref = 0, can sweep twice, cannot do go_high twice!! must do go_high() then go_low() (note that running go_low() then go_high() does not seem to work)
    # ref = 1, turn off RF after the sweep
    # note that the t input does not mean anything here
    # form: double_ramp(t, channel_descriptor0, channel_descriptor1, ramp0_start, ramp0_stop, ramp0_time_up, ramp0_time_down, ramp1_start, ramp1_stop, ramp1_time_up, ramp1_time_down, ref = 0):
    sidetrap_770_ad9959.double_ramp(t, "AOD0", "AOD1", ch0_startfreq, ch0_endfreq, 0.01, 0.01, ch1_startfreq, ch1_endfreq, 0.3, 0.3, ref=0)
    t+=0.5
    triggerRampSync.go_high(t)
    t+=1
    triggerRampSync.go_low(t)
    t+=1e-2
    stop(t)