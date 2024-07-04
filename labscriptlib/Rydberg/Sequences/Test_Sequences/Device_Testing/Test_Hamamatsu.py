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
from labscriptlib.Rydberg.Subseqeuences_Utils.Subsequences import *
from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    # Import and define the global variables for devices
    cxn_table()

    hamamatsu.camera_attributes['exposure'] = HC_EXPOSURE
    hamamatsu.camera_attributes['subarrayHsize'] = HC_HSIZE
    hamamatsu.camera_attributes['subarrayVsize'] = HC_VSIZE
    hamamatsu.camera_attributes['subarrayHpos'] = HC_HPOS
    hamamatsu.camera_attributes['subarrayVpos'] = HC_VPOS
    hamamatsu.camera_attributes['subarrayMode'] = 2

    delay = 10e-3*4
    start()
    t=0
    t+=10e-3
    
    t+= load_mot(t, 1e-3)

    hamamatsu.expose(t, name="absorption", frametype='atoms', trigger_duration=100e-6)
    t+=HC_EXPOSURE

    t+=500e-3

    hamamatsu.expose(t, name="absorption", frametype='atoms', trigger_duration=100e-6)
    t+=HC_EXPOSURE

    t+=1e-3


    stop(t)

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
