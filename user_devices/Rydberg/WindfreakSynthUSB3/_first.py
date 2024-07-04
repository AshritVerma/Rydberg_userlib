# on COM6

# create class
from labscript import Device, LabscriptError

class SynthUSB3(Device):
    description = 'Windfreak SynthUSB3'
    allowed_children = []

    def __init__(self, name, parent_device, connection, **kwargs):
        Device.__init__(self, name, parent_device, connection, **kwargs)
        self.BLACS_connection = connection

    def generate_code(self, hdf5_file):
        # Code to generate the device-specific instructions
        pass

    def program_manual(self, value):
        # Code to send manual commands to the device
        pass




# implement communication

from labscript import Device, LabscriptError

class SynthUSB3(Device):
    description = 'Windfreak SynthUSB3'
    allowed_children = []

    def __init__(self, name, parent_device, connection, **kwargs):
        Device.__init__(self, name, parent_device, connection, **kwargs)
        self.BLACS_connection = connection

    def generate_code(self, hdf5_file):
        # Code to generate the device-specific instructions
        pass

    def program_manual(self, value):
        # Code to send manual commands to the device
        pass



# integrating with BLACS

from blacs.device_base_class import DeviceTab

class SynthUSB3Tab(DeviceTab):
    def initialise_GUI(self):
        # Create GUI elements for the device
        pass

    def initialise_workers(self):
        # Initialize the worker process for the device
        self.create_worker(
            'main_worker',
            'path.to.SynthUSB3Worker',
            {}
        )
        self.primary_worker = 'main_worker'



# the worker class 

from blacs.tab_base_classes import Worker

class SynthUSB3Worker(Worker):
    def init(self):
        self.ser = serial.Serial(self.BLACS_connection, 115200, timeout=1)

    def program_manual(self, value):
        self.ser.write(value.encode())
        response = self.ser.read(100)
        return response

    def shutdown(self):
        self.ser.close()
    


# testing and debugging

from labscript import start, stop, SynthUSB3

synth = SynthUSB3('synth', parent_device, 'COM3')

start()
synth.program_manual('FREQ 1000MHz')
stop()