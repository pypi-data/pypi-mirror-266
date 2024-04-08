"""Characterization tests for QLres module"""
import os.path
import unittest
import numpy as np
import tempfile

from quasielasticbayes.testing import add_path, load_json, RELATIVE_TOLERANCE_FIT, RELATIVE_TOLERANCE_PROB
from quasielasticbayes.QLdata import qldata

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class QLdataTest(unittest.TestCase):
    """
    Characterization tests using inputs that have been accepted as correct.
    The output is based on running BayesQuasi algorithm in mantid 6.2
    with the inputs taken from the BayesQuasiTest unit test
    """

    def test_qlres_minimal_input(self):
        with open(os.path.join(DATA_DIR, 'qldata', 'qldata_input.json'), 'r') as fh:
            inputs = load_json(fh)

        with tempfile.TemporaryDirectory() as tmp_dir:
            inputs['wrks'] = add_path(tmp_dir, inputs['wrks'])

            nd, xout, yout, eout, yfit, yprob = qldata(inputs['numb'],
                                                       inputs['Xv'],
                                                       inputs['Yv'],
                                                       inputs['Ev'],
                                                       inputs['reals'],
                                                       inputs['fitOp'],
                                                       inputs['Xdat'],
                                                       inputs['Xb'],
                                                       inputs['Yb'],
                                                       inputs['Eb'],
                                                       inputs['Wy'],
                                                       inputs['We'],
                                                       inputs['wrks'],
                                                       inputs['wrkr'],
                                                       inputs['lwrk'])
            # verify
            with open(os.path.join(DATA_DIR, 'qldata', 'qldata_output.json'), 'r') as fh:
                reference = load_json(fh)

            self.assertEqual(reference['nd'], nd)
            np.testing.assert_allclose(reference['xout'], xout)
            np.testing.assert_allclose(reference['yout'], yout)
            np.testing.assert_allclose(reference['eout'], eout)
            np.testing.assert_allclose(reference['yfit'], yfit, rtol=RELATIVE_TOLERANCE_FIT)
            np.testing.assert_allclose(reference['yprob'], yprob, rtol=RELATIVE_TOLERANCE_PROB)


if __name__ == '__main__':
    unittest.main()
