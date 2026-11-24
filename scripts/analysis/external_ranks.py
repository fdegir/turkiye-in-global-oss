#!/usr/bin/env python3
"""Reproduce rank concordance using explicit matched LFX and external country ranks."""
import argparse
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

def analyse(frame):
    required={"iso3","lfx_rank","external_rank"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Missing columns {required-set(frame.columns)}")
    pair=frame[["iso3","lfx_rank","external_rank"]].dropna().copy()
    if pair.iso3.duplicated().any():
        raise ValueError("Each country may appear at most once")
    if len(pair)<3:
        raise ValueError("At least 3 matched countries required")
    pair[["lfx_rank","external_rank"]]=pair[["lfx_rank","external_rank"]].apply(pd.to_numeric)
    test=spearmanr(pair.lfx_rank,pair.external_rank)
    return pd.DataFrame([{"n":len(pair),"rho":test.statistic,"p":test.pvalue}])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True,help="CSV: iso3,lfx_rank,external_rank")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=analyse(pd.read_csv(a.input))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.output,index=False)
    print(result.to_string(index=False))

if __name__=="__main__":
    main()
