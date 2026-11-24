import tempfile
import unittest
from pathlib import Path
import pandas as pd

from tests.fixtures.synthetic_atlas import write_csv
from scripts.analysis.geography import evaluate, bounded_focal_stress


class TestGeography(unittest.TestCase):
    def test_synthetic_sensitivity(self):
        with tempfile.TemporaryDirectory() as d:
            f = pd.read_csv(write_csv(Path(d) / "atlas.csv"))
            summary, ranks = evaluate(f, multipliers=[0, 1, 2, 5])
            self.assertEqual(len(summary), 4)
            self.assertEqual(len(ranks), 4 * 5)
            self.assertEqual(summary.total_countries.tolist(), [5] * 4)
            self.assertTrue(summary.unknown_records.eq(40).all())
            self.assertTrue(summary.focal_mean_share_pct.is_monotonic_increasing)
            # A proportional allocation of Unknown is the known-only share.
            known = f[f.iso3 == "TUR"].known_share.mean()
            self.assertAlmostEqual(float(summary.loc[summary.multiplier == 1,
                                        "focal_mean_share_pct"].iloc[0]), known)
            extreme = bounded_focal_stress(f, fractions=[0, 1])
            self.assertEqual(len(extreme), 2)
            self.assertGreater(extreme.focal_mean_share_pct.iloc[1],
                               extreme.focal_mean_share_pct.iloc[0])

    def test_invalid_multiplier(self):
        with tempfile.TemporaryDirectory() as d:
            f = pd.read_csv(write_csv(Path(d) / "atlas.csv"))
            with self.assertRaises(ValueError):
                evaluate(f, multipliers=[-1])


if __name__ == "__main__":
    unittest.main()
