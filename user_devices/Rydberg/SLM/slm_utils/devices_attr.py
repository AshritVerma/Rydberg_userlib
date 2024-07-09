'''
Classes for each physical device

Emily Qiu
Oct. 27, 2021
'''
import os
import sys
import numpy as np
import imageio
import torch
import pickle
from zernike import RZern
import cv2
import imutils
from slm_utils import freq_funcs
import matplotlib.pyplot as plt

## Camera properties, returns uint8 images

class BaslerCamera:
    def __init__(self):

        self.model = 'acA2440-75um'

        self.nx = 2464
        self.ny = 2056

        self.px = 3.45e-6

        self.xm, self.ym = np.meshgrid(np.linspace(1, self.nx, self.nx),np.linspace(1,self.ny,self.ny))

class ThorlabsCamera:
    def __init__(self):

        self.model = 'DCC1545M'

        self.nx = 1280
        self.ny = 1024

        self.px = 5.2e-6

        self.xm, self.ym = np.meshgrid(np.linspace(1, self.nx, self.nx),np.linspace(1,self.ny,self.ny))


class AlliedVisionCamera:
    def __init__(self):

        self.model = 'Alvium 1800 U-2050m'

        self.nx = 5496
        self.ny = 3672

        self.px = 2.4e-6

        self.Lx = 13.2e-3
        self.Ly = 8.8e-3

        self.adc = 10

        self.xm, self.ym = np.meshgrid(np.linspace(1, self.nx, self.nx),np.linspace(1,self.ny,self.ny))

## SLM properties

class SLMx13138:
    def __init__(self, half=False):

        # model no.
        self.model = 'X13138-02'

        # display settings
        self.sxga_nx = 1280
        self.sxga_ny=1024

        # pixel pitch
        self.px = 12.5e-6

        # fill factor
        self.ff = .96

        # number of pixels
        self.nx = 1272
        self.ny = 1024

        # physical size of SLM
        self.Lx = self.nx*self.px
        self.Ly = self.ny*self.px

        # by default: use square region of SLM only, short axis of 1024 pixels
        # note that we need to adjust the desired trap spacing calcs if using full SLM
        self.n = self.ny
        self.t_n = torch.tensor(self.n)

        # position of optical axis/zero order
        self.ax = int(self.n/2)

        # first order line spacing, position of the first order using tile_blazed() functions compared to blazed_pixel()
        self.line_sp = 11
        self.flip_lr = False
        self.flip_ud = True

        # position of the first order using blazed_pixel()
        self.xt = self.n/self.line_sp
        self.yt = -self.n/self.line_sp

        # shape of the "side" portions for square SLM (set zeros)
        self.side = int((self.nx-self.n)/2)

        # SLM meshgrid
        self.xm, self.ym = np.meshgrid(np.linspace(1,self.n,self.n),np.linspace(1,self.n,self.n))

        # normalized - for zernike polynomials
        self.xmn, self.ymn = np.meshgrid(np.linspace(-1,1,self.n),np.linspace(-1,1,self.n))

        # Tests for using L/R side of SLM to generate even/odd traps
        # Boolean variable, still work in progress
        self.half = half

        # Wavelength dependent
        self.lambda0 = 808.e-9
        self.calfile = 'CAL_LSH0802598_810nm.bmp'

        # Diffraction eff, can pre-compensate by interpolating the distance/spatial frequency
        self.lp_mm = [5, 10, 20, 40, 60]
        self.de = [67.5e-2, 55e-2, 35e-2, 10e-2, 0.05]
        
        # calibrated transfer function from desired intensity to modulation depth
        # (april 3, 2023)
        self.k_fit =  1.02901057e-02
        self.x0_fit = 1.37057357e+02
        
        # Useful patterns
        self.unif = np.zeros(shape=(self.n,self.n))
        self.rand = 2*np.pi*np.random.rand(self.n,self.n)

        self.on_axis_trap = self.blazed_pixel(xt=self.xt,yt=self.yt)[:self.n,:self.n]

        # trap indices
        self.trap_xy = None

        ##### optics side
        # beam size at the SLM
        self.w0 = 7.5e-3/2 #6.23e-3 # 3.74e-3/2*250/75
        
        # intensity distribution at the SLM
        self.slm_intensity = freq_funcs.gauss2d_int(x=self.xm, y=self.ym, wx=self.w0/self.px, wy=self.w0/self.px, x0=self.n/2, y0=self.n/2)

        # expected beam_waist
        self.beam_waist = 1.83e-6
        self.wt = self.n/(np.pi*self.w0/self.px)

        # Zernike up to order n = 6
        self.cart = RZern(6)
        self.cart.make_cart_grid(self.xmn, self.ymn, unit_circle=True)
        
        # cart.nk is the total number of polynomials up to (including) order n. Each n has m=n+1 polynomials
        self.cart_nk = self.cart.nk

        # binary unit circle mask
        uniform_coeff = np.zeros(self.cart_nk)
        uniform_coeff[0] = 1
        self.unit_circ_mask = np.array(self.cart.eval_grid(uniform_coeff, matrix=True))
        self.unit_circ_mask = np.nan_to_num(self.unit_circ_mask, nan=0)

        ########### the following depends on long axis dimensions, not used anymore
        # # expected trap size in number of pixels in the FT array
        # self.wx = self.nx/(np.pi*self.w0/self.px)
        # self.wy = self.ny/(np.pi*self.w0/self.px)
        
        # # pixel resolution in Fourier space
        # self.pkx = np.pi/self.Lx
        # self.pky = np.pi/self.Ly

        # these are for labscript
        self.curr_phase_pattern = self.unif
        self.reset_dynamic_vars()

    ## array methods
    def calc_separation_px(self, desired_separation):
        """
        desired_separation (float)      between traps [m]

        with current beam radius = 7.5mm/2 at the slm, trap waist = 1.83um
        trap waist in pixels is 1.09 
        for ~10um spacing, target trap separation in pixels is 10um/1.83um*1.09 = 5.95 pixels
        """
        return desired_separation/self.beam_waist*self.wt

    def get_array_indices(self, nx_traps, ny_traps, sp_x, sp_y, offset_zo=True, xt=None, yt=None, arraytype=None):
        """
        Given number of traps along X and Y, calculate the equally-spaced
        trap indices given in number of pixels.

        Parameters:
        nx_traps (int):     desired number of traps along X
        ny_traps (int):     desired number of traps along Y
        sp_x,sp_y (int):    desired spacing between traps along X/Y, >=1

        Optional params:
        offset_zo (bool):   whether to shift/offset the array with respect to the zero order
        
        *** need to implement these **
        xt (float):         amount to offset the center of array along X, in [-self.n/2, self.n/2]
        yt (float):         amount to offset the center of array along Y, in [-self.n/2, self.n/2]

        Set new attributes:
        nx_traps:           number of traps along x axis
        ny_traps:           number of traps along y axis
        trap_xy:            array of size ny_traps*nx_traps, containing coordinates
                            of trap indices in tuple form (y,x) given in number of pixels

        (retired)
        bw (float):         equally space traps over some bw fraction of
                            trapping plane, in (0,1). if specified, ignore sp
        """
        if xt is None:
            xt = self.xt
        if yt is None:
            yt = self.yt
            
        # store number of traps
        self.nx_traps = nx_traps
        self.ny_traps = ny_traps

        n_traps = nx_traps*ny_traps
        
        # set inter-trap spacing
        self.trap_spacing_x = sp_x
        self.trap_spacing_y = sp_y

        # store all the trap indices
        self.trap_xy = np.zeros(shape=(ny_traps,nx_traps,2), dtype=int)

        # size of region for fitting purposes (WGSfeedback)
        self.nboxx = int(self.trap_spacing_x/2)
        self.nboxy = int(self.trap_spacing_y/2)

        # set index of array center
        if offset_zo:
            self.center_x = int(self.n/2 + xt)
            self.center_y = int(self.n/2 + yt)

        # otherwise, center on optical axis
        else:
            self.center_x = int(self.n/2)
            self.center_y = int(self.n/2)

        # begin from one of the furthest traps from the optical axis
        self.txmin = int(self.center_x - (nx_traps-1)*self.trap_spacing_x/2)
        self.tymin = int(self.center_y - (ny_traps-1)*self.trap_spacing_y/2)

        # calculate trap locations and store them into self.trap_xy
        for iy,ix in np.ndindex(self.trap_xy.shape[:2]):

            if arraytype == 'triangle':
                offs = round(self.trap_spacing_x/2)

                if iy % 2 == 0:
                    xid = self.txmin + offs + ix*self.trap_spacing_x

                else:
                    xid = self.txmin + ix*self.trap_spacing_x
                yid = self.tymin + iy*self.trap_spacing_y

            elif arraytype == 'hexagon':
                offs = round(self.trap_spacing_x/2)

                if iy % 2 == 0:
                    if ix % 2 == 0:
                        xid = self.txmin + offs + ix*self.trap_spacing_x*1.5

                    else:
                        xid = self.txmin + ix*self.trap_spacing_x*1.5
                else:
                    if ix % 2 == 0:
                        xid = self.txmin + ix*self.trap_spacing_x*1.5

                    else:
                        xid = self.txmin + offs + ix*self.trap_spacing_x*1.5
                        
                yid = self.tymin + iy*self.trap_spacing_y

            else:
                xid = self.txmin + ix*self.trap_spacing_x
                yid = self.tymin + iy*self.trap_spacing_y

            self.trap_xy[iy,ix] = (yid, xid)

        # get the target intensity distribution
        self.get_target_int()

        return
    
    def set_array_indices(self, target_array, lattice_spacing, offset_zo=True, xt=None, yt=None):
        
        if xt is None:
            xt = self.xt
        if yt is None:
            yt = self.yt

        trap_indices = np.argwhere(target_array)

        # calculate how much to shift the indices
        offs_x = np.median(trap_indices[:,1])
        offs_y = np.median(trap_indices[:,0])

        n_traps = np.sum(target_array)
        
        # store number of traps
        self.nx_traps = 1
        self.ny_traps = n_traps

        self.trap_xy = np.zeros(shape=(1,self.nx_traps,2), dtype=int)

        # set inter-trap spacing - minimum only
        self.trap_spacing_x = lattice_spacing
        self.trap_spacing_y = lattice_spacing

        # store all the trap indices
        self.trap_xy = np.zeros(shape=(self.ny_traps,self.nx_traps,2), dtype=int)

        # size of region for fitting purposes (WGSfeedback)
        self.nboxx = int(self.trap_spacing_x/2)
        self.nboxy = int(self.trap_spacing_y/2)

        # set index of array center
        if offset_zo:
            self.center_x = int(self.n/2 + xt)
            self.center_y = int(self.n/2 + yt)

        # otherwise, center on optical axis
        else:
            self.center_x = int(self.n/2)
            self.center_y = int(self.n/2)

        # begin from one of the furthest traps from the optical axis
        self.txmin = int(self.center_x - offs_x)
        self.tymin = int(self.center_y - offs_y)

        # calculate trap locations and store them into self.trap_xy
        for iy,ix in np.ndindex(self.trap_xy.shape[:2]):

            xid = self.txmin + trap_indices[iy, 1]
            yid = self.tymin + trap_indices[iy, 0]

            self.trap_xy[iy,ix] = (yid, xid)

        # get the target intensity distribution
        self.get_target_int()

        return

    def get_target_int(self,mode='single_pixel'):
        """
        Get the desired 2D intensity profile consisting of single pixels of
        non-zero intensity at the desired trap coordinates.

        Calculate the expected diffaction efficiencies for each trap, do simple
        linear interpolation based on frequency in lp/mm (equivalently,
        the distance of the trap in the image plane from zero order)

        Parameters:
        self.trap_xy        the desired trap coordinates

        Set new attributes:
        vtarget0_i (float)  2D matrix of desired intensity profile
        diff_eff (float)    expected diffraction efficiency for each trap
        """

        if self.trap_xy is None:
            raise RuntimeError('Need to get trap indices before calculating the target intensity profile. Quit.')

        # Target intensity profile
        self.vtarget0_i = np.zeros(shape=(self.n,self.n))
        # self.vtarget0_i_g = np.zeros(shape=(self.n,self.n))

        # Pre-compensate for the angle-dependent diffraction efficiency
        self.diff_eff = np.ones(shape=(np.shape(self.trap_xy)[:2]))

        # For each trap, add some light to the target trap location
        for iy,ix in np.ndindex(self.trap_xy.shape[:2]):

            # get the trap coordinate
            (yid, xid) = self.trap_xy[iy,ix]
            
            # Precompensate the diffraction efficiency
            # calculate the distance from the optical axis
            dist = np.sqrt((yid-self.ax)**2+((xid-self.ax)*(self.n/self.n))**2)
            # dist = np.sqrt((yid-self.axy)**2+((xid-self.axx)*(self.ny/self.nx))**2)

            # diffraction effiiency for SLM is quoted up to 40 lp/mm
            if dist > self.ny/2:
                raise ValueError('Target distance from origin is too large to interpolate diffraction efficiency. Quit.')
            
            lp_dy_scale = self.ny/np.max(self.lp_mm)/2
            
            self.diff_eff[iy,ix] = np.interp(
                dist,
                xp = np.multiply(self.lp_mm, lp_dy_scale),
                fp = self.de
            )

            # set trap indensity equal to one
            self.vtarget0_i[yid, xid] = 1
            # self.vtarget0_i[self.trap_xy[iy,ix]] = 1/diff_eff[iy,ix]

            # # MRAF algorithm
            # self.vtarget0_i_g += freq_funcs.gauss2d_int(x=self.xm, y=self.ym, wx=wx, wy=wy, x0=xid, y0=yid)

        self.vtarget0_i = freq_funcs.normalize2d(self.vtarget0_i)
        self.vtarget0_e = np.sqrt(self.vtarget0_i)

        # self.vtarget0_i_g = freq_funcs.normalize2d(vtarget0_i_g)
        # self.vtarget0_e_g = np.sqrt(vtarget0_i_g)
        return


    def shift_array_indices(self, shiftx, shifty):
        """
        Shift indices of array by some integer number of pixels in X,Y

        Parameters:
        shiftx (int):           number of pixels to shift traps in X
        shifty (int):           number of pixels to shift traps in Y

        Returns:
        shifted_trap_xy (int)   new array of tuples (y,x) of trap indices in no. pixels
        """

        # new trap indices
        shifted_trap_xy = self.trap_xy.copy()

        for iy,ix in np.ndindex(self.trap_xy.shape[:2]):

           # get the current trap coordinate
            (yid, xid) = self.trap_xy[iy,ix]

            shifted_trap_xy[iy,ix] = (yid+shifty, xid+shiftx)

        return shifted_trap_xy

    ## Blazed grating functions

    def lpmm_linesp(self, lpmm):
        """
        Convert between lp_per_mm and line_spacing. 
        """
        linesp = 80/lpmm
        return linesp

    def tile_blazed_xy(self, line_sp, check_int_linesp=True):
        """
        Calculate 2D blazed grating for some integer line spacing (defined along one axis), given in numbers of pixels.
        By tiling the base pattern, we obtain an effective line spacing of sqrt(2)*line_sp for diagonal deflection
        Choose a minimum line spacing/period of 2 pixels

        Parameters:
        line_sp (float):    line spacing of the blazed grating along one axis

        Returns:
        (float)             phase pattern for blazed grating, no wrapping
        """
        if check_int_linesp and (line_sp % 1 != 0):
            raise ValueError('Line spacing is not an integer. Quit')

        line_sp = int(line_sp)

        # base pattern to be tiled
        base_pattern_1d = np.arange(0,2*np.pi, 2*np.pi/line_sp)
        base_pattern_2d = []

        for item_num in range(line_sp):

            # shift the base pattern by one element, then append to the 2d base pattern
            base_pattern_2d.append(np.roll(base_pattern_1d,-item_num))

        reps = int(np.ceil(self.n/line_sp))

        # tile the pattern to fill the whole SLM
        phase = np.tile(base_pattern_2d, reps=(reps, reps))

        # get the +1 or -1 order
        if self.flip_ud:
            phase = np.flipud(phase)
        if self.flip_lr:
            phase = np.flipud(phase)

        return phase[:self.n,:self.n]

    def tile_blazed_xy_int(self, line_sp, maxval, check_int_linesp=True):

        if check_int_linesp and (line_sp % 1 != 0):
            raise ValueError('Line spacing is not an integer. Quit')

        line_sp = int(line_sp)

        # base pattern to be tiled
        base_pattern_1d = np.linspace(0, maxval, line_sp)
        base_pattern_2d = []

        for item_num in range(line_sp):

            # shift the base pattern by one element, then append to the 2d base pattern
            base_pattern_2d.append(np.roll(base_pattern_1d,-item_num))
        
        reps = int(np.ceil(self.n/line_sp))

        # tile the pattern to fill the whole SLM
        phase = np.tile(base_pattern_2d, reps=(reps, reps))

        # get the +1 or -1 order
        if self.flip_ud:
            phase = np.flipud(phase)
        if self.flip_lr:
            phase = np.flipud(phase)

        return phase[:self.n,:self.n]

    def tile_blazed_x(self, line_sp, check_int_linesp=True):
        """
        Calculate 1D blazed grating for some integer line spacing along X, given in numbers of pixels.
        Choose a minimum line spacing/period of 2 pixels

        Parameters:
        line_sp (float):    line spacing of the blazed grating along one axis

        Returns:
        (float)             phase pattern for blazed grating, no wrapping
        """
        if check_int_linesp and (line_sp % 1 != 0):
            raise ValueError('Line spacing is not an integer. Quit')

        line_sp = int(line_sp)

        # base pattern to be tiled
        base_pattern_1d = np.arange(0,2*np.pi, 2*np.pi/line_sp)
        base_pattern_2d = []

        for item_num in range(line_sp):
            base_pattern_2d.append(base_pattern_1d)

        reps = int(np.ceil(self.n/line_sp))

        # tile the pattern to fill the whole SLM
        phase = np.tile(base_pattern_2d, reps=(reps, reps))

        return phase[:self.n,:self.n]

    def tile_blazed_y(self, line_sp, check_int_linesp=True):
        """
        Calculate 1D blazed grating for some integer line spacing along Y, given in numbers of pixels.
        Choose a minimum line spacing/period of 2 pixels

        Parameters:
        line_sp (float):    line spacing of the blazed grating along one axis

        Returns:
        (float)             phase pattern for blazed grating, no wrapping
        """
        return self.tile_blazed_x(line_sp=line_sp, check_int_linesp=check_int_linesp).T

    def blazed_period(self, xperiod, yperiod):
        """
        Calculate blazed grating for some line spacing/period, given in numbers of pixels.
        Choose a minimum line spacing/period of 2 pixels

        Parameters:
        xperiod (float):    line spacing of the blazed grating along X
        yperiod(float):     line spacing of the blazed grating along Y

        Returns:
        (float)             phase pattern for blazed grating, no wrapping
        """
        return 2*np.pi*(self.xm/xperiod + self.ym/yperiod)

    def blazed_pixel(self, xt, yt):
        """
        Calculate blazed grating for some target trap position in Fourier plane,
        given in numbers of pixels with respect to the zero order position.
        Choose a trap position within +/-self.n/2, +/-self.n/2

        Parameters:
        xt (int):           Target trap position along X
        yt (int):           Target trap position along Y

        Returns:
        (float)              phase pattern for blazed grating, no wrapping
        """
        return 2*np.pi*(self.xm*xt/self.n + self.ym*yt/self.n)

    def focus(self, foc):
        """
        Calculate the Fresnel pattern to focus the beam after the SLM

        Parameters:
        foc (float):        desired focal length along optical axis, in [m]
        """
        coeff = np.pi*(self.px**2)/(self.lambda0*foc)
        return coeff*(np.power(self.xm-self.n/2,2)+np.power(self.ym-self.n/2,2))

    def defocus(self, z0, foc):
        """
        Calculate the phase pattern to defocus the image plane by distance z0
        with respect to the focal length foc

        Parameters:
        z0 (float):         desired defocus distance, in [m]
        foc (float):        focal length, in [m]
        """
        coeff = np.pi*z0*(self.px**2)/(self.lambda0*foc**2)
        return coeff*(np.power(self.xm-self.n/2,2)+np.power(self.ym-self.n/2,2))

    ## FFT functions
    def fft2d(self, u):
        """
        Returns 2D FFT of input u
        """
        return (1/np.sqrt(self.n**2))*np.fft.fftshift(np.fft.fft2(np.fft.fftshift(u)))

    def t_fft2d(self, u):
        """ pytorch version of above function"""
        return (1/torch.sqrt(self.t_n**2))*torch.fft.fftshift(torch.fft.fft2(torch.fft.fftshift(u)))

    def ifft2d(self, u):
        """
        Returns 2D IFFT of input u
        """
        return np.sqrt(self.n**2)*np.fft.ifftshift(np.fft.ifft2(np.fft.ifftshift(u)))

    def e_i(self, u):
        """
        Parameters:
        u (float):          complex amplitude in position/Fourier space

        Returns:
        (float)             intensity in position/Fourier space
        """
        return np.power(np.absolute(u), 2)

    def t_e_i(self, u):
        """ pytorch version of above function"""
        return torch.pow(torch.abs(u), 2)

    def xe_ve(self, xu, xphi):
        """
        Parameters:
        xu (float):         complex amplitude in position space
        xphi (float):       phase in position space

        Returns:
        (float)             complex amplitude in Fourier space
        """
        return self.fft2d(np.multiply(xu, np.exp(1j*xphi)))
    
    def t_xe_ve(self, xu, xphi):
        """ pytorch version of above function"""
        return self.t_fft2d(torch.multiply(xu, torch.exp(1j*xphi)))

    def xe_vi(self, xu, xphi):
        """
        Parameters:
        xu (float):         complex amplitude in position space
        xphi (float):       phase in position space

        Returns:
        (float)             intensity in Fourier space
        """
        return self.e_i(self.xe_ve(xu=xu, xphi=xphi))

    def ve_xe(self, vu, vphi):
        """
        Parameters:
        vu (float):         complex amplitude in Fourier space
        vphi (float):       phase in Fourier space

        Returns:
        (float)             complex amplitude in position space
        """
        return self.ifft2d(np.multiply(vu, np.exp(1j*vphi)))

    def pad_half_xe_vi(self, xu, xphi):
        """
        *** Still testing: for using one beam on each of L/R side of SLM to generate
        even/odd traps. Pad remaining array with zeros to obtain full size plane

        Parameters:
        xu (float):         complex amplitude in position space
        xphi (float):       phase in position spaces

        Returns:
        (float)             intensity of padded array in Fourier space
        """
        if not self.half:
            raise RuntimeError('Defined full SLM. Do not pad other half')

        amp = np.pad(xu,((0,0),(0,self.nx)))
        phase = np.pad(xphi,((0,0),(0,self.nx)))

        return self.xe_vi(xu=amp,xphi=phase)

    ## Upload to SLM
    def pad_square_pattern(self, phi):
        """
        For square phase patterns (i.e. for arrays), pad the phase pattern with zeros to fill the SLM dimension
        The argument phi should be of size (self.ny x self.ny), since that's the smaller dimension of the SLM.

        Parameters:
        phi (float):        square phase pattern to display on SLM, in rad

        Returns:
        (float)             rectangular phase pattern whose size matches the number of pixels on SLM
        """
        # check the size of the input pattern
        if np.shape(phi) != (self.ny, self.ny):
            raise ValueError('Input phase pattern does not have correct size. Quit.')

        # appending zeros dimensions
        full_pattern = np.zeros(shape=(self.ny,self.nx))
        full_pattern[:,self.side:self.nx-self.side] = phi.copy()

        return full_pattern
        
    def convert_rad_int8(self, phi_rad):
        """
        Convert phase pattern into uint8 format.
        To be used when doing wavefront measurements, since we add uint8 formats and then mod.

        Parameters:
        phi_rad (float):        phase pattern to display on SLM, in rad

        Returns:
        (uint8)             un-scaled bitmap to be displayed on SLM
        """
        return np.array(phi_rad*256./(2*np.pi))

    def convert_int8_rad(self, phi_uint8):
        """
        Convert uint8 phase pattern into 2*pi format.
        To be used when doing wavefront measurements, since we add uint8 formats and then mod.

        Parameters:
        phi_uint8 (float):        phase pattern to display on SLM, in uint8

        Returns:
        (uint8)             phase in rad to be displayed on SLM
        """
        return np.array(phi_uint8*(2*np.pi)/256.)

    def pad_zeros(self, phi):
        # simply add zeros to RHS
        phi_t = np.zeros((self.sxga_ny,self.sxga_nx))
        h,w = np.shape(phi)
        phi_t[:h,:w] = np.array(phi)
        return phi_t

    def intensity_to_moddepth(self, target_intensity):
        """
        Reference intensity is self.slm_intensity, which is the max intensity distribution that we can achieve.
        Normalize things so that the peak intensity is 1.
        Given the desired distribution target_intensity < self.slm_intensity, calculate what is the required modulation depth.

        Things are written such that that we are NOT outputting in modulation depth units, but this will later get rescaled in the convert_bmp function
        """
        intensity_mask = np.divide(target_intensity,self.slm_intensity)
        # print(np.sum(intensity_mask > 1))

        # get the feasible ranges
        # this fails when you have input beam smaller than target beam! we want to clip it, not normalize it
        # intensity_mask_norm = intensity_mask/np.max(intensity_mask)
        intensity_mask_clipped = np.clip(intensity_mask, 0.01, 0.99)

        # function to convert from intensity to modulation depth
        mod_depth = self.x0_fit + (1/self.k_fit)*np.arctanh(2*intensity_mask_clipped-1)
        mod_depth_clipped = np.clip(mod_depth, 0, 255)
        
        return mod_depth_clipped

    def convert_bmp(self, phi_rad, bit_depth = 255., calfile=None):
        """
        Convert phase pattern into BMP format for display on SLM.
        For best performance of correction pattern, I believe that phi_rad should
        not be wrapped yet (hard to tell a difference, still need to check with atoms***)
        
        Note that the output of np.angle returns range (-pi, pi]
        Double check that the phase pattern has the same size as the SLM
        uint8 modulation bit depth for: 
        
        790nm = 209
        800nm = 211
        810nm = 214

        Parameters:
        phi_rad (float):    phase pattern to display on SLM, in rad
        bit_depth (float):  SLM int8 bit depth for 2*pi, mask so that you can control each pixel individually
        calfile (str):      name of the wavefront correction file to be added
                            default is 810nm correction pattern stored in self.calfile
        Returns:
        (uint8)             pattern to be displayed on SLM
        """
        # check the size of the input pattern
        if np.shape(phi_rad) == (self.ny,self.ny):
            phi_rad = self.pad_square_pattern(phi_rad)
        
        if np.shape(phi_rad) == (self.ny,self.nx):
            # scaled phase pattern to uint8 format
            phi_t = np.zeros((self.sxga_ny,self.sxga_nx))
            phi_t[:self.ny,:self.nx] = np.array(phi_rad*256./(2*np.pi))
        
        elif np.shape(phi_rad) == (self.sxga_ny,self.sxga_nx):
            phi_t = np.array(phi_rad*256./(2*np.pi))

        else:
            raise ValueError('Input phase pattern does not match SLM dimensions. Quit.')


        # add calfile
        if calfile is not None:

            wf_corr = imageio.imread(calfile)

            # check if the calfile is  in uint8 format
            if wf_corr.dtype != 'uint8':
                raise ValueError('Calibration file is NOT in uint8 format. Do not add the file.')
            
            phi_t[:self.ny,:self.nx] += wf_corr[:self.ny,:self.nx]

        # wrap and scale to desired bit depth
        phi_t_wrap = np.mod(phi_t, 256.)
        phi_t_scaled = np.multiply(phi_t_wrap, bit_depth)/255.

        return phi_t_scaled.astype(np.uint8)

    ## Padding: increase size/number of samples in SLM plane
    
    def pad_int(self, x, n_repeats):
        """
        Increase number of samples per pixel, roughly simulates higher orders.
        Maintains physical size of SLM.
        Extends physical size of simulated trapping plane by factor n_repeats.

        Params:
        x(float):           phase pattern to be padded, 2D matrix of entries
        n_repeats(int):     number of samples per pixel, to be repeated

        Returns:
        (float)             padded phase pattern, larger by n_repeats*n_repeats
        """
        return np.repeat(np.repeat(x,n_repeats,axis=0), n_repeats, axis=1)

    def pad_ext(self, x, n_repeats):
        """
        Pad SLM externally with zeros to improve resolution in Fourier plane.
        Maintains physical size of simulated trapping plane.
        Extends physical size of SLM plane by factor n_repeats.

        Params:
        x(float):           phase pattern to be padded, 2D matrix of entries
        n_repeats(int):     for each pixel, pad with additional n_repeats zeros
                            note the padding is symmetric about the SLM grid

        Returns:
        (float)             padded phase pattern, larger by n_repeats*n_repeats
        """

        # get size of desired output pattern
        sz = np.shape(x)
        targ_sz = tuple((n_repeats+1)*i for i in sz)

        xnew = np.zeros(shape=targ_sz)

        # calculate positions where the pattern will be placed
        y1 = int(sz[0]*n_repeats/2)
        yn = int(sz[0]*(n_repeats+2)/2)

        x1 = int(sz[1]*n_repeats/2)
        xn = int(sz[1]*(n_repeats+2)/2)

        # set pattern within extended array
        xnew[y1:yn,x1:xn] = x

        return xnew

    def predict_array(self, phi, nint, next, w0 = None, chop=True):
        """
        Using the functions pad_int and pad_ext, improve the resolution of the
        simulated array in the fourier plane.

        Params:
        phi (float):        phase pattern to be padded, 2D matrix of entries
        nint (int):         number of samples per pixel, to be repeated
        next (int):         for each pixel, pad with n_repeats zeros
                            note the padding is symmetric about the SLM grid
        w0 (float):         desired beam size
        chop (bool):        whether or not to include effect of truncating at the SLM

        Returns:
        (float)             intensity in Fourier plane, larger by
                            a factor nint*next*nit*next
        """

        # Regular size
        ny,nx = np.shape(phi)

        phi_in = self.pad_int(phi, n_repeats = nint)
        phi_in_ext = self.pad_ext(phi_in, n_repeats = next)

        # Shape of new array
        nyt,nxt = np.shape(phi_in_ext)
        xmesh_p, ymesh_p = np.meshgrid(np.linspace(1,nxt,nxt), np.linspace(1,nyt,nyt))

        # default incident beam field is the one defined in class attributes
        if w0 == None:
            w0 = self.w0
        
        # Need to scale effective beam size by nint
        beam_i_p = freq_funcs.normalize2d(freq_funcs.gauss2d_int(x=xmesh_p, y=ymesh_p, wx=nint*w0/self.px, wy=nint*w0/self.px, x0=nxt/2, y0=nyt/2))
        beam_e_p = np.sqrt(beam_i_p)


        if chop:
            beam_e = np.zeros(shape=(nyt,nxt))
            beam_e[int(nyt/2-ny/2):int(nyt/2+ny/2),int(nxt/2-nx/2):int(nxt/2+nx/2)] = beam_e_p[int(nyt/2-ny/2):int(nyt/2+ny/2),int(nxt/2-nx/2):int(nxt/2+nx/2)]


        # Expected array in intensity
        return beam_e, self.xe_vi(xu=beam_e, xphi=phi_in_ext)

    # # # # # # # # # # # # # # # # # # Command dictionary functions for SLM server
    def one_trap(self, **kwargs):
        """
        Generate one trap.
        
        optional:
        shiftx, shifty, defocus (float):    num. pixels to shift the average trap position (unit of defocus is such that we take focal length to be 1m). set zero if not defined
        """
        
        # optional args
        shiftx = 0 if 'shiftx' not in kwargs else kwargs['shiftx']
        shifty = 0 if 'shifty' not in kwargs else kwargs['shifty']
        defocus = 0 if 'defocus' not in kwargs else kwargs['defocus']

        # average position
        center_x = self.xt + shiftx
        center_y = self.yt + shifty

        # add focal shift
        foc = 1 # assume 1m
        shift_z = self.defocus(z0=defocus, foc=foc)

        phase_rad = self.blazed_pixel(xt=center_x,yt=center_y) + shift_z

        return phase_rad
    
    # def one_trap(self, **kwargs):
    #     """
    #     Generate one trap.
        
    #     optional:
    #     shiftx, shifty (float):     num. pixels to shift the average trap position. set zero if not defined
    #     """
        
    #     # optional args
    #     shiftx = 0 if 'shiftx' not in kwargs else kwargs['shiftx']
    #     shifty = 0 if 'shifty' not in kwargs else kwargs['shifty']

    #     # average position
    #     center_x = self.xt + shiftx
    #     center_y = self.yt + shifty

    #     # optional args
    #     line_sp = self.line_sp # if not kwargs['line_sp'] else kwargs['line_sp']
    #     # generate first order
    #     phase_rad = self.tile_blazed_xy(line_sp=line_sp)

    #     return phase_rad

    # def two_traps(self, **kwargs):
    #     """
    #     Generate two traps.
        
    #     Parameters:
    #     target_sep (float):         in meters at the atom plane
    #     alpha(float):               rotation angle in radians to rotate the axis of separation between traps. 
    #                                 alpha = 0 gives separation along X, alpha = pi/2 gives separation along Y

    #     optional:
    #     shiftx, shifty, defocus (float):    num. pixels to shift the average trap position (unit of defocus is such that we take focal length to be 1m). set zero if not defined
    #     """

    #     # check required arguments
    #     try:
    #         target_sep = kwargs['target_sep']
    #         alpha = kwargs['alpha']

    #     except:
    #         print("At least one of (target_sep or alpha) are missing.")

    #     # optional args
    #     shiftx = 0 if 'shiftx' not in kwargs else kwargs['shiftx']
    #     shifty = 0 if 'shifty' not in kwargs else kwargs['shifty']
    #     defocus = 0 if 'defocus' not in kwargs else kwargs['defocus']

    #     # mapping of trap separation goes as follows: beam_waist/target_sep = wx/sepx = wy/sepy
    #     # # (if using different nx and ny, for 10 micron separation, this corresponds to 3.7 pixels in x, 3 pixels in y)
    #     # # sepx = self.wx*target_sep/self.beam_waist
    #     # # sepy = self.wy*target_sep/self.beam_waist

    #     # in units of pixels
    #     sep = self.wt*target_sep/self.beam_waist

    #     # separation along X and Y
    #     sep_x = np.cos(alpha)*sep
    #     sep_y = np.sin(alpha)*sep

    #     # average position
    #     center_x = self.xt + shiftx
    #     center_y = self.yt + shifty

    #     # phase pattern corresponding to each target trap position
    #     phi1 = self.blazed_pixel(xt=center_x + sep_x/2 ,yt=center_y + sep_y/2)
    #     phi2 = self.blazed_pixel(xt=center_x - sep_x/2 ,yt=center_y - sep_y/2)
        
    #     # add focal shift
    #     foc = 1 # assume 1m
    #     shift_z = self.defocus(z0=defocus, foc=foc)
        
    #     # get the total pattern - may be some small differences in power between the two traps with this method
    #     phase_rad = np.angle(np.exp(1j*phi1)+np.exp(1j*phi2)) + shift_z
        
    #     return phase_rad
    
    def two_traps(self, **kwargs):
        """
        Generate two traps.
        
        Parameters:
        target_sep (float):         in meters at the atom plane
        alpha(float):               rotation angle in radians to rotate the axis of separation between traps. 
                                    alpha = 0 gives separation along X, alpha = pi/2 gives separation along Y

        optional:
        shiftx, shifty, defocus (float):    num. pixels to shift the average trap position (unit of defocus is such that we take focal length to be 1m). set zero if not defined
        """

        # check required arguments
        try:
            target_sep = kwargs['target_sep']
            alpha = kwargs['alpha']

        except:
            print("At least one of (target_sep or alpha) are missing.")

        # optional args
        shiftx = 0 if 'shiftx' not in kwargs else kwargs['shiftx']
        shifty = 0 if 'shifty' not in kwargs else kwargs['shifty']
        defocus = 0 if 'defocus' not in kwargs else kwargs['defocus']

        # mapping of trap separation goes as follows: beam_waist/target_sep = wx/sepx = wy/sepy
        # # (if using different nx and ny, for 10 micron separation, this corresponds to 3.7 pixels in x, 3 pixels in y)
        # # sepx = self.wx*target_sep/self.beam_waist
        # # sepy = self.wy*target_sep/self.beam_waist

        # in units of pixels
        sep = self.wt*target_sep/self.beam_waist

        # separation along X and Y
        sep_x = sep
        sep_y = 0

        # average position
        center_x = self.xt + shiftx
        center_y = self.yt + shifty

        # phase pattern corresponding to each target trap position
        phi1 = self.blazed_pixel(xt=center_x + sep_x/2 ,yt=center_y + sep_y/2)
        phi2 = self.blazed_pixel(xt=center_x - sep_x/2 ,yt=center_y - sep_y/2)
        
        # add focal shift
        foc = 1 # assume 1m
        shift_z = self.defocus(z0=defocus, foc=foc)
        
        # get the total pattern - may be some small differences in power between the two traps with this method
        phase_rad = np.angle(np.exp(1j*phi1)+np.exp(1j*phi2)) + shift_z
        
        # rotate the net pattern about the optical axis
        rotated = imutils.rotate(phase_rad, angle=alpha*180./np.pi)

        # # affine transformations do something weird
        # M = cv2.getRotationMatrix2D((self.n, self.n), alpha*180./np.pi, 1.0)
        # rotated = cv2.warpAffine(phase_rad, M, (self.n, self.n))
        return rotated
        
    def array_traps(self, **kwargs):
        """
        Generate array of traps.
        
        Parameters:
        phase_pattern_file (float):         string of the phase pattern file, assumed to be located in 'Z:\Calculations\Emily\SLM project\v4_array_patterns'
        shiftx, shifty, defocus (float):    num. pixels to shift the average trap position (unit of defocus is such that we take focal length to be 1m). set zero if not defined
        """

        # check required arguments
        try:
            phase_pattern_file = kwargs['phase_pattern_file']
            phase_pattern_folder = kwargs['phase_pattern_folder']
            shiftx = kwargs['shiftx']
            shifty = kwargs['shifty']
            defocus = kwargs['defocus']
            alpha = kwargs['alpha']

        except:
            print("At least one of the parameters are missing.")

        # optional folder
        base_folder = r'Z:\VV Rydberg lab\Calculations\Emily\SLM project\v4_array_patterns/'
        if phase_pattern_folder != '':
            base_folder = os.path.join(base_folder, phase_pattern_folder, "")
            print('entering subfolder: ' + base_folder)
            
        # read the array phase pattern. if file is string, read from the path, else assume it's the 2d array of phases
        if type(phase_pattern_file) == str:
            filename = os.path.join(base_folder, phase_pattern_file)
            array_rad = freq_funcs.pkread(filename)
        else:
            array_rad = phase_pattern_file.copy()

        # phase pattern corresponding to the shifts in XY and defocus
        shift_xy = self.blazed_pixel(xt=shiftx, yt=shifty)
        foc = 1 # assume 1m
        shift_z = self.defocus(z0=defocus, foc=foc)

        # get the total pattern - may be some small differences in power between the two traps with this method
        phase_rad = array_rad + shift_xy + shift_z

        # rotate the net pattern about the optical axis
        rotated = imutils.rotate(phase_rad, angle=alpha*180./np.pi)

        # # affine transformations do something weird
        # M = cv2.getRotationMatrix2D((self.n, self.n), alpha*180./np.pi, 1.0)
        # rotated = cv2.warpAffine(phase_rad, M, (self.n, self.n))

        return rotated

    def set_zernike(self, **kwargs):
        """
        Evaluate zernike polynomial expansion on a list of coefficients. Following Knoll's indexing (python index = Knoll's index - 1)

        Parameters:
        coeffs (float):     array of coefficients, in units of waves where the range (0,1) is rescaled to (0, 2*pi)

        Returns:
        (float)             evaluated zernike expansion, in radians.
        """
        # check required arguments
        try:
            coeffs = kwargs['coeffs']
        except:
            print("At least one of (coeffs) are missing.")

        if np.sum(np.isnan(np.array(coeffs))) >= 1:
            print("Not adding the zernike coefficients because there are NaN in the coeffs.")
            return

        # pad coeffs array with zeros if coeffs does not include zeros for higher orders
        full_coeffs = np.zeros(self.cart_nk)
        full_coeffs[:len(coeffs)] = np.copy(coeffs)

        # evaluate the coefficients
        zernike = np.array(self.cart.eval_grid(full_coeffs, matrix=True))*2*np.pi
        
        # replace nan values outside unit circle with zeros
        zernike = np.nan_to_num(zernike, nan=0)

        # avoiding rounding issues near 2*pi
        # this line is very important!!
        zernike += -np.min(zernike) + 1e-10

        return zernike

    def add_wf_correction(self, **kwargs):
        '''
        Add the wavefront correction that was calibrated interferometrically.
        
        Parameters:
        wf_corr_file (string):      path to the correction pattern to be added

        Returns:
        (float)                     phase correction pattern to be added to the desired phase pattern
        '''
        # check required arguments
        try:
            wf_corr_file = kwargs['wf_corr_file']
        except:
            print("At least one of (wf_corr_file) are missing.")

        return -np.load(wf_corr_file)

    def add_bob_circle(self, **kwargs):
        """
        Get a pi phase shift with radius rad_shift

        Parameters:
        rad_shift (int):    radius of the pi phase shift circle
        dx (int):           position of circle along x
        dy (int):           position of circle along y

        Returns:
        (float)             pi phase shift mask with radius rad_shift
        """
        # check required arguments
        try:
            rad_shift = kwargs['rad_shift']
            dx = kwargs['bob_shiftx']
            dy = kwargs['bob_shifty']
            bob_defocus = kwargs['bob_defocus']
        except:
            print("At least one of (rad_shift, bob_shiftx, bob_shifty, bob_defocus) are missing.")

        # normal bob, center
        phase_shift = np.zeros(shape=(self.sxga_ny,self.sxga_nx))
        cv2.circle(phase_shift, (int(self.nx/2) + dx, int(self.ny/2) + dy), rad_shift, 1, -1)

        # the donut area around center bob
        outer_donut = 1-phase_shift

        # add focal shift
        foc = 1 # assume 1m
        shift_z = self.pad_zeros(self.pad_square_pattern(self.defocus(z0=bob_defocus, foc=foc)))
        
        return phase_shift*np.pi + shift_z*outer_donut
        
        # # Turning off center bob
        # phase_shift = np.ones(shape=(self.sxga_ny,self.sxga_nx))
        # cv2.circle(phase_shift, (int(self.nx/2) + dx, int(self.ny/2) + dy), rad_shift, 0, -1)

        # return phase_shift

    def get_unit_circ_phase(self, phase):
        # try:
        #     phase = kwargs['phase']
        # except:
        #     print("At least one of (phase) are missing.")

        return np.multiply(phase, self.unit_circ_mask)


    # def clip_circle(self, **kwargs):
    #     """
    #     Clip the center of the SLM pattern in circle shape.

    #     Parameters:
    #     px_ring (float):    size of ring outside SLM diffracting region, in pixels.

    #     Returns:
    #     (float)             binary mask of size (self.sxga_ny,self.sxga_nx)
    #     """
        
    #     # check required arguments
    #     try:
    #         px_radius = int(self.ny/2 - kwargs['px_ring'])
    #         dx = kwargs['clip_shiftx']
    #         dy = kwargs['clip_shifty']
    #         print('Using radius: ' + str(px_radius) + ' and shifts (dx, dy) = (%g, %g)' %(dx, dy) + ' ; smooth=' + str(smooth))

    #     except:
    #         print("At least one of (px_ring) are missing.")

    #     # no clipping = 8um, 400 atoms
    #     # 400 pixels = 10um, 650 atoms
    #     # 350 pixels, 12um, 900 atoms
    #     # 300 pixels, 16um, 1000 atoms - using this for May 20th MLOOP
    #     # continued testing on another day
    #     # 250 - seems still more atoms
    #     # 200 - similar
    #     # 150 - lose over half the atoms 
    #     mask = np.zeros(shape=(self.sxga_ny,self.sxga_nx), dtype="uint8")
    #     cv2.circle(mask, (int(self.nx/2+dx), int(self.ny/2+dy)), px_radius, 1, -1)
        
    #     return mask

    def clip_circle_greyscale(self, **kwargs):
        """
        Clip the center of the SLM pattern in circle shape.
        If smooth is true, then assume px_radius is the gaussian beam waist (intensity).
        Noite that this only makes sense in the context of some target modulation depth, otherwise need to re-calculate intensity_to_moddepth b/c simple multiplicative factor doesn't work!
        Assume everything works for full bit depth of 255 (we can come back to this later if for some reason we want to modulate at less than that)

        Parameters:
        px_ring (float):    size of ring outside SLM diffracting region, in pixels.

        Returns:
        (float)             greyscale mask of size (self.n,self.n) describing the modulation depth.
        """
        
        # check required arguments
        try:
            smooth = bool(kwargs['smooth_bool'])
            px_radius = int(self.n/2 - kwargs['px_ring'])
            dx = kwargs['clip_shiftx']
            dy = kwargs['clip_shifty']
            print('Using radius: ' + str(px_radius) + ' and shifts (dx, dy) = (%g, %g)' %(dx, dy) + ' ; smooth=' + str(smooth))

        except:
            print("At least one of (px_ring) are missing.")

        if smooth:
            target_intensity = np.zeros(shape=(self.n,self.n))
            target_intensity += freq_funcs.gauss2d_int(x=self.xm, y=self.ym, wx=px_radius, wy=px_radius, x0=self.n/2, y0=self.n/2)

            # print('Using full modulation depth? ', np.max(target_intensity) == 1)
            print('Effective beam size at SLM: {waist:.2f} mm'.format(waist=px_radius*self.px*1e3))

            mod_depth_mask = self.intensity_to_moddepth(target_intensity)
            return mod_depth_mask
        
        else:
            # fine without the int8
            mask = np.zeros(shape=(self.n,self.n))
            cv2.circle(mask, (int(self.n/2+dx), int(self.n/2+dy)), px_radius, 1, -1)
        
            return mask*255.

    def create_speckle(self, mod_depth, px_offs_x, px_offs_y, period_x, period_y):
        
        speckle = np.zeros(shape=(self.n,self.n)) + np.pi

        num_sine = len(mod_depth)
        for curr in range(num_sine):
            speckle += mod_depth[curr]*np.sin(2*np.pi*((self.xm-px_offs_x[curr])/period_x[curr] + (self.ym-px_offs_y[curr])/period_y[curr]))

        return speckle

    def _return(self, **kwargs):
        ''' this is necessary for slm_server as we have defined things'''
        return

    def reset_dynamic_vars(self):
        self.curr_zernike_pattern = None
        self.corr_pattern_rad = None
        self.curr_bob_phase = None
        self.curr_mask = None

        return