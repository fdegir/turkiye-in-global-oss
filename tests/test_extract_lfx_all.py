import importlib.util
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import extract_lfx_all as bulk
import extract_lfx_pilot as pilot

class BulkTests(unittest.TestCase):
    def test_eight_endpoints_and_case(self):
        rows = list(bulk.endpoints({"project_id": "CL001", "lfx_project_slug": "OpenStack"}))
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({r["endpoint_id"] for r, _, _ in rows}), 8)
        for row, url, params in rows:
            self.assertIn("/projects/OpenStack", url)
            if row["entity_type"] == "project":
                self.assertEqual(params, {})
            else:
                self.assertEqual(params["startDate"], pilot.START)
                self.assertEqual(params["endDate"], pilot.END)
                self.assertEqual((params["includeCodeContributions"], params["includeCollaborations"]), pilot.SCOPES[row["extraction_mode"]])

    def test_inventory_and_category(self):
        self.assertEqual(len(bulk.projects()), 42)
        selected = bulk.projects("software_delivery_developer_infrastructure")
        self.assertEqual(len(selected), 6)
        self.assertEqual({r["lfx_project_slug"] for r in selected}, {"argo", "backstage", "jenkins", "tekton", "harbor", "bazelbuild-bazel"})
        self.assertEqual(sum(len(list(bulk.endpoints(r))) for r in selected), 48)
        with self.assertRaises(ValueError):
            bulk.projects("not_a_category")

    def test_repository_normalization(self):
        self.assertEqual(bulk.normalize_repository_url("https://example.org/repo.git/"), "https://example.org/repo")

    def test_slug_validation(self):
        raw = b'{"slug":"OpenStack","repositories":[]}'
        pilot.check_payload(raw, "project_details", "project", "OpenStack")
        with self.assertRaises(ValueError):
            pilot.check_payload(raw, "project_details", "project", "openstack")

if __name__ == "__main__":
    unittest.main()
