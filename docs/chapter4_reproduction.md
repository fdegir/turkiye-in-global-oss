# Reproducible Chapter 4 analyses

All scripts accept an explicitly supplied local data path. Raw LFX API archives and the OpenSSF bulk datasets are **not** committed.

Install: `python -m pip install pandas numpy scipy pycountry matplotlib`.

Start by normalising the 2 local LFX ZIP archives:
```bash
python scripts/analysis/normalize_lfx.py --archives /secure/bulk-20261115T002108Z-118fd4a7.zip /secure/bulk-20261115T004136Z-1af7e1fe.zip --output /secure/derived/observations.csv
```

The synthetic **Atlas Engine** fixture is entirely fabricated (not a real LFX project or contributor count). Generate with `python -m tests.fixtures.synthetic_atlas` and run `python -m unittest discover -s tests`. The synthetic data support smoke tests, not research results.

Data status: an absent country bucket in a nonempty LFX response is a recorded zero; an empty response is missing. Every total includes Unknown. Individuals and organisations, and all/code/collaboration scopes, remain separate. Summing across projects counts occurrences rather than distinct individuals.

Analysis branches are independent changes proposed atop the normalisation foundation. Merge the foundation first; retarget individual analysis PRs to main afterward.