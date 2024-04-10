from gvec_to_python.base.base import SplineFourierBases

def make_base(data: dict, axis: str):
    """Recreate B-spline x Fourier basis given parameters and B-spline coefficients.

    Parameters
    ----------
        data : dict
            A `dict` containing GVEC output as given by `GVEC_Reader`.
        axis : str
            One of the "X1", "X2", "LA" axis.

    Returns
    -------
        Base
            A `Base` object which is a combination of B-spline x Fourier basis.
    """

    # Params for s_base.
    sgrid = data["grid"]["sGrid"]       # Element boundaries.
    degree    = data[axis]["s_base"]["deg"] # Spline degree.

    # Params for f_base.
    sin_cos      = data[axis]["f_base"]["sin_cos"]      # Whether the data has only sine, only cosine, or both sine and cosine basis.
    mn           = data[axis]["f_base"]["mn"]           # mn-mode numbers, with NFP premultiplied into the n-modes.
    range_sin    = data[axis]["f_base"]["range_sin"]    # Index range of sine modes in `mn` list.

    base = SplineFourierBases(sgrid, degree, sin_cos, mn, range_sin)

    return base
