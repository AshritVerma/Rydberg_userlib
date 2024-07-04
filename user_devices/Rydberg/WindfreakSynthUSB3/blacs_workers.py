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

from collections import defaultdict
import time

import labscript_utils.h5_lock  # Must be imported before importing h5py.
import h5py
from matplotlib.pyplot import pause #i don't think this is even needed here - ashrit
import numpy as np
from labscript.labscript import set_passed_properties
import time

import pyvisa
from pyvisa.constants import StopBits, Parity

from blacs.tab_base_classes import Worker


class WindfreakSynthUSB3Worker(Worker):

    def init(self):
        # Once off device initialisation code called when the
        # worker process is first started .
        # Usually this is used to create the connection to the
        # device and/or instantiate the API from the device
        # manufacturer
        #global pyvisa; import pyvisa
        
        print(f"Initializing WindFreakSynthUSB3 worker with COM port: {self.com_port}")
        #print("Connecting to Windfreak Technologies RF Signal Generator")

        rm = pyvisa.ResourceManager('@py')
        print(f"Available resources: {rm.list_resources()}")

        """
        
        # start up the serial connection
        visa_address = self.com_port #'USB0::0x0AAD::0x006E::101266::INSTR'
        self.connection = rm.open_resource(visa_address)
        self.connection.write("*CLS") # clear any errors from before 
        """

        """
         # start up the serial connection
        visa_address = "GPIB0::%d::INSTR" % self.com_port # address 6 
        self.connection = rm.open_resource(visa_address)
        self.connection.write("*CLS") # clear any errors from before 
        """
       
        # Use the COM port directly for USB communication
        visa_address = f'ASRL{self.com_port}::INSTR'
        print(f"Attempting to connect to: {visa_address}")
        
        try:
            self.connection = rm.open_resource(visa_address)
            print("Successfully connected to the device")
        except pyvisa.errors.VisaIOError as e:
            print(f"Failed to connect to the device. Error: {str(e)}")
            raise
        
        """
        # Set appropriate settings for USB serial communication (may not be written, or automatically rewritten dependdingon i/o device api but good to have anyways esp. buffer clear for speed)
        try:
            self.connection.baud_rate = 115200  # Set the baud rate to match your device
            self.connection.data_bits = 8
            self.connection.stop_bits = pyvisa.constants.StopBits.one
            self.connection.parity = pyvisa.constants.Parity.none
            self.connection.flow_control = pyvisa.constants.ControlFlow.none
        except pyvisa.errors.VisaIOError as e:
            print(f"Warning: Could not set all serial parameters. Error: {str(e)}")
            print("continuing with default setting...")
        """
        

        # Clear any previous errors and check communication
        try:
            self.connection.write("?")
            time.sleep(0.1)  # Give the device some time to respond
            response = self.connection.read()
            print(f"Device response: {response}")
        except Exception as e:
            print(f"Warning: Error in initial communication. Error: {str(e)}")

        print("Initialization complete.")


    def send_commands(self, commands):
        responses = []
        for command in commands:
            try:
                self.connection.write(command + "\n")  # Add newline character
                time.sleep(0.1)  # Allow time for the command to be processed
                
                # Try to read the response, but don't wait too long
                try:
                    response = self.connection.read()
                except pyvisa.errors.VisaIOError as e:
                    if e.error_code == pyvisa.constants.StatusCode.error_timeout:
                        response = "Timeout: No response from device"
                    else:
                        raise
                
                responses.append(response)
            except Exception as e:
                print(f"Error sending command '{command}': {str(e)}")
                responses.append(f"Error: {str(e)}")

        # Join all responses into a single string
        return "; ".join(responses)
    
    def shutdown ( self ):
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
    def transition_to_buffered ( self , device_name , h5_file_path,
    initial_values , fresh ):
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

        # self.h5_filepath = h5_file
        # self.device_name = device_name

        # From the H5 sequence file, get the sequence we want programmed into AWG and command it
        with h5py.File(h5_file_path, 'r') as hdf5_file:
            
            devices = hdf5_file['devices'][device_name]

            command_list = devices['command_list']
            command_list = [n.decode('utf-8') for n in command_list]

            self.send_commands(command_list)


        final_values = {}
        return final_values


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
    
    

