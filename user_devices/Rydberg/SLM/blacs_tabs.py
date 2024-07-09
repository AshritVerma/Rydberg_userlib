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



from blacs.device_base_class import DeviceTab, define_state
from matplotlib.pyplot import text
from qtutils.qt.QtCore import*
from qtutils.qt.QtGui import *
from qtutils.qt.QtWidgets import *
from PyQt5.QtWidgets import QComboBox, QGridLayout, QLineEdit

class SLMTab(DeviceTab):
    def initialise_GUI ( self ):

        pass

    def initialise_workers(self):
        connection_table = self.settings['connection_table']
        device = connection_table.find_by_name(self.device_name)

        # Create and set the primary worker
        self.create_worker(
            'main_worker',
            'user_devices.Rydberg.SLM.blacs_workers.SLMWorker',
            {
                'name': device.properties['name'],
                'ip_address': device.properties['ip_address']
            },
        )
        self.primary_worker = 'main_worker'

