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

from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt, setup_slm
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    start()
    #spec.add_segment(.1, {0:"lambda x: np.sin(2*np.pi*.1*x/64)",1:"lambda x: np.sin(2*np.pi*.1*x/64)"}, 2**16)
    #spec.add_segment(.1, {0:"lambda x: 0",1:"lambda x: 0"}, 32)
    load_mot(0, 1)
    spectrum_awg.add_segment(.5, {0:"lambda x: np.sin(2*np.pi*.4*x/64) * np.heaviside(x-1250, 0.5) + np.sin(2*np.pi*1*x/64) * np.heaviside(-x+1250, 0.5)",
                          1:"lambda x: np.sin(2*np.pi*.02*x/64)"}, 2**15) # 125 MHz
    # for pure EIT
    spectrum_awg.add_segment(.5, {0:"lambda x: np.sin(2*np.pi*.4*x/64)",
                          1:"lambda x: np.sin(2*np.pi*.02*x/64)"}, 2**15) # will last 2**15 / (125 MHz) = 262 us 


    

    # two traps for the other segment
    # spectrum_awg.add_segment(.5, {0:"lambda x: 0.5*np.cos(2*np.pi*x*.32 + np.pi/8)+0.5*np.cos(2*np.pi*x*.3224 + np.pi/9)",
    #                       1:"lambda x: 0.5*np.cos(2*np.pi*x*.32 + np.pi/7)+0.5*np.cos(2*np.pi*x*.3224 + np.pi/6)"}, 2**20) # (2*np.pi*x*.32) is 40 MHz
    # line of 10 traps for the other segment
    # spectrum_awg.add_segment(.5, {1:"lambda x: 0.1*np.cos(2*np.pi*x*.3104 + np.pi/8.123)+0.1*np.cos(2*np.pi*x*.3128 + np.pi/9.1789) + 0.1*np.cos(2*np.pi*x*.3152 + np.pi/6.789) + 0.1*np.cos(2*np.pi*x*.3176 + np.pi/4.789) + + 0.1*np.cos(2*np.pi*x*.32 + np.pi/3.789) + 0.1*np.cos(2*np.pi*x*.3224 + np.pi/10.789) + 0.1*np.cos(2*np.pi*x*.3248 + np.pi/2.789) + 0.1*np.cos(2*np.pi*x*.3272 + np.pi/5.789) + 0.1*np.cos(2*np.pi*x*.3296 + np.pi/1.789) + 0.1*np.cos(2*np.pi*x*.332 + np.pi/11.789)",
    #                       0:"lambda x: np.cos(2*np.pi*x*.32 + np.pi/7)"}, 2**20) # (2*np.pi*x*.32) is 40 MHz
    ## single beam at 40MHz:
    # spectrum_awg.add_segment(.5, {0:"lambda x: np.cos(2*np.pi*x*.32)",
    #                       1:"lambda x: np.cos(2*np.pi*x*.32)"}, 2**20) # (2*np.pi*x*.32) is 40 MHz

    #spec.reset(.6)

    stop(2)

    # steps=33
    # dt=4*1*1e-6
    # delay=4*200*1e-3

    # t=0
    # start()
    # t=0
    # t+=1

    # for ii in range(steps):

    #     hc.expose(t, name="fluoresence", frametype='atoms', trigger_duration=4*20e-6)
    #     # t+=dt
    #     #aom_switch.enable(t)
    #     #t+=4*1*1e-3
    #     #aom_switch.disable(t)
    #     t+=delay
    # t+=3

    # stop(t)
