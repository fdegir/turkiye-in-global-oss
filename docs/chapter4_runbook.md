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
python scripts/analysis/external_ranks.py --observations "$OSS_DATA_DIR/processed/observations.csv" --external "$OSS_DATA_DIR/world_countries_2021.csv" --output-dir "$OSS_DATA_DIR/processed/external"
python scripts/analysis/health.py --archives "$OSS_DATA_DIR/bulk-20261115T002108Z-118fd4a7.zip" "$OSS_DATA_DIR/bulk-20261115T004136Z-1af7e1fe.zip" --observations "$OSS_DATA_DIR/processed/observations.csv" --economic data/metadata/wdi_reference.csv --output-dir "$OSS_DATA_DIR/processed/health"
```

Download Wachs et al.'s source table from [OSS_Geography_Data/data/world_countries_2021.csv](https://github.com/johanneswachs/OSS_Geography_Data/blob/main/data/world_countries_2021.csv), preserving its filename. The external script joins all 19 individual G20 members and prints the exact rank table and Spearman coefficient. It uses `count_total_contributors` by default and accepts `--external-measure count_github` for a sensitivity check.

## Fixed inputs and caveats

- `data/metadata/wdi_reference.csv` reproduces the World Bank inputs recorded in Chapter 3 (November 2026 extract). GDP is in billions of **current US dollars**; R&D observations span **2020–2024**, and per-country reference years are explicit.
- Original shares include unknown-country records; known-geography shares have smaller denominators. Proportional assignment is **not** an independent sensitivity test because it preserves within-project ranking. `geography.py` additionally evaluates explicit non-proportional odds multipliers and identification bounds. These are assumptions, **not imputed home countries**.
- Code and collaboration scopes overlap. Do not sum them.
- Aggregated contributors count **project–person occurrences**, not unique people across projects.
- TOPSIS scores depend on the criteria and weights. Do not interpret them as direct digital-sovereignty measurements.
- OpenSSF scores are a **July 2025 repository-level snapshot**. Link scores by the exact, verified GitHub primary repository. Five non-GitHub or group-level references remain unmatched.
- LFX Health Score is a project-level snapshot. The default health analysis uses only complete 3-category/100-point records (40 projects), excluding OpenStack's partial 55/65 score and the unavailable Linux Kernel total. Health-weighted country participation and the augmented TOPSIS model are **sensitivity analyses**, not direct measurements of country-level project health.
- The baseline samples were selected purposively; significance refers to the selected project portfolio.
- External Wachs data must be downloaded from the cited research repository. Do not substitute previously transcribed country ranks.

PR #26 (normalisation foundation) has been merged. All remaining analysis PRs target `main` and can be reviewed individually; merge only after their CI checks and scientific review pass.
