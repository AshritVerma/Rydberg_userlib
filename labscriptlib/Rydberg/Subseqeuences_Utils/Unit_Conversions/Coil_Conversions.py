#####################################################################
#                                                                   #
# example.py                                                        #
#                                                                   #
# Copyright 2013, Monash University                                 #
#                                                                   #
# This file is part of the labscript suite (see                     #
# http://labscriptsuite.org) and is licensed under the Simplified   #
# BSD License. See the license.txt file in the root of the project  #
# for the full license.                                             #
#                                                                   #
#####################################################################
from labscript_utils.unitconversions.UnitConversionBase import *

class volts_to_gauss(UnitConversion):
    # This must be defined outside of init, and must match the default hardware unit specified within the BLACS tab
    base_unit = 'Vpp'
    
    # You can pass a dictionary at class instantiation with some parameters to use in your unit converstion.
    # You can also place a list of "order of magnitude" prefixes (eg, k, m, M, u, p) you also want available
    # and the UnitConversion class will automatically generate the conversion function based on the functions 
    # you specify for the "derived units". This list should be stored in the 'magnitudes' key of the parameters
    # dictionary
    
    def __init__(self,calibration_parameters=None):            
        self.coil_name = calibration_parameters

        coil_
        
        self.derived_units = ['W']
        
        # Set default parameters if they are not speficied in calibration_parameters
        self.parameters.setdefault('grad',2)      
        self.parameters.setdefault('int',0.05)      
        
        UnitConversion.__init__(self,self.parameters)

    def W_to_base(self,watts):
        #here is the calibration code that may use self.parameters
        vpp = float(watts - self.parameters['int'])/self.parameters['grad']
        return vpp
    def W_from_base(self,vpp):
        #here is the calibration code that may use self.parameters
        watts = self.parameters['grad']*vpp + self.parameters['int']
        return watts
