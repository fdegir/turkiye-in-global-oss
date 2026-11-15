# Project selection amendment — 2026-11-15

## Decision

The researcher approved a seventh category, **Software delivery and developer infrastructure** (Yazılım Teslimatı ve Geliştirici Altyapısı), after technical collection of the original 36 candidates. The previous six-category freeze is retained as historical design version 1; this is version 2, with 42 candidates (seven strata of six). The 24-country sample, observation window, eight endpoint types and analytical dimensions are unchanged.

## Rationale and timing

The original strata cover foundational software, cloud/virtualization, cloud-native systems, languages/toolchains, data/AI and security. They omit the infrastructure that builds, integrates, catalogs, distributes and deploys software. This is an architectural gap for a software supply-chain study, not an outcome-based reason to increase the sample. The new candidates were selected for complementary technical roles, not Türkiye-attributed counts. Backstage had already been used as a technical pilot; acknowledge that prior knowledge rather than claiming the design was completely blinded. The original 36 were already collected; no original candidate was removed based on outcomes. No further expansion is planned.

| ID | Project | Role | LFX slug | Proposed primary repository |
|---|---|---|---|---|
| SD001 | Argo | GitOps and workflow/deployment orchestration | argo | argoproj/argo-cd |
| SD002 | Backstage | Developer portal and software catalog | backstage | backstage/backstage |
| SD003 | Jenkins | CI/CD automation | jenkins | jenkinsci/jenkins |
| SD004 | Tekton | Cloud-native CI/CD pipelines | tekton | tektoncd/pipeline |
| SD005 | Harbor | Artifact registry and distribution | harbor | goharbor/harbor |
| SD006 | Bazel | Build automation | bazelbuild-bazel | bazelbuild/bazel |

Primary repositories are proposed before inspecting the new research captures. Argo is an umbrella project: Argo CD is the preselected primary scoring repository, not a claim that all Argo participation is Argo CD activity. Tekton pipeline is the analogous primary repository. Check the repository inventories for exact mapping, active/nonexcluded scope, mirrors, overlap with existing projects and geographic availability. Retain only if technical eligibility is satisfied. Do not select an alternative repository based on a higher score. If an eligible mapping is unavailable, document the issue and use a technically motivated reserve or leave the category incomplete rather than selecting on country results.

## Selection history

Original replacements: Buildroot -> OpenWrt (standalone LFX project unavailable; Yocto considered but core repositories absent), Open vSwitch -> KubeVirt (no suitable standalone LFX record found), runc -> CRI-O (geography unavailable in UI; original API geography not independently tested). The original slot IDs OS006, CL005 and CN003 are retained. All 36 original candidates have nonempty Code and All responses and verified project identity. Retain with the quality caveats documented in [the data-quality register](lfx_data_quality.md). New candidates remain pending the same checks.

## Analysis implications

Seven categories of equal size; 42 x 24 x 3 = 3,024 possible project-country-scope observations (two entity measures per row). 336 endpoint captures across the complete inventory, collected in two runs (288 existing + 48 supplemental). Keep the historical pilot separate from SD002. Preserve the original 36-project analysis as a possible sensitivity comparison, not a second primary design. No new statistical methods or metrics are introduced. Record the amendment and its timing in the thesis methodology.
