#!/usr/bin/env python3
"""Check local LFX bulk archives, manifests and reconciled observation matrix.

This validates stored-response integrity and internal arithmetic, NOT the
historical completeness or accuracy of geography attribution.
"""
import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path

import pandas as pd


def audit(archives, observations=None):
    counts=Counter()
    issues=[]
    projects=set()
    for archive in archives:
        with zipfile.ZipFile(archive) as z:
            names=set(z.namelist())
            manifest_files=sorted(n for n in names if n.endswith("/manifest.json"))
            for path in manifest_files:
                counts["manifests"]+=1
                meta=json.loads(z.read(path))
                response_path=path[:-len("manifest.json")]+"response.json"
                if response_path not in names:
                    issues.append(f"{path}: missing response")
                    continue
                raw=z.read(response_path)
                counts["responses"]+=1
                expected=meta.get("response",{})
                if hashlib.sha256(raw).hexdigest()!=expected.get("sha256"):
                    issues.append(f"{path}: SHA-256 mismatch")
                if len(raw)!=expected.get("size_bytes"):
                    issues.append(f"{path}: byte-size mismatch")
                if meta.get("retrieval",{}).get("http_status")!=200:
                    issues.append(f"{path}: non-200 response")
                project=meta.get("project",{})
                projects.add(project.get("slug"))
                if "/geographical_distribution/" in response_path:
                    counts["geographical_responses"]+=1
                    data=json.loads(raw).get("data",[])
                    if not data:
                        counts["empty_geography"]+=1
                    entity=response_path.split("/")[3]
                    measure="contributors" if entity=="individual" else "organizations"
                    rows={}
                    for item in data:
                        country=item["countryCode"]
                        if country in rows:
                            issues.append(f"{path}: duplicate country {country}")
                        if measure not in item:
                            issues.append(f"{path}: missing {measure}")
                        rows[country]=item.get(measure,0)
                    if any(not isinstance(v,int) or v<0 for v in rows.values()):
                        issues.append(f"{path}: nonnegative integer count violation")
    counts["projects"]=len(projects)
    if observations is not None:
        df=pd.read_csv(observations)
        counts["normalised_rows"]=len(df)
        if df.duplicated(["project_id","iso3","scope","entity"]).any():
            issues.append("Duplicate normalized project-country-scope-entity")
        for _,g in df.groupby(["project_id","scope","entity"]):
            if g.status.eq("empty_coverage_unverified").all():
                if g["count"].notna().any():
                    issues.append("Empty response must be missing, not zero")
                continue
            if g[["count","denom","unknown"]].isna().any().any():
                issues.append("Unexpected null in nonempty response")
                continue
            if g.denom.nunique()!=1 or g.unknown.nunique()!=1:
                issues.append("Inconsistent project-scope denominators")
            if g["count"].sum() > g.denom.iloc[0]-g.unknown.iloc[0]+1e-9:
                issues.append("Selected-country counts exceed globally known total")
    return {"counts":dict(counts),"issues":issues}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archives",nargs="+",type=Path,required=True)
    p.add_argument("--observations",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.archives,a.observations)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    if result["issues"]:
        raise SystemExit("Audit detected errors")


if __name__=="__main__":
    main()
