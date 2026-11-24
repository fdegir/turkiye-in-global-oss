import tempfile
import unittest
from pathlib import Path
import pandas as pd
from tests.fixtures.synthetic_atlas import write_csv
from scripts.analysis.topsis import analyse,closeness

class TestTOPSIS(unittest.TestCase):
    def test_rank(self):
        with tempfile.TemporaryDirectory() as d:
            f=pd.read_csv(write_csv(Path(d)/"atlas.csv"))
            eco=pd.DataFrame({"iso3":["TUR","BRA","POL","ESP","KOR"],
                              "population":[10,20,30,40,50]})
            out=analyse(f,eco)
            self.assertEqual(len(out),5)
            self.assertTrue(out.topsis_primary.between(0,1).all())

    def test_ideal(self):
        self.assertAlmostEqual(closeness([[1,1],[5,5]],[0.5,0.5])[1],1)

if __name__=="__main__":
    unittest.main()
