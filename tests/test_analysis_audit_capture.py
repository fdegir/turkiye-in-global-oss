import csv
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from scripts.analysis.audit_capture import audit

class TestCaptureAudit(unittest.TestCase):
    def test_checksum_mismatch_is_detected(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"ex.zip"
            raw=json.dumps({"data":[{"countryCode":"TR","organizations":2}]}).encode()
            manifest={"response":{"sha256":hashlib.sha256(raw).hexdigest(),
                                  "size_bytes":len(raw)},
                      "retrieval":{"http_status":200},"project":{"slug":"atlas"}}
            prefix="atlas/geographical_distribution/all/organization/2021_2026/run/"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr(prefix+"response.json",raw)
                z.writestr(prefix+"manifest.json",json.dumps(manifest))
            self.assertEqual(audit([p])["issues"],[])
            manifest["response"]["sha256"]="wrong"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr(prefix+"response.json",raw)
                z.writestr(prefix+"manifest.json",json.dumps(manifest))
            self.assertTrue(any("SHA-256" in x for x in audit([p])["issues"]))

if __name__=="__main__":
    unittest.main()
