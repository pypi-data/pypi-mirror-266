# 3D GVEC equilibria in Python

PyPI install:

```
pip install gvec_to_python
```
Or from source:
```
git clone git@gitlab.mpcdf.mpg.de:gvec-group/gvec_to_python.git
cd gvec_to_python
pip install -e .
```
Compile kernels for faster evaluations:
```
compile-gvec-tp
```

# Usage

The [Galerkin Variational Equilibrium Code (GVEC)](https://gitlab.mpcdf.mpg.de/gvec-group/gvec) calculates magneto-hydrodynamic (MHD) equilibria for Tokamaks and Stellarators. `gvec_to_python` parses the GVEC output file (`.dat`) and collects the data in a `.json` file: 
```
from gvec_to_python.reader.gvec_reader import create_GVEC_json

create_GVEC_json(dat_file_in, json_file_out)  # give absolute paths to the files
```
In a second step, callables of MHD equilibrium quantities are created as methods of the GVEC class:
```
from gvec_to_python import GVEC

gvec = GVEC(json_file_out, mapping='gvec')
```
Profiles can be evaluated via
```
gvec.profiles.profile(s, name='phi')        # toroidal flux profile (radial coordinate s~sqrt(phi_norm)
gvec.profiles.profile(s, name='chi')        # poloidal flux profile
gvec.profiles.profile(s, name='iota')       # iota profile
gvec.profiles.profile(s, name='pressure')   # pressure profile
```
where the radial coordinate `s` is the square-root of the normalized toroidal flux. Profile derivatives are callable via
```
gvec.profiles.profile(s, name='phi', der='s') # first derivative
gvec.profiles.profile(s, name='phi', der='ss') # second derivative
```

![Profiles](notebooks/profiles.png "Title")

The mapping and metric coefficients are called via
```
gvec.f(s, a1, a2)       # mapping
gvec.df(s, a1, a2)      # Jacobian matrix
gvec.det_df(s, a1, a2)  # Jacobian determinant
gvec.df_inv(s, a1, a2)  # inverse Jacobian matrix
gvec.g(s, a1, a2)       # metric tensor
gvec.g_inv(s, a1, a2)   # inverse metric tensor
```
The **radial coordinate** denotes `s`  is **always the square-root of the normalized toroidal flux**, `a1` is the poloidal angle and `a2` denotes the toroidal angle.

![Profiles](notebooks/poloidal.png "Title")
![](notebooks/topview.png)

Five different mappings can be invoked by the `mapping.setter`:
```
# gvec standard coordinates: (s, th, ze) -> (x, y, z) 
#   from (s,a1,a2)=(s,theta,zeta) in [0,1],[0,2pi],[0,2pi] to cartesian coordinates (x,y,z)
gvec.mapping = 'gvec'

# gvec straight-field-line mapping (PEST) (s, theta*, zeta*) -> (x, y, z) 
#   from (s,a1,a2)=(s,theta*,zeta*) in [0,1],[0,2pi],[0,2pi] to cartesian coordinates (x,y,z)
gvec.mapping = 'pest'

# gvec with unit cube as logical domain  (s, u, v) -> (x,y,z)
#   from (s,a1,a2)=(s,u,v) in [0,1],[0,1],[0,1] to cartesian coordinates (x,y,z)
gvec.mapping = 'unit'

# gvec straight-field-line (PEST)  with unit cube as logical domain  (s, u*, v*) -> (x,y,z)
#   from (s,a1,a2)=(s,u*,v*) in [0,1],[0,1],[0,1] to cartesian coordinates (x,y,z)
gvec.mapping = 'unit_pest'

# gvec without hmap (s,th,ze) -> (X1,X2,zeta) 
#   from (s,a1,a2)=(s,theta,zeta) in [0,1],[0,2pi],[0,2pi] to GVECs internal coordinates (X1,X2,zeta)
#   if default torus (hmap=1) is used in GVEC, then (R,Z,phi)=(X1,X2,-zeta)
gvec.mapping = 'wo_hmap'
```

![](notebooks/dtheta.png)
![](notebooks/det_df.png)

The MHD quantities are called via
```
gvec.p0(s, a1, a2)      # pressure as 0-form
gvec.p3(s, a1, a2)      # pressure as 3-form

gvec.bv(s, a1, a2)      # contra-variant B-field
gvec.b1(s, a1, a2)      # co-variant B-field (1-form)
gvec.b2(s, a1, a2)      # 2-form B-field
gvec.b_cart(s, a1, a2)  # Cartesian B-field

gvec.av(s, a1, a2)      # contra-variant vector potential
gvec.a1(s, a1, a2)      # co-variant vector potential (1-form)
gvec.a2(s, a1, a2)      # 2-form vector potential
gvec.a_cart(s, a1, a2)  # Cartesian vector potential

gvec.jv(s, a1, a2)      # contra-variant current 
gvec.j1(s, a1, a2)      # co-variant current (1-form)
gvec.j2(s, a1, a2)      # 2-form current
gvec.j_cart(s, a1, a2)  # Cartesian current
```

![](notebooks/pressure.png)

![](notebooks/absB.png)




