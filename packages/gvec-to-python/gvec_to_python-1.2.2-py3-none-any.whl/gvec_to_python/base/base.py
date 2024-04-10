# import logging
from gvec_to_python.util.logger import logger
# logger = logging.getLogger(__name__)

import warnings

import numpy as np

from gvec_to_python.base.sbase import sBase
from gvec_to_python.base.fbase import fBase
from gvec_to_python.geometry.domain import GVEC_domain


class SplineFourierBases:
    """Create evaluation routines for gvec's B-spline-Fourier bases at logical coordinates (s, th, ze) in [0, 1] x [0, 2*pi]^2.
    
    Parameters
    ----------
    sgrid : array[float]
        Cell boundaries in s-direction in [0, 1].

    degree : int
        Degree of spline space.
        
    sin_cos : int 
        Type of Fourier basis: 1: use only sine, 2: use only cosine, 3: use both.

    mn : list
        mn-mode numbers, with NFP premultiplied into the n-modes.

    range_sin : array-like
        Index range of sine modes in `mn` list."""

    def __init__(self, sgrid, degree, sin_cos, mn, range_sin):

        self.sbase = sBase(sgrid, degree)
        self.fbase = fBase(sin_cos, range_sin)

        self._degree = degree
        self._sin_cos = sin_cos
        self._mn = mn
        self._range_sin = range_sin

    @property
    def degree(self):
        '''Spline degree of s-basis.'''
        return self._degree

    @property
    def sin_cos(self):
        '''Type of Fourier basis: 1: use only sine, 2: use only cosine, 3: use both.'''
        return self._sin_cos

    @property
    def mn(self):
        '''List of mn-mode numbers, with NFP premultiplied into the n-modes.'''
        return self._mn

    @property
    def range_sin(self):
        '''Index range of sine modes in `mn` list.'''
        return self._range_sin

    def eval_stz(self, s, th, ze, coef, der=None, flat_eval=False):
        """Evaluate a B-spline x Fourier basis, or its first or second derivatives, at `s`, `theta`, `zeta`.

        Parameters
        ----------
        s : float or meshgrid numpy.ndarray
            Logical coordinate in radial direction.

        th : float or meshgrid numpy.ndarray
            Angle theta in Tokamak coordinate along poloidal direction.

        ze : float or meshgrid numpy.ndarray
            Angle zeta in Tokamak coordinate along toroidal direction.

        coef : array_like
            A list of B-spline control points (coefficients) for each (m, n) Fourier mode.

        der : str
            Which derivative to evaluate: None, "s", "th", "ze", "ss", "thth", "zeze", "sth", "sze" or "thze".

        flat_eval : bool
            Whether to do flat (marker) evaluation.

        Returns
        -------
        float or meshgrid numpy.ndarray
            Evaluated coordinate.
        """

        s, th, ze = GVEC_domain.prepare_args(s, th, ze, flat_eval=flat_eval)
        if isinstance(s, np.ndarray):
            vals = np.zeros((s + th + ze).shape)
        else:
            vals = 0.

        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        for idx, (m, n) in enumerate(self.mn):

            if der is None:
                eval_Bspline_at_s    = self.sbase.eval_s(s, coef[idx])
                eval_Fourier_at_mtnz = self.fbase.eval_f(idx, m, th, n, ze)
            elif der == 's':
                eval_Bspline_at_s    = self.sbase.eval_ds(s, coef[idx])
                eval_Fourier_at_mtnz = self.fbase.eval_f(idx, m, th, n, ze)
            elif der == 'th':
                eval_Bspline_at_s    = self.sbase.eval_s(s, coef[idx])
                eval_Fourier_at_mtnz = self.fbase.eval_f_dtheta(idx, m, th, n, ze)
            elif der == 'ze':
                eval_Bspline_at_s    = self.sbase.eval_s(s, coef[idx])
                eval_Fourier_at_mtnz = self.fbase.eval_f_dzeta(idx, m, th, n, ze)
            elif der == 'ss':
                eval_Bspline_at_s    = self.sbase.eval_dds(s, coef[idx])
                eval_Fourier_at_mtnz = self.fbase.eval_f(idx, m, th, n, ze)
            elif der == 'thth':
                eval_Bspline_at_s    = self.sbase.eval_s(s, coef[idx])
                eval_Fourier_at_mtnz = self.fbase.eval_f_ddth(idx, m, th, n, ze)
            elif der == 'zeze':
                eval_Bspline_at_s    = self.sbase.eval_s(s, coef[idx])
                eval_Fourier_at_mtnz = self.fbase.eval_f_ddze(idx, m, th, n, ze)
            elif der == 'sth':
                eval_Bspline_at_s    = self.sbase.eval_ds(s, coef[idx])
                eval_Fourier_at_mtnz = self.fbase.eval_f_dtheta(idx, m, th, n, ze)
            elif der == 'sze':
                eval_Bspline_at_s    = self.sbase.eval_ds(s, coef[idx])
                eval_Fourier_at_mtnz = self.fbase.eval_f_dzeta(idx, m, th, n, ze)
            elif der == 'thze':
                eval_Bspline_at_s    = self.sbase.eval_s(s, coef[idx])
                eval_Fourier_at_mtnz = self.fbase.eval_f_dthdze(idx, m, th, n, ze)
            else:
                raise NotImplementedError('Only up to second-order derivatives are supported.')

            # If (s, th, ze) are sparse meshgrids, they should be able to broadcast automatically into a full grid below:
            vals += eval_Bspline_at_s * eval_Fourier_at_mtnz

        return vals

