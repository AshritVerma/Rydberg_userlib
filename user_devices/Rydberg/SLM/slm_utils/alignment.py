'''
This file is used for testing the SLM/using the SLM to assist in alignment of optics.

Emily Qiu
Oct. 27, 2021
'''

import sys
import os
import numpy as np
import time
import matplotlib
import matplotlib.pyplot as plt
from zernike import RZern
import json
from tqdm import tqdm
from scipy import ndimage, misc
import scipy.optimize as optimize
import imageio
import pickle
import cv2

# parameters that need to be defined by user
in_lab = True
royoffice = False
calfile="corr_nov19.bmp"



from slm_utils.devices_attr import SLMx13138
from slm_utils import slmpy_updated as slmpy
from slm_utils import freq_funcs
from slm_utils.freq_funcs import qim

# # our own files/functions
# # from funcs import *
# from params import *
# from const import *

# useful to save files
base_filename = time.strftime("%Y_%m_%d-%H_%M__")

MONITOR_ID = 2 # RoyBeast current configuration

# # instantiate SLM class
# slm = SLMx13138(useSq=False)
#
# # collimated beam size at the SLM
# w0 = 3.74e-3/2*250/75
#
# # Expected trap size in number of pixels in the FT
# wx = slm.nx/(np.pi*w0/slm.px)
# wy = slm.ny/(np.pi*w0/slm.px)

# take image routine
def take_image():
    # Assume global variable camera = pylon.InstantCamera()
    # tried passing camera as a function argument - leads to "Grab TimeoutException"

    camera.StartGrabbing()
    grabResult = camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)

    img_arr = np.array(grabResult.Array)
    # img_arr = np.fliplr(img_arr)			# determined based on direction/orientation of deflected traps

    grabResult.Release()
    camera.StopGrabbing()

    return img_arr.astype(int)



# instantiate SLM display connection class
slm_disp = slmpy.SLMdisplay(isImageLock = False, monitor=MONITOR_ID)

# SLM
slm = SLMx13138()
##

# full size blazed gratings
phase_rad = slm.tile_blazed_xy(line_sp=11)

# phase_rad = slm.get_unit_circ_phase(phase_rad)

phase_int8 = slm.convert_bmp(phase_rad, bit_depth = 255.)

# # mask
# px_radius = 150
# mask = np.zeros(np.shape(phase_int8), dtype="uint8")
# cv2.circle(mask, (int(slm.nx/2), int(slm.ny/2)), px_radius, 1, -1)
# phase_int8 = cv2.bitwise_and(phase_int8, phase_int8, mask=mask)

slm_disp.updateArray(phase_int8)

#### estimate where we should place the first diffracted order array
array_phase = pkread("../tests_daily_log/2021_03_26_atomarray_pattern/w0=5.68mm_nxt=15_nyt=15_offs=True_xt=130.0_yt=130.0_sp=15_bw=None.pkl")

# Need to scale effective beam size by nint. no chopping
beam_i = gauss2d_int(x=slm.xm, y=slm.ym, wx=w0/slm.px, wy=w0/slm.px, x0=slm.nx/2, y0=slm.ny/2)
beam_e = np.sqrt(beam_i)

ft = slm.xe_vi(xu=beam_e, xphi=array_phase)

plt.figure()
plt.imshow(ft)
plt.show()


## Check something

# desired line spacing
line_sp = 67

# obtain the blazed grating
aimed_phase = slm.tile_blazed_xy(line_sp)

ft = slm.xe_vi(xu=beam_e, xphi=aimed_phase)

plt.figure()
plt.imshow(ft)
plt.show()

## Deflect one trap with some desired integer line spacing

# calfile = 'CAL_LSH0802598_810nm.bmp'
calfile="corr_nov19.bmp"

# desired line spacing
line_sp = 4

# obtain the blazed grating
aimed_phase = slm.tile_blazed_xy(line_sp)

# image the correct order i.e. make sure the correct order is on the camera
aimed_phase = (np.fliplr(aimed_phase))

# phi_t = np.zeros((slm.sxga_ny,slm.sxga_nx))
# phi_t[:slm.ny,:slm.nx] = np.array(aimed_phase*256./(2*np.pi))
#
# # wrap and scale to desired bit depth
# phi_t_wrap = np.mod(phi_t+corr, 256.)
# phi_t_scaled = phi_t_wrap*(213./255.)
#
# slm_disp.updateArray(phi_t_scaled.astype(np.uint8))

# convert the phase pattern to BMP
aimed_phase_bmp = slm.convert_bmp(aimed_phase, corr=False, calfile=calfile)

# upload the phase pattern to the SLM
slm_disp.updateArray(aimed_phase_bmp, check_img_size=True)

## testing adding zernike polynomials

# aimed_phase = slm.blazed(xperiod=4, yperiod=4)

# try using only a square region
aimed_phase = slm.tile_blazed_xy(line_sp=4)[:1024,:1024]
aimed_phase = (np.fliplr(aimed_phase))
aimed_phase = slm.pad_square_pattern(aimed_phase)

# up to order 6
cart = RZern(6)
cart.make_cart_grid(slm.xmn, slm.ymn, unit_circle=True)

# cart.nk is the total number of polynomials up to order n. each n has m=n+1 total polynomials
c = np.zeros(cart.nk)

test_zernike = np.zeros(shape=np.shape(aimed_phase))

# kth order is the desired aberration
k = 4
c[k] = 1.

coeff = 0.09
test_zernike += coeff*np.array(cart.eval_grid(c, matrix=True))*2*np.pi
test_zernike = np.nan_to_num(test_zernike, nan=0)

# avoiding rounding issues near 2*pi
test_zernike += -np.min(test_zernike) + 1e-10

mod_pattern = np.mod(test_zernike + aimed_phase, 2*np.pi)*256./(2*np.pi)*213./255.

full_mod_pattern = slm.pad_zeros(mod_pattern)

slm_disp.updateArray(full_mod_pattern.astype(np.uint8))

## testing our correction pattern
""" Just press CTRL+ENTER to run this """

# test_pattern = np.load("/Users/emilyqiu/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_02-22_46_modesz=64_probesz=10/test_wf_corr.npy")
# test_pattern = np.load("C:\\Users\\rydbe\\Dropbox (MIT)\\Calculations\\Emily\\SLM project\\tests_daily_log\\2021_10-11_wf_measurement\\2021_11_02-22_46_modesz=64_probesz=10\\test_wf_corr.npy"
# test_pattern = np.load("C:\\Users\\rydbe\\Dropbox (MIT)\\Calculations\\Emily\\SLM project\\tests_daily_log\\2021_10-11_wf_measurement\\2021_11_19-22_07_modesz=64_probesz=2\\unwrapped_fitted.npy")
# 2021_11_19-22_07_modesz=64_probesz=2
# 2021_11_26-21_18_modesz=64_probesz=2
# test_pattern = np.load(r"Z:\2022-data\2022-03\20220331-wf_correction\19_44_modesz=64_probesz=2\unwrapped_fitted.npy")

# test_pattern = np.load(r"Z:\2022-data\2022-04\20220407-wf_correction\18_41_modesz=64_probesz=2\unwrapped_fitted.npy")  # big beam
# test_pattern = np.load(r"Z:\2022-data\2022-04\20220414-wf_correction\14_05_modesz=64_probesz=2\unwrapped_fitted.npy")   # small beam
test_pattern = np.load(r"Z:\2022-data\2022-04\20220415-wf_correction\11_47_modesz=64_probesz=2\unwrapped_fitted.npy")   # small beam

mod_test_pattern = np.array((-test_pattern)*256./(2*np.pi))
mod_test_pattern = np.mod(mod_test_pattern, 256.)

add_corr = True

# imgiowrite("C:\\Users\\rydbe\\Dropbox (MIT)\\Calculations\\Emily\\SLM project\\v3_final_copy\\corr_nov35.bmp", mod_test_pattern.astype(np.uint8))

aimed_phase = slm.tile_blazed_xy(line_sp=11)*256./(2*np.pi)
# aimed_phase = np.flipud(np.fliplr(aimed_phase))
# aimed_phase = (np.fliplr(aimed_phase))

aimed_phase = slm.get_unit_circ_phase(aimed_phase) # whether to diffract with a circle, else square

full_aimed_phase = slm.pad_square_pattern(aimed_phase)

if add_corr:
    mod_pattern = np.mod(mod_test_pattern + slm.pad_zeros(full_aimed_phase), 256)#*213./255.
else:
    mod_pattern = np.mod(slm.pad_zeros(full_aimed_phase), 256)#*213./255.

# mod_pattern = slm.pad_zeros(np.mod(full_aimed_phase, 256))#*213./255.
bmp = mod_pattern.astype(np.uint8)

slm_disp.updateArray(bmp)

## Testing with code

phase_rad = slm.tile_blazed_xy(line_sp=11)

phase_rad = slm.get_unit_circ_phase(phase_rad)
phase_rad = slm.pad_zeros(slm.pad_square_pattern(phase_rad))

# read the test correction pattern
corr_pattern_rad = -np.load(r"Z:\2022-data\2022-04\20220414-wf_correction\14_05_modesz=64_probesz=2\unwrapped_fitted.npy")

# comment the line below to remove correction pattern
phase_rad += corr_pattern_rad

phase_int = slm.convert_bmp(phase_rad, bit_depth = 255.)
phase_int8 = phase_int.astype(np.uint8)

slm_disp.updateArray(phase_int8)

## Add the correction pattern for array

array_phase = pkread('..\\tests_daily_log\\2021_02_____numeric_results\\precomp_phases\\w0=5.68mm_nxt=50_bw=0.45.pkl')

# w0=5.68mm_nxt=50_bw=0.45.pkl

# pad the phase with zeros to match dimensions of SLM
array_phase_full = slm.pad_square_pattern(array_phase)

# put it into the FOV of camera
# aimed_phase = slm.aim_blazed(xt=slm.nx/3, yt=slm.ny/6)
aimed_phase = slm.tile_blazed_xy(line_sp)
aimed_phase = (np.fliplr(aimed_phase))

phase_disp = slm.convert_bmp(array_phase_full+aimed_phase,corr=True, calfile='corr_nov19.bmp')
slm_disp.updateArray(phase_disp)

##

aimed_phase = slm.tile_blazed_xy(line_sp=4)
aimed_phase = (np.fliplr(aimed_phase))

tot_phase = array_phase_full
beam, ft = slm.predict_array(w0=w0,phi=array_phase_full,nint=1,next=1, chop=True)


## Use aim_blazed function for any spatial period along (x,y)

# modulate bit depth, value between [0,1]
mod_depth = 1

# deflect the trap to a target location with respect to zero order
aimed_phase = np.mod(slm.aim_blazed(-slm.nx/4.5, -slm.ny/4.5),2*np.pi)*mod_depth

aimed_phase_bmp = slm.convert_bmp(aimed_phase, corr=True)

slm_disp.updateArray(aimed_bmp)

# look at FT of the phase pattern
intensity_dist = slm.predict_array(w0=w0,phi=aimed_phase,nint=2,next=1)

## Use SLM as Fresnel lens to focus

# positive values is focus, negative values is defocus
foc = 400e-3

# calculate the phase pattern
focus_phase = slm.focus(foc=foc)

# add the two phase patterns together before converting to bmp
phase_bmp = slm.convert_bmp(focus_phase+aimed_phase, corr=True)
slm_disp.updateArray(phi_align_disp)

## Defocus the image plane of a lens

# focal length of lens
foc = 400e-3

# amount to defocus
z0 = 250e-3

# calculate the phase pattern
defocus_phase = slm.defocus(z0, foc)

phase_bmp = slm.convert_bmp(defocus_phase+aimed_phase, corr=True)
slm_disp.updateArray(phase_bmp)

## Align to center of SLM
# Display four different blazed gratings (with different deflection angles) on the SLM, one in each quadrant
# well aligned to the center if there's equal amounts of power in each order

period = 20

# calculate the phase patterns
phase_q1 = slm.blazed(xperiod=period, yperiod=period)
phase_q2 = slm.blazed(xperiod=period, yperiod=-period)
phase_q3 = slm.blazed(xperiod=-period, yperiod=period)
phase_q4 = slm.blazed(xperiod=-period, yperiod=-period)

# place the patterns onto each quadrant
align_phase = np.empty(shape=(slm.ny,slm.nx))
align_phase[:slm.axy,:slm.axx] = phase_q1[:slm.axy,:slm.axx]
align_phase[slm.axy:,:slm.axx] = phase_q2[slm.axy:,:slm.axx]
align_phase[:slm.axy,slm.axx:] = phase_q3[:slm.axy,slm.axx:]
align_phase[slm.axy:,slm.axx:] = phase_q4[slm.axy:,slm.axx:]

# display onto SLM
align_phase_disp = slm.convert_bmp(align_phase_disp, corr=False)
slm_disp.updateArray(align_phase_disp)


## Generate array with previously saved pkl file

array_phase = pkread('../tests_daily_log/2021_02_____numeric_results/precomp_phases/w0=5.68mm_nxt=20_bw=0.45.pkl')

# pad the array with zeros to match dimensions of SLM
array_phase_full = slm.pad_square_pattern(array_phase)

aimed_phase = slm.tile_blazed_xy(line_sp=4)

phase_disp = slm.convert_bmp(array_phase_full+aimed_phase,corr=False)
slm_disp.updateArray(phase_disp)

## upload a uniform phase pattern or random phase pattern

slm_disp.updateArray(slm.unif)
slm_disp.updateArray(slm.rand)

############# TESTS

## numerical single trap: make sure calculated gaussian trap size is correct, corresponds to the FT

# add internal/external padding
nint = 1
next = 5

# target trap location
xt = -slm.nx/4
yt = -slm.ny/4

# shape of new, padded array array
nyt,nxt = (slm.ny*(nint+next), slm.nx*(nint+next))
xmesh_p, ymesh_p = np.meshgrid(np.linspace(1,nxt,nxt), np.linspace(1,nyt,nyt))

# (?? don't understand/remember this comment) unchopped, only works without internal sampling
xt_ext = xt*(nint+next)
yt_ext = yt*(nint+next)

# expected array image
xt_sim = (slm.nx/2+xt)*(nint+next)+1
yt_sim = (slm.ny/2+yt)*(nint+next)+1

phi_unchopped = 2*np.pi*(xmesh_p*xt_ext/nxt + ymesh_p*yt_ext/nyt)

# Need to scale effective beam size by nint. no chopping
beam_i_p = normalize2d(gauss2d_int(x=xmesh_p, y=ymesh_p, wx=nint*w0/slm.px, wy=nint*w0/slm.px, x0=nxt/2, y0=nyt/2))
beam_e_p = np.sqrt(beam_i_p)


ft = slm.xe_vi(xu=beam_e_p, xphi=phi_unchopped)
ft_exp = gauss2d_int(x=xmesh_p, y=ymesh_p, wx=wx*(nint+next), wy=wy*(nint+next), x0=xt_sim, y0=yt_sim)

ycut = int(yt_sim)

plt.figure()
plt.plot(ft[ycut,:])
plt.plot(np.max(ft[ycut,:])/np.max(ft_exp[ycut,:])*ft_exp[ycut,:],'--')
plt.show()


## Check two trap separation/interferences
calfile="corr_nov19.bmp"

trapsz = 2.2e-6
target_sep = 10e-6

# trapsz/target_sep = wx/sepx = wy/sepy
# for 10 micron separation, 3.7 pixels in x, 3 pixels in y
sepx = wx*target_sep/trapsz
sepy = wy*target_sep/trapsz

# sep = 3.7
sep = 3.1

xt = -slm.nx/4
yt = slm.ny/4

# separation along x
aimed1 = slm.aim_blazed(xt+sep, yt)
aimed2 = slm.aim_blazed(xt-sep, yt)

# # separation along y
# aimed1 = slm.aim_blazed(xt, yt+sep)
# aimed2 = slm.aim_blazed(xt, yt-sep)

phi = np.angle(np.exp(1j*aimed1)+np.exp(1j*aimed2))
# phi = aimed1

phi_align_disp = slm.convert_bmp(phi, corr=True, calfile=calfile)
slm_disp.updateArray(phi_align_disp)

## Check numerics

# obtain the blazed grating
phi = slm.tile_blazed_xy(line_sp)

nint = 1
next = 5

# phi_in = slm.pad_int(phi, n_repeats = nint)
# phi_in_ext = slm.pad_ext(phi_in, n_repeats = next)

# # phi_ext = slm.pad_ext(phi_in, n_repeats = next)
# # phi_in_ext = slm.pad_int(phi, n_repeats = nint)

beam, ft = slm.predict_array(w0=w0,phi=phi,nint=1,next=5, chop=True)

##
# # # chopped phase pattern due to pad_ext
# # xmesh_ext =
# # ny_ext, nx_ext = (self.ny*(next+1),self.nx*(next+1))

# expected array image, top left corner
xt_sim1 = (slm.nx/2+xt-sep)*(nint+next)+1
xt_sim2 = (slm.nx/2+xt+sep)*(nint+next)+1

yt_sim = (slm.ny/2+yt)*(nint+next)+1

# Shape of new array
nyt,nxt = (slm.ny*(nint+next), slm.nx*(nint+next))
xmesh_p, ymesh_p = np.meshgrid(np.linspace(1,nxt,nxt), np.linspace(1,nyt,nyt))

# unchopped, only works without internal sampling
xt_ext = xt*(nint+next)
yt_ext = yt*(nint+next)

phi_unchopped = 2*np.pi*(xmesh_p*xt_ext/nxt + ymesh_p*yt_ext/nyt)

# Need to scale effective beam size by nint
beam_i_p = normalize2d(gauss2d_int(x=xmesh_p, y=ymesh_p, wx=nint*w0/slm.px, wy=nint*w0/slm.px, x0=nxt/2, y0=nyt/2))
beam_e_p = np.sqrt(beam_i_p)

chop = False

if chop:
    beam_e = np.zeros(shape=(nyt,nxt))
    beam_e[int(nyt/2-ny/2):int(nyt/2+ny/2),int(nxt/2-nx/2):int(nxt/2+nx/2)] = beam_e_p[int(nyt/2-ny/2):int(nyt/2+ny/2),int(nxt/2-nx/2):int(nxt/2+nx/2)]


# chopped
ft = slm.xe_vi(xu=beam_e_p, xphi=phi_in_ext)

# unchopped
ft_exp = gauss2d_int(x=xmesh_p, y=ymesh_p, wx=wx*(nint+next), wy=wy*(nint+next), x0=xt_sim1, y0=yt_sim)#+gauss2d_int(x=xmesh_p, y=ymesh_p, wx=wx*(nint+next), wy=wy*(nint+next), x0=xt_sim2, y0=yt_sim)


# plot
ycut = int(yt_sim)

plt.figure()
plt.plot(ft[ycut,:])
plt.plot(np.max(ft[ycut,:])/np.max(ft_exp[ycut,:])*ft_exp[ycut,:],'--')
plt.show()

# slm_disp.updateArray(phi_align_disp)


## Upload a phase pattern, take a picture/save

camera = pylon.InstantCamera(pylon.TlFactory_GetInstance().CreateFirstDevice())
camera.Open()

# Sample phase pattern
phi0 = imageio.imread('10x10test_full.bmp')

phi0_disp = convert_bmp(phi0, corr=False)
slm_disp.updateArray(phi0_disp)

img = take_image()
imageio.imwrite(base_folder + base_filename + 'firstorder.bmp', img)

# Close the devices
slm.close()
camera.Close()

# plt.imshow(img, cmap=plt.get_cmap('gray'), vmin=0, vmax=50)
# plt.imshow(img, cmap=plt.get_cmap('copper'), vmin=0, vmax=120)
plt.imshow(img)
plt.show()

############ TESTING THE CORRECTION PATTERN

## check hamamtsu correction pattern
readphase = imageio.imread('../export_software_nocorr.bmp') #CAL_LSH0802598_810nm
slm_full = np.zeros((1024,1280))
slm_full[:,:1272] = readphase.copy()

slm_disp.updateArray(slm_full)

## this one looked terrible for some reason, maybe because the wavefront correction completely washed away the first order? not sure..
# also we didn't add the negative sign

single_mode = slm.tile_blazed_xy_int(4, 24)
curr_phase_disp = slm.pad_zeros(single_mode).astype(np.uint8)

# slm_disp.updateArray(curr_phase_disp+mod_test_pattern)

## manually add the correction pattern for array

array_phase = pkread('..\\tests_daily_log\\2021_02_____numeric_results\\precomp_phases\\w0=5.68mm_nxt=50_bw=0.45.pkl')

# pad the array with zeros to match dimensions of SLM
array_phase_full = np.mod(slm.pad_zeros(slm.pad_square_pattern(array_phase)),2*np.pi)*256./(2*np.pi)

aimed_phase = slm.blazed(xperiod=3, yperiod=6)*256./(2*np.pi)
aimed_phase = np.flipud(np.fliplr(aimed_phase))

aimed_phase_full = slm.pad_zeros(aimed_phase)

mod_pattern = np.mod(mod_test_pattern + aimed_phase_full + array_phase_full, 256)*213./255.

# phase_disp = slm.convert_bmp(array_phase_full+aimed_phase,corr=False)
slm_disp.updateArray(mod_pattern.astype(np.uint8))

## try 0, 2pi, 0, pi
#
# line_sp = 2
# base_pattern_2d = np.array([[0, 2*np.pi], [2*np.pi, 0]])
# base_pattern_2d = slm.pad_int(base_pattern_2d, n_repeats=line_sp)
#
# # tile the pattern to fill the whole SLM
# phase = np.tile(base_pattern_2d, reps=(int(np.ceil(slm.ny/line_sp)+1), int(np.ceil(slm.nx/line_sp)+1)))
#
# full_phase = slm.pad_zeros(phase[:slm.ny, :slm.nx])
#
# mod_pattern = np.mod(full_phase, 256)*100./255.
#
# slm_disp.updateArray(mod_pattern.astype(np.uint8))
