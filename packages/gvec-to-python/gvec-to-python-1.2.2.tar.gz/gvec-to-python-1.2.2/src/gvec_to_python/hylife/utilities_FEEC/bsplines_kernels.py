# coding: utf-8
#
# Copyright 2020 Florian Holderied

"""
Basic functions for point-wise B-spline evaluation
"""

# from pyccel.decorators import types

from numpy import empty, zeros

# ==============================================================================


def scaling(t_d: 'float[:]', p_d: int, span_d: int, values: 'float[:]'):
    """
    Scales local B-spline values to M-spline values

    Parameters
    ----------
    knots : array_like
        Knots sequence.

    degree : int
        Polynomial degree of B-splines.

    span : int
        Knot span index.

    Returns
    -------
    x : array_like
        Scaling vector with elements (p + 1)/(t[i + p + 1] - t[i])
    """

    for il in range(p_d + 1):
        i = span_d - il
        values[p_d - il] *= (p_d + 1)/(t_d[i + p_d + 1] - t_d[i])


# ==============================================================================
def find_span(t: 'float[:]', p: int, eta: float):

    # Knot index at left/right boundary
    low = p
    high = 0
    high = len(t) - 1 - p

    # Check if point is exactly on left/right boundary, or outside domain
    if eta <= t[low]:
        returnVal = low
    elif eta >= t[high]:
        returnVal = high - 1
    else:

        # Perform binary search
        span = (low + high)//2

        while eta < t[span] or eta >= t[span + 1]:

            if eta < t[span]:
                high = span
            else:
                low = span
            span = (low + high)//2

        returnVal = span

    return returnVal


# =============================================================================
def basis_funs(t: 'float[:]', p: int, eta: float, span: int, left: 'float[:]', right: 'float[:]', values: 'float[:]'):
    """
    Parameters
    ----------
    t : array_like
        Knots sequence.

    p : int
        Polynomial degree of B-splines.

    eta : double
        Evaluation point.

    span : int
        Knot span index.

    Returns
    -------
    values : numpy.ndarray
        Values of p + 1 non-vanishing B-Splines at location eta.
    """

    left[:] = 0.
    right[:] = 0.

    values[0] = 1.

    for j in range(p):
        left[j] = eta - t[span - j]
        right[j] = t[span + 1 + j] - eta
        saved = 0.
        for r in range(j + 1):
            temp = values[r]/(right[r] + left[j - r])
            values[r] = saved + right[r] * temp
            saved = left[j - r] * temp
        values[j + 1] = saved


# =============================================================================
def basis_funs_all(t: 'float[:]', p: int, eta: float, span: int, left: 'float[:]', right: 'float[:]', values: 'float[:, :]', diff: 'float[:]'):
    """
    Parameters
    ----------
    t : array_like
        Knots sequence.

    p : int
        Polynomial degree of B-splines.

    eta : double
        Evaluation point.

    span : int
        Knot span index.

    Returns
    -------
    values : numpy.ndarray
        Values of (p + 1, p + 1) non-vanishing B-Splines at location eta.

    diff : np.ndarray
        Scaling array (p) for M-splines.
    """

    left[:] = 0.
    right[:] = 0.

    values[:, :] = 0.
    values[0, 0] = 1.

    for j in range(p):
        left[j] = eta - t[span - j]
        right[j] = t[span + 1 + j] - eta
        saved = 0.
        for r in range(j + 1):
            diff[r] = 1. / (right[r] + left[j - r])
            temp = values[j, r] * diff[r]
            values[j + 1, r] = saved + right[r] * temp
            saved = left[j - r] * temp
        values[j + 1, j + 1] = saved

    diff[:] = diff*p


# =============================================================================
def basis_funs_and_der(t: 'float[:]', p: int, eta: float, span: int, left: 'float[:]', right: 'float[:]', values: 'float[:, :]', diff: 'float[:]', der: 'float[:]'):
    """
    Parameters
    ----------
    t : array_like
        Knots sequence.

    p : int
        Polynomial degree of B-splines.

    eta : double
        Evaluation point.

    span : int
        Knot span index.

    left : array_like
        p left values

    right : array_like
        p right values

    values_all : array_like

    Returns
    -------
    values : numpy.ndarray
        Values of (2, p + 1) non-vanishing B-Splines and derivatives at location eta.
    """

    left[:] = 0.
    right[:] = 0.

    values[:, :] = 0.
    values[0, 0] = 1.

    for j in range(p):
        left[j] = eta - t[span - j]
        right[j] = t[span + 1 + j] - eta
        saved = 0.
        for r in range(j + 1):
            diff[r] = 1. / (right[r] + left[j - r])
            temp = values[j, r] * diff[r]
            values[j + 1, r] = saved + right[r] * temp
            saved = left[j - r] * temp
        values[j + 1, j + 1] = saved

    diff[:] = diff*p

    # compute derivatives
    # j = 0
    saved = values[p - 1, 0]*diff[0]
    der[0] = -saved

    # j = 1, ... , p
    for j in range(1, p):
        temp = saved
        saved = values[p - 1, j]*diff[j]
        der[j] = temp - saved

    # j = p
    der[p] = saved


# ==============================================================================
def basis_funs_1st_der(t: 'float[:]', p: int, eta: float, span: int, left: 'float[:]', right: 'float[:]', values: 'float[:]'):
    """
    Parameters
    ----------
    t : array_like
        Knots sequence.

    p : int
        Polynomial degree of B-splines.

    eta : double
        Evaluation point.

    span : int
        Knot span index.

    Returns
    -------
    values : numpy.ndarray
        Derivatives of p + 1 non-vanishing B-Splines at location eta.
    """

    # Compute nonzero basis functions and knot differences for splines up to degree p - 1
    values_b = empty(p + 1, dtype=float)
    basis_funs(t, p - 1, eta, span, left, right, values_b)

    # Compute derivatives at x using formula based on difference of splines of degree p - 1
    # -------
    # j = 0
    saved = p * values_b[0] / (t[span + 1] - t[span + 1 - p])
    values[0] = -saved

    # j = 1, ... , p - 1
    for j in range(1, p):
        temp = saved
        saved = p * values_b[j] / (t[span + j + 1] - t[span + j + 1 - p])
        values[j] = temp - saved

    # j = degree
    values[p] = saved


# ==============================================================================
def basis_funs_all_ders(knots: 'float[:]', degree: int, eta: float, span: int, left: 'float[:]', right: 'float[:]', n: int, ders: 'float[:, :]'):
    """
    Evaluate value and n derivatives at eta of all basis functions with
    support in interval [x_{span-1}, x_{span}].

    ders[i,j] = (d/deta)^i B_k(eta) with k=(span-degree+j),
                for 0 <= i <= n and 0 <= j <= degree+1.

    Parameters
    ----------
    knots : array_like
        Knots sequence.

    degree : int
        Polynomial degree of B-splines.

    eta : float
        Evaluation point.

    span : int
        Knot span index.

    n : int
        Max derivative of interest.

    Results
    -------
    ders : numpy.ndarray (n+1,degree+1)
        2D array of n+1 (from 0-th to n-th) derivatives at eta of all (degree+1)
        non-vanishing basis functions in given span.

    Notes
    -----
    The original Algorithm A2.3 in The NURBS Book [1] is here improved:
        - 'left' and 'right' arrays are 1 element shorter;
        - inverse of knot differences are saved to avoid unnecessary divisions;
        - innermost loops are replaced with vector operations on slices.
    """
    #left = empty(degree)
    #right = empty(degree)
    ndu = empty((degree+1, degree+1))
    a = empty((2, degree+1))
    #ders = zeros((n+1, degree+1))  # output array

    # Number of derivatives that need to be effectively computed
    # Derivatives higher than degree are = 0.
    ne = min(n, degree)

    # Compute nonzero basis functions and knot differences for splines
    # up to degree, which are needed to compute derivatives.
    # Store values in 2D temporary array 'ndu' (square matrix).
    ndu[0, 0] = 1.0
    for j in range(0, degree):
        left[j] = eta - knots[span-j]
        right[j] = knots[span+1+j] - eta
        saved = 0.0
        for r in range(0, j+1):
            # compute inverse of knot differences and save them into lower triangular part of ndu
            ndu[j+1, r] = 1.0 / (right[r] + left[j-r])
            # compute basis functions and save them into upper triangular part of ndu
            temp = ndu[r, j] * ndu[j+1, r]
            ndu[r, j+1] = saved + right[r] * temp
            saved = left[j-r] * temp
        ndu[j+1, j+1] = saved

    # Compute derivatives in 2D output array 'ders'
    ders[0, :] = ndu[:, degree]
    for r in range(0, degree+1):
        s1 = 0
        s2 = 1
        a[0, 0] = 1.0
        for k in range(1, ne+1):
            d = 0.0
            rk = r-k
            pk = degree-k
            if r >= k:
                a[s2, 0] = a[s1, 0] * ndu[pk+1, rk]
                d = a[s2, 0] * ndu[rk, pk]
            j1 = 1 if (rk > -1) else -rk
            j2 = k-1 if (r-1 <= pk) else degree-r
            a[s2, j1:j2+1] = (a[s1, j1:j2+1] - a[s1, j1-1:j2]
                              ) * ndu[pk+1, rk+j1:rk+j2+1]
            for l in range(j2 + 1 - j1):
                d += a[s2, j1 + l] * ndu[rk + j1 + l, pk]
            #d += dot(a[s2, j1:j2+1], ndu[rk+j1:rk+j2+1, pk])
            if r <= pk:
                a[s2, k] = - a[s1, k-1] * ndu[pk+1, r]
                d += a[s2, k] * ndu[r, pk]
            ders[k, r] = d
            j = s1
            s1 = s2
            s2 = j

    # Multiply derivatives by correct factors
    r = degree
    for k in range(1, ne+1):
        ders[k, :] = ders[k, :] * r
        r = r * (degree-k)

