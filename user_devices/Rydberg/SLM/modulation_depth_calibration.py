r"""
Based on wavefront processing code, that was updated after we integrated SLM code into labscript.
Mar. 29, 2022

Fixed issues with new library installation on RoyAL. changed code for configuring path, etc.
April 3, 2023

Some code for debugging
libraries are here:
C:\Users\RoyAL\labscript-suite\Rydberg_userlib\user_devices\Rydberg\SLM\zelux_sdk\Scientific Camera Interfaces\SDK\Python Toolkit\thorlabs_tsi_camera_python_sdk_package.zip\thorlabs_tsi_sdk-0.0.8\thorlabs_tsi_sdk
sys.path.append(r"C:\\Users\\RoyAL\\labscript-suite\\Rydberg_userlib\\user_devices\\Rydberg\\SLM\\zelux_sdk\\Scientific Camera Interfaces\\SDK\\Python Toolkit\\dlls\\64_lib")

"""

import sys
sys.path.append(r'Z:\2022-data\common_files/')

from imports import *

"""idea #6: use np vec torized otpizations instead of loops, if possible
import numpy as np
"""

# from skimage import data, img_as_float, color, exposure
# from skimage.restoration import unwrap_phase

# import tifffile

# our own files/functions
from slm_utils.devices_attr import SLMx13138
from slm_utils import slmpy_updated as slmpy
from slm_utils import freq_funcs
from slm_utils.freq_funcs import qim

# downloaded from: https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ThorCam
from zelux_sdk.thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from zelux_sdk.thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from zelux_sdk.thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE

# # Allied vision vimba sdk
# from vimba_sdk.Vimba_5_1.VimbaPython_Source.vimba import *

# Thorlabs Zelux camera
os.chdir(os.getcwd() + "\\zelux_sdk\\Scientific Camera Interfaces\\SDK\\Python Toolkit\\examples")

# After installation, neek
from windows_setup import configure_path
configure_path()


# # Basler camera(?)
# from pypylon import pylon
# from pypylon import genicam

MONITOR_ID = 1 # RoyBeast current configuration
MOD_BIT_DEPTH = 255.

take_img = True
save_files = True
fancy_ref_mode = False


## Create SLM device, add the functionalities we want
# instantiate SLM display connection class
slm_win = slmpy.SLMdisplay(isImageLock = False, monitor=MONITOR_ID)

# SLM
slm_attr = SLMx13138()

## check exposure times, etc.
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

# (april 3, 2023)
kwargs = {'shiftx': 12, 'shifty': -5, 'defocus':0}

# multitraps:
kwargs_multi = {'phase_pattern_file': '2022_07_29-12_21__nxt=10_nyt=01_sepx=12.000_sepy=12.000_offx=93.09_offy=-93.09_feedback1.pkl', 'phase_pattern_folder': 'common', 'shiftx': 12, 'shifty': -10, 'defocus': 0.0, 'alpha': -0.145}

# # what pattern do we want
# slm_attr.curr_phase_pattern = slm_attr.one_trap(**kwargs)
slm_attr.curr_phase_pattern = slm_attr.array_traps(**kwargs_multi)

# processing
phase_rad = slm_attr.curr_phase_pattern.copy()
phase_rad = slm_attr.pad_zeros(slm_attr.pad_square_pattern(phase_rad))

wf_corr_file = r'Z:\2023-data\2023-01\20230110-wf_correction\20_59_modesz=64_probesz=3\unwrapped_fitted.npy'
wf_kwargs = {'wf_corr_file': wf_corr_file}

phase_rad += slm_attr.pad_zeros(slm_attr.pad_square_pattern(slm_attr.add_wf_correction(**wf_kwargs)))

# # clipping binary mask
# slm.curr_mask = slm.clip_circle(**{'px_ring': 0})
# phase_rad = cv2.bitwise_and(phase_rad, phase_rad, mask=slm.curr_mask)

# convert to bitmap
phase_int8 = slm_attr.convert_bmp(phase_rad, bit_depth = 255)

slm_win.updateArray(phase_int8)
# slm_disp.updateArray(phase_int8)

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

camera.exposure_time_us = 550 #single trap
camera.exposure_time_us = 8000 #multiple traps


# need to save the image width and height for color processing
image_width = camera.image_width_pixels
image_height = camera.image_height_pixels

# start triggering
camera.issue_software_trigger()

## Create the folder

# Information for saving
folder_name = "modulation_depth_calibration_multitraps"#time.strftime("%H_%M") + '_modesz={modesz}_probesz={probesz}'.format(modesz=mode_sz,probesz=probe_sz)

# curr_path = "Z:\\2022-data\\2022-10\\20221017-wf_correction\\"
curr_path = "Z:\\2023-data\\2024-04\\20230403\\"

save_folder = curr_path + folder_name + "\\"

os.chdir(curr_path)

# make folder
if save_files:
    freq_funcs.makedir(save_folder)


## For each modulation depth, take a picture, and save it

mod_depth = np.arange(1, MOD_BIT_DEPTH, step=2)
# mod_depth = np.arange(100, 102, step=2)
max_pixels = np.zeros(np.shape(mod_depth))

# replace this loop with 
# results = np.vectorize(some_function)(mod_depth)
for i in range(len(mod_depth)):
    # convert to bitmap
    phase_int8 = slm_attr.convert_bmp(phase_rad, bit_depth = mod_depth[i])

    slm_win.updateArray(phase_int8)

    time.sleep(0.5)

    # thorlabs zelux
    # camera.exposure_time_us = acq_time_get_loc
    frame = camera.get_pending_frame_or_null()
    img = frame.image_buffer
    # img = cv2.normalize(frame.image_buffer, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)

    # save the file
    if save_files:
        freq_funcs.imgiowrite(save_folder + 'mod_depth={mod_depth}.tif'.format(mod_depth= mod_depth[i]), img)

    max_pixels[i] = np.max(img)

## Save files

if save_files:
    freq_funcs.npwrite("Z:\\2023-data\\2024-04\\20230403\\modulation_depth_calibration_multitraps\\mod_depth.npy", mod_depth)
    freq_funcs.npwrite("Z:\\2023-data\\2024-04\\20230403\\modulation_depth_calibration_multitraps\\max_pixels.npy", max_pixels)


## plot the peak intensity vs modulation depth, fit to tanh

max_pixels_single = np.load("Z:\\2023-data\\2024-04\\20230403\\modulation_depth_calibration_singletrap\\max_pixels.npy")

plt.figure()
plt.plot(mod_depth, max_pixels_single, label='single trap')
plt.plot(mod_depth, max_pixels*np.max(max_pixels_single)/np.max(max_pixels), label='multi traps, rescaled')
plt.xlabel('Modulation bit depth')
plt.ylabel('Peak intensity in image')
plt.legend()
plt.show()

## fit the data
max_pixels_data =  max_pixels*np.max(max_pixels_single)/np.max(max_pixels)

def custom_tanh(x,amp,k,x0,offs):
    # return amp/(1+np.exp(-k*(x-x0)))**4 + offs
    return amp*np.tanh(k*(x-x0)) + offs

# for single trap
offs0 = np.mean(max_pixels_data)
amp0 = np.max(max_pixels_data) - offs0
x0 = np.mean(mod_depth)
k0 = 1

initial_guess = [amp0, k0, x0, offs0]

params, params_covar = scipy.optimize.curve_fit(
    custom_tanh,
    mod_depth,
    max_pixels_data,
    p0=initial_guess
    # bounds=([0, 0.5/alpha_bit_depth*2*np.pi, 0, 0],[np.max(phi_offset), 2.5/alpha_bit_depth*2*np.pi, 1e7,1e6]),
    # maxfev=100000
)

plt.figure()
plt.scatter(mod_depth, max_pixels_data)
plt.plot(mod_depth, custom_tanh(mod_depth,*params), 'r--',label='fit to tanh')
plt.xlabel('Modulation bit depth')
plt.ylabel('Peak intensity in image')
plt.show()

## plot the fits together to double check

max_pixels_fit_single = np.array([6.07076486e+02, 9.73910378e-03, 1.44140262e+02, 5.25383296e+02])
max_pixels_fit_multi = np.array([5.90405570e+02, 1.02901057e-02, 1.37057357e+02, 5.12265482e+02])

plt.figure()
# plt.plot(mod_depth, max_pixels_single, label='single trap')
plt.plot(mod_depth, custom_tanh(mod_depth,*max_pixels_fit_single), label='single trap fitted')
# plt.plot(mod_depth, max_pixels*np.max(max_pixels_single)/np.max(max_pixels), label='multi traps, rescaled')
plt.plot(mod_depth, custom_tanh(mod_depth,*max_pixels_fit_multi), label='multi traps, rescaled, fitted')
plt.xlabel('Modulation bit depth')
plt.ylabel('Peak intensity in image')
plt.legend()
plt.show()

## get modulation transfer function
mod_depth_fitted = np.arange(0, MOD_BIT_DEPTH, 0.5)

# to get 0 to 1, just use the np tanh function and ignore offset and amp
k_fit =  1.02901057e-02
x0_fit = 1.37057357e+02

max_pixels_fitted = (np.tanh(k_fit*(mod_depth_fitted-x0_fit))+1)/2

plt.figure()
plt.plot(mod_depth_fitted,max_pixels_fitted, label='multi traps, rescaled, fitted, rescaled to [0,1]')
plt.xlabel('Modulation bit depth')
plt.ylabel('Peak intensity in image')
plt.legend()
plt.show()

## invert it
# for intensity between 0 and 1, get the modulation depth we need
i0_normalized = np.linspace(0.01, 0.99, 500)

# to get 0 to 1, just use the np tanh function and ignore offset and amp
k_fit =  1.02901057e-02
x0_fit = 1.37057357e+02

def i0_to_mod(i0_normalized, k, x0):
    # initially, no clipping. get singularities
    # raw = x0 + (1/k)*np.arctanh(2*i0_normalized-1)
    # return raw
    i0_filtered = np.clip(i0_normalized, 0.01, 0.99)

    raw = x0 + (1/k)*np.arctanh(2*i0_filtered-1)
    return np.clip(raw, 0, 255)

mod_depth_inverted = i0_to_mod(i0_normalized, k_fit, x0_fit)

plt.figure()
plt.plot(mod_depth_fitted,max_pixels_fitted, label='data')
plt.plot(mod_depth_inverted,i0_normalized, label='inverted data')
plt.xlabel('Modulation bit depth')
plt.ylabel('Peak intensity in image')
plt.legend()
plt.show()

##
plt.figure()
plt.plot(i0_normalized, mod_depth_inverted, label='inverted data')
plt.ylabel('Modulation bit depth')
plt.xlabel('Peak intensity in image')
plt.legend()
plt.show()

## (2) now get the amplitude mask for some desired trap waist
effective_trap_waist = np.linspace(1.83e-6, 10e-6, 5)
# effective_trap_waist = np.linspace(1.5e-6, 10e-6, 50)
wavelength = 808e-9
focal_length = 10e-3

effective_fourier_waist = wavelength*focal_length/(np.pi*effective_trap_waist)*400/150

plt.figure()
plt.plot(effective_trap_waist*1e6,effective_fourier_waist*1e3)
plt.xlabel('Trap waist [um]')
plt.ylabel('Required waist at SLM [mm]')
# plt.legend()
plt.show()

## get gaussians corresponding to the waist we have at the SLM vs the target
## using intensity because we calibrated the transfer function of modulation depth in terms of intensity, not electric field
# the intensity at the SLM
slm_intensity0 = freq_funcs.gauss2d_int(x=slm_attr.xm, y=slm_attr.ym, wx=slm_attr.w0/slm_attr.px, wy=slm_attr.w0/slm_attr.px, x0=slm_attr.n/2, y0=slm_attr.n/2)

target_w0 = effective_fourier_waist[1]
target_w0 = 7.e-3/2

# the effective intensity we want at the SLM
slm_intensity_target = freq_funcs.gauss2d_int(x=slm_attr.xm, y=slm_attr.ym, wx=target_w0/slm_attr.px, wy=target_w0/slm_attr.px, x0=slm_attr.n/2, y0=slm_attr.n/2)

# the fractional intensity we want to modulate with respect to the incident intensity
# between zero and 1, because we can only reduce the intensity not increase it with respect to the incident light
intensity_mask = np.divide(slm_intensity_target,slm_intensity0)
modulation_mask = i0_to_mod(intensity_mask, k_fit, x0_fit)

qim(modulation_mask)

