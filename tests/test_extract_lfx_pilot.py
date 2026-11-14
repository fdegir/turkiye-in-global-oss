import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/extract_lfx_pilot.py"
SPEC = importlib.util.spec_from_file_location("pilot", SCRIPT)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class PilotTests(unittest.TestCase):
    def test_inventory(self):
        entries = list(pilot.endpoints())
        self.assertEqual(len(entries), 7)
        self.assertEqual(len({r["endpoint_id"] for r, _, _ in entries}), 7)
        for row, _, params in entries:
            if row["entity_type"] != "project":
                self.assertEqual(params["endDate"], "2026-11-01")
                self.assertEqual((params["includeCodeContributions"], params["includeCollaborations"]),
                                 pilot.SCOPES[row["extraction_mode"]])

    def test_capture_preserves_bytes(self):
        row, url, params = next(r for r in pilot.endpoints() if r[0]["endpoint_id"] == "backstage_individual_all")
        raw = b'{"data":[{"country":"Turkey","countryCode":"TR","contributors":3,"contributorPercentage":1.2}]}\n'
        with tempfile.TemporaryDirectory() as tmp, patch.object(pilot, "fetch", return_value=(200, "application/json", raw, 5)):
            directory = pilot.capture(row, url, params, "test-token", Path(tmp), "run", "test-version")
            self.assertEqual((directory / "response.json").read_bytes(), raw)
            manifest = json.loads((directory / "manifest.json").read_text())
            self.assertEqual(manifest["response"]["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(manifest["response"]["size_bytes"], len(raw))
            self.assertEqual(manifest["request"]["query_parameters"], params)
            self.assertNotIn("test-token", json.dumps(manifest))

    def test_bad_payload(self):
        with self.assertRaises(ValueError):
            pilot.check_payload(b'{"data":[{}]}', "all", "organization")
        with self.assertRaises(ValueError):
            pilot.check_payload(b'{"slug":"wrong","repositories":[]}', "project_details", "project")

    def test_empty_geography_is_retained(self):
        self.assertEqual(pilot.check_payload(b'{"data":[]}', "all", "organization"), {"data": []})


if __name__ == "__main__":
    unittest.main()
