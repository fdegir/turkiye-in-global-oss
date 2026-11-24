#!/usr/bin/env python3
"""Quantify rank sensitivity to non-proportional Unknown-country allocation.

These are counterfactual stress scenarios, not estimates of true contributor locations.
The 24-country sample is NOT the entire world; all unknown records are allocated
across the globally known buckets, with a focal-country multiplier.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def _matrix(data, scope="all", entity="individual"):
    sub = data.loc[(data.scope == scope) & (data.entity == entity)
                   & (data.status != "empty_coverage_unverified")].copy()
    for key in ("count", "denom", "unknown"):
        sub[key] = pd.to_numeric(sub[key], errors="coerce")
    if sub[["count", "denom", "unknown"]].isna().any().any():
        raise ValueError("Missing counts for included observations")
    if sub.duplicated(["project_id", "iso3"]).any():
        raise ValueError("Duplicate project-country pair")
    matrix = sub.pivot(index="project_id", columns="iso3", values="count")
    if matrix.isna().any().any():
        raise ValueError("Incomplete country-project matrix")
    totals = sub.drop_duplicates("project_id").set_index("project_id")
    totals = totals.loc[matrix.index, ["denom", "unknown"]]
    known = totals.denom - totals.unknown
    if (known <= 0).any() or (totals.unknown < 0).any():
        raise ValueError("Project must have a nonzero known-location denominator")
    if (matrix.sum(axis=1) > known + 1e-9).any():
        raise ValueError("Selected countries cannot exceed globally known records")
    return matrix.astype(float), totals.astype(float)


def evaluate(data, focal="TUR", multipliers=(0, 0.25, 0.5, 1, 2, 5, 10),
             scope="all", entity="individual"):
    counts, totals = _matrix(data, scope, entity)
    if focal not in counts:
        raise ValueError(f"Missing focal country {focal}")
    N, U = totals.denom, totals.unknown
    K = N - U
    base = counts.div(N, axis=0).mul(100).mean().rename("original_mean_share")
    ranks = []
    summary = []
    for m in multipliers:
        if m < 0 or not np.isfinite(m):
            raise ValueError("Multipliers must be finite nonnegative")
        # Unknown-country observations are allocated across ALL known-country
        # buckets, not merely the selected comparison countries.
        # Reweight the focal country by m and every other known country by 1.
        # If f_c is its observed fraction of known records, its share of
        # allocated Unknown is m*f_c / (1 + (m-1)*f_c).
        den = K + (m-1) * counts[focal]
        if (den <= 0).any():
            raise ValueError("Scenario has a zero effective weight denominator")
        result = counts.div(den, axis=0).mul(U, axis=0) + counts
        result[focal] = counts[focal] + U * (m * counts[focal] / den)
        # Remaining unselected-country buckets account for the unrepresented
        # portion; their allocations are never spuriously assigned to sample.
        mean_share = result.div(N, axis=0).mul(100).mean()
        order = mean_share.rank(method="min", ascending=False).astype(int)
        baseline_order = base.rank(method="min", ascending=False).astype(int)
        rho = spearmanr(baseline_order, order).statistic
        tag = f"{m:g}"
        for iso, value in mean_share.items():
            ranks.append(dict(multiplier=m, iso3=iso, mean_share_pct=value,
                              rank=int(order[iso]), rank_original=int(baseline_order[iso]),
                              rank_shift=int(order[iso] - baseline_order[iso])))
        summary.append(dict(multiplier=m, focal=focal,
                            focal_mean_share_pct=float(mean_share[focal]),
                            focal_rank=int(order[focal]), total_countries=len(order),
                            rank_spearman=float(rho), unknown_records=int(U.sum()),
                            total_records=int(N.sum())))
    return pd.DataFrame(summary), pd.DataFrame(ranks)


def bounded_focal_stress(data, focal="TUR", fractions=(0, 0.001, 0.005, 0.01, 0.02, 0.05, 1)):
    """Extra extreme stress: assign a chosen fraction of Unknown to focal country.

    Unassigned Unknown remains Unknown. Other countries keep observed counts.
    It is not a demographic estimator; 100% is an identification bound.
    """
    c, t = _matrix(data)
    if focal not in c:
        raise ValueError(f"Missing focal country {focal}")
    results = []
    for f in fractions:
        if not (0 <= f <= 1):
            raise ValueError("Stress fractions must be in [0, 1]")
        candidate = c.copy()
        candidate[focal] += f * t.unknown
        means = candidate.div(t.denom, axis=0).mul(100).mean()
        results.append(dict(fraction_unknown_allocated_to_focal=f,
                            focal_rank=int(means.rank(ascending=False, method="min")[focal]),
                            focal_mean_share_pct=float(means[focal])))
    return pd.DataFrame(results)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--focal", default="TUR")
    p.add_argument("--multipliers", nargs="+", type=float, default=[0, 0.25, 0.5, 1, 2, 5, 10])
    args = p.parse_args()
    data = pd.read_csv(args.input)
    summary, ranks = evaluate(data, focal=args.focal, multipliers=args.multipliers)
    stress = bounded_focal_stress(data, args.focal)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output_dir / "geography_multiplier_scenarios.csv", index=False)
    ranks.to_csv(args.output_dir / "geography_country_rank_scenarios.csv", index=False)
    stress.to_csv(args.output_dir / "geography_focal_stress_bounds.csv", index=False)
    print(summary.to_string(index=False))
    print("These are counterfactual scenarios, NOT inferred home countries.")


if __name__ == "__main__":
    main()
