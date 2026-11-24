import tempfile
import unittest
from pathlib import Path

from scripts.analysis.normalize_lfx import extract
from tests.fixtures.synthetic_atlas import write_archive, write_csv


class SyntheticAtlasTests(unittest.TestCase):
    def test_local_zip_normalisation(self):
        with tempfile.TemporaryDirectory() as d:
            rows = extract([write_archive(Path(d) / "atlas.zip")], ["TUR", "BRA", "POL"])
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]["count"], 2)
            self.assertEqual(rows[0]["denom"], 20)
            self.assertEqual(rows[2]["count"], 0)
            self.assertEqual(rows[2]["status"], "absent_reported_bucket")
            self.assertAlmostEqual(rows[0]["known_share"], 20)

    def test_synthetic_fixture_rows(self):
        with tempfile.TemporaryDirectory() as d:
            rows = write_csv(Path(d) / "atlas.csv").read_text()
            self.assertIn("atlas-security", rows)
            self.assertIn("synthetic_atlas_engine", rows)


if __name__ == "__main__":
    unittest.main()
