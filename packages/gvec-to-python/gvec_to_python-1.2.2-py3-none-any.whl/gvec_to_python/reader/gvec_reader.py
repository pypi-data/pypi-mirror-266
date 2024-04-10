import json
import numpy as np
import pandas as pd
from io import StringIO

from gvec_to_python.util.numpy_encoder import NumpyEncoder


def create_GVEC_json(dat_file_in: str, json_file_out: str) -> dict:
    """Automatically convert .dat GVEC output into .json upon initialization.

    Parameters
    ----------
    dat_file_in : str
        Name of the input .dat GVEC file (with file extension).

    json_file_out : str
        Name of the output .json file (with file extension).

    """

    sections = read_GVEC_file(dat_file_in)
    parsed_data = parse_GVEC_data(sections)

    with open(json_file_out, 'w') as outfile:
        json.dump(parsed_data, outfile, indent=4,
                  sort_keys=False, cls=NumpyEncoder)


def read_GVEC_file(dat_file_in: str) -> list:
    """Parse each section from .dat GVEC output file into a `list`.

    Each element from the `list` output is a `dict` containing metadata, and a `pandas.DataFrame`.
    While Pandas makes the data easier to visualize, if we focus only on speed, we should read into Numpy ndarray directly.

    Parameters
    ----------
        dat_file_in : str
            Name of the input .dat GVEC file (with file extension).

    Returns
    -------
        list
            The GVEC data file separated into 12 sections and each section parsed as `pandas.DataFrame` in a python `dict`.
    """

    with open(dat_file_in, 'r') as f:
        data = f.read()

    sections = []

    for idx, section in enumerate(data.split("\n##")):

        if idx != 0:
            section = '##' + section

        # Hack: Python's has no `switch` statement.
        if idx == 0:
            cols = ["outputLevel", "fileID"]
        elif idx == 1:
            cols = ["nElems", "gridType"]
        elif idx == 2:
            cols = ["sgrid"]
        elif idx == 3:
            cols = ["nfp", "degGP", "mn_nyq(1)", "mn_nyq(2)", "hmap"]
        elif idx == 4:  # X1_base
            cols = ["s_nbase", "s_deg", "s_continuity",
                    "f_modes", "f_sin_cos", "f_excl_mn_zero"]
        elif idx == 5:  # X2_base
            cols = ["s_nbase", "s_deg", "s_continuity",
                    "f_modes", "f_sin_cos", "f_excl_mn_zero"]
        elif idx == 6:  # LA_base
            cols = ["s_nbase", "s_deg", "s_continuity",
                    "f_modes", "f_sin_cos", "f_excl_mn_zero"]
        elif idx == 7:  # X1 mn mode numbers and spline coefficients
            cols = ["m-modenumber", "n-modenumber"]
        elif idx == 8:  # X2 mn mode numbers and spline coefficients
            cols = ["m-modenumber", "n-modenumber"]
        elif idx == 9:  # LA mn mode numbers and spline coefficients
            cols = ["m-modenumber", "n-modenumber"]
        # Profiles: interpolated values at GREVILLE points in s (can be used to initialize a spline of the same basis as X1%s): spos, phi, chi, iota, pressure
        elif idx == 10:
            cols = ["spos", "phi", "chi", "iota", "pressure"]
        elif idx == 11:
            cols = ["a_minor", "r_major", "volume"]
        else:
            cols = None

        # `section.split("\n", 1)` splits each section into only 2 parts using a newline character.
        # The first part is the header, and the second part is the data is CSV format.
        buffer = StringIO(section.split("\n", 1)[1])

        if idx in [2]:  # If parsed data should be transposed.
            df = pd.read_csv(buffer, header=None).T
            df.columns = cols
        # If arbitrary column numbers (e.g. spline coefficients).
        elif idx in [7, 8, 9]:
            df = pd.read_csv(buffer, header=None)
            for coef_num in range(1, len(df.columns) - 1):
                cols.append("coef{:d}".format(coef_num))
            df.columns = cols
        else:  # If parsed data should be interpreted normally.
            df = pd.read_csv(buffer, header=None, names=cols)

        temp = {
            "header": section.split("\n", 1)[0],
            "cols": cols,
            "df": df,
        }
        sections.append(temp)

    return sections


def parse_GVEC_data(sections: list) -> dict:
    """Parse each section from .dat GVEC output into a `dict`.

    Parameters
    ----------
    sections : list
        List of GVEC output sections, parsed as pandas DataFrame embeded in a dict.

    Returns
    -------
    dict
        Parsed GVEC output.
    """

    nElems = sections[1]['df'].iloc[:, 0][0]
    sgrid = sections[2]['df'].iloc[:, :].T.to_numpy().tolist()[0]
    nfp = sections[3]['df'].iloc[:, 0][0]
    hmap = sections[3]['df'].iloc[:, 4][0]

    X1_s_nbase = sections[4]['df'].iloc[:, 0][0]
    X1_s_deg = sections[4]['df'].iloc[:, 1][0]
    X1_s_continuity = sections[4]['df'].iloc[:, 2][0]
    X1_f_modes = sections[4]['df'].iloc[:, 3][0]
    X1_f_sin_cos = sections[4]['df'].iloc[:, 4][0]
    X1_f_excl_mn_zero = sections[4]['df'].iloc[:, 5][0]

    X2_s_nbase = sections[5]['df'].iloc[:, 0][0]
    X2_s_deg = sections[5]['df'].iloc[:, 1][0]
    X2_s_continuity = sections[5]['df'].iloc[:, 2][0]
    X2_f_modes = sections[5]['df'].iloc[:, 3][0]
    X2_f_sin_cos = sections[5]['df'].iloc[:, 4][0]
    X2_f_excl_mn_zero = sections[5]['df'].iloc[:, 5][0]

    LA_s_nbase = sections[6]['df'].iloc[:, 0][0]
    LA_s_deg = sections[6]['df'].iloc[:, 1][0]
    LA_s_continuity = sections[6]['df'].iloc[:, 2][0]
    LA_f_modes = sections[6]['df'].iloc[:, 3][0]
    LA_f_sin_cos = sections[6]['df'].iloc[:, 4][0]
    LA_f_excl_mn_zero = sections[6]['df'].iloc[:, 5][0]

    (X1_f_m, X1_f_n, X1_f_m_max, X1_f_n_max, X1_f_modes_sin, X1_f_modes_cos, X1_f_range_sin, X1_f_range_cos
     ) = calculate_sincos_range(nfp, X1_f_modes, X1_f_sin_cos, X1_f_excl_mn_zero, sections[7]['df'])
    (X2_f_m, X2_f_n, X2_f_m_max, X2_f_n_max, X2_f_modes_sin, X2_f_modes_cos, X2_f_range_sin, X2_f_range_cos
     ) = calculate_sincos_range(nfp, X2_f_modes, X2_f_sin_cos, X2_f_excl_mn_zero, sections[8]['df'])
    (LA_f_m, LA_f_n, LA_f_m_max, LA_f_n_max, LA_f_modes_sin, LA_f_modes_cos, LA_f_range_sin, LA_f_range_cos
     ) = calculate_sincos_range(nfp, LA_f_modes, LA_f_sin_cos, LA_f_excl_mn_zero, sections[9]['df'])

    # X1_f_coef = {}
    # for row in range(len(X1_f_m)):
    #     m = X1_f_m[row]
    #     n = X1_f_n[row]
    #     if m not in X1_f_coef:
    #         X1_f_coef[m] = {}
    #     X1_f_coef[m][n] = sections[7]['df'].iloc[row, 2:].tolist()

    # X2_f_coef = {}
    # for row in range(len(X2_f_m)):
    #     m = X2_f_m[row]
    #     n = X2_f_n[row]
    #     if m not in X2_f_coef:
    #         X2_f_coef[m] = {}
    #     X2_f_coef[m][n] = sections[8]['df'].iloc[row, 2:].tolist()

    # LA_f_coef = {}
    # for row in range(len(LA_f_m)):
    #     m = LA_f_m[row]
    #     n = LA_f_n[row]
    #     if m not in LA_f_coef:
    #         LA_f_coef[m] = {}
    #     LA_f_coef[m][n] = sections[9]['df'].iloc[row, 2:].tolist()

    X1_coef = []
    for row in range(len(X1_f_m)):
        X1_coef.append(sections[7]['df'].iloc[row, 2:].tolist())

    X2_coef = []
    for row in range(len(X2_f_m)):
        X2_coef.append(sections[8]['df'].iloc[row, 2:].tolist())

    LA_coef = []
    for row in range(len(LA_f_m)):
        LA_coef.append(sections[9]['df'].iloc[row, 2:].tolist())


    greville_spos = sections[10]['df'].iloc[:, 0].tolist()
    greville_phi = sections[10]['df'].iloc[:, 1].tolist()
    greville_chi = sections[10]['df'].iloc[:, 2].tolist()
    greville_iota = sections[10]['df'].iloc[:, 3].tolist()
    greville_pres = sections[10]['df'].iloc[:, 4].tolist()

    a_minor = sections[11]['df'].iloc[:, 0][0]
    r_major = sections[11]['df'].iloc[:, 1][0]
    volume = sections[11]['df'].iloc[:, 2][0]

    assert hmap == 1, 'hmap != 1 not implemented in this reader. Only R Z phi.'
    assert X1_s_deg - 1 == X1_s_continuity, 'X1 radial direction is not a spline.'
    assert X2_s_deg - 1 == X2_s_continuity, 'X2 radial direction is not a spline.'
    assert LA_s_deg - 1 == LA_s_continuity, 'LA radial direction is not a spline.'

    data = {

        "general": {
            "nfp": nfp,
            "hmap": hmap,
            # Unused.
            "a_minor": a_minor,
            "r_major": r_major,
            "volume": volume,
        },

        "grid": {
            "nElems": nElems,
            "sGrid": sgrid,
        },

        "X1": {
            "s_base": {
                "nBase": X1_s_nbase,
                "deg": X1_s_deg,
                "continuity": X1_s_continuity,
            },
            "f_base": {
                "modes": X1_f_modes,
                "sin_cos": X1_f_sin_cos,
                "excl_mn_zero": X1_f_excl_mn_zero,
                "mn": np.array([X1_f_m, X1_f_n]).T.tolist(),
                "mn_max": [X1_f_m_max, X1_f_n_max],
                "modes_sin": X1_f_modes_sin,
                "modes_cos": X1_f_modes_cos,
                "range_sin": X1_f_range_sin,
                "range_cos": X1_f_range_cos,
            },
            "coef": X1_coef,
        },

        "X2": {
            "s_base": {
                "nBase": X2_s_nbase,
                "deg": X2_s_deg,
                "continuity": X2_s_continuity,
            },
            "f_base": {
                "modes": X2_f_modes,
                "sin_cos": X2_f_sin_cos,
                "excl_mn_zero": X2_f_excl_mn_zero,
                "mn": np.array([X2_f_m, X2_f_n]).T.tolist(),
                "mn_max": [X2_f_m_max, X2_f_n_max],
                "modes_sin": X2_f_modes_sin,
                "modes_cos": X2_f_modes_cos,
                "range_sin": X2_f_range_sin,
                "range_cos": X2_f_range_cos,
            },
            "coef": X2_coef,
        },

        "LA": {
            "s_base": {
                "nBase": LA_s_nbase,
                "deg": LA_s_deg,
                "continuity": LA_s_continuity,
            },
            "f_base": {
                "modes": LA_f_modes,
                "sin_cos": LA_f_sin_cos,
                "excl_mn_zero": LA_f_excl_mn_zero,
                "mn": np.array([LA_f_m, LA_f_n]).T.tolist(),
                "mn_max": [LA_f_m_max, LA_f_n_max],
                "modes_sin": LA_f_modes_sin,
                "modes_cos": LA_f_modes_cos,
                "range_sin": LA_f_range_sin,
                "range_cos": LA_f_range_cos,
            },
            "coef": LA_coef,
        },

        "profiles": {
            "greville": {
                "nPoints": len(greville_spos),
                "spos": greville_spos,
                "phi": greville_phi,
                "chi": greville_chi,
                "iota": greville_iota,
                "pres": greville_pres,
            },
        },

        # "a_minor"           : a_minor,
        # "r_major"           : r_major,
        # "volume"            : volume,
    }


    return data


def calculate_sincos_range(Nfp, f_modes, f_sin_cos, f_excl_mn_zero, f_df, verbose=False):
    # modes_sin :: m=0: n=1...nMax , m=1...m_max: n=-n_max...n_max. REMARK: for sine, m=0,n=0 is automatically excluded.
    # mode_ cos :: m=0: n=0...nMax , m=1...m_max: n=-n_max...n_max. mn_excl=True will exclude m=n=0.
    # Parameter `f_modes` is used only for double-checking.

    _SIN_ = 1
    _COS_ = 2
    _SINCOS_ = 3

    f_m = f_df.iloc[:, 0].tolist()
    f_n = f_df.iloc[:, 1].tolist()
    # f_coef = f_df.iloc[:, 2:].to_numpy()
    assert f_modes == len(
        f_df), "Inconsistent number of f_modes. ??_base specifies {} modes, but spline coefficients have {} rows.".format(f_modes, len(f_df))

    f_m_max = max(f_m)
    f_n_max = max(f_n) // Nfp
    if verbose:
        print("f_m_max {:d}".format(f_m_max))
        print("f_n_max {:d}".format(f_n_max))

    f_modes_sin = (f_n_max) + f_m_max*(2*f_n_max+1)
    f_modes_cos = (f_n_max+1) - f_excl_mn_zero + f_m_max*(2*f_n_max+1)

    if f_sin_cos == _SIN_:
        # f_modes     = f_modes_sin
        f_range_sin = [0, f_modes_sin]
        f_range_cos = None
        f_modes_cos = 0
    elif f_sin_cos == _COS_:
        # f_modes     = f_modes_cos
        f_range_sin = None
        f_range_cos = [0, f_modes_cos]
        f_modes_sin = 0
    elif f_sin_cos == _SINCOS_:
        # f_modes     = f_modes_sin + f_modes_cos
        f_range_sin = [0, f_modes_sin]
        f_range_cos = [f_modes_sin+1, f_modes]
    else:
        pass  # Throw error.

    if verbose:
        print("f_modes_sin {:d}".format(f_modes_sin))
        print("f_modes_cos {:d}".format(f_modes_cos))
        print("f_range_sin {}  ".format(f_range_sin))
        print("f_range_cos {}  ".format(f_range_cos))

    return f_m, f_n, f_m_max, f_n_max, f_modes_sin, f_modes_cos, f_range_sin, f_range_cos


def read_file_generator(file_path: str):
    """Read a file line by line.

    Parameters
    ----------
    file_path: str
        Name of the file.

    Yields
    ------
    str
        A line from the file that's being read.

    Notes
    -----
    Example usage of `read_file_generator()`:  
    `for i in read_file_generator(file_path):`  
    `    print(i)`
    """

    with open(file_path, 'r') as f:
        while True:
            data = f.readline()
            if not data:
                break
            yield data
