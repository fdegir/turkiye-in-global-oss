#!/usr/bin/env python3
"""Independent G20 ranking comparison with Wachs et al. (2022) GitHub geography.

Source: johanneswachs/OSS_Geography_Data/data/world_countries_2021.csv
Licensed under the source repository's MIT license.
"""
import argparse
from pathlib import Path
import pandas as pd
import pycountry
from scipy.stats import spearmanr

# Exactly 19 country members; EU and AU are supranational members and omitted.
G20 = ("ARG", "AUS", "BRA", "CAN", "CHN", "FRA", "DEU", "IND", "IDN",
       "ITA", "JPN", "MEX", "RUS", "SAU", "ZAF", "KOR", "TUR", "GBR", "USA")


def analyse(observations, external, iso3_codes=G20, external_measure="count_total_contributors"):
    """Return matched ranking table and Spearman summary, excluding no G20 countries."""
    f = observations.loc[(observations.scope == "all")
                         & (observations.entity == "individual")
                         & (observations.iso3.isin(iso3_codes))
                         & (observations.status != "empty_coverage_unverified")].copy()
    f["count"] = pd.to_numeric(f["count"], errors="raise")
    totals = f.groupby("iso3", as_index=False)["count"].sum()
    ext = external.copy()
    if external_measure not in ext:
        raise ValueError(f"Missing external measure {external_measure}")
    # Wachs dataset uses ISO alpha-2 codes. Convert by ISO-3166 mapping.
    def to_iso3(iso2):
        try:
            return pycountry.countries.get(alpha_2=str(iso2).upper()).alpha_3
        except AttributeError:
            return None
    ext["iso3"] = ext["iso2"].map(to_iso3)
    ext = ext.loc[ext.iso3.isin(iso3_codes), ["iso3", external_measure]].copy()
    if ext.iso3.duplicated().any():
        raise ValueError("Duplicate country in external source")
    ext[external_measure] = pd.to_numeric(ext[external_measure], errors="raise")
    pairs = totals.merge(ext, on="iso3", how="inner", validate="one_to_one")
    expected = set(iso3_codes)
    if set(pairs.iso3) != expected:
        raise ValueError(f"Unmatched countries: {sorted(expected - set(pairs.iso3))}")
    pairs = pairs.rename(columns={"count": "lfx_project_occurrences",
                                  external_measure: "wachs_contributors"})
    pairs["lfx_rank"] = pairs.lfx_project_occurrences.rank(ascending=False, method="min").astype(int)
    pairs["wachs_rank"] = pairs.wachs_contributors.rank(ascending=False, method="min").astype(int)
    rho = spearmanr(pairs.lfx_rank, pairs.wachs_rank)
    results = pd.DataFrame([dict(n=len(pairs),rho=float(rho.statistic),p=float(rho.pvalue),
                                 external_measure=external_measure)])
    return pairs.sort_values("lfx_rank"), results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--observations", type=Path, required=True,
                   help="Local CSV from normalize_lfx.py")
    p.add_argument("--external", type=Path, required=True,
                   help="Downloaded Wachs world_countries_2021.csv")
    p.add_argument("--external-measure", default="count_total_contributors",
                   choices=["count_total_contributors", "count_github"])
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    ranks, summary = analyse(pd.read_csv(args.observations), pd.read_csv(args.external),
                             external_measure=args.external_measure)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    ranks.to_csv(args.output_dir / "g20_country_ranks.csv", index=False)
    summary.to_csv(args.output_dir / "g20_spearman.csv", index=False)
    print(summary.to_string(index=False))
    print(ranks.to_string(index=False))


if __name__ == "__main__":
    main()
