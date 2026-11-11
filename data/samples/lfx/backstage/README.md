# Backstage LFX pilot samples

Pilot slug: backstage

Status: pending API verification.

The candidate project-details URL is recorded in data/audit/project_api_endpoints.csv. This directory will contain sanitized JSON examples only after the corresponding endpoints have been called and their responses inspected.

Expected sample types to investigate during issue #11:

- project details / overview;
- individual geographical distribution under the code-contribution filter;
- individual geographical distribution under the collaboration filter;
- organization geographical distribution under the code-contribution filter;
- organization geographical distribution under the collaboration filter.

These are investigation targets, not confirmed endpoint names or response schemas. Record the actual endpoint path, parameters and response type in the endpoint inventory before adding a sample.

Do not add placeholder JSON payloads. Preserve original responses separately under data/raw/lfx/backstage/ only if LFX redistribution terms permit it.
