#!/usr/bin/env python3
"""Capture all eight LFX endpoints for the frozen candidate inventory."""
import argparse
import csv
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
from uuid import uuid4
import zipfile

import extract_lfx_pilot as pilot

INVENTORY = pilot.ROOT / "data/metadata/projects.csv"

def projects():
    with INVENTORY.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 36:
        raise ValueError("Expected 36 candidates in projects.csv")
    for field in ("project_id", "lfx_project_slug"):
        values = [r[field] for r in rows]
        if len(set(values)) != 36 or any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", v) for v in values):
            raise ValueError("Missing, duplicate or invalid " + field + "; merge project mapping PR #20 first")
    return rows

def endpoints(project):
    slug = project["lfx_project_slug"]
    base = pilot.BASE + "/v1-alpha/projects/" + slug
    for mode, entity, suffix, params in [
        ("project_details", "project", "", {}),
        ("health_score", "project", "/overview/health-score", {}),
        *[(scope, entity, "/contributors/" + route + "-geographical-distribution",
           {"startDate": pilot.START, "endDate": pilot.END,
            "includeCodeContributions": code, "includeCollaborations": collab})
          for scope, (code, collab) in pilot.SCOPES.items()
          for entity, route in (("individual", "contributor"), ("organization", "organization"))]
    ]:
        row = {"endpoint_id": project["project_id"] + "_" + mode + "_" + entity,
               "project_id": project["project_id"], "project_slug": slug,
               "api_version": "v1-alpha", "resource_type": mode if entity == "project" else "geographical_distribution",
               "extraction_mode": mode, "entity_type": entity}
        yield row, base + suffix, params

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--zip", action="store_true", help="Archive this run's captures and summary")
    args = parser.parse_args()
    token = os.environ.get("LFX_API_TOKEN", "").strip()
    if not token:
        parser.error("LFX_API_TOKEN environment variable must be set")
    try:
        inventory = projects()
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    data = (args.data_dir or Path(os.environ.get("OSS_DATA_DIR") or pilot.ROOT / "data")).expanduser().resolve()
    root = data / "raw" / "lfx"
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    run_root = root / "bulk_runs" / run_id
    run_root.mkdir(parents=True, exist_ok=False)
    version = pilot.git_version()
    records = []
    captures = []
    stopped = False
    for project in inventory:
        slug = project["lfx_project_slug"]
        for row, url, params in endpoints(project):
            record = {"endpoint_id": row["endpoint_id"], "project_id": row["project_id"],
                      "slug": slug, "mode": row["extraction_mode"], "entity": row["entity_type"],
                      "status": "not_attempted" if stopped else "pending"}
            records.append(record)
            if stopped:
                continue
            try:
                directory = pilot.capture(row, url, params, token, root / slug, run_id + "-" + row["project_id"], version)
                captures.append(directory)
                record.update(status="captured", response_file=str((directory / "response.json").relative_to(root)))
                if row["entity_type"] != "project":
                    payload = json.loads((directory / "response.json").read_bytes())
                    record["geographical_buckets"] = len(payload["data"])
                elif row["extraction_mode"] == "project_details":
                    payload = json.loads((directory / "response.json").read_bytes())
                    expected = project.get("lfx_primary_repository_url") or project["primary_repository_url"]
                    urls = [r.get("url") for r in payload["repositories"] if isinstance(r, dict)]
                    record["expected_primary_repository"] = expected
                    record["primary_repository_present"] = expected.rstrip("/") in {u.rstrip("/") for u in urls if isinstance(u, str)}
                    record["repository_count"] = len(urls)
                print("OK  " + row["endpoint_id"], flush=True)
            except (OSError, ValueError, RuntimeError) as exc:
                record.update(status="failed", error_type=type(exc).__name__)
                if isinstance(exc, RuntimeError) and str(exc).startswith("HTTP "):
                    record["error"] = str(exc)
                print("FAILED  " + row["endpoint_id"] + ": " + record.get("error", type(exc).__name__), file=sys.stderr, flush=True)
                if isinstance(exc, RuntimeError) and str(exc) in ("HTTP 401", "HTTP 403"):
                    stopped = True
    summary = {"run_id": run_id, "script_version": version, "started_period": pilot.START,
               "exclusive_end_date": pilot.END, "project_count": len(inventory),
               "planned": len(records), "captured": len(captures),
               "records": records,
               "notes": "Capture success is not eligibility or historical coverage verification. Empty geography and absent primary mappings require review."}
    summary_file = run_root / "run_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    # Preserve the exact selection inventory used by this run; it is public metadata.
    inventory_file = run_root / "projects.csv"
    inventory_file.write_bytes(INVENTORY.read_bytes())
    print(f"Captured {len(captures)}/{len(records)} responses in {root}")
    print("Run summary: " + str(summary_file))
    if args.zip:
        bundle = root / ("bulk-" + run_id + ".zip")
        with zipfile.ZipFile(bundle, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in (summary_file, inventory_file):
                archive.write(path, path.relative_to(root))
            for directory in captures:
                for name in ("response.json", "manifest.json"):
                    path = directory / name
                    archive.write(path, path.relative_to(root))
        print("Review bundle: " + str(bundle))
    return 0 if len(captures) == len(records) and all(r["status"] == "captured" for r in records) else 1

if __name__ == "__main__":
    sys.exit(main())
