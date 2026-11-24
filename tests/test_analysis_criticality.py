import gzip
import tempfile
import unittest
from pathlib import Path
import pandas as pd
from scripts.analysis.criticality import analyse

class TestCriticality(unittest.TestCase):
    def test_exact_url_matching(self):
        projects=pd.DataFrame([dict(project_id="EX001",primary_repository_url="https://github.com/example/atlas"),
          dict(project_id="EX002",primary_repository_url="https://git.example.org/atlas")])
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"criticality.csv.gz"
            with gzip.open(f,"wt") as stream:
                stream.write("repo.url,default_score,collection_date\nhttps://github.com/example/atlas,0.75,2025-07-25\n")
            result=analyse(projects,f)
            self.assertEqual(result.match_status.tolist(),["matched","non_github_primary"])
            self.assertAlmostEqual(result.openssf_criticality.iloc[0],0.75)

if __name__=="__main__":
    unittest.main()
