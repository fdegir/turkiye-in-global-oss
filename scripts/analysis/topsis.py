#!/usr/bin/env python3
"""Exploratory TOPSIS: separate project mean share from per-capita participation."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

def closeness(matrix,weights):
    x=np.asarray(matrix,dtype=float)
    if not np.isfinite(x).all() or (x<0).any():
        raise ValueError("TOPSIS criteria must be finite nonnegative values")
    norm=np.sqrt((x*x).sum(axis=0))
    if (norm==0).any():
        raise ValueError("At least one TOPSIS criterion has zero variance/magnitude")
    v=(x/norm)*np.asarray(weights)
    best=v.max(axis=0)
    worst=v.min(axis=0)
    db=np.linalg.norm(v-best,axis=1)
    dw=np.linalg.norm(v-worst,axis=1)
    return np.divide(dw,db+dw,out=np.zeros_like(dw),where=(db+dw)>0)

def analyse(observations,economics):
    d=observations.loc[(observations.scope=="all")&(observations.status!="empty_coverage_unverified")].copy()
    d["source_share"]=pd.to_numeric(d.source_share,errors="coerce")
    d["count"]=pd.to_numeric(d["count"],errors="coerce")
    stats=d.groupby(["iso3","entity"]).agg(mean_share=("source_share","mean"),
               occurrences=("count","sum")).reset_index()
    means=stats.pivot(index="iso3",columns="entity",values="mean_share")
    counts=stats[stats.entity=="individual"].set_index("iso3").occurrences
    eco=economics.set_index("iso3")
    result=pd.DataFrame({"individual_mean_share":means["individual"],
                         "per_million":counts*1_000_000/pd.to_numeric(eco.population)})
    result["organisation_mean_share"]=means.get("organization")
    result=result.dropna(subset=["individual_mean_share","per_million"])
    criteria=["individual_mean_share","per_million"]
    result["topsis_primary"]=closeness(result[criteria],[0.5,0.5])
    result["rank_primary"]=result.topsis_primary.rank(method="min",ascending=False).astype(int)
    for name,weight in [("individual_heavy",[0.75,0.25]),("per_capita_heavy",[0.25,0.75])]:
        result["topsis_"+name]=closeness(result[criteria],weight)
        result["rank_"+name]=result["topsis_"+name].rank(method="min",ascending=False).astype(int)
    if result.organisation_mean_share.notna().all():
        result["topsis_equal_three"]=closeness(result[criteria+["organisation_mean_share"]],[1/3]*3)
        result["rank_equal_three"]=result.topsis_equal_three.rank(method="min",ascending=False).astype(int)
    return result.reset_index().sort_values("rank_primary")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--economics",type=Path,required=True,help="CSV with iso3,population")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=analyse(pd.read_csv(a.input),pd.read_csv(a.economics))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.output,index=False)
    print(result[["iso3","rank_primary","topsis_primary"]].to_string(index=False))

if __name__=="__main__":
    main()

# Analysis input: local derived records; no raw research data committed.
