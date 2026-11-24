#!/usr/bin/env python3
"""Stream the official OpenSSF score CSV.gz and join exact primary GitHub URLs."""
import argparse
import csv
import gzip
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

def canonical(url):
    value=str(url or "").strip().lower().rstrip("/")
    if value.endswith(".git"):
        value=value[:-4]
    return value if value.startswith("https://github.com/") else None

def analyse(projects,score_file,observations=None):
    projects=projects.copy()
    projects["matched_url"]=projects.primary_repository_url.map(canonical)
    if projects.matched_url.dropna().duplicated().any():
        raise ValueError("Two projects map to the same primary repository")
    wanted=set(projects.matched_url.dropna())
    found={}
    with gzip.open(score_file,"rt",newline="",encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key=canonical(row["repo.url"])
            if key in wanted:
                if key in found:
                    raise ValueError(f"Duplicate score repository: {key}")
                found[key]=(float(row["default_score"]),row["collection_date"])
    out=projects.merge(pd.DataFrame([{"matched_url":k,"openssf_criticality":v[0],
             "openssf_collected_at":v[1]} for k,v in found.items()]),
             on="matched_url",how="left",validate="one_to_one")
    out["match_status"]=out.apply(lambda r: "matched" if pd.notna(r.openssf_criticality)
             else ("non_github_primary" if pd.isna(r.matched_url) else "not_found"),axis=1)
    if observations is not None:
        obs=observations.loc[(observations.iso3=="TUR")&(observations.scope=="all")&
            (observations.entity=="individual"),["project_id","source_share"]].copy()
        obs.source_share=pd.to_numeric(obs.source_share,errors="coerce")
        out=out.merge(obs,on="project_id",how="left",validate="one_to_one")
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--projects",type=Path,default=Path("data/metadata/projects.csv"))
    p.add_argument("--scores",type=Path,required=True,help="Local 20250725_all.csv.gz, never commit raw dataset")
    p.add_argument("--observations",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    obs=pd.read_csv(a.observations) if a.observations else None
    result=analyse(pd.read_csv(a.projects),a.scores,obs)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.output,index=False)
    print(result.match_status.value_counts().to_string())
    if obs is not None:
        pair=result[["openssf_criticality","source_share"]].dropna()
        if len(pair)>=3:
            s=spearmanr(pair.openssf_criticality,pair.source_share)
            print(f"Türkiye share vs criticality: n={len(pair)}, rho={s.statistic:.4f}, p={s.pvalue:.4g}")

if __name__=="__main__":
    main()
