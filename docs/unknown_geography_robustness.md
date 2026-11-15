# Robustness to unknown geographical attribution

Related issue #24. Research scope remains frozen: 42 projects, seven categories, 24 countries, 2021-11-01 through 2026-10-31. No new source data or endpoint requests. This is a methodological refinement after exploratory review, not a change to the project sample or primary outcome.

## Definitions and three approaches

For project p, country c, activity scope s and entity type e, C is the observed country bucket count, T is the sum of all returned geographical bucket counts including Unknown, U is the Unknown (XX) count, K=T-U. Each entity and scope has its own denominator. These arithmetic denominators are not independently verified globally deduplicated populations. Use all returned countries in T and K, not just the 24 selected countries.

1. **Primary:** preserve original LFX counts and reported percentages. For exploratory country totals sum C across the 42 projects. Also compare equal-weight mean project shares 100*C/T, computed using the same project set as the robustness analysis; this isolates the effect of changing the denominator from the effect of changing project weights.
2. **Robustness:** calculate 100*C/K per project; take the arithmetic mean over the same 42 projects. This conditions on reported known geography, not an imputation. Equal project weighting prevents the largest projects from dominating. Within a project all countries receive the same denominator, so relative country ratios do not change. Across projects rankings can change.
3. **Sensitivity:** estimate C*T/K per project, sum over projects, allowing fractional values until final presentation. This proportional-allocation scenario assumes the Unknown buckets have the same country distribution as known buckets within each project/entity/scope. It is equivalent to applying project-specific inverse known-coverage weights. It does not identify the actual missing countries, repair incomplete source ingestion, or establish an unbiased estimator. Do not use one global adjustment factor.

Individuals and organizations are separate. Across-project count sums are contributor-project/organization-project participations, not distinct people or organizations. All activity is primary; complementary Code and Collaboration analyses may be performed only where coverage is comparable; never sum these overlapping scopes.

## Eligibility and missingness

- Require a verified nonempty response and valid denominator K>0; explicitly report unavailable comparisons when missing. Do not replace missing or empty responses with zeros or allocate their Unknown values.
- An absent selected-country bucket in an otherwise verified nonempty response is zero *reported* qualifying entities. Preserve this status separately from explicit rows.
- Require nonnegative integer counts, no duplicate country codes and valid source percentage reconciliation. Check manifests and preserve provenance. If an XX bucket is absent, treat U=0 only when the response is otherwise valid and record that no Unknown bucket was reported.
- Use a common project set for country comparisons and original/known shares; report the count and any exclusions. Never silently use different project denominators across countries. If T=0 or K=0, mark the relevant share/scenario unavailable.
- Preserve original counts, reported percentages, unknown counts, and recalculated shares. Store derived scenario estimates in a separate local output; do not overwrite observed analytical data or commit raw API payloads.

## Interpretation

Unknown attribution affects all countries, but the country composition of Unknown is not identified. Missingness can depend on location, organization, platform, project and activity. Proportional allocation is a transparent hypothetical scenario, not evidence that missingness is random. A stable rank under this scenario supports robustness to that particular assumption only, not robustness to every possible allocation or proof of no bias. Known-geography shares are conditional on observed attribution. Project-source coverage and identity overlap remain separate limitations. No causal claims, statistical significance or actual country totals can be inferred solely from these calculations.

Report both original and conditional shares, observed and estimated counts, ranks and peer-country contrasts separately for both entities. If comparing GDP/population-normalized rates, reuse the same verified country-year denominators for observed and scenario counts and document the source/reference year. Do not treat any exploratory ranking as a new primary outcome or select projects/methods based on it.

## Reproducibility

Run the local script against the two complete frozen-sample ZIPs (original 36 and supplemental six). It checks archive response manifests, requires exactly the 42 frozen project IDs and the selected country inventory, uses All geography only, and outputs country-level observed counts, mean original share, mean known share and scenario totals. Outputs remain local. The exploratory analysis does not replace the pending full normalization pipeline or formal statistical analysis. See [LFX data quality](lfx_data_quality.md), DQ05/DQ06/DQ10, and issue #24.
