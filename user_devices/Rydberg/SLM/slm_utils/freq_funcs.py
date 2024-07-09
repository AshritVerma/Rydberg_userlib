import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
from PIL import Image
import imageio
import torch
from matplotlib import patches


## read/write

def tifread(fileName):
	return np.asarray(Image.open(fileName))[:,:,0]

def bmpread(fileName):
	return np.asarray(Image.open(fileName))

def makedir(folderName):
	if not os.path.exists(folderName):
		os.mkdir(folderName)
	return

def pkread(fileName):
	return pickle.load(open(fileName, 'rb'))

def pkwrite(fileName, var):

	if not os.path.exists(fileName):
		return pickle.dump(var, open(fileName,'wb'))
	else:
		raise ValueError('File exists already, choose another filename to save.')

def npwrite(fileName, var):

	if not os.path.exists(fileName):
		with open(fileName, 'wb') as f:
			np.save(f, var)
	else:
		raise ValueError('File exists already, choose another filename to save.')

def imgiowrite(fileName, var):
	if not os.path.exists(fileName):
		imageio.imwrite(fileName, var)
	else:
		raise ValueError('File exists already, choose another filename to save.')


## Gaussian functions

def fwhm(sigma, p):
	""" return FWHM based on 1/e^2 waist definition"""

	return 2*(sigma/np.sqrt(2))*(np.log(2))**(1/(2*p))

def gauss2d_int(x, y, wx, wy, x0, y0):
	"""
	Output a 2D Gaussian profile. All inputs must have the same units.

	Parameters:
	x,y (float):			2D meshgrids
	wx,wy (float):		1/e^2 radius of gaussian
	x0,y0 (float):		center position of gaussian

	Return:
	(float)				output gaussian profile as 2D matrix
	"""
	y = np.exp(-(2.*(x - x0)**2. / wx**2. + 2.*(y - y0)**2. / wy**2.))
	return y

def gauss2d_fit(mesh, amp, wx, wy, x0, y0):
	"""
	Fitting function for 2D Gaussian profile

	Parameters:
	mesh (float):		array with 2 elements, with X and Y meshgrids
	amp (float):			amplitude of fit
	wx,wy (float):		1/e^2 radius of gaussian
	x0,y0 (float):		center position of gaussian

	Return:
	(float)				1D array containing ravelled elements of gaussian function
	"""
	assert len(mesh) == 2

	x = mesh[0]
	y = mesh[1]

	g = amp*np.exp(-(2.*(x - x0)**2. / wx**2. + 2.*(y - y0)**2. / wy**2.))
	return g.ravel()

def gauss2d_plot_fit(mesh, amp, wx, wy, x0, y0):
	"""
	Outputs non-ravelled gaussian function as 2D matrix, see gauss2d_fit()
	"""
	assert len(mesh) == 2

	x = mesh[0]
	y = mesh[1]

	return amp*np.exp(-(2.*(x - x0)**2. / wx**2. + 2.*(y - y0)**2. / wy**2.))


def super_gauss2d_fit(mesh, amp, wx, wy, x0, y0, p):
	"""
	Same as above, supergaussian with parameter p = power of exponential
	"""
	assert len(mesh) == 2

	x = mesh[0]
	y = mesh[1]

	g = amp*np.exp(-((2.*(x - x0)**2. / wx**2. + 2.*(y - y0)**2. / wy**2.))**p)
	return g.ravel()

def super_gauss2d_plot_fit(mesh, amp, wx, wy, x0, y0):
	"""
	Same as above, supergaussian with parameter p = power of exponential
	"""
	assert len(mesh) == 2

	x = mesh[0]
	y = mesh[1]

	return amp*np.exp(-((2.*(x - x0)**2. / wx**2. + 2.*(y - y0)**2. / wy**2.))**p)

def super_gauss1d(x, amp, wx, x0, p):
	"""
	1D version
	"""
	g = amp*np.exp(-(2.*(x - x0)**2. / wx**2.)**p)
	return g

## other functions
def int_fringe_fit(mesh, amp, k1, k2, x0, y0, phi0, gamma):
	"""
	Fitting function for wavefront measurements
	"""
	assert len(mesh) == 2

	x = mesh[0]
	y = mesh[1]

	x_p = np.cos(gamma)*(x-x0) + np.sin(gamma)*(y-y0)
	y_p = np.cos(gamma)*(y-y0) - np.sin(gamma)*(x-x0)

	two_pt_int = np.power(np.cos(k1*x_p+phi0), 2)

	slit_x = np.power(np.sinc(k2*x_p/np.pi), 2)
	slit_y = np.power(np.sinc(k2*y_p/np.pi), 2)

	return (amp*two_pt_int*slit_x*slit_y).ravel()

def int_fringe_plot_fit(mesh, amp, k1, k2, x0, y0, phi0, gamma):
	"""
	Fitting function for wavefront measurements
	"""
	assert len(mesh) == 2

	x = mesh[0]
	y = mesh[1]

	x_p = np.cos(gamma)*(x-x0) + np.sin(gamma)*(y-y0)
	y_p = np.cos(gamma)*(y-y0) - np.sin(gamma)*(x-x0)

	two_pt_int = np.power(np.cos(k1*x_p+phi0), 2)

	slit_x = np.power(np.sinc(k2*x_p/np.pi), 2)
	slit_y = np.power(np.sinc(k2*y_p/np.pi), 2)

	return amp*two_pt_int*slit_x*slit_y

## Math helpers

def normalize2d(u):
	return np.divide(u, np.sum(np.abs(u)))

def t_normalize2d(u):
	return torch.divide(u, torch.sum(torch.abs(u)))

def rotation_matrix(theta):
	"""
	Apply rotation to vector in the form [y,x] by angle theta
	"""
	return np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])

def sine_func(x, phi0, k, amp, b):
	return amp*np.sin(x*k + phi0) + b

def get_angle_vec(p1,p2):
	"""
	Given vector p2-p1, calculate the rotation angle

	Parameters:
	p1 (float):			position [x,y] of first point
	p2 (float):			position [x,y] of second point
	"""

	# unit vector of input points
	v = np.subtract(p2,p1)
	vhat = v/np.linalg.norm(v)

	# # reflect about y axis (due to nature of imshow)
	# vhat_refl = np.array([vhat[0],-vhat[1]])

	# get angle
	angle = np.arccos(np.dot(vhat,[0,1]))
	sign = 1 if vhat[1] > 0 else -1

	return sign*angle

def get_angle_imshow(p1,p2):
	"""
	Given two input points at two corners of a square array (top left, bottom
	right), get the effective angle of rotation of the square.

	Assume input coordinates are in the form [x,y] as consistent with ginput()
	Take origin as the top left corner of the square, positive angle is
	anti-clockwise, as consistent with imshow()

	Parameters:
	p1 (float):			position [x,y] of top left corner of aray
	p2 (float):			position [x,y] of bottom right corner of aray
	"""

	# unit vector of input points
	v = np.subtract(p2,p1)
	vhat = v/np.linalg.norm(v)

	# reflect about y axis (due to nature of imshow) then rotate by +pi/4
	vhat_refl = np.array([vhat[0],-vhat[1]])
	vhat_transf = np.dot(1/np.sqrt(2)*np.array([[1,-1],[1,1]]), vhat_refl.reshape(2,1)).reshape(1,2)[0]

	# get angle
	angle = np.arccos(np.dot(vhat_transf,[1,0]))
	sign = 1 if vhat_transf[1] < 0 else -1

	return sign*angle

## Quick commands

def qim(img):
	"""
	Show binay image with one command
	"""
	plt.figure()
	plt.imshow(img, cmap='binary')
	plt.colorbar()
	plt.show()


def torch_to_np(arr):
	return arr.detach().numpy()

def qimh(img):
	"""
	Show colour image with one command
	"""
	plt.figure()
	plt.imshow(img)
	plt.colorbar()
	plt.show()

def qp(y):
	"""
	Show plot with one command
	"""
	plt.figure()
	plt.plot(y)
	plt.show()

