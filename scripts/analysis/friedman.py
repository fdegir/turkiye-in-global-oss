#!/usr/bin/env python3
"""Friedman test of countries ranked within the same selected projects."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare

DEFAULT = ["TUR","BRA","POL","ESP","KOR"]

def analyse(frame, countries=DEFAULT, metric="source_share"):
    data = frame.loc[(frame.scope=="all") & (frame.entity=="individual")
                     & (frame.iso3.isin(countries)) & (frame.status!="empty_coverage_unverified")].copy()
    data[metric] = pd.to_numeric(data[metric], errors="coerce")
    wide = data.pivot(index="project_id", columns="iso3", values=metric).reindex(columns=countries).dropna()
    n, k = wide.shape
    if n < 2 or k < 3:
        raise ValueError("Friedman needs at least two matched projects and three countries")
    result = friedmanchisquare(*(wide[c].to_numpy() for c in countries))
    return pd.DataFrame([dict(metric=metric, countries=";".join(countries),
                              n_projects=n, k=k, chi2=result.statistic, p=result.pvalue,
                              kendall_W=result.statistic/(n*(k-1)))])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--countries",nargs="+",default=DEFAULT)
    p.add_argument("--metric",choices=["source_share","known_share","count"],default="source_share")
    a=p.parse_args()
    result=analyse(pd.read_csv(a.input),a.countries,a.metric)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.output,index=False)
    print(result.to_string(index=False))

if __name__=="__main__":
    main()

# Analysis input: local derived records; no raw research data committed.
