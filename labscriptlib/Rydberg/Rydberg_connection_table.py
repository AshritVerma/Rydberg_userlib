from multiprocessing import connection
#from labscript import start, stop, ClockLine, DigitalOut, RemoteBLACS
from labscript_devices.NI_DAQmx.models.NI_PCI_6733 import NI_PCI_6733
from labscript_devices.NI_DAQmx.models.NI_PCIe_6738 import NI_PCIe_6738
from labscript_devices.NI_DAQmx.models.NI_PCI_6534 import NI_PCI_6534
from labscript_devices.PulseBlasterUSB import PulseBlasterUSB
from labscript_devices.IMAQdxCamera.labscript_devices import IMAQdxCamera
from user_devices.Rydberg.AndorCamera.labscript_devices import AndorCamera
from user_devices.Rydberg.PTSControl.labscript_devices import PTSControl
from user_devices.Rydberg.BaslerCamera.labscript_devices import BaslerCamera
from user_devices.Rydberg.AD9959ArduinoComm.labscript_devices import AD9959ArduinoComm, AD9959ArduinoTriggerDigital
from user_devices.Rydberg.Agilent33250a.labscript_devices import Agilent33250a 
from user_devices.Rydberg.AgilentE8257D.labscript_devices import AgilentE8257D
from user_devices.Rydberg.SMC100A.labscript_devices import SMC100A
from user_devices.Rydberg.AgilentSG8648.labscript_devices import AgilentSG8648
from user_devices.Rydberg.SRSLukinSG384.labscript_devices import SRSLukinSG384
from user_devices.Rydberg.NICounter.labscript_devices import NICounter
from user_devices.Rydberg.HRM.labscript_devices import HRM
from user_devices.Rydberg.SLM.labscript_devices import SLM
from user_devices.Rydberg.CUAServoMirror.labscript_devices import CUAServoMirror
from user_devices.Rydberg.Elliptec.labscript_devices import ElliptecInterfaceBoard, ELL14
from user_devices.Rydberg.Elliptec.elliptec_unit_conversions import ELL14_Unit_Converter
from user_devices.Rydberg.HamamatsuCamera.labscript_devices import HamamatsuCamera
from user_devices.Rydberg.SpectrumAWG.labscript_devices import SpectrumAWG

from user_devices.Rydberg.AD9959ArduinoCommSpecial.labscript_devices import AD9959ArduinoCommSpecial, AD9959ArduinoTriggerDigitalSpecial

## ashrit
from user_devices.Rydberg.WindfreakSynthUSB3.labscript_devices import WindfreakSynthUSB3


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

def cxn_table():


    PulseBlasterUSB(
        name='pulseblaster_0',
        board_number=1,
    )

    ##
    ## Clocks for NI cards and initialize NI cards
    ## 
    ClockLine(
        name='ni_6534_clk',
        pseudoclock=pulseblaster_0.pseudoclock,
        connection='flag 23',
    )

    NI_PCI_6534(
        name="ni_6534",
        parent_device=ni_6534_clk,
        clock_terminal="/DO_6534_A/PFI2", #"/DO_6534_A/PFI6",#
        MAX_name='DO_6534_A'
    )
    
    ClockLine(
        name='ni_6733B_clk',
        pseudoclock=pulseblaster_0.pseudoclock,
        connection='flag 1',
    )

    ClockLine(
        name='ni_6733C_clk',
        pseudoclock=pulseblaster_0.pseudoclock,
        connection='flag 2',
    )

    ClockLine(
        name='ni_6733A_clk',
        pseudoclock=pulseblaster_0.pseudoclock,
        connection='flag 6',
    )


    NI_PCI_6733(
        name="ni_6733A", 
        parent_device=ni_6733A_clk, 
        clock_terminal = "/AO_A/PFI0", 
        MAX_name = "AO_A"
        )

    ####

    NI_PCI_6733(
        name="ni_6733B", 
        parent_device=ni_6733B_clk, 
        clock_terminal = "/AO_B/PFI0", 
        MAX_name = "AO_B"
        )

    #####
    NI_PCI_6733(
        name="ni_6733C", 
        parent_device=ni_6733C_clk, 
        clock_terminal = "/AO_C/PFI0", 
        MAX_name = "AO_C"
    )

    # #####

    # ClockLine(
    #     name='ni_6738_clk',
    #     pseudoclock=pulseblaster_0.pseudoclock,
    #     connection='flag 23',
    # )

    # NI_PCIe_6738(
    #     name="ni_6738", 
    #     parent_device=ni_6738_clk, 
    #     clock_terminal = "/AO_32/PFI0", 
    #     MAX_name = "AO_32"
    # )

    # ######
    # ###### Devices
    # ######

    # MOT and Repump beatnote locking
    AD9959ArduinoTriggerDigital(
        name="motl_trigger",
        parent_device=pulseblaster_0.direct_outputs,
        connection="flag 9",
        default_value=0,
    )

    AD9959ArduinoTriggerDigital(
        name="repump_trigger",
        parent_device=pulseblaster_0.direct_outputs,
        connection="flag 11",
        default_value=0,
    )

    AD9959ArduinoComm(
        name="motl_repump_ad9959",
        parent_device=None,
        com_port="COM3",
        baud_rate = 115200,
        channel_mappings={"MOT":'ch0', "Repump":'ch3'},
        default_values={"MOT":1148e6, "Repump":5602.17e6},
        trigger_mappings={"MOT":motl_trigger, "Repump":repump_trigger},
        div_32=True
    )
    ### Zeyang's AOD setup BEGIN

    # ##### new code for ramping frequencies
    # AD9959ArduinoTriggerDigital(
    #     name="AOD0_trigger",
    #     parent_device=pulseblaster_0.direct_outputs,
    #     connection="flag 0",
    #     default_value=0,
    # )

    # # AD9959ArduinoTriggerDigital(
    # #     name="AOD1_trigger",
    # #     parent_device=pulseblaster_0.direct_outputs,
    # #     connection="flag 8",
    # #     default_value=0,
    # # )

    # DigitalOut(
    #     name='triggerRampSync', 
    #     parent_device=pulseblaster_0.direct_outputs, 
    #     connection='flag 8'
    # )

    # AD9959ArduinoCommSpecial(
    #     name="sidetrap_770_ad9959",
    #     parent_device=None,
    #     com_port="COM7",
    #     baud_rate = 115200,
    #     channel_mappings={"AOD0":'ch0', "AOD1":'ch1'},
    #     default_values={"AOD0":92e6, "AOD1":91e6},
    #     trigger_mappings={"AOD0":AOD0_trigger, "AOD1":None},
    #     div_32=False
    # )

    ##### old code for jumping frequencies
    # AD9959ArduinoTriggerDigital(
    #     name="AOD0_trigger",
    #     parent_device=pulseblaster_0.direct_outputs,
    #     connection="flag 0",
    #     default_value=0,
    # )

    # AD9959ArduinoTriggerDigital(
    #     name="AOD1_trigger",
    #     parent_device=pulseblaster_0.direct_outputs,
    #     connection="flag 8",
    #     default_value=0,
    # )

    # AD9959ArduinoComm(
    #     name="sidetrap_770_ad9959",
    #     parent_device=None,
    #     com_port="COM7",
    #     baud_rate = 115200,
    #     channel_mappings={"AOD0":'ch0', "AOD1":'ch1'},
    #     default_values={"AOD0":92e6, "AOD1":91e6},
    #     trigger_mappings={"AOD0":AOD0_trigger, "AOD1":AOD1_trigger},
    #     div_32=False
    # )

    ### Zeyang's AOD setup END

    # This turns on both the SPCM and the NICounter so that they begin counting. This is equivalent to SPCM 1 in labrad
    Trigger(
        name='spcm_on_trigger',
        parent_device=pulseblaster_0.direct_outputs,
        connection='flag 21',
        default_value=0,
    )

    # Equivalent to Counting Card in Labrad
    NICounter(
        name='spcm_counter', 
        parent_device=pulseblaster_0.direct_outputs,
        connection='flag 7',
        MAX_name='Dev6', 
        counter_channel="Dev6/Ctr0", 
        input_channel="/Dev6/PFI39", 
        gate_channel="/Dev6/PFI38", 
    )

    # Trigger(
    #     name='pts_rydberg_trigger',
    #     parent_device=pulseblaster_0.direct_outputs,
    #     connection='flag 0'
    # )

    # PTSControl(
    #     name='pts_rydberg',
    #     parent_device=pts_rydberg_trigger,
    #     device_serial=b'10440000K8',
    # )

    PTSControl(
        name='pts_probe',
        parent_device=pulseblaster_0.direct_outputs,
        connection='flag 3',
        device_serial=b'10440000K8',
        #device_serial=b'10440000KE',
    )

    ### COILS

    
    AnalogOut(
        name='small_z_coil',
        parent_device=ni_6733C,
        connection="ao0",
        default_value=0,
        limits=(-10, 6.5) # oscillates above ~6.5 V
        
    )

    AnalogOut(
        name="z_coil",
        parent_device=ni_6733C,
        connection="ao3",
        default_value=0,
        limits=(-1e-10, 5.1)
    )

    AnalogOut(
        name="x_coil",
        parent_device=ni_6733C,
        connection="ao1",
        default_value=0,
        limits=(-6, 10.1)
    )

    

    AnalogOut(
        name="y_coil",
        parent_device=ni_6733C,
        connection="ao2",
        default_value=0,
        limits=(-9, 9)
    )


    AnalogOut(
        name="gradient_coil",
        parent_device=ni_6733C,
        connection="ao4",
        default_value=0,
        limits=(-1e-10, 4.0)
    )

    # switch to ditgital once tested
    DigitalOut(
        name='gradient_coil_switch',
        parent_device=ni_6534,
        connection="port1/line1", 
        default_value=1,
    )   
    # switch to ditgital once tested
    DigitalOut(
        name='detection_shutter',
        parent_device=ni_6534,
        connection="port1/line0", 
        default_value=0,
    )   
    # switch to ditgital once tested
    DigitalOut(
        name='repump_shutter',
        parent_device=ni_6534,
        connection="port0/line7",
        default_value=1,
    )   

    DigitalOut(
        name='mot_shutter',
        parent_device=ni_6534,
        connection="port1/line2",
        default_value=1,
    )   

    ### LASERS
    AnalogOut(
        name="motl_aom_power",
        parent_device=ni_6733C,
        connection="ao6",
        default_value=0,
        limits=(-1e-10, 3)
    )

    DigitalOut(
        name='motl_aom_switch',
        parent_device=pulseblaster_0.direct_outputs,
        connection="flag 20",
        default_value=0,
    )   

    AnalogOut(
        name="repump_aom_power",
        parent_device=ni_6733C,
        connection="ao5",
        default_value=0,
        limits=(-1e-10, 3)
    )


    DigitalOut(
        name='repump_aom_switch',
        parent_device=pulseblaster_0.direct_outputs,
        connection="flag 19",
        default_value=0,
    )   

    AnalogOut(
        name= "dt770_aom_power",#"rsc_aom_power",
        parent_device=ni_6733B,
        connection="ao6",
        default_value=0,
        limits=(-1e-10, 3)
    )

    DigitalOut(
        name='dt770_aom_switch',#'rsc_aom_switch',
        parent_device=ni_6534,
        connection="port0/line5",
        default_value=0,
    ) 

    DigitalOut(
        name='is_it_top_control',
        parent_device=ni_6534,
        connection="port0/line4",
        default_value=0,
    )    

    DigitalOut(
        name='MW_TTL',
        parent_device=ni_6534,
        connection="port0/line6",
        default_value=0,
    )  

    DigitalOut(
        name='Top_flip_mount',
        parent_device=ni_6534,
        connection="port1/line5",
        default_value=0,
    ) 

    AnalogOut(
        name="imaging_aom_power",
        parent_device=ni_6733C,
        connection="ao7",
        default_value=0,
        limits=(-1e-10, 2)
    )

    DigitalOut(
        name='imaging_aom_switch',
        parent_device=pulseblaster_0.direct_outputs,
        connection="flag 13",
        default_value=0,
    )   

    AnalogOut(
        name="dt808_aom_power",
        parent_device=ni_6733B,
        connection="ao3",
        default_value=0,
        limits=(-1e-10, 7)
    )

    DigitalOut(
        name='dt808_aom_switch',
        parent_device=pulseblaster_0.direct_outputs,
        connection="flag 16",
        default_value=0,
    )   

    AnalogOut(
        name="dt785_aom_power",
        parent_device=ni_6733B,
        connection="ao2",
        default_value=0,
        limits=(-1e-10, 0.51)
    )

    AnalogOut(
        name="dt852_aom_power",
        parent_device=ni_6733B,
        connection="ao5",
        default_value=0,
        limits=(-1e-10, 0.91)
    )

    DigitalOut(
        name='dt785_aom_switch',
        parent_device=pulseblaster_0.direct_outputs,
        connection="flag 15",
        default_value=0,
    )   

    AnalogOut(
        name="control_aom_power",
        parent_device=ni_6733B,
        connection="ao0",
        default_value=0,
        limits=(-1e-10, 3)
    )

    DigitalOut(
        name='control_aom_switch',
        parent_device=pulseblaster_0.direct_outputs,
        connection="flag 14",
        default_value=0,
    )   

    AnalogOut(
        name="probe_aom_power",
        parent_device=ni_6733B,
        connection="ao4",
        default_value=0,
    )

    DigitalOut(
        name='probe_aom_switch',
        parent_device=pulseblaster_0.direct_outputs,
        connection="flag 18",
        default_value=0,
    )   

    AnalogOut(
        name="sacher_aom_power",
        parent_device=ni_6733B,
        connection="ao1",
        default_value=2,
        limits=(-1e-10, 3)
    )

    DigitalOut(
        name='sacher_aom_switch',
        parent_device=pulseblaster_0.direct_outputs,
        connection="flag 17",
        default_value=1,
    )  

    AnalogOut(
        name="op_aom_power",
        parent_device=ni_6733B,
        connection="ao7",
        default_value=0,
        limits=(-1e-10, 3)
    )


    DigitalOut(
        name='op_aom_switch',
        parent_device=pulseblaster_0.direct_outputs,
        connection="flag 12",
        default_value=0,
    )  

    ## E FIELD PLATES:
    AnalogOut(
        name="V1",
        parent_device=ni_6733A,
        connection="ao0",
        default_value=0,
        limits=(-10,10)
    )
    
    AnalogOut(
        name="V2",
        parent_device=ni_6733A,
        connection="ao1",
        default_value=0,
        limits=(-10,10)
    )

    AnalogOut(
        name="V3",
        parent_device=ni_6733A,
        connection="ao2",
        default_value=0,
        limits=(-10,10)
    )

    AnalogOut(
        name="V4",
        parent_device=ni_6733A,
        connection="ao3",
        default_value=0,
        limits=(-10,10)
    )

    AnalogOut(
        name="V5",
        parent_device=ni_6733A,
        connection="ao4",
        default_value=0,
        limits=(-10,10)
    )

    AnalogOut(
        name="V6",
        parent_device=ni_6733A,
        connection="ao5",
        default_value=0,
        limits=(-10,10)
    )

    AnalogOut(
        name="V7",
        parent_device=ni_6733A,
        connection="ao6",
        default_value=0,
        limits=(-10,10)
    )

    AnalogOut(
        name="V8",
        parent_device=ni_6733A,
        connection="ao7",
        default_value=0,
        limits=(-10,10)
    )

    # ### WAVEPLATES
    # RemoteBLACS(name='rsc_standing_half_waveplate_worker', 
    #     host='192.168.10.105')

    # # Instantiate a interface board.
    # ElliptecInterfaceBoard(
    #     name='rsc_standing_half_waveplate_board',
    #     com_port='COM1', 
    #     mock=False,
    #     #worker=rsc_standing_half_waveplate_worker,
    # )
    # # Instantiate a actuator.
    # ELL14(
    #     name='rsc_standing_half_waveplate',
    #     parent_device=rsc_standing_half_waveplate_board,
    #     connection='0',
    #     serial_number='11400102',
    #     home_on_startup=True,
    #     unit_conversion_class=ELL14_Unit_Converter,
    #     unit_conversion_parameters={'offset': 0},
    # )

    ### SIGNAL GENERATOR DEVICES
    Agilent33250a(
        name='agilent_awg1',
        parent_device=pulseblaster_0.direct_outputs,
        com_port = 10,
        connection='flag 4',
        device_ID=10
    )   

    # Trigger(
    #     name='test_trigger2',
    #     parent_device=pulseblaster_0.direct_outputs,
    #     connection='flag 22',
    #     default_value=0,
    # )

    Agilent33250a(
        name='agilent_awg2',
        parent_device=pulseblaster_0.direct_outputs,
        com_port = 11,
        connection='flag 22',
        device_ID=11
    )

    # Agilent device (TO DO: TEST)
    Agilent33250a(
        name='agilent_awg3',
        parent_device=pulseblaster_0.direct_outputs,
        com_port = 18,
        connection='flag 10',
        device_ID=12
    )  

    AgilentE8257D(
        name='agilentE8257D',
        parent_device=None,
        com_port = 5025,
        IP = '192.168.10.103',
    )  

    SMC100A(
        name='smc_sg1',
        parent_device=None,
        com_port = 'USB0::0x0AAD::0x006E::101266::INSTR',
    )

    WindfreakSynthUSB3(
        name = 'synthusb3',
        parent_device=None,
        #parent_device=pulseblaster_0.direct_outputs,
        com_port = 'COM6'
        #com_port = 6
        )


    AgilentSG8648(
        name='agilent_sg1',
        parent_device=None,
        com_port = 12,
    )

    SRSLukinSG384(
        name='srs384',
        parent_device=None,
        com_port = 26,
    )

    RemoteBLACS(name='spectrum_awg_worker', 
                # host='192.168.10.108')
                host='192.168.10.105')

    SpectrumAWG(name='spectrum_awg', parent_device=ni_6534, connection='port1/line3', worker=spectrum_awg_worker)
    

    HRM(
        name='hrm'
    )

    SLM(
        name="slm",
        ip_address='192.168.10.105',
        worker='roy_beast'
    )

    ## 480 AOD is it prepare or detect config
    DigitalOut(
        name='switch_480AODconfig_to_detect',
        parent_device=ni_6534,
        connection="port1/line4",
        default_value=0,
    )  

    # Dummy output
    # DigitalOut(
    #     name='dummy_output',
    #     parent_device=ni_6534,
    #     connection="port1/line7",
    #     default_value=0,
    # )   

    # Mirrors
    CUAServoMirror(name="mirror_controller",
                   mirror_mapping_dict={
                        "spcm_close":(4, 3),
                        "spcm_far":(13, 12),
                        "side_trap":(24, 25),
                        "control_light":(10,11),
                        "control_light_top":(26,27),
                        "770_mirror":(32,31)

                        },
                  com_port="COM6")

    ## Camera
######## USE THIS ONE #############################################
    # AndorCamera(
    #     'andor',
    #     parent_device=pulseblaster_0.direct_outputs,
    #     # I made a custom class from PylonCamera that initializes the camera by searching a list rather than using a serial number,
    #     # because I couldn't get the SN to work. This approach will break if we ever have more than one basler camera connected at a time
    #     # This serial number is irrelevant and is not used in camera creation
    #     connection = 'flag 6',
    #     serial_number=24820,
    #     camera_attributes= {
    #         'readout': 'full_image',
    #         'trigger': 'external',
    #     },
    #     manual_mode_camera_attributes={
    #         'trigger': 'internal'
    #     }
    # )

    RemoteBLACS(name='hamamatsu_worker', 
                # host='192.168.10.108')
                host='192.168.10.105')


    
    
    hamamatsu_camera_attributes={'exposure':5e-3,'triggerMode':2,#'binning':1,
    'TriggerGlobalExposure':5,
    'pixelType':2,
    'bufferpixelType':2,
    'triggerPolarity':2,
    'readoutMode':2,
    'subarrayMode':2,
    'subarrayHsize':256,
    'subarrayVsize':16,
    'subarrayHpos':2500,
    'subarrayVpos':668,
    'FrameBundEn':1,
    'FrameBundFrames':2,
    'OutputTriggerKind':4,
    'OutputTriggerActive':1,
    'OutputTriggerPolarity':2
    }

    hamamatsu_manual_mode_camera_attributes={'exposure':1e-4,'triggerMode':1,
    'pixelType':2,
    'bufferpixelType':2,
    'subarrayMode':2,
    'readoutMode':2,}
    # 'subarrayHsize':1024,#256,
    # 'subarrayVsize':1024,#16,
    # 'subarrayHpos':1600, #2500,
    # 'subarrayVpos':4}#668}

    HamamatsuCamera(name='hamamatsu',
        parent_device= pulseblaster_0.direct_outputs,#ni_6534,
        serial_number=1337,
        connection='flag 8',#'port0/line1',
        worker=hamamatsu_worker,
        camera_attributes=hamamatsu_camera_attributes,
        #manual_mode_camera_attributes=hamamatsu_manual_mode_camera_attributes
        )

    # the order that the attributes are set in is ***very*** important
    # IMAQdxCamera(
    #     'lucid', 
    #     parent_device=ni_6534,
    #     connection="port1/line6",
    #     serial_number=0x1C0FAF05987D,
    #     trigger_duration=1e-7,
    #     minimum_recovery_time=10e-3,
    #     #worker=lucid_worker,
    #     camera_attributes = {'TriggerMode':'On', 'AcquisitionMode':'Continuous',  'TriggerSource':'Line 0', 'TriggerSelector':'Exposure Active',  
    #                          'ShortExposureEnable':False, 'GammaEnable':False,  'ExposureTime':196.048, 'OffsetX': 300, 'OffsetY': 600, 'Width':156, 'Height':600,
    #                          'PixelFormat':'Mono8', 'DeviceStreamChannelPacketSize':1500,'AcquisitionFrameCount':3}, # increase the acquistion frame count if you want more frames, otherwise it will error 
    #     manual_mode_camera_attributes={'AcquisitionMode':'Continuous', 'TriggerSelector':'Frame Start', 
    #     								'TriggerSource':'Software','AcquisitionFrameCount':1, 'TriggerMode':'Off'}
    #     								# ExposureTime shouldn't matter and should instead be controlled by the trigger in this setting exposure in us
    # )
    # Note: if the camera is disconnected, wait 5-10 seconds before trying to reconnect or you will get an error
 


######## DON'T USE THIS ONE #############################################
    # AndorCamera(
    #     'andor',
    #     parent_device=pulseblaster_0.direct_outputs,
    #     # I made a custom class from PylonCamera that initializes the camera by searching a list rather than using a serial number,
    #     # because I couldn't get the SN to work. This approach will break if we ever have more than one basler camera connected at a time
    #     # This serial number is irrelevant and is not used in camera creation
    #     connection = 'flag 6',
    #     serial_number=24820,
    #     camera_attributes= {
    #         'acquisition': 'single',
    #         'preamp': False, #True,
    #         'preamp_gain': 1.0, #2.0,
    #         'exposure_time': 50e-6,
    #         'readout': 'full_image',
    #         'trigger': 'external',
    #         'xbin': 1,
    #         'ybin': 1,
    #         'height': 1024,
    #         'width': 1024,
    #         'left_start': 1,
    #         'bottom_start': 1,
    #         'number_kinetics': 1,
    #         'vertical_shift_speed': 1,
    #         'horizontal_shift_speed': 1,
    #     },
    #     manual_mode_camera_attributes={
    #         'trigger': 'internal'
    #     }
    # )

    BaslerCamera(
        'basler',
        parent_device=pulseblaster_0.direct_outputs,
        # I made a custom class from PylonCamera that initializes the camera by searching a list rather than using a serial number,
        # because I couldn't get the SN to work. This approach will break if we ever have more than one basler camera connected at a time
        # This serial number is irrelevant and is not used in camera creation
        serial_number=-1,
        connection='flag 5',
        trigger_duration=50e-6,
        camera_attributes= {
            'ExposureAuto': 'Off',
            'GainAuto': 'Off',
            'Gain': 0.0,
            'BlackLevel': 0.0,
            'Gamma': 1.0,
            'ExposureMode': 'Timed',
            'ExposureTime': 50.0,
            'TriggerMode': 'On', # Can set to 'Off' for software triggering, 'On' for external triggering
            'LineSelector': 'Line1',
            'CounterEventSource': 'FrameStart',
            'CounterResetActivation': 'RisingEdge',
            'TriggerActivation': "RisingEdge",
            'TriggerDelay': 0,
            "PixelFormat": "Mono8"
        },
        manual_mode_camera_attributes={
            'TriggerMode': 'Off',
            'ExposureTime': 1050.0,
        }
    )

    # PylonCamera(
    #     'thorlabs_cam',
    #     worker=roy_beast,
    #     parent_device=pulseblaster_0.direct_outputs,
    #     serial_number='4102994040',
    #     connection='flag 8',

    # )
    
    # #Bad camera >:(
    # IMAQdxCamera(
    # 'firebrain701b',
    # parent_device=pulseblaster_0.direct_outputs,
    # connection='flag 8',
    # serial_number=0x814436300001000,
    # trigger_duration=1e-7,
    # minimum_recovery_time=1e-2,
    # camera_attributes = {
    #     'AcquisitionAttributes::Bayer::Algorithm': 'Bilinear',
    #     'AcquisitionAttributes::Bayer::GainB': 1.0,
    #     'AcquisitionAttributes::Bayer::GainG': 1.0,
    #     'AcquisitionAttributes::Bayer::GainR': 1.0,
    #     'AcquisitionAttributes::Bayer::Pattern': 'Use hardware value',
    #     'AcquisitionAttributes::BitsPerPixel': 'Use hardware value',
    #     'AcquisitionAttributes::Controller::DesiredStreamChannel': 0,
    #     'AcquisitionAttributes::Controller::StreamChannelMode': 'Automatic',
    #     'AcquisitionAttributes::Height': 1024,
    #     'AcquisitionAttributes::ImageDecoderCopyMode': 'Auto',
    #     'AcquisitionAttributes::OffsetX': 0,
    #     'AcquisitionAttributes::OffsetY': 0,
    #     'AcquisitionAttributes::OutputImageType': 'Auto',
    #     'AcquisitionAttributes::OverwriteMode': 'Get Newest',
    #     'AcquisitionAttributes::PacketSize': 3072,
    #     'AcquisitionAttributes::PixelFormat': 'Mono 8',
    #     'AcquisitionAttributes::ReceiveTimestampMode': 'None',
    #     'AcquisitionAttributes::ReserveDualPackets': 0,
    #     'AcquisitionAttributes::ShiftPixelBits': 0,
    #     'AcquisitionAttributes::Speed': '400 Mbps',
    #     'AcquisitionAttributes::SwapPixelBytes': 0,
    #     'AcquisitionAttributes::Timeout': 5000,
    #     'AcquisitionAttributes::VideoMode': 'Format 7, Mode 0, 1280 x 1024',
    #     'AcquisitionAttributes::Width': 1280,
    #     'CameraAttributes::AutoExposure::Mode': 'Ignored',
    #     'CameraAttributes::Brightness::Mode': 'Relative',
    #     'CameraAttributes::Brightness::Value': 418.0,
    #     'CameraAttributes::Gain::Mode': 'Relative',
    #     'CameraAttributes::Gain::Value': 0.0,
    #     'CameraAttributes::Gamma::Mode': 'Relative',
    #     'CameraAttributes::Gamma::Value': 10.0,
    #     'CameraAttributes::Sharpness::Mode': 'Relative',
    #     'CameraAttributes::Sharpness::Value': 414.0,
    #     'CameraAttributes::Shutter::Mode': 'Relative',
    #     'CameraAttributes::Shutter::Value': 50.0,#50.0,#1000.0,
    #     'CameraAttributes::Trigger::TriggerActivation': 'Level High',
    #     'CameraAttributes::Trigger::TriggerMode': 'Mode 0',
    #     },
    #     # Didn't seem to work :(
    #     # manual_mode_camera_attributes={
    #     #     'TriggerMode': 'Off'
    #     # }
    # )


if __name__ == '__main__':

    cxn_table()
    start()
    stop(1)