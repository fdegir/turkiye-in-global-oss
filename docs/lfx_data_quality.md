# LFX data-quality register and analysis gates

**Status:** living source of truth for issues #3, #4, #5, #6, #7, #9 and #10. Update this register and the per-project eligibility CSV after every capture/audit. Do not proceed to substantive statistical analysis until the outstanding checks and interpretation rules below are addressed or explicitly accepted as limitations.

## Evidence and scope

Audit of original 36-project run `20261115T002108Z-118fd4a7`, script revision `2313e592029b9632298fd73d42cb45c50e76107b`. Local ZIP SHA-256: `fe76029a37edbaaa409add8e11fde02970d2d1e677075c40e3dc686bc21a423f`. Capture span 2026-11-15 00:21:09–00:25:14 UTC. The uploaded inventory and run summary match archive bytes. Archive test passed; 578 files (288 response/manifest pairs, summary and inventory); 288/288 SHA-256 and byte lengths match; all HTTP statuses 200; all project IDs, slugs, endpoint URLs and query flags verified. Raw data remains local; no raw payloads or tokens committed. This is capture integrity, not proof of completeness or representativeness.

The six new delivery projects are not included in these statistics. Recompute the report for all 42 after supplemental collection.

## Findings and required treatment

| ID | Finding / evidence (36-project baseline) | Required treatment | Status |
|---|---|---|---|
| DQ01 | 34 exact primary repository matches; Linux .git URL equivalent; OpenStack namespace with 1,336 repositories, not one primary. No exact cross-project repository URL overlaps. | Preserve authoritative upstream and indexed URL separately; normalize terminal .git and slash; explicitly recognize OpenStack group; check mirror/fork overlap beyond exact URLs. | Mapping addressed; group/mirror caveat retained |
| DQ02 | 216 geographical responses; 197 nonempty, 19 empty. All 72 Code and 72 All nonempty; 53/72 Collaboration nonempty. | Empty entire scope = coverage unverified, not real-world zero; keep source response and status; use All primary, Code/Collaboration complementary. | Open: activity coverage |
| DQ03 | 5,243 country/entity cross-scope checks; zero violations of max(code, collaboration) <= all <= code + collaboration. | Scopes overlap; never sum counts or percentages across them. Repeat check for supplemental data; absent buckets only treated as zero for diagnostic. | Baseline pass |
| DQ04 | 13,483 geographical rows; zero percentage mismatches at 0.005 percentage-point rounding tolerance, duplicate country codes, invalid counts/percentages. | Preserve reported shares and independently calculated shares using full geographical count sum including Unknown; do not call sum globally deduplicated unique population. | Baseline pass; repeat |
| DQ05 | All-scope Unknown individual share median 47.94%, range 30.28–75.28%; 16/36 >50%; weighted across project count sums 48.73%. Organization median 25.97%, range 17.96–41.29%; weighted 29.09%. | Preserve Unknown separately; never redistribute; describe findings as recorded/geographically attributed participation; assess sensitivity to low coverage without deleting projects based on country outcomes. | Material limitation |
| DQ06 | Country absent from a nonempty response may mean no reported qualifying entity. Entire response empty has different meaning. API unknown project can return empty list. | Distinguish explicit row, absent bucket in verified nonempty response, empty coverage-unverified response, failed/not attempted and null metric. Only absent bucket in verified nonempty response may receive zero reported count; otherwise missing. | Normalization gate |
| DQ07 | Linux Kernel Health Score null (maintainer 25/40 only, max/coverage null); OpenStack 55/65, maintainer 40, activity 15, security null, coverage 2. 34 full scores; 35 non-null total; 34 security scores. | Preserve raw score/max/coverage and null components. Never convert missing to zero or compare partial normalized score as equivalent to full score. Snapshot separate from five-year participation. | Material limitation |
| DQ08 | 34 LFX primary scores available; OpenStack and CRI-O null. Linux 0.93943 after URL correction. | Primary indexed repository only; no averaging or selecting highest score. External OpenSSF Criticality separate; scoring methodology/version/circularity caveat. | Mapping addressed; external snapshot pending |
| DQ09 | Impact available 32/36; missing Linux, FreeBSD, systemd, OpenStack. LFX health docs hide Impact documentation pending data quality fix IN-1243. | Capture only; defer analytical use. Package-dependent reach/downloads may omit infrastructure. Software value is estimated rebuild cost, not market value. | Deferred |
| DQ10 | Requested date window is correct, but availability does not independently prove complete historical ingestion. U-Boot, QEMU, Xen indexed GitHub mirrors; PostgreSQL upstream and mirror; collaboration outside indexed sources may be missing. | Preserve scope and repository metadata; don't claim all historical participation. Identity/geography attribution and mirror deduplication remain uncertain. | Material limitation |
| DQ11 | Health categories are project-level rollups; security score is not an independent comprehensive security measurement. Missing scan data may be treated as zero vulnerabilities/full points; some blocked signals imputed or reallocated. | Do not equate score to actual security or strategic autonomy; do not assume components independent or always additive. In baseline all 35 non-null totals happen to equal component sums. | Material limitation |
| DQ12 | 36 original projects captured before theoretical seventh-category amendment; Backstage was pilot. | Document timing and rationale; use new research ID SD002, avoid duplicate pilot; no selection based on country outcomes. | Amendment recorded |

## Empty Collaboration responses

Individual AND organization empty: OS002 FreeBSD, OS005 U-Boot, CL001 OpenStack, CL003 QEMU, CL004 Xen, DT005 OpenJDK, DA001 PostgreSQL, DA003 Apache Kafka, SC002 Portable OpenSSH. Organization only empty: OS001 Linux Kernel (individual response has 9 buckets). No empty Code or All responses. This likely reflects activity classification/source coverage for some projects, not absence of actual collaboration. Do not assume all collaboration coverage is equally good even when nonempty.

## Interpretation and normalization rules (binding for issue #5/#9)

- Counts are active individuals or organizations matching the filter, not events. Organization geography is attributed to the organization, not necessarily its contributors' locations. Country attribution may overlap; sum of buckets is the verified arithmetic denominator, not necessarily a unique global count.
- Keep reported and recalculated percentage separate; use all returned country buckets including XX/Unknown, never just selected 24 countries. Retain unknown count and source paths. A known-country-only share, if ever needed for sensitivity, must be labeled separately and cannot replace the original share.
- Empty scope: preserve raw empty array; normalized analytical measures missing with status empty_coverage_unverified. An absent selected country in a nonempty verified response gets zero reported count, with status absent_reported_bucket; explicit source rows status reported_bucket. Failed or unavailable responses stay missing. Preserve distinct entity statuses in notes or explicit fields so one missing entity does not erase the other.
- Health snapshots: use actual manifest retrieval date; retain missing metrics as null/NA, not zero. Project age, foundation and OpenSSF snapshot provenance separately. Do not infer missing values from unrelated metrics. Impact deferred.
- All is primary participation measure; code and collaboration complementary, overlapping. Acknowledge All may be incomplete where underlying activity coverage is missing. No inference of strategic autonomy, security or influence directly from participation.
- No raw responses in public Git; only permitted derived quality findings. Confirm terms before sharing or publishing derived research data.

## Required checks before normalization and statistical analysis

- [x] Original run archive integrity, identity, scope, query parameters, checksums, counts, percentages and set-bound checks.
- [x] Original 36 project mappings and empty-response exceptions recorded in eligibility audit.
- [x] Document category amendment, missingness, denominator and health rules.
- [ ] Capture six new candidates, verify all 48 manifests, repository mappings (including umbrella projects), geography and all same diagnostics; compare repository overlap across all 42.
- [ ] Recompute aggregate quality statistics for 42 projects and record per-project/entity/scope provenance and unknown fractions.
- [ ] Implement reproducible archive-to-CSV normalization and automated validation (#5/#9). Preserve both runs and exact inventory versions; do not silently substitute older pilot data.
- [ ] Verify country code mapping and distinguish missing from zero; check selected-country row coverage.
- [ ] Assess historical coverage limitations and source attribution; no assertion of complete five-year ingestion without evidence.
- [ ] Collect previously agreed external country indicators and external OpenSSF Criticality snapshot (#7/#8).
- [ ] Carry all material limitations into methodology, results and discussion; assess sensitivity to coverage and partial metrics before statistical analysis (#10). Do not select models solely on apparent significance.

## Source references

- [Contributor geographical endpoint](https://github.com/linuxfoundation/insights/blob/main/api/src/versions/v1-alpha/contributors/contributor-geographical-distribution.ts)
- [Organization geographical endpoint](https://github.com/linuxfoundation/insights/blob/main/api/src/versions/v1-alpha/contributors/organization-geographical-distribution.ts)
- [Geographical distribution implementation](https://github.com/linuxfoundation/insights/blob/main/api/src/lib/geo-distribution.ts)
- [Health Score methodology](https://github.com/linuxfoundation/insights/blob/main/frontend/docs/metrics/health-score/index.md)
- [Health Score endpoint](https://github.com/linuxfoundation/insights/blob/main/api/src/versions/v1-alpha/overview/health-score.ts)
- [Project details endpoint](https://github.com/linuxfoundation/insights/blob/main/api/src/versions/v1-alpha/projects.ts)
- [LF OSS Index methodology](https://github.com/linuxfoundation/insights/blob/main/frontend/docs/introduction/lf-oss-index/index.md)

Local archive is the evidence for numerical observations, not an independently verified source of true population coverage.
