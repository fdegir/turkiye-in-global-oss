#!/usr/bin/env python3
"""Capture the seven documented Backstage pilot responses, without normalization."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from uuid import uuid4
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://api.insights.linuxfoundation.org"
REGISTRY = ROOT / "data/audit/project_api_endpoints.csv"
START, END = "2021-11-01", "2026-11-01"
SCOPES = {"code": (True, False), "collaboration": (False, True), "all": (True, True)}


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def git_version():
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "backstage-pilot-v1"


def endpoints():
    with REGISTRY.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["project_slug"] == "backstage"]
    if len(rows) != 7:
        raise ValueError("Expected seven Backstage endpoints; merge PR #17 first.")
    expected = {("project_details", "project")} | {
        (scope, entity) for scope in SCOPES for entity in ("individual", "organization")
    }
    if {(r["extraction_mode"], r["entity_type"]) for r in rows} != expected:
        raise ValueError("Unexpected pilot endpoint inventory.")
    for r in rows:
        mode, entity = r["extraction_mode"], r["entity_type"]
        params = json.loads(r["query_parameters"] or "{}")
        url = r["endpoint_url"].rstrip("/")
        if mode == "project_details":
            wanted = BASE + "/v1-alpha/projects/backstage"
            expected_params = {}
        else:
            route = "contributor" if entity == "individual" else "organization"
            wanted = BASE + "/v1-alpha/projects/backstage/contributors/" + route + "-geographical-distribution"
            code, collab = SCOPES[mode]
            expected_params = {"startDate": START, "endDate": END,
                               "includeCodeContributions": code, "includeCollaborations": collab}
        if url != wanted or params != expected_params or r["http_method"] != "GET":
            raise ValueError("Unexpected URL, method or parameters: " + r["endpoint_id"])
        yield r, url, params


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url, params, token):
    query = urlencode({k: str(v).lower() if isinstance(v, bool) else v
                       for k, v in params.items()})
    request = Request(url + ("?" + query if query else ""),
                      headers={"Authorization": "Bearer " + token, "Accept": "application/json"})
    opener = build_opener(NoRedirect())
    for attempt in range(3):
        start = time.monotonic()
        try:
            with opener.open(request, timeout=60) as response:
                return response.status, response.headers.get("Content-Type"), response.read(), int((time.monotonic()-start)*1000)
        except HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < 2:
                retry = exc.headers.get("Retry-After", "")
                delay = min(60, int(retry)) if retry.isdigit() else 2 ** attempt
                exc.close()
                time.sleep(delay)
                continue
            # Do not retain error payloads: they may contain unexpected or sensitive content.
            status = exc.code
            exc.close()
            raise RuntimeError("HTTP " + str(status)) from None
        except (URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError("Network request failed after three attempts") from None
            time.sleep(2 ** attempt)


def check_payload(raw, mode, entity):
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object")
    if mode == "project_details":
        if data.get("slug") != "backstage" or not isinstance(data.get("repositories"), list):
            raise ValueError("Unexpected project details response")
    else:
        key = "contributors" if entity == "individual" else "organizations"
        pct = "contributorPercentage" if entity == "individual" else "organizationPercentage"
        if not isinstance(data.get("data"), list):
            raise ValueError("Expected geographical data array")
        for item in data["data"]:
            if not isinstance(item, dict) or not {"country", "countryCode", key, pct} <= item.keys():
                raise ValueError("Unexpected geographical response item")
    return data


def capture(row, url, params, token, raw_root, run_id, version):
    mode, entity = row["extraction_mode"], row["entity_type"]
    status, content_type, raw, duration = fetch(url, params, token)
    retrieved = utc()
    if status != 200:
        raise ValueError("Unexpected HTTP status " + str(status))
    if token.encode() in raw:
        raise ValueError("Response contains credential; not saved")
    check_payload(raw, mode, entity)
    period = "snapshot" if mode == "project_details" else "2021-11-01_2026-10-31"
    extraction_id = run_id + "-" + mode + "-" + entity
    directory = raw_root / row["resource_type"] / mode / entity / period / extraction_id
    directory.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema_version": "1.0", "extraction_id": extraction_id,
        "endpoint_id": row["endpoint_id"],
        "source": {"name": "lfx_insights", "api_version": row["api_version"], "base_url": BASE},
        "project": {"slug": "backstage", "project_id": row["project_id"]},
        "request": {"method": "GET", "url": url, "query_parameters": params,
                    "requested_period": None if mode == "project_details" else
                    {"start_date": START, "end_date": END}},
        "retrieval": {"retrieved_at_utc": retrieved, "http_status": status,
                      "content_type": content_type, "duration_ms": duration},
        "response": {"file": "response.json", "sha256": hashlib.sha256(raw).hexdigest(),
                     "size_bytes": len(raw), "format": "json", "is_complete": True,
                     "pagination": None if mode == "project_details" else
                     {"strategy": "none", "pages_retrieved": 1, "next_page_present": False,
                      "notes": "Unpaginated geographical endpoint."}},
        "provenance": {"script_version": version,
                       "repository_url": "https://github.com/fdegir/turkiye-in-global-oss",
                       "sanitized": False,
                       "notes": "Complete HTTP response; historical coverage and denominator not yet validated. API endDate is exclusive."}
    }
    (directory / "response.json").write_bytes(raw)
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=None,
                        help="Local data root (contains raw/); defaults to OSS_DATA_DIR or repo data/")
    parser.add_argument("--zip", action="store_true", help="Create a ZIP of this run's successful responses and manifests")
    args = parser.parse_args()
    data_dir = (args.data_dir or Path(os.environ.get("OSS_DATA_DIR") or ROOT / "data")).expanduser().resolve()
    raw_root = data_dir / "raw" / "lfx" / "backstage"
    try:
        planned = list(endpoints())
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    token = os.environ.get("LFX_API_TOKEN", "").strip()
    if not token:
        parser.error("LFX_API_TOKEN environment variable must be set")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    version = git_version()
    successes, failures = [], []
    for row, url, params in planned:
        label = row["endpoint_id"]
        try:
            directory = capture(row, url, params, token, raw_root, run_id, version)
            successes.append(directory)
            print("OK  " + label, flush=True)
        except (OSError, ValueError, RuntimeError) as exc:
            failures.append(label)
            print("FAILED  " + label + ": " + str(exc), file=sys.stderr, flush=True)
            if isinstance(exc, RuntimeError) and str(exc) in ("HTTP 401", "HTTP 403"):
                break
    print("Captured " + str(len(successes)) + "/7 responses in " + str(raw_root))
    if args.zip and successes:
        bundle = raw_root / (run_id + ".zip")
        with zipfile.ZipFile(bundle, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for directory in successes:
                for name in ("response.json", "manifest.json"):
                    path = directory / name
                    archive.write(path, path.relative_to(raw_root))
        print("Review bundle: " + str(bundle))
    if failures:
        print("Incomplete pilot; review failures and rerun. Previous captures are preserved.", file=sys.stderr)
    return 0 if len(successes) == 7 else 1


if __name__ == "__main__":
    sys.exit(main())
