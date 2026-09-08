# Options research

Project location: `E:\Work\options`, in the existing E:\Work Git repository.
Moved out of commodity/options at the user's request on 2026-09-08.

Collection is PAUSED. Existing source snapshots are immutable and excluded from Git.
The saved dataset contains 324 catalogued Ahrom contracts, 230 detail snapshots,
and 191 underlying daily IV observations. Contract snapshots are not daily histories.

See docs/STATUS.md for scope and unresolved coverage, and docs/WORKFLOW.md for layout.

Validation: `python -m pytest options/tests` from E:\Work tests numeric parsing, missing values, and immutable/idempotent imports. CLI JSON output uses ASCII escapes for Windows console compatibility.
