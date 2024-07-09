import os
import sys
import numpy as np

import h5py
import socket
import pickle
import time
import matplotlib.pyplot as plt

os.chdir('/Users/emilyqiu/labscript-suite/Rydberg_userlib/user_devices/Rydberg/SLM')

# from slm_utils import slmpy_updated as slmpy
from slm_utils import devices_attr
from slm_utils import freq_funcs

# # create a display window on SLM
# slm_win = slmpy.SLMdisplay(isImageLock=False, monitor=MONITOR_ID)

# create the SLM device class
slm_attr = devices_attr.SLMx13138()

# # some command
# w='one_trap'
#
# try:
#     function = dispatcher[w]
# except KeyError:
#     raise ValueError('invalid input')

phase_rad = slm_attr.one_trap()
phase_rad = slm_attr.two_traps(shiftx = 0, shifty = 0, target_sep = 10e-6, alpha=0)

# get the correction pattern

# third attempt - 8 poly but failed bc we forgot to set the higher orders to zero
# with h5py.File(path, 'r') as f:
#     coeffs = f.get('devices/slm/zernike_array').value

# first attempt, 5 poly
coeffs = [0,0,0,-0.17852612, -0.05489775, 0.10766948, 0.02597523, 0.03392248]

# second attempt, 14 poly
coeffs = [0,0,0,-0.184, -0.040, 0.113, 0.040, 0.019, 0.005, -0.035, 0.008, -0.002, -0.001, 0.000, -0.002, -0.002, -0.001]

zernike_corr =  slm_attr.eval_zernike(coeffs)
# phase_rad += zernike_corr

# # visualize the zernike correction
# plt.figure()
# plt.imshow(np.mod(zernike_corr,2*np.pi), cmap='bwr' )
# plt.colorbar()
# plt.show()

# add
phase_int8 = slm_attr.convert_bmp(phase_rad, bit_depth = 213.)

beam, int = slm_attr.predict_array(phi=phase_rad, nint=1, next=2)
# slm_win.updateArray(phase_int8)
# slm_win.close()
