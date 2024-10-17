from labscript import (
    ClockLine,
    AnalogOut,
    DigitalOut,
    MHz,
    Trigger,
    start,
    stop,
    RemoteBLACS
)

from labscript_devices.DummyPseudoclock.labscript_devices import DummyPseudoclock
from user_devices.Rydberg.WindfreakSynthUSB3.labscript_devices import WindfreakSynthUSB3
from user_devices.Rydberg.KoheronCTL200.labscript_devices import KoheronCTL200

from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
from labscript_devices.NI_DAQmx.models.NI_PCIe_6738 import NI_PCIe_6738

def cxn_table():
    # Primary pseudoclock
    #DummyPseudoclock(name='dummy_pseudoclock')

    # PulseBlasterESRPro500(
    #     name='pulseblaster',
    #     board_number=0
    # )
    # ClockLine(
    #      name='ni_6738_clk',
    #      pseudoclock=pulseblaster.pseudoclock,
    #      connection='flag 0',
    # )

    # NI_PCIe_6738(
    #      name="ni_6738", 
    #      parent_device=ni_6738_clk, 
    #      clock_terminal = "/AO_32/PFI0", 
    #      MAX_name = "Dev1"
    # )

    
    # WindfreakSynthUSB3 device
    WindfreakSynthUSB3(
        name='synthusb3',
        parent_device=None,
        #parent_device=pulseblaster_0.direct_outputs,
        com_port=5  # Changed to string 'COM6' instead of integer 6
    )

    # KoheronCTL200(
    #     name='ctl200',
    #     parent_device=None,
    #     com_port=7,
    #     #current_limit = #in mA
    # )
       

    # Removed other devices not in use:
    # RemoteBLACS, CUAServoMirror, ElliptecInterfaceBoard, ELL14

if __name__ == '__main__':
    cxn_table()
    start()
    stop(1)