import pytest

@pytest.mark.parametrize('degree', [1, 2, 3, 4, 5])
def test_splines(degree):
    '''Test spline evaluations and derivatives.'''

    import numpy as np
    from gvec_to_python.base.sbase import sBase
    from gvec_to_python.hylife.utilities_FEEC.spline_space import spline_space_1d

    sgrid = np.linspace(0, 1, 10)
    base = sBase(sgrid, degree)
    knots = base.knots
    dim = base.spline_space.NbaseN

    s = np.random.rand(30)

    if degree == 1:
        for i in range(dim):
            coef = np.zeros(dim)
            coef[i] = 1.
            assert np.all(base.eval_dds(s, coef) == 0.*s)
        return
    elif degree == 2:
        return

    space1 = spline_space_1d(knots[1:-1], degree - 1, False)
    space2 = spline_space_1d(knots[2:-2], degree - 2, False)

    print(knots)
    print(space1.T)
    print(space2.T)

    # weights for first derivative
    w1 = [None]
    for i in range(1, dim):
        w1 += [degree / (knots[i + degree] - knots[i])] 

    # weights for second derivative
    w2 = [None]
    for i in range(1, space1.NbaseN):
        w2 += [(degree - 1) / (space1.T[i + degree - 1] - space1.T[i])] 

    for i in range(dim):
        coef = np.zeros(dim)
        coef[i] = 1.

        coef1 = np.zeros(dim - 1)

        coef2 = np.zeros(dim - 2)

        if i == 0:
            coef1[i] = - w1[i + 1]

            coef2[i] = w1[i + 1] * w2[i + 1]
        elif i == 1:
            coef1[i - 1] = w1[i]
            coef1[i] = -w1[i + 1]

            coef2[i - 1] = - w1[i] * w2[i] - w1[i + 1] * w2[i]
            coef2[i] = w1[i + 1] * w2[i + 1]
        elif i == dim - 2:
            coef1[i - 1] = w1[i]
            coef1[i] = -w1[i + 1]

            coef2[i - 2] = w1[i] * w2[i-1]
            coef2[i - 1] = - w1[i] * w2[i] - w1[i + 1] * w2[i]
        elif i == dim - 1:
            coef1[i - 1] = w1[i]

            coef2[i - 2] = w1[i] * w2[i-1]
        else:
            coef1[i - 1] = w1[i]
            coef1[i] = -w1[i + 1]

            coef2[i - 2] = w1[i] * w2[i-1]
            coef2[i - 1] = - w1[i] * w2[i] - w1[i + 1] * w2[i]
            coef2[i] = w1[i + 1] * w2[i + 1] 
            
        vals1 = space1.evaluate_N(s.flatten(), coef1).reshape(s.shape)
        vals2 = space2.evaluate_N(s.flatten(), coef2).reshape(s.shape)

        assert np.allclose(base.eval_ds(s, coef), vals1)
        assert np.allclose(base.eval_dds(s, coef), vals2)

if __name__ == '__main__':
    test_splines(3)