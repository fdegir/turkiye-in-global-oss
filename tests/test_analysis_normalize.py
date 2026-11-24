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

    def test_real_lfx_organization_field(self):
        import json
        import zipfile
        from pathlib import Path
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            p = Path(d) / "org.zip"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("bulk_runs/example/projects.csv",
                           "project_id,project_name,category,lfx_project_slug\n"
                           "EX001,Atlas,synthetic,atlas-core\n")
                z.writestr("atlas-core/geographical_distribution/all/organization/"
                           "2021_2026/one/response.json",
                           json.dumps({"data": [
                               {"countryCode": "TR", "organizations": 3, "organizationPercentage": 30},
                               {"countryCode": "XX", "organizations": 7, "organizationPercentage": 70}
                           ]}))
            rows = extract([p], ["TUR", "BRA"])
            self.assertEqual(rows[0]["entity"], "organization")
            self.assertEqual(rows[0]["count"], 3)
            self.assertEqual(rows[0]["denom"], 10)
            self.assertEqual(rows[0]["unknown"], 7)
            self.assertEqual(rows[1]["status"], "absent_reported_bucket")


if __name__ == "__main__":
    unittest.main()
