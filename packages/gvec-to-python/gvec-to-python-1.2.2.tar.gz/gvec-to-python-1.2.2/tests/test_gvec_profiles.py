import pytest

@pytest.mark.parametrize('gvec_file', ["testcases/ellipstell/newBC_E1D6_M6N6/GVEC_ELLIPSTELL_E1D6_M6N6_State_0000_00200000", 
                                       "testcases/ellipstell/newBC_E4D6_M6N6/GVEC_ELLIPSTELL_E4D6_M6N6_State_0001_00200000"])
@pytest.mark.parametrize('name', ['phi', 'chi', 'iota', 'pressure'])
def test_profile(name,gvec_file):
    '''Test whether the return of profile evaluations has the correct type/dimension.'''

    import os
    import numpy as np
    from gvec_to_python.reader.gvec_reader import create_GVEC_json
    from gvec_to_python import GVEC
    import gvec_to_python as _

    # give absolute paths to the files
    pkg_path = _.__path__[0]
    print(pkg_path)
    dat_file_in   = os.path.join( pkg_path, gvec_file+'.dat')
    json_file_out = os.path.join( pkg_path, gvec_file+'.json')
    create_GVEC_json(dat_file_in, json_file_out)

    # main object (one without, the other one with pyccel kernels)
    gvec = GVEC(json_file_out)

    # test single-point float evaluation
    s = .5
    th = np.pi
    ze = np.pi/2

    assert isinstance(gvec.profiles.profile(s, name=name), float)
    assert isinstance(gvec.profiles.profile(s, name=name, der='s'), float)
    assert isinstance(gvec.profiles.profile(s, name=name, der='ss'), float)
    assert gvec.profiles.profile(s, th, ze, name=name) == gvec.profiles.profile(s, name=name)
    assert gvec.profiles.profile(s, th, ze, name=name, der='s') == gvec.profiles.profile(s, name=name, der='s')
    assert gvec.profiles.profile(s, th, ze, name=name, der='ss') == gvec.profiles.profile(s, name=name, der='ss')

    # test single-point array evaluation
    s = np.array([.5])
    th = np.array([np.pi])
    ze = np.array([np.pi/2])

    assert gvec.profiles.profile(s, name=name).shape == (1,)
    assert gvec.profiles.profile(s, name=name, der='s').shape == (1,)
    assert gvec.profiles.profile(s, name=name, der='ss').shape == (1,)
    assert gvec.profiles.profile(s, th, ze, name=name).shape == (1, 1, 1)
    assert gvec.profiles.profile(s, th, ze, name=name, der='s').shape == (1, 1, 1)
    assert gvec.profiles.profile(s, th, ze, name=name, der='ss').shape == (1, 1, 1)
    assert gvec.profiles.profile(s, th, ze, name=name)[0, 0, 0] == gvec.profiles.profile(s, name=name)[0]
    assert gvec.profiles.profile(s, th, ze, name=name, der='s')[0, 0, 0] == gvec.profiles.profile(s, name=name, der='s')[0]
    assert gvec.profiles.profile(s, th, ze, name=name, der='ss')[0, 0, 0] == gvec.profiles.profile(s, name=name, der='ss')[0]

    # test 1d array evaluation
    s = np.linspace(0, 1, 3)
    th = np.linspace(0, 2*np.pi, 4)
    ze = np.linspace(0, 2*np.pi, 5)
    shp3 = (s.size, th.size, ze.size)

    assert gvec.profiles.profile(s, name=name).shape == (s.size,)
    assert gvec.profiles.profile(s, name=name, der='s').shape == (s.size,)
    assert gvec.profiles.profile(s, name=name, der='ss').shape == (s.size,)
    assert gvec.profiles.profile(s, th, ze, name=name).shape == shp3
    assert gvec.profiles.profile(s, th, ze, name=name, der='s').shape == shp3
    assert gvec.profiles.profile(s, th, ze, name=name, der='ss').shape == shp3
    for n in range(s.size):
        assert np.all(gvec.profiles.profile(s, th, ze, name=name)[n] == gvec.profiles.profile(s, name=name)[n])
        assert np.all(gvec.profiles.profile(s, th, ze, name=name, der='s')[n] == gvec.profiles.profile(s, name=name, der='s')[n])
        assert np.all(gvec.profiles.profile(s, th, ze, name=name, der='ss')[n] == gvec.profiles.profile(s, name=name, der='ss')[n])

    # test 3d array evaluation
    s, th, ze = np.meshgrid(s, th, ze, indexing='ij')

    assert gvec.profiles.profile(s, th, ze, name=name).shape == s.shape
    assert gvec.profiles.profile(s, th, ze, name=name, der='s').shape == s.shape
    assert gvec.profiles.profile(s, th, ze, name=name, der='ss').shape == s.shape


if __name__ == '__main__':
    test_profile('phi')
