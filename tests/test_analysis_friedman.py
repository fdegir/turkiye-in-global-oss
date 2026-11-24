import tempfile
import unittest
from pathlib import Path
import pandas as pd
from tests.fixtures.synthetic_atlas import write_csv
from scripts.analysis.friedman import analyse

class TestSyntheticAtlas(unittest.TestCase):
    def test_analysis_produces_results(self):
        with tempfile.TemporaryDirectory() as folder:
            data=pd.read_csv(write_csv(Path(folder)/"atlas.csv"))
            output=analyse(data)
            if isinstance(output,tuple):
                self.assertTrue(all(len(x)>0 for x in output))
            else:
                self.assertGreater(len(output),0)

if __name__=="__main__":
    unittest.main()
