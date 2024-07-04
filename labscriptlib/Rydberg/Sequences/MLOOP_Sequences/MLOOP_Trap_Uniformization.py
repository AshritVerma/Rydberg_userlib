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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import image_cmot, load_mot, compress_mot, reset_mot, zero_B_fields, reshape_dt, hold_dt, slm_set_zernike, image_cmot_cut,image_dt, setup_slm
from labscriptlib.Rydberg.Subseqeuences_Utils.MLOOP_Subsequences import mloop_hold_dt, mloop_compress_mot, mloop_reshape_dt
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table
import numpy as np

if __name__ == '__main__':

  # Import and define the global variables for devices
    cxn_table()

    #slm_set_zernike()

    t=0

######## Make strings for prep in one detect in other state:   
    ntraps_x = 10
    ntraps_y = 1 #10
    separation_um = 10 #5 #20 #5 #10
    sampling_rate = 125 # in MHz
    central_freq = 40 # in MHz
    time_to_be_on = 200 #200 # in us
    freq_to_um_conversion = 0.0344 # MHz/um

    N_samples = time_to_be_on*sampling_rate
    ### 4 beams string:
    random_phase_x = [MLOOP_CONTROL_PHASE0, MLOOP_CONTROL_PHASE1,MLOOP_CONTROL_PHASE2,MLOOP_CONTROL_PHASE3,MLOOP_CONTROL_PHASE4,MLOOP_CONTROL_PHASE5,MLOOP_CONTROL_PHASE6,MLOOP_CONTROL_PHASE7,MLOOP_CONTROL_PHASE8,MLOOP_CONTROL_PHASE9]
    random_amp_x = [MLOOP_CONTROL_AMP0, MLOOP_CONTROL_AMP1,MLOOP_CONTROL_AMP2,MLOOP_CONTROL_AMP3,MLOOP_CONTROL_AMP4,MLOOP_CONTROL_AMP5,MLOOP_CONTROL_AMP6,MLOOP_CONTROL_AMP7,MLOOP_CONTROL_AMP8,MLOOP_CONTROL_AMP9]
    random_amp_x = np.array(random_amp_x) / np.sum(random_amp_x)
    random_phase_y = [1.258]


    string_x10 = " lambda x: "
    traps_to_keep10 = range(ntraps_x)
    for i in range(ntraps_x):
        if i in traps_to_keep10:
            atom_pos = i - int(0.5*ntraps_x)
            freq_atom = (central_freq + atom_pos*freq_to_um_conversion*separation_um)/sampling_rate
            # random_phase = round(random.uniform(0,1)*2*np.pi,3)
            random_phase = random_phase_x[i]
            if (i != traps_to_keep10[-1]):
                string_x10 += " %g*np.cos(2*np.pi*x*%g +%g) +" %(random_amp_x[i], round(freq_atom,4), random_phase)
                # string_x += " %g*np.cos(2*np.pi*x*%g +%g) +" %(amplitudes_x[i], round(freq_atom,4), random_phase)

            else:
                string_x10 += " %g*np.cos(2*np.pi*x*%g +%g) " %(random_amp_x[i], round(freq_atom,4), random_phase)
                # string_x += " %g*np.cos(2*np.pi*x*%g +%g) " %(amplitudes_x[i], round(freq_atom,4), random_phase)
    

    


    t=0

    start()

    spectrum_awg.add_segment(.001, {0: string_x10, 1:string_x10}, N_samples) # (2*np.pi*x*.32) is 40 MHz
    t+=0.003

    spectrum_awg.add_segment(t, {0: string_x10, 1:string_x10}, N_samples) # (2*np.pi*x*.32) is 40 MHz
    
    t+= load_mot(t, .1)
    #t+=50e-3
    is_it_top_control.enable(t)
    control_aom_switch.enable(t)
    utils.jump_from_previous_value(control_aom_power, t, 0.5)
    lucid.expose(t, 'beams', trigger_duration=50e-6)
    t+=10e-3
    spectrum_awg.reset(t)
    t += reset_mot(t)

    stop(t)