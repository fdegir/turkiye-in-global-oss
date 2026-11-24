import tempfile
import unittest
from pathlib import Path
import pandas as pd
from tests.fixtures.synthetic_atlas import write_csv
from scripts.analysis.spearman import analyse

class TestSpearman(unittest.TestCase):
    def test_synthetic(self):
        with tempfile.TemporaryDirectory() as d:
            frame=pd.read_csv(write_csv(Path(d)/"atlas.csv"))
            economics=pd.DataFrame({"iso3":["TUR","BRA","POL","ESP","KOR"],
                "population":[10,20,30,40,50],"gdp_bn":[100,200,300,400,500],
                "rd_gdp_pct":[1.0,1.5,2.0,2.5,3.0],"rd_year":[2023]*5})
            result=analyse(frame,economics)
            self.assertTrue({"population","gdp_bn","rd_gdp_pct"}.issubset(set(result.variable)))
            self.assertTrue((result.n>=3).all())

if __name__=="__main__":
    unittest.main()
