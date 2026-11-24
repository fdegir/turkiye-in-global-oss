# Chapter 4 reproducible analysis

These scripts operate on **local files**. Do not commit LFX raw archives, contributor-level data, or the OpenSSF bulk snapshots to this repository.

## Setup
```bash
python -m pip install -r requirements-analysis.txt
python -m unittest discover -s tests
```

Generate the fully fictional Atlas Engine fixture (4 fabricated components; 5 countries):
```bash
python -m tests.fixtures.synthetic_atlas
```

The fixture is an example of the LFX-derived record structure, **not real measurements**.

## Prepare the actual research observations

Download the two archived LFX extraction ZIPs from your private research Drive folder and run:

```bash
python scripts/analysis/normalize_lfx.py \
  --archives "$OSS_DATA_DIR/bulk-20261115T002108Z-118fd4a7.zip" "$OSS_DATA_DIR/bulk-20261115T004136Z-1af7e1fe.zip" \
  --output "$OSS_DATA_DIR/processed/observations.csv"
```

All other scripts accept `--input "$OSS_DATA_DIR/processed/observations.csv"`.

## Independent analyses

```bash
python scripts/analysis/descriptive.py --input "$OSS_DATA_DIR/processed/observations.csv" --output-dir "$OSS_DATA_DIR/processed/descriptive"
python scripts/analysis/friedman.py --input "$OSS_DATA_DIR/processed/observations.csv" --output "$OSS_DATA_DIR/processed/friedman.csv"
python scripts/analysis/wilcoxon.py --input "$OSS_DATA_DIR/processed/observations.csv" --output "$OSS_DATA_DIR/processed/wilcoxon.csv"
python scripts/analysis/spearman.py --input "$OSS_DATA_DIR/processed/observations.csv" --economics data/metadata/wdi_reference.csv --output "$OSS_DATA_DIR/processed/spearman.csv"
python scripts/analysis/topsis.py --input "$OSS_DATA_DIR/processed/observations.csv" --economics data/metadata/wdi_reference.csv --output "$OSS_DATA_DIR/processed/topsis.csv"
python scripts/analysis/geography.py --input "$OSS_DATA_DIR/processed/observations.csv" --output-dir "$OSS_DATA_DIR/processed/geography"
python scripts/analysis/criticality.py --projects data/metadata/projects.csv --scores "$OSS_DATA_DIR/20250725_all.csv.gz" --observations "$OSS_DATA_DIR/processed/observations.csv" --output "$OSS_DATA_DIR/processed/criticality.csv"
python scripts/analysis/external_ranks.py --input "$OSS_DATA_DIR/external_paired_ranks.csv" --output "$OSS_DATA_DIR/processed/external_spearman.csv"
```

External rank input columns: `iso3,lfx_rank,external_rank`. Use the exact matched country set and source methodology; the complete G20 Wachs dataset is not supplied in the LFX archives.

## Fixed inputs and caveats

- `data/metadata/wdi_reference.csv` reproduces the World Bank inputs recorded in Chapter 3 (November 2026 extract). GDP is in billions of **current US dollars**; R&D observations span **2020–2024**, and per-country reference years are explicit.
- Original shares include unknown-country records; known-geography shares have smaller denominators. Proportional assignment is **not** an independent sensitivity test because it preserves within-project ranking.
- Code and collaboration scopes overlap. Do not sum them.
- Aggregated contributors count **project–person occurrences**, not unique people across projects.
- TOPSIS scores depend on the criteria and weights. Do not interpret them as direct digital-sovereignty measurements.
- OpenSSF scores are a **July 2025 repository-level snapshot**. Link scores by the exact, verified GitHub primary repository. Five non-GitHub or group-level references remain unmatched.
- The baseline samples were selected purposively; significance refers to the selected project portfolio.
- Scripts do not reproduce an external source whose raw input is absent. The Wachs/G20 comparison requires its own country-ranking source file.

Analysis PRs are layered on the foundation PR and target that branch for clean review. Merge the foundation first, then retarget each analysis PR to `main` as appropriate.
