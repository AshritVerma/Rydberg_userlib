
import sys
sys.path.append(r'Z:\2022-data\common_files/')

from imports import *


from slm_utils.devices_attr import SLMx13138
from slm_utils import slmpy_updated as slmpy
from slm_utils import freq_funcs
from slm_utils.freq_funcs import qim

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

## params

slm = SLMx13138()

# bit depth corresponding to the wavelength of the measurement
# 790nm = 209
# 800nm = 211
# 810nm = 214

y_cutoff = 65000*4

alpha_bit_depth = 210 # for 793
alpha_bit_depth = 203 # for 770
alpha_bit_depth = 214 # for 810
# alpha_bit_depth = 255 # This only matters

mode_sz = 64

# (oct 2022)
probe_sz = 2

# (jan 2023)
probe_sz = 3

# used only for fitting
img_bit_depth_factor = 4 # in addition to 8 bits

# # instead of adding phase, just add some value to the uint8 bitmap
# needed to extract the phase offset
int_res = 2
# int_res = 3

# phi_offset = np.arange(0, 214, int_res) # for mdepth = 3*6
phi_offset = np.arange(0, 200, int_res) # for mdepth = 3*6
n_pts = len(phi_offset)

# for square measurement region
npix_x = slm.n
npix_y = slm.n
# npix_x = 1272
# npix_y = 1024

nmode_x = int(np.ceil(slm.n/mode_sz))
nmode_y = int(np.ceil(slm.n/mode_sz))
# nmode_x = int(np.ceil(npix_x/mode_sz))
# nmode_y = int(np.ceil(npix_y/mode_sz))

# # sample interference result
# intensity = int_fringe_plot_fit(mesh=[cam.xm, cam.ym], amp=1, k1=2*np.pi/100, k2=2*np.pi/500, x0=600, y0=500, phi0=0, gamma=np.pi/4, b=1)

## Read tif file and fit the interference function to a small region of the image
#
# os.chdir(r"/Users/emilyqiu/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_14-18_25_modesz=64_probesz=2/")
#
# list_txt = glob.glob('*.bmp')
#
# # use one file to get the estimated fit parameters
# sample_file = "ix,iy=10,11_phi=50.bmp"
#
# img = bmpread(sample_file)    # Image.open() this is substantially faster, but can't script... takes 1 sec to read 4,000 images
#
# # get guess for k2 (envelope), click the bright peak and drag to node along one of the orthogonal axes
# cv2.namedWindow("get_k2", cv2.WINDOW_NORMAL)
# cv2.imshow("get_k2", img)
# x0, y0, w, h = cv2.selectROI("get_k2", img, showCrosshair=True)
# cv2.waitKey(1)
# cv2.destroyAllWindows()
#
# x1 = x0+w
# y1 = y0+h
# period2 = np.linalg.norm(np.subtract([y0,x0],[y1,x1]))
#
# # get guess for the angle, click two points along a fringe
# plt.figure()
# plt.imshow(img)
# plt.get_current_fig_manager().window.showMaximized()
# corners = np.array(plt.ginput(2)).astype(int)
# plt.close()
#
# angle = np.mod(get_angle_vec(corners[0], corners[1]),2*np.pi)
#
# # zoom in on image
# cv2.namedWindow("zoom_in", cv2.WINDOW_NORMAL)
# cv2.imshow("zoom_in", img)
# x0, y0, w, h = cv2.selectROI("zoom_in", img, showCrosshair=True)
# cv2.waitKey(1)
# cv2.destroyAllWindows()
#
# x1 = x0+w
# y1 = y0+h
#
# zoom = img[y0:y1, x0:x1]
#
# img_nx = x1-x0
# img_ny = y1-y0
#
# xm, ym = np.meshgrid(np.arange(img_nx),np.arange(img_ny))
#
# # zoom in, and get guess for k1 (oscillations)
# # click the bright peak and drag to next bright peak along one of the orthogonal axes
# cv2.namedWindow("get_k1", cv2.WINDOW_NORMAL)
# cv2.imshow("get_k1", zoom)
# x0, y0, w, h = cv2.selectROI("get_k1", zoom, showCrosshair=True)
# cv2.waitKey(1)
# cv2.destroyAllWindows()
#
# x1 = x0+w
# y1 = y0+h
#
# period1 = np.linalg.norm(np.subtract([y0,x0],[y1,x1]))
#
# # Get the guess for the fit
# # int_fringe_fit(mesh, amp, k1, k2, x0, y0, phi0, gamma)
# amp0 = np.max(zoom)
# k10 = np.pi/period1
# k20 = np.pi/period2
#
# p0 = [amp0, k10, k20, int(img_nx/2), int(img_ny/2), 0, angle]
#
# # images = np.zeros((nmode_x,nmode_y,n_pts,npix_y,1280))
# fit_params = np.zeros((nmode_x,nmode_y,n_pts, 7))
# fit_params_covar = np.zeros((nmode_x,nmode_y,n_pts,7,7))
#
# ## Fit the images
#
# curr_file = 0
# for file in list_txt:
#
#     # get the list of files and images
#     fileparams = file.strip('.bmp').strip("ix,iy=").split('_phi=')
#
#     modes = fileparams[0].split(",")
#     currmode_x = int(modes[0])
#     currmode_y = int(modes[1])
#
#     phi = float(fileparams[1])
#     curr_pt = int(phi/int_res)
#
#     # np.asarray(PIL.Image.open) takes 11.5sec for 4,000 but imageio.imread() takes substantially longer
#     img = bmpread(file)    # Image.open() this is substantially faster, but can't script... takes 1 sec to read 4,000 images
#     # images[currmode_x,currmode_y,curr_pt,:,:] = img
#
#     params, params_covar = optimize.curve_fit(
#         int_fringe_fit,
#         [xm, ym],
#         zoom.ravel(),
#         p0=p0,
#         bounds=([np.mean(img), np.pi/1e3, np.pi/1e3, img_nx*1/4, img_nx*1/4, 0, 0],[1e3, np.pi/1, np.pi/1, img_nx*3/4, img_nx*3/4, 2*np.pi-0.001, 2*np.pi-0.001]),
#         maxfev=3000
#     )
#     fit_params[currmode_y, currmode_y, curr_pt, :] = params
#     fit_params_covar[currmode_y, currmode_y, curr_pt, :,:] = params_covar
#
#
# intensity = int_fringe_plot_fit([xm, ym], *params)
# int2 = int_fringe_plot_fit([xm, ym], *p0)
#
# qim(intensity)
# # qim(intensity)
# # qim(zoom)

## Read tif file and fit to cross section - too noisy
#
# img = tifread(r"/Users/emilyqiu/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/images/interference_nov_2.tif")
#
#
# # 2. Get box size to do fitting/feedback
# plt.figure()
# plt.imshow(img)
# plt.get_current_fig_manager().window.showMaximized()
# points = np.array(plt.ginput(2)).astype('int')
# plt.close()
#
#
# x0, y0 = points[0][0], points[0][1]
# x1, y1 = points[1][0], points[1][1]
#
# distance = np.linalg.norm(np.subtract([y0,x0],[y1,x1]))
#
# m = (y1-y0)/(x1-x0)
#
# xp = np.arange(0, distance, 0.5)
# yp = m*xp + (y0-x0*m)
#
# zi = scipy.ndimage.map_coordinates(np.transpose(img), np.vstack((xp,yp))) # THIS SEEMS TO WORK CORRECTLY
#
# fig, axes = plt.subplots(nrows=2)
# axes[0].imshow(img,cmap='binary')
# axes[0].plot([x0, x1], [y0, y1], 'ro-')
# axes[0].axis('image')
#
# axes[1].plot(zi)
#
# plt.show()


## Read the data and take a look

# os.chdir(r"/Users/rydbe/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_14-18_25_modesz=64_probesz=2/")
# os.chdir(r"/Users/emilyqiu/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_26-21_18_modesz=64_probesz=2/")
# os.chdir(r"Z:\2022-data\2022-04\20220407-wf_correction\21_04_modesz=64_probesz=2/")
# os.chdir(r"Z:\2022-data\2022-04\20220415-wf_correction\11_47_modesz=64_probesz=2/")
# os.chdir(r"Z:\2022-data\2022-10\20221017-wf_correction\19_14_modesz=64_probesz=2/")
# os.chdir(r"Z:\2023-data\2023-01\20230113-wf_correction\15_49_modesz=64_probesz=3/")
# os.chdir(r"Z:\2023-data\2023-01\20230113-wf_correction\20_20_modesz=64_probesz=3/")
os.chdir(r"Z:\2023-data\2023-01\20230115-wf_correction\15_55_modesz=64_probesz=3/")


# # probe_region is nearly 3gb at the moment... size (16, 20, 107, 100, 100)
# probe_sig = np.load("/Users/emilyqiu/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_02-22_46_modesz=64_probesz=10/probe_sig.npy")
# probe_region = np.load("/Users/emilyqiu/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_02-22_46_modesz=64_probesz=10/probe_region.npy")

probe_sig = np.load(r"probe_sig.npy")
probe_region = np.load(r"probe_region.npy")
ref_mode_index = np.load(r"ref_mode_index.npy")


## Look at how the probe region or smth else changes
#
# # os.chdir("/Users/emilyqiu/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_01-21_32_modesz=64_probesz=100/")
#
# # data = probe_region_cent
# # data = store_curr_phase_disp
# data = probe_region
#
# currmode_y = 0
# currmode_x = 0
#
# plt.ion()
# fig, cax = plt.subplots(1,1,figsize=(14,6))
# # fig_handle = cax.imshow(data[0], cmap='binary')
# fig_handle = cax.imshow(data[currmode_y,currmode_x,0], cmap='binary')
# fig.colorbar(fig_handle,ax=cax, orientation="horizontal")
#
# for curr in range(len(phi_offset)):
#
#     # show the probe region
#     # fig_handle.set_data(data[curr])
#     fig_handle.set_data(probe_region[currmode_y,currmode_x,curr])
#     fig_handle.autoscale()
#
#     fig.canvas.draw()
#     fig.canvas.flush_events()
#
#     plt.pause(0.1)
#     print(phi_offset[curr])
#
# plt.close()

## Change the size of the probing region, this only matters when the full image is saved and we want to change the size (otherwise the saved data in probe_region is only a scalar for each phase offset value (i.e. shape (nx, ny, int_res)

test_probe_sz = 2
test_probe_sig = np.zeros((nmode_y, nmode_x, n_pts))
test_probe_region = np.zeros((nmode_y, nmode_x, n_pts, test_probe_sz, test_probe_sz))

# plt.ion()
# fig, cax = plt.subplots(1,1,figsize=(6,6))
# # fig_handle = cax.imshow(data[0], cmap='binary')
# fig_handle = cax.imshow(test_probe_region[0,0,0], cmap='binary')
# fig.colorbar(fig_handle,ax=cax, orientation="horizontal")

for iy in range(nmode_y):
    for ix in range(nmode_x):
        for curr in range(len(phi_offset)):

            # if ix==nmode_ref_x and iy==nmode_ref_y:
            #     continue

            test_probe_region[iy, ix, curr] =  get_probe_region(img=probe_region[iy,ix,curr], probe_sz=test_probe_sz, x0=int(probe_sz/2), y0=int(probe_sz/2))

            # Read sum of probe region intensities
            test_probe_sig[iy, ix, curr] = np.sum(test_probe_region[iy, ix, curr])

# 			fig_handle.set_data(test_probe_region[iy, ix, curr])
# 			fig_handle.autoscale()
#
# 			fig.canvas.draw()
# 			fig.canvas.flush_events()
#
# 			print(phi_offset[curr])
#
# plt.close()

# ## Plot over region of probe signal
#
#
# # modey_scan = range(8,9)
# # modex_scan = range(8,13)
# modey_scan = range(0,2)
# modex_scan = range(0,2)
#
# no_cols = len(modey_scan)*len(modex_scan)
#
# colors = list(Color("red").range_to(Color("purple"),no_cols))
#
# legend = []
# plt.figure()
#
# curr_col = 0
# for iy in modey_scan:
#     for ix in modex_scan:
#
#         # if ix==nmode_ref_x and iy==nmode_ref_y:
#         #     continue
#
#         plt.plot(phi_offset, test_probe_sig[iy,ix,:], color=colors[curr_col].hex)
#         legend.append('x={x}, y={y}'.format(x=ix,y=iy))
#
#         curr_col += 1
#
# plt.xlabel('Phase offset')
# plt.ylabel('Sum of probe pixel intensity')
# plt.legend(legend)
# plt.show()
#

## Fit to probe signal

# Index of reference mode (at quarter position of SLM)
nmode_center_x = int(npix_x/mode_sz/2)
nmode_center_y = int(npix_y/mode_sz/2)

# Index of reference mode (at quarter position of SLM)
# # mode_sz = 64

nmode_ref_x = 6
nmode_ref_y = 5

# nmode_ref_x = 5
# nmode_ref_y = 5

curr_probe_sig = test_probe_sig
curr_probe_sz = test_probe_sz

def sine_func(x, x0, k, amp, b):
    return amp*np.cos(k*(x-x0)) + b
    # return amp*np.sin(k*x+phi0) + b
    # return amp*np.sin(k*x+phi0) + b

# Optimized wf pattern, RMS error, sine fit parameters
global_phase_mod = np.zeros((nmode_y, nmode_x))
mse = np.zeros((nmode_y, nmode_x))
mse_norm = np.zeros((nmode_y, nmode_x))		# normalize amplitude to 1 and then compute MSE
# rms_err = np.zeros((nmode_y, nmode_x))

sine_fit_params = np.zeros((nmode_y, nmode_x, 4))
sine_fit_params_covar = np.zeros((nmode_y, nmode_x, 4, 4))

# Failed fits - if failed, set equal to one
fit_failed = np.zeros((nmode_y, nmode_x))


plt.ion()
fig  = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111)

line1, = ax.plot(phi_offset[1:], curr_probe_sig[0, 0,1:], 'ro')
line2, = ax.plot(phi_offset[1:], curr_probe_sig[0, 0,1:], 'b--')
ax.set_ylim([np.min(curr_probe_sig),np.max(curr_probe_sig)])


# # for testing
# for currmode_y in range(10, 11):
#     for currmode_x in range(9, 10):

for currmode_y in range(nmode_y):
    for currmode_x in range(nmode_x):

        # Skip modulation of reference mode
        if currmode_y == nmode_ref_y and currmode_x == nmode_ref_x:
            continue

        xdata_full = phi_offset[1:]
        ydata_full = curr_probe_sig[currmode_y,currmode_x,1:].copy()

        # get non-saturated values
        mask = (ydata_full < y_cutoff)
        xdata = xdata_full[mask].copy()
        ydata = ydata_full[mask].copy()

        # # remove effects of peaks and wrapping when frequency is not 1... why is this not the case? does it matter?
        # argmax_guess = np.argmax(np.convolve(ydata, np.ones(5), mode='valid'))

        # # used up until jan 13, 2023)
        # phi0 = -xdata[argmax_guess]*2.*np.pi/alpha_bit_depth + np.pi/2
        # phi0 = np.mod(-xdata[argmax_guess]*2.*np.pi/alpha_bit_depth + np.pi/2, 2*np.pi)
        #
        # # starting (jan 13, 2023)
        # # phi0 = np.mod(-xdata[argmax_guess]*2.*np.pi/alpha_bit_depth, 2*np.pi)
        # phi0 = -xdata[argmax_guess]*2.*np.pi/alpha_bit_depth + 3*np.pi/2
        #
        # # phi0 = np.mod(-xdata[np.argmax(ydata)]*2.*np.pi/alpha_bit_depth + np.pi/2, 2*np.pi)*alpha_bit_depth/2/np.pi

        # starting (jan 16, 2023, switch to cosine. checked all initial guess, looks robust now.)
        # x0 = xdata[argmax_guess]
        x0 = xdata[np.argmax(ydata)]
        b0 = np.mean(ydata)
        amp0 = (np.max(ydata) - np.min(ydata))/2
        # p0 = [phi0, 1/alpha_bit_depth*2*np.pi, amp0, b0]
        #
        # # for some reason it seems like the frequency ~ 1.5-2x
        # p0 = [phi0, 1.5/alpha_bit_depth*2*np.pi, amp0, b0]

        # cosine, jan16 2023
        p0 = [x0, 1.75/alpha_bit_depth*2*np.pi, amp0, b0]

        # try:
        # fit to probe signal, params order [phi0, k, amp, b]:
        params, params_covar = optimize.curve_fit(
            sine_func,
            xdata,
            ydata,
            p0=p0,
            # bounds=([0, 0.5/alpha_bit_depth*2*np.pi, 0, 0],[2*np.pi-0.001, 2.5/alpha_bit_depth*2*np.pi, 1e7,1e6]),
            # # # # # # # # # # #
            # starting (jan 13, 2023)
            # bounds=([-np.pi/2, 0.5/alpha_bit_depth*2*np.pi, 0, 0],[3*np.pi/2-0.001, 2.5/alpha_bit_depth*2*np.pi, 1e7,1e6]),
            # old ones..
            # bounds=([0, 0.5/alpha_bit_depth*2*np.pi, 0, 0],[2*np.pi-0.001, 2./alpha_bit_depth*2*np.pi, 1e7,1e6]),
            # 255*img_bit_depth_factor*(curr_probe_sz**2), 255*img_bit_depth_factor*(curr_probe_sz)**2]),
            # bounds=([0, 0.5/alpha_bit_depth*2*np.pi, 0, 0],[alpha_bit_depth, 1.5/alpha_bit_depth*2*np.pi, 255*(curr_probe_sz)**2, 255*(curr_probe_sz)**2]),
            # starting (jan 16, 2023)
            bounds=([0, 0.5/alpha_bit_depth*2*np.pi, 0, 0],[np.max(phi_offset), 2.5/alpha_bit_depth*2*np.pi, 1e7,1e6]),
            maxfev=100000
            )

        # Save params
        # global_phase_mod[currmode_y,currmode_x] = params[0]
        global_phase_mod[currmode_y,currmode_x] = params[0]*params[1]
        sine_fit_params[currmode_y,currmode_x,:] = params
        sine_fit_params_covar[currmode_y,currmode_x,:,:] = params_covar

        # mean squared error
        diff = ydata-sine_func(xdata, *params)
        mse[currmode_y,currmode_x] = np.linalg.norm(diff)/n_pts

        # normalized error
        mse_norm[currmode_y,currmode_x] = np.linalg.norm(diff/params[2])/n_pts

        # # Compute error
        # rel_err = np.subtract(np.divide(ydata, sine_func(xdata, *params)), 1)
        # sq_rel_err = np.power(rel_err,2)
        # sum_sq_rel_err = np.sum(sq_rel_err)
        # rms_err[currmode_y,currmode_x] = np.sqrt(1/n_pts*sum_sq_rel_err)

        # except RuntimeError:
        # 	fit_failed[currmode_y, currmode_x] = 1
        # 	print('fit_failed')
        #
        # except ValueError:
        # 	fit_failed[currmode_y, currmode_x] = 1
        # 	print('fit_failed')


        # # # # # # # # # # Plotting
        line1.set_ydata(ydata_full)
        # line2.set_ydata(sine_func(xdata_full, *p0))
        line2.set_ydata(sine_func(xdata_full, *params))

        # ax.autoscale()

        fig.canvas.draw()
        fig.canvas.flush_events()

        # time.sleep(0.3)

        print('x={x}, y={y}'.format(x=currmode_x, y=currmode_y))

# ##
# # test
# plt.figure()
# plt.plot(xdata, ydata)
# plt.plot(xdata, sine_func(xdata, *p0))
# plt.show()
#
# # qim(mse_norm)
# qim(global_phase_mod)

## Look at quality of fit

# modey_scan = range(5,7)
# modex_scan = range(5,7)

# modey_scan = range(0,4)
# modex_scan = range(0,4)


modey_scan = range(8,10)
modex_scan = range(8,10)

modey_scan = range(0,2)
modex_scan = range(0,2)

# modey_scan = range(14,16)
# modex_scan = range(14,16)

no_cols = len(modey_scan)*len(modex_scan)

colors = list(Color("red").range_to(Color("purple"),no_cols))

legend = []
plt.figure()

curr_col = 0

for iy in modey_scan:
    for ix in modex_scan:

        plt.plot(phi_offset[1:], curr_probe_sig[iy,ix,1:],'o', color=colors[curr_col].hex)
        curr_col+=1
        legend.append('x={x}, y={y}'.format(x=ix,y=iy))

plt.xlabel('Phase offset')
plt.ylabel('Sum of probe pixel intensity')
# plt.xlim([0,8])
plt.legend(legend)

curr_col = 0

for iy in modey_scan:
    for ix in modex_scan:

        plt.plot(phi_offset, sine_func(phi_offset, *sine_fit_params[iy,ix]), color=colors[curr_col].hex)
        curr_col+=1
# plt.plot(phi_offset, sine_func(phi_offset, 3.46e-20, 4.8e-2, 5.76e4, 8.2e4))

plt.show()


## Unwrap the phase and do the fit

# global_phase_mod = np.load("C:\\Users\\rydbe\\Dropbox (MIT)\\Calculations\\Emily\\SLM project\\tests_daily_log\\2021_10-11_wf_measurement\\2021_11_02-22_46_modesz=64_probesz=10\\unwrapped.npy")
# global_phase_mod = np.load('/Users/emilyqiu/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_02-22_46_modesz=64_probesz=10/unwrapped.npy')
# global_phase_mod = np.load(r"/Users/rydbe/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_14-18_25_modesz=64_probesz=2/")

phase_unwrapped = unwrap_phase(global_phase_mod)

# if in uint8
# phase_unwrapped = unwrap_phase(global_phase_mod*2*np.pi/alpha_bit_depth)
qim(phase_unwrapped)

half_mode_sz = int(mode_sz/2)

coarse_x1d = np.arange(nmode_x)
coarse_y1d = np.arange(1, nmode_y)

coarse_x2d, coarse_y2d = np.meshgrid(coarse_x1d, coarse_y1d, copy=False)

dxy = 1./64
fine_x1d = np.arange(0, nmode_x, dxy)
fine_y1d = np.arange(0, nmode_y, dxy)

# # coarse mesh for fitting
# coarse_x1d = np.linspace(half_mode_sz, nmode_x*mode_sz -half_mode_sz, nmode_x)
# # skipping y=1
# coarse_y1d = np.linspace(half_mode_sz+mode_sz, nmode_y*mode_sz -half_mode_sz, nmode_y-1)
#
# # fine mesh for interpolating
# fine_x1d = np.arange(slm.nx)
# fine_y1d = np.arange(slm.ny)

# the data we're using to do fits
phase_data = phase_unwrapped[1:,:].copy()

def polyfit2d_func(x, y, z, kxmin, kxmax, kymin, kymax, order=None):
    '''
    Two dimensional polynomial fitting by least squares.
    Fits the functional form f(x,y) = z.

    Notes
    -----
    Resultant fit can be plotted with:
    np.polynomial.polynomial.polygrid2d(x, y, soln.reshape((kx+1, ky+1)))

    Parameters
    ----------
    x, y: 2d meshgrid
    z: np.ndarray, 2d
        Surface to fit.
    kx, ky: int, default is 3
        Polynomial order in x and y, respectively.
    order: int or None, default is None
        If None, all coefficients up to maxiumum kx, ky, ie. up to and including x^kx*y^ky, are considered.
        If int, coefficients up to a maximum of kx+ky <= order are considered.

    Returns
    -------
    Return paramters from np.linalg.lstsq.

    soln: np.ndarray
        Array of polynomial coefficients.
    residuals: np.ndarray
    rank: int
    s: np.ndarray

    '''

    # coefficient array, up to x^kx, y^ky
    coeffs = np.ones((kxmax-kxmin+1, kymax-kymin+1))

    # solve array
    a = np.zeros((coeffs.size, x.size))

    # for each coefficient produce array x^i, y^j
    for index, (i, j) in enumerate(np.ndindex(coeffs.shape)):

        # do not include powers greater than order
        if order is not None and i + j > order:
            arr = np.zeros_like(x)
        else:
            arr = coeffs[i, j] * x**(i+kxmin) * y**(j+kymin)
        a[index] = arr.ravel()

    # do leastsq fitting and return leastsq result
    return np.linalg.lstsq(a.T, np.ravel(z), rcond=None)

def getfit_func(x, y, kxmin, kymin, coeffs):

    assert np.shape(x)==np.shape(y)

    summed = np.zeros(shape=np.shape(x))

    for (i, j) in np.ndindex(coeffs.shape):
        summed += coeffs[i, j] * x**(i+kxmin) * y**(j+kymin)
    return summed


kxmin = 0
kxmax = 5

kymin = 0
kymax = 5

# kxmin = 0
# kxmax = 1
#
# kymin = 0
# kymax = 0

soln, r, rank, s = polyfit2d_func(x=coarse_x2d, y=coarse_y2d, z=phase_data, kxmin=kxmin, kxmax=kxmax, kymin=kxmin, kymax=kymax, order=5)

# interpolating function
# interp_func = scipy.interpolate.interp2d(x=coarse_x2d, y=coarse_y2d, z=phase_data, kind='linear')
# znew = interp_func(x=fine_x1d, y=fine_y1d)

coeffs = soln.reshape((kxmax-kxmin+1,kymax-kymin+1))

fitted_phase_data = np.polynomial.polynomial.polygrid2d(x=coarse_x1d, y=coarse_y1d, c=coeffs).T
fitted_phase_data_interp = np.polynomial.polynomial.polygrid2d(x=fine_x1d, y=fine_y1d, c=coeffs).T

qim(fitted_phase_data_interp)
qim(np.mod(fitted_phase_data_interp,2*np.pi))
freq_funcs.npwrite('unwrapped_fitted.npy', fitted_phase_data_interp)

# ## Remove the linear part
#
# coeffs = soln.reshape((kxmax-kxmin+1,kymax-kymin+1))
#
# # write linear coeffs
# linear_coeffs = np.zeros(shape=np.shape(coeffs))
# linear_coeffs[0,0] = coeffs[0,0]
# linear_coeffs[0,1] = coeffs[0,1]
# linear_coeffs[1,0] = coeffs[1,0]
#
# linear_fitted_phase_data_interp = np.polynomial.polynomial.polygrid2d(x=fine_x1d, y=fine_y1d, c=linear_coeffs).T
#
# # # remove linear part from fit
# # linearx = getfit_func(x=coarse_x2d, y=coarse_y2d, kxmin=kxmin, kymin=kymin, coeffs=coeffs)
#
# removed_linearx = np.subtract(fitted_phase_data_interp, linear_fitted_phase_data_interp)
# qim(np.mod(removed_linearx,2*np.pi))
# # qim(linearx)
#
# # npwrite('/Users/emilyqiu/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_02-22_46_modesz=64_probesz=10/unwrapped_fitted.npy', fitted_phase_data_interp)
#
# ## First, fit and remove linear x part
#
# kxmin = 0
# kxmax = 1
#
# kymin = 0
# kymax = 0
#
# soln, r, rank, s = polyfit2d_func(x=coarse_x2d, y=coarse_y2d, z=phase_data, kxmin=kxmin, kxmax=kxmax, kymin=kxmin, kymax=kymax, order=5)
#
# # interpolating function
# # interp_func = scipy.interpolate.interp2d(x=coarse_x2d, y=coarse_y2d, z=phase_data, kind='linear')
# # znew = interp_func(x=fine_x1d, y=fine_y1d)
#
# coeffs = soln.reshape((kxmax-kxmin+1,kymax-kymin+1))
#
# fitted_phase_data = np.polynomial.polynomial.polygrid2d(x=coarse_x1d, y=coarse_y1d, c=coeffs).T
# fitted_phase_data_interp = np.polynomial.polynomial.polygrid2d(x=fine_x1d, y=fine_y1d, c=coeffs).T
#
# # qim(fitted_phase_data)
# # qim(fitted_surf_interp)
#
# # remove linear part from fit
# linearx = getfit_func(x=coarse_x2d, y=coarse_y2d, kxmin=kxmin, kymin=kymin, coeffs=coeffs)
#
# removed_linearx = np.subtract(phase_data, linearx)
# qim(removed_linearx)
# qim(linearx)
#
# npwrite('/Users/emilyqiu/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_02-22_46_modesz=64_probesz=10/unwrapped_fitted.npy', fitted_phase_data_interp)
#
# ##then, remove linear y part
#
# kxmin = 0
# kxmax = 0
#
# kymin = 0
# kymax = 1
#
# soln, r, rank, s = polyfit2d_func(x=coarse_x2d, y=coarse_y2d, z=removed_linearx, kxmin=kxmin, kxmax=kxmax, kymin=kxmin, kymax=kymax)
#
# # interpolating function
# # interp_func = scipy.interpolate.interp2d(x=coarse_x2d, y=coarse_y2d, z=phase_data, kind='linear')
# # znew = interp_func(x=fine_x1d, y=fine_y1d)
#
# coeffs = soln.reshape((kxmax-kxmin+1,kymax-kymin+1))
#
# fitted_phase_data = np.polynomial.polynomial.polygrid2d(x=coarse_x1d, y=coarse_y1d, c=coeffs).T
# fitted_phase_data_interp = np.polynomial.polynomial.polygrid2d(x=fine_x1d, y=fine_y1d, c=coeffs).T
#
# # qim(fitted_phase_data)
# # qim(fitted_surf_interp)
#
# # remove linear part from fit
# lineary = getfit_func(x=coarse_x2d, y=coarse_y2d, kxmin=kxmin, kymin=kymin, coeffs=coeffs)
#
# removed_linear = np.subtract(removed_linearx, lineary)
# qim(removed_linear)
#
# ## Then remove quadratic x^2, (y^0, y^1, y^2)
#
# kxmin = 0
# kxmax = 2
#
# kymin = 0
# kymax = 2
#
# # now fit again
# soln_x2, r, rank, s = polyfit2d_func(x=coarse_x2d, y=coarse_y2d, z=removed_linear, kxmin=kxmin, kxmax=kxmax, kymin=kymin, kymax=kymax)
# # interp_func = scipy.interpolate.interp2d(x=coarse_x2d, y=coarse_y2d, z=zdata, kind='linear')
# # znew = interp_func(x=fine_x1d, y=fine_y1d)
#
# coeffs_x2 = soln_x2.reshape((kxmax-kxmin+1,kymax-kymin+1))
#
# fitted_phase_surf_x2 = np.polynomial.polynomial.polygrid2d(x=coarse_x1d, y=coarse_y1d, c=coeffs_x2).T
# fitted_phase_surf_x2_interp = np.polynomial.polynomial.polygrid2d(x=fine_x1d, y=fine_y1d, c=coeffs_x2).T
#
# # qim(fitted_phase_surf_x2)
#
# # remove from fit
# quadraticx = getfit_func(x=coarse_x2d, y=coarse_y2d, kxmin=kxmin, kymin=kymin, coeffs=coeffs)
# removed_quadraticx = np.subtract(removed_linear, quadraticx)
#
# qim(removed_quadraticx)
#
# ## Then remove quadratic y^2, (x^0, x^1)
#
# kxmin = 0
# kxmax = 1
#
# kymin = 0
# kymax = 2
#
# # now fit again
# soln_2, r, rank, s = polyfit2d_func(x=coarse_x2d, y=coarse_y2d, z=removed_quadraticx, kxmin=kxmin, kxmax=kxmax, kymin=kymin, kymax=kymax)
# # interp_func = scipy.interpolate.interp2d(x=coarse_x2d, y=coarse_y2d, z=zdata, kind='linear')
# # znew = interp_func(x=fine_x1d, y=fine_y1d)
#
# coeffs_2 = soln_2.reshape((kxmax-kxmin+1,kymax-kymin+1))
#
# fitted_phase_surf_2 = np.polynomial.polynomial.polygrid2d(x=coarse_x1d, y=coarse_y1d, c=coeffs_2).T
# fitted_phase_surf_2_interp = np.polynomial.polynomial.polygrid2d(x=fine_x1d, y=fine_y1d, c=coeffs_2).T
#
# # qim(fitted_phase_surf_2)
#
# # remove from fit
# quadraticy = getfit_func(x=coarse_x2d, y=coarse_y2d, kxmin=kxmin, kymin=kymin, coeffs=coeffs)
# removed_quadratic = np.subtract(removed_quadraticx, quadraticy)
#
# qim(removed_quadratic)
#
#
# ## Then remove cubic x^3, (y^0, y^1, y^2, y^3)
#
# kxmin = 0
# kxmax = 3
#
# kymin = 0
# kymax = 3
#
# # now fit again
# soln, r, rank, s = polyfit2d_func(x=coarse_x2d, y=coarse_y2d, z=removed_quadratic, kxmin=kxmin, kxmax=kxmax, kymin=kymin, kymax=kymax)
# # interp_func = scipy.interpolate.interp2d(x=coarse_x2d, y=coarse_y2d, z=zdata, kind='linear')
# # znew = interp_func(x=fine_x1d, y=fine_y1d)
#
# coeffs = soln.reshape((kxmax-kxmin+1,kymax-kymin+1))
#
# fitted_phase_surf = np.polynomial.polynomial.polygrid2d(x=coarse_x1d, y=coarse_y1d, c=coeffs).T
# fitted_phase_surf_interp = np.polynomial.polynomial.polygrid2d(x=fine_x1d, y=fine_y1d, c=coeffs).T
#
# # qim(fitted_phase_surf_2)
#
# # remove from fit
# cubicx = getfit_func(x=coarse_x2d, y=coarse_y2d, kxmin=kxmin, kymin=kymin, coeffs=coeffs)
# removed_cubicx = np.subtract(removed_quadratic, cubicx)
#
# qim(removed_cubicx)
#
# ## Then remove cubic y^3, (x^0, x^1, x^2)
#
# kxmin = 0
# kxmax = 2
#
# kymin = 0
# kymax = 3
#
# # now fit again
# soln_3, r, rank, s = polyfit2d_func(x=coarse_x2d, y=coarse_y2d, z=removed_cubicx, kxmin=kxmin, kxmax=kxmax, kymin=kymin, kymax=kymax)
# # interp_func = scipy.interpolate.interp2d(x=coarse_x2d, y=coarse_y2d, z=zdata, kind='linear')
# # znew = interp_func(x=fine_x1d, y=fine_y1d)
#
# coeffs_3 = soln_3.reshape((kxmax-kxmin+1,kymax-kymin+1))
#
# fitted_phase_surf = np.polynomial.polynomial.polygrid2d(x=coarse_x1d, y=coarse_y1d, c=coeffs).T
# fitted_phase_surf_interp = np.polynomial.polynomial.polygrid2d(x=fine_x1d, y=fine_y1d, c=coeffs).T
#
# # qim(fitted_phase_surf_2)
#
# # remove from fit
# cubic = getfit_func(x=coarse_x2d, y=coarse_y2d, kxmin=kxmin, kymin=kymin, coeffs=coeffs)
# removed_cubic = np.subtract(removed_quadratic, cubic)
#
# qim(removed_cubic)
#
#
# ## Then remove quartic x^4, (y^0, y^1, y^2, y^3, y^4)
#
# kxmin = 0
# kxmax = 4
#
# kymin = 0
# kymax = 4
#
# # now fit again
# soln, r, rank, s = polyfit2d_func(x=coarse_x2d, y=coarse_y2d, z=removed_cubic, kxmin=kxmin, kxmax=kxmax, kymin=kymin, kymax=kymax)
# # interp_func = scipy.interpolate.interp2d(x=coarse_x2d, y=coarse_y2d, z=zdata, kind='linear')
# # znew = interp_func(x=fine_x1d, y=fine_y1d)
#
# coeffs = soln.reshape((kxmax-kxmin+1,kymax-kymin+1))
#
# fitted_phase_surf = np.polynomial.polynomial.polygrid2d(x=coarse_x1d, y=coarse_y1d, c=coeffs).T
# fitted_phase_surf_interp = np.polynomial.polynomial.polygrid2d(x=fine_x1d, y=fine_y1d, c=coeffs).T
#
# # qim(fitted_phase_surf_2)
#
# # remove from fit
# quarticx = getfit_func(x=coarse_x2d, y=coarse_y2d, kxmin=kxmin, kymin=kymin, coeffs=coeffs)
# removed_quarticx = np.subtract(removed_cubic, quarticx)
#
# qim(removed_quarticx)

## Get fit
colors = list(Color("red").range_to(Color("purple"),nmode_x))

plt.figure()
for i in range(1,nmode_x):

    plt.plot(phase_unwrapped[i,:],color=colors[i].hex)
    plt.plot(global_phase_mod[i,:]*2*np.pi/alpha_bit_depth, 'o', color=colors[i].hex)

    # plt.plot(quarticx[:,i],color=colors[i].hex)
    # plt.plot(removed_cubic[:,i], 'o', color=colors[i].hex)
plt.show()

# npwrite('/Users/emilyqiu/Dropbox (MIT)/Calculations/Emily/SLM project/tests_daily_log/2021_10-11_wf_measurement/2021_11_02-22_46_modesz=64_probesz=10/test_wf_corr.npy', fitted_surf_interp.T*alpha_bit_depth./2/np.pi)

## sklearn fitting

#X is the independent variable (bivariate in this case)
X = array([[0.44, 0.68], [0.99, 0.23]])

#vector is the dependent data
vector = [109.85, 155.72]

#predict is an independent variable for which we'd like to predict the value
predict= [0.49, 0.18]

#generate a model of polynomial features
poly = PolynomialFeatures(degree=2)

#transform the x data for proper fitting (for single variable type it returns,[1,x,x**2])
X_ = poly.fit_transform(X)

#transform the prediction to fit the model type
predict_ = poly.fit_transform(predict)

#here we can remove polynomial orders we don't want
#for instance I'm removing the `x` component
X_ = np.delete(X_,(1),axis=1)
predict_ = np.delete(predict_,(1),axis=1)

#generate the regression object
clf = linear_model.LinearRegression()
#preform the actual regression
clf.fit(X_, vector)

print("X_ = ",X_)
print("predict_ = ",predict_)
print("Prediction = ",clf.predict(predict_))

