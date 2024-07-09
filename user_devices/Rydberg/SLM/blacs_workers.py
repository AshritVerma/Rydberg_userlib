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

import socket
import labscript_utils.h5_lock  # Must be imported before importing h5py.
import pickle
import h5py
import numpy as np
from labscript.labscript import set_passed_properties
from blacs.tab_base_classes import Worker
import pickle
import time
"""idea #1: use asyncio for asynch communication
"""
import asyncio
"""idea #2: use msgpack for serialization instead
# replace msgpack.packb with msgpack.packb(data)
# replace pickle.loads with msgpack.unpackb(data)
"""
import msgpack 

class SLMWorker(Worker):

    def init (self):
        # Once off device initialisation code called when the
        # worker process is first started .
        # Usually this is used to create the connection to the
        # device and/or instantiate the API from the device
        # manufacturer

        self.HOST = self.ip_address  # The server's hostname or IP address
        self.PORT = 42069  # The port used by the server

        print("Connecting {} @ port {}...".format(self.HOST, self.PORT))

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.HOST, self.PORT))
        
        # how to separate different arguments that we send over IP
        self.sep = b'\n\n\n\n\n'
        self.command_dictionary = {
            "add_zernike": b'0' + self.sep,
            "one_trap": b'1' + self.sep,
            "two_traps": b'2' + self.sep
        }

        self.old_zernike_array = None

        print("Connected!")        
    
    def shutdown(self):
        # Once off device shutdown code called when the
        # BLACS exits
        self.connection.close()


    def program_manual ( self , front_panel_values ):
        # Update the output state of each channel using the values
        # in front_panel_values ( which takes the form of a
        # dictionary keyed by the channel names specified in the
        # BLACS GUI configuration
        # return a dictionary of coerced / quantised values for each
        # channel , keyed by the channel name (or an empty dictionary )
        return {}
     
    async def transition_to_buffered(self, device_name, h5_file_path, initial_values, fresh):
    #def transition_to_buffered ( self , device_name , h5_file, initial_values , fresh ):
        # Access the HDF5 file specified and program the table of
        # hardware instructions for this device .
        # Place the device in a state ready to receive a hardware
        # trigger (or software trigger for the master pseudoclock )
        #
        # The current front panel state is also passed in as
        # initial_values so that the device can ensure output
        # continuity up to the trigger .
        #
        # The fresh keyword indicates whether the entire table of
        # instructions should be reprogrammed (if the device supports
        # smart programming )
        # Return a dictionary , keyed by the channel names , of the
        # final output state of the shot file . This ensures BLACS can
        # maintain output continuity when we return to manual mode
        # after the shot completes .

        self.h5_filepath = h5_file
        self.device_name = device_name

        with h5py.File(self.h5_filepath, 'r') as hdf5_file:
            
            devices = hdf5_file['devices'][device_name]
            self.zernike_array = list(devices['zernike_array'])
            self.set_zernike = devices.attrs['set_zernike']
    
            self.n_traps = devices.attrs['n_traps']

            # one trap
            if self.n_traps == 1:
                
                data_string = self.command_dictionary['one_trap']
                data_string +=  b"shiftx" + self.sep + msgpack.packb(devices.attrs['shiftx'])
                data_string +=  self.sep + b"shifty" + self.sep + msgpack.packb(devices.attrs['shifty'])
                # data_string +=  b"line_sp\n\n" + msgpack.packb(devices.attrs['line_sp']) 
                
                print('Setting one trap: {}'.format(data_string))

                self.connection.send(data_string)
                return_string = self.connection.recv(2048)
                print(return_string)
                if not return_string:
                    raise Exception("One trap was not generated.")

            # two traps
            elif self.n_traps == 2:
                
                data_string = self.command_dictionary['two_traps'] 
                data_string +=  b"target_sep" + self.sep + msgpack.packb(devices.attrs['target_sep']) 
                data_string +=  self.sep + b"alpha" + self.sep + msgpack.packb(devices.attrs['alpha'])
                data_string +=  self.sep + b"shiftx" + self.sep + msgpack.packb(devices.attrs['shiftx'])
                data_string +=  self.sep + b"shifty" + self.sep + msgpack.packb(devices.attrs['shifty'])

                print('Setting two traps: {}'.format(data_string))

                #self.connection.send(self.command_dictionary['add_zernike'])
                self.connection.send(data_string)
                return_string = self.connection.recv(2048)
                print(return_string)
                if not return_string:
                    raise Exception("Two traps were not generated")

        # Only set if the new array is not empty and is different from the old array
        if self.set_zernike and self.zernike_array != self.old_zernike_array:

            print('Setting Zernike Coefficients: {}'.format(self.zernike_array))
            
            data_string = self.command_dictionary['add_zernike'] 
            data_string +=  b"coeffs" + self.sep + msgpack.packb(self.zernike_array) 
            print(data_string)
            #self.connection.send(self.command_dictionary['add_zernike'])
            self.connection.send(data_string)
            return_string = self.connection.recv(2048)
            print(return_string)
            if not return_string:
                raise Exception("The SLM Zernikes do not seem to have been set! :o")

            self.old_zernike_array = self.zernike_array

        
        
        tasks = []
        for command in command_list:
            tasks.append(self.send_command(command, data))
        return_strings = await asyncio.gather(*tasks)
        
        final_values = {}
        return final_values
    
    async def send_command(self, command, data):
        self.connection.sendall(command + data)
        return await self.connection.recv(2048)


    def transition_to_manual ( self ):
        # Called when the shot has finished , the device should
        # be placed back into manual mode
        # return True on success

        return True

    def abort_transition_to_buffered ( self ):
        # Called only if transition_to_buffered succeeded and the
        # shot if aborted prior to the initial trigger
        # return True on success
        return True
    def abort_buffered ( self ):
        # Called if the shot is to be abort in the middle of
        # the execution of the shot ( after the initial trigger )
        # return True on success
        return True

