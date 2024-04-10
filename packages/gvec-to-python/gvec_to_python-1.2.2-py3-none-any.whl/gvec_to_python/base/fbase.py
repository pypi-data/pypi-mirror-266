import numpy as np


class fBase:
    '''Fourier bases in theta- and zeta directions. Evaluates float or (sparse) meshgrid input.

    Parameters
    ----------
        sin_cos : int 
            1: use only sine, 2: use only cosine, 3: use both.

        range_sin : array-like
            Index range of sine modes in `mn` list.'''

    # Most parameters are unused!
    def __init__(self, sin_cos, range_sin):

        self.range_sin = range_sin 
        if range_sin is not None:
            self.range_sin = np.array(range_sin)

        if sin_cos == 1: # Only sine.
            self.evaluator = fBase.eval_sin
            self.evaluator_dtheta = fBase.eval_sin_dtheta
            self.evaluator_dzeta = fBase.eval_sin_dzeta
            self.evaluator_ddth = fBase.eval_sin_ddth
            self.evaluator_ddze = fBase.eval_sin_ddze
            self.evaluator_dthdze = fBase.eval_sin_dthdze
        elif sin_cos == 2: # Only sosine.
            self.evaluator = fBase.eval_cos
            self.evaluator_dtheta = fBase.eval_cos_dtheta
            self.evaluator_dzeta = fBase.eval_cos_dzeta
            self.evaluator_ddth = fBase.eval_cos_ddth
            self.evaluator_ddze = fBase.eval_cos_ddze
            self.evaluator_dthdze = fBase.eval_cos_dthdze
        elif sin_cos == 3: # Both sine and cosine terms.
            self.evaluator = fBase.eval_sin_cos
            self.evaluator_dtheta = fBase.eval_sin_cos_dtheta
            self.evaluator_dzeta = fBase.eval_sin_cos_dzeta
            self.evaluator_ddth = fBase.eval_sin_cos_ddth
            self.evaluator_ddze = fBase.eval_sin_cos_ddze
            self.evaluator_dthdze = fBase.eval_sin_cos_dthdze
        else:
            ValueError(
                f'basis must be either 1, 2 or 3, is {sin_cos}.')

    @staticmethod
    def eval_sin(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return np.sin(m * theta - n * zeta)

    @staticmethod
    def eval_cos(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return np.cos(m * theta - n * zeta)

    @staticmethod
    def eval_sin_cos(idx, m, theta, n, zeta, range_sin):
        # If it is guaranteed to evaluate in sequential order, one may be able to neglect this if-else check.
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        if idx <= range_sin[1] and idx >= range_sin[0]:
            return np.sin(m * theta - n * zeta)
        else:
            return np.cos(m * theta - n * zeta)

    ###################
    # First derivatives
    ###################

    @staticmethod
    def eval_sin_dtheta(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return np.cos(m * theta - n * zeta) * m

    @staticmethod
    def eval_cos_dtheta(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return - np.sin(m * theta - n * zeta) * m

    @staticmethod
    def eval_sin_cos_dtheta(idx, m, theta, n, zeta, range_sin):
        # If it is guaranteed to evaluate in sequential order, one may be able to neglect this if-else check.
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        if idx <= range_sin[1] and idx >= range_sin[0]:
            return np.cos(m * theta - n * zeta) * m
        else:
            return - np.sin(m * theta - n * zeta) * m

    @staticmethod
    def eval_sin_dzeta(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return np.cos(m * theta - n * zeta) * (- n)  # * NFP

    @staticmethod
    def eval_cos_dzeta(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return - np.sin(m * theta - n * zeta) * (- n)  # * NFP

    @staticmethod
    def eval_sin_cos_dzeta(idx, m, theta, n, zeta, range_sin):
        # If it is guaranteed to evaluate in sequential order, one may be able to neglect this if-else check.
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        if idx <= range_sin[1] and idx >= range_sin[0]:
            return np.cos(m * theta - n * zeta) * (- n)  # * NFP
        else:
            return - np.sin(m * theta - n * zeta) * (- n)  # * NFP

    ####################
    # Second derivatives
    ####################

    @staticmethod
    def eval_sin_ddth(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return - np.sin(m * theta - n * zeta) * m**2

    @staticmethod
    def eval_cos_ddth(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return - np.cos(m * theta - n * zeta) * m**2

    @staticmethod
    def eval_sin_cos_ddth(idx, m, theta, n, zeta, range_sin):
        # If it is guaranteed to evaluate in sequential order, one may be able to neglect this if-else check.
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        if idx <= range_sin[1] and idx >= range_sin[0]:
            return - np.sin(m * theta - n * zeta) * m**2
        else:
            return - np.cos(m * theta - n * zeta) * m**2

    @staticmethod
    def eval_sin_ddze(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return  - np.sin(m * theta - n * zeta) * (- n)**2  # * NFP

    @staticmethod
    def eval_cos_ddze(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return - np.cos(m * theta - n * zeta) * (- n)**2  # * NFP

    @staticmethod
    def eval_sin_cos_ddze(idx, m, theta, n, zeta, range_sin):
        # If it is guaranteed to evaluate in sequential order, one may be able to neglect this if-else check.
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        if idx <= range_sin[1] and idx >= range_sin[0]:
            return - np.sin(m * theta - n * zeta) * (- n)**2  # * NFP
        else:
            return - np.cos(m * theta - n * zeta) * (- n)**2  # * NFP

    @staticmethod
    def eval_sin_dthdze(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return - np.sin(m * theta - n * zeta) * m * (- n)

    @staticmethod
    def eval_cos_dthdze(idx, m, theta, n, zeta, range_sin):
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        return - np.cos(m * theta - n * zeta) * m * (- n)

    @staticmethod
    def eval_sin_cos_dthdze(idx, m, theta, n, zeta, range_sin):
        # If it is guaranteed to evaluate in sequential order, one may be able to neglect this if-else check.
        # Nfp is already premultiplied into n-modes. Otherwise n * NFP * zeta.
        if idx <= range_sin[1] and idx >= range_sin[0]:
            return - np.sin(m * theta - n * zeta) * m * (- n)
        else:
            return - np.cos(m * theta - n * zeta) * m * (- n)

    # A better function name may be 'eval_base'.
    def eval_f(self, idx, m, theta, n, zeta):
        """Evaluate a Fourier term given mn-mode numbers and angles `theta` and `zeta`.

        Parameters
        ----------
            idx : int
                Index of the given mode number pair (m, n) in `self.mn`.

            m : int
                Mode number m along poloidal direction.

            theta : float or (sparse) meshgrid numpy.ndarray
                Angle theta in Tokamak coordinate along poloidal direction.

            n : int
                Mode number n along toroidal direction.

            zeta : float or (sparse) meshgrid numpy.ndarray
                Angle zeta in Tokamak coordinate along toroidal direction.

        Returns
        -------
            value : float or meshgrid numpy.ndarray
                Fourier contribution from mode (m, n) evaluated at angles `theta` and `zeta`.
        """
        return self.evaluator(idx, m, theta, n, zeta, self.range_sin)

    def eval_f_dtheta(self, idx, m, theta, n, zeta):
        """Evaluate partial derivative of a Fourier term w.r.t. `theta` given mn-mode numbers and angles `theta` and `zeta`.

        Parameters
        ----------
            idx : int
                Index of the given mode number pair (m, n) in `self.mn`.

            m : int
                Mode number m along poloidal direction.

            theta : float or (sparse) meshgrid numpy.ndarray
                Angle theta in Tokamak coordinate along poloidal direction.

            n : int
                Mode number n along toroidal direction.

            zeta : float or (sparse) meshgrid numpy.ndarray
                Angle zeta in Tokamak coordinate along toroidal direction.

        Returns
        -------
            value : float or meshgrid numpy.ndarray
                Partial derivative w.r.t. `theta` of the Fourier contribution from mode (m, n) evaluated at angles `theta` and `zeta`.
        """
        return self.evaluator_dtheta(idx, m, theta, n, zeta, self.range_sin)

    def eval_f_dzeta(self, idx, m, theta, n, zeta):
        """Evaluate partial derivative of a Fourier term w.r.t. `zeta` given mn-mode numbers and angles `theta` and `zeta`.

        Parameters
        ----------
        idx : int
            Index of the given mode number pair (m, n) in `self.mn`.

        m : int
            Mode number m along poloidal direction.

        theta : float or meshgrid numpy.ndarray
            Angle theta in Tokamak coordinate along poloidal direction.

        n : int
            Mode number n along toroidal direction.

        zeta : float or meshgrid numpy.ndarray
            Angle zeta in Tokamak coordinate along toroidal direction.

        Returns
        -------
        value : float or meshgrid numpy.ndarray
            Partial derivative w.r.t. `zeta` of the Fourier contribution from mode (m, n) evaluated at angles `theta` and `zeta`.
        """
        return self.evaluator_dzeta(idx, m, theta, n, zeta, self.range_sin)

    def eval_f_ddth(self, idx, m, theta, n, zeta):
        """Evaluate second derivative of a Fourier term w.r.t. `theta` given mn-mode numbers and angles `theta` and `zeta`.

        Parameters
        ----------
            idx : int
                Index of the given mode number pair (m, n) in `self.mn`.

            m : int
                Mode number m along poloidal direction.

            theta : float or (sparse) meshgrid numpy.ndarray
                Angle theta in Tokamak coordinate along poloidal direction.

            n : int
                Mode number n along toroidal direction.

            zeta : float or (sparse) meshgrid numpy.ndarray
                Angle zeta in Tokamak coordinate along toroidal direction.

        Returns
        -------
            value : float or meshgrid numpy.ndarray
                Partial derivative w.r.t. `theta` of the Fourier contribution from mode (m, n) evaluated at angles `theta` and `zeta`.
        """
        return self.evaluator_ddth(idx, m, theta, n, zeta, self.range_sin)

    def eval_f_ddze(self, idx, m, theta, n, zeta):
        """Evaluate second derivative of a Fourier term w.r.t. `zeta` given mn-mode numbers and angles `theta` and `zeta`.

        Parameters
        ----------
            idx : int
                Index of the given mode number pair (m, n) in `self.mn`.

            m : int
                Mode number m along poloidal direction.

            theta : float or (sparse) meshgrid numpy.ndarray
                Angle theta in Tokamak coordinate along poloidal direction.

            n : int
                Mode number n along toroidal direction.

            zeta : float or (sparse) meshgrid numpy.ndarray
                Angle zeta in Tokamak coordinate along toroidal direction.

        Returns
        -------
            value : float or meshgrid numpy.ndarray
                Partial derivative w.r.t. `theta` of the Fourier contribution from mode (m, n) evaluated at angles `theta` and `zeta`.
        """
        return self.evaluator_ddze(idx, m, theta, n, zeta, self.range_sin)

    def eval_f_dthdze(self, idx, m, theta, n, zeta):
        """Evaluate mixed second derivative of a Fourier term given mn-mode numbers and angles `theta` and `zeta`.

        Parameters
        ----------
            idx : int
                Index of the given mode number pair (m, n) in `self.mn`.

            m : int
                Mode number m along poloidal direction.

            theta : float or (sparse) meshgrid numpy.ndarray
                Angle theta in Tokamak coordinate along poloidal direction.

            n : int
                Mode number n along toroidal direction.

            zeta : float or (sparse) meshgrid numpy.ndarray
                Angle zeta in Tokamak coordinate along toroidal direction.

        Returns
        -------
            value : float or meshgrid numpy.ndarray
                Partial derivative w.r.t. `theta` of the Fourier contribution from mode (m, n) evaluated at angles `theta` and `zeta`.
        """
        return self.evaluator_dthdze(idx, m, theta, n, zeta, self.range_sin)
