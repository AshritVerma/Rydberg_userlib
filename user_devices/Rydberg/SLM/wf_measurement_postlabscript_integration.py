'''
Implementation of wavefront measurement technique based on the work of Cizmar et al, Nature, 2010.
Link: https://www.nature.com/articles/nphoton.2010.85

Emily Qiu
Oct. 17, 2022


For Zelux camera:
thorlabs_tsi_sdk.tl_camera TLCameraSDK

Integrated into experiment
Mar. 29, 2022

New allied vision camera examples:
https://github.com/alliedvision/VimbaPython/blob/master/Examples/synchronous_grab.py

need to install Vimba python SDK and replace period in vimba_5.1 to vimba_5_1 to import the vimba module
changed so that we only correct in central square region (after changing all the SLM code to return only square patterns)
'''


import sys
sys.path.append(r'Z:\VV Rydberg lab\2022-data\common_files/')

from imports import *

# from skimage import data, img_as_float, color, exposure
# from skimage.restoration import unwrap_phase

# import tifffile

# our own files/functions
from slm_utils.devices_attr import SLMx13138
from slm_utils import slmpy_updated as slmpy
from slm_utils import freq_funcs
from slm_utils.freq_funcs import qim

# # Allied vision vimba sdk
# from vimba_sdk.Vimba_5_1.VimbaPython_Source.vimba import *

# (??) This doesn't work anymore
# Thorlabs Zelux camera
os.chdir(os.getcwd() + "\\zelux_sdk\\Scientific Camera Interfaces\\SDK\\Python Toolkit\\examples")

from windows_setup import configure_path
configure_path()


from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE


# # Basler camera(?)
# import slmpy_updated as slmpy
# from pypylon import pylon
# from pypylon import genicam

MONITOR_ID = 1 # RoyBeast current configuration

take_img = True
save_files = True
fancy_ref_mode = False

# get probe signal such that the region is of size probe_sz^2
def get_probe_region(img, probe_sz, x0, y0):

    # get floor
    probe_sz_half = int(probe_sz/2)

    # separate into odd and even cases
    if np.mod(probe_sz, 2) == 0:
        return img[y0-probe_sz_half:y0+probe_sz_half, x0-probe_sz_half:x0+probe_sz_half]

    else:
        # need to add one to the upper limit
        return img[y0-probe_sz_half:y0+probe_sz_half+1, x0-probe_sz_half:x0+probe_sz_half+1]

def check_matrix_for_item(matrix, check_item):
    for row in matrix:
        for item in row:
            if (check_item == item).all():
                return True

    return False

def av_take_img(acq_time):
    # subroutine
    with Vimba.get_instance() as vimba:

        cameras = vimba.get_all_cameras()
        with cameras[0] as camera:

            camera.ExposureTime.set(acq_time)
            # it only rounds to the nearest increment, only discrete options for the exposure time

            img = camera.get_frame()
            img.convert_pixel_format(PixelFormat.Mono8)
            img = img.as_opencv_image()

    return img[918:918+1830,1374:1374+2000]

## Create SLM device
# instantiate SLM display connection class
slm_disp = slmpy.SLMdisplay(isImageLock = False, monitor=MONITOR_ID)

# SLM
slm = SLMx13138()

# # manually from before
# # full size blazed gratings
# full_grating = slm.tile_blazed_xy(line_sp=11)
# # mod_full_grating = np.mod(full_grating, 2*np.pi)*4/(2*np.pi)
#
# # # Get the location of first order from user clicks
# full_grating_bmp = slm.convert_bmp(full_grating, bit_depth=255.)
#
# slm_disp.updateArray(full_grating_bmp,check_img_size=False)

# (oct. 17, 2022) what we are doing now with SLM server
kwargs = {'shiftx': 20, 'shifty': -16, 'defocus':0}

# (jan 10, 2023)
kwargs = {'shiftx': 20, 'shifty': -19, 'defocus':0}

# (jan 13, 2023)
kwargs = {'shiftx': 24, 'shifty': 5, 'defocus':0}

phase_rad = slm.one_trap(**kwargs)
phase_rad = slm.pad_zeros(slm.pad_square_pattern(phase_rad))

# # clipping binary mask
# slm.curr_mask = slm.clip_circle(**{'px_ring': 0})
# phase_rad = cv2.bitwise_and(phase_rad, phase_rad, mask=slm.curr_mask)

# convert to bitmap
phase_int8 = slm.convert_bmp(phase_rad, bit_depth = 255.)

# slm_disp.updateArray(phase_int8)
slm_disp.updateArray(phase_int8)

full_grating = slm.one_trap(**kwargs)

## configure Zelux camera
sdk = TLCameraSDK()
camera = sdk.open_camera(sdk.discover_available_cameras()[0])

#  setup the camera for continuous acquisition
camera.frames_per_trigger_zero_for_unlimited = 0
camera.image_poll_timeout_ms = 2000  # 2 second timeout
camera.arm(2)

# save these values to place in our custom TIFF tags later
bit_depth = camera.bit_depth
# camera.exposure_time_us = 40 ## seems to be the minimum

# need to save the image width and height for color processing
image_width = camera.image_width_pixels
image_height = camera.image_height_pixels

# start triggering
camera.issue_software_trigger()

## configure Vimba camera
# img = av_take_img(1500)

## configure basler camera
# if take_img:
#
# 	from instrumental import list_instruments, instrument
# 	# camera = pylon.InstantCamera(pylon.TlFactory_GetInstance().CreateFirstDevice())
# 	# camera.Open()
# 	#
# 	# camera = instrument(list_instruments()[0], reopen_policy='reuse')
# 	# camera.open()
#
# 	camera = instrument(list_instruments()[0], reopen_policy='reuse')
# 	camera.open()

## WF measurement params

# # camera acquisition time
# acq_time_get_loc = 30

# # dcc
# acq_time_get_probe = 1200
# acq_time_get_probe = 30

# zelux
acq_time_get_loc = 40
acq_time_get_probe = 40

# # Parameters
# # distance between modes
# mode_dy = 5
# mode_dx = 5

# figure out what I want for this one
# mod_depth_get_loc = 0.015#0.009
mod_depth_get_loc = 0.009

# Deflect small amount of light at the center of SLM to get location of the first order
# use square region of size get_loc_sz. larger than mode size, bc we need to deflect
# enough light to be able to see where the first order is
# get_loc_sz = 64
get_loc_sz = 1000

# SLM mode size, limited by saturation of interference between two modes near center of Gaussian
# mode_sz = 200
mode_sz = 64

# probe signal = sum of intensities over camera region of size (2*probe_size)^2
probe_sz = 3

# full modulation uint8 depth
# mdepth_blazed = 3*6 # then we make sure phase spacing is uniform for line_sp = 4
mdepth_blazed = 10*2 # then we make sure phase spacing is uniform for line_sp = 4


# # Resolution of phase modulation
# phi_res_n = 40
# dphi = 2*np.pi/phi_res_n
#
# # Points of phase offset to scan
# phi_offset = np.arange(0,2*np.pi,dphi)

# # instead of adding phase, just add some value to the uint8 bitmap
int_res = 2

# phi_offset = np.arange(0, 214, int_res) # for mdepth = 3*6
phi_offset = np.arange(0, 200, int_res) # for mdepth = 3*6

n_pts = len(phi_offset)

# do only square
slm_nx = slm.n
slm_ny = slm.n

# position of the upper left corner of reference mode, for full SLM
nloc_x = int((slm_nx-get_loc_sz)/2)
nloc_y = int((slm_ny-get_loc_sz)/2)

# mini grating for the mode used to get first order location
get_loc_mod = full_grating[:get_loc_sz,:get_loc_sz]

# phase pattern to be displayed with only the temporary mode turned on to get position
get_loc_phase = np.zeros(shape=(slm_ny,slm_nx))
get_loc_phase[nloc_y:nloc_y+get_loc_sz, nloc_x:nloc_x+get_loc_sz] += get_loc_mod

# Information for saving
folder_name = time.strftime("%H_%M") + '_modesz={modesz}_probesz={probesz}'.format(modesz=mode_sz,probesz=probe_sz)

# curr_path = "Z:\\2022-data\\2022-10\\20221017-wf_correction\\"
curr_path = "Z:\\2023-data\\2023-01\\20230115-wf_correction\\"

save_folder = curr_path + folder_name + "\\"

os.chdir(curr_path)

# make folder
if save_files:
    freq_funcs.makedir(save_folder)


## Get location of first order

# # check that it's working
# ref_phase_bmp = slm.convert_bmp(full_grating, bit_depth=255.)
# slm_disp.updateArray(ref_phase_bmp)
#
# time.sleep(1)

# # Get the location of first order from user clicks
curr_phase = slm.pad_zeros(slm.pad_square_pattern(get_loc_phase))
get_loc_phase_bmp = slm.convert_bmp(curr_phase, bit_depth=255.*mod_depth_get_loc)

slm_disp.updateArray(get_loc_phase_bmp,check_img_size=False)
time.sleep(1)

if take_img:

    # # allied vision
    # img = av_take_img(acq_time_get_loc)

    # thorlabs zelux
    camera.exposure_time_us = acq_time_get_loc
    frame = camera.get_pending_frame_or_null()
    img = frame.image_buffer
    img = cv2.normalize(frame.image_buffer, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)

    # # thorlabs DCC?
    # img = camera.grab_image(exposure_time=acq_time_get_loc)

    # save the file
    if save_files:
        freq_funcs.imgiowrite(save_folder + 'get_loc_sz={get_loc_sz}.tif'.format(get_loc_sz=get_loc_sz), img)

    # Zoom in on the image
    cv2.namedWindow("get_first_order")#, cv2.WINDOW_NORMAL)
    cv2.imshow("get_first_order", img)
    x0, y0, w, h = cv2.selectROI("get_first_order", img, showCrosshair=True)
    cv2.waitKey(1)
    cv2.destroyAllWindows()

    # save the zoomed in figure
    x1 = x0+w
    y1 = y0+h

    zoomed = img[y0:y1,x0:x1]
    loc = (int(x0+w/2), int(y0+h/2))

    # center position of the probe
    probe_x = loc[0]
    probe_y = loc[1]

    # camera.exposure_time_us = acq_time_get_probe


# # resize window
# win_w = 500
# win_h = 500
# rescaled_zoomed = cv2.resize(zoomed, (0,0), fx=10, fy=10)
#
# # Get position of center of first order, where the probe will be centered
# cv2.namedWindow("get_first_order_center",cv2.WINDOW_NORMAL)
# cx0, cy0, cw, ch = cv2.selectROI("get_first_order_center", rescaled_zoomed, showCrosshair=True)
# cv2.waitKey(1)
# cv2.destroyAllWindows()
#
# loc = (x0+cx0, y0+cy0)

# # Get window
# plt.figure()
# plt.imshow(img)
# plt.get_current_fig_manager().window.showMaximized()
# zoom = np.array(plt.ginput(2)).astype(int)			# Top left, Bottom right of zoomed region
# plt.close()
#
# # Get position of center of first order, where the probe will be centered
# plt.figure()
# plt.imshow(zoomed)
# plt.get_current_fig_manager().window.showMaximized()
# center = np.array(plt.ginput(1)).astype(int)
# plt.close()

## Wavefront measurement paarms

# number of modes - use rectangle
nmode_x = int(np.ceil(slm_nx/mode_sz))
nmode_y = int(np.ceil(slm_ny/mode_sz))

# Index of reference mode (at quarter position of SLM)
nmode_center_x = int(slm_nx/mode_sz/2)
nmode_center_y = int(slm_ny/mode_sz/2)

# Index of reference mode (at quarter position of SLM)
nmode_ref_x = int(slm_nx/mode_sz/3)
nmode_ref_y = int(slm_ny/mode_sz/3)

# # generate the reference mode
# single_mode = slm.tile_blazed_xy_int(line_sp=11, maxval = mdepth_blazed)[:mode_sz, :mode_sz]
single_mode = (slm.one_trap(**kwargs)*mdepth_blazed)[:mode_sz, :mode_sz]

# set the reference mode
base_phase = np.zeros(shape=(slm_ny,slm_nx))
base_phase[nmode_ref_y*mode_sz:(nmode_ref_y+1)*mode_sz, nmode_ref_x*mode_sz:(nmode_ref_x+1)*mode_sz] += single_mode

# Probe region and signal (intensity) as fcn of modulated phase
probe_region = np.zeros((nmode_y, nmode_x, n_pts, probe_sz, probe_sz))
probe_sig = np.zeros((nmode_y, nmode_x, n_pts))

# testing the probe signal with edge/center modes
probe_region_edge = np.zeros((n_pts, probe_sz, probe_sz))
probe_region_cent = np.zeros((n_pts, probe_sz, probe_sz))
probe_sig_edge = np.zeros(n_pts)
probe_sig_cent = np.zeros(n_pts)

# Save modulation depth for reference and test modes
mdepth_ref = np.zeros((nmode_y,nmode_x))
mdepth_test = np.zeros((nmode_y,nmode_x))

# # Reference mode power - modulate as function of total power?
# beam_i = normalize2d(gauss2d_int(x=slm.xm, y=slm.ym, wx=slm.w0/slm.px, wy=slm.w0/slm.px, x0=slm.axx, y0=slm.axy))

## Check scaling function on edge and center modes
#
# # ref_mode_power = np.sum(beam_i[nmode_ref_y*mode_sz:(nmode_ref_y+1)*mode_sz, nmode_ref_x*mode_sz:(nmode_ref_x+1)*mode_sz])
# ref_mode_power = np.max(beam_i[nmode_ref_y*mode_sz:(nmode_ref_y+1)*mode_sz, nmode_ref_x*mode_sz:(nmode_ref_x+1)*mode_sz])
# cent_mode_power = np.max(beam_i[nmode_center_y*mode_sz:(nmode_center_y+1)*mode_sz, nmode_center_x*mode_sz:(nmode_center_x+1)*mode_sz])
# edge_mode_power = np.max(beam_i[:mode_sz,:mode_sz])
#
# eps_control = 0.1
#
# ref_mode_depth = np.sqrt(ref_mode_power)
# edge_mode_depth = np.sqrt(edge_mode_power)
# cent_mode_depth = np.sqrt(cent_mode_power)
#
# # scaling function for modes
# def scale_func(test_mode_depth):
# 	# try linear function of sqrt of max powers
# 	# first rescaled to (0, 1-eps_control) corresponding to edge mode, and center mode
# 	# then take (1-value), want edge mode to have mod_depth of 1, and center mode to have non-zero
#
# 	return 1-(test_mode_depth - edge_mode_depth)/(cent_mode_depth-edge_mode_depth)*(1-eps_control)
#
# # scale for reference mode
# ref_scale_factor = scale_func(ref_mode_depth)
#
# # scale for edge mode
# edge_scale_factor = scale_func(edge_mode_depth)
#
# # scale for center mode
# cent_scale_factor = scale_func(cent_mode_depth)
#
## Set some phase pattern, check if there's saturation
#
# currmode_y = nmode_center_y
# currmode_x = nmode_center_x
#
# # indices of the array
# ix0 = currmode_x*mode_sz
# iy0 = currmode_y*mode_sz
#
# ix1 = (currmode_x+1)*mode_sz
# iy1 = (currmode_y+1)*mode_sz
#
# # Set blazed grating of reference mode
# curr_phase = base_phase.copy()#*ref_scale_factor
#
# # set blazed grating of edge mode
# curr_phase[iy0:iy1,ix0:ix1] = single_mode[:iy1-iy0,:ix1-ix0].copy()#*cent_scale_factor
#
# store_curr_phase_disp = np.zeros((n_pts, mode_sz, mode_sz))
#
# # add test mode
# curr_phase[iy0:iy1,ix0:ix1] += dphi*36.99999999
# curr_phase_disp = slm.convert_bmp(curr_phase, bit_depth=255.)
#
# slm_disp.updateArray(curr_phase_disp)
#
## Check different modes

# # mode_sz = 200
# nmode_ref_y = 3
# nmode_ref_x = 4
#
# currmode_x = 0
# currmode_y = 0
#
# currmode_x = nmode_center_x
# currmode_y = nmode_center_y

# nmode_ref_x = int(nmode_center_x-mode_dx/2)
# nmode_ref_y = int(nmode_center_y-mode_dy/2)
#
# currmode_x = int(nmode_center_x+mode_dx/2)
# currmode_y = int(nmode_center_y+mode_dy/2)


# # mode_sz = 64
nmode_ref_x = 6
nmode_ref_y = 5

# furthest edge mode - 1 (X size is not multiple of 64)
# currmode_x = 1
# currmode_y = 1

currmode_x = 8 #18
currmode_y = 8 #15

# # # mode_sz = 64
# nmode_ref_x = 0
# nmode_ref_y = 0
#
# # furthest edge mode - 1 (X size is not multiple of 64)
# currmode_x = 2
# currmode_y = 2

# set the reference mode
max_base_phase = np.zeros(shape=(slm_ny,slm_nx))
max_base_phase[nmode_ref_y*mode_sz:(nmode_ref_y+1)*mode_sz, nmode_ref_x*mode_sz:(nmode_ref_x+1)*mode_sz] += single_mode

# indices of the array
ix0 = currmode_x*mode_sz
iy0 = currmode_y*mode_sz

ix1 = (currmode_x+1)*mode_sz
iy1 = (currmode_y+1)*mode_sz

# Set blazed grating of reference mode
curr_phase_uint8 = max_base_phase.copy()#*ref_scale_factor

# set blazed grating of edge mode
curr_phase_uint8[iy0:iy1,ix0:ix1] = single_mode[:iy1-iy0,:ix1-ix0].copy()#*cent_scale_factor

curr_phase_disp = slm.pad_zeros(slm.pad_square_pattern(curr_phase_uint8)).astype(np.uint8)
slm_disp.updateArray(curr_phase_disp)
time.sleep(1)


# # allied vision
# img = av_take_img(acq_time_get_probe)

# zelux
camera.exposure_time_us = acq_time_get_probe
frame = camera.get_pending_frame_or_null()
img = frame.image_buffer
img = cv2.normalize(frame.image_buffer, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)

# # dcc
# img = camera.grab_image(exposure_time=acq_time_probe)

# iterate through the phase offsets
for curr in range(n_pts):

    print('current phase:' + str(curr))

    # # # display the pattern on SLM and take a picture
    # # img = camera.grab_image(exposure_time=acq_time_probe)

    # img = av_take_img(acq_time_get_probe)

    # zelux
    frame = camera.get_pending_frame_or_null()
    img = frame.image_buffer
    img = cv2.normalize(frame.image_buffer, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)

    # add uint8 explicitly
    curr_phase_uint8[iy0:iy1,ix0:ix1] += int_res
    curr_phase_disp = slm.pad_zeros(slm.pad_square_pattern(curr_phase_uint8)).astype(np.uint8)

    slm_disp.updateArray(curr_phase_disp)

    # get the probe signal
    probe_region_cent[curr] = get_probe_region(img=img, probe_sz=1, x0=probe_x, y0=probe_y)

    # Read sum of probe region intensities
    probe_sig_cent[curr] = np.mean(probe_region_cent[curr])
    print(probe_sig_cent[curr])
    # time.sleep(0.1)


freq_funcs.qp(probe_sig_cent)

## Look at the image to make sure it's changing
#
# plt.ion()
# fig, cax = plt.subplots(1,1,figsize=(6,6))
# # fig_handle = cax.imshow(data[0], cmap='binary')
# fig_handle = cax.imshow(probe_region[currmode_y,currmode_x,0], cmap='binary')
# fig.colorbar(fig_handle,ax=cax, orientation="horizontal")
#
# for curr in range(len(phi_offset)):
#
#     # show the probe region
#     # fig_handle.set_data(data[curr])
#     fig_handle.set_data(probe_region_cent[curr])
#     fig_handle.autoscale()
#
#     fig.canvas.draw()
#     fig.canvas.flush_events()
#
#     plt.pause(1)
#     print(phi_offset[curr])
#
# plt.close()

## Now, check edge mode
#
# currmode_y = 0
# currmode_x = 0
#
# # indices of the array
# ix0 = currmode_x*mode_sz
# iy0 = currmode_y*mode_sz
#
# ix1 = (currmode_x+1)*mode_sz
# iy1 = (currmode_y+1)*mode_sz
#
# # mdepth_test[currmode_y,currmode_x] = test_scale_factor
# # mdepth_ref[currmode_y,currmode_x] = ref_scale_factor
# #
# # # mdepth_test[currmode_y,currmode_x] = (1-rel_test_mode_depth)*rescale_factor
# # # mdepth_ref[currmode_y,currmode_x] = (1-rel_ref_mode_depth)*rescale_factor
# #
# # # # set the modulation depth
# # # rel_mode_depth = np.sqrt(test_mode_power/ref_mode_power)
# # # # rel_mode_depth = 1
# # #
# # # # if test mode power at SLM is higher than ref, then set ref mode modulation = 1, reduce test mode.
# # # if rel_mode_depth >= 1:
# # # 	mdepth_test[currmode_y,currmode_x] = 1/rel_mode_depth
# # # 	mdepth_ref[currmode_y,currmode_x] = 1
# # #
# # # # else, test mode modulation = 1, reduce ref mode.
# # # else:
# # # 	mdepth_test[currmode_y,currmode_x] = 1
# # # 	mdepth_ref[currmode_y,currmode_x] = rel_mode_depth
#
# # Set blazed grating of reference mode
# curr_phase_uint8 = base_phase.copy()#*ref_scale_factor
#
# # set blazed grating of edge mode
# curr_phase_uint8[iy0:iy1,ix0:ix1] = single_mode[:iy1-iy0,:ix1-ix0].copy()#*edge_scale_factor
#
# # iterate through the phase offsets
# for curr in range(n_pts):
# 	print('current phase:' + str(curr))
#
# 	# add uint8 explicitly
# 	curr_phase_uint8[iy0:iy1,ix0:ix1] += int_res
# 	curr_phase_disp = slm.pad_zeros(curr_phase_uint8).astype(np.uint8)
#
# 	# display the pattern on SLM and take a picture
#
# 		slm_disp.updateArray(curr_phase_disp)
# 		img = camera.grab_image(exposure_time=acq_time_probe)
#
# 	# get the probe signal
# 	probe_region_edge[curr] =  get_probe_region(img=img, probe_sz=probe_sz, x0=probe_x, y0=probe_y)
#
# 	# Read sum of probe region intensities
# 	probe_sig_edge[curr] = np.mean(probe_region_edge[curr])
#
# qp(probe_sig_edge)

## Calculate the reference modes of the reference modes

# # show the first order fringe and the phase pattern
# plt.ion()
# fig, cax = plt.subplots(1, 2, figsize=(14,6))
# first_order = cax[0].imshow(zoomed, cmap='binary')
# fig.colorbar(first_order,ax=cax[0], orientation="horizontal")
# curr_pattern = cax[1].imshow(base_phase)
# fig.colorbar(curr_pattern,ax=cax[1], orientation="horizontal")
# print("done display")
#
# reduction_factor=10
#
# # rescale so that the edge mode depth is 1
# rescale_factor = 1/(1-np.sqrt(edge_mode_power/cent_mode_power))


# matrix containing the indices of the reference mode for a g
ref_mode_index = np.zeros((nmode_y, nmode_x, 2))

if fancy_ref_mode:
    # thresholds of where the quadrants are defined
    quad_x = [8, 16, 24]
    quad_y = [6, 13, 19]

    # ref_modes[curr_quad_y, curr_quad_x]
    ref_modes = np.array([[[3, 4], [3, 12], [3, 20], [3, 28]], [[9, 4], [9, 12], [9, 20], [9, 28]], [[16, 4], [16, 12], [16, 20], [16, 28]],[[22, 4], [22, 12], [22, 20], [22, 28]]])

    nref_mode_y = np.shape(ref_modes)[0]
    nref_mode_x = np.shape(ref_modes)[1]

    curr_quad_x = 0
    curr_quad_y = 0

    # iterate through test modes
    for currmode_y in range(nmode_y):
        for currmode_x in range(nmode_x):

            currmode = [currmode_y, currmode_x]

            # define the reference modes for the test modes only
            if not check_matrix_for_item(matrix=ref_modes, check_item = currmode):

                # check if we're not yet at the last quadrant
                if curr_quad_x < len(quad_x):

                    # increment the quadrant when we reach the reshold value
                    if currmode_x == quad_x[curr_quad_x]:
                        curr_quad_x += 1

                if curr_quad_y < len(quad_y):
                    if currmode_y == quad_y[curr_quad_y]:
                        curr_quad_y += 1

                ref_mode_index[currmode_y, currmode_x, :] = ref_modes[curr_quad_y, curr_quad_x, :]

                # reached end of row, reset the curr_quad_x
                if currmode_x == nmode_x-1:
                    curr_quad_x = 0


    # define the reference modes for the reference modes
    for curr_refmode_y in range(nref_mode_y):
        for curr_refmode_x in range(nref_mode_x):

            # skip the first reference mode = global reference
            if curr_refmode_x == 0 and curr_refmode_y == 0:
                continue

            # if in the first row, choose along the first row
            if curr_refmode_y == 0:
                refmode_refmode_y = curr_refmode_y
                refmode_refmode_x = curr_refmode_x - 1

            # else, choose along the vertical
            else:
                refmode_refmode_y = curr_refmode_y - 1
                refmode_refmode_x = curr_refmode_x

            curr_refmode = ref_modes[curr_refmode_y, curr_refmode_x]
            ref_mode_index[curr_refmode[0], curr_refmode[1], :] = ref_modes[refmode_refmode_y, refmode_refmode_x]

else:

    ref_mode_index[:, :, :] = [nmode_ref_y, nmode_ref_x]

## Wavefront measurement ####################################################################################################################################

curr_mode = 0

# iterate through test modes
# for currmode_y in [10]:
# 	for currmode_x in [10]:
for currmode_y in range(nmode_y):
    for currmode_x in range(nmode_x):

        if not fancy_ref_mode:

            # Skip modulation of reference mode
            if currmode_y == nmode_ref_y and currmode_x == nmode_ref_x:
                curr_mode += 1
                continue

        # Edge cases of SLM, rectangular modes
        if currmode_x == nmode_x-1:
            ix1 = slm_nx
        else:
            ix1 = (currmode_x+1)*mode_sz

        if currmode_y == nmode_y-1:
            iy1 = slm_ny
        else:
            iy1 = (currmode_y+1)*mode_sz

        # indices of array
        ix0 = currmode_x*mode_sz
        iy0 = currmode_y*mode_sz

        # # Scale modulation depth of test mode to improve SNR
        # # test_mode_power = np.sum(beam_i[iy0:iy1,ix0:ix1])
        # test_mode_power = np.max(beam_i[iy0:iy1,ix0:ix1])
        # test_mode_depth = np.sqrt(test_mode_power)
        #
        # # get the scale factor
        # test_scale_factor = scale_func(test_mode_depth)

        mdepth_test[currmode_y,currmode_x] = 1
        mdepth_ref[currmode_y,currmode_x] = 1
        # mdepth_test[currmode_y,currmode_x] = test_scale_factor
        # mdepth_ref[currmode_y,currmode_x] = ref_scale_factor

        # make reading easier
        ref_mode_y = int(ref_mode_index[currmode_y, currmode_x, 0])
        ref_mode_x = int(ref_mode_index[currmode_y, currmode_x, 1])

        ref_base_phase = np.zeros(shape=(slm_ny,slm_nx))
        ref_base_phase[ref_mode_y*mode_sz:(ref_mode_y+1)*mode_sz, ref_mode_x*mode_sz:(ref_mode_x+1)*mode_sz] += single_mode

        # Set blazed grating of reference mode
        curr_phase_uint8 = ref_base_phase.copy()*mdepth_ref[currmode_y,currmode_x]

        # set blazed grating of test mode
        curr_phase_uint8[iy0:iy1,ix0:ix1] = single_mode[:iy1-iy0,:ix1-ix0].copy()*mdepth_test[currmode_y,currmode_x]

        print('current mode number: ' + str(curr_mode))

        # iterate through the phase offsets
        for curr in range(n_pts):
            print('current phase:' + str(curr))

            curr_phase_disp = slm.pad_zeros(slm.pad_square_pattern(curr_phase_uint8)).astype(np.uint8)

            # display the pattern on SLM and take a picture
            slm_disp.updateArray(curr_phase_disp)
            time.sleep(0.1)

            if take_img:

                # # allied vision
                # img = av_take_img(acq_time=acq_time_get_probe)

                # zelux
                frame = camera.get_pending_frame_or_null()
                img = frame.image_buffer
                img = cv2.normalize(frame.image_buffer, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)


                # # not sure if the following line is part of the same camera
                # img = camera.grab_image(exposure_time=acq_time_probe)

                # get the probe signal
                probe_region[currmode_y,currmode_x,curr] = np.reshape(get_probe_region(img=img, probe_sz=probe_sz, x0=probe_x, y0=probe_y), newshape=(probe_sz,-1))

                # # show the current phase pattern
                # curr_pattern.set_data(curr_phase_disp)
                # curr_pattern.autoscale()
                #
                # # show the probe region
                # first_order.set_data(probe_region[currmode_y,currmode_x, curr])
                # first_order.autoscale()
                # plt.pause(1)
                #
                # # save the image
                # probe_filename = 'ix,iy={i},{j}_phi={phi}.tif'.format(i=currmode_x,j=currmode_y,phi=phi_offset[curr])
                # # probe_filename += '_mdepthref={mdepthref}_mdepthtest={mdepthtest}.tif'.format(mdepthref=mdepth_ref[currmode_y,currmode_x], mdepthtest=mdepth_test[currmode_y,currmode_x])
                #
                # freq_funcs.imgiowrite(save_folder + probe_filename, img)

                # Read sum of probe region intensities
                probe_sig[currmode_y,currmode_x,curr] = np.mean(probe_region[currmode_y,currmode_x,curr])

                print(probe_sig[currmode_y,currmode_x,curr])

                # fig.canvas.draw()
                # fig.canvas.flush_events()

            # add uint8 explicitly
            curr_phase_uint8[iy0:iy1,ix0:ix1] += int_res

        curr_mode += 1

# freq_funcs.qp(probe_sig[1,1])

# zelux
camera.disarm()

# thorlabs
# camera.close()


# Save files
if save_files:
    freq_funcs.npwrite(save_folder + 'probe_sig.npy', probe_sig)
    freq_funcs.npwrite(save_folder + 'probe_region.npy', probe_region)
    freq_funcs.npwrite(save_folder + 'ref_mode_index.npy', ref_mode_index)

## Check graph state
#
# import networkx as nx
# G = nx.Graph()
#
# G.add_node([1,2])
#
# ##
# adj_matrix = np.zeros(shape=(nmode_y, nmode_x))
#
# # get adjacency matrix
# for currmode_y in range(nmode_y):
# 	for currmode_x in range(nmode_x):
#
# 		ref_mode_y = ref_mode_index[currmode_y, currmode_x, 0]
# 		ref_mode_x = ref_mode_index[currmode_y, currmode_x, 1]
#
# 		adj_matrix[ref_mode_y, ref_mode_x]