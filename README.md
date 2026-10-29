# Rayls Checkpoint Study: Reproduce the Original Findings and Follow-up

This package accompanies **How Can You Verify a Blockchain Checkpoint? Lessons from 175 Rayls Epoch Records**. It preserves the original publication archive unchanged and adds a separately dated follow-up covering every distinct saved certificate and every referenced execution header.

The research question is practical: can a reader reconstruct the signed bytes, verify an authorized quorum, follow committee changes, and bind the resulting checkpoint to an execution header?

**No wallet, private key, tokens or transaction submission is required.** Installing dependencies needs internet access. The default complete audit then works offline. A separate, explicit `--capture` option is the only new program that makes public RPC requests.

## 1. What is original and what was added?

| Measurement | Original publication | Follow-up recorded on 29 October 2026 |
|---|---|---|
| Epoch commitments | 175, numbered 0 through 174 | The same fixed 175 commitments |
| Saved epoch observations | Two captures: 22 and 23 October; 350 observations | Both complete saved sequences checked again |
| Certificate variants | Twelve certificates differed between captures | All **187 distinct certificates** checked using py_ecc |
| Second cryptographic implementation | Three original samples plus both variants of twelve changed records | Complete coverage of the distinct certificates in both captures |
| Execution headers | Three sampled block references | Fresh read-only retrieval and verification of **all 175 referenced headers** |
| Local header mutations | Three gasUsed changes | One gasUsed change detected for each of the 175 headers |
| Offline verifier controls | Thirteen outcomes | Seven additional three-record synthetic-chain scenarios |
| Pinned-source comparison | Nine saved source identities | All nine compared again with the pinned GitHub tree |
| Initial trust | Committee observed from the official RPC | Still not independently authenticated out of band |

There are **175 record commitments, 350 captured observations, and 187 distinct certificates**. These counts describe related data, not 350 different checkpoints or 187 independent experiments. The 187-check follow-up includes certificates already sampled in the original study; it is an extension of coverage, not 187 additional observations.

The seven synthetic scenarios are separate from the thirteen original controls. Five reject as expected, and two are intentionally valid under their supplied synthetic anchors. No synthetic record was sent to a live node.

## 2. Download and extract the complete study

Open the [public repository](https://github.com/davidvnvn276/david-rayls-checkpoint-study), select **Code**, then **Download ZIP**. Fully extract that source ZIP and open the extracted repository folder.

Alternatively, if Git is installed:

```bash
git clone https://github.com/davidvnvn276/david-rayls-checkpoint-study.git
cd david-rayls-checkpoint-study
```

The folder containing `verify_study.py`, `requirements-lock.txt`, `original-publication.zip` and `followup/` is the **study root**. Run all commands from that folder, not from inside a ZIP viewer.

The complete study is available as readable files in the repository. There is no requirement to find a separately uploaded outer ZIP with a particular filename. If using a separately distributed complete study ZIP, extract it and identify the same study root.

The launcher extracts `original-publication.zip` automatically. That inner archive preserves the original 121-file publication; it is not a substitute for the current follow-up files.

| Path | Purpose |
|---|---|
| README.md | This reader-facing reproduction guide |
| ARTICLE_COPY.md | Current clean English article |
| ARTICLE.md | Current article with figure positions and captions |
| ARTICLE.html | Standalone illustrated article; figures are embedded |
| images/ | Four full-resolution PNGs and editable SVGs |
| original-publication.zip | Unmodified original 121-file publication |
| requirements-lock.txt | Pinned Python dependencies |
| verify_study.py | Complete offline audit launcher and integrity check |
| followup/verify_followup.py | All-certificate py_ecc verification and seven synthetic-chain controls |
| followup/check_headers.py | Saved-header verification; optional explicit live capture |
| followup/check_publication.py | Article and figure consistency checks |
| followup/data/headers-20261029/ | Exact request/response bodies for the new 175-header capture |
| followup/results/ | Recorded calculations, control fixtures, provenance and logs |
| followup/ANCHOR_REVIEW.md | Bootstrap-source review and remaining trust assumption |
| followup/CLAIM_MAP.md | Claims mapped to evidence and executable checks |
| .github/workflows/verify-checkpoints.yml | Active-location GitHub Actions workflow definition |
| ci/verify-checkpoints.yml | Identical readable copy of the workflow |
| MANIFEST_SHA256.json | Hashes of the distributed files except the manifest itself |

## 3. Install Python and the locked dependencies

The recorded review used **Linux, Python 3.12.14**. Native Windows and macOS were not executed during this review. Commands for Windows are supplied to avoid unnecessary activation or execution-policy changes, but they are not a claim that every platform was tested.

### Linux

Open a terminal in the study root:

```bash
python3.12 --version
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
```

Expected: Python reports 3.12.x and pip installs all pinned packages without errors.

### Windows PowerShell

In File Explorer, open the extracted study folder. Open PowerShell in that directory and run:

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements-lock.txt
```

These commands call the environment's interpreter directly. `Activate.ps1` and PowerShell execution-policy changes are unnecessary. If `py` is unavailable, use the full path of an installed Python 3.12 interpreter for the first two commands.

Use the same interpreter to install and run. Installing into one Python environment and executing with another produces missing-module errors.

The lock includes pyblst 0.3.15, py_ecc 8.0.0, BLAKE3, Keccak, Base58 and Roaring bitmap dependencies. Do not substitute unrelated package versions when reproducing the fixed environment.

## 4. Check file identity first

Linux:

```bash
.venv/bin/python verify_study.py --integrity-only
```

Windows:

```powershell
.\.venv\Scripts\python.exe .\verify_study.py --integrity-only
```

Expected: `status` is `passed` and `files_checked` equals the number of entries in the manifest. This step uses only the Python standard library and does not verify any BLS signatures.

The original archive is separately pinned to:

```text
SHA-256: b0e51f0b6cd4bc4ed51bbd336108812b395201fcf08f6586cbf3c5e6ed892bdc
Git blob: ec5a38812268db0a5ba9c065fae1bec18b09642a
Repository commit: 6442353baa0096fe260c5d5f2a8c757e40de94d4
```

Checksums establish identity relative to these recorded values. They do not independently authenticate the publisher, RPC endpoint, initial committee or canonical network.

## 5. Run the complete offline reproduction

Linux:

```bash
.venv/bin/python verify_study.py --output runs/first-run
```

Windows:

```powershell
.\.venv\Scripts\python.exe .\verify_study.py --output .\runs\first-run
```

Choose a new output directory for each run. For example, use `runs/second-run` next time. Omitting `--output` creates a timestamped directory under `runs/`.

The launcher performs these stages:

1. Check the current distribution manifest and the exact original archive identity.
2. Extract the original publication into the new output directory.
3. Execute its complete ten-step audit: original and repeat-capture records, three original execution headers per capture, thirteen controls, certificate comparisons and encoding recipes.
4. Verify every one of the 187 distinct saved certificates using py_ecc and execute the seven separately generated synthetic-chain scenarios.
5. Reconstruct all 175 newly captured execution headers, bind their block numbers and hashes to the signed records, and repeat their local gasUsed mutations.
6. Check the current article's numerical claims and figure values.
7. Check distribution integrity again.

The final summary reports **four executed subprocess stages**. The integrity and extraction operations are part of the launcher, not separate cryptographic experiments.

The second-library stage prints progress into its own log after the first certificate and every twenty certificates. Pairing calculations take time. A complete run took a few minutes in the recorded environment; runtime is not a production-performance benchmark.

Run without Python `-O` or `-OO`. Some preserved input readers use assertions, and both launchers explicitly reject optimized execution.

## 6. Locate and interpret the output

Under your chosen output directory:

| File or directory | What to inspect |
|---|---|
| review-summary.json | Overall status, interpreter, commands, timings, exit codes and errors |
| logs/01-original-ten-step-audit.log | Original audit progress and final result |
| baseline/audit-summary.json | All ten original checks and their individual log paths |
| logs/02-complete-second-library-and-chain-controls.log | Progress through 187 certificate checks and final summary |
| followup/summary.json | 187 passes, 350 covered observations, and seven scenario outcomes |
| followup/all-certificates-pyecc.json | Every distinct certificate's identity and its A/B observation mapping |
| followup/synthetic-chain-controls.json | Public test scalars, all synthetic records/certificates and exact rejection stages |
| logs/03-all-175-execution-headers.log | Full saved-header verification summary |
| headers.json | All 175 block numbers, signed hashes, reconstructed hashes and mutation results |
| logs/04-article-and-figure-values.log | Publication consistency result |

Expected final fields:

```json
{
  "status": "passed",
  "expected_stages": 4,
  "stages_completed": 4,
  "error": null
}
```

Each stage must have exit code zero. A partial run or a copied old summary is not a successful reproduction. When a stage fails, the launcher stops, saves a failed summary and exits nonzero.

The original publication, raw observations and packaged result files are not regenerated in place. Fresh outputs live under the directory you chose.

## 7. Understand what the new checks establish

### Complete second-library coverage

The two saved captures contain 350 record/certificate observations. Because 163 certificates are byte-identical between captures and twelve differ, they contain 187 distinct certificates over 175 record commitments.

The follow-up deduplicates exact record/certificate pairs, checks every distinct certificate with py_ecc, and maps each result back to every observation it covers. It also reruns both complete chains under the original observed anchor.

pyblst and Axyl share blst. py_ecc supplies a different cryptographic implementation. This is still not an independent authentication of the starting committee or a production light-client implementation.

### All referenced execution headers

The 29 October capture requested the block number in `parent_state` for every original epoch. Each response is bound to its method, request ID, exact requested block number, returned block number and signed block hash.

Every reconstructed RLP/Keccak hash matched both the RPC's block hash and the corresponding signed record reference. A local gasUsed modification changed the reconstructed hash for every header.

These are checks of committed headers. They do not replay transactions, validate every state transition or prove transaction inclusion. The new HTTP observations came from the same documented RPC; they are not a second independent node.

### Seven synthetic chain scenarios

| Scenario | Individual signature equations | Expected chain result |
|---|---|---|
| Authorized committee handoff and linked chain | Valid | Accept |
| Wrong parent link after re-signing the modified records | Valid | Reject parent link |
| Linked records signed by an unannounced committee | Valid | Reject committee handoff |
| Two-of-four valid aggregate signature | Valid | Reject insufficient three-of-four quorum |
| Three named signers do not match the aggregate | One fails | Reject BLS signature |
| Valid chain with a different expected anchor | Valid | Reject anchor mismatch |
| Alternative synthetic chain with its own supplied anchor | Valid | Accept under that supplied anchor |

Each chain has three records. The test scalars are public fixtures. These scenarios demonstrate the separate roles of cryptography, quorum, committee authorization, parent linkage and initial trust. Acceptance under a synthetic supplied anchor is an expected property of the research verifier, not evidence that Rayls accepted a counterfeit chain.

## 8. Run individual checks when diagnosing a failure

After a full run has extracted the original archive, use its extracted directory as the `--publication` argument. The examples below assume `runs/first-run`.

```bash
.venv/bin/python followup/verify_followup.py \
  --publication runs/first-run/extracted-original/DAVID_Week4_Publication \
  --output runs/certificate-diagnostic

.venv/bin/python followup/check_headers.py \
  --publication runs/first-run/extracted-original/DAVID_Week4_Publication \
  --capture-dir followup/data/headers-20261029 \
  --output runs/header-diagnostic.json

.venv/bin/python followup/check_publication.py
```

On Windows, use `.\.venv\Scripts\python.exe` and put each command on one line instead of using the Linux `\` continuation characters.

All these commands use saved inputs. Each diagnostic output must be a new path.

## 9. Optional fresh read-only RPC capture

This operation is **not** part of the default audit and needs internet access:

```bash
.venv/bin/python followup/check_headers.py \
  --publication runs/first-run/extracted-original/DAVID_Week4_Publication \
  --capture-dir runs/new-header-capture \
  --capture \
  --output runs/new-header-checks.json
```

Read-only methods are `eth_chainId`, `web3_clientVersion` and `eth_getBlockByNumber`. There is no transaction-signing or submission method. Requests are limited to the fixed 175 historical block references, in batches of at most ten.

The fetcher refuses to replace an existing capture directory. It preserves UTC request/response times, exact HTTP body text and parsed responses. HTTP failures, JSON-RPC errors and missing results are failures or unavailable observations, never zero headers.

A new capture is a new observation. It does not replace the old observations or authenticate their starting anchor.

## 10. Inspect public CI honestly

The public repository is [david-rayls-checkpoint-study](https://github.com/davidvnvn276/david-rayls-checkpoint-study). Check its [Actions page](https://github.com/davidvnvn276/david-rayls-checkpoint-study/actions) for the actual run and commit.

The workflow at `.github/workflows/verify-checkpoints.yml` checks out the repository, verifies the distribution manifest, installs the pinned dependencies, executes `verify_study.py` directly from the repository root, and retains reports and logs as an artifact. It does not depend on an extra outer ZIP. It performs saved-data reproduction; it does not make live RPC queries.

The existence of a workflow definition is not a successful public run. During the 29 October repository review, commit `18a2c211dd8c89629daf331dab25fa50733c16aa` had no Actions runs: its workflow was only under `ci/`, and its commands expected a separately uploaded outer ZIP. The repository-ready definition supplied here uses the required workflow location and runs the checked-out files directly. Local successful execution is recorded separately. Only an actual completed public run against a stated commit should be described as a public CI pass.

Artifacts have a retention period. The saved follow-up results inside this distribution remain available independently of temporary CI artifacts.

## 11. Troubleshooting

| Symptom | Action |
|---|---|
| Script or requirements file not found | Fully extract the downloaded source ZIP and open the folder containing verify_study.py |
| `py` or `python3.12` not found | Install Python 3.12 or use the actual full interpreter path |
| PowerShell blocks activation | Call the environment interpreter directly; activation is unnecessary |
| `ModuleNotFoundError` | Install the lock with the same interpreter used to run the study |
| Native wheel installation fails | Save the platform and pip error; the recorded environment is Linux/Python 3.12 |
| Output already exists | Choose a new directory or omit `--output` |
| Hash mismatch | Inspect the named file and compare with a clean extraction; do not remove the check |
| Second-library stage appears slow | Inspect its log for certificate progress; do not treat a still-running process as a pass |
| Missing header or RPC error | Preserve the error; it is not a zero value or a cryptographic failure by itself |
| Chain rejected with valid individual signatures | Inspect the parent, expected committee, quorum and supplied anchor independently |

A useful reproduction report includes the OS, Python version, exact command, failed stage and its log. No credentials are needed.

## 12. Limits that remain

- The initial mainnet committee was observed from the official RPC. It was not independently authenticated out of band.
- The bootstrap documents inspected at the pinned source commit ask operators to obtain genesis and committee files from the network operator. This review did not obtain and authenticate those deployment artifacts.
- The complete saved certificate review does not replay execution or establish live bridge settlement, validator organizational independence, throughput, latency or binary attestation.
- The header follow-up checks the same 175 commitments, not a larger epoch range.
- The exact operational reason for the twelve certificate variants remains unestablished.
- Synthetic controls test the offline research verifier. They do not test the live network's acceptance of malformed inputs.

The useful result is narrower and reproducible: the saved signed sequence, alternative certificates and all referenced header commitments are consistent under the explicitly recorded starting committee.
