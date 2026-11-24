#!/usr/bin/env python3
"""Reconstruct a reproducible project-country matrix from local LFX bulk ZIPs."""
import argparse
import csv
import io
import json
import zipfile
from pathlib import Path

import pycountry

COLUMNS = ("project_id", "slug", "category", "iso3", "scope", "entity",
           "count", "denom", "unknown", "source_share", "known_share", "status")


def iso3(code):
    if code == "XX" or not code:
        return "UNK"
    if code.upper() == "XK":
        return "XKX"
    c = pycountry.countries.get(alpha_2=code.upper())
    return c.alpha_3 if c else None


def extract(archives, countries):
    rows = []
    seen = set()
    for archive in archives:
        with zipfile.ZipFile(archive) as z:
            inventory_file = next(n for n in z.namelist() if n.startswith("bulk_runs/") and n.endswith("/projects.csv"))
            inventory = {r["lfx_project_slug"]: r for r in csv.DictReader(io.StringIO(z.read(inventory_file).decode("utf-8-sig")))}
            for path in z.namelist():
                parts = path.split("/")
                if len(parts) != 7 or parts[1] != "geographical_distribution" or not path.endswith("/response.json"):
                    continue
                slug, _, scope, entity, _, _, _ = parts
                key = (slug, scope, entity)
                if key in seen:
                    raise ValueError(f"Duplicate capture: {key}")
                seen.add(key)
                entries = json.loads(z.read(path)).get("data", [])
                source = {}
                for item in entries:
                    code = iso3(item.get("countryCode"))
                    if code is None:
                        raise ValueError(f"Unmapped country code {item.get('countryCode')}")
                    if code in source:
                        raise ValueError(f"Duplicate geographical bucket: {slug} {code}")
                    source[code] = int(item["contributors" if entity == "individual" else "organizations"])
                total = sum(source.values())
                unknown = source.get("UNK", 0)
                if not entries:
                    status = "empty_coverage_unverified"
                else:
                    status = "reported"
                project = inventory[slug]
                for country in countries:
                    count = source.get(country, 0)
                    state = "reported_bucket" if country in source else ("absent_reported_bucket" if entries else status)
                    rows.append(dict(project_id=project["project_id"], slug=slug, category=project["category"],
                                     iso3=country, scope=scope, entity=entity,
                                     count=count if entries else "", denom=total if entries else "",
                                     unknown=unknown if entries else "",
                                     source_share=100 * count / total if total else "",
                                     known_share=100 * count / (total - unknown) if total > unknown else "",
                                     status=state))
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archives", nargs="+", type=Path, required=True)
    p.add_argument("--countries", type=Path, default=Path("data/metadata/countries.csv"))
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    with args.countries.open(newline="", encoding="utf-8-sig") as f:
        countries = [r["country_code_iso3"] for r in csv.DictReader(f) if r["include_in_country_analysis"].upper() == "TRUE"]
    rows = extract(args.archives, countries)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} project-country-scope-entity rows written to {args.output}")


if __name__ == "__main__":
    main()
