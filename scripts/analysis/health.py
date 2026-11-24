#!/usr/bin/env python3
"""Analyse LFX project Health Score snapshots with explicit coverage handling.

Primary analysis requires coveredCategoryCount==3 and healthMaxScore==100.
Health is a project attribute, not a country attribute. A country-level
health-weighted participation measure is a *sensitivity construct* and does
not directly measure national security, sovereignty or project governance.
"""
import argparse
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def read_health(archives):
    rows = []
    for archive in archives:
        with zipfile.ZipFile(archive) as z:
            for path in z.namelist():
                if "/health_score/" not in path or not path.endswith("/response.json"):
                    continue
                slug = path.split("/")[0]
                obj = json.loads(z.read(path))
                rows.append(dict(slug=slug, score=obj.get("score"),
                                 health_max=obj.get("healthMaxScore"),
                                 covered_categories=obj.get("coveredCategoryCount"),
                                 maintainer=obj.get("maintainerHealthScore"),
                                 security_supply_chain=obj.get("securitySupplyChainScore"),
                                 development_activity=obj.get("developmentActivityScore")))
    out = pd.DataFrame(rows)
    if out.slug.duplicated().any():
        raise ValueError("Repeated health source for the same project")
    for field in out.columns.difference(["slug"]):
        out[field] = pd.to_numeric(out[field], errors="coerce")
    out["coverage"] = np.select(
        [out.score.isna(),
         out.score.notna() & out.covered_categories.eq(3) & out.health_max.eq(100)],
        ["missing", "full"], default="partial")
    return out


def analyse(observations, health, focal="TUR"):
    # Accept source-compatible normalized observations.
    d = observations.loc[(observations.scope == "all")
                         & (observations.entity == "individual")
                         & (observations.status != "empty_coverage_unverified")].copy()
    if d.duplicated(["slug", "iso3"]).any():
        raise ValueError("Duplicate project-country observation")
    d["source_share"] = pd.to_numeric(d["source_share"], errors="raise")
    h = health[health.coverage == "full"][["slug", "score"]].copy()
    if h.empty:
        raise ValueError("No fully covered health scores")
    joined = d.merge(h, on="slug", how="inner", validate="many_to_one")
    if joined.slug.nunique() != len(h):
        raise ValueError("Fully covered projects missing from country observation table")
    if joined.groupby("iso3").slug.nunique().nunique() != 1:
        raise ValueError("Different available project sets across countries")
    # Same set of 3-category, /100 projects is used for weighted and unweighted.
    country = joined.groupby("iso3").apply(
        lambda g: pd.Series({
            "mean_share_full_projects": g.source_share.mean(),
            "health_weighted_share": np.average(g.source_share, weights=g.score / 100),
            "n_projects": len(g)}), include_groups=False).reset_index()
    for key in ("mean_share_full_projects", "health_weighted_share"):
        country["rank_" + key] = country[key].rank(ascending=False, method="min").astype(int)
    country["rank_change"] = (country.rank_health_weighted_share
                              - country.rank_mean_share_full_projects)
    focal_project = joined[joined.iso3 == focal]
    test = spearmanr(focal_project.score, focal_project.source_share)
    rank_correlation = spearmanr(country.rank_mean_share_full_projects,
                                country.rank_health_weighted_share)
    summary = pd.DataFrame([dict(total_projects=health.slug.nunique(),
        score_available=int(health.score.notna().sum()),
        full_coverage=int((health.coverage == "full").sum()),
        partial_coverage=int((health.coverage == "partial").sum()),
        missing_score=int((health.coverage == "missing").sum()),
        focal=focal, focal_health_share_rho=test.statistic,
        focal_health_share_p=test.pvalue, focal_n=len(focal_project),
        country_rank_rho=rank_correlation.statistic,
        country_rank_p=rank_correlation.pvalue)])
    return country.sort_values("rank_health_weighted_share"), summary


def add_health_weighted_topsis(country, economic, observations):
    """Exploratory health-augmented TOPSIS; never replace the primary model.

    Avoid cross-project identity confounding: indicators are derived at country
    level from documented project-level measures. Their possible redundancy
    must be reported and interpreted.
    """
    d = observations.loc[(observations.scope == "all")
                         & (observations.entity == "individual")
                         & (observations.status != "empty_coverage_unverified")].copy()
    d["count"] = pd.to_numeric(d["count"], errors="raise")
    d["source_share"] = pd.to_numeric(d["source_share"], errors="raise")
    totals = d.groupby("iso3").agg(
        original_mean_share=("source_share", "mean"),
        contributor_project_occurrences=("count", "sum"))
    e = economic.set_index("iso3")
    all_ = country.set_index("iso3").join(totals).join(e[["population"]])
    all_["per_million"] = all_.contributor_project_occurrences * 1_000_000 / all_.population
    criteria = ["original_mean_share", "per_million", "health_weighted_share"]
    if all_[criteria].isna().any().any():
        raise ValueError("Incomplete health-augmented TOPSIS criterion matrix")
    def closeness(keys):
        x = all_[keys].to_numpy(dtype=float)
        unit = x / np.sqrt(np.square(x).sum(axis=0))
        v = unit / len(keys)
        best, worst = v.max(axis=0), v.min(axis=0)
        db, dw = np.linalg.norm(v-best,axis=1),np.linalg.norm(v-worst,axis=1)
        return dw/(db+dw)
    all_["primary_closeness"] = closeness(criteria[:2])
    all_["augmented_closeness"] = closeness(criteria)
    for col in ("primary", "augmented"):
        all_["rank_" + col] = all_[col + "_closeness"].rank(
            ascending=False, method="min").astype(int)
    return all_.reset_index()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archives", nargs="+", type=Path, required=True)
    p.add_argument("--observations", type=Path, required=True)
    p.add_argument("--economic", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--focal", default="TUR")
    a = p.parse_args()
    health = read_health(a.archives)
    observations = pd.read_csv(a.observations)
    ranking, summary = analyse(observations, health, focal=a.focal)
    topsis = add_health_weighted_topsis(ranking, pd.read_csv(a.economic), observations)
    a.output_dir.mkdir(parents=True, exist_ok=True)
    health.to_csv(a.output_dir / "project_health_coverage.csv", index=False)
    ranking.to_csv(a.output_dir / "health_weighted_participation.csv", index=False)
    summary.to_csv(a.output_dir / "health_analysis_summary.csv", index=False)
    topsis.to_csv(a.output_dir / "health_topsis_sensitivity.csv", index=False)
    print(summary.to_string(index=False))
    print(f"{a.focal} ranks: ", topsis.loc[topsis.iso3 == a.focal,
                                       ["rank_primary", "rank_augmented"]].to_dict("records"))


if __name__ == "__main__":
    main()
