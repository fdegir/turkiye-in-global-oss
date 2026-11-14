import hashlib
import importlib.util
import json
import os
import sys
import subprocess
import io
from contextlib import redirect_stderr
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/extract_lfx_pilot.py"
SPEC = importlib.util.spec_from_file_location("pilot", SCRIPT)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class PilotTests(unittest.TestCase):
    def test_missing_token_fails_without_request(self):
        with patch.dict(os.environ, {"LFX_API_TOKEN": ""}), patch.object(sys, "argv", [str(SCRIPT)]), patch.object(pilot, "fetch") as fetch, redirect_stderr(io.StringIO()) as stderr:
            with self.assertRaises(SystemExit) as exc:
                pilot.main()
            self.assertEqual(exc.exception.code, 2)
            self.assertIn("LFX_API_TOKEN", stderr.getvalue())
            fetch.assert_not_called()

    def test_curl_transport_and_rate_limit(self):
        calls = []
        def fake_run(args, **kwargs):
            calls.append(args)
            self.assertNotIn("test-token", " ".join(args))
            self.assertEqual(kwargs["input"], b"Authorization: Bearer test-token\n")
            self.assertEqual(args[0], "curl")
            self.assertIn("@-", args)
            self.assertIn("includeCollaborations=true", args[-1])
            Path(args[args.index("--output") + 1]).write_bytes(b'{"data":[]}')
            header_file = Path(args[args.index("--dump-header") + 1])
            if len(calls) == 1:
                header_file.write_text("HTTP/2 429\nRetry-After: 2\n\n")
                return subprocess.CompletedProcess(args, 0, b"429\napplication/json", b"")
            header_file.write_text("HTTP/2 200\nX-RateLimit-Remaining: 0\nX-RateLimit-Reset: 1\n\n")
            return subprocess.CompletedProcess(args, 0, b"200\napplication/json", b"")
        with patch.object(pilot.subprocess, "run", side_effect=fake_run), patch.object(pilot.time, "sleep") as sleep:
            status, content_type, raw, duration = pilot.fetch(pilot.BASE + "/v1-alpha/projects/backstage", {"includeCollaborations": True}, "test-token")
        self.assertEqual((status, content_type, raw), (200, "application/json", b'{"data":[]}'))
        self.assertEqual(len(calls), 2)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [2, 1])

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
