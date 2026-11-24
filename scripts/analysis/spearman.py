#!/usr/bin/env python3
"""Rank correlations between country participation and economic WDI indicators."""
import argparse
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

INDICATORS=["population","gdp_bn","rd_gdp_pct"]

def analyse(observations, economics):
    d=observations.loc[(observations.scope=="all")&(observations.entity=="individual")
                       &(observations.status!="empty_coverage_unverified")].copy()
    for field in ("source_share","count"):
        d[field]=pd.to_numeric(d[field],errors="coerce")
    m=d.groupby("iso3").agg(mean_share=("source_share","mean"),occurrences=("count","sum")).reset_index()
    e=economics.copy()
    for c in INDICATORS+["rd_year"]:
        e[c]=pd.to_numeric(e[c],errors="coerce")
    m=m.merge(e,on="iso3",validate="one_to_one")
    m["per_million"]=m.occurrences*1_000_000/m.population
    rows=[]
    for measure in ("mean_share","occurrences","per_million"):
        for variable in INDICATORS:
            for since in ([None,2022,2023] if variable=="rd_gdp_pct" else [None]):
                subset=m if since is None else m[m.rd_year>=since]
                pair=subset[[measure,variable]].dropna()
                if len(pair)<3:continue
                result=spearmanr(pair[measure],pair[variable])
                rows.append(dict(measure=measure,variable=variable,rd_min_year=since,
                                 n=len(pair),rho=result.statistic,p=result.pvalue))
    return pd.DataFrame(rows)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--economics",type=Path,required=True,
                   help="CSV with iso3,population,gdp_bn,rd_gdp_pct,rd_year")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=analyse(pd.read_csv(a.input),pd.read_csv(a.economics))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.output,index=False)
    print(result.to_string(index=False))

if __name__=="__main__":
    main()

# Analysis input: local derived records; no raw research data committed.
