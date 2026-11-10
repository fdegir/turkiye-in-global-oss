# Türkiye in Global OSS — CSV data templates

## Files
- `countries.csv`: 24-country comparison sample and group labels.
- `projects.csv`: provisional 36-project inventory and LFX coverage audit fields.
- `country_project_observations.csv`: one row per project × country × observation period. Contains separate individual/organization counts and percentages for code-contribution and collaboration filters.
- `project_metrics.csv`: project-level metadata and snapshot indicators.
- `extraction_log.csv`: request provenance and extraction audit trail.
- `data_dictionary.csv`: field definitions, units, availability and cautions.

## Fixed observation period
2021-11-01 through 2026-10-31. If annual sub-periods are later collected, add one row per country/project/year with exact start/end dates. Do not add unique contributor counts across periods unless the metric is explicitly an event count.

## Important semantic cautions
1. In `country_project_observations.csv`, `individual_*` refers to the contributor view; `organization_*` refers to the organization view.
2. `collaboration` names the LFX collaboration filter. It should not be interpreted as a raw number of collaboration events without validating the endpoint's semantics.
3. Keep LFX-reported percentages and independently recalculated percentages in separate columns.
4. Do not add code-contribution and collaboration values unless LFX confirms they are disjoint.
5. Distinguish zero from missing, unavailable, suppressed, or unknown-country values.
6. Record unknown/unattributed counts wherever the API exposes them. If not exposed, document this limitation.
7. `project_metrics.csv` is snapshot-based. Record a snapshot date for every row; do not treat a July 2025 OpenSSF score as a five-year measure.
8. LFX Health Score can be partial and its coverage can vary by platform/repository. Preserve `health_score_max` and `health_score_coverage_status`.
9. LFX Criticality/Impact, Health, Lifecycle/Maturity and Software Value should be treated as distinct metrics. Verify exact definitions before analysis.
10. The 36-project list is provisional pending an LFX coverage and repository-mapping audit. Do not remove projects based on country contribution results.

## Suggested missing-value conventions
- Empty field: not yet collected / unknown.
- `0`: observed zero only.
- `NA`: confirmed not available from the source.
- `NR`: source does not report the field.
- `UNK`: source reports an unknown/unattributed category.
Use one convention consistently; do not mix blank and zero.

## Country group labels
- `focal_country`: Türkiye.
- `original_peer_comparator`: Brazil, Poland, Spain, South Korea.
- `original_reference_comparator`: Germany, France, India, Japan. This preserves the original reference set without assuming they are the highest contributors.
- `additional_G20_comparator`: remaining G20 country members in the sample.
- `additional_european_comparator`: Netherlands, Sweden, Finland, plus Poland and Spain are separately tagged as original peers.

## Project categories
- operating_systems_foundational
- cloud_infrastructure_virtualization
- cloud_native_platforms_networking
- programming_languages_toolchains
- data_platforms_messaging_ai_ml
- security_identity_supply_chain

## Project-list note
The initial proposed security/supply-chain category uses Trivy in place of SPDX as a software project. SPDX may be retained as a reserve candidate if LFX provides an appropriate project-level activity record.
