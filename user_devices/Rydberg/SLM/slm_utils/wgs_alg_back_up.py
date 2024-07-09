'''
Weighted GS implementation.
Option to use phase-fixing in image plane (see Donggyu's paper on LOFA generation)
Option to use MRAF algorithm.

Emily Qiu

For Zelux camera:
thorlabs_tsi_sdk.tl_camera TLCameraSDK

Integrated into experiment
April 26, 2022

Note that indexing the array directly via e.g.
vtarget_i_new[slm_attr.trap_xy[iy,ix]] does not seem to work, could be an issue
with python3 vs python2
'''


import sys
import os
import time
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

save_path = "Z:\\Calculations\\Emily\\SLM project\\v4_array_patterns\\"
base_filename = time.strftime("%Y_%m_%d-%H_%M__")

# our own files/functions
from slm_utils.devices_attr import SLMx13138
from slm_utils import slmpy_updated as slmpy
from slm_utils import freq_funcs
from slm_utils.freq_funcs import qim

# # Allied vision vimba sdk
# from vimba_sdk.Vimba_5_1.VimbaPython_Source.vimba import *

# Thorlabs Zelux camera
os.chdir(os.getcwd() + "\\zelux_sdk\\Scientific Camera Interfaces\\SDK\\Python Toolkit\\examples")

from windows_setup import configure_path
configure_path()

from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE

## params

slm_attr = SLMx13138()

# # fraction of total trapping plane to be used for array
# # b/c of array indexing, do not set to 1 (can do 0.9 repeated)
# bw = 0.22

# Array params
nx_traps = 20
ny_traps = 1
n_traps = nx_traps*ny_traps

compensate_de = False

sp_x = 6 						# separation between traps in pixels
sp_y = sp_x

# sp_x = 12 						# hexagonal array base tiling
# sp_y = 6

# sp_x = 8*2 						# hexagonal array base tiling
# sp_y = 7*2

offx = slm_attr.xt
offy = slm_attr.yt

# Algorithm
lofa = False
memory = True 				# of WGS scaling factor g. If false, use expression in Nogrette paper

g_wgsa = 0.7	           		# g = 0 limits to GS
# m_mraf = 0.6	           		# m = relative target intensity in signal region
# offset_mraf = sys.float_info.epsilon

# Iterations
no_iter_wgs = 12
no_iter = 50

## get the array indices

array_type = ""
filename = "nxt={nx_traps:02d}_nyt={ny_traps:02d}_sepx={sp_x:.3f}_sepy={sp_y:.3f}_offx={offx:.2f}_offy={offy:.2f}.pkl".format(nx_traps=nx_traps, ny_traps=ny_traps, sp_x=sp_x, sp_y=sp_y, offx=offx, offy=offy)

# calculate trap indices
slm_attr.get_array_indices(nx_traps=nx_traps, ny_traps=ny_traps, sp_x=sp_x, sp_y=sp_y)

## arb arrays
pic = imageio.imread(r'Z:\Calculations\Emily\SLM project\images\cua.png', pilmode='L')

array_type = "arb\\"

lattice_spacing = 4
threshold = 200
downsample = 7

# # aws
# lattice_spacing = 5
# threshold = 200
# downsample = 6

pic = pic[0::downsample,0::downsample]
pic_mask = (pic < threshold)

nyp, nxp = np.shape(pic)
xmp, ymp = np.meshgrid(np.linspace(1,nxp,nxp), np.linspace(1,nyp,nyp))

lattice_x = (xmp % lattice_spacing == 0)
lattice_y = (ymp % lattice_spacing == 0)

reg_lattice = (lattice_x & lattice_y)

target_array = (pic_mask & reg_lattice)
print(np.sum(target_array))

slm_attr.set_array_indices(target_array=target_array, lattice_spacing=lattice_spacing, xt=slm_attr.xt+20)

# draw target intensity distribution
plt.figure()
plt.imshow(slm_attr.vtarget0_i, cmap='binary')
plt.colorbar()
plt.plot(np.arange(slm_attr.n), np.repeat(slm_attr.ax,slm_attr.n),'b--')
plt.plot(np.repeat(slm_attr.ax,slm_attr.n),np.arange(slm_attr.n),'b--')
plt.title('Initial intensity distribution')
plt.show()

# filename = 'cua_123traps_xt+20.pkl'
# filename = 'aws_90traps_nocomp_xt+20.pkl'

## Store variables


# define beam in SLM plane
beam_i = freq_funcs.normalize2d(freq_funcs.gauss2d_int(x=slm_attr.xm, y=slm_attr.ym, wx=slm_attr.w0/slm_attr.px, wy=slm_attr.w0/slm_attr.px, x0=slm_attr.ax, y0=slm_attr.ax))
beam_e = np.sqrt(beam_i)

ntrap_shape = np.append(no_iter, np.shape(slm_attr.trap_xy)[:2])
narray_shape = (no_iter,slm_attr.n,slm_attr.n)

# Store variables
slm_phase = np.empty(shape=narray_shape)
v_phase = np.full(shape=narray_shape,fill_value=0.)

vtarget_e = np.empty(shape=narray_shape)
g_dyn = np.full(shape=ntrap_shape,fill_value=g_wgsa)

# trap statistics
fit_heights = np.empty(shape=ntrap_shape)
avg_heights = np.empty(no_iter)
stdev_heights = np.empty(no_iter)

# choice of initial phase
slm_phase[0,:] = slm_attr.defocus(z0=1,foc=400e-3) + slm_attr.on_axis_trap
# focus = slm_attr.focus(foc=10)
# aimed = np.mod(slm_attr.aim_blazed(slm_attr.n/8, -slm_attr.n/8), 2*np.pi)
# slm_phase[0,:] = focus+aimed
# slm_phase[0,:] = 2*np.pi*np.random.rand(slm_attr.n,slm_attr.n)

# initial target amplitude
vtarget_e[0,:] = slm_attr.vtarget0_e

vfield_e = slm_attr.xe_ve(xu=beam_e, xphi=slm_phase[0])
vfield_i = slm_attr.e_i(vfield_e)

# # draw initial intensity distribution
# plt.figure()
# plt.imshow(vfield_i, cmap='binary')
# plt.colorbar()
# plt.plot(np.arange(slm_attr.n), np.repeat(slm_attr.ax,slm_attr.n),'b--')
# plt.plot(np.repeat(slm_attr.ax,slm_attr.n),np.arange(slm_attr.n),'b--')
# plt.title('Initial intensity distribution')
# plt.show()

## Plotting

draw = False

# check if traps fall within slm_attr.nboxx and slm_attr.nboxy
ncheck = False

nrangex = 50
nrangey = int(slm_attr.n/slm_attr.n*nrangex)

# # Choose random traps to observe their evolution
# rt1 = int(n_traps*np.random.rand(1))
# rt2 = int(n_traps*np.random.rand(1))
# rt3 = int(n_traps*np.random.rand(1))
# rt1 = 5
# rt2 = 178
# rt3 = 232
# rt4 = 390
rt1 = 5
rt2 = 18
rt3 = 42
rt4 = 84


if draw:

	plt.ion()

	# fig, ax = plt.subplots(2,3,figsize=(18,12))
	fig, ax = plt.subplots(2,3,figsize=(12,8))


	iter_lims = [0,no_iter]
	log_lims = [10**-4,10**0]
	phi_ticks = [-3.14,0,3.14]

	# SLM phase
	cax = ax[0,0]
	xphi_plot = cax.imshow(slm_phase[0][slm_attr.ax-nrangey:slm_attr.ax+nrangey,slm_attr.ax-nrangex:slm_attr.ax+nrangex], cmap='binary')
	xphi_plot.set_clim(vmin=-3.14,vmax=3.14)
	cbar = fig.colorbar(xphi_plot, ax=cax, ticks=phi_ticks, orientation="horizontal")
	cbar.ax.set_xticklabels([r'$-\pi$',r'$0$',r'$\pi$'])
	cax.set_title('Phase in SLM plane')

	# Fourier phase
	cax = ax[1,0]
	vphi_plot = cax.imshow(v_phase[0][slm_attr.ax-nrangey:slm_attr.ax+nrangey,slm_attr.ax-nrangex:slm_attr.ax+nrangex], cmap='binary')
	vphi_plot.set_clim(vmin=-3.14,vmax=3.14)
	cbar = fig.colorbar(vphi_plot, ax=cax, ticks=phi_ticks, orientation="horizontal")
	cbar.ax.set_xticklabels([r'$-\pi$',r'$0$',r'$\pi$'])
	cax.set_title('Phase in image plane')

	# Generated array
	cax = ax[0,1]
	array = cax.imshow(vtarget_e[0], cmap='binary')
	fig.colorbar(array,ax=cax, orientation="horizontal")
	cax.set_title(r'LOFA: $N_{wgs}$ = %s' %(no_iter_wgs) if lofa else 'WGS')

	# Normalized trap height histogram
	cax = ax[0,2]
	histparams = {'bins': 100, 'range':(0,2), 'density':True, 'color': 'royalblue'}
	alpha = np.linspace(0.1,1,no_iter)
	cax.set_ylabel('Counts')
	cax.set_title('Normalized Trap heights')

	# Average trap height + heights of three random traps.
	# Linear scale to see fluctuations, not normalized to look at power efficiency
	cax = ax[1,1]
	cax.set_xlim(iter_lims)
	cax.set_xlabel('Iteration no.')
	cax.set_ylabel('Intensity')
	cax.set_title('Heights of 4 random traps')

	# Width of trap height distribution.
	# Log scale to see fast decrease, normalized
	cax = ax[1,2]
	cax.set_xlim(iter_lims)
	cax.set_ylim(log_lims)
	cax.set_yscale('log')
	cax.set_xlabel('Iteration no.')
	cax.set_ylabel('Intensity (normalized)')
	cax.set_title('Width of distribution')

	fig.tight_layout(pad=3)

## Run iterations

for i in range(50):

	print(i)

	# # Fourier plane
	vfield_e = slm_attr.xe_ve(xu=beam_e, xphi=slm_phase[i])
	vfield_i = slm_attr.e_i(vfield_e)
	vphi = np.angle(vfield_e)

	# # Phase fixing
	if lofa:
		if i == no_iter_wgs:
			print('%s: extract vphi' %(i))
			fix_vphi = vphi

		elif i > no_iter_wgs:
			print('%s: fix' %(i))
			vphi = fix_vphi

		else:
			print('%s: dont fix' %(i))

	v_phase[i] = vphi

	# # # Check to make sure slm_attr.nbox size is appropriate, plot 4 random traps
	if ncheck is True and i == 1:
		checkfig, checkax = plt.subplots(2,2)

		(yid1,xid1) = slm_attr.trap_xy[rt1]
		checkax[0,0].imshow(vfield_i[yid1-slm_attr.nboxy:yid1+slm_attr.nboxy,xid1-slm_attr.nboxx:xid1+slm_attr.nboxx])

		(yid2,xid2) = slm_attr.trap_xy[rt2]
		checkax[0,1].imshow(vfield_i[yid2-slm_attr.nboxy:yid2+slm_attr.nboxy,xid2-slm_attr.nboxx:xid2+slm_attr.nboxx])

		(yid3,xid3) = slm_attr.trap_xy[rt3]
		checkax[1,0].imshow(vfield_i[yid3-slm_attr.nboxy:yid3+slm_attr.nboxy,xid3-slm_attr.nboxx:xid3+slm_attr.nboxx])

		(yid4,xid4) = slm_attr.trap_xy[rt4]
		checkax[1,1].imshow(vfield_i[yid4-slm_attr.nboxy:yid4+slm_attr.nboxy,xid4-slm_attr.nboxx:xid4+slm_attr.nboxx])

		plt.pause(0.1)
		checkfig.show()
		value = input("Is a single trap being resolved?\nIf not, hit 'n'. Otherwise, hit any other key.\n")
		if value == 'n' or value == 'N':
			raise ValueError('Input "n", redefine nbox.')

		else:
			print('nbox OK, continue.')
			# time.sleep(5)

		plt.close(checkfig)

	# # Extract heights
	Itot = 0

	# for curr in range(n_traps):
	for iy,ix in np.ndindex(slm_attr.trap_xy.shape[:2]):


		# (yid, xid) = slm_attr.trap_xy[curr]
		(yid, xid) = slm_attr.trap_xy[iy,ix]

		# Take intensity at single point
		if slm_attr.trap_spacing_x == 1 or slm_attr.nboxx == 0:

			if compensate_de:
				Ii = slm_attr.diff_eff[iy,ix]*np.amax(vfield_i[yid,xid])
			else:
				Ii = np.amax(vfield_i[yid,xid])

		# Take max intensity within small region
		else:
			if compensate_de:
				Ii = slm_attr.diff_eff[iy,ix]*np.amax(vfield_i[yid-slm_attr.nboxy:yid+slm_attr.nboxy,xid-slm_attr.nboxx:xid+slm_attr.nboxx])
			else:
				Ii = np.amax(vfield_i[yid-slm_attr.nboxy:yid+slm_attr.nboxy,xid-slm_attr.nboxx:xid+slm_attr.nboxx])

		if Ii == 0:
			raise ValueError('Encountered trap height of 0, scaling will divide by 0. Quit.')

		# store trap statistics
		fit_heights[i,iy,ix] = Ii
		Itot += Ii

	# Average trap height
	Ibar = Itot/n_traps

	avg_heights[i] = Ibar
	stdev_heights[i] = np.std(fit_heights[i]/Ibar) 		# stdevs normalized to 1

	# # Update target intensity pattern
	vtarget_i_new = np.power(slm_attr.vtarget0_e, 2)

	# for curr in range(n_traps):
	for iy,ix in np.ndindex(slm_attr.trap_xy.shape[:2]):

		(yid, xid) = slm_attr.trap_xy[iy,ix]

		Ii = fit_heights[i,iy,ix]

		if memory:
			g_new = Ibar/Ii*g_dyn[i,iy,ix]
			vtarget_i_new[yid, xid] *= g_new

		else:
			vtarget_i_new[yid, xid] = Ibar/(1-g_wgsa*(1-Ii/Ibar))

	vtarget_e_new = np.sqrt(vtarget_i_new)

	# # SLM plane
	xfield_e = slm_attr.ve_xe(vu=vtarget_e_new, vphi=vphi)
	xphi = np.angle(xfield_e)

	if draw:
		# # Update plots
		array.set_data(vfield_i)
		array.autoscale()

		xphi_plot.set_data(xphi[slm_attr.ax-nrangey:slm_attr.ax+nrangey,slm_attr.ax-nrangex:slm_attr.ax+nrangex])
		vphi_plot.set_data(vphi[slm_attr.ax-nrangey:slm_attr.ax+nrangey,slm_attr.ax-nrangex:slm_attr.ax+nrangex])

		# Histogram
		cax = ax[0,2]
		# cax.cla()						# clear
		histparams['alpha']=alpha[i]		# impove visibility
		if i == no_iter-1: 		# Final plot, solid face colour
			histparams['color']='b'
		cax.hist(fit_heights[i]/Ibar,**histparams)
		# cax.autoscale()

		# 4 random traps
		cax = ax[1,1]
		cax.plot(np.arange(0,i+1),avg_heights[:i+1],'r--')
		cax.plot(np.arange(0,i+1),fit_heights[:i+1,rt1],'gold',linewidth=2)
		cax.plot(np.arange(0,i+1),fit_heights[:i+1,rt2],'lightsalmon',linewidth=2)
		cax.plot(np.arange(0,i+1),fit_heights[:i+1,rt3],'orange',linewidth=2)
		cax.plot(np.arange(0,i+1),fit_heights[:i+1,rt4],'darkgoldenrod',linewidth=2)

		cax.legend(['Mean', 'Trap %s' %(rt1),'Trap %s' %(rt2),'Trap %s' %(rt3), 'Trap %s' %(rt4)])

		# Height distibution width
		cax = ax[1,2]
		cax.plot(np.arange(0,i+1),stdev_heights[:i+1],'lightblue')

		fig.canvas.draw()
		fig.canvas.flush_events()

	# Update data
	if i == no_iter-1:
		break

	slm_phase[i+1] = xphi
	vtarget_e[i+1] = vtarget_e_new
	g_dyn[i+1] = np.multiply(np.divide(Ibar, fit_heights[i]), g_dyn[i])


slm_phase_final = slm_phase[-1].copy()
# plt.savefig(base_folder + base_filename + '.pdf', transparent=True)

# save the phase
freq_funcs.pkwrite(var=slm_phase_final, fileName=save_path+array_type + base_filename+filename)

qim(vfield_i)

## Read/upload the phase
slm = slmpy.SLMdisplay()

slm_final = pkread('Tests/2021_03_24/clean.pkl')

# fixing dimensions
side = int((1272-1024)/2)
full_pattern = np.zeros(shape=(1024,1272))
full_pattern[:,side:1272-side] = slm_final.copy()

# calculate any additional shifts needed
slmfull = SLM(full=True)
aimed = np.mod(slmfull.aim_blazed(-slmfull.nx/8, -slmfull.ny/8), 2*np.pi)

# display on SLM
slm_full_disp = slm_attr.convert_bmp(full_pattern+aimed,corr=True)
slm.updateArray(slm_full_disp)


##
filename = 'w0=5.68mm_nxt=1_bw=0.45_offs=True_sp=6.pkl' ##y
# filename = 'w0=5.68mm_nxt=2_bw=0.225_offs=True_sp=20.pkl' ##x

slm_final = pkread('Tests/2021_03_14/twotrap_y/' + filename)

# Add shift
# nx/8 = ny/8 = 159
# trap spacing = 13
slmfull = SLM(full=True)

# CENTER (slm_attr.n/8, -slm_attr.n/8)
aimed = np.mod(slmfull.aim_blazed(-slmfull.nx/8, -slmfull.ny/8), 2*np.pi)
# aimed = np.mod(slm_attr.aim_blazed(-150,-160),2*np.pi)


# fixing dimensions
slm_full = np.zeros(shape=(1024,1272))
# slm_full[:,side:1272-side] = slm_attr.aim_blazed(slm_attr.n/8,-slm_attr.n/8)
slm_full[:,side:1272-side] = slm_final.copy()# + aimed# + spher


slm_full_disp = slm_attr.convert_bmp(slm_full+aimed,corr=True)
slm.updateArray(slm_full_disp)

## Incremental shift in in SLM plane for small
# camera = instrument(list_instruments()[0], reopen_policy='reuse')
# camera.open()

slmfull = SLM(full=True)
slm = slmpy.SLMdisplay(isImageLock = True)

side = int((1272-1024)/2)
xshift = np.arange(0,512, 25) #int(512/2) # between 0 and 512
yshift = np.arange(0,512, 25) #int(512/2) # between 0 and 512

filename = 'w0=5.68mm_nxt=10_bw=0.45_offs=True_sp=26.pkl'
#'w0=5.68mm_nxt=20_bw=0.45_offs=True_sp=13.pkl'

slm_final = pkread('Tests/2021_03_22/half_slm/' + filename)

for xi in xshift:
	for yj in yshift:

		# fixing dimensions
		slm_full = np.zeros(shape=(1024,1272))
		slm_full[yj:1024-512+yj,side+xi:1272-side-512+xi] = slm_final.copy()

		slm_full_disp = slm_attr.convert_bmp(slm_full,corr=True)
		slm.updateArray(slm_full_disp)

		time.sleep(0.5)

		filename = 'yshift={:03d}_xshift={:03d}.bmp'.format(yshift, xshift)

		im = Image.fromarray(camera.grab_image(exposure_time=tau))
		im.save('Tests/2021_03_22/half_slm_sp=26/' + filename,'BMP')

## Incremental shift in image plane
# camera = instrument(list_instruments()[0], reopen_policy='reuse')
# camera.open()

slmfull = SLM(full=True)
slm = slmpy.SLMdisplay(isImageLock = True)

side = int((1272-1024)/2)

filename = 'w0=5.68mm_nxt=1_bw=0.45_offs=True_sp=13.pkl' ##y
# filename = 'w0=5.68mm_nxt=2_bw=0.225_offs=True_sp=20.pkl' ##x

slm_final = pkread('Tests/2021_03_14/twotrap_y/' + filename)

# CENTER (slm_attr.n/8, -slm_attr.n/8)
aimed = np.mod(slmfull.aim_blazed(+slmfull.nx/8, +slmfull.ny/8), 2*np.pi)

# fixing dimensions
slm_full = np.zeros(shape=(1024,1272))
slm_full[:,side:1272-side] = slm_final.copy()# + aimed# + spher

slm_full_disp = slm_attr.convert_bmp(slm_full+aimed,corr=True)
slm.updateArray(slm_full_disp)

xincr = np.arange(int(-slmfull.nx/8),int(slmfull.nx/8)+60)

for i in range(len(xincr)):
	aimed = np.mod(slmfull.aim_blazed(xincr[i], 0), 2*np.pi)

	slm_full_disp = slm_attr.convert_bmp(slm_full+aimed,corr=True)
	slm.updateArray(slm_full_disp)

	time.sleep(0.5)

	filename = 'yoffs=-ny_8_xoffs={:03d}.bmp'.format(xincr[i]+int(slmfull.nx/8))

	im = Image.fromarray(camera.grab_image(exposure_time=tau))
	im.save('Tests/2021_03_21/yoffs=-ny_8/' + filename,'BMP')

## subroutines
#
# def take_image(camera):
# 	# Assume global camera = pylon.InstantCamera()
# 	# passing it as a function argument leads to Grab TimeoutException
# 	camera.StartGrabbing()
# 	grabResult = camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
#
# 	img_arr = np.array(grabResult.Array)
# 	# img_arr = np.fliplr(img_arr)			# determined based on direction of deflected trap
#
# 	grabResult.Release()
# 	camera.StopGrabbing()
# 	return img_arr.astype(int)

## WGSA

# Get real indices in image

# # Get SLM -> camera mapping

# # Basler camera
# camera = pylon.InstantCamera(pylon.TlFactory_GetInstance().CreateFirstDevice())
# camera.Open()

# # this seems to work ok, but technically instrument() should be only called once,
# # saved, and passed around. closing does not require calling instrument() again.
# # once camera.close() is called, can open the software and stream feed as usual
camera = instrument(list_instruments()[0], reopen_policy='reuse')
camera.open()

qim(camera.grab_image())

##

img_trap_xy = [(0,0)]*n_traps 				# in the form (y,x), interpolated coordinates
fit_trap_xy = [(0,0)]*n_traps 				# in the form (y,x), fitted coords
fit_params = np.empty(shape=(n_traps,3))	# return parameters of fit (height, width)

# 1. Zoom in on array
# img = take_image(camera)
img = camera.grab_image()
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
box = np.array(plt.ginput(2)).astype(int)					# Top left, Bottom right of box
plt.close()

box_sz = int(np.linalg.norm(np.subtract(box[0],box[1]))/2) 	# cleaner indexing, use 1/2

# 3. Get location of array in camera, relative to the index of upper left corner displayed
plt.figure()
plt.imshow(zoomed)
plt.get_current_fig_manager().window.showMaximized()
corners = np.array(plt.ginput(3)).astype(int) 		# Top left, Top right, Bottom right, trap center
plt.close()


# # # Old way
# # # Locations of corner traps in image, in [x,y] form
# # loc_1 = zoom[0] + corners[0]
# # loc_nsq = zoom[0] + corners[1]
# #
# # # Scaling using linear dimensions of arrays
# # array_sz = np.linalg.norm(np.subtract(slm_attr.trap_xy[0],slm_attr.trap_xy[-1])) 		# in numerics
# # l1 = np.linalg.norm(np.subtract(corners[0],corners[1]))
# # l2 = np.linalg.norm(np.subtract(corners[1],corners[2]))
# # L = np.sqrt(2)*np.average([l1,l2])
# # scale_factor = L/array_sz
# #
# #
# # # Total angle of rotation in the image, positive is anti-clockwise
# # # This works only for square arrays atm b/c doing pi/4 fixed rotation
# # angle = get_angle_imshow(corners[0], corners[2])
# # rm = rotation_matrix(angle)

# Find points of maximum intensity, use that pixel as index
sz = 10
t1 = zoomed[corners[0][1]-sz:corners[0][1]+sz,corners[0][0]-sz:corners[0][0]+sz]
tn = zoomed[corners[1][1]-sz:corners[1][1]+sz,corners[1][0]-sz:corners[1][0]+sz]
tn2 = zoomed[corners[2][1]-sz:corners[2][1]+sz,corners[2][0]-sz:corners[2][0]+sz]

dy0,dx0 = np.unravel_index(np.argmax(t1, axis=None), t1.shape)
dy1,dx1 = np.unravel_index(np.argmax(tn, axis=None), tn.shape)
dy2,dx2 = np.unravel_index(np.argmax(tn2, axis=None), tn2.shape)

loc_1 = zoom[0] + corners[0] + [dy0-sz, dx0-sz]
loc_n = zoom[0] + corners[1] + [dy1-sz, dx1-sz]
loc_nsq = zoom[0] + corners[2] + [dy2-sz, dx2-sz]


# Locations of corner traps in image, in [x,y] form
loc_1 = zoom[0] + corners[0]
loc_n = zoom[0] + corners[1]

# Scaling using linear dimensions of arrays
array_sz = np.linalg.norm(np.subtract(slm_attr.trap_xy[0],slm_attr.trap_xy[-1])) 		# in numerics
l1 = np.linalg.norm(np.subtract(loc_1,loc_n))
l2 = np.linalg.norm(np.subtract(loc_n,loc_nsq))
L = np.sqrt(2)*np.average([l1,l2])
scale_factor = L/array_sz


# Total angle of rotation in the image, positive is anti-clockwise
# This works only for square arrays atm b/c doing pi/4 fixed rotation
angle = get_angle_imshow(loc_1,loc_nsq)
rm = rotation_matrix(angle)

# plt.figure()
# plt.imshow(img)
for curr in range(n_traps):
	# Relative to index of first trap, in the form [y,x]
	rotated_vec = np.dot(rm, np.subtract(slm_attr.trap_xy[curr],slm_attr.trap_xy[0]).reshape(2,1)).reshape(1,2)[0]

	# Scale from numerics to image dimensions
	rotated_vec_sc = (scale_factor*rotated_vec).astype(int)

	# New rotated coordinates
	img_trap_xy[curr] = (loc_1[1]+rotated_vec_sc[0],loc_1[0]+rotated_vec_sc[1])

	# plt.scatter(img_trap_xy[curr][1],img_trap_xy[curr][0])
# plt.show()

# # Fit to peaks, update trap indices from image in fit_trap_xy
# fitted_array = np.empty(shape=(cam.ny,cam.nx))

## Show relevant region

no_iter_fb = 20

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

g_dyn_fb = np.full(shape=(no_iter_fb,n_traps),fill_value=g_wgsa)

slm_phase_fb[0,:] = slm_final

fit_heights_fb = np.empty(shape=(no_iter_fb,n_traps))
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

	if lofa:
		vphi = fix_vphi

	v_phase_fb[i] = vphi


	Itot = 0
	for curr in range(n_traps):

		(yid, xid) = img_trap_xy[curr]

		# Don't do this, easier to get it from user input
		# box_sz = int(nbox*wt/px_b)

		# 1. take maximum of region
		ydata = img[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz]

		Ii = np.amax(ydata)
		if Ii == 0:
			raise ValueError('Encountered trap height of 0, scaling will divide by 0. Quit.')

		fit_heights_fb[i,curr] = Ii
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

	Ibar = Itot/n_traps

	avg_heights_fb[i] = Ibar
	stdev_heights_fb[i] = np.std(fit_heights_fb[i]/Ibar) 		# stdevs normalized to 1

	# # # # Update target
	vtarget_i_new = np.power(vtarget0_e, 2)

	for curr in range(n_traps):
		Ii = fit_heights_fb[i,curr]

		if memory:
			g_new = Ibar/Ii*g_dyn_fb[i,curr]
			vtarget_i_new[slm_attr.trap_xy[curr]] *= g_new

		else:
			vtarget_i_new[slm_attr.trap_xy[curr]] = Ibar/(1-g_wgsa*(1-Ii/Ibar))

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
	slm_full[:,side:1272-side] = xphi.copy()
	slm_full_disp = slm_attr.convert_bmp(slm_full,corr=True)
	slm.updateArray(slm_full_disp)
	img = take_image(camera)

	# img_trap.set_data(img)
	# img_trap.autoscale()
	#
	# fig.canvas.draw()
	# fig.canvas.flush_events()

slm_phase_final_fb = slm_phase_fb[-1].copy()

# save the phase
pkwrite(var=slm_phase_final_fb, fileName=fb_folder + 'final_phases_feb3\\' + filename)
pkwrite(var=fit_heights_fb, fileName=fb_folder + 'heights(t)_feb3\\'+ filename)

camera.Close()

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


