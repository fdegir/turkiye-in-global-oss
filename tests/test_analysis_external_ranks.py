import tempfile
import unittest
from pathlib import Path
import pandas as pd

from tests.fixtures.synthetic_atlas import write_csv
from scripts.analysis.external_ranks import analyse, G20


class TestExternalRanks(unittest.TestCase):
    def test_synthetic_four_countries(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = pd.read_csv(write_csv(Path(tmp) / "atlas.csv"))
            subset = ("TUR", "BRA", "POL", "ESP")
            external = pd.DataFrame([
                {"iso2": "TR", "count_total_contributors": 1},
                {"iso2": "BR", "count_total_contributors": 3},
                {"iso2": "PL", "count_total_contributors": 4},
                {"iso2": "ES", "count_total_contributors": 2},
            ])
            ranks, summary = analyse(data, external, iso3_codes=subset)
            self.assertEqual(len(ranks), 4)
            self.assertAlmostEqual(float(summary.rho.iloc[0]), 1.0)
            self.assertEqual(int(ranks[ranks.iso3 == "TUR"].lfx_rank.iloc[0]), 4)

    def test_missing_external_country_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = pd.read_csv(write_csv(Path(tmp) / "atlas.csv"))
            external = pd.DataFrame([{"iso2": "TR", "count_total_contributors": 1}])
            with self.assertRaises(ValueError):
                analyse(data, external, iso3_codes=("TUR", "BRA"))

    def test_exact_g20_size(self):
        self.assertEqual(len(G20), 19)


if __name__ == "__main__":
    unittest.main()
