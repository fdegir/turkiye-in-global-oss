# LFX data-quality register and analysis gates

**Status:** living source of truth for issues #3, #4, #5, #6, #7, #9 and #10. Update this register and the per-project eligibility CSV after every capture/audit. Do not proceed to substantive statistical analysis until the outstanding checks and interpretation rules below are addressed or explicitly accepted as limitations.

## Evidence and scope

Audit of original 36-project run `20261115T002108Z-118fd4a7`, script revision `2313e592029b9632298fd73d42cb45c50e76107b`. Local ZIP SHA-256: `fe76029a37edbaaa409add8e11fde02970d2d1e677075c40e3dc686bc21a423f`. Capture span 2026-11-15 00:21:09–00:25:14 UTC. The uploaded inventory and run summary match archive bytes. Archive test passed; 578 files (288 response/manifest pairs, summary and inventory); 288/288 SHA-256 and byte lengths match; all HTTP statuses 200; all project IDs, slugs, endpoint URLs and query flags verified. Raw data remains local; no raw payloads or tokens committed. This is capture integrity, not proof of completeness or representativeness.

The original findings below remain a historical 36-project baseline. The **combined 42-project audit** appended below supersedes baseline totals for the final sample. Both archives are retained locally; no raw payloads are published.

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
- [x] Capture six new candidates; verify 48 manifests, mappings, geography, diagnostics and exact normalized repository URL overlap across all 42.
- [x] Recompute combined quality statistics and record project-level scope/entity provenance; delivery unknown fractions below.
- [ ] Implement reproducible archive-to-CSV normalization and automated validation (#5/#9). Preserve both runs and exact inventory versions; do not silently substitute older pilot data.
- [ ] Verify country code mapping and distinguish missing from zero; check selected-country row coverage.
- [ ] Assess historical coverage limitations and source attribution; no assertion of complete five-year ingestion without evidence.
- [ ] Collect previously agreed external country indicators and external OpenSSF Criticality snapshot (#7/#8).
- [ ] Carry all material limitations into methodology, results and discussion; assess sensitivity to coverage and partial metrics before statistical analysis (#10). Do not select models solely on apparent significance.

## Supplemental and combined audit — 2026-11-15

Run `20261115T004136Z-1af7e1fe`, script revision `0b43f8d0f0d72878c64ae2d98198ccc808836846`; local ZIP SHA-256 `081af2c5a9409cf78bb1f6d915789136264e7a602ef388a09f58c3d1d57ac24e`. Retrieval span 00:41:40–00:42:18 UTC. Archive contains 98 files (48 response/manifest pairs plus summary and selected inventory). Both original and supplemental ZIPs reopened and independently checked. All 336 response checksums, byte counts, project identities, endpoint URLs, query flags, HTTP statuses and summary geography bucket counts match. No exact normalized repository URL overlap between projects.

| Check | Original 36 | Delivery six | Combined 42 |
|---|---:|---:|---:|
| Captures | 288 | 48 | 336 |
| Geographic responses | 216 | 36 | 252 |
| Nonempty | 197 | 36 | 233 |
| Empty Collaboration | 19 | 0 | 19 |
| Geographic rows | 13,483 | 2,553 | 16,036 |
| Country/entity scope bound checks | 5,243 | 939 | 6,182 |
| Percentage mismatches (>0.005 pp) | 0 | 0 | 0 |
| Invalid count/percentage, duplicate country code or scope violations | 0 | 0 | 0 |

All 42 Code and All responses for both entities nonempty (84 per scope). All six delivery primary repositories match, active and not excluded. Jenkins only indexes core jenkinsci/jenkins, not wider plugins; Argo, Tekton and Bazel are multi-repository aggregates while primary scores refer to preselected repositories. No duplicate pilot: SD002 is the research capture, historical Backstage pilot excluded.

| Project | Repos | All individual buckets | All organization buckets | Unknown individuals % | Unknown organizations % | Health/max | Primary score |
|---|---:|---:|---:|---:|---:|---:|---:|
| Argo | 38 | 118 | 93 | 42.70 | 21.23 | 72/100 | 0.65740 |
| Backstage | 23 | 101 | 73 | 42.80 | 17.99 | 68/100 | 0.79975 |
| Jenkins | 1 | 68 | 36 | 51.26 | 27.17 | 85/100 | 0.71788 |
| Tekton | 24 | 71 | 46 | 40.43 | 20.76 | 78/100 | 0.62468 |
| Harbor | 24 | 95 | 71 | 45.74 | 21.06 | 62/100 | 0.57814 |
| Bazel | 137 | 101 | 66 | 44.34 | 30.38 | 78/100 | 0.58621 |

Final 42-project unknown attribution (All scope, computed from count sums):

| Measure | Individuals | Organizations |
|---|---:|---:|
| Median project unknown share | 46.76% | 25.51% |
| Range | 30.28–75.28% | 17.96–41.29% |
| Projects >50% Unknown | 17/42 | 0/42 |
| Weighted across project count sums | 48.07% | 28.04% |

Selected-country All-scope combinations: 1,008 per entity; 963 individual buckets present (45 absent), 904 organization buckets present (104 absent). These are reported bucket presence, not independent historical coverage. Apply DQ06 to normalization.

Combined metric availability: 40/42 primary scores (OpenStack and CRI-O missing); 41/42 Health Score (Linux Kernel missing); 40/42 full Health Score, 40/42 security scores; 38/42 Impact Scores. All six delivery Health Scores have all three categories and max 100. All 41 non-null totals happen to equal the sum of available category components, but do not generalize this arithmetic as the rollup definition. Impact remains deferred. Original Linux and OpenStack caveats unchanged.

**Final freeze:** 42 retained projects, seven categories, 24 countries; 3,024 possible project-country-scope rows. Data collection complete for the eight LFX endpoint types, but attribution, source coverage and historical completeness are not established. No further scope expansion. Archive-to-CSV normalization and repeatable validation remain open. Exploratory country comparisons are not formal hypothesis tests and must not influence selection.

## Source references

- [Contributor geographical endpoint](https://github.com/linuxfoundation/insights/blob/main/api/src/versions/v1-alpha/contributors/contributor-geographical-distribution.ts)
- [Organization geographical endpoint](https://github.com/linuxfoundation/insights/blob/main/api/src/versions/v1-alpha/contributors/organization-geographical-distribution.ts)
- [Geographical distribution implementation](https://github.com/linuxfoundation/insights/blob/main/api/src/lib/geo-distribution.ts)
- [Health Score methodology](https://github.com/linuxfoundation/insights/blob/main/frontend/docs/metrics/health-score/index.md)
- [Health Score endpoint](https://github.com/linuxfoundation/insights/blob/main/api/src/versions/v1-alpha/overview/health-score.ts)
- [Project details endpoint](https://github.com/linuxfoundation/insights/blob/main/api/src/versions/v1-alpha/projects.ts)
- [LF OSS Index methodology](https://github.com/linuxfoundation/insights/blob/main/frontend/docs/introduction/lf-oss-index/index.md)

Local archive is the evidence for numerical observations, not an independently verified source of true population coverage.
