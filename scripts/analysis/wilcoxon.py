#!/usr/bin/env python3
"""Paired project-wise Wilcoxon signed-rank tests; Holm-adjusted p values."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

PEERS=["BRA","POL","ESP","KOR"]

def holm(pvalues):
    order=np.argsort(pvalues)
    out=np.zeros(len(pvalues))
    maximum=0.0
    for i,idx in enumerate(order):
        maximum=max(maximum,(len(pvalues)-i)*pvalues[idx])
        out[idx]=min(1.0,maximum)
    return out

def analyse(frame, focal="TUR", peers=PEERS, metric="source_share"):
    df=frame.loc[(frame.scope=="all") & (frame.entity=="individual")
                & (frame.iso3.isin([focal]+peers)) & (frame.status!="empty_coverage_unverified")].copy()
    df[metric]=pd.to_numeric(df[metric],errors="coerce")
    wide=df.pivot(index="project_id",columns="iso3",values=metric)
    results=[]
    for peer in peers:
        paired=wide[[focal,peer]].dropna()
        diff=paired[focal]-paired[peer]
        if len(diff)<2:
            raise ValueError(f"Insufficient matched projects for {peer}")
        test=wilcoxon(diff,zero_method="wilcox",alternative="two-sided",method="auto")
        results.append(dict(comparison=f"{focal}-{peer}",metric=metric,n_pairs=len(diff),
                            positive=int((diff>0).sum()),negative=int((diff<0).sum()),
                            ties=int((diff==0).sum()),median_difference=float(diff.median()),
                            statistic=float(test.statistic),p=float(test.pvalue)))
    for row,p in zip(results,holm([r["p"] for r in results])):
        row["holm_p"]=float(p)
    return pd.DataFrame(results)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--focal",default="TUR")
    p.add_argument("--peers",nargs="+",default=PEERS)
    p.add_argument("--metric",default="source_share",choices=["source_share","known_share","count"])
    a=p.parse_args()
    result=analyse(pd.read_csv(a.input),a.focal,a.peers,a.metric)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.output,index=False)
    print(result.to_string(index=False))

if __name__=="__main__":
    main()
