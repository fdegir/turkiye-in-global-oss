import unittest
import pandas as pd
from scripts.analysis.external_ranks import analyse

class TestExternalRanks(unittest.TestCase):
    def test_identical_rankings(self):
        result=analyse(pd.DataFrame({"iso3":["TUR","BRA","POL","ESP"],
                       "lfx_rank":[4,3,2,1],"external_rank":[4,3,2,1]}))
        self.assertEqual(result.n.iloc[0],4)
        self.assertAlmostEqual(result.rho.iloc[0],1.0)

if __name__=="__main__":
    unittest.main()
