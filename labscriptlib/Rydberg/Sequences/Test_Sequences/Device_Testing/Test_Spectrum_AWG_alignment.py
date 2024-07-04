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

import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_dt, setup_slm
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table
import random 
import numpy as np

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    ntraps_x = 10
    ntraps_y = 1
    separation_um = 5 #10
    sampling_rate = 125 # in MHz
    central_freq = 40 #40 # in MHz
    time_to_be_on = 200 # in us
    freq_to_um_conversion = 0.0344 # MHz/um

    N_samples = time_to_be_on*sampling_rate

    random_phase_x = [3.282,0.356,3.775,0.358,4.371,3.791,3.174,1.453,6.142,1.373]
    random_phase_y = [1.258]

    amplitudes_x = [0.0151,0.9312,0.0004,0.0016,0.0034,0.0013,0.037,0.0004,0.003,0.0067]

######## Random initial phases
    string_x = " lambda x: "
    for i in range(ntraps_x):
        atom_pos = i - int(0.5*ntraps_x)
        freq_atom = (central_freq + atom_pos*freq_to_um_conversion*separation_um)/sampling_rate
        # random_phase = round(random.uniform(0,1)*2*np.pi,3)
        random_phase = random_phase_x[i]
        if (i != ntraps_x -1):
            string_x += " %g*np.cos(2*np.pi*x*%g +%g) +" %(1/ntraps_x, round(freq_atom,4), random_phase)
            # string_x += " %g*np.cos(2*np.pi*x*%g +%g) +" %(amplitudes_x[i], round(freq_atom,4), random_phase)

        else:
            string_x += " %g*np.cos(2*np.pi*x*%g +%g) " %(1/ntraps_x, round(freq_atom,4), random_phase)
            # string_x += " %g*np.cos(2*np.pi*x*%g +%g) " %(amplitudes_x[i], round(freq_atom,4), random_phase)


    string_y = " lambda x: "
    for i in range(ntraps_y):
        atom_pos = i - int(0.5*ntraps_y)
        freq_atom = (central_freq + atom_pos*freq_to_um_conversion*separation_um)/sampling_rate
        # random_phase = round(random.uniform(0,1)*2*np.pi,3)
        random_phase = random_phase_y[i]
        if (i != ntraps_y -1):
            string_y += " %g*np.cos(2*np.pi*x*%g +%g) +" %(1/ntraps_y, round(freq_atom,4), random_phase)
        else:
            string_y += " %g*np.cos(2*np.pi*x*%g +%g) " %(1/ntraps_y, round(freq_atom,4), random_phase)

 ######## Make strings for prep in one detect in other state:   
    ### 4 beams string:
    string_x4 = " lambda x: "
    traps_to_keep4 = [1,3,6,8]
    for i in range(ntraps_x):
        if i in traps_to_keep4:
            atom_pos = i - int(0.5*ntraps_x)
            freq_atom = (central_freq + atom_pos*freq_to_um_conversion*separation_um)/sampling_rate
            # random_phase = round(random.uniform(0,1)*2*np.pi,3)
            random_phase = random_phase_x[i]
            if (i != traps_to_keep4[-1]):
                string_x4 += " %g*np.cos(2*np.pi*x*%g +%g) +" %(1/len(traps_to_keep4), round(freq_atom,4), random_phase)
                # string_x += " %g*np.cos(2*np.pi*x*%g +%g) +" %(amplitudes_x[i], round(freq_atom,4), random_phase)

            else:
                string_x4 += " %g*np.cos(2*np.pi*x*%g +%g) " %(1/len(traps_to_keep4), round(freq_atom,4), random_phase)
                # string_x += " %g*np.cos(2*np.pi*x*%g +%g) " %(amplitudes_x[i], round(freq_atom,4), random_phase)
    
    ### 2 beams string:
    string_x2 = " lambda x: "
    traps_to_keep2 = [2,7]
    for i in range(ntraps_x):
        if i in traps_to_keep2:
            atom_pos = i - int(0.5*ntraps_x)
            freq_atom = (central_freq + atom_pos*freq_to_um_conversion*separation_um)/sampling_rate
            # random_phase = round(random.uniform(0,1)*2*np.pi,3)
            random_phase = random_phase_x[i]
            if (i != traps_to_keep2[-1]):
                string_x2 += " %g*np.cos(2*np.pi*x*%g +%g) +" %(2.0/len(traps_to_keep4), round(freq_atom,4), random_phase)
                # string_x += " %g*np.cos(2*np.pi*x*%g +%g) +" %(amplitudes_x[i], round(freq_atom,4), random_phase)

            else:
                string_x2 += " %g*np.cos(2*np.pi*x*%g +%g) " %(2.0/len(traps_to_keep4), round(freq_atom,4), random_phase)
                # string_x += " %g*np.cos(2*np.pi*x*%g +%g) " %(amplitudes_x[i], round(freq_atom,4), random_phase)




    # # uniformly distributed phases (I. Madjarov thesis, Endres group)
    # string_x = " lambda x: "
    # for i in range(ntraps_x):
    #     atom_pos = i - int(0.5*ntraps_x)
    #     freq_atom = (central_freq + atom_pos*freq_to_um_conversion*separation_um)/sampling_rate
    #     uniform_phase = round(i/ntraps_x*2*np.pi,3)
    #     if (i != ntraps_x -1):
    #         string_x += " %g*np.cos(2*np.pi*x*%g +%g) +" %(1/ntraps_x, round(freq_atom,4), uniform_phase)
    #     else:
    #         string_x += " %g*np.cos(2*np.pi*x*%g +%g) " %(1/ntraps_x, round(freq_atom,4), uniform_phase)

    # string_y = " lambda x: "
    # for i in range(ntraps_y):
    #     atom_pos = i - int(0.5*ntraps_y)
    #     freq_atom = (central_freq + atom_pos*freq_to_um_conversion*separation_um)/sampling_rate
    #     uniform_phase = round(i/ntraps_y*2*np.pi,3)
    #     if (i != ntraps_y -1):
    #         string_y += " %g*np.cos(2*np.pi*x*%g +%g) +" %(1/ntraps_y, round(freq_atom,4), uniform_phase)
    #     else:
    #         string_y += " %g*np.cos(2*np.pi*x*%g +%g) " %(1/ntraps_y, round(freq_atom,4), uniform_phase)



    start()
    ## Add control light:
    is_it_top_control.enable(0.05) # use if you want top control
    utils.jump_from_previous_value(control_aom_power, 0.05, 0.2)# for side use:0.2)#0.2)#0.3)# 2.0) #2.0)
    control_aom_switch.enable(0.05) 

    #spec.add_segment(.1, {0:"lambda x: np.sin(2*np.pi*.1*x/64)",1:"lambda x: np.sin(2*np.pi*.1*x/64)"}, 2**16)
    # spectrum_awg.add_segment(.1, {0:"lambda x: 0",1:"lambda x: 0"}, 32)
    # spectrum_awg.add_segment(.1, {0:"lambda x: np.cos(2*np.pi*x*.32)",
    #                       1:"lambda x: np.cos(2*np.pi*x*.32)"}, 2**20)
    # spectrum_awg.add_segment(.1, {0: string_x, 1:string_y}, N_samples) # (2*np.pi*x*.32) is 40 MHz
    #spectrum_awg.add_segment(.1, {0: string_x4, 1:string_y, 2:string_y, 3:string_y}, N_samples) # (2*np.pi*x*.32) is 40 MHz
    # spectrum_awg.add_segment(.1, {0: string_x4, 1:string_y}, N_samples)
    # spectrum_awg.add_segment(.1, {0: string_x2, 1:string_x4}, N_samples)
    spectrum_awg.add_segment(.1, {0: string_y, 1:"lambda x: 0"}, N_samples)
    load_mot(0, 1)
    # spectrum_awg.add_segment(.5, {0:"lambda x: np.sin(2*np.pi*.4*x/64) * np.heaviside(x-1250, 0.5) + np.sin(2*np.pi*1*x/64) * np.heaviside(-x+1250, 0.5)",
    #                       1:"lambda x: np.sin(2*np.pi*.02*x/64)"}, 2**15) # 125 MHz
    # # for pure EIT
    # spectrum_awg.add_segment(1, {0:"lambda x: np.sin(2*np.pi*.4*x/64)",
    #                       1:"lambda x: np.sin(2*np.pi*.02*x/64)"}, 2**15) # will last 2**15 / (125 MHz) = 262 us 


    

    # two traps for the other segment
    # spectrum_awg.add_segment(.5, {0:"lambda x: 0.5*np.cos(2*np.pi*x*.32 + np.pi/8)+0.5*np.cos(2*np.pi*x*.3224 + np.pi/9)",
    #                       1:"lambda x: 0.5*np.cos(2*np.pi*x*.32 + np.pi/7)+0.5*np.cos(2*np.pi*x*.3224 + np.pi/6)"}, 2**20) # (2*np.pi*x*.32) is 40 MHz
    
    # line of 10 traps for the other segment
    # spectrum_awg.add_segment(.5, {1:"lambda x: 0.1*np.cos(2*np.pi*x*.3104 + np.pi/8.123)+0.1*np.cos(2*np.pi*x*.3128 + np.pi/9.1789) + 0.1*np.cos(2*np.pi*x*.3152 + np.pi/6.789) + 0.1*np.cos(2*np.pi*x*.3176 + np.pi/4.789) + + 0.1*np.cos(2*np.pi*x*.32 + np.pi/3.789) + 0.1*np.cos(2*np.pi*x*.3224 + np.pi/10.789) + 0.1*np.cos(2*np.pi*x*.3248 + np.pi/2.789) + 0.1*np.cos(2*np.pi*x*.3272 + np.pi/5.789) + 0.1*np.cos(2*np.pi*x*.3296 + np.pi/1.789) + 0.1*np.cos(2*np.pi*x*.332 + np.pi/11.789)",
    #                       0:"lambda x: np.cos(2*np.pi*x*.32 + 4.057)"}, 2**20) # (2*np.pi*x*.32) is 40 MHz
    
    # line of 10 traps more random for the other segment
    # spectrum_awg.add_segment(.5, {1:"lambda x: 0.1*np.cos(2*np.pi*x*.306 + 1.575)+0.1*np.cos(2*np.pi*x*.3088 + 5.079) + 0.1*np.cos(2*np.pi*x*.3116 + 2.843) + 0.1*np.cos(2*np.pi*x*.3144 + 1.369) + 0.1*np.cos(2*np.pi*x*.3172 + 5.018) + 0.1*np.cos(2*np.pi*x*.32 + 0.84) + 0.1*np.cos(2*np.pi*x*.3228 + 0.748) + 0.1*np.cos(2*np.pi*x*.3256 + 1.461) + 0.1*np.cos(2*np.pi*x*.3284 + 5.927) + 0.1*np.cos(2*np.pi*x*.3312 + 3.531)",
    #                       0:"lambda x: np.cos(2*np.pi*x*.32 + 4.057)"}, 2**20) # (2*np.pi*x*.32) is 40 MHz


    # single beam at 40MHz:
    # spectrum_awg.add_segment(.5, {0:"lambda x: np.cos(2*np.pi*x*.32)",
    #                       1:"lambda x: np.cos(2*np.pi*x*.32)"}, 2**20) # (2*np.pi*x*.32) is 40 MHz

    # arbitrary position of blue beams:
    # spectrum_awg.add_segment(.5, {0: string_x, 1:string_y}, N_samples) # (2*np.pi*x*.32) is 40 MHz
    #spectrum_awg.add_segment(.5, {0: string_x4, 1:string_y, 2:string_y, 3:string_y}, N_samples) # (2*np.pi*x*.32) is 40 MHz
    # spectrum_awg.add_segment(.5, {0: string_x4, 1:string_y}, N_samples)
    # spectrum_awg.add_segment(.5, {0: string_x2, 1:string_x4}, N_samples)
    spectrum_awg.add_segment(.5, {0: string_y, 1:"lambda x: 0"}, N_samples)


    
    switch_480AODconfig_to_detect.enable(.6)
    switch_480AODconfig_to_detect.disable(.7)


    spectrum_awg.reset(1.5)

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