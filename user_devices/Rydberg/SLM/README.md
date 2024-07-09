# Explanation

This labscript class interacts with the High-Resolution Timing Module. It is used to record data with 27 ps resolution. It records the times that it receives events, then returns the time gap between all of those events as an array saved into the HDF \data\ folder. 

Note: There are extra events recorded that do not correspond to true detected counts. This is because the HRM will only read out data in 256-event groups. E.g., if you have 13 events, the HRM will not allow you to read out this data. To get around this, we send 256 "fake" events to the HRM after 3 acquire times. 

Example:
Suppose you have 257 events on the HRM. Then the event array with time gaps will have 512-1 entries (minus one, since we ignore the first time gap), where the last 511-257=254 correspond to the fake events. These 254 events can be identified by the fact that they are evenly spaced (default is 3us) and occur after 3\*acquire_time input into the hrm.acquire_data function. I do not remove these in the code in case we accidentally remove real counts in some future situation that I did not predict

# Labscript Structure
The structure of this code is as follows: the blacs worker functions as an IP client that opens up a 32-bit server "32bit_HRM_Server.py", which then uses the HRM dll to talk to the HRM. This confusing structure is necessary because the dll is 32-bit and does not function with 64-bit python. Additionally, for backwards compatibility reasons, the 32 bit python server is python 2.7. 

In summary, the blacs worker sends commands to the 32bit_HRM_Server, which then sends commands to the HRM. The 32bit server then reads/processes the data, then sends it back to the blacs worker. Finally, it is appended to the hdf file.