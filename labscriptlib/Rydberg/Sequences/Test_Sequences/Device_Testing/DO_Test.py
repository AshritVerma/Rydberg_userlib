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

import numpy as np
from labscript import (
    start,
    stop,
)

import labscript as lab


from labscriptlib.Rydberg.Rydberg_connection_table import cxn_table

if __name__ == '__main__':

    cxn_table()

    start()

    do_test.go_high(0)
    do_test.go_low(1)
    do_test.go_high(2)
    do_test.go_low(3)
    




    stop(5)