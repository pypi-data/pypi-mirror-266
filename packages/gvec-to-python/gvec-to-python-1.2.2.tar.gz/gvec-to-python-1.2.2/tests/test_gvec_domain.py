import pytest

@pytest.mark.parametrize('use_pyccel,gvec_file', [(False,"testcases/ellipstell/newBC_E1D6_M6N6/GVEC_ELLIPSTELL_E1D6_M6N6_State_0000_00200000"),
                                                  (True ,"testcases/ellipstell/newBC_E4D6_M6N6/GVEC_ELLIPSTELL_E4D6_M6N6_State_0001_00200000")])   
@pytest.mark.parametrize('mapping', ['gvec', 'pest', 'unit', 'unit_pest', 'wo_hmap'])
def test_output_formats(mapping, use_pyccel,gvec_file):
    '''Test whether the return of mapping evaluations has the correct type/dimension.'''

    import os
    import numpy as np
    from gvec_to_python.reader.gvec_reader import create_GVEC_json
    from gvec_to_python import GVEC
    import gvec_to_python as _

    # give absolute paths to the files
    pkg_path = _.__path__[0]
    dat_file_in   = os.path.join( pkg_path, gvec_file+'.dat')
    json_file_out = os.path.join( pkg_path, gvec_file+'.json')
    create_GVEC_json(dat_file_in, json_file_out)

    # main object 
    gvec = GVEC(json_file_out, mapping=mapping, use_pyccel=use_pyccel)
    print('gvec.mapping: ', gvec.mapping)

    # test single-point float evaluation
    s = .5
    if 'unit' not in mapping:
        a1 = np.pi
        a2 = np.pi/2
    else:
        a1 = .5
        a2 = .25

    assert isinstance(gvec.f(s, a1, a2)[0], float)
    assert gvec.df(s, a1, a2).shape == (3, 3)
    assert isinstance(gvec.det_df(s, a1, a2), float)
    assert gvec.df_inv(s, a1, a2).shape == (3, 3)
    assert gvec.g(s, a1, a2).shape == (3, 3)
    assert gvec.g_inv(s, a1, a2).shape == (3, 3)

    # test single-point array evaluation
    s = np.array([s])
    a1 = np.array([a1])
    a2 = np.array([a2])

    assert gvec.f(s, a1, a2)[0].shape == (1, 1, 1)
    assert gvec.df(s, a1, a2).shape == (1, 1, 1, 3, 3)
    assert gvec.det_df(s, a1, a2).shape == (1, 1, 1)
    assert gvec.df_inv(s, a1, a2).shape == (1, 1, 1, 3, 3)
    assert gvec.g(s, a1, a2).shape == (1, 1, 1, 3, 3)
    assert gvec.g_inv(s, a1, a2).shape == (1, 1, 1, 3, 3)

    # test 1d array evaluation (all combinations)
    for n0,n1,n2 in [(3,4,5),(3,4,1),(3,1,5),(1,4,5),(3,1,1),(1,4,1),(1,1,5),(1,1,1)]:
        s = np.linspace(.01, 1, n0) # mappings are singular at s=0
        if 'unit' not in mapping:
            a1 = np.linspace(0, 2*np.pi, n1,endpoint=False)
            a2 = np.linspace(0, 2*np.pi, n2,endpoint=False)
        else:
            a1 = np.linspace(0, 1, n1,endpoint=False)
            a2 = np.linspace(0, 1, n2,endpoint=False)
        
        shp3 = (s.size, a1.size, a2.size)
        shp5 = (s.size, a1.size, a2.size, 3, 3)
        
        assert gvec.f(s, a1, a2)[0].shape == shp3
        assert gvec.df(s, a1, a2).shape == shp5
        assert gvec.det_df(s, a1, a2).shape == shp3
        assert gvec.df_inv(s, a1, a2).shape == shp5
        assert gvec.g(s, a1, a2).shape == shp5
        assert gvec.g_inv(s, a1, a2).shape == shp5

    # test 3d array evaluation
    s, a1, a2 = np.meshgrid(s, a1, a2, indexing='ij')

    assert gvec.f(s, a1, a2)[0].shape == shp3
    assert gvec.df(s, a1, a2).shape == shp5
    assert gvec.det_df(s, a1, a2).shape == shp3
    assert gvec.df_inv(s, a1, a2).shape == shp5
    assert gvec.g(s, a1, a2).shape == shp5
    assert gvec.g_inv(s, a1, a2).shape == shp5
    
    # test flat (marker) evaluation
    Np = 17
    s = np.linspace(.01, 1, Np) # mappings are singular at s=0
    if 'unit' not in mapping:
        a1 = np.linspace(0, 2*np.pi, Np, endpoint=False)
        a2 = np.linspace(0, 2*np.pi, Np, endpoint=False)
    else:
        a1 = np.linspace(0, 1, Np, endpoint=False)
        a2 = np.linspace(0, 1, Np, endpoint=False)
        
    shp3 = s.shape
    shp5 = (s.size, 3, 3)
    
    assert gvec.f(s, a1, a2, flat_eval=True)[0].shape == shp3
    assert gvec.df(s, a1, a2, flat_eval=True).shape == shp5
    assert gvec.det_df(s, a1, a2, flat_eval=True).shape == shp3
    assert gvec.df_inv(s, a1, a2, flat_eval=True).shape == shp5
    assert gvec.g(s, a1, a2, flat_eval=True).shape == shp5
    assert gvec.g_inv(s, a1, a2, flat_eval=True).shape == shp5

 
@pytest.mark.parametrize('use_pyccel,gvec_file', [(True ,"testcases/ellipstell/newBC_E4D6_M6N6/GVEC_ELLIPSTELL_E4D6_M6N6_State_0001_00200000")])   
@pytest.mark.parametrize('unit_tor_domain', ["one-fp","full","1/3"])   
def test_values(use_pyccel,gvec_file,unit_tor_domain):
    '''Compare values of different mappings provided by GVEC_domain.'''

    import os
    import numpy as np
    from gvec_to_python.reader.gvec_reader import create_GVEC_json
    from gvec_to_python import GVEC
    import gvec_to_python as _

    # give absolute paths to the files
    pkg_path = _.__path__[0]
    dat_file_in   = os.path.join( pkg_path, gvec_file+'.dat')
    json_file_out = os.path.join( pkg_path, gvec_file+'.json')
    create_GVEC_json(dat_file_in, json_file_out)

    # main object 
    gvec = GVEC(json_file_out, use_pyccel=use_pyccel,unit_tor_domain=unit_tor_domain)

    # compare f and f_pest
    s0 = np.array([.52,.63])
    th0 = np.random.rand(5)*2*np.pi
    ze0 = np.random.rand(3)*np.pi
    # all combinations of 1D arrays 
    for n0,n1,n2 in [(2,5,3),(2,5,1),(2,1,3),(1,5,3),(2,1,1),(1,5,1),(1,1,3),(1,1,1)]:
        s  = s0[0:n0]
        th = th0[0:n1]
        ze = ze0[0:n2]
        s, th, ze = gvec.domain.prepare_args(s, th, ze,sparse=True)
        th2 = th + gvec._lambda(s, th, ze)
        
        
        # check Pmap
        assert np.allclose(s,  gvec.domain.Pmap(s, th2, ze)[0])
        assert np.allclose(th, gvec.domain.Pmap(s, th2, ze)[1])
        assert np.allclose(ze, gvec.domain.Pmap(s, th2, ze)[2])

        # compare f and f_pest
        assert np.allclose(gvec.domain.f_gvec(s, th, ze)[0], gvec.domain.f_pest(s, th2, ze)[0])
        assert np.allclose(gvec.domain.f_gvec(s, th, ze)[1], gvec.domain.f_pest(s, th2, ze)[1])
        assert np.allclose(gvec.domain.f_gvec(s, th, ze)[2], gvec.domain.f_pest(s, th2, ze)[2])

        # compare f and f_unit
        assert np.allclose(gvec.domain.f_gvec(s, th, ze)[0], gvec.domain.f_unit(s, th/(2*np.pi), ze/(2*np.pi*gvec.domain.tor_fraction))[0])
        assert np.allclose(gvec.domain.f_gvec(s, th, ze)[1], gvec.domain.f_unit(s, th/(2*np.pi), ze/(2*np.pi*gvec.domain.tor_fraction))[1])
        assert np.allclose(gvec.domain.f_gvec(s, th, ze)[2], gvec.domain.f_unit(s, th/(2*np.pi), ze/(2*np.pi*gvec.domain.tor_fraction))[2])
        
    # check Pmap, computing theta with 3d arrays of non-meshgrid coordinates
    s =np.random.rand(2,5,3)
    th=np.random.rand(2,5,3)*2.*np.pi
    ze=np.random.rand(2,5,3)*np.pi
    th2 = th + gvec._lambda(s, th, ze)

    assert np.allclose(s,  gvec.domain.Pmap(s, th2, ze)[0])
    assert np.allclose(th, gvec.domain.Pmap(s, th2, ze)[1])
    assert np.allclose(ze, gvec.domain.Pmap(s, th2, ze)[2])

    # compute theta with 3d arrays of non-meshgrid coordinates, compare f and f_pest again
    s2 = np.random.rand(2,5,3)
    th2= np.random.rand(2,5,3)*2*np.pi
    ze2= np.random.rand(2,5,3)*np.pi
    s,th,ze=gvec.domain.Pmap(s2, th2, ze2)
    
    assert np.allclose(gvec.domain.f_gvec(s, th, ze)[0], gvec.domain.f_pest(s2, th2, ze2)[0])
    assert np.allclose(gvec.domain.f_gvec(s, th, ze)[1], gvec.domain.f_pest(s2, th2, ze2)[1])
    assert np.allclose(gvec.domain.f_gvec(s, th, ze)[2], gvec.domain.f_pest(s2, th2, ze2)[2])

    # compare f_pest and f_unit_pest
    assert np.allclose(gvec.domain.f_pest(s2, th2, ze2)[0], gvec.domain.f_unit_pest(s2, th2/(2*np.pi), ze2/(2*np.pi*gvec.domain.tor_fraction))[0])
    assert np.allclose(gvec.domain.f_pest(s2, th2, ze2)[1], gvec.domain.f_unit_pest(s2, th2/(2*np.pi), ze2/(2*np.pi*gvec.domain.tor_fraction))[1])
    assert np.allclose(gvec.domain.f_pest(s2, th2, ze2)[2], gvec.domain.f_unit_pest(s2, th2/(2*np.pi), ze2/(2*np.pi*gvec.domain.tor_fraction))[2])

 
if __name__ == '__main__':
    #test_values(False ,"testcases/ellipstell/newBC_E1D6_M6N6/GVEC_ELLIPSTELL_E1D6_M6N6_State_0000_00200000","full")
    test_output_formats('pest', True ,"testcases/ellipstell/newBC_E4D6_M6N6/GVEC_ELLIPSTELL_E4D6_M6N6_State_0001_00200000")
    test_output_formats('unit', True ,"testcases/ellipstell/newBC_E4D6_M6N6/GVEC_ELLIPSTELL_E4D6_M6N6_State_0001_00200000")
