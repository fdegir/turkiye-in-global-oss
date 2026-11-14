# Backstage LFX pilot

This pilot implements issue #11 and uses the eight Backstage entries in the endpoint inventory. Backstage is a technical pilot, not a member of the research sample.

## Run locally

Requires Python 3.9+ and curl (available by default on macOS); no third-party Python packages. The script uses curl because the authenticated endpoint returned HTTP 200 with curl but HTTP 403 with Python urllib during the pilot. The token is sent through stdin, not subprocess arguments. From the repository root:

    python3 scripts/extract_lfx_pilot.py --data-dir ./data --zip

Set the LFX_API_TOKEN environment variable securely before running. The script requires this variable and exits with an error if it is missing or empty; it never prompts for credentials. Never put the token in a command argument, source file, or shared output.

The explicit data directory above selects the ignored data/raw folder in your local repository checkout. Alternatively omit --data-dir to use OSS_DATA_DIR when configured, or the repository data directory by default. To use the separate research data directory, specify its root (not raw/).

The script requests project details, and the whole-project Health Score snapshot, plus contributor and organization geography for code, collaboration and all scopes. Dates are 2021-11-01 inclusive to 2026-11-01 exclusive. It preserves exact successful JSON response bytes, with one adjacent manifest per capture. Each run has a unique ID; retries do not overwrite prior runs. HTTP errors and malformed responses are reported and not saved; authentication failure stops the run. Exit status is nonzero if fewer than all requested responses succeed.

With --zip, the script prints the path of a ZIP containing this run's successful response/manifest pairs. Review the contents and share only if permitted by LFX terms and applicable privacy requirements. Do not commit raw data or ZIP archives. The pilot collects aggregate geography and project metadata only; no individual contributor profiles are requested.

A successful capture is not proof of historical coverage or denominator validity. The pilot intentionally does not normalize or calculate metrics. Review actual response shapes, country attribution, scope overlap, score mapping and coverage before bulk extraction.

## Health Score snapshot

The eighth endpoint is GET /v1-alpha/projects/backstage/overview/health-score (no dates or repos filter). It returns the overall score, labels, impact score, three category scores, covered category count and maximum. Capture the full original JSON, including null fields. Health and impact are snapshots, not five-year observations. To capture just this additional endpoint after an earlier successful seven-response run:

    python3 scripts/extract_lfx_pilot.py --data-dir ./data --health-only --zip

Keep the earlier ZIP; this new ZIP contains only the health response and manifest. The existing project metrics schema captures the returned fields (including health_covered_category_count). Impact fields are retained but analytical use is deferred: LF documentation currently hides Impact Score because of data quality issue IN-1243. Compare health scores only with appropriate coverage context; security scores may include imputed signals and do not measure comprehensive supply-chain security. See https://github.com/linuxfoundation/insights/blob/main/frontend/docs/metrics/health-score/index.md and https://github.com/linuxfoundation/insights/blob/main/api/src/versions/v1-alpha/overview/health-score.ts.

## Offline tests

    python3 -m unittest discover -s tests

Tests mock curl and HTTP retrieval and verify endpoint configuration, exact-byte preservation, manifests and response validation. Live API behavior still requires your authenticated run.
