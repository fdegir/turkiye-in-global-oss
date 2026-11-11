# Türkiye in Global OSS

An empirical study of Türkiye's participation in the global open-source software ecosystem, examining contribution patterns across selected projects and countries, with implications for software supply-chain sustainability.

## Research scope

- Observation period: 2021-11-01 through 2026-10-31.
- Country sample: Türkiye and a predefined comparative sample; see data/metadata/countries.csv.
- Project sample: a provisional, stratified inventory; see data/metadata/projects.csv.
- Primary source: LFX Insights, subject to endpoint, attribution and coverage validation.

The country and project samples must be frozen using documented criteria before substantive contribution comparisons. Do not select or replace projects based on the observed level of Türkiye-attributed contributions.

Country comparison-group labels in countries.csv describe the sampling design, not contribution performance:
- focal_country: Türkiye.
- original_peer_comparator: Brazil, Poland, Spain and South Korea.
- original_reference_comparator: Germany, France, India and Japan.
- additional_G20_comparator: other sampled G20 country members.
- additional_european_comparator: Netherlands, Sweden and Finland. Poland and Spain also retain their original peer-comparator tag.

The 36-project inventory is provisional and remains subject to the LFX coverage and repository-mapping audit.

## Repository data conventions

Use each format for the kind of information it represents:

- CSV: rectangular research datasets, inventories, endpoint registers and extraction logs.
- YAML: small, human-maintained configuration and controlled vocabularies.
- JSON: original API responses and sanitized response examples; preserve nested source structures.
- JSON Schema: only after actual response shapes and normalized record contracts have been observed and agreed.
- Markdown: methodology, collection procedures and format conventions.

See docs/data_formats.md.

## Main datasets

- data/metadata/countries.csv: country sample and comparison-group labels.
- data/metadata/projects.csv: provisional project inventory and LFX coverage audit fields.
- schemas/country_project_observations.csv: analytical observation record header.
- data/project_metrics/project_metrics.csv: project-level metadata and snapshot indicators.
- data/project_metrics/extraction_log.csv: request provenance and extraction audit trail.
- data/metadata/data_dictionary.csv: field definitions, units, availability and cautions.
- data/audit/project_api_endpoints.csv: endpoint inventory; entries remain unverified until tested.

## Configuration

- config/extraction.yaml: fixed observation window and source defaults.
- config/project_categories.yaml: category identifiers and descriptions.

These files describe research configuration; they do not assert that every listed API route or field exists.

## Raw data and samples

- data/raw/ is reserved for original source responses and other collected source files. Preserve source payloads unchanged where licensing and redistribution terms permit.
- data/samples/ is reserved for small, sanitized examples used to document and develop against observed response structures.
- Never put API tokens, credentials, private headers or personal data in the repository.
- Do not fabricate example API payloads. A sample must come from an actual response and include provenance.

See data/samples/README.md for naming and capture conventions.

## Important semantic cautions

1. In country_project_observations.csv, individual_* refers to the contributor view; organization_* refers to the organization view.
2. collaboration names the LFX collaboration filter. It must not be interpreted as a raw number of collaboration events until endpoint semantics are validated.
3. Keep LFX-reported percentages and independently recalculated percentages separate.
4. Do not add code-contribution and collaboration values unless LFX confirms they are disjoint.
5. Distinguish observed zero from missing, unavailable, suppressed and unknown-country values.
6. Record unknown/unattributed counts wherever the API exposes them. If not exposed, document the limitation.
7. Project metrics are snapshots. Record a snapshot date for every metric; do not treat a single snapshot as a five-year measure.
8. Preserve Health Score maximum/coverage information where available.
9. Treat Criticality, Impact, Health, Lifecycle/Maturity and Software Value as distinct metrics. Verify definitions before analysis.
10. LFX coverage and repository mappings must be audited before the project sample is finalized.

## Missing-value conventions

- Empty field: not yet collected / unknown.
- 0: observed zero only.
- NA: confirmed not available from the source.
- NR: source does not report the field.
- UNK: source reports an unknown/unattributed category.

Use these consistently; never silently convert missing records to zero.

## Project categories

- operating_systems_foundational
- cloud_infrastructure_virtualization
- cloud_native_platforms_networking
- programming_languages_toolchains
- data_platforms_messaging_ai_ml
- security_identity_supply_chain

The initial security/supply-chain category uses Trivy in place of SPDX as a software project. SPDX may be retained as a reserve candidate if LFX provides an appropriate project-level activity record.
