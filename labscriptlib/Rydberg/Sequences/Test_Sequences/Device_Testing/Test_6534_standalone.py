from telnetlib import DO
from PyDAQmx import *
#from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxTypes import *
from numpy.lib.recfunctions import structured_to_unstructured
#from PyDAQmx.DAQmxCallBack import *
import numpy as np
import ctypes
import time

DO_table = np.array([( 0,), (32,), ( 0,), (32,), ( 0,), (32,), ( 0,), ( 255,), ( 0,)],
      dtype=[('port0', 'u1')])

DO_table = np.array([( 0,), (0,)],
      dtype=[('port0', 'u1')])

DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByScanNumber = 1
MAX_name = '/Dev1'
clock_terminal = '/Dev1/PFI2'
DAQmx_Val_ChanForAllLines = 1
clock_limit = 20e6
npts = 7
DO_task = Task()
written = int32()
ports = DO_table.dtype.names

final_values = {}
for port_str in ports:
    # Add each port to the task:
    con = '%s/%s' % (MAX_name, port_str)
    DO_task.CreateDOChan(con, "", DAQmx_Val_ChanForAllLines)

    # Collect the final values of the lines on this port:
    port_final_value = DO_table[port_str][-1]
    for line in range(7):
        # Extract each digital value from the packed bits:
        line_final_value = bool((1 << line) & port_final_value)
        final_values['%s/line%d' % (port_str, line)] = int(line_final_value)

# Convert DO table to a regular array and ensure it is C continguous:
DO_table = np.ascontiguousarray(
    structured_to_unstructured(DO_table, dtype=np.uint32)
)

# Check if DOs are all zero for the whole shot. If they are this triggers a
# bug in NI-DAQmx that throws a cryptic error for buffered output. In this
# case, run it as a non-buffered task.
DO_all_zero = not np.any(DO_table)
if DO_all_zero:
    DO_table = DO_table[0:1]

# Set up timing:
DO_task.CfgSampClkTiming(
    clock_terminal,
    clock_limit,
    DAQmx_Val_Rising,
    DAQmx_Val_FiniteSamps,
    uInt64(8),
)

DO_table = np.array(DO_table, dtype=np.uint32)

# Write data. See the comment in self.program_manual as to why we are using
# uint32 instead of the native size of each port.
DO_task.WriteDigitalU32(
    int32(8),
    True,  # autostart
    30.0,  # timeout
    DAQmx_Val_GroupByScanNumber,
    DO_table, # All but the last sample as mentioned above
    written,
    None,
)

time.sleep(10)
DO_task.StopTask()
DO_task.ClearTask()

# taskHandle = TaskHandle(0)
# _check( nidaq.DAQmxCreateTask("",byref(taskHandle)) )

# _check( nidaq.DAQmxCreateDOChan(
#     taskHandle,
#     channel_string,
#     "",
#     DAQmx_Val_ChanForAllLines #mabe have a channel for each line to speed up transfer ?
#     ))


# _check(
#         nidaq.DAQmxSetDODataXferMech(
#             taskHandle,
#             "",        #channel
#             int32(DAQmx_Val_DMA),        #Mode
#         )
#     )
    
# _check(
#         nidaq.DAQmxSetDOUseOnlyOnBrdMem(
#             taskHandle,
#             "",        #channel
#             True,        #Mode
#         )
#     )

# #        _check(
# #            nidaq.DAQmxCfgDigEdgeStartTrig(
# #            taskHandle,
# #            trigger_source,         # source
# #            DAQmx_Val_Rising)       # active edge
# #            )	
    
# _check( nidaq.DAQmxCfgSampClkTiming(
#     taskHandle,
#     clock_source, #source  
#     float64(clock_freq), # rate
#     DAQmx_Val_Rising, #activeEdge
#     DAQmx_Val_ContSamps, #sampleMode 
#     uInt64(numSamples) #numSamples
#     ))
    


# #NOTE - need to have atleast 2 samples or otherwise need to configure buffer
    
# _check(
#     nidaq.DAQmxWriteDigitalU32(
#         taskHandle,
#         int32(numSamples),         # numSampsPerChan
#         0,                              # autoStart
#         float64(30.0),                  # timeout
#         DAQmx_Val_GroupByChannel,       # dataLayout
#         data.ctypes.data,          # writeArray[]  #Check if this has to be converted to a ctypes type
#         byref(sampsPerChanWritten),           # *sampsPerChanWritten
#         None)                           # *reserved
#     )
