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
#!/usr/bin/env python3

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

import socket
import pickle
import time
import cv2

"""idea #3: asynch handling of connections

"""
import asyncio

"""idea #4: numpy is faster for array operations
import numpy as np
# replace list operations with numpy operations, if possible
"""

from slm_utils.devices_attr import SLMx13138
from slm_utils import slmpy_updated as slmpy
from slm_utils import freq_funcs

MONITOR_ID = 1 # configuration frequently changes when computer restarts and if there are many monitors
SEPARATOR = b"\n\n\n\n\n"
TESTING_SLM = False # if true, then we are testing the server/SLM code so we do not check the monitor size

MOD_BIT_DEPTH = 255. # intensity to modulation depth functions are calibrated for this depth

effective_trap_waist = np.linspace(1.83e-6, 10e-6, 5)
wavelength = 808e-9
focal_length = 10e-3

effective_fourier_waist = wavelength*focal_length/(np.pi*effective_trap_waist)

# reproduce the inverted dictionary of functions defined in labscript
# every time a command is sent, the whole script runs. so need to be careful that the phases are not being added many times
command_dict = {
    b'0': 'set_zernike',
    b'1': 'one_trap',
    b'2': 'two_traps',
    b'3': 'array_traps',
    # not related to the intrinsic phase pattern itself
    b'a': 'add_wf_correction',
    b'b': 'add_bob_circle',
    # b'c': 'clip_circle',
    b'c': 'clip_circle_greyscale',
    b'z': '_return'
}

n_items = 3
rand_kernel1 = np.random.rand(n_items)
rand_kernel2 = np.random.rand(n_items)

"""
In the slm_server.py file, you would replace the existing main loop with an asynchronous version. Here's how you can restructure the file to incorporate the async def handle_client function:
pythonCopyimport asyncio
import socket
import pickle
# ... other imports ...

# ... existing command_dict and other global variables ...

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connect {addr}")

    slm_win = slmpy.SLMdisplay(isImageLock=False, monitor=MONITOR_ID)
    slm_attr = SLMx13138()

    try:
        while True:
            data = await reader.read(2048)
            if not data:
                break

            split_data = data.split(SEPARATOR)
            command_byte = split_data[0]

            print(f"Command byte: {command_byte}")

            # ... rest of your command processing logic ...

            if command_byte == b"z":
                # ... your existing 'z' command logic ...
                await writer.write(b"Updated phase pattern.")
                await writer.drain()

            await writer.write(b" -> Waiting for next command...")
            await writer.drain()

    except asyncio.CancelledError:
        print("Connection cancelled")
    finally:
        print(f"Closing connection to {addr}")
        slm_win.close()
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(
        handle_client, HOST, PORT)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())

print("SLM server ended")
"""


def main():
    HOST = '192.168.10.104'  # Standard loopback interface address (localhost)
    PORT = 42069  # Port to listen on (non-privileged ports are > 1023)

    s = socket.socket()
    s.bind((HOST, PORT))

    s.listen(1)
    while True:

        conn, addr = s.accept()
        print("Connect" + str(addr))

        # create a display window on SLM
        slm_win = slmpy.SLMdisplay(isImageLock=False, monitor=MONITOR_ID)
        
        # create the SLM device class, get phase pattern for the default trap position
        slm_attr = SLMx13138()

        try:

            while True:
                
                data = conn.recv(2048)

                # separator is \n\n\n\n\n because sometimes there are \n\n\n characters in the data
                split_data = data.split(SEPARATOR)

                command_byte = split_data[0]

                print("Command byte: " + str(command_byte))
                if not command_byte:
                    break
                
                # assume even, odd elements in remaining data are alternating argument names and values
                args = split_data[1::2]
                vals = split_data[2::2]

                args = [element.decode("utf-8") for element in args]
                vals = [pickle.loads(val) for val in vals]

                # save arguments to functions as a dictionary
                kwargs = dict(zip(args, vals))
                print(kwargs)

                # execute the command
                try:
                    command_function = getattr(slm_attr, command_dict[command_byte])
                    command_return = command_function(**kwargs)

                except KeyError:
                    raise ValueError("Invalid input command.")

                # if adding zernike coefficients, update the current zernike pattern
                # else, update the current phase pattern
                # if command_byte == b"0":
                #     print("Updating the Zernike pattern.")
                    
                #     # update existing zernike pattern
                #     slm_attr.curr_zernike_pattern = command_return.copy()
                
                # if command_byte == b"a":
                #     print("Adding wf correction pattern")
                #     slm_attr.corr_pattern_rad = command_return.copy()

                if command_byte == b"b":
                    print("Adding BOB central circle with pi phase shift")
                    slm_attr.curr_bob_phase = command_return.copy()
                    
                elif command_byte == b"c":
                    print("Updating the clipping mask radius.")

                    # update the mask. assume everything is normalized such that we are using the full modulation depth
                    slm_attr.curr_mask = command_return.copy()

                # reset vars at the end of this script
                elif command_byte == b"z":
                    pass

                else:
                    print("Updating the current phase pattern.")

                    # update the ccurrent phase pattern
                    slm_attr.curr_phase_pattern = command_return.copy()

                ### done updating all the parameters for SLM phase pattern
                if command_byte == b"z":
                    '''
                    This command byte signals that all the commands for a given shot are completed.
                    Here, it is necessary to reset variables that are used via checking if they are not none
                    The way that things are set up: we send the command string if we want to add a certain phase pattern (e.g. clipping or BOB), 
                    but if we want to turn it off for the next shot then it wouldn't work since it is not None.
                    This needs to occur after updateArray() has been executed so that it will stay on the SLM.
                    '''
                    print("Completed commands. Now send to SLM")

                    # phase_rad is the only main local variable, and not an attribute of slm_attr
                    # set the phase pattern to the current phase pattern defined in slm_attr.
                    phase_rad = slm_attr.curr_phase_pattern.copy()

                    if slm_attr.curr_zernike_pattern is not None:
                        phase_rad += slm_attr.curr_zernike_pattern


                    # # # # # # # # # # # # # # # # # # # set the phase pattern by hand
                    # try:
                    #     # filename = r'Z:\Calculations\Emily\SLM project\v4_array_patterns\triangular\2022_04_26-16_10__nxt=05_nyt=05_sepx=8.000_sepy=7.000_offx=93.09_offy=-93.09.pkl'
                    #     # filename = r'Z:\Calculations\Emily\SLM project\v4_array_patterns\hexagonal\2022_04_26-18_26__nxt=07_nyt=08_sepx=16.000_sepy=14.000_offx=93.09_offy=-93.09.pkl'
                    #     # filename = r'Z:\Calculations\Emily\SLM project\v4_array_patterns\arb\2022_04_26-19_16__mit_86traps.pkl'
                    #     # filename = r'Z:\Calculations\Emily\SLM project\v4_array_patterns\2022_05_06-18_12__nxt=01_nyt=10_sepx=12.000_sepy=12.000_offx=93.09_offy=-93.09.pkl'
                    #     # filename = r'Z:\Calculations\Emily\SLM project\v4_array_patterns\arb\2022_04_27-12_15__cua_70traps_xt+20.pkl'
                    #     #2022_04_27-12_15__cua_70traps_xt+20.pkl
                    #     # alignment of side image
                    #     filename = r'Z:\Calculations\Emily\SLM project\v4_array_patterns\2022_05_06-18_12__nxt=10_nyt=01_sepx=12.000_sepy=12.000_offx=93.09_offy=-93.09.pkl'
                    #     phase_rad = freq_funcs.pkread(filename)
                    # except:
                    #     raise ValueError("can't read the array file")
                    # # # # # # # # # # # # # # # # #          
                    

                    # # # # # # # # # # # # # # # # # add speckle
                    # create_speckle(self, mod_depth, px_offs_x, px_offs_y, period_x, period_y)

                    # mod_depth = [np.pi/10]*n_items
                    # # px_offs_x = slm_attr.n*rand_kernel1 # rand draws from uniform distribution over [0,1)
                    # # px_offs_y = slm_attr.n*rand_kernel2

                    # # # set 1
                    # # px_offs_x = np.array([90.97112728, 263.9801162, 401.19512256])
                    # # px_offs_y = np.array([5.57276052e-01, 5.96187789e+02, 9.45039227e+01])

                    # # set 2
                    # px_offs_x = np.array([548.67282229, 933.5039829,   94.07823488])
                    # px_offs_y = np.array([342.69882484, 168.53486977, 342.16711963])

                    # # print(px_offs_x)
                    # # print(px_offs_y)

                    # # # to change with n_items
                    # # period_x = [slm_attr.n]
                    # period_x = [slm_attr.n, 2*slm_attr.n/3, slm_attr.n/2]
                    # period_y = period_x.copy()

                    # # on top of trap
                    # phase_rad += slm_attr.create_speckle(mod_depth, px_offs_x, px_offs_y, period_x, period_y)
                    
                    # # no trap, only speckle
                    # # phase_rad = slm_attr.create_speckle(mod_depth, px_offs_x, px_offs_y, period_x, period_y)

                    # # # # # # # # # # # # # # # # # 

                    # # # # # # # # # # # # # # # # # 
                    # at this point, we are done adding all "variable" phases. 
                    # only wf corrections and clipping from here onwards.
                    # after padding zeros, note that the phase pattern has the size of the monitor (NOT the size of SLM!!!)
                    phase_rad = slm_attr.pad_zeros(slm_attr.pad_square_pattern(phase_rad))
                    
                    # # wf correction in units of radians
                    # if slm_attr.corr_pattern_rad is not None:
                    #     phase_rad += slm_attr.corr_pattern_rad
                    #     print('adding wf correction')

                    # do it by hand so that it is not changing when it is read as a command from labscript
                    # wf_corr_file = r'Z:\2022-data\2022-04\20220415-wf_correction\11_47_modesz=64_probesz=2\unwrapped_fitted.npy'
                    
                    ########################
                    wf_corr_file = r'Z:\VV Rydberg lab\2023-data\2023-01\20230110-wf_correction\20_59_modesz=64_probesz=3\unwrapped_fitted.npy'
                    ########################

                    ## did not remove saturated points
                    # wf_corr_file = r'Z:\2023-data\2023-01\20230113-wf_correction\15_49_modesz=64_probesz=3\unwrapped_fitted_nofiltering.npy'
                    # wf_corr_file = r'Z:\2023-data\2023-01\20230113-wf_correction\15_49_modesz=64_probesz=3\unwrapped_fitted.npy'

                    # ######### (jan 16, 2023) fixed fitting
                    # wf_corr_file = r'Z:\2023-data\2023-01\20230115-wf_correction\15_55_modesz=64_probesz=3\unwrapped_fitted.npy'
                
                    wf_kwargs = {'wf_corr_file': wf_corr_file}

                    phase_rad += slm_attr.pad_zeros(slm_attr.pad_square_pattern(slm_attr.add_wf_correction(**wf_kwargs)))
                    # phase_rad += slm_attr.add_wf_correction(**wf_kwargs) # (april 15, 2022)

                    # add phase shift for the BOB traps
                    if slm_attr.curr_bob_phase is not None:
                        # # turning off center bob
                        # phase_rad *= slm_attr.curr_bob_phase

                        phase_rad += slm_attr.curr_bob_phase
                        print('adding BOB phase')

                    # # (April 3): we apply a greyscale mask (calculated from intensity distribution) on the square array
                    if slm_attr.curr_mask is not None:
                        slm_attr.curr_mask = slm_attr.pad_zeros(slm_attr.pad_square_pattern(slm_attr.curr_mask))
                        phase_int8 = slm_attr.convert_bmp(phase_rad, bit_depth = slm_attr.curr_mask)
                        
                        # plt.figure()
                        # plt.imshow(phase_int8)
                        # plt.colorbar()
                        # plt.show()
                    else:
                        # convert to bitmap
                        # phase_int8 = slm_attr.convert_bmp(phase_rad)
                        phase_int8 = slm_attr.convert_bmp(phase_rad, bit_depth = 255.)
                    
    
                    slm_win.updateArray(phase_int8, check_img_size=not TESTING_SLM)

                    conn.send(b"Updated phase pattern.")
                    slm_attr.reset_dynamic_vars()
                
                # print('Continue')
                conn.send(b" -> Waiting for next command...")

        except ConnectionResetError:
            print("connection lost; resetting")

            conn.close()
            slm_win.close()
        
        conn.close()
        slm_win.close()

    s.close()

if __name__ == '__main__':
    main()

print("SLM server ended")
