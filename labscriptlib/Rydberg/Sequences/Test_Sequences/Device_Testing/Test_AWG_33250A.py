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

# This script is to test the analog output and Arduino dds controller

import numpy as np
from labscript import (
    start,
    stop,
)

import time
import labscript as lab
# from labscript_utils import import_or_reload
#
# # Connection_Table
#
# import_or_reload(r"C:\Users\12566\PycharmProjects\SineWaveTest\SineWaveCxnTable.py")

import labscriptlib.Rydberg.Subseqeuences_Utils.Sequence_Utils as utils
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import *

if __name__ == '__main__':
    cxn_table()
    rate = 1e6

    #start_time += 6e-3
    #lab.add_time_marker(start_time, marker_name)
    #agilent_awg2.program_gated_sine(1e5,0.2,0.000)
    #agilent_awg2.program_square_pulse(0.2,100e-6,99e-6)
    #agilent_awg2.program_DC(0.2)
    #agilent_awg2.program_gated_TTL2(0.2)
    #wf_time = 5e-6
    #wfm = np.array([0.0] + list(np.ones(400)*0.2) + 1*[0.0])
    #agilent_awg2.send_wf(total_time=wf_time,voltages=wfm)
    agilent_awg2.program_gated_TTL(0.2,2e-6,1000)

    # For some reason this is required to make the PB trigger
    #pb_digital_out.go_high(0)

    t=0.0
    start()

    t+= load_mot(t, 0.1)
    #least.go_high(0)
    #most.go_high(0)

    #utils.jump_from_previous_value(big_x_coil, t+1e-3, 0.0)
    #agilent_awg2.program_DC(0.2) #V
     #Vhigh,width,freq
    #agilent_awg2.program_square_pulse(Vhigh=0.2,width=1e-2,period=1)
    
    #agilent_awg2.program_arb_test(np.linspace(0.0,0.1,100),0,0.4,1e-5,50)

    #agilent_awg2.arb(2e-4, 0.1, load = 1000.0)
    #agilent_awg2.sample_control_wf

    #def arb(self,total_time, voltages, load = 1000.0):

    #program_arb_test(self,wf_data,Vmin,Vmax,ttot, load, ncycles=1):


    #t += 1e-6
    agilent_awg2.trigger(t+1e-3, duration=10e-6)

        #def program_square_pulse(self,Vhigh,period,width,edge):
        #"""set the Vhigh, period, pulse width and edge to make square pulse

    #agilent_awg2.program_DC(0.0) #V

    t = t+1
    stop(t+1)