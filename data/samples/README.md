# API response samples

This directory contains small, sanitized examples captured from actual source responses. It is for development and documentation; it is not a substitute for retaining original raw responses where permitted.

## Naming

Use this structure:

    data/samples/<source>/<project_slug>/<resource>__<mode>__<entity>__<period-start>_<period-end>__<retrieved-utc>.json

Examples of resource/mode/entity components (names only; not claims that these routes or response types have been verified):

- project_details__snapshot__project
- geographical_distribution__code_contributions__individual
- geographical_distribution__collaborations__individual
- geographical_distribution__code_contributions__organization
- geographical_distribution__collaborations__organization

For project-level snapshots without a requested period, use snapshot in place of the period range. Use UTC timestamps in filenames, for example 20261111T120000Z.

## Required provenance

For every sample, include a neighbouring README or a small metadata sidecar that records:

- source and API version;
- exact endpoint URL and HTTP method;
- query parameters (excluding secrets);
- retrieval timestamp in UTC;
- HTTP status;
- project slug and relevant project identifier;
- requested period, if applicable;
- whether the response is complete or paginated;
- sanitization performed and why;
- related endpoint-inventory and extraction-log identifiers.

Do not embed authorization headers, API keys, cookies, access tokens or secrets. Remove personal/sensitive fields only where necessary, document the redaction, and do not alter counts or other analytical values.

## Raw versus sample

- data/raw/<source>/ is for the original response body, unchanged, when redistribution is permitted.
- data/samples/<source>/ is for a small sanitized example.
- If raw redistribution is not permitted, do not commit the response. Record the restriction and retain only permitted derived data.

## Current pilot status

The Backstage project-details URL is listed in data/audit/project_api_endpoints.csv as example_unverified. No JSON payload is included yet because no actual response has been captured and validated. Do not create speculative payloads or JSON Schemas.
