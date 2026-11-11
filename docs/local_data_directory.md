# Local research data directory

## Purpose

Keep collected source data outside the public Git repository. The public repository contains research code, configuration examples, schemas, methodology and permitted derived outputs. The local data directory is an independently located working-data store.

The default suggested location is:

    ~/research/turkiye-in-global-oss-data/

Set the location with the `OSS_DATA_DIR` environment variable. Scripts should accept an explicit `--data-dir` argument, with the command-line argument taking precedence over the environment variable. Do not hard-code a user-specific absolute path.

## Directory layout

    turkiye-in-global-oss-data/
    ├── raw/
    │   ├── lfx/
    │   │   └── <project_slug>/
    │   │       └── <resource>/
    │   │           └── <extraction_mode>/
    │   │               └── <entity_type>/
    │   │                   └── <period_or_snapshot>/
    │   │                       └── <extraction_id>/
    │   │                           ├── response.json
    │   │                           └── manifest.json
    │   └── openssf/
    ├── samples/
    │   └── <source>/<project_slug>/
    ├── processed/
    │   ├── tables/
    │   └── validation_reports/
    ├── logs/
    │   └── extraction_log.csv
    └── manifest/
        └── extraction_manifest.schema.json

The raw response and its manifest are stored together in the same extraction directory. Keep the response body unchanged. A manifest describes exactly one retrieved response. For paginated endpoints, either store each page as a separately manifested response or document the exact page aggregation convention; do not silently discard page-level provenance.

## Manifest

Every captured response must have a `manifest.json` beside it. The manifest records:
- stable extraction ID and endpoint inventory ID;
- source, API version, project slug and resource/mode/entity;
- exact request method, URL and non-secret query parameters;
- requested observation period, if applicable;
- UTC retrieval timestamp, HTTP status and content type;
- response filename, byte size and SHA-256 checksum;
- completeness/pagination state;
- extraction script version or Git commit;
- sanitization status and notes.

Never include authorization headers, tokens, cookies, credentials, or other secrets in the manifest. Avoid recording contributor names, email addresses or other personal data in manifests. The schema is in `schemas/extraction_manifest.schema.json`; a clearly illustrative template is in `config/extraction_manifest.example.json`.

## Retention and terms

A local directory is not an exemption from source terms, privacy obligations or data-retention restrictions. Do not collect or retain contributor-level responses until the Linux Foundation clarifies that the intended academic use and retention are permitted. If permission is not established, use only permitted aggregate/derived fields and record the limitation. Do not publish raw LFX responses or push the local data directory to GitHub.

## Implementation conventions

- `OSS_DATA_DIR` identifies the root directory, not the `raw/` subdirectory.
- Use UTC timestamps in run IDs and manifests.
- Use stable project slugs and controlled resource/mode/entity identifiers from the endpoint inventory.
- Never treat an HTTP 200 response as proof that the requested time period or all pages are complete.
- Compute SHA-256 over the exact response bytes written to disk.
- Keep the manifest and response immutable after capture; corrections should create a new extraction ID.
- Normalized data belongs in `processed/` and must retain references to the source extraction IDs.
