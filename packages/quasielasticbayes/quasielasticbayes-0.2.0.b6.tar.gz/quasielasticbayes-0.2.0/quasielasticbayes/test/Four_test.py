"""Characterization tests for Four module"""
import unittest
import numpy as np

from quasielasticbayes.Four import four


class FourTest(unittest.TestCase):
    """
    Characterization tests for the four Fortran module
    """
    # P = +1, N = -1, Z = 0
    def test_Four_PPN_Re(self):
        # reference inputs
        x = np.zeros(4098, dtype=complex)
        nonzero_entries = 8
        x[:nonzero_entries] = [complex(np.cos(float(i)+0.1), 0.)
                               for i in range(nonzero_entries)]
        y = x
        out = four(y, 8, 1, 1, -1)
        np.testing.assert_allclose(-1.6806+3.6243j, out[0], rtol=1e-3)
        np.testing.assert_allclose(1.4300-0.4846j, out[1], rtol=1e-3)
        np.testing.assert_allclose(0.5016-0.4846j, out[2], rtol=1e-3)
        np.testing.assert_allclose(1.4299+3.6243j, out[3], rtol=1e-3)
        np.testing.assert_allclose(-0.5748, out[4], rtol=1e-3)
        np.testing.assert_allclose(0.3780, out[5], rtol=1e-3)
        np.testing.assert_allclose(0.9833, out[6], rtol=1e-3)
        np.testing.assert_allclose(0.6845, out[7], rtol=1e-3)

    # In the code it only seems to use 1,-1,-1 and 1,1,0
    # So these are the two we will test
    def test_Four_PNN_Re(self):
        x = np.zeros(4098, dtype=complex)
        nonzero_entries = 8
        x[:nonzero_entries] = [complex(np.cos(float(i)+0.1), 0.)
                               for i in range(nonzero_entries)]
        y = x
        out = four(y, 8, 1, -1, -1)
        np.testing.assert_allclose(-1.681+3.6243j, out[0], rtol=1e-3)
        np.testing.assert_allclose(1.4299-0.4846j, out[1], rtol=1e-3)
        np.testing.assert_allclose(0.5016-0.4846j, out[2], rtol=1e-3)
        np.testing.assert_allclose(1.4299+3.6243j, out[3], rtol=1e-3)
        np.testing.assert_allclose(-0.5748, out[4], rtol=1e-3)
        np.testing.assert_allclose(0.37800, out[5], rtol=1e-3)
        np.testing.assert_allclose(0.9833, out[6], rtol=1e-3)
        np.testing.assert_allclose(0.6845, out[7], rtol=1e-3)

    def test_Four_PNN_Im(self):
        x = np.zeros(4098, dtype=complex)
        nonzero_entries = 8
        x[:nonzero_entries] = [complex(np.cos(float(i)+0.1), i)
                               for i in range(nonzero_entries)]
        y = x
        out = four(y, 8, 1, -1, -1)
        np.testing.assert_allclose(-1.681+13.2812j, out[0], rtol=1e-3)
        np.testing.assert_allclose(-2.5701+1.1722j, out[1], rtol=1e-3)
        np.testing.assert_allclose(0.5016-2.1415j, out[2], rtol=1e-3)
        np.testing.assert_allclose(5.4299-6.0326j, out[3], rtol=1e-3)
        np.testing.assert_allclose(-0.5748+4j, out[4], rtol=1e-3)
        np.testing.assert_allclose(0.3780+5j, out[5], rtol=1e-3)
        np.testing.assert_allclose(0.9833+6j, out[6], rtol=1e-3)
        np.testing.assert_allclose(0.6845+7j, out[7], rtol=1e-3)

    def test_Four_PPZ_Re(self):
        x = np.zeros(4098, dtype=complex)
        nonzero_entries = 8
        x[:nonzero_entries] = [complex(np.cos(float(i)+0.1), 0.)
                               for i in range(nonzero_entries)]
        y = x
        out = four(y, 8, 1, 1, 0)
        np.testing.assert_allclose(-0.0553, out[0], rtol=1e-2)
        np.testing.assert_allclose(1.5000+1.4527j, out[1], rtol=1e-2)
        np.testing.assert_allclose(1.0357, out[2], rtol=1e-2)
        np.testing.assert_allclose(1.5000-1.4527j, out[3], rtol=1e-2)
        np.testing.assert_allclose(-0.0554, out[4], rtol=1e-2)
        np.testing.assert_allclose(0.3780, out[5], rtol=1e-2)
        np.testing.assert_allclose(0.9833, out[6], rtol=1e-2)
        np.testing.assert_allclose(0.6845, out[7], rtol=1e-2)

    def test_Four_PPZ_Im(self):
        x = np.zeros(4098, dtype=complex)
        nonzero_entries = 8
        x[:nonzero_entries] = [complex(np.cos(float(i)+0.1), i)
                               for i in range(nonzero_entries)]
        y = x
        out = four(y, 8, 1, 1, 0)
        np.testing.assert_allclose(5.9446, out[0], rtol=1e-3)
        np.testing.assert_allclose(1.4999-1.3757j, out[1], rtol=1e-3)
        np.testing.assert_allclose(1.0357-2j, out[2], rtol=1e-3)
        np.testing.assert_allclose(1.4999-4.2812j, out[3], rtol=1e-3)
        np.testing.assert_allclose(-6.0554, out[4], rtol=1e-3)
        np.testing.assert_allclose(0.3780+5j, out[5], rtol=1e-3)
        np.testing.assert_allclose(0.9833+6j, out[6], rtol=1e-3)
        np.testing.assert_allclose(0.6845+7j, out[7], rtol=1e-3)


if __name__ == '__main__':
    unittest.main()
