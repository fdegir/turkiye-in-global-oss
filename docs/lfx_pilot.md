# Backstage LFX pilot

This pilot implements issue #11 and uses the seven Backstage entries in the endpoint inventory. Backstage is a technical pilot, not a member of the research sample.

## Run locally

Requires Python 3.9+ and curl (available by default on macOS); no third-party Python packages. The script uses curl because the authenticated endpoint returned HTTP 200 with curl but HTTP 403 with Python urllib during the pilot. The token is sent through stdin, not subprocess arguments. From the repository root:

    python3 scripts/extract_lfx_pilot.py --data-dir ./data --zip

Set the LFX_API_TOKEN environment variable securely before running. The script requires this variable and exits with an error if it is missing or empty; it never prompts for credentials. Never put the token in a command argument, source file, or shared output.

The explicit data directory above selects the ignored data/raw folder in your local repository checkout. Alternatively omit --data-dir to use OSS_DATA_DIR when configured, or the repository data directory by default. To use the separate research data directory, specify its root (not raw/).

The script requests project details, then contributor and organization geography for code, collaboration and all scopes. Dates are 2021-11-01 inclusive to 2026-11-01 exclusive. It preserves exact successful JSON response bytes, with one adjacent manifest per capture. Each run has a unique ID; retries do not overwrite prior runs. HTTP errors and malformed responses are reported and not saved; authentication failure stops the run. Exit status is nonzero if fewer than seven responses succeed.

With --zip, the script prints the path of a ZIP containing this run's successful response/manifest pairs. Review the contents and share only if permitted by LFX terms and applicable privacy requirements. Do not commit raw data or ZIP archives. The pilot collects aggregate geography and project metadata only; no individual contributor profiles are requested.

A successful capture is not proof of historical coverage or denominator validity. The pilot intentionally does not normalize or calculate metrics. Review actual response shapes, country attribution, scope overlap, score mapping and coverage before bulk extraction.

## Offline tests

    python3 -m unittest discover -s tests

Tests mock curl and HTTP retrieval and verify endpoint configuration, exact-byte preservation, manifests and response validation. Live API behavior still requires your authenticated run.
