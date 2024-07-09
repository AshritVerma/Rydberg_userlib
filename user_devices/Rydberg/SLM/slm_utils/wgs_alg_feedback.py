'''
Weighted GS implementation, feedback to camera and/or data from experiment
Option to use phase-fixing in image plane (see Donggyu's paper on LOFA generation)
Option to use MRAF algorithm.

Emily Qiu

For Zelux camera:
thorlabs_tsi_sdk.tl_camera TLCameraSDK

August 2,2022

Note that indexing the array directly via e.g.
vtarget_i_new[slm_attr.trap_xy[iy,ix]] does not seem to work, could be an issue
with python3 vs python2
'''


import sys
import os
import time
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import json
import scipy
from scipy import misc, ndimage
from tqdm import tqdm
import imageio
import pickle
from PIL import Image

# os.chdir(r"C:\Users\RoyBeast\labscript-suite\Rydberg_userlib\user_devices\Rydberg\SLM/")
os.chdir(r"C:\Users\RoyAL\labscript-suite\Rydberg_userlib\user_devices\Rydberg\SLM/")


save_path = "Z:\\Calculations\\Emily\\SLM project\\v4_array_patterns\\"
base_filename = time.strftime("%Y_%m_%d-%H_%M__")

# our own files/functions
from slm_utils.devices_attr import SLMx13138
from slm_utils import slmpy_updated as slmpy
from slm_utils import freq_funcs
from slm_utils.freq_funcs import qim

# # Allied vision vimba sdk
# from vimba_sdk.Vimba_5_1.VimbaPython_Source.vimba import *

# # Thorlabs Zelux camera
# os.chdir(os.getcwd() + "\\zelux_sdk\\Scientific Camera Interfaces\\SDK\\Python Toolkit\\examples")
#
# from windows_setup import configure_path
# configure_path()
#
# from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
# from thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
# from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE

# # seems we need to add this when we switched to RoyAL... not sure why configure_path does not seem to work anymore
os.chdir(r"C:\Users\RoyAL\labscript-suite\Rydberg_userlib\user_devices\Rydberg\SLM/")

from zelux_sdk.thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from zelux_sdk.thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from zelux_sdk.thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE


## Testing thorlabs cameras

# configure Zelux camera
sdk = TLCameraSDK()
sdk.discover_available_cameras()
# camera = sdk.open_camera(sdk.discover_available_cameras()[0])


## phase pattern to feedback on - camera feedback

# # display the phase pattern
# command_dict = {'phase_pattern_file': slm_phase_final, 'phase_pattern_folder': '', 'shiftx': 7.8, 'shifty': -31.0, 'defocus': 0.0, 'alpha': -0.145}

command_dict = {'phase_pattern_file': '2022_07_29-12_21__nxt=10_nyt=01_sepx=8.000_sepy=8.000_offx=93.09_offy=-93.09.pkl',
                'phase_pattern_folder': '',
                'shiftx': 7.8,
                'shifty': -31.0,
                'defocus': 0.0,
                'alpha': -0.145}

# command_dict['phase_pattern_file'] = '2022_07_29-12_21__nxt=10_nyt=01_sepx=8.000_sepy=8.000_offx=93.09_offy=-93.09_feedback1.pkl'
command_dict['phase_pattern_file'] = '2022_08_01-19_56__nxt=10_nyt=01_sepx=8.000_sepy=8.000_offx=93.09_offy=-93.09_feedback2.pkl'

# command_dict = {'phase_pattern_file': "2022_04_26-19_16__mit_86traps.pkl", 'phase_pattern_folder': 'arb', 'shiftx': 7.8, 'shifty': -31.0, 'defocus': 0.0, 'alpha': -0.145}

# phase_pattern_filename = '2023_05_24-16_30__nxt=05_nyt=01_sepx=12.000_sepy=12.000_offx=93.09_offy=-93.09.pkl'
# # may 24, 2023
# command_dict = {'phase_pattern_file': phase_pattern_filename,
#                 'phase_pattern_folder': '',
#                 'shiftx': 10,
#                 'shifty': -10,
#                 'defocus': 0.0,
#                 'alpha': -0.145}

phase_pattern_filename = "2023_11_06-20_15__nxt=04_nyt=03_sepx=12.000_sepy=12.000_offx=93.09_offy=-93.09.pkl"
command_dict['phase_pattern_file'] = phase_pattern_filename

slm_phase_final = freq_funcs.pkread(save_path+array_type + phase_pattern_filename)


#### double check everything is working

phase_rad = slm_phase_final = freq_funcs.pkread('Z:\\Calculations\\Emily\\SLM project\\v4_array_patterns\\vary_num_detectors\\2024_01_08-00_44__4detect_nxt=03_nyt=03_sepx=8.000_sepy=8.000_offx=93.09_offy=-93.09.pkl')
#2024_01_08-00_44__3detect_nxt=03_nyt=03_sepx=8.000_sepy=8.000_offx=93.09_offy=-93.09.pkl')
#2024_01_08-01_54__1detect.pkl')
#2024_01_08-00_44__2detect_nxt=03_nyt=03_sepx=8.000_sepy=8.000_offx=93.09_offy=-93.09.pkl')



vfield_e = slm_attr.xe_ve(xu=beam_e, xphi=phase_rad)
vfield_i = slm_attr.e_i(vfield_e)

qim(vfield_i)

## check what happens to the image plane phase
# command_dict = {'target_sep': 3e-05, 'shiftx': 0, 'shifty': 0, 'defocus': 0.0, 'alpha': 0.0}
command_dict = {'target_sep': 2.74e-6, 'shiftx': 0, 'shifty': 0, 'defocus': 0.0, 'alpha': 0.0}

phase_rad = slm_attr.two_traps(**command_dict)
# phase_rad = slm_attr.pad_zeros(slm_attr.pad_square_pattern(phase_rad))  # this works, but it is so messy, need to fix it

vfield_e = slm_attr.xe_ve(xu=beam_e, xphi=phase_rad)
vfield_i = slm_attr.e_i(vfield_e)
vphi = np.angle(vfield_e)

y_index = 419
x0 = 580
x1 = 630

plt.figure()
plt.plot(vfield_i[y_index,x0:x1])
plt.show()

plt.figure()
plt.plot(vphi[y_index,x0:x1])
plt.show()

plt.figure()
plt.imshow(vfield_i[y_index-10:y_index+10:,x0:x1])
plt.colorbar()
plt.show()

plt.figure()
plt.imshow(vphi[y_index-10:y_index+10:,x0:x1])
plt.colorbar()
plt.show()


## params - if have not run wgs_alg already

# slm_attr = SLMx13138()
#
# # # fraction of total trapping plane to be used for array
# # # b/c of array indexing, do not set to 1 (can do 0.9 repeated)
# # bw = 0.22
#
# # Array params
# nx_traps = 10
# ny_traps = 2
# n_traps = nx_traps*ny_traps
#
# compensate_de = False
#
# sp_x = 9 						# separation between traps in pixels
# sp_y = sp_x
#
# # sp_x = 12 						# hexagonal array base tiling
# # sp_y = 6
#
# # sp_x = 8*2 						# hexagonal array base tiling
# # sp_y = 7*2
#
# offx = slm_attr.xt
# offy = slm_attr.yt
#
# # Algorithm
# lofa = False
# memory = True 				# of WGS scaling factor g. If false, use expression in Nogrette paper
#
# g_wgsa = 0.7	           		# g = 0 limits to GS
# # m_mraf = 0.6	           		# m = relative target intensity in signal region
# # offset_mraf = sys.float_info.epsilon
#
# # Iterations
# no_iter_wgs = 12
# no_iter = 50

## get the array indices

# array_type = "" # "arb"
# filename = "nxt={nx_traps:02d}_nyt={ny_traps:02d}_sepx={sp_x:.3f}_sepy={sp_y:.3f}_offx={offx:.2f}_offy={offy:.2f}.pkl".format(nx_traps=nx_traps, ny_traps=ny_traps, sp_x=sp_x, sp_y=sp_y, offx=offx, offy=offy)

# calculate trap indices
slm_attr.get_array_indices(nx_traps=nx_traps, ny_traps=ny_traps, sp_x=sp_x, sp_y=sp_y)

## arb arrays
# pic = imageio.imread(r'Z:\Calculations\Emily\SLM project\images\mit.png', pilmode='L')
#
# array_type = "arb\\"
#
# # mit
# lattice_spacing = 15
# threshold = 50
# downsample = 7
#
# # # cua
# # lattice_spacing = 4
# # threshold = 200
# # downsample = 7
#
# # # aws
# # lattice_spacing = 5
# # threshold = 200
# # downsample = 6
#
# pic = pic[0::downsample,0::downsample]
# # pic_mask = (pic < threshold)
# pic_mask = (pic > threshold)
#
# nyp, nxp = np.shape(pic)
# xmp, ymp = np.meshgrid(np.linspace(1,nxp,nxp), np.linspace(1,nyp,nyp))
#
# lattice_x = (xmp % lattice_spacing == 0)
# lattice_y = (ymp % lattice_spacing == 0)
#
# reg_lattice = (lattice_x & lattice_y)
#
# target_array = (pic_mask & reg_lattice)
# print(np.sum(target_array))
#
# slm_attr.set_array_indices(target_array=target_array, lattice_spacing=lattice_spacing, xt=slm_attr.xt+20)
#
# # draw target intensity distribution
# plt.figure()
# plt.imshow(slm_attr.vtarget0_i, cmap='binary')
# plt.colorbar()
# plt.plot(np.arange(slm_attr.n), np.repeat(slm_attr.ax,slm_attr.n),'b--')
# plt.plot(np.repeat(slm_attr.ax,slm_attr.n),np.arange(slm_attr.n),'b--')
# plt.title('Initial intensity distribution')
# plt.show()
#
# filename = 'mit_33traps_xt+20.pkl'
# # filename = 'cua_123traps_xt+20.pkl'
# # filename = 'aws_90traps_nocomp_xt+20.pkl'

## (I) WGSA feedback to camera

second_zelux = True

# create a display window on SLM
slm_win = slmpy.SLMdisplay(isImageLock=False, monitor=1)

# configure Zelux camera
sdk = TLCameraSDK()
camera = sdk.open_camera(sdk.discover_available_cameras()[0])

# setup the camera for continuous acquisition
camera.frames_per_trigger_zero_for_unlimited = 0
camera.image_poll_timeout_ms = 2000  # 2 second timeout
camera.arm(2)

# save these values to place in our custom TIFF tags later
bit_depth = camera.bit_depth
camera.exposure_time_us = 10000 #40 # 90 ## for second zelux # 200 ## for first zelux# 40 seems to be the minimum

# need to save the image width and height for color processing
image_width = camera.image_width_pixels
image_height = camera.image_height_pixels

# start triggering
camera.issue_software_trigger()

# ##
# plt.hist(img.flatten())
# plt.xlim([60e3, 70e3])
# plt.ylim([0, 100])
# plt.show()

## display phase and get image

phase_rad = slm_attr.array_traps(**command_dict)
phase_rad = slm_attr.pad_zeros(slm_attr.pad_square_pattern(phase_rad))  # this works, but it is so messy, need to fix it

# read the test correction pattern
corr_pattern_rad = -np.load(r"Z:\2022-data\2022-04\20220415-wf_correction\11_47_modesz=64_probesz=2\unwrapped_fitted.npy")

# comment the line below to remove correction pattern
phase_rad += corr_pattern_rad

# convert to bitmap
phase_int = slm_attr.convert_bmp(phase_rad, bit_depth = 255.)
phase_int8 = phase_int.astype(np.uint8)

slm_win.updateArray(phase_int8)
time.sleep(0.5)

frame = camera.get_pending_frame_or_null()
img = frame.image_buffer
# img = cv2.normalize(frame.image_buffer, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)
if second_zelux:
    img = np.flipud(img)
qim(img)

## get trap indices
# # Basler camera
# camera = pylon.InstantCamera(pylon.TlFactory_GetInstance().CreateFirstDevice())
# camera.Open()

# # this seems to work ok, but technically instrument() should be only called once,
# # saved, and passed around. closing does not require calling instrument() again.
# # once camera.close() is called, can open the software and stream feed as usual
# camera = instrument(list_instruments()[0], reopen_policy='reuse')
# camera.open()
#
# qim(camera.grab_image())

slm_attr.img_trap_xy = np.zeros(shape=(slm_attr.ny_traps,slm_attr.nx_traps,2), dtype=int)	# in the form (y,x), interpolated coordinates
slm_attr.fit_trap_xy =np.zeros(shape=(slm_attr.ny_traps,slm_attr.nx_traps,2)) 	# in the form (y,x), fitted coords
fit_params = np.empty(shape=(n_traps,3))	# return parameters of fit (height, width)

# 1. Zoom in on array
# img = take_image(camera)
# img = camera.grab_image()
# img = exp_int

plt.figure()
plt.imshow(img)
plt.get_current_fig_manager().window.showMaximized()
zoom = np.array(plt.ginput(2)).astype(int)			# Top left, Bottom right of zoomed region
plt.close()

zoomed = img[zoom[0][1]:zoom[1][1],zoom[0][0]:zoom[1][0]]

# 2. Get box size to do fitting/feedback
plt.figure()
plt.imshow(zoomed)
plt.get_current_fig_manager().window.showMaximized()
box = np.array(plt.ginput(2)).astype(int)					# Top left, Bottom right of box for each array
plt.close()

box_sz = int(np.linalg.norm(np.subtract(box[0],box[1]))/2) 	# cleaner indexing, use 1/2

# 3. Get location of array in camera, relative to the index of upper left corner displayed
plt.figure()
plt.imshow(zoomed)
plt.get_current_fig_manager().window.showMaximized()
corners = np.array(plt.ginput(3)).astype(int) 		# Top left, Top right, Bottom right, trap center
plt.close()

# # Old way
# # Locations of corner traps in image, in [x,y] form
# loc_1 = zoom[0] + corners[0]
# loc_nsq = zoom[0] + corners[1]
#
# # Scaling using linear dimensions of arrays
# array_sz = np.linalg.norm(np.subtract(slm_attr.trap_xy[0],slm_attr.trap_xy[-1])) 		# in numerics
# l1 = np.linalg.norm(np.subtract(corners[0],corners[1]))
# l2 = np.linalg.norm(np.subtract(corners[1],corners[2]))
# L = np.sqrt(2)*np.average([l1,l2])
# scale_factor = L/array_sz
#
#
# # Total angle of rotation in the image, positive is anti-clockwise
# # This works only for square arrays atm b/c doing pi/4 fixed rotation
# angle = get_angle_imshow(corners[0], corners[2])
# rm = rotation_matrix(angle)

## (1) for 1D arrays
# # Find points of maximum intensity, use that pixel as index
# sz = 10
# t1 = zoomed[corners[0][1]-sz:corners[0][1]+sz,corners[0][0]-sz:corners[0][0]+sz]
# tn = zoomed[corners[1][1]-sz:corners[1][1]+sz,corners[1][0]-sz:corners[1][0]+sz]
# tn2 = zoomed[corners[2][1]-sz:corners[2][1]+sz,corners[2][0]-sz:corners[2][0]+sz]
#
# dy0,dx0 = np.unravel_index(np.argmax(t1, axis=None), t1.shape)
# dy1,dx1 = np.unravel_index(np.argmax(tn, axis=None), tn.shape)
# dy2,dx2 = np.unravel_index(np.argmax(tn2, axis=None), tn2.shape)
#
# loc_1 = zoom[0] + corners[0] + [dy0-sz, dx0-sz]
# loc_n = zoom[0] + corners[1] + [dy1-sz, dx1-sz]
#
# # Locations of corner traps in image, in [x,y] form
# loc_1 = zoom[0] + corners[0]
# loc_n = zoom[0] + corners[1]
#
# # Scaling using linear dimensions of arrays
# array_sz = np.linalg.norm(np.subtract(slm_attr.trap_xy[0,0],slm_attr.trap_xy[-1,-1])) 		# in numerics
# L = np.linalg.norm(np.subtract(loc_1,loc_n))
# scale_factor = L/array_sz
#
# # Total angle of rotation in the image, positive is anti-clockwise
# # This works only for square arrays atm b/c doing pi/4 fixed rotation
# # # angle = -0.14295749959372162
# angle = -freq_funcs.get_angle_imshow(loc_1,loc_n)-np.pi/4
# rm = freq_funcs.rotation_matrix(angle)
#
# plt.figure()
# plt.imshow(img)
# for iy,ix in np.ndindex(slm_attr.trap_xy.shape[:2]):
#
# 	# Relative to index of first trap, in the form [y,x]
# 	rotated_vec = np.dot(rm, np.subtract(slm_attr.trap_xy[iy,ix],slm_attr.trap_xy[0,0]).reshape(2,1)).reshape(1,2)[0]
#
# 	# Scale from numerics to image dimensions
# 	rotated_vec_sc = (scale_factor*rotated_vec).astype(int)
#
# 	# New rotated coordinates
# 	slm_attr.img_trap_xy[iy, ix] = np.array([loc_1[1]+rotated_vec_sc[0],loc_1[0]+rotated_vec_sc[1]])
#
# 	plt.scatter(slm_attr.img_trap_xy[iy, ix][1],slm_attr.img_trap_xy[iy, ix][0])
# plt.show()
#
#
# # # Fit to peaks, update trap indices from image in fit_trap_xy
# # fitted_array = np.empty(shape=(cam.ny,cam.nx))
#

## (2) for square arrays
# # Find points of maximum intensity, use that pixel as index
# sz = 10
# t1 = zoomed[corners[0][1]-sz:corners[0][1]+sz,corners[0][0]-sz:corners[0][0]+sz]
# tn = zoomed[corners[1][1]-sz:corners[1][1]+sz,corners[1][0]-sz:corners[1][0]+sz]
# tn2 = zoomed[corners[2][1]-sz:corners[2][1]+sz,corners[2][0]-sz:corners[2][0]+sz]
#
# dy0,dx0 = np.unravel_index(np.argmax(t1, axis=None), t1.shape)
# dy1,dx1 = np.unravel_index(np.argmax(tn, axis=None), tn.shape)
# dy2,dx2 = np.unravel_index(np.argmax(tn2, axis=None), tn2.shape)
#
# loc_1 = zoom[0] + corners[0] + [dy0-sz, dx0-sz]
# loc_n = zoom[0] + corners[1] + [dy1-sz, dx1-sz]
# loc_nsq = zoom[0] + corners[2] + [dy2-sz, dx2-sz]
#
#
# # Locations of corner traps in image, in [x,y] form
# loc_1 = zoom[0] + corners[0]
# loc_n = zoom[0] + corners[1]
#
# # Scaling using linear dimensions of arrays
# array_sz = np.linalg.norm(np.subtract(slm_attr.trap_xy[0,0],slm_attr.trap_xy[-1,-1])) 		# in numerics
# l1 = np.linalg.norm(np.subtract(loc_1,loc_n))
# l2 = np.linalg.norm(np.subtract(loc_n,loc_nsq))
# L = np.sqrt(2)*np.average([l1,l2])
# scale_factor = L/array_sz
#
#
# # Total angle of rotation in the image, positive is anti-clockwise
# # This works only for square arrays atm b/c doing pi/4 fixed rotation
# # # angle = -0.14295749959372162
# angle = -freq_funcs.get_angle_imshow(loc_1,loc_nsq)
# rm = freq_funcs.rotation_matrix(angle)
#
# plt.figure()
# plt.imshow(img)
# for iy,ix in np.ndindex(slm_attr.trap_xy.shape[:2]):
#
# 	# Relative to index of first trap, in the form [y,x]
# 	rotated_vec = np.dot(rm, np.subtract(slm_attr.trap_xy[iy,ix],slm_attr.trap_xy[0,0]).reshape(2,1)).reshape(1,2)[0]
#
# 	# Scale from numerics to image dimensions
# 	rotated_vec_sc = (scale_factor*rotated_vec).astype(int)
#
# 	# New rotated coordinates
# 	slm_attr.img_trap_xy[iy, ix] = np.array([loc_1[1]+rotated_vec_sc[0],loc_1[0]+rotated_vec_sc[1]])
#
# 	plt.scatter(slm_attr.img_trap_xy[iy, ix][1],slm_attr.img_trap_xy[iy, ix][0])
# plt.show()

## for any arbitrary array
# Find points of maximum intensity, use that pixel as index
sz = 10
t1 = zoomed[corners[0][1]-sz:corners[0][1]+sz,corners[0][0]-sz:corners[0][0]+sz]
tn = zoomed[corners[1][1]-sz:corners[1][1]+sz,corners[1][0]-sz:corners[1][0]+sz]
tn2 = zoomed[corners[2][1]-sz:corners[2][1]+sz,corners[2][0]-sz:corners[2][0]+sz]

dy0,dx0 = np.unravel_index(np.argmax(t1, axis=None), t1.shape)
dy1,dx1 = np.unravel_index(np.argmax(tn, axis=None), tn.shape)
dy2,dx2 = np.unravel_index(np.argmax(tn2, axis=None), tn2.shape)

loc_1 = zoom[0] + corners[0] + [dy0-sz, dx0-sz]
# loc_n = zoom[0] + corners[1] + [dy1-sz, dx1-sz]
loc_nsq = zoom[0] + corners[2] + [dy2-sz, dx2-sz]

# # Locations of corner traps in image, in [x,y] form
# loc_1 = zoom[0] + corners[0]
# loc_n = zoom[0] + corners[1]

# Scaling using linear dimensions of arrays
array_sz = np.linalg.norm(np.subtract(slm_attr.trap_xy[0,0],slm_attr.trap_xy[-1,-1])) 		# in numerics
L = np.linalg.norm(np.subtract(loc_1,loc_nsq))
scale_factor = L/array_sz

# Total angle of rotation in the image, positive is anti-clockwise
# This works only for square arrays atm b/c doing pi/4 fixed rotation
# angle = -freq_funcs.get_angle_imshow(loc_1,loc_nsq)-np.pi/4
if second_zelux:
    angle = -0.03 # callibrated for the second zelux
else:
    angle = -0.128 # callibrated for the first zelux

rm = freq_funcs.rotation_matrix(angle)

plt.figure()
plt.imshow(img)
for iy,ix in np.ndindex(slm_attr.trap_xy.shape[:2]):

    # Relative to index of first trap, in the form [y,x]
    rotated_vec = np.dot(rm, np.subtract(slm_attr.trap_xy[iy,ix],slm_attr.trap_xy[0,0]).reshape(2,1)).reshape(1,2)[0]

    # Scale from numerics to image dimensions
    rotated_vec_sc = (scale_factor*rotated_vec).astype(int)

    # New rotated coordinates
    slm_attr.img_trap_xy[iy, ix] = np.array([loc_1[1]+rotated_vec_sc[0],loc_1[0]+rotated_vec_sc[1]])

    # plt.scatter(slm_attr.img_trap_xy[iy, ix][1],slm_attr.img_trap_xy[iy, ix][0])

    # trap region
    rect = patches.Rectangle((slm_attr.img_trap_xy[iy, ix][1] - box_sz,slm_attr.img_trap_xy[iy, ix][0] - box_sz),2*box_sz,2*box_sz, linewidth=1, edgecolor='w', facecolor='none')
    plt.gca().add_patch(rect)


plt.show()

# # Fit to peaks, update trap indices from image in fit_trap_xy
# fitted_array = np.empty(shape=(cam.ny,cam.nx))

## Measure intensity distribution

# # Extract heights
Itot = 0

fit_heights_fb = np.empty(shape=(slm_attr.ny_traps,slm_attr.nx_traps))

for iy,ix in np.ndindex(slm_attr.trap_xy.shape[:2]):

    (yid, xid) = slm_attr.img_trap_xy[iy,ix]

    # Don't do this, easier to get it from user input
    # box_sz = int(nbox*wt/px_b)

    # 1. Take max intensity within small region
    ydata = img[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz]

    if compensate_de:
        Ii = slm_attr.diff_eff[iy,ix]*np.amax(ydata)
    else:
        Ii = np.amax(ydata)

    if Ii == 0:
        raise ValueError('Encountered trap height of 0, scaling will divide by 0. Quit.')

    # store trap statistics
    fit_heights_fb[iy,ix] = Ii
    Itot += Ii

# Average trap height
Ibar = Itot/n_traps

# stdev_heights_fb[i] = np.std(fit_heights_fb[i]/Ibar) 		# stdevs normalized to 1


## Run iterations of camera feedback

no_iter_fb = 30

slm_phase_fb = np.empty(shape=(no_iter_fb,slm_attr.n,slm_attr.n))
v_phase_fb = np.full(shape=(no_iter_fb,slm_attr.n,slm_attr.n),fill_value=0.)

# g_dyn_fb = np.full(shape=(no_iter_fb,n_traps),fill_value=g_dyn[-1])

# last_g = np.array([9.32368080e+11, 7.52634963e+11, 6.18442254e+11, 5.64016542e+11,
# 4.12097263e+11, 9.10531872e+11, 6.85432745e+11, 4.37236936e+11,
# 4.99129713e+11, 3.41334517e+11, 9.74970579e+11, 7.61396585e+11,
# 6.97507440e+11, 5.44517057e+11, 5.07986180e+11, 1.01194484e+12,
# 6.29695867e+11, 6.10387522e+11, 9.13930471e+11, 2.76578725e+11,
# 1.38155897e+12, 9.21969573e+11, 8.05112186e+11, 4.54781775e+11,
# 7.66838353e+11])
# g_dyn_fb = np.full(shape=(no_iter_fb,n_traps),fill_value=last_g)

g_dyn_fb = np.full(shape=(no_iter_fb,slm_attr.ny_traps,slm_attr.nx_traps),fill_value=g_wgsa)

slm_phase_fb[0,:] = slm_phase_final.copy()

fit_heights_fb = np.empty(shape=(no_iter_fb,slm_attr.ny_traps,slm_attr.nx_traps))
avg_heights_fb = np.empty(shape=(no_iter_fb))
stdev_heights_fb = np.empty(shape=(no_iter_fb))

# # plot generated traps
# plt.ion()
#
# fig, ax = plt.subplots(figsize=(6,6))
# img_trap = ax.imshow(img, cmap='binary')

for i in range(no_iter_fb):

    print(i)

    vfield_e = slm_attr.xe_ve(xu=beam_e, xphi=slm_phase_fb[i])
    vfield_i = slm_attr.e_i(vfield_e)
    vphi = np.angle(vfield_e)

    if use_lofa:
        print('%s: fix' %(i))
        vphi = fix_vphi

    v_phase_fb[i] = vphi

    # # Extract heights
    Itot = 0

    for iy,ix in np.ndindex(slm_attr.trap_xy.shape[:2]):

        (yid, xid) = slm_attr.img_trap_xy[iy,ix]

        # Don't do this, easier to get it from user input
        # box_sz = int(nbox*wt/px_b)

        # 1. Take max intensity within small region
        ydata = img[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz]

        if compensate_de:
            Ii = slm_attr.diff_eff[iy,ix]*np.amax(ydata)
        else:
            Ii = np.amax(ydata)

        if Ii == 0:
            raise ValueError('Encountered trap height of 0, scaling will divide by 0. Quit.')

        # store trap statistics
        fit_heights_fb[i,iy,ix] = Ii
        Itot += Ii

        # 2. fit maximum
        # meshx = slm_attr.xm_b[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz]
        # meshy = slm_attr.ym_b[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz]
        #
        # xdata = np.vstack((meshx.ravel(),meshy.ravel()))
        # ydata = img[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz].ravel()
        #
        # # Returns [amplitude, widthx, widthy, x0, y0]
        # # [amplitude, widthx, widthy] stored in fit_params
        # # [x0, y0] stored in fit_trap_xy
        # popt, pcov = scipy.optimize.curve_fit(
        # 	gauss2d_fit,
        # 	xdata = xdata,
        # 	ydata = ydata,
        # 	# p0 = (np.max(ydata), wt/px_b, wt/px_b, xid, yid),
        # 	bounds = ([0, 1, 1, xid-box_sz, yid-box_sz], [1, box_sz, box_sz, xid+box_sz, yid+box_sz]),
        # 	# sigma = n.sqrt(img[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz].ravel())
        # )
        #
        # fitted_array += gauss2d_plot_fit((slm_attr.xm_b,slm_attr.ym_b), *popt)
        #
        # # Extract fit params
        # x0, y0 = int(popt[3]), int(popt[4])
        # amp, widthx, widthy = popt[0:3]
        #
        # plt.figure()
        # plt.plot(ydata)
        # plt.plot(amp*gauss2d_int(meshx,meshy,widthx,widthy,x0,y0).ravel(),'--')
        # plt.show()
        #
        # # Save params
        # fit_trap_xy[curr] = (y0,x0)
        # fit_params[curr] = [amp, widthx, widthy]

    # Average trap height
    Ibar = Itot/n_traps

    avg_heights_fb[i] = Ibar
    stdev_heights_fb[i] = np.std(fit_heights_fb[i]/Ibar) 		# stdevs normalized to 1

    # # # # Update target
    vtarget_i_new = np.power(slm_attr.vtarget0_e, 2)

    for iy,ix in np.ndindex(slm_attr.trap_xy.shape[:2]):

        (yid, xid) = slm_attr.trap_xy[iy,ix]

        Ii = fit_heights_fb[i,iy,ix]

        #  check special case
        if iy == 0 and ix == 9:

            # # # # normal
            if use_memory:
                g_new = 2*Ibar/Ii*g_dyn_fb[i,iy,ix]
                vtarget_i_new[yid, xid] *= g_new

            else:
                vtarget_i_new[yid, xid] = 2*Ibar/(1-g_wgsa*(1-Ii/Ibar))
            # # # # # #

        else:
            if use_memory:
                g_new = Ibar/Ii*g_dyn_fb[i,iy,ix]
                vtarget_i_new[yid, xid] *= g_new

            else:
                vtarget_i_new[yid, xid] = Ibar/(1-g_wgsa*(1-Ii/Ibar))

    vtarget_e_new = np.sqrt(vtarget_i_new)

    xfield_e = slm_attr.ve_xe(vu=vtarget_e_new, vphi=vphi)
    # xfield_i = slm_attr.e_i(xfield_e)
    xphi = np.angle(xfield_e)

    # Update data
    if i == no_iter_fb-1:
        break

    slm_phase_fb[i+1] = xphi
    g_dyn_fb[i+1] = np.multiply(np.divide(Ibar, fit_heights_fb[i]), g_dyn_fb[i])

    # Update SLM and take new image
    command_dict = {'phase_pattern_file': xphi, 'phase_pattern_folder': '','shiftx': 7.8, 'shifty': -31.0, 'defocus': 0.0, 'alpha': -0.145}
    phase_rad = slm_attr.array_traps(**command_dict)
    phase_rad = slm_attr.pad_zeros(slm_attr.pad_square_pattern(phase_rad))  # this works, but it is so messy, need to fix it
    # comment the line below to remove correction pattern
    phase_rad += corr_pattern_rad
    # convert to bitmap
    phase_int = slm_attr.convert_bmp(phase_rad, bit_depth = 255.)
    phase_int8 = phase_int.astype(np.uint8)
    slm_win.updateArray(phase_int8)
    time.sleep(0.5)

    # take image
    frame = camera.get_pending_frame_or_null()
    img = frame.image_buffer
    # img = cv2.normalize(frame.image_buffer, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)
    if second_zelux:
        img = np.flipud(img)

    # img = take_image(camera)

    # img_trap.set_data(img)
    # img_trap.autoscale()
    #
    # fig.canvas.draw()
    # fig.canvas.flush_events()

slm_phase_final_fb = slm_phase_fb[-1].copy()

if second_zelux:
    newfilename = filename.strip('.pkl') + '_feedback2.pkl'
else:
    newfilename = filename.strip('.pkl') + '_feedback1.pkl'

# save the phase
freq_funcs.pkwrite(var=slm_phase_final_fb, fileName=save_path+array_type + base_filename + newfilename)

# # save the phase
# pkwrite(var=slm_phase_final_fb, fileName=fb_folder + 'final_phases_feb3\\' + filename)
# pkwrite(var=fit_heights_fb, fileName=fb_folder + 'heights(t)_feb3\\'+ filename)
#
# camera.Close()

## (II) WGSA feedback to atomic signal

# just the phase - for simulation purposes
command_dict = {'phase_pattern_file': '2022_07_29-12_21__nxt=10_nyt=01_sepx=8.000_sepy=8.000_offx=93.09_offy=-93.09.pkl', 'phase_pattern_folder': '', 'shiftx': 0, 'shifty': 0, 'defocus': 0.0, 'alpha': 0}

command_dict['phase_pattern_file'] = '2022_08_02-18_06__nxt=10_nyt=02_sepx=9.000_sepy=9.000_offx=93.09_offy=-93.09.pkl'

slm_phase_final = slm_attr.array_traps(**command_dict)

## Run iterations of camera feedback

no_iter_fb = 30

slm_phase_fb = np.empty(shape=(no_iter_fb,slm_attr.n,slm_attr.n))
v_phase_fb = np.full(shape=(no_iter_fb,slm_attr.n,slm_attr.n),fill_value=0.)

# g_dyn_fb = np.full(shape=(no_iter_fb,n_traps),fill_value=g_dyn[-1])

# last_g = np.array([9.32368080e+11, 7.52634963e+11, 6.18442254e+11, 5.64016542e+11,
# 4.12097263e+11, 9.10531872e+11, 6.85432745e+11, 4.37236936e+11,
# 4.99129713e+11, 3.41334517e+11, 9.74970579e+11, 7.61396585e+11,
# 6.97507440e+11, 5.44517057e+11, 5.07986180e+11, 1.01194484e+12,
# 6.29695867e+11, 6.10387522e+11, 9.13930471e+11, 2.76578725e+11,
# 1.38155897e+12, 9.21969573e+11, 8.05112186e+11, 4.54781775e+11,
# 7.66838353e+11])
# g_dyn_fb = np.full(shape=(no_iter_fb,n_traps),fill_value=last_g)

g_dyn_fb = np.full(shape=(no_iter_fb,slm_attr.ny_traps,slm_attr.nx_traps),fill_value=g_wgsa)

# slm_phase_fb[0,:] = slm_phase_final.copy()
slm_phase_fb[0,:] = slm_phase_final_fb.copy()

fit_heights_fb = np.empty(shape=(no_iter_fb,slm_attr.ny_traps,slm_attr.nx_traps))
avg_heights_fb = np.empty(shape=(no_iter_fb))
stdev_heights_fb = np.empty(shape=(no_iter_fb))

# adjust target via "compensate_de" code
compensate_de = True

# meas_od_list = np.array([0.7884452611845753, 0.9327409658662432, 0.9311851482339732, 1.712237958067231, 1.1813071804204847, 0.9855566240172454, 0.42982405071948065, 0.587711629348009, 0.46944353017368456, 0.28794701236835607, 0.7550399071870649, 0.45120688962254474, 0.47039599761083, 0.7876003218859765, 1.08858129963778, 0.9566200701044003, 0.4834339228917738, 0.6869115484305246, 0.5055728334256517, 0.24492234150800776])

meas_od_list = np.array([0.5982253461136325, 0.3108098054629378, 0.2944932869979604, 0.3553555421014914, 0.25685604691913244, 0.3911752601880752, 0.5595541429949753, 0.5890986654827486, 0.7054072546074585, 0.6773692579664783, 0.5813507046934341, 0.538237850387046, 0.5815822515691409, 0.5355058176481525, 0.3540926252573995, 0.5828244347406221, 0.5604924627663059, 0.5106484801468603, 0.6895477148295388, 0.9141867886501025])

meas_od_list = np.reshape(meas_od_list, slm_attr.trap_xy.shape[:2])


# # plot generated traps
# plt.ion()
#
# fig, ax = plt.subplots(figsize=(6,6))
# img_trap = ax.imshow(img, cmap='binary')

for i in range(no_iter_fb):

    print(i)

    vfield_e = slm_attr.xe_ve(xu=beam_e, xphi=slm_phase_fb[i])
    vfield_i = slm_attr.e_i(vfield_e)
    vphi = np.angle(vfield_e)

    if lofa:
        print('%s: fix' %(i))
        vphi = fix_vphi

    v_phase_fb[i] = vphi

    # # Extract heights
    Itot = 0

    for iy,ix in np.ndindex(slm_attr.trap_xy.shape[:2]):

        (yid, xid) = slm_attr.trap_xy[iy,ix]

        # Don't do this, easier to get it from user input
        # box_sz = int(nbox*wt/px_b)

        # 1. Take max intensity within small region
        # ydata = vfield_i[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz]
        ydata = vfield_i[yid,xid]

        if compensate_de:
            # Ii = slm_attr.diff_eff[iy,ix]*np.amax(ydata)
            Ii = meas_od_list[iy,ix]*np.amax(ydata)
        else:
            Ii = np.amax(ydata)

        if Ii == 0:
            raise ValueError('Encountered trap height of 0, scaling will divide by 0. Quit.')

        # store trap statistics
        fit_heights_fb[i,iy,ix] = Ii
        Itot += Ii

        # 2. fit maximum
        # meshx = slm_attr.xm_b[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz]
        # meshy = slm_attr.ym_b[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz]
        #
        # xdata = np.vstack((meshx.ravel(),meshy.ravel()))
        # ydata = img[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz].ravel()
        #
        # # Returns [amplitude, widthx, widthy, x0, y0]
        # # [amplitude, widthx, widthy] stored in fit_params
        # # [x0, y0] stored in fit_trap_xy
        # popt, pcov = scipy.optimize.curve_fit(
        # 	gauss2d_fit,
        # 	xdata = xdata,
        # 	ydata = ydata,
        # 	# p0 = (np.max(ydata), wt/px_b, wt/px_b, xid, yid),
        # 	bounds = ([0, 1, 1, xid-box_sz, yid-box_sz], [1, box_sz, box_sz, xid+box_sz, yid+box_sz]),
        # 	# sigma = n.sqrt(img[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz].ravel())
        # )
        #
        # fitted_array += gauss2d_plot_fit((slm_attr.xm_b,slm_attr.ym_b), *popt)
        #
        # # Extract fit params
        # x0, y0 = int(popt[3]), int(popt[4])
        # amp, widthx, widthy = popt[0:3]
        #
        # plt.figure()
        # plt.plot(ydata)
        # plt.plot(amp*gauss2d_int(meshx,meshy,widthx,widthy,x0,y0).ravel(),'--')
        # plt.show()
        #
        # # Save params
        # fit_trap_xy[curr] = (y0,x0)
        # fit_params[curr] = [amp, widthx, widthy]

    # Average trap height
    Ibar = Itot/n_traps

    avg_heights_fb[i] = Ibar
    stdev_heights_fb[i] = np.std(fit_heights_fb[i]/Ibar) 		# stdevs normalized to 1

    # # # # Update target
    vtarget_i_new = np.power(slm_attr.vtarget0_e, 2)

    for iy,ix in np.ndindex(slm_attr.trap_xy.shape[:2]):

        (yid, xid) = slm_attr.trap_xy[iy,ix]

        Ii = fit_heights_fb[i,iy,ix]

        #  check special case
        if iy == 0 and ix == 9:

            # # # # normal
            if memory:
                g_new = 2*Ibar/Ii*g_dyn_fb[i,iy,ix]
                vtarget_i_new[yid, xid] *= g_new

            else:
                vtarget_i_new[yid, xid] = 2*Ibar/(1-g_wgsa*(1-Ii/Ibar))
            # # # # # #

        else:
            if memory:
                g_new = Ibar/Ii*g_dyn_fb[i,iy,ix]
                vtarget_i_new[yid, xid] *= g_new

            else:
                vtarget_i_new[yid, xid] = Ibar/(1-g_wgsa*(1-Ii/Ibar))

    vtarget_e_new = np.sqrt(vtarget_i_new)

    xfield_e = slm_attr.ve_xe(vu=vtarget_e_new, vphi=vphi)
    # xfield_i = slm_attr.e_i(xfield_e)
    xphi = np.angle(xfield_e)

    # Update data
    if i == no_iter_fb-1:
        break

    slm_phase_fb[i+1] = xphi
    g_dyn_fb[i+1] = np.multiply(np.divide(Ibar, fit_heights_fb[i]), g_dyn_fb[i])

slm_phase_final_fb = slm_phase_fb[-1].copy()


newfilename = filename.strip('.pkl') + '_feedback_od2.pkl'

# save the phase
freq_funcs.pkwrite(var=slm_phase_final_fb, fileName=save_path+array_type + base_filename + newfilename)

# # save the phase
# pkwrite(var=slm_phase_final_fb, fileName=fb_folder + 'final_phases_feb3\\' + filename)
# pkwrite(var=fit_heights_fb, fileName=fb_folder + 'heights(t)_feb3\\'+ filename)
#
# camera.Close()

## show the distributin of intensities
# qim(fit_heights_fb[0])
# qim(fit_heights_fb[-1])

plt.figure()

# for arbitrary arrays
int_dist = fit_heights_fb[0].flatten()
plt.hist(int_dist, alpha=0.5, label='before, stdev/mean={err:.2f}%'.format(err=np.std(int_dist)/np.mean(int_dist)*100))

int_dist = fit_heights_fb[9].flatten()
plt.hist(int_dist, alpha=0.5, label='round 10, stdev/mean={err:.2f}%'.format(err=np.std(int_dist)/np.mean(int_dist)*100))

int_dist = fit_heights_fb[19].flatten()
plt.hist(int_dist, alpha=0.5, label='round 20, stdev/mean={err:.2f}%'.format(err=np.std(int_dist)/np.mean(int_dist)*100))

int_dist = fit_heights_fb[29].flatten()
plt.hist(int_dist, alpha=0.5, label='round 30, stdev/mean={err:.2f}%'.format(err=np.std(int_dist)/np.mean(int_dist)*100))

plt.legend()
plt.show()

## Get 1D cut
# camera = instrument(list_instruments()[0], reopen_policy='reuse')
camera = instrument(list_instruments()[0])
camera.open()

# camera = pylon.InstantCamera(pylon.TlFactory_GetInstance().CreateFirstDevice())
# camera.Open()

tau = '.5ms'

slm.updateArray(slm_attr.unif)
bgimg = camera.grab_image(exposure_time=tau)

xaxis = True
# filename = 'w0=5.68mm_nxt=1_bw=0.45_offs=True_sp=4.pkl'
filename = 'w0=5.68mm_nxt=2_bw=0.225_offs=True_sp=20.pkl'
slm_final = pkread('Tests/2021_03_14/twotrap_x/' + filename)

# fixing dimensions
slm_full = np.zeros(shape=(1024,1272))
slm_full[:,side:1272-side] = slm_final.copy()

slm_full_disp = slm_attr.convert_bmp(slm_full,corr=True)
slm.updateArray(slm_full_disp)

# img = take_image(camera)
img = camera.grab_image(exposure_time=tau)

##
if xaxis != True:
	img = np.transpose(img.copy())
	bgimg = np.transpose(bgimg.copy())

# plt.figure()
# plt.imshow(img)
# plt.get_current_fig_manager().window.showMaximized()
# zoom = np.array(plt.ginput(2)).astype(int)			# Top left, Bottom right of zoomed region
# plt.close()

signal = img[zoom[0][1]:zoom[1][1],zoom[0][0]:zoom[1][0]].astype(np.float16) - 	     			bgimg[zoom[0][1]:zoom[1][1],zoom[0][0]:zoom[1][0]].astype(np.float16)

zoom_raw = signal
zoom_interp = np.abs(zoom_raw).astype(np.uint8)

# 2. Get box size to do fitting/feedback
plt.figure()
plt.imshow(zoom_interp)
plt.get_current_fig_manager().window.showMaximized()
index = np.array(plt.ginput(2)).astype(int)
plt.close()

tot = index
# tot = zoom

sz = 5
t1 = zoom_interp[tot[0][1]-sz:tot[0][1]+sz,tot[0][0]-sz:tot[0][0]+sz]
tn = zoom_interp[tot[1][1]-sz:tot[1][1]+sz,tot[1][0]-sz:tot[1][0]+sz]

dy0,dx0 = np.unravel_index(np.argmax(t1, axis=None), t1.shape)
dy1,dx1 = np.unravel_index(np.argmax(tn, axis=None), tn.shape)

# tot = zoom[0] + index
# # tot = zoom
#
# sz = 5
# t1 = img[tot[0][1]-sz:tot[0][1]+sz,tot[0][0]-sz:tot[0][0]+sz]
# tn = img[tot[1][1]-sz:tot[1][1]+sz,tot[1][0]-sz:tot[1][0]+sz]
#
# dy0,dx0 = np.unravel_index(np.argmax(t1, axis=None), t1.shape)
# dy1,dx1 = np.unravel_index(np.argmax(tn, axis=None), tn.shape)

y0 = tot[0][1]-sz+dy0
x0 = tot[0][0]-sz+dx0

y1 = tot[1][1]-sz+dy1
x1 = tot[1][0]-sz+dx1

cam = Camera()

# # x0, y0 = tot[0][0], tot[0][1]
# # x1, y1 = tot[1][0], tot[1][1]
#
# m = (y1-y0)/(x1-x0)
#
# xp = np.arange(np.shape(zoom_interp)[1])
# yp = m*xp + (y0-x0*m)
#
# zi = scipy.ndimage.map_coordinates(np.transpose(zoom_interp), np.vstack((xp,yp))) # THIS SEEMS TO WORK CORRECTLY
#
# fig, axes = plt.subplots(nrows=2)
# axes[0].imshow(zoom_interp,cmap='binary')
# axes[0].plot([x0, x1], [y0, y1], 'ro-')
# axes[0].axis('image')
#
# axes[1].plot(zi)
#
# plt.show()


# Get ratio of center peak height vs total trap height

midx = int(np.mean([x0,x1]))
midy = int(np.mean([y0,y1]))

# 1D single pixel
# window = 2
# trap_int = zoom_raw[y0,x0] + zoom_raw[y1,x1]
mid_int = np.max(zoom_raw[midy-window:midy+window,midx-window:midx+window])

# 2D slice sum
ysum = 4
summed = np.sum(zoom_raw[midy-ysum:midy+ysum,:],axis=0)

trap_int = np.max(summed[x0-window:x0+window]) + np.max(summed[x1-window:x1+window])
mid_int = np.max(summed[midx-window:midx+window])

sg.append(mid_int/trap_int)

print(mid_int)
print(trap_int)

qp(summed)

##
yslicesep = np.arange(4,22)

yslicesg = [0.2417, 0.1512, 0.0725, 0.0786, 0.0566, 0.01065, 0.010796, 0.009964, 0.002527, 0.001717, 0.0016775, 0.002718, 0.0027, 0.00184, 0.002901, 0.00188, 0.001871, 0.003756]

xslicesep = np.arange(4,21)

xslicesg = [0.3857, 0.2295, 0.1036, 0.0851, 0.05334, 0.01813, 0.01826, 0.01093, 0.01563, 0.01944, 0.00642, 0.00955, 0.011795, 0.011795, 0.002575, 0.005318, 0.002642]


# yslicesep = [4,  5,  6,  7,  8,  9,  10, 12, 14, 20]
# yslicesg = [0.1714  , 0.1186  , 0.082   , 0.0819  , 0.04843 , 0.02975 ,	0.01138 , 			0.00496 , 0.012436, 0.001812]
#
# xslicesep=np.arange(4,21)
#
# xslicesg = [0.3628, 0.2113, 0.093, 0.0949, 0.0355,   0.01865, 0.01385, 0.00917,  0.01534,  0.02, 0.00608, 0.004414, 0.013756, 0.007812, 0.002617, 0.003443, 0.002647]

plt.plot(xslicesep, xslicesg)
plt.plot(yslicesep, yslicesg)
plt.legend(['X', 'Y'])
plt.show()

## Analyze
# temp = pkread(fileName=fb_folder + 'heights(t)\\'+ filename)

plt.figure()
for i in range(n_traps):
	plt.plot(fit_heights_fb[:,i])
plt.show()

##  Show fitted array
# calc_array = np.empty(shape=(cam.ny,cam.nx))
#
# for curr in range(n_traps):
# 	xid = img_trap_xy[curr][1]
# 	yid = img_trap_xy[curr][0]
#
# 	amp = np.max(img[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz])
#
# 	calc_array += amp*gauss2d_int(slm_attr.xm_b,slm_attr.ym_b,wx=slm_attr.n/np.pi/(w0/px),wy=slm_attr.n/np.pi/(w0/px),x0=trap_xy[curr][1], y0=trap_xy[curr][0])
#
# plt.figure()
# plt.imshow(img, cmap='binary')
# plt.colorbar()
# plt.scatter([img_trap_xy[i][1] for i in range(len(img_trap_xy))],[img_trap_xy[i][0] for i in range(len(img_trap_xy))])
# plt.show()

# plt.figure()
# plt.plot(trap_xy)
# plt.plot(fit_trap_xy)
# plt.show()

# # Close the devices
# slm.close()
# camera.Close()

## Averaging over many instances of initial phase
#
# # # Params
# nbox = int(trap_spacing/2)
# ncheck = 1
#
# lofa = True 			# After no_iter_wgs
# memory = True 		# of scaling factor g. If false, use expression in Nogrette paper. else, use LOFA
#
# no_trials = 1000
#
# no_iter_wgs = 12
# no_iter = 50
#
# # Normal lofa
# # no_lofa = no_iter-no_iter_wgs
# # no_wgs = 0
#
# no_lofa = 3
# no_wgs = 7
#
# n_loop = no_wgs + no_lofa
#
# # # Choose random traps
# # rt1 = int(n_traps*np.random.rand(1))
# # rt2 = int(n_traps*np.random.rand(1))
# # rt3 = int(n_traps*np.random.rand(1))
# # rt1 = 5
# # rt2 = 178
# # rt3 = 232
# # rt4 = 390
# rt1 = 5
# rt2 = 18
# rt3 = 42
# rt4 = 84
#
# g_dyn = np.full(shape=(no_trials,no_iter,n_traps),fill_value=g_wgsa)
#
# fit_heights = np.empty(shape=(no_trials,no_iter,n_traps))
# avg_heights = np.empty(shape=(no_trials,no_iter))
# stdev_heights = np.empty(shape=(no_trials,no_iter))
#
# # SLM plane
# beam_i = normalize2d(gauss2d_int(x=slm_attr.xm, y=slm_attr.ym, wx=w0/slm_attr.px, wy=w0/slm_attr.px, x0=slm_attr.ax, y0=slm_attr.ax))
# beam_e = np.sqrt(beam_i)
#
# init_phase = 2*np.pi*np.random.rand(no_trials,slm_attr.n,slm_attr.n)
#
# for ptr in range(no_trials):
# 	print(ptr)
# 	xphi = init_phase[ptr]
#
# 	for i in range(no_iter):
#
# 		vfield_e = slm_attr.xe_ve(xu=beam_e, xphi=xphi)
# 		vfield_i = slm_attr.e_i(vfield_e)
# 		vphi = np.angle(vfield_e)
#
# 		# # # # # Check to make sure nbox is appropriate, plot 4 random traps
# 		# if i == ncheck:
# 		# 	checkfig, checkax = plt.subplots(2,2)
# 		#
# 		# 	(yid1,xid1) = trap_xy[rt1]
# 		# 	checkax[0,0].imshow(vfield_i[yid1-nbox:yid1+nbox,xid1-nbox:xid1+nbox])
# 		#
# 		# 	(yid2,xid2) = trap_xy[rt2]
# 		# 	checkax[0,1].imshow(vfield_i[yid2-nbox:yid2+nbox,xid2-nbox:xid2+nbox])
# 		#
# 		# 	(yid3,xid3) = trap_xy[rt3]
# 		# 	checkax[1,0].imshow(vfield_i[yid3-nbox:yid3+nbox,xid3-nbox:xid3+nbox])
# 		#
# 		# 	(yid4,xid4) = trap_xy[rt4]
# 		# 	checkax[1,1].imshow(vfield_i[yid4-nbox:yid4+nbox,xid4-nbox:xid4+nbox])
# 		#
# 		# 	plt.pause(0.1)
# 		# 	checkfig.show()
# 		#
# 		# 	value = input("Is a single trap being resolved?\nIf not, hit 'n'. Otherwise, hit any other key.\n")
# 		# 	if value == 'n' or value == 'N':
# 		# 		raise ValueError('Input "n", redefine nbox.')
# 		#
# 		# 	else:
# 		# 		print('nbox OK, continue.')
# 		# 		time.sleep(5)
# 		# 	plt.close(checkfig)
#
# 		if lofa and i >= no_iter_wgs:
#
# 			if np.mod(i-no_iter_wgs, n_loop) == 0:
# 				# print('%s: extract vphi' %(i))
# 				fix_vphi = vphi
#
# 			elif np.mod(i-no_iter_wgs, n_loop) < no_lofa:
# 				# print('%s: fix vphi' %(i))
# 				vphi = fix_vphi
#
# 			# else:
# 			# 	print('%s: update vphi' %(i))
#
# 			# if lofa:
# 			# 	if i == no_iter_wgs:
# 			# 		print('%s: extract vphi' %(i))
# 			# 		fix_vphi = vphi
# 			#
# 			# 	elif i > no_iter_wgs:
# 			# 		vphi = fix_vphi
#
# 		# # # # Extract heights
# 		Itot = 0.
# 		for curr in range(n_traps):
# 			(yid,xid) = slm_attr.trap_xy[curr]
#
# 			# Ok for numerics for now
# 			Ii = np.amax(vfield_i[yid-slm_attr.nbox:yid+slm_attr.nbox,xid-slm_attr.nbox:xid+slm_attr.nbox])
#
# 			if Ii == 0 or np.isnan(Ii):
# 				raise ValueError('Encountered trap height of 0/nan. Quit.')
#
# 			fit_heights[ptr,i,curr] = Ii
# 			Itot += Ii
#
# 		Ibar = Itot/n_traps
#
# 		avg_heights[ptr,i] = Ibar
# 		stdev_heights[ptr,i] = np.std(fit_heights[ptr,i]/Ibar) 		# stdevs normalized to 1
#
# 		# # # # Update target
# 		vtarget_i_new = np.power(vtarget0_e, 2)
#
# 		for curr in range(n_traps):
# 			Ii = fit_heights[ptr,i,curr]
#
# 			if memory:
# 				g_new = Ibar/Ii*g_dyn[ptr,i,curr]
# 				vtarget_i_new[slm_attr.trap_xy[curr]] *= g_new
#
# 			else:
# 				vtarget_i_new[slm_attr.trap_xy[curr]] = Ibar/(1-g_wgsa*(1-Ii/Ibar))
#
# 		vtarget_e_new = np.sqrt(vtarget_i_new)
#
# 		xfield_e = slm_attr.ve_xe(vu=vtarget_e_new, vphi=vphi)
# 		xphi = np.angle(xfield_e)
#
# 		# Update data
# 		if i == no_iter-1:
# 			break
#
# 		if memory:
# 			g_dyn[ptr,i+1] = np.multiply(np.divide(Ibar, fit_heights[ptr,i]), g_dyn[ptr,i])
#
# # plt.savefig(base_folder + base_filename + '.pdf', transparent=True)
# # pickle.dump(fig, open(base_folder + base_filename +'data.fig.pickle', 'wb'))
# # figx = pickle.load(open(base_folder + base_filename +'data.fig.pickle', 'rb'))
#
# stdev_stdev_heights = np.empty(no_iter)
# mean_stdev_heights = np.empty(no_iter)
#
# for i in range(no_iter):
# 	stdev_stdev_heights[i] = np.std(stdev_heights[:,i])
# 	mean_stdev_heights[i] = np.average(stdev_heights[:,i])
#
# plt.figure()
# plt.plot(np.arange(no_iter),mean_stdev_heights,'r--')
# for i in range(no_trials):
# 	plt.plot(np.arange(no_iter),stdev_heights[i])
# plt.show()
#
# # Saving the objects:
# with open(base_folder + base_filename + 'mixed_nwgs=12_full_vars.pkl', 'wb') as f:
# 	pickle.dump([stdev_heights, stdev_stdev_heights, mean_stdev_heights], f)

## Plot FT result
# plt.figure()
# plt.imshow(slm_attr.xe_vi(xu=beam_e, xphi=xphi),cmap='binary')
# plt.plot([slm_attr.ax,slm_attr.ax],[0,slm_attr.n],'b--',alpha=.2)
# plt.plot([0,slm_attr.n],[slm_attr.ax,slm_attr.ax],'b--',alpha=.2)
# plt.xlim([0,slm_attr.n])
# plt.ylim([slm_attr.n,0])
# plt.show()

## stdev of trap height distribution, averaged over many instances of initial (random) phase

# WGS
wgs_f = '2020_12_18-00_50__gs_full_vars.pkl'
wgs_q = '2020_12_18-16_50__gs_quarter_vars.pkl'

# WGS memory
wgsm_f = '2020_12_17-01_21__wgs_full_vars.pkl'
wgsm_q = '2020_12_18-22_27__wgs_quarter_vars.pkl'

# LOFA
lofa_f = '2020_12_16-20_12__lofa_nwgs=12_full_vars.pkl'
lofa_q = '2020_12_19-22_21__lofa_nwgs=12_quarter_vars.pkl'
# lofa_q = '2020_12_19-13_07__lofa_nwgs=15_quarter_vars.pkl'

# Mixed
mix_f = '2020_12_20-02_54__mixed_nwgs=12_full_vars.pkl'
# mix_f = '2020_12_17-18_40__mixed_nwgs=15_full_vars.pkl'

# WGS
with open('Images/full/' + wgs_f,'rb') as f:
	swgs, sswgs, uwgs = pickle.load(f)
# wgs_min = np.argmin(swgs[:,-1])
# wgs_max = np.argmax(swgs[:,-1])

# WGS memory
with open('Images/full/' + wgsm_f,'rb') as f:
	swgsm, sswgsm, uwgsm = pickle.load(f)
# wgsm_min = np.argmin(swgsm[:,-1])
# wgsm_max = np.argmax(swgsm[:,-1])

# LOFA
with open('Images/full/' + lofa_f,'rb') as f:
	slofa, sslofa, ulofa = pickle.load(f)
# lofa_min = np.argmin(slofa[:,-1])
# lofa_max = np.argmax(slofa[:,-1])

# # Mixed
# with open('Images/full/' + mix_q,'rb') as f:
# 	smix, ssmix, umix = pickle.load(f)

# Plot together with errorbars = standard deviation over all instances

xlims = [0,no_iter]
log_lims = [10**-6,10**0]

plt.figure()
plt.xlim(xlims)
plt.ylim(log_lims)
plt.yscale('log')
plt.xlabel('Iteration no.')
plt.ylabel('Intensity [normalized]')

asm = 0.3
alg = 0.4
# Averages (for legend)
plt.plot(np.arange(no_iter), uwgs, 'g--')
plt.plot(np.arange(no_iter), uwgsm, 'b--')
plt.plot(np.arange(no_iter), ulofa, 'r--')
# plt.plot(np.arange(no_iter), umix, 'm--')

# plt.legend(['WGS Memory', 'LOFA', 'Mixed'])
plt.legend(['WGS','WGS Memory', 'LOFA'])

# WGS
# plt.plot(np.arange(no_iter), swgs[wgs_min], 'g--', alpha=asm)
# plt.plot(np.arange(no_iter), swgs[wgs_max], 'g--', alpha=asm)
plt.fill_between(np.arange(no_iter), uwgs + sswgs, uwgs - sswgs, facecolor='g', alpha=alg)

# WGS Memory
# plt.plot(np.arange(no_iter), swgsm[wgsm_min], 'b--', alpha=asm)
# plt.plot(np.arange(no_iter), swgsm[wgsm_max], 'b--', alpha=asm)
plt.fill_between(np.arange(no_iter), uwgsm + sswgsm, uwgsm - sswgsm, facecolor='b', alpha=alg)

# LOFA
# plt.plot(np.arange(no_iter), slofa[lofa_min], 'r--', alpha=asm)
# plt.plot(np.arange(no_iter), slofa[lofa_max], 'r--', alpha=asm)
plt.fill_between(np.arange(no_iter), ulofa + sslofa, ulofa - sslofa, facecolor='r', alpha=alg)
plt.plot([12+1]*2, log_lims, 'k', linewidth=2, alpha=asm)

plt.plot(np.arange(no_iter), stdev_heights)
# # Mixed
# plt.fill_between(np.arange(no_iter), umix + ssmix, umix - ssmix, facecolor='m', alpha=alg)
# # no_iter_wgs=12, n_loop=10
# plt.plot([12+1]*2, log_lims, 'k', linewidth=2, alpha=asm)
# plt.plot([12+1+1*10]*2, log_lims, 'k', linewidth=2, alpha=asm)
# plt.plot([12+1+2*10]*2, log_lims, 'k', linewidth=2, alpha=asm)
# plt.plot([12+1+3*10]*2, log_lims, 'k', linewidth=2, alpha=asm)


plt.show()
# plt.savefig(base_folder + 'quarter_compare_zout.pdf', transparent=True)

##
# log_lims = [10**-6,10**0]
#
# axs = 0.1
#
# # fig, (ax1,ax2,ax3) = plt.subplots(1,3)
# fig, (ax2,ax3, ax4) = plt.subplots(1,3, figsize=(18,5))
#
# ax2.set_ylabel('Intensity [normalized]')
#
# # # WGS
# # for i in range(np.shape(swgs)[0]):
# # 	ax1.plot(np.arange(no_iter),swgs[i], 'g', alpha=axs)
# # ax1.plot(np.arange(no_iter),uwgs,'w--')
# # ax1.set_xlim(xlims)
# # ax1.set_yscale('log')
# # ax1.set_ylim(log_lims)
# # ax1.set_xlabel('Iteration no.')
# # ax1.set_title('WGS')
#
# # WGS Memory
# for i in range(np.shape(swgsm)[0]):
# 	ax2.plot(np.arange(no_iter),swgsm[i], 'b', alpha=axs)
# ax2.plot(np.arange(no_iter),uwgsm,'w--')
# ax2.set_xlim(xlims)
# ax2.set_yscale('log')
# ax2.set_ylim(log_lims)
# ax2.set_xlabel('Iteration no.')
# ax2.set_title('WGS Memory')
#
# # LOFA
# for i in range(np.shape(slofa)[0]):
# 	ax3.plot(np.arange(no_iter),slofa[i], 'r', alpha=axs)
# ax3.plot(np.arange(no_iter),ulofa,'w--')
# ax3.plot([12+1]*2, log_lims, 'k', linewidth=2, alpha=asm)
# ax3.set_xlim(xlims)
# ax3.set_yscale('log')
# ax3.set_ylim(log_lims)
# ax3.set_xlabel('Iteration no.')
# ax3.set_title('LOFA')
#
# # Mixed
# for i in range(np.shape(smix)[0]):
# 	ax4.plot(np.arange(no_iter),smix[i], 'm', alpha=axs)
# ax4.plot(np.arange(no_iter),umix,'w--')
# ax4.plot([12+1]*2, log_lims, 'k', linewidth=2, alpha=asm)
# ax4.plot([12+1+1*10]*2, log_lims, 'k', linewidth=2, alpha=asm)
# ax4.plot([12+1+2*10]*2, log_lims, 'k', linewidth=2, alpha=asm)
# ax4.plot([12+1+3*10]*2, log_lims, 'k', linewidth=2, alpha=asm)
# ax4.set_xlim(xlims)
# ax4.set_yscale('log')
# ax4.set_ylim(log_lims)
# ax4.set_xlabel('Iteration no.')
# ax4.set_title('Mixed')
#
# fig.show()
# plt.savefig(base_folder + 'full_indiv_mix.pdf', transparent=True)
#
# ##
#
# log_lims = [10**-6,10**0]
#
# axs = 0.1
#
# fig, (ax1,ax2,ax3) = plt.subplots(1,3, figsize=(18,5))
# ax1.set_ylabel('Intensity [normalized]')
#
# # WGS
# for i in range(np.shape(swgs)[0]):
# 	ax1.plot(np.arange(no_iter),swgs[i], 'g', alpha=axs)
# ax1.plot(np.arange(no_iter),uwgs,'w--')
# ax1.set_xlim(xlims)
# ax1.set_yscale('log')
# ax1.set_ylim(log_lims)
# ax1.set_xlabel('Iteration no.')
# ax1.set_title('WGS')
#
# # WGS Memory
# for i in range(np.shape(swgsm)[0]):
# 	ax2.plot(np.arange(no_iter),swgsm[i], 'b', alpha=axs)
# ax2.plot(np.arange(no_iter),uwgsm,'w--')
# ax2.set_xlim(xlims)
# ax2.set_yscale('log')
# ax2.set_ylim(log_lims)
# ax2.set_xlabel('Iteration no.')
# ax2.set_title('WGS Memory')
#
# # LOFA
# for i in range(np.shape(slofa)[0]):
# 	ax3.plot(np.arange(no_iter),slofa[i], 'r', alpha=axs)
# ax3.plot(np.arange(no_iter),ulofa,'w--')
# ax3.plot([12+1]*2, log_lims, 'k', linewidth=2, alpha=asm)
# ax3.set_xlim(xlims)
# ax3.set_yscale('log')
# ax3.set_ylim(log_lims)
# ax3.set_xlabel('Iteration no.')
# ax3.set_title('LOFA')
# fig.show()
# plt.savefig(base_folder + 'quarter_indiv_nomix.pdf', transparent=True)
#

## Calculating average SLM phase change as a function of iteration no.

# font = {'family' : 'normal', 'weight': 'normal', 'size'   : 20}
# matplotlib.rc('font', **font)
#
# diff_phase = slm_phase[1:,:,:] - slm_phase[:-1,:,:]
# sum_diff_phase = np.sum(np.sum(np.absolute(diff_phase),axis=2),axis=1)/(slm_attr.n*slm_attr.n)
#
# plt.figure()
# plt.plot(sum_diff_phase[:50])
# plt.xlabel('Iteration no.')
# plt.ylabel(r'Mean $\Delta \phi$ per pixel [rad]')
# plt.ylim([0,1])
# plt.tight_layout()
# plt.show()
#
# plt.savefig(base_folder + base_filename + 'dphi_n=50.pdf', transparent=True)
#
# ##
# plt.figure()
# plt.imshow(slm_phase[-1],cmap='binary')
# plt.colorbar()
# plt.tight_layout()
# plt.show()
#
# plt.savefig(base_folder + base_filename + 'slmphi.pdf', transparent=True)
#
##
# equivalent to simple FT: nint = samples per pixel, next = additional chip lengths
# nint = 1
# next = 0
# exp_int_lofa = predict_array(w0=w0, phi=slm_phase[-1], nint=nint, next=next)
# exp_int_wgs = predict_array(w0=w0, phi=wgs_phase, nint=nint, next=next)

# qim(exp_int_lofa)
# qim(exp_int_wgs)
