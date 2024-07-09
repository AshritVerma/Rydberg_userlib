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
from labscript.labscript import Device, set_passed_properties

import numpy as np
"""idea #5: use numpy arays instead of lists for faster operations
"""

class SLM(IntermediateDevice):

    # A human readable name for device model used in error messages
    description = "Spatial Light Modulator"
    # The labscript Output classes this device supports
    allowed_children = [ ]
    # The maximum update rate of this device (in Hz)
    clock_limit = 60

    @set_passed_properties(
        property_names={
            'connection_table_properties':
                [
                    'name',
                    'ip_address'
                ]
        }
    )
    def __init__ (self, name, ip_address='localhost', **kwargs):
        """ initialize device

        Args:
            name (str): name of device
        """
        IntermediateDevice.__init__ (self, name, parent_device=None)
        self.BLACS_connection = "SLM Connection"
        self.name = name
        self.ip_address = ip_address
        self.zernike_array = [0]
        #self.zernike_array = np.zeros(18) #what initial size is appropraite?
        self.set_zernike = False

        self.n_traps = 0
        self.one_trap_kwargs = {'shiftx': 0, 'shifty': 0}
        # self.one_trap_kwargs = {'line_sp': 11}
        self.two_traps_kwargs = {'target_sep': 10e-6, 'alpha': 0, 'shiftx': 0, 'shifty': 0}


    def generate_code(self,hdf5_file):
        """Write the frequency sequence for each channel to the HDF file

        Args:
            hdf5_file (hdf): labscript hdf file
        """

        Device.generate_code(self, hdf5_file)

        grp = hdf5_file.require_group('/devices/{}/'.format(self.name))
        
        dset1 = grp.require_dataset('zernike_array', (len(self.zernike_array),),dtype='f')
        dset1[:] = self.zernike_array
        
        """
        dset1 = grp.require_dataset('zernike_array', self.zernike_array.shape, dtype='f')
        dset1[:] = self.zernike_array
        """

        grp.attrs['set_zernike'] = self.set_zernike 
        grp.attrs['n_traps'] = self.n_traps

        if self.n_traps == 1:
            grp.attrs['shiftx'] = self.one_trap_kwargs['shiftx']
            grp.attrs['shifty'] = self.one_trap_kwargs['shifty']
            # grp.attrs['line_sp'] = self.one_trap_kwargs['line_sp']

        if self.n_traps == 2:
            grp.attrs['target_sep'] = self.two_traps_kwargs['target_sep']
            grp.attrs['alpha'] = self.two_traps_kwargs['alpha']
            grp.attrs['shiftx'] = self.two_traps_kwargs['shiftx']
            grp.attrs['shifty'] = self.two_traps_kwargs['shifty']

    def add_zernike(self, zernike_array):
        self.zernike_array = zernike_array
        self.set_zernike = True

    def one_trap(self, shiftx=None, shifty=None):
        self.n_traps = 1
        self.one_trap_kwargs['shiftx'] = self.one_trap_kwargs['shiftx'] if shiftx==None else shiftx
        self.one_trap_kwargs['shifty'] = self.one_trap_kwargs['shifty'] if shifty==None else shifty
        # self.one_trap_kwargs['line_sp'] = self.one_trap_kwargs['line_sp'] if line_sp==None else line_sp
        
    def two_traps(self, target_sep, alpha, shiftx=None, shifty=None):
        self.n_traps = 2
        self.two_traps_kwargs['target_sep'] = target_sep
        self.two_traps_kwargs['alpha'] = alpha
        self.two_traps_kwargs['shiftx'] = self.two_traps_kwargs['shiftx'] if shiftx==None else shiftx
        self.two_traps_kwargs['shifty'] = self.two_traps_kwargs['shifty'] if shifty==None else shifty
