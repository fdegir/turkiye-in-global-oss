# Bulk LFX extraction

Pull latest main after merging the category amendment.
Requires Python 3.9+, curl, and LFX_API_TOKEN in the environment.

    python3 scripts/extract_lfx_all.py --data-dir ./data --zip

Reads the 42 candidate rows from data/metadata/projects.csv; preserves slug case.
To collect only the six new software-delivery projects, preserving the existing 36-project run:

    python3 scripts/extract_lfx_all.py --data-dir ./data --category software_delivery_developer_infrastructure --zip

This issues 48 requests; full collection issues 336. The ZIP contains the selected inventory, not all 42 rows when filtering. Keep both archives; later normalization combines them by stable project ID and scope, not by replacing the first run. Backstage research capture uses SD002 rather than the historical pilot ID.

Requests project details and whole-project Health Score snapshots plus six geography
responses (individual and organization for code, collaboration and all).
Geography uses 2021-11-01 inclusive to 2026-11-01 exclusive. No repository filters.
Uses the validated pilot curl transport with rate-limit handling and retries.

The script writes original responses and manifests under data/raw/lfx/<slug>/.
A run summary and exact selected project inventory are under data/raw/lfx/bulk_runs/<run_id>/.
With --zip, one bulk-<run_id>.zip in data/raw/lfx/ contains the run summary, inventory,
and every successful response/manifest pair from this run only. Prior runs are not overwritten.
A partial run also produces a ZIP and returns a nonzero exit code; authentication failure
stops subsequent requests and marks them not_attempted. Other endpoint failures are recorded
and collection continues. Re-running starts a new run (no resume or cache reuse yet).

Review archive contents before sharing, subject to LFX terms and privacy requirements.
Raw data stays local and ignored by git. No contributor profiles are requested.
The token is never passed as a command argument or written to manifests.

Capture is not final eligibility verification. The summary flags empty geographical responses
and records whether the expected primary repository is present in project details.
OpenStack is explicitly a repository group; equivalent .git URL suffixes are normalized. Project-level multi-repository mappings and historical coverage require review. Apply docs/lfx_data_quality.md to each run.
No normalization or analytical expansion is performed by this script.

Offline tests:

    python3 -m unittest discover -s tests
