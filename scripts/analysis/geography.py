#!/usr/bin/env python3
"""Compare source/known-geography shares without redistributing unknown records."""
import argparse
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

def analyse(observations):
    df=observations.loc[(observations.scope=="all")&(observations.entity=="individual")&
                        (observations.status!="empty_coverage_unverified")].copy()
    for c in ("source_share","known_share","unknown","denom","count"):
        df[c]=pd.to_numeric(df[c],errors="coerce")
    countries=df.groupby("iso3").agg(source_mean=("source_share","mean"),
                     known_mean=("known_share","mean")).reset_index()
    countries["rank_source"]=countries.source_mean.rank(ascending=False,method="min")
    countries["rank_known"]=countries.known_mean.rank(ascending=False,method="min")
    countries["rank_shift"]=countries.rank_known-countries.rank_source
    projects=df.drop_duplicates(["project_id"])[["project_id","category","unknown","denom"]].copy()
    projects["unknown_pct"]=100*projects.unknown/projects.denom
    corr=spearmanr(countries.rank_source,countries.rank_known,nan_policy="omit")
    return countries.sort_values("rank_source"),projects,dict(n_countries=len(countries),rho=float(corr.statistic),p=float(corr.pvalue))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    countries,projects,summary=analyse(pd.read_csv(a.input))
    a.output_dir.mkdir(parents=True,exist_ok=True)
    countries.to_csv(a.output_dir/"geography_country_ranks.csv",index=False)
    projects.to_csv(a.output_dir/"geography_project_missingness.csv",index=False)
    pd.DataFrame([summary]).to_csv(a.output_dir/"geography_rank_correlation.csv",index=False)
    print(summary)

if __name__=="__main__":
    main()
