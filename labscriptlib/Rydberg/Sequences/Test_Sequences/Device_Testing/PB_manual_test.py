from spinapi import *
import numpy as np
from ctypes import *

PULSE_PROGRAM = 0
CONTINUE = 0
STOP = 1
LOOP = 2
END_LOOP = 3
JSR = 4
RTS = 5
BRANCH = 6
LONG_DELAY = 7
WAIT = 8
RTI = 9


print(pb_count_boards())
# spinapi.pb_set_clock(c_double(250))
# spinapi.pb_core_clock(c_double(250))
# spinapi.pb_set_debug(c_uint(1))

# print("Starting programming... ")

# spinapi.pb_stop()

# # Write the first two lines of the pulse program:

# spinapi.pb_start_programming(c_int(PULSE_PROGRAM))
# flags = 0xFFFFFF
# # Line zero is a wait:
# print(spinapi.pb_inst_pbonly(c_uint(flags), CONTINUE, 0, c_double(100)))
# # Line one is a branch to line 0:
# #print(spinapi.pb_inst_pbonly(c_uint(0xFFFFFE),BRANCH, 0, c_double(100)))
# print(spinapi.pb_get_error())
# spinapi.pb_stop_programming()

# # Now we're waiting on line zero, so when we start() we'll go to
# # line one, then brach back to zero, completing the static update:
# spinapi.pb_start()

# RESETS NOT PART OF LABSCRIPT
# pb_select_board(0)
# pb_init()
# pb_core_clock(250)
# pb_stop()

                

# flags = '000000000000000000000000'
# # Write the first two lines of the pulse program:
# pb_start_programming(PULSE_PROGRAM)
# # Line zero is a wait:
# pb_inst_pbonly(flags, WAIT, 0, 100)
# # Line one is a brach to line 0:
# pb_inst_pbonly(flags, BRANCH, 0, 100)
# pb_stop_programming()
# pulse_program = np.array([
#     (0b111111111111111111111111, 0, 0, 1.00e+07), 
#     #(0, 0, 0, 9.98e+08), 
#     #(0, 0, 0, 4.00e+01),
#     (0, BRANCH, 0, 4.00e+01)],
#       dtype=[('flags', '<i4'), ('inst', '<i4'), ('inst_data', '<i4'), ('length', '<f8')])
# #Write the first two lines of the pulse program:
# pb_start_programming(PULSE_PROGRAM)
# pb_inst_pbonly(0,WAIT,0,100)
# pb_inst_pbonly('000000000000000000000000', CONTINUE, 0, 100)
# for args in pulse_program:
#     pb_inst_pbonly(*args)
# pb_stop_programming()
# # pb_start()
# spinapi = CDLL("spinapi64.dll")
# spinapi.pb_select_board(0)
# spinapi.pb_init()
# spinapi.pb_set_clock(c_double(250))
# #spinapi.pb_stop()
# spinapi.pb_start_programming(c_int(PULSE_PROGRAM))
# spinapi.pb_inst_pbonly(c_int(16777215), 0, 0, c_double(50e6))
# wait_add = spinapi.pb_inst_pbonly(c_uint(0), WAIT, 0, c_double(100e6))
# loop_add = spinapi.pb_inst_pbonly(c_uint(16777215), LOOP, c_int(2), c_double(50e6))
# spinapi.pb_inst_pbonly(c_uint(0), LONG_DELAY, c_int(7), c_double(25e6) )
# spinapi.pb_inst_pbonly(c_uint(0), BRANCH, wait_add, c_double(22e6))
# #spinapi.pb_inst_pbonly(c_uint(0), CONTINUE, c_uint(0), c_double(100))
# # spinapi.pb_inst_pbonly(c_int(16777215), 0, 0, c_double(50))
# # branch_ret = spinapi.pb_inst_pbonly(c_int(16777215), WAIT, 0, c_double(100))
# # spinapi.pb_inst_pbonly(c_uint(0), LOOP, c_int(8), c_double(1e6))
# # spinapi.pb_inst_pbonly(c_uint(16777215), LOOP, c_int(8), c_double(1e6))
# # spinapi.pb_inst_pbonly(c_uint(0), LOOP, c_int(8), c_double(1e6))
# # spinapi.pb_inst_pbonly(c_uint(0), LONG_DELAY, c_int(7), c_double(250) )
# # spinapi.pb_inst_pbonly(c_uint(0), BRANCH, branch_ret, c_double(22))
# #spinapi.pb_inst_pbonly(c_uint(0), 0, c_uint(0), c_double(1e9))
# #spinapi.pb_inst_pbonly(c_uint(0), BRANCH, c_uint(0), c_double(4e5))
# spinapi.pb_stop_programming()
# spinapi.pb_start()
