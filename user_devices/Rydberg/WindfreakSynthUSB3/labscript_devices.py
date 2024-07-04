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

from labscript import IntermediateDevice
from labscript.labscript import  set_passed_properties
#import numpy as np

class WindfreakSynthUSB3(IntermediateDevice):

    # A human readable name for device model used in error messages
    description = "Windfreak Technologies RF Signal Generator"
    # The labscript Output classes this device supports
    allowed_children = [ ]
    # The maximum update rate of this device (in Hz)
    
    clock_limit = 1e3 ### update this #Cs lab using 1e4 a value

    @set_passed_properties(
        property_names={
            'connection_table_properties':
                [
                    'name',
                    'com_port', # USB address 
                ]
        }
    )
    
    def __init__ ( self, name, parent_device, com_port, **kwargs):
        """initialize the device

        Args:
            name (str): name of device
            parent_device (None): None
            com_port (str): USB com port address 
        """
        IntermediateDevice.__init__ (self, name, parent_device)
        self.BLACS_connection = "Windfreak Technologies RF Signal Generator {}".format(com_port)
        self.name = name
        self.command_list = []
    
    def generate_code(self, hdf5_file):
        """Write the command sequence to the HDF fi le

        Args:
            hdf5_file (hdf): labscript hdf file
        """ 
        IntermediateDevice.generate_code(self, hdf5_file)
        grp = hdf5_file.require_group(f'/devices/{self.name}/')
        dset = grp.require_dataset('command_list', (len(self.command_list),), dtype='S30')
        dset[:] = [n.encode("ascii", "ignore") for n in self.command_list]

    def set_frequency(self, freq):
        # Set frequency in MHz
        self.command_list.append(f"f{freq:.8f}")

    def set_power(self, power):
        # Set power in dBm
        self.command_list.append(f"W{power:.3f}")

    def enable_output(self, state):
        # Enable (1) or disable (0) the PLL output
        self.command_list.append(f"E{1 if state else 0}")

    def set_reference(self, source):
        # Set reference source: external (0) or internal 27MHz (1)
        self.command_list.append(f"x{1 if source == 'internal' else 0}")

    def set_sweep(self, start_freq, stop_freq, step_size, step_time):
        # Set up a frequency sweep
        self.command_list.extend([
            f"l{start_freq:.8f}",
            f"u{stop_freq:.8f}",
            f"s{step_size:.8f}",
            f"t{step_time:.3f}"
        ])

    def run_sweep(self, continuous=False):
        # Start a sweep (continuous or single)
        self.command_list.extend([
            f"c{1 if continuous else 0}",
            "g1"
        ])
    
    def stop_sweep(self):
        self.command_list.append("g0")

    def set_am_modulation(self, freq, on_time):
        # Set up amplitude modulation
        self.command_list.extend([
            f"F{on_time}",
            f"A1"
        ])
        # Note: Setting up the AM lookup table is more complex and may require additional methods

    def set_fm_modulation(self, freq, deviation):
        # Set up frequency modulation
        self.command_list.extend([
            f"<{freq}",
            f">{deviation}",
            "/1"
        ])

    def save_settings(self):
        # Save current settings to EEPROM
        self.command_list.append("e")

    """legacy function"""
    """
    def set_freq_amp(self, freq, amp):
        Set output frequency to freq in MHz and amplitude to amp in dBm

        Args:
            freq (float): frequency in MHz
            amp (float): amplitude in dBm
        self.command_list.append(f'f{freq:.6f}')
        self.command_list.append(f'W{amp:.3f}')
"""