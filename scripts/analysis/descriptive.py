#!/usr/bin/env python3
"""Calculate country, category and coverage summaries from normalised LFX CSV."""
import argparse
from pathlib import Path
import pandas as pd

def analyse(frame, scope="all", entity="individual"):
    df = frame.loc[(frame.scope == scope) & (frame.entity == entity) & (frame.status != "empty_coverage_unverified")].copy()
    for c in ("count", "source_share", "known_share", "unknown", "denom"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["count", "source_share"])
    group = lambda keys: (df.groupby(keys, as_index=False)
        .agg(projects=("project_id", "nunique"), occurrences=("count", "sum"),
             mean_share=("source_share", "mean"), median_share=("source_share", "median"),
             known_mean_share=("known_share", "mean"), std_share=("source_share", "std")))
    return group(["iso3"]), group(["category", "iso3"])

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--scope", default="all")
    p.add_argument("--entity", default="individual")
    a = p.parse_args()
    country, category = analyse(pd.read_csv(a.input), a.scope, a.entity)
    a.output_dir.mkdir(parents=True, exist_ok=True)
    country.to_csv(a.output_dir/"country_summary.csv", index=False)
    category.to_csv(a.output_dir/"category_summary.csv", index=False)
    print(f"{len(country)} countries, {len(category)} country-category combinations")

if __name__ == "__main__":
    main()

# Analysis input: local derived records; no raw research data committed.
