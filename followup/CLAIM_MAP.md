# Claims and Reproduction Map

Paths below start in the reviewed study root. Original paths are inside `original-publication.zip`, under `DAVID_Week4_Publication/`.

| Claim | Saved evidence | Executable check |
|---|---|---|
| Original archive is unchanged | `followup/results/baseline-identity.json` and exact archive bytes | `verify_study.py`, fixed original archive SHA-256 |
| All ten original audit steps pass | `followup/results/baseline-audit-summary.json`, `baseline-logs/` | Complete launcher extracts and runs original `verify_all.py` |
| Nine source files match the pinned GitHub tree | `fresh-source-validation.json`, `axyl-tree-6909618.json` | Source Git-blob identities; original integrity program |
| Two captures contain 350 observations of 175 commitments | Original and repeat batches inside archive | Preserved request/response readers and both full chain checks |
| 187 distinct certificates pass py_ecc | `all-certificates-pyecc.json`, `summary.json` | `followup/verify_followup.py` |
| All observations are covered without counting duplicates twice | Each certificate's `observations` mapping | Same program; total mapped observations must equal 350 |
| All 175 execution headers match their signed references | `data/headers-20261029/`, `results/headers-20261029.json` | `followup/check_headers.py` |
| Metadata and raw HTTP bodies remain bound to parsed results | Metadata, exact request and response bodies in capture files | Same header checker |
| gasUsed mutation changes all 175 header hashes | Per-header mutation outcomes | Same header checker |
| Seven synthetic chains isolate authority/link/quorum assumptions | `synthetic-chain-controls.json` includes every generated fixture | `followup/verify_followup.py` |
| Updated images agree with the article | `figure-data.json`, PNG/SVG files | `followup/check_publication.py` |
| Public CI passed | Requires an actual public run and commit | No such run is claimed by the local review |
| Initial committee is canonical | Not independently established | Remains an explicit input/trust assumption |

The local mutation controls test checker behavior. They are not additional mainnet observations or attacks against a live node.
