# Chapter 4 end-to-end reproducibility audit

**Date:** 24 November 2026  
**Scope:** 42 frozen LFX projects, 24 countries, 1 November 2021–31 October 2026  
**Outcome:** **PASS after normaliser fix in PR #36**. The already-merged normaliser in `main` fails on real organisation records and must be corrected before a clean rerun is possible.

## Inputs and integrity

| Input | SHA-256 |
|---|---|
| `bulk-20261115T002108Z-118fd4a7.zip` | `fe76029a37edbaaa409add8e11fde02970d2d1e677075c40e3dc686bc21a423f` |
| `bulk-20261115T004136Z-1af7e1fe.zip` | `081af2c5a9409cf78bb1f6d915789136264e7a602ef388a09f58c3d1d57ac24e` |

All **336** response/manifest pairs (288 + 48) pass nested `response.sha256` and `response.size_bytes` verification, and manifest-reported HTTP status is 200. The archives contain **42** projects and **252** geographical responses, of which **19** are empty. The normalised result has **6,048** project × country × scope × entity rows: **5,592** source-nonempty rows and **456** explicitly missing rows (not zeros).

A field mismatch was discovered by running the actual archives: individual entries contain `contributors`, but organisation entries contain `organizations`. The merged script expected `contributors` universally and raised `KeyError`. **PR #36** fixes the selector and adds a regression test for the organisation schema. Synthetic tests alone had not detected the mismatch.

The fixed script's 5,592 nonempty rows exactly match the independently extracted earlier data: no differences in `count`, `denom`, `unknown`, `source_share`, or `known_share`. The 456 additional records retain the empty-scope/missing distinction.

## Independent rerun of the scripts

Run each CLI from the checked-out repo with the two private ZIPs and the locally retained OpenSSF `20250725_all.csv.gz`, using the documented economic table `data/metadata/wdi_reference.csv` and the public Wachs et al. country file. The full set of 16 synthetic tests also passes in the local audit environment.

| Analysis | Reproduced result |
|---|---|
| Friedman, 5 peer countries | χ²(4) = 92.86618, n = 42, p = 3.2393×10⁻¹⁹; Kendall's W = 0.552775 |
| Wilcoxon vs Brazil | median Δ = −0.539359 percentage points; Holm p = 5.6272×10⁻⁸ |
| Wilcoxon vs Poland | median Δ = −0.662133; Holm p = 6.0027×10⁻¹¹ |
| Wilcoxon vs Spain | median Δ = −0.482197; Holm p = 3.7721×10⁻⁹ |
| Wilcoxon vs South Korea | median Δ = −0.202131; Holm p = 1.5040×10⁻⁵ |
| Spearman, mean individual share vs GDP | ρ = 0.720, n = 24, p = 0.000073 |
| Spearman, mean individual share vs R&D/GDP | ρ = 0.502609, n = 24, p = 0.012311 |
| Primary two-criterion TOPSIS | Türkiye 19/24; relative closeness 0.025267 |
| Non-proportional Unknown allocation | Türkiye 19th at 1×; 18th at 2×; 11th at 5×; 8th at 10× |
| OpenSSF primary GitHub repository matches | 37 matched / 42 projects; Türkiye share–criticality ρ = −0.2086, p = 0.2153 |
| LFX Health Score | 41 available, 40 fully comparable, 1 partial, 1 missing; Türkiye share–health ρ = −0.081721, p = 0.616 |
| G20 external correlation (Wachs total contributors) | n = 19, ρ = 0.950877, p = 4.39214×10⁻¹⁰ |

The external comparison uses `johanneswachs/OSS_Geography_Data/data/world_countries_2021.csv` and independently joins the exact 19 country members; the Github-only alternative yields ρ = 0.961404.

## Boundaries of the audit

This is **internal numerical reproducibility and archive integrity**, not validation of source completeness, LFX identity attribution, upstream activity coverage, geographic truth, or causal interpretation. Approximately **48.07%** of all-activities individual project-occurrences have an Unknown country. Missingness can be country- or project-dependent; non-proportional scenarios are stress tests and **not corrected point estimates**. All cross-project sums represent project-level occurrences, not distinct people.

The 42 projects and 24 countries were purposively selected, which limits the inferential generality of p-values. R&D reference years differ (2020–2024); source score snapshots have their own retrieval dates; OpenSSF 2025 values are repository-scoped, not country measures. TOPSIS results depend on modelling criteria, weights and fixed sample membership.

**Remaining action:** merge PR #36 after review. No new statistical technique is needed to fulfil the predefined MBA analysis plan. If claiming stronger strategic autonomy, collect direct evidence on dependency concentration, maintainer authority, governance and replacement capability instead of extrapolating from contribution numbers.

## Reproduction commands

```bash
python -m pip install -r requirements-analysis.txt
python -m unittest discover -s tests -p 'test_analysis_*.py' -v
python scripts/analysis/normalize_lfx.py --archives "$OSS_DATA_DIR/bulk-20261115T002108Z-118fd4a7.zip" "$OSS_DATA_DIR/bulk-20261115T004136Z-1af7e1fe.zip" --output "$OSS_DATA_DIR/processed/observations.csv"
python scripts/analysis/audit_capture.py --archives "$OSS_DATA_DIR/bulk-20261115T002108Z-118fd4a7.zip" "$OSS_DATA_DIR/bulk-20261115T004136Z-1af7e1fe.zip" --observations "$OSS_DATA_DIR/processed/observations.csv" --output "$OSS_DATA_DIR/processed/audit.json"
```

Afterwards use the independent analysis invocations in `docs/chapter4_runbook.md`. Keep the original restricted source archives outside Git.
