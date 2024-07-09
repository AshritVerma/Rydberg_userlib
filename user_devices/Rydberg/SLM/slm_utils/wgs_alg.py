'''
Weighted GS implementation.
Option to use phase-fixing in image plane (see Donggyu's paper on LOFA generation)
Option to use MRAF algorithm.
Option to use L-BFGS

Emily Qiu

For Zelux camera:
thorlabs_tsi_sdk.tl_camera TLCameraSDK

Added L-BFGS algorithm
May 11, 2023

Integrated into experiment
April 26, 2022

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

import torch
import torch.optim as optim
import matplotlib.pyplot as plt


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

# # Thorlabs Zelux camera libraries
os.chdir(os.getcwd() + "\\zelux_sdk\\Scientific Camera Interfaces\\SDK\\Python Toolkit\\examples")

from windows_setup import configure_path
configure_path()

# from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
# from thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
# from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE

# # seems we need to add this when we switched to RoyAL... not sure why configure_path does not seem to work anymore
os.chdir(r"C:\Users\RoyAL\labscript-suite\Rydberg_userlib\user_devices\Rydberg\SLM/")

from zelux_sdk.thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from zelux_sdk.thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from zelux_sdk.thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE


## params

slm_attr = SLMx13138()

# # fraction of total trapping plane to be used for array
# # b/c of array indexing, do not set to 1 (can do 0.9 repeated)
# bw = 0.22

# Array params
nx_traps = 3
ny_traps = 3
n_traps = nx_traps*ny_traps

compensate_de = False

# 6 pixels = 10um
sp_x = 8 						# separation between traps in pixels
sp_y = sp_x

# sp_x = 12 						# hexagonal array base tiling
# sp_y = 6

# sp_x = 8*2 						# hexagonal array base tiling
# sp_y = 7*2

offx = slm_attr.xt
offy = slm_attr.yt

# Algorithm
use_wgs = True
use_lofa = False
use_memory = True 				# memory of WGS scaling factor g. If false, use expression in Nogrette paper

use_lbfgs = not use_wgs

g_wgsa = 0.7	           		# g = 0 limits to GS
# m_mraf = 0.6	           		# m = relative target intensity in signal region
# offset_mraf = sys.float_info.epsilon

# Iterations
no_iter_wgs = 12
no_iter = 100

## get the array indices

# for testing
array_type = ""

# # top hats
# array_type = "extended_objects\\"

filename = "nxt={nx_traps:02d}_nyt={ny_traps:02d}_sepx={sp_x:.3f}_sepy={sp_y:.3f}_offx={offx:.2f}_offy={offy:.2f}.pkl".format(nx_traps=nx_traps, ny_traps=ny_traps, sp_x=sp_x, sp_y=sp_y, offx=offx, offy=offy)

# calculate trap indices
slm_attr.get_array_indices(nx_traps=nx_traps, ny_traps=ny_traps, sp_x=sp_x, sp_y=sp_y)

## delete some array indices, syntax np.delete(obj, indices, axis)
# # delete(i, 0) - deletes row i
# # delete(j, 1) - deletes column j
# temp_array = slm_attr.trap_xy.copy()
# temp_array = np.delete(temp_array, 3, 1)
# slm_attr.trap_xy = temp_array.copy()

# delete one at a time. need to change the list of trap indices so it's a 1D list and not a matrix due to limitation of np.delete() function
# 4 detectors: indices_to_delete = [1,3,5,7]
# 3 detectors: indices_to_delete = [1,3,5,6,7]
# 2 detectors: indices_to_delete = [1,2,3,5,6,7]
# 1 detectors:
indices_to_delete = [0,1,2,3,5,6,7]
temp_array = np.reshape(slm_attr.trap_xy, (-1, 2))
initial_ntraps = len(temp_array)
print(initial_ntraps)

temp_array = np.delete(temp_array, indices_to_delete, 0)
final_ntraps = len(temp_array)
print(final_ntraps)
print(temp_array)

slm_attr.trap_xy = np.reshape(temp_array, (1, final_ntraps, 2))


##slm_attr.trap_xy = temp_array.copy()
# update target intensity pattern
slm_attr.get_target_int()

# update the filename
filename = '1detect_' + filename

## arb arrays
# # pic = imageio.imread(r'Z:\Calculations\Emily\SLM project\images\mit.png', pilmode='L')
# pic = imageio.imread(r'Z:\Calculations\Emily\SLM project\images\cua.png', pilmode='L')
#
# array_type = "arb\\"
#
# # # mit
# # lattice_spacing = 3
# # threshold = 50
# # downsample = 20
# # init_pt = 15
#
# # cua
# lattice_spacing = 4
# threshold = 200
# downsample = 10
# init_pt = 1
#
# # # aws
# # lattice_spacing = 5
# # threshold = 200
# # downsample = 6
#
#
# pic = pic[init_pt::downsample,init_pt::downsample]
# pic_mask = (pic < threshold)
# # for MIT
# # pic_mask = (pic > threshold)
# # qim(pic_mask)
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
# # filename = 'cua_168traps_2023.pkl'
# filename = 'cua_105traps_2023.pkl'
# # filename = 'mit_113traps_2023.pkl'
#
# # filename = 'mit_33traps_xt+20.pkl'
# # filename = 'cua_123traps_xt+20.pkl'
# # filename = 'aws_90traps_nocomp_xt+20.pkl'

## Store variables
# ratio_flengths = (12/4.51)
# slm_attr.w0 = 3.75e-3/ratio_flengths

# define beam in SLM plane
beam_i = freq_funcs.normalize2d(freq_funcs.gauss2d_int(x=slm_attr.xm, y=slm_attr.ym, wx=slm_attr.w0/slm_attr.px, wy=slm_attr.w0/slm_attr.px, x0=slm_attr.ax, y0=slm_attr.ax))
beam_e = np.sqrt(beam_i)

# np shapes for initializing relevant variables
ntrap_shape = np.append(no_iter, np.shape(slm_attr.trap_xy)[:2])
narray_shape = (no_iter,slm_attr.n,slm_attr.n)

# Store variables
slm_phase = np.empty(shape=narray_shape)
v_phase = np.full(shape=narray_shape,fill_value=0.)

vtarget_e = np.empty(shape=narray_shape)
# dynamic g factor
g_dyn = np.full(shape=ntrap_shape,fill_value=g_wgsa)

# trap statistics
fit_heights = np.empty(shape=ntrap_shape)
avg_heights = np.empty(no_iter)
stdev_heights = np.empty(no_iter)

# choice of initial phase
slm_phase[0,:] = slm_attr.defocus(z0=1,foc=400e-3) + slm_attr.on_axis_trap
# slm_phase[0,:] =  slm_attr.on_axis_trap

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
	cax.set_title(r'LOFA: $N_{wgs}$ = %s' %(no_iter_wgs) if use_lofa else 'WGS')

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

## (1) WGS

if use_wgs:
	for i in range(no_iter):

		print(i)

		# # Fourier plane
		vfield_e = slm_attr.xe_ve(xu=beam_e, xphi=slm_phase[i])
		vfield_i = slm_attr.e_i(vfield_e)
		vphi = np.angle(vfield_e)

		# # Phase fixing
		if use_lofa:
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

			if use_memory:
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

	# # save the phase
	freq_funcs.pkwrite(var=slm_phase_final, fileName=save_path+array_type + base_filename+filename)


qim(vfield_i)
##(1.1) no WGS for 2 traps (doesn't work)

trap_1 = slm_attr.trap_xy[0][0]-slm_attr.n/2
trap_2 = slm_attr.trap_xy[0][1]-slm_attr.n/2

# phase pattern corresponding to each target trap position
phi1 = slm_attr.blazed_pixel(xt=trap_1[1],yt=trap_1[0])
phi2 = slm_attr.blazed_pixel(xt=trap_2[1],yt=trap_2[0])

# # add focal shift
# foc = 1 # assume 1m
# shift_z = slm_attr.defocus(z0=0, foc=foc)

# get the total pattern - may be some small differences in power between the two traps with this method
phase_rad = np.angle(np.exp(1j*phi1)+np.exp(1j*phi2))# + shift_z

vfield_e = slm_attr.xe_ve(xu=beam_e, xphi=phase_rad)
vfield_i = slm_attr.e_i(vfield_e)

qim(vfield_i)

freq_funcs.pkwrite(var=phase_rad, fileName=save_path+array_type + base_filename+'1detect.pkl')
######################################################################################################################
## (2) LBFGS

# initial phase
# # phi0 = freq_funcs.pkread(r"Z:\Calculations\Emily\SLM project\v4_array_patterns\extended_obj\2023_05_11-10_59__nxt=03_nyt=03_sepx=1.000_sepy=1.000_offx=93.09_offy=-93.09.pkl")
# phi0 = freq_funcs.pkread(r"Z:\Calculations\Emily\SLM project\v4_array_patterns\2023_05_11-17_46__nxt=03_nyt=03_sepx=1.000_sepy=1.000_offx=93.09_offy=-93.09.pkl")

phi0 = slm_phase[0].copy()

# initialize lbfgs
if use_lbfgs:

	# first, assume always the same target field for lbfgs
	t_vtarget_e = torch.tensor(slm_attr.vtarget0_e.copy())
	t_vtarget_phi = torch.angle(t_vtarget_e)

	# input field
	t_beam_e = torch.tensor(beam_e)

	# initialize the optimizer = lbfgs
	# x is the phase to be optimized
	x_lbfgs = torch.tensor(phi0, requires_grad = True)

	history_lbfgs = []

	# LBFGS
	lbfgs = optim.LBFGS([x_lbfgs],
		history_size=10,
		max_iter=4,
		line_search_fn="strong_wolfe")

	# # try different algorithms
	# lbfgs = optim.SGD([x_lbfgs], lr=0.1)

	signal_sz = 10
	yc = 418
	xc = 605

	x0 = xc-signal_sz
	x1 = xc+signal_sz

	y0 = yc-signal_sz
	y1 = yc+signal_sz

	# target field, signal region
	# signal parameters have prefix "ts_" instead of "t_"
	ts_vtarget_e = t_vtarget_e[y0:y1,x0:x1]
	ts_vtarget_phi = t_vtarget_phi[y0:y1,x0:x1]

	# goal to minimize loss_fcn()
	def loss_fcn(xphi):

		# # Fourier plane propagator
		t_vfield_e = slm_attr.t_xe_ve(xu=t_beam_e, xphi=x_lbfgs)
		t_vfield_i = slm_attr.t_e_i(t_vfield_e)
		t_vphi = torch.angle(t_vfield_e)

		# cost function

		# (1) difference between the trapping field and the target field
		ts_vfield_e = freq_funcs.t_normalize2d(t_vfield_e[y0:y1,x0:x1])
		ts_vtarget_e = freq_funcs.t_normalize2d(t_vtarget_e[y0:y1,x0:x1])
		difference = t_vfield_e - t_vtarget_e
		# cost = torch.linalg.norm(difference)
		cost = torch.pow(torch.linalg.norm(difference),2)

		# # (2) cost function in (bowman, 2017 opt express)
		# # use full field as the signal region
		# # t_vphi_diff = t_vphi - t_vtar?get_phi
		# product_fields = torch.multiply(torch.conj(t_vtarget_e),t_vfield_e)
		# sum_term = torch.real(product_fields)
		# sum = torch.sum(sum_term)
		# cost = 10**10*((1-sum)**2)

		# # (3) implementation of the signal region
		# ts_vfield_e = freq_funcs.t_normalize2d(t_vfield_e[y0:y1,x0:x1])
		# ts_vphi = freq_funcs.t_normalize2d(t_vphi[y0:y1,x0:x1])
		#
		# # ts_vphi_diff = ts_vphi - ts_vtarget_phi
		# product_fields = torch.multiply(torch.conj(ts_vtarget_e),ts_vfield_e)
		# sum_term = torch.real(product_fields)
		# sum = torch.sum(sum_term)
		# cost = 10**10*((1-sum)**2)

		return cost

	# L-BFGS
	def closure():
		# initialize gradients to zero
		lbfgs.zero_grad()

		# compute the loss
		objective = loss_fcn(x_lbfgs)

		# compute the gradients
		objective.backward()

		return objective


	# iterate
	for i in range(no_iter):

		print(i)

		# append cost
		history_lbfgs.append(loss_fcn(x_lbfgs).item())

		# take optimization step. need the closure() function for conjugate gradient and LBFGS to recompute the model
		# closure will clear gradients, compute loss, and return it
		lbfgs.step(closure)

		# # # SLM plane
		# xfield_e = slm_attr.ve_xe(vu=t_vtarget_e, vphi=vphi)
		# xphi = np.angle(xfield_e)

		# Update data
		if i == no_iter-1:
			break

##
plt.semilogy(history_lbfgs, label='L-BFGS')
plt.ylabel('Cost')
plt.xlabel('Iteration number')
plt.title('Final cost (1-sum)^2: {cost:.3f}'.format(cost=history_lbfgs[-1]/10**10))
plt.legend()
plt.show()


# x_lbfgs = torch.tensor(freq_funcs.pkread('Z:\\Calculations\\Emily\SLM project\\v4_array_patterns\\extended_objects\\2023_05_16-14_01__nxt=06_nyt=06_sepx=1.000_sepy=1.000_offx=93.09_offy=-93.09.pkl'))


# # save the phase
freq_funcs.pkwrite(var=freq_funcs.torch_to_np(x_lbfgs), fileName=save_path+array_type + base_filename+filename)

## (1) end point from algorithm - torch version

vfield_e = slm_attr.t_xe_ve(xu=t_beam_e, xphi=x_lbfgs)
vfield_i = slm_attr.t_e_i(vfield_e)

y0 = 419
x0 = 605
delta = 10

qim(freq_funcs.torch_to_np(vfield_i)[y0-delta:y0+delta,x0-delta:x0+delta])
qim(torch.angle(vfield_e).detach().numpy()[y0-delta:y0+delta,x0-delta:x0+delta])

# # final phase pattern
# qim(np.mod(torch_to_np(x_lbfgs),2*np.pi))
# qim(torch_to_np(x_lbfgs))

# # get efficiency
signal_region = freq_funcs.torch_to_np(vfield_i)[y0-delta:y0+delta,x0-delta:x0+delta]
full_region = freq_funcs.torch_to_np(vfield_i)
print('Pattern efficiency: {frac:.2f} \%'.format(frac=100*np.sum(signal_region)/np.sum(full_region)))

## see the full atom plane
qim(freq_funcs.torch_to_np(vfield_i))
qim(torch.angle(vfield_e).detach().numpy())

## cross section
freq_funcs.qp(freq_funcs.torch_to_np(vfield_i)[y0-delta:y0+delta,x0])

## target
qim(torch_to_np(t_vtarget_e))

## (2) starting point

vfield_e = slm_attr.xe_ve(xu=beam_e, xphi=phi0)
vfield_i = slm_attr.e_i(vfield_e)

qim(vfield_i)
qim(np.angle(vfield_e))
qim(phi0)

## cross section
qp(vfield_i[y0-delta:y0+delta,x0])


## Previous diffraction limited size = 2um

phi_test = slm_attr.on_axis_trap

vfield_e_difflim = slm_attr.xe_ve(xu=beam_e, xphi=phi_test)
vfield_i_difflim = slm_attr.e_i(vfield_e_difflim)

qim(vfield_i_difflim)

# # get efficiency
signal_region = (vfield_i_difflim)[y0-delta:y0+delta,x0-delta:x0+delta]
full_region = (vfield_i_difflim)
print('Pattern efficiency: {frac:.2f} \%'.format(frac=100*np.sum(signal_region)/np.sum(full_region)))

## our current trap = 5um
# define beam in SLM plane

ratio_flengths = (12/4.51)
curr_waist = 3.75e-3/ratio_flengths

beam_i = freq_funcs.normalize2d(freq_funcs.gauss2d_int(x=slm_attr.xm, y=slm_attr.ym, wx=curr_waist/slm_attr.px, wy=curr_waist/slm_attr.px, x0=slm_attr.ax, y0=slm_attr.ax))
beam_e = np.sqrt(beam_i)

phi_test = slm_attr.on_axis_trap

vfield_e_difflim = slm_attr.xe_ve(xu=beam_e, xphi=phi_test)
vfield_i_difflim = slm_attr.e_i(vfield_e_difflim)

qim(vfield_i_difflim)

# # get efficiency
signal_region = (vfield_i_difflim)[y0-delta:y0+delta,x0-delta:x0+delta]
full_region = (vfield_i_difflim)
print('Pattern efficiency: {frac:.2f} \%'.format(frac=100*np.sum(signal_region)/np.sum(full_region)))

## (3) compare, improve padding

next=5
ratio_flengths = (12/4.51)
curr_waist = 3.75e-3/ratio_flengths

_, vfield_i_pad_difflim = slm_attr.predict_array(phi_test,w0=curr_waist, nint=1,next=next)
beam_e_pad, vfield_i_pad = slm_attr.predict_array(freq_funcs.torch_to_np(x_lbfgs),nint=1,next=next)

delta_pad = (next+1)*(delta)

## Check how the cross sections look like
y0_pad = (next+1)*y0
x0_pad = (next+1)*x0

# try to put the edge next to each other
shift_pos = -8
tophat_xsection = vfield_i_pad[y0_pad-delta_pad:y0_pad+delta_pad,x0_pad]
difflim_xsection = vfield_i_pad_difflim[y0_pad-delta_pad-shift_pos:y0_pad+delta_pad-shift_pos,x0_pad]
difflim_xsection_resc = difflim_xsection*np.max(tophat_xsection)/np.max(difflim_xsection)

npts = len(tophat_xsection)


# (1) fit the tophat
ydata = tophat_xsection
xdata = np.arange(npts)

init_vals_top = [np.max(ydata), 30, int(npts/2)-shift_pos, 5]


# super_gauss1d(x, amp, wx, x0, p)
popt_top, pcov_top = scipy.optimize.curve_fit(
	freq_funcs.super_gauss1d,
	xdata = xdata,
	ydata = ydata,
	p0 = init_vals_top,
	# bounds = ([0, 1, 1, xid-box_sz, yid-box_sz], [1, box_sz, box_sz, xid+box_sz, yid+box_sz]),
	# sigma = n.sqrt(img[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz].ravel())
)
# y_fit_top = freq_funcs.super_gauss1d(xdata, *init_vals_top)
y_fit_top = freq_funcs.super_gauss1d(xdata, *popt_top)
fwhm_top = freq_funcs.fwhm(sigma=popt_top[1], p=popt_top[3])

# (1.1) checking how does the p parameter affect it
popt_top_test = popt_top.copy()
popt_top_test[-1] = 1
y_fit_top_test = freq_funcs.super_gauss1d(xdata, *popt_top_test)


# (2) fit the gaussian
ydata = difflim_xsection_resc
xdata = np.arange(npts)

init_vals_gauss = [np.max(ydata), 30, int(npts/2), 1]

# super_gauss1d(x, amp, wx, x0, p)
popt_gauss, pcov_gauss = scipy.optimize.curve_fit(
	freq_funcs.super_gauss1d,
	xdata = xdata,
	ydata = ydata,
	p0 = init_vals_gauss,
	# bounds = ([0, 1, 1, xid-box_sz, yid-box_sz], [1, box_sz, box_sz, xid+box_sz, yid+box_sz]),
	# sigma = n.sqrt(img[yid-box_sz:yid+box_sz,xid-box_sz:xid+box_sz].ravel())
)
# y_fit_gauss = freq_funcs.super_gauss1d(xdata, *init_vals_gauss)
y_fit_gauss = freq_funcs.super_gauss1d(xdata, *popt_gauss)
fwhm_gauss = freq_funcs.fwhm(sigma=popt_gauss[1], p=popt_gauss[3])

plt.figure()
plt.plot(difflim_xsection_resc, color='orange', label='diffraction limited trap 2um (renormalized)')
plt.plot(tophat_xsection, color='blue', label='top hat cross section')

plt.plot(y_fit_gauss, linestyle='--',
	label='diffraction limited trap fitted, w0 = {waist:.2f} px, p = {p:.2f}, FWHM = {fwhm:.2f}'.format(waist=popt_gauss[1], p=popt_gauss[3], fwhm=fwhm_gauss))
plt.plot(y_fit_top,linestyle='--',
	label='top hat fitted, w0 = {waist:.2f} px, p = {p:.2f}, FWHM = {fwhm:.2f}'.format(waist=popt_top[1], p=popt_top[3], fwhm=fwhm_top))
# plt.plot(y_fit_top_test,linestyle='--', label='top hat fitted, w0 = {waist:.2f} px, p = {p:.2f}'.format(waist=popt_top_test[1], p=popt_top_test[3]))
plt.ylabel('intensity')
plt.legend()
plt.show()



## Check the phase profile in the image plane

qim(vfield_i[y0-delta:y0+delta,x0-delta:x0+delta])
qim(vphi[y0-delta:y0+delta,x0-delta:x0+delta])

## Get better resolution
next=5

phi_pad = slm_attr.pad_ext(slm_phase_final, n_repeats = next)
beam_e_pad, vfield_i_pad = slm_attr.predict_array(slm_phase_final,nint=1,next=next)

## get the phase
vfield_e_pad = slm_attr.xe_ve(beam_e_pad,phi_pad)
vphi_pad = np.angle(vfield_e_pad)

##
qim(vfield_i_pad[(next+1)*(y0-delta):(next+1)*(y0+delta),(next+1)*(x0-delta):(next+1)*(x0+delta)])
qim(vphi_pad[(next+1)*(y0-delta):(next+1)*(y0+delta),(next+1)*(x0-delta):(next+1)*(x0+delta)])


# camera subroutines
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



