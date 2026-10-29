# Checkpoint Study Review - 29 October 2026

## Scope and source identity

This review inspected the article supplied as a Binance Square PDF and downloaded the publication archive from repository commit `6442353baa0096fe260c5d5f2a8c757e40de94d4`.

The downloaded archive's Git blob identity matched `ec5a38812268db0a5ba9c065fae1bec18b09642a`. Its SHA-256 is `b0e51f0b6cd4bc4ed51bbd336108812b395201fcf08f6586cbf3c5e6ed892bdc`. The archive is retained unchanged as `original-publication.zip`.

The pinned `mainnet-v1.4.1` annotated tag was dereferenced again and points to commit `6909618ba3d178884e613b329a99816ba546f62e`. All nine source blobs matched the corresponding entries in a fresh GitHub tree retrieval. A source tag or node version string is not remote binary attestation.

## Original results reproduced

All ten stages of the original complete launcher passed in a fresh Python 3.12.14 environment with the supplied lock. This reran cryptographic verification, not just file checksums.

The results support the published claims: 175 records in each of two saved captures; all record digests and aggregate signatures valid under the observed anchor; 174 parent links and handoffs per sequence; one seven-to-eight-key transition; twelve alternative certificates over unchanged records; the thirteen expected original control outcomes; and three original execution-header samples. The BLAKE3/u32 recipe matched all records, while the three deliberately different recipes matched none.

The published figures communicate these findings and their scope correctly. No numerical contradiction between the article's central claims and the reproduced original evidence was found.

## Follow-up executed

1. Complete second-library coverage: all 187 distinct saved certificates passed py_ecc. Their observation mappings cover 350 captured observations of 175 record commitments. This includes previously sampled certificates; it is not 187 additional checkpoints.
2. Full execution-header coverage: new read-only requests on 29 October retrieved all 175 block headers referenced by the original record range. Every reconstructed RLP/Keccak hash matched the RPC-reported hash and signed record reference. All 175 local gasUsed mutations changed the reconstructed hash.
3. Seven three-record synthetic-chain controls: authorized linked chains and an alternative chain under its own supplied anchor intentionally passed. Wrong parent linkage, unauthorized handoff, insufficient quorum, a mismatched bitmap/signature and a different expected anchor were rejected at their expected stages.
4. Publication checks: four PNG/SVG figures, embedded original logo bytes, header sample values and article counts passed consistency checks. The fourth figure now states full 175-header coverage while showing three illustrative rows.

The synthetic controls run against the offline verifier. Their signatures use public test scalars. No synthetic record was submitted to a live node. Fresh header data came from the same documented RPC; this is not a second independent node.

## Complete launcher validation

The new preserving launcher executed all four stages successfully in 206.528 seconds in the recorded environment. Its reports and logs are included under `followup/results/full-launcher-*`. Its output included a fresh rerun of all 187 certificate checks, the seven controls and the 175-header reconstruction.

After validation, only this report, run logs and release-tag provenance were added, and the distribution manifest was refreshed. Executable code and captured research inputs were not changed. Timing is context, not a production-performance claim.

## Limits and public status

The initial committee is still an observed input, not independently authenticated out of band. The inspected bootstrap instructions require network-operator-supplied genesis and committee files; this review did not obtain and authenticate those mainnet artifacts. No claim is made that such artifacts do not exist elsewhere.

The study does not replay execution, establish live bridge settlement, identify validator organizations, measure throughput/latency, or attest the running binary. The operational cause of the twelve certificate variants remains unestablished.

At the repository check during this review, the checkpoint repository had no GitHub Actions runs. A workflow is supplied, but only an actual successful public run at a specified commit can support a public-CI claim. Local successful execution and prepared workflow syntax are recorded separately.

## Publication changes

The updated article retains the original research question and chronological boundaries, adds the completed follow-up, and gives one preserving reproduction command. The current root README is addressed to readers reproducing the work. It supplies environment setup, Linux/Windows commands, expected outputs, file paths and troubleshooting, without author-preparation instructions or reward-score claims.
