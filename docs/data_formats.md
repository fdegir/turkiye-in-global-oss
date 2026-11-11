# Repository structure and data formats

## Principles

1. Prefer the simplest format that fits the data.
2. Keep analytical tables rectangular and machine-readable.
3. Preserve source responses separately from normalized research datasets.
4. Record provenance, observation periods and snapshot dates.
5. Do not create schemas or examples that imply unverified API behaviour.
6. Keep credentials and secrets out of Git.

## Format choices

| Format | Use | Do not use it for |
|---|---|---|
| CSV | Country/project inventories, country-project observations, project metrics, endpoint inventories and extraction logs | Nested API payloads or complex configuration |
| YAML | Human-maintained extraction defaults and controlled vocabularies | Raw source responses or large analytical tables |
| JSON | Original API responses and sanitized examples of observed payloads | Manually maintained country-project analytical tables |
| JSON Schema | Validation contracts after real response shapes are understood | Guessing the shape of undocumented endpoints |
| Markdown | Methodology, data collection instructions and conventions | Data intended for programmatic analysis |

CSV files use UTF-8, a header row, comma delimiters and one record per row. Quote fields containing commas, quotes or newlines according to standard CSV rules. Empty means not yet collected/unknown; use the documented NA, NR and UNK values only when their meanings are established.

YAML files are configuration, not evidence. Keep them small, reviewed and explicit. Use ISO 8601 dates (YYYY-MM-DD) and quote values that could be interpreted ambiguously as booleans, dates or numbers. Avoid YAML anchors, custom tags and implicit magic.

JSON response samples must be valid UTF-8 JSON. Do not reformat or normalize files stored as raw responses. Sanitized samples may be pretty-printed, but must retain the source field names, nesting and value types. Redaction must be limited to secrets or personal/sensitive values and documented; do not alter analytical values silently.

## Directory responsibilities

    config/                 Human-maintained YAML configuration
    data/metadata/          Country/project inventories and data dictionary (CSV)
    data/audit/             Eligibility and endpoint audit registers (CSV)
    data/raw/lfx/           Original LFX responses, organized by project/resource
    data/raw/openssf/       Original OpenSSF responses, organized by source/resource
    data/samples/lfx/       Small sanitized examples of observed LFX responses
    data/processed/         Derived/normalized datasets ready for analysis (CSV)
    data/project_metrics/   Project-level metrics and extraction log (CSV)
    schemas/                Analytical CSV headers and, later, validated JSON Schemas
    docs/                   Research methodology and collection documentation
    scripts/                Reproducible collection, transformation and validation code

## YAML configuration conventions

- Keep the observation period in one place: config/extraction.yaml.
- Store project category identifiers and descriptions in config/project_categories.yaml.
- Use stable snake_case identifiers that match the CSV data dictionary.
- Do not store credentials, tokens, cookies or authorization headers in configuration.
- Keep source base URLs and API versions explicit, but treat endpoint paths and parameters as unverified until tested and recorded in data/audit/project_api_endpoints.csv.
- Configuration changes that affect collection must be reflected in the extraction log for each run.

## Endpoint inventory conventions

data/audit/project_api_endpoints.csv has one row per distinct endpoint and extraction mode. Use a URL template only when the variable path/query structure is known. Record query parameters as JSON text in the CSV cell when they are structured; do not place credentials there. A row is not validated merely because its URL has been recorded. Set verification_status to an explicit state such as example_unverified, not_tested, tested_success or tested_error, and record the test timestamp and HTTP status when applicable.

## JSON response-sample conventions

See data/samples/README.md. Samples must be captured from actual API responses. Until the pilot confirms endpoint paths and response structure, create no placeholder payloads and no speculative JSON Schemas.

## Raw response retention

Keep the original response body unchanged, with request provenance recorded in data/project_metrics/extraction_log.csv. Store raw files only where the source terms permit repository redistribution. If redistribution is not permitted, retain permitted derived fields and document the restriction; do not commit restricted payloads. Never store secrets or credentials.

## Relationship to the LFX pilot

The pilot in issue #11 is the source of truth for confirming endpoint paths, request parameters, response structures, pagination, historical coverage and field semantics. Update this document and add schemas only after observing real responses. The broader candidate-project audit remains tracked separately in issue #4.
