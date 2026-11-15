#!/usr/bin/env python3
"""Local, exploratory All-scope unknown-attribution robustness analysis."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
# ISO 3166-1 alpha-3 to alpha-2 for the frozen 24-country sample.
ISO2 = dict(zip(
    "TUR BRA POL ESP KOR DEU FRA IND JPN USA CHN GBR CAN AUS ITA MEX IDN ARG ZAF RUS SAU NLD SWE FIN".split(),
    "TR BR PL ES KR DE FR IN JP US CN GB CA AU IT MX ID AR ZA RU SA NL SE FI".split(),
))

def calculate(archives, projects, countries):
    expected = {r["project_id"]: r["lfx_project_slug"] for r in projects}
    if len(expected) != 42 or len(projects) != 42:
        raise ValueError("Expected frozen 42-project inventory")
    selected = {ISO2[r["country_code_iso3"]]: r for r in countries}
    if len(selected) != 24 or len(countries) != 24:
        raise ValueError("Expected frozen 24-country inventory")
    captures = {}
    for path in archives:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if len(names) != len(set(names)) or z.testzip() is not None:
                raise ValueError("Invalid archive: " + str(path))
            for name in names:
                if not name.endswith("/response.json"):
                    continue
                raw = z.read(name)
                manifest = json.loads(z.read(name.rsplit("/", 1)[0] + "/manifest.json"))
                if (hashlib.sha256(raw).hexdigest() != manifest["response"]["sha256"]
                        or len(raw) != manifest["response"]["size_bytes"]
                        or manifest["retrieval"]["http_status"] != 200):
                    raise ValueError("Invalid response manifest: " + name)
                if "/geographical_distribution/all/" not in name:
                    continue
                entity = name.split("/")[3]
                if entity not in ("individual", "organization"):
                    raise ValueError("Unexpected entity")
                pid = manifest["project"]["project_id"]
                slug = manifest["project"]["slug"]
                if expected.get(pid) != slug or (pid, entity) in captures:
                    raise ValueError("Unexpected or duplicate project/entity: " + pid)
                params = manifest["request"]["query_parameters"]
                if params != {"startDate": "2021-11-01", "endDate": "2026-11-01",
                              "includeCodeContributions": True, "includeCollaborations": True}:
                    raise ValueError("Unexpected query parameters")
                route = "contributor" if entity == "individual" else "organization"
                url = "https://api.insights.linuxfoundation.org/v1-alpha/projects/" + slug + "/contributors/" + route + "-geographical-distribution"
                if manifest["request"]["url"] != url:
                    raise ValueError("Unexpected endpoint")
                key = "contributors" if entity == "individual" else "organizations"
                pct = "contributorPercentage" if entity == "individual" else "organizationPercentage"
                rows = json.loads(raw)["data"]
                if not rows:
                    raise ValueError("Empty All response: " + pid)
                by = {r["countryCode"]: r[key] for r in rows}
                if len(by) != len(rows) or any(type(v) is not int or v < 0 for v in by.values()):
                    raise ValueError("Invalid counts or duplicate countries: " + pid)
                total = sum(by.values())
                known = total - by.get("XX", 0)
                if known <= 0 or total <= 0:
                    raise ValueError("No known geography: " + pid)
                if any(abs(r[pct] - 100*r[key]/total) > 0.005000001 for r in rows):
                    raise ValueError("Percentage mismatch: " + pid)
                captures[pid, entity] = (by, total, known)
    if set(captures) != {(p, e) for p in expected for e in ("individual", "organization")}:
        raise ValueError("Incomplete frozen sample; require both research archives")
    output = []
    for entity in ("individual", "organization"):
        for code, country in selected.items():
            observed = original = conditional = scenario = 0
            for pid in expected:
                by, total, known = captures[pid, entity]
                c = by.get(code, 0)
                observed += c
                original += 100*c/total
                conditional += 100*c/known
                scenario += c*total/known
            output.append({"country_code": code, "country": country["country_name"],
                           "entity": entity, "observed_project_participations": observed,
                           "mean_all_geography_share_pct": original/42,
                           "mean_known_geography_share_pct": conditional/42,
                           "proportional_allocation_project_participations": scenario})
    return output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs=2, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="Local output CSV outside tracked data")
    args = parser.parse_args()
    with (ROOT / "data/metadata/projects.csv").open(newline="", encoding="utf-8") as f:
        projects = list(csv.DictReader(f))
    with (ROOT / "data/metadata/countries.csv").open(newline="", encoding="utf-8") as f:
        countries = list(csv.DictReader(f))
    rows = calculate(args.archives, projects, countries)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("Wrote", len(rows), "country/entity rows to", args.output)

if __name__ == "__main__":
    main()
