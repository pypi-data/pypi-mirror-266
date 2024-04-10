import pytest

@pytest.mark.parametrize('use_pyccel,gvec_file', [(False,"testcases/ellipstell/newBC_E1D6_M6N6/GVEC_ELLIPSTELL_E1D6_M6N6_State_0000_00200000"),
                                                  (True ,"testcases/ellipstell/newBC_E4D6_M6N6/GVEC_ELLIPSTELL_E4D6_M6N6_State_0001_00200000")])   
@pytest.mark.parametrize('mapping', ['gvec', 'pest', 'unit', 'unit_pest', 'wo_hmap'])
def test_mhd_fields(mapping, use_pyccel,gvec_file):
    '''Test whether the return of mhd field evaluations has the correct type/dimension.'''

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

    assert isinstance(gvec.p0(s, a1, a2), float)
    assert isinstance(gvec.p3(s, a1, a2), float)
    assert np.all([isinstance(gvec.bv(s, a1, a2)[j], float) for j in range(3)])
    assert np.all([isinstance(gvec.b1(s, a1, a2)[j], float) for j in range(3)])
    assert np.all([isinstance(gvec.b2(s, a1, a2)[j], float) for j in range(3)])
    assert np.all([isinstance(gvec.b_cart(s, a1, a2)[i][j], float) for j in range(3) for i in range(2)])
    assert np.all([isinstance(gvec.av(s, a1, a2)[j], float) for j in range(3)])
    assert np.all([isinstance(gvec.a1(s, a1, a2)[j], float) for j in range(3)])
    assert np.all([isinstance(gvec.a2(s, a1, a2)[j], float) for j in range(3)])
    assert np.all([isinstance(gvec.a_cart(s, a1, a2)[i][j], float) for j in range(3) for i in range(2)])
    assert np.all([isinstance(gvec.jv(s, a1, a2)[j], float) for j in range(3)])
    assert np.all([isinstance(gvec.j1(s, a1, a2)[j], float) for j in range(3)])
    assert np.all([isinstance(gvec.j2(s, a1, a2)[j], float) for j in range(3)])
    assert np.all([isinstance(gvec.j_cart(s, a1, a2)[i][j], float) for j in range(3) for i in range(2)])

    # test single-point array evaluation
    s = np.array([s])
    a1 = np.array([a1])
    a2 = np.array([a2])

    assert gvec.p0(s, a1, a2).shape == (1, 1, 1)
    assert gvec.p3(s, a1, a2).shape == (1, 1, 1)
    assert np.all([gvec.bv(s, a1, a2)[j].shape == (1, 1, 1) for j in range(3)])
    assert np.all([gvec.b1(s, a1, a2)[j].shape == (1, 1, 1) for j in range(3)])
    assert np.all([gvec.b2(s, a1, a2)[j].shape == (1, 1, 1) for j in range(3)])
    assert np.all([gvec.b_cart(s, a1, a2)[i][j].shape == (1, 1, 1) for j in range(3) for i in range(2)])
    assert np.all([gvec.av(s, a1, a2)[j].shape == (1, 1, 1) for j in range(3)])
    assert np.all([gvec.a1(s, a1, a2)[j].shape == (1, 1, 1) for j in range(3)])
    assert np.all([gvec.a2(s, a1, a2)[j].shape == (1, 1, 1) for j in range(3)])
    assert np.all([gvec.a_cart(s, a1, a2)[i][j].shape == (1, 1, 1) for j in range(3) for i in range(2)])
    assert np.all([gvec.jv(s, a1, a2)[j].shape == (1, 1, 1) for j in range(3)])
    assert np.all([gvec.j1(s, a1, a2)[j].shape == (1, 1, 1) for j in range(3)])
    assert np.all([gvec.j2(s, a1, a2)[j].shape == (1, 1, 1) for j in range(3)])
    assert np.all([gvec.j_cart(s, a1, a2)[i][j].shape == (1, 1, 1) for j in range(3) for i in range(2)])

    # test 1d array evaluation
    s = np.linspace(.01, 1, 4) # mappings are singular at s=0
    if 'unit' not in mapping:
        a1 = np.linspace(0, 2*np.pi, 5)
        a2 = np.linspace(0, 2*np.pi, 6)
    else:
        a1 = np.linspace(0, 1, 4)
        a2 = np.linspace(0, 1, 5)

    shp3 = (s.size, a1.size, a2.size)

    assert gvec.p0(s, a1, a2).shape == shp3
    assert gvec.p3(s, a1, a2).shape == shp3
    tmp = gvec.bv(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.b1(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.b2(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.b_cart(s, a1, a2)
    assert np.all([tmp[i][j].shape == shp3 for j in range(3) for i in range(2)])
    tmp = gvec.av(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.a1(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.a2(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.a_cart(s, a1, a2)
    assert np.all([tmp[i][j].shape == shp3 for j in range(3) for i in range(2)])
    tmp = gvec.jv(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.j1(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.j2(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.j_cart(s, a1, a2)
    assert np.all([tmp[i][j].shape == shp3 for j in range(3) for i in range(2)])

    # test 3d array evaluation
    s, a1, a2 = np.meshgrid(s, a1, a2, indexing='ij')

    assert gvec.p0(s, a1, a2).shape == shp3
    assert gvec.p3(s, a1, a2).shape == shp3
    tmp = gvec.bv(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.b1(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.b2(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.b_cart(s, a1, a2)
    assert np.all([tmp[i][j].shape == shp3 for j in range(3) for i in range(2)])
    tmp = gvec.av(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.a1(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.a2(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.a_cart(s, a1, a2)
    assert np.all([tmp[i][j].shape == shp3 for j in range(3) for i in range(2)])
    tmp = gvec.jv(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.j1(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.j2(s, a1, a2)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.j_cart(s, a1, a2)
    assert np.all([tmp[i][j].shape == shp3 for j in range(3) for i in range(2)])
    
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
    
    assert gvec.p0(s, a1, a2, flat_eval=True).shape == shp3
    assert gvec.p3(s, a1, a2, flat_eval=True).shape == shp3
    tmp = gvec.bv(s, a1, a2, flat_eval=True)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.b1(s, a1, a2, flat_eval=True)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.b2(s, a1, a2, flat_eval=True)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.b_cart(s, a1, a2, flat_eval=True)
    assert np.all([tmp[i][j].shape == shp3 for j in range(3) for i in range(2)])
    tmp = gvec.av(s, a1, a2, flat_eval=True)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.a1(s, a1, a2, flat_eval=True)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.a2(s, a1, a2, flat_eval=True)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.a_cart(s, a1, a2, flat_eval=True)
    assert np.all([tmp[i][j].shape == shp3 for j in range(3) for i in range(2)])
    tmp = gvec.jv(s, a1, a2, flat_eval=True)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.j1(s, a1, a2, flat_eval=True)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.j2(s, a1, a2, flat_eval=True)
    assert np.all([tmp[j].shape == shp3 for j in range(3)])
    tmp = gvec.j_cart(s, a1, a2, flat_eval=True)
    assert np.all([tmp[i][j].shape == shp3 for j in range(3) for i in range(2)])

 
@pytest.mark.parametrize('use_pyccel,gvec_file', [(True ,"testcases/ellipstell/newBC_E4D6_M6N6/GVEC_ELLIPSTELL_E4D6_M6N6_State_0001_00200000")])   
@pytest.mark.parametrize('unit_tor_domain', ["one-fp","full"])   
def test_values(use_pyccel,gvec_file,unit_tor_domain):
    '''Compare values of b_cart for different mappings provided by GVEC_domain.'''

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
    s0 = np.array([.5,.99])
    th0 = np.random.rand(5)*2*np.pi
    ze0 = np.random.rand(3)*np.pi/gvec.nfp
    # all combinations of 1D arrays  
    for n0,n1,n2 in [(-1,-1,-1),(1,1,1),(2,1,1),(2,5,3),(2,5,1),(2,1,3),(1,5,3),(1,5,1),(1,1,3)]:
        if((n0,n1,n2)==(-1,-1,-1)): # also test a fully 3d array
            s =np.random.rand(3,4,2)
            th=np.random.rand(3,4,2)*2*np.pi
            ze=np.random.rand(3,4,2)*np.pi/gvec.nfp
        else:
            s  = s0[0:n0]
            th = th0[0:n1]
            ze = ze0[0:n2]
            s, th, ze = gvec.domain.prepare_args(s, th, ze,sparse=False)
        th2 = th + gvec._lambda(s, th, ze)
        
        gvec.mapping="gvec"
        b_gvec, xyz_gvec = gvec.b_cart(s,th,ze)
        a_gvec, xyz_gvec = gvec.a_cart(s,th,ze)
        
        # compare f and f_pest
        gvec.mapping="pest"
        b_pest, xyz_pest = gvec.b_cart(s,th2,ze)
        a_pest, xyz_pest = gvec.a_cart(s,th2,ze)
        
        assert np.allclose(b_gvec[0], b_pest[0])
        assert np.allclose(b_gvec[1], b_pest[1])
        assert np.allclose(b_gvec[2], b_pest[2])
        assert np.allclose(a_gvec[0], a_pest[0])
        assert np.allclose(a_gvec[1], a_pest[1])
        assert np.allclose(a_gvec[2], a_pest[2])
        
        # compare f and f_unit, where the tor_fraction is needed for unit to have the same point positions
        gvec.mapping="unit"
        b_unit, xyz_unit = gvec.b_cart(s,th/(2*np.pi),ze/(2*np.pi*gvec.domain.tor_fraction))
        a_unit, xyz_unit = gvec.a_cart(s,th/(2*np.pi),ze/(2*np.pi*gvec.domain.tor_fraction))
       
        assert np.allclose(b_gvec[0], b_unit[0])
        assert np.allclose(b_gvec[1], b_unit[1])
        assert np.allclose(b_gvec[2], b_unit[2])
        assert np.allclose(a_gvec[0], a_unit[0])
        assert np.allclose(a_gvec[1], a_unit[1])
        assert np.allclose(a_gvec[2], a_unit[2])
        
        # compare f_unit_pest and f_gvec
        gvec.mapping="unit_pest"
        b_unit_pest, xyz_unit_pest = gvec.b_cart(s,th2/(2*np.pi),ze/(2*np.pi*gvec.domain.tor_fraction))
        a_unit_pest, xyz_unit_pest = gvec.a_cart(s,th2/(2*np.pi),ze/(2*np.pi*gvec.domain.tor_fraction))
        
        assert np.allclose(b_unit_pest[0], b_gvec[0])
        assert np.allclose(b_unit_pest[1], b_gvec[1])
        assert np.allclose(b_unit_pest[2], b_gvec[2])
        assert np.allclose(a_unit_pest[0], a_gvec[0])
        assert np.allclose(a_unit_pest[1], a_gvec[1])
        assert np.allclose(a_unit_pest[2], a_gvec[2])

@pytest.mark.parametrize('use_pyccel,gvec_file', [(True ,"testcases/ellipstell/newBC_E4D6_M6N6/GVEC_ELLIPSTELL_E4D6_M6N6_State_0001_00200000")])   
@pytest.mark.parametrize('mapping', ['gvec', 'pest', 'unit', 'unit_pest'])
def test_derivs_with_FD(mapping,use_pyccel,gvec_file):
    '''Compare exact derivatives of functions to their finite difference counterpart.'''

    import os
    import numpy as np
    from gvec_to_python.reader.gvec_reader import create_GVEC_json
    from gvec_to_python import GVEC
    import gvec_to_python as _

    def do_FD(func,s,th,ze,der=None):
        '''  compute s,th,ze derivative of input function func'''
        eps=1.0e-8
        f0 = func(s,th,ze)
        df_ds  = (func(s+eps,th,ze) - f0 )/ eps
        df_dth = (func(s,th+eps,ze) - f0 )/ eps
        df_dze = (func(s,th,ze+eps) - f0 )/ eps
        if(der=="s"):
            return df_ds
        elif(der=="th"):
            return df_dth
        elif(der=="ze"):
            return df_dze
        else:
            return df_ds,df_dth,df_dze

    def bth(s,th,ze):
        '''  computes B^theta=b^theta/det_df'''
        return gvec._b_small_th(s, th, ze) / gvec.domain.det_df_gvec(s, th, ze)
        
    def bze(s,th,ze):
        '''  computes B^zeta=b^zeta/det_df'''
        return gvec._b_small_ze(s, th, ze) / gvec.domain.det_df_gvec(s, th, ze)

    # give absolute paths to the files
    pkg_path = _.__path__[0]
    dat_file_in   = os.path.join( pkg_path, gvec_file+'.dat')
    json_file_out = os.path.join( pkg_path, gvec_file+'.json')
    create_GVEC_json(dat_file_in, json_file_out)

    # main object 
    gvec = GVEC(json_file_out, mapping=mapping, use_pyccel=use_pyccel)
    print('gvec.mapping: ', gvec.mapping)

    # test single-point float evaluation
    s = .45
    if 'unit' not in mapping:
        th = 0.77*2*np.pi
        ze = 0.33*2*np.pi
    else:
        th = .77
        ze = .33


    #check derivative of Jacobian of gvec mapping
    dJf_FD = do_FD(gvec.domain.det_df_gvec,s,th,ze)
    dJf_ex = [gvec.domain.dJ_gvec(s,th,ze,der=deriv) for deriv in  ["s","th","ze"]]
    assert(np.allclose(dJf_FD,dJf_ex,rtol=1e-6,atol=1e-4))
    
    
    # check derivative of metric tensor g of the gvec mapping
    for deriv in ["s","th","ze"]:
        dg_FD = do_FD(gvec.domain.g_gvec,s,th,ze,der=deriv)
        dg_ex = gvec.domain.dg_gvec(s,th,ze,der=deriv)
        assert(np.allclose(dg_FD,dg_ex,rtol=1e-6,atol=1e-4))
    
        
    # check derivative of  B^theta 
    dbth_FD = do_FD(bth,s,th,ze)
    dbth_ex  = gvec._grad_b_theta(s, th, ze)
    assert(np.allclose(dbth_FD,dbth_ex,rtol=1e-6,atol=1e-4))
        
    # check derivative of  B^zeta 
    dbze_FD = do_FD(bze,s,th,ze)
    dbze_ex  = gvec._grad_b_zeta(s, th, ze)
    #print("diff dbze_FD-dbze_ex",dbze_FD-np.array(dbze_ex))
    assert(np.allclose(dbze_FD,dbze_ex,rtol=1e-6,atol=1e-4))



if __name__ == '__main__':
    #test_mhd_fields('gvec', use_pyccel=False,gvec_file='testcases/ellipstell/newBC_E1D6_M6N6/GVEC_ELLIPSTELL_E1D6_M6N6_State_0000_00200000')
    test_mhd_fields('pest', use_pyccel=True ,gvec_file='testcases/ellipstell/newBC_E4D6_M6N6/GVEC_ELLIPSTELL_E4D6_M6N6_State_0001_00200000')
