"""Synthetic atlas projects for exercising analysis scripts; no real LFX observations."""
import csv
import json
import zipfile
from pathlib import Path

COUNTRIES = ["TUR", "BRA", "POL", "ESP", "KOR"]
PROJECTS = ["atlas-core", "atlas-edge", "atlas-cloud", "atlas-security"]
# Source-like counts are entirely invented; the structure mirrors the LFX observations.
COUNTS = [
    [2, 8, 10, 7, 4],
    [3, 11, 9, 7, 5],
    [4, 10, 12, 8, 6],
    [3, 12, 13, 9, 7],
]


def write_csv(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["project_id", "slug", "category", "iso3", "scope", "entity",
            "count", "denom", "unknown", "source_share", "known_share", "status"]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        for i, name in enumerate(PROJECTS):
            denominator = sum(COUNTS[i]) + 10
            for iso, count in zip(COUNTRIES, COUNTS[i]):
                writer.writerow(dict(project_id=f"EX{i+1:03d}", slug=name,
                                 category="synthetic_atlas_engine", iso3=iso,
                                 scope="all", entity="individual", count=count,
                                 denom=denominator, unknown=10,
                                 source_share=100*count/denominator,
                                 known_share=100*count/sum(COUNTS[i]),
                                 status="reported_bucket"))
    return path


def write_archive(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    header = ("project_id,project_name,category,lfx_project_slug\n"
              "EX001,Atlas Engine,synthetic_atlas_engine,atlas-core\n")
    data = {"data": [
        {"country": "Unknown", "countryCode": "XX", "contributors": 10},
        {"country": "Türkiye", "countryCode": "TR", "contributors": 2},
        {"country": "Brazil", "countryCode": "BR", "contributors": 8},
    ]}
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("bulk_runs/example/projects.csv", header)
        z.writestr("atlas-core/geographical_distribution/all/individual/2021_2026/ex-1/response.json", json.dumps(data))
    return path


if __name__ == "__main__":
    write_csv("tests/fixtures/synthetic_atlas.csv")
    write_archive("tests/fixtures/synthetic_atlas.zip")
