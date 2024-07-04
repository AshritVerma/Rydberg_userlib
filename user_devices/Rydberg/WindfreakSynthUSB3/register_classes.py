#####################################################################
#                                                                   #
# Copyright 2019, Monash University and contributors                #
#                                                                   #
# This file is part of labscript_devices, in the labscript suite    #
# (see http://labscriptsuite.org), and is licensed under the        #
# Simplified BSD License. See the license.txt file in the root of   #
# the project for the full license.                                 #
#                                                                   #
#####################################################################
from labscript_devices import register_classes

register_classes(
    'WindfreakSynthUSB3',
    BLACS_tab='user_devices.Rydberg.WindfreakSynthUSB3.blacs_tabs.WindfreakSynthUSB3Tab',
    runviewer_parser=None,
)
