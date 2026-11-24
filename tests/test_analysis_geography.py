import tempfile
import unittest
from pathlib import Path
import pandas as pd
from tests.fixtures.synthetic_atlas import write_csv
from scripts.analysis.geography import analyse

class TestGeography(unittest.TestCase):
    def test_synthetic(self):
        with tempfile.TemporaryDirectory() as d:
            f=pd.read_csv(write_csv(Path(d)/"atlas.csv"))
            countries,projects,summary=analyse(f)
            self.assertEqual(len(projects),4)
            self.assertEqual(summary["n_countries"],5)
            self.assertTrue((projects.unknown_pct>0).all())

if __name__=="__main__":
    unittest.main()
