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

class KoheronCTL200(IntermediateDevice):

    # A human readable name for device model used in error messages
    description = "Khoeron digital butterly laser diode controller"
    # The labscript Output classes this device supports
    allowed_children = [ ]
    # The maximum update rate of this device (in Hz)
    
    #clock_limit = 1e3 ### update this #Cs lab using 1e4 a value

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
        self.BLACS_connection = "Khoeron digital butterly laser diode controller {}".format(com_port)
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

    def enable_laser(self, state):
        """Enable or disable the laser output."""
        value = 1 if state else 0
        command = f"lason {value}"
        self.command_list.append(command)

    def set_laser_current(self, current):
        """Set the laser current in mA."""
        command = f"ilaser {current}"
        self.command_list.append(command)

    def set_temperature(self, resistance):
        """Set the temperature setpoint via thermistor resistance in Ohms."""
        command = f"rtset {resistance}"
        self.command_list.append(command)

    def set_interlock(self, state):
        """Enable or disable the interlock functionality."""
        value = 1 if state else 0
        command = f"lckon {value}"
        self.command_list.append(command)

    def set_pid_gains(self, p_gain, i_gain, d_gain):
        """Set the PID gains for temperature control."""
        commands = [
            f"pgain {p_gain}",
            f"igain {i_gain}",
            f"dgain {d_gain}"
        ]
        self.command_list.extend(commands)

    def save_settings(self):
        """Save the current configuration to internal memory."""
        command = "save"
        self.command_list.append(command)

    def get_laser_current(self):
        """Get the current laser current."""
        command = "ilaser"
        self.command_list.append(command)

    def get_temperature(self):
        """Get the current temperature (thermistor resistance)."""
        command = "rtact"
        self.command_list.append(command)

    def get_tec_current(self):
        """Get the TEC current."""
        command = "itec"
        self.command_list.append(command)

    def get_photodiode_current(self):
        """Get the photodiode current."""
        command = "iphd"
        self.command_list.append(command)

    def get_status(self):
        """Get the device status."""
        command = "status"
        self.command_list.append(command)

    def set_current_limit(self, limit):
        """Set the software current limit in mA."""
        command = f"ilmax {limit}"
        self.command_list.append(command)

    def set_temp_protection(self, state):
        """Enable or disable temperature protection."""
        value = 1 if state else 0
        command = f"tprot {value}"
        self.command_list.append(command)

    def set_temp_limits(self, min_resistance, max_resistance):
        """Set the temperature protection limits via thermistor resistance."""
        commands = [
            f"rtmin {min_resistance}",
            f"rtmax {max_resistance}"
        ]
        self.command_list.extend(commands)

    def set_tec_voltage_limits(self, min_voltage, max_voltage):
        """Set the TEC voltage limits."""
        commands = [
            f"vtmin {min_voltage}",
            f"vtmax {max_voltage}"
        ]
        self.command_list.extend(commands)

    def get_error(self):
        """Get the error code."""
        command = "err"
        self.command_list.append(command)

    def clear_error(self):
        """Clear the error code."""
        command = "errclr"
        self.command_list.append(command)

    