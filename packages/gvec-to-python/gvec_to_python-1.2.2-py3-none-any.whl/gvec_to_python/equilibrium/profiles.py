import numpy as np
import scipy.sparse as spa
from scipy.sparse.linalg import splu

from gvec_to_python.hylife.utilities_FEEC import bsplines
from gvec_to_python.hylife.utilities_FEEC.spline_space import spline_space_1d
from gvec_to_python.geometry.domain import GVEC_domain


class GVEC_profiles:
    '''Object for equilibrium profiles (not fields).

    Profiles for "phi" (toroidal flux), "chi" (poloidal flux) "iota" and "pressure" can be evaluated either
    as functions of a single coordinate s, or as 0-forms of three coordinates (s, ., .).

    s can be either float or array-like.
    
    Parameters
    ----------
    sgrid : array[float]
        Cell boundaries in s-direction in [0, 1].
        
    degree : int
        Degree for spline interpolation of the profiles (spos_grev = sgrid - 1 + degree).
        
    spos_grev : array[float]
        Greville points in s-direction in [0, 1].
        
    phi_grev, chi_grev, iota_grev, pres_grev : array[float]
        Profile values at spos_grev of "phi" (toroidal flux), "chi" (poloidal flux) "iota" and "pressure".'''

    def __init__(self, sgrid, degree, spos_grev, phi_grev, chi_grev, iota_grev, pres_grev):

        # Create spline space for interpolation
        knots = bsplines.make_knots(sgrid, degree, periodic=False)
        self._spline_space = spline_space_1d(knots, degree, spl_kind=False)

        # Interpolate at Greville points given by GVEC data
        I_mat = bsplines.collocation_matrix(knots, degree, spos_grev, periodic=False) 
        I_LU  = splu(spa.csc_matrix(I_mat))

        self._phi_coef  = I_LU.solve(phi_grev)
        self._chi_coef  = I_LU.solve(chi_grev)
        self._iota_coef = I_LU.solve(iota_grev)
        self._pres_coef = I_LU.solve(pres_grev)

    @property
    def spline_space(self):
        '''Spline space used for interpolation of profiles.'''
        return self._spline_space

    @property
    def phi_coef(self):
        '''Spline coefficients of toroidal flux for basis of spline_space .'''
        return self._phi_coef

    @property
    def chi_coef(self):
        '''Spline coefficients of poloidal flux for basis of spline_space .'''
        return self._chi_coef

    @property
    def iota_coef(self):
        '''Spline coefficients of iota profile for basis of spline_space .'''
        return self._iota_coef

    @property
    def pres_coef(self):
        '''Spline coefficients of pressure profile for basis of spline_space .'''
        return self._pres_coef

    def profile(self, *args, name='phi', der=None, flat_eval=False):
        '''Profile (derivatives) as a function of s in [0, 1]. 
        
        Parameters
        ----------
        *args : float or array-like
            Arguments of the profile function. 
            If one array argument is given, it must be 1d.
            If three arguments are given (s, a1, a2), a meshgrid or flat evaluation is performed.
    
        name : str
            Profile identifier; must be one of "phi" (toroidal flux), "chi" (poloidal flux) "iota", or "pressure".

        der : str
            Which derivative to evaluate: None, "s" or "ss".
            
        flat_eval : bool
            Whether to do flat (marker) evaluation when three array arguments are given. 
                
        Returns
        -------
        A numpy array.'''

        if name == 'phi':
            coef = self.phi_coef
        elif name == 'chi':
            coef = self.chi_coef
        elif name == 'iota':
            coef = self.iota_coef
        elif name == 'pressure':
            coef = self.pres_coef
        else:
            ValueError(f'Profile name must be "phi", "chi", "iota"  or "pressure", is {name}.')

        if der is None:
            _fun = self.spline_space.evaluate_N
        elif der == 's':
            _fun = self.spline_space.evaluate_dN
        elif der == 'ss':
            _fun = self.spline_space.evaluate_ddN
        else:
            raise ValueError('Only up to second order derivatives implemented.')

        if len(args) == 1:
            return _fun(args[0], coef)
        
        elif len(args) == 3:
            if flat_eval:
                assert np.shape(args[0]) == np.shape(args[1]) == np.shape(args[2])
                assert np.ndim(args[0]) == 1 
                vals = _fun(args[0], coef)
            else:
                s, a1, a2 = GVEC_domain.prepare_args(args[0], args[1], args[2], sparse=False)
                if isinstance(s, np.ndarray):
                    vals = _fun(s.flatten(), coef).reshape(s.shape)
                else:
                    vals = _fun(s, coef)
                    
            return vals
        else:
            ValueError(f'Number of independent variables must be 1 or 3, is {len(args)}.')

    
