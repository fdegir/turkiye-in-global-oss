import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import pandas as pd
from tests.fixtures.synthetic_atlas import write_csv
from scripts.analysis.health import read_health, analyse, add_health_weighted_topsis


class TestLFXHealth(unittest.TestCase):
    def test_archive_coverage_and_rank_sensitivity(self):
        with tempfile.TemporaryDirectory() as d:
            archive = Path(d) / "synthetic_health.zip"
            with zipfile.ZipFile(archive, "w") as z:
                for i, slug in enumerate(["atlas-core","atlas-edge","atlas-cloud","atlas-security"]):
                    info = dict(score=70 + i*5, healthMaxScore=100,
                                coveredCategoryCount=3,
                                maintainerHealthScore=30,
                                securitySupplyChainScore=20,
                                developmentActivityScore=20+i*5)
                    z.writestr(f"{slug}/health_score/health_score/project/snapshot/example/response.json",
                               json.dumps(info))
            scores = read_health([archive])
            self.assertEqual(scores.coverage.tolist(), ["full"]*4)
            obs = pd.read_csv(write_csv(Path(d)/"observations.csv"))
            ranks, stats = analyse(obs, scores)
            self.assertEqual(int(stats.full_coverage.iloc[0]),4)
            self.assertEqual(len(ranks), 5)
            eco = pd.DataFrame(dict(iso3=["TUR","BRA","POL","ESP","KOR"],
                                    population=[10,20,30,40,50]))
            table = add_health_weighted_topsis(ranks, eco, obs)
            self.assertEqual(len(table), 5)
            self.assertTrue(table.augmented_closeness.between(0,1).all())

    def test_partial_score_exclusion(self):
        with tempfile.TemporaryDirectory() as d:
            archive = Path(d)/"health.zip"
            with zipfile.ZipFile(archive,"w") as z:
                z.writestr("a/health_score/health_score/project/snapshot/one/response.json",
                    json.dumps({"score":55,"healthMaxScore":65,"coveredCategoryCount":2}))
                z.writestr("b/health_score/health_score/project/snapshot/one/response.json",
                    json.dumps({"score":None,"healthMaxScore":None,"coveredCategoryCount":None}))
            result = read_health([archive])
            self.assertEqual(result.set_index("slug").loc["a","coverage"],"partial")
            self.assertEqual(result.set_index("slug").loc["b","coverage"],"missing")


if __name__ == "__main__":
    unittest.main()
