# Bulk LFX extraction

Merge project mapping PR #20 and this PR before running from main.
Requires Python 3.9+, curl, and LFX_API_TOKEN in the environment.

    python3 scripts/extract_lfx_all.py --data-dir ./data --zip

Reads the 36 candidate rows from data/metadata/projects.csv; preserves slug case.
Requests project details and whole-project Health Score snapshots plus six geography
responses (individual and organization for code, collaboration and all).
Geography uses 2021-11-01 inclusive to 2026-11-01 exclusive. No repository filters.
Uses the validated pilot curl transport with rate-limit handling and retries.

The script writes original responses and manifests under data/raw/lfx/<slug>/.
A run summary and exact public project inventory are under data/raw/lfx/bulk_runs/<run_id>/.
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
Project-level multi-repository mappings and historical coverage require review.
No normalization or analytical expansion is performed by this script.

Offline tests:

    python3 -m unittest discover -s tests
