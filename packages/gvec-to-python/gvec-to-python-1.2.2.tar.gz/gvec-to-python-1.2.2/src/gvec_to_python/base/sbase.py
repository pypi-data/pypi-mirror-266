import numpy as np

from gvec_to_python.hylife.utilities_FEEC import bsplines as bsp
from gvec_to_python.hylife.utilities_FEEC.spline_space import spline_space_1d


class sBase:
    '''B-spline basis for s-direction, regularity is degree - 1, interpolatory at boundary.

    Parameters
    ----------
        sgrid : array[float]
            Cell boundaries in s-direction in [0, 1].

        degree : int
            Degree of spline space.'''

    def __init__(self, sgrid, degree):

        self._knots = bsp.make_knots(sgrid, degree, periodic=False)
        self._spline_space = spline_space_1d(self.knots, degree, spl_kind=False)

    @property
    def spline_space(self):
        '''Spline space object.'''
        return self._spline_space

    @property
    def knots(self):
        '''Knot sequence.'''
        return self._knots

    def eval_s(self, s, coef):
        """Evaluate B-spline at point `s` given coefficients `coef`.

        Parameters
        ----------
            s : float or array-like
                Logical coordinate in radial direction. Point(s) of evaluation.

            coef : array-like
                B-spline coefficients. 

        Returns
        -------
            Float or numpy.ndarray of same shape as s.
        """

        if isinstance(s, (list, tuple)):
            s = np.array(s)

        if isinstance(s, np.ndarray):
            vals = self.spline_space.evaluate_N(
                s.flatten(), coef).reshape(s.shape)
        else:
            vals = self.spline_space.evaluate_N(s, coef)

        return vals

    def eval_ds(self, s, coef):
        """Evaluate derivative of B-spline at point `s` given coefficients `coef`.

        Parameters
        ----------
            s : float or array-like
                Logical coordinate in radial direction. Point(s) of evaluation.

            coef : array-like
                B-spline coefficients. 

        Returns
        -------
            Float or numpy.ndarray of same shape as s.
        """

        if isinstance(s, (list, tuple)):
            s = np.array(s)

        if isinstance(s, np.ndarray):
            vals = self.spline_space.evaluate_dN(
                s.flatten(), coef).reshape(s.shape)
        else:
            vals = self.spline_space.evaluate_dN(s, coef)

        return vals

    def eval_dds(self, s, coef):
        """Evaluate second derivative of B-spline at point `s` given coefficients `coef`.

        Parameters
        ----------
            s : float or array-like
                Logical coordinate in radial direction. Point(s) of evaluation.

            coef : array-like
                B-spline coefficients. 

        Returns
        -------
            Float or numpy.ndarray of same shape as s.
        """

        if isinstance(s, (list, tuple)):
            s = np.array(s)

        if isinstance(s, np.ndarray):
            vals = self.spline_space.evaluate_ddN(
                s.flatten(), coef).reshape(s.shape)
        else:
            vals = self.spline_space.evaluate_ddN(s, coef)

        return vals
