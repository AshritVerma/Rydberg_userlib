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


from labscriptlib.Rydberg.Prototype_connection_table import cxn_table
if __name__ == '__main__':
    cxn_table()

    start()
    ProtoDev.labscript_sequence_method(["Sequence", "Command"])
    stop(1)