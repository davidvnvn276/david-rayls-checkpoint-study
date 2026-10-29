"""Recheck every distinct saved certificate with py_ecc and test chain authority.

The input is the unchanged publication archive's extracted directory. No network,
wallet, private validator key or transaction submission is used. Public synthetic
scalars below are reproducible test inputs, never live validator credentials.
"""
from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_common(publication):
    spec = importlib.util.spec_from_file_location(
        "checkpoint_followup_common", publication / "evidence/review/review_common.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic_controls(verifier):
    """Hold signature validity apart from parent, handoff, quorum and anchor checks."""
    import base58
    import pyblst
    from pyroaring import BitMap

    scalars = {"A": [101, 102, 103, 104], "B": [102, 103, 104, 105],
               "C": [201, 202, 203, 204]}
    by_key = {}
    committees = {}
    for name, values in scalars.items():
        raw = []
        for scalar in values:
            key = verifier.G2.scalar_mul(scalar).compress()
            by_key[key] = scalar
            raw.append(key)
        committees[name] = [base58.b58encode(k).decode() for k in sorted(raw)]

    def fake_hash(label):
        return "0x" + hashlib.sha256(label.encode()).hexdigest()

    def record(epoch, current, following, parent):
        return {"epoch": epoch, "committee": committees[current],
                "next_committee": committees[following], "parent_hash": parent,
                "parent_state": {"number": epoch + 1,
                                 "hash": fake_hash(f"synthetic execution {epoch}")},
                "parent_consensus": fake_hash(f"synthetic consensus {epoch}")}

    def sign(rec, signer_indices=(0, 1, 2)):
        keys = verifier.committee_bytes(rec)
        digest = verifier.record_digest(rec)
        hashed = pyblst.BlstP1Element.hash_to_group(verifier.intent_message(digest), verifier.DST)
        sig = None
        for i in signer_indices:
            part = hashed.scalar_mul(by_key[keys[i]])
            sig = part if sig is None else sig + part
        return {"epoch_hash": "0x" + digest.hex(),
                "signature": base58.b58encode(sig.compress()).decode(),
                "signed_authorities": base58.b58encode(BitMap(signer_indices).serialize()).decode()}

    def chain(names):
        pairs = {}
        parent = "0x" + "00" * 32
        for epoch, current in enumerate(names):
            following = names[min(epoch + 1, len(names) - 1)]
            rec = record(epoch, current, following, parent)
            cert = sign(rec)
            pairs[epoch] = (rec, cert)
            parent = cert["epoch_hash"]
        return pairs

    def anchor(pairs):
        rec, cert = pairs[0]
        return {"first_epoch": 0, "last_epoch": 2, "record_hash": cert["epoch_hash"],
                "committee_hex": [k.hex() for k in verifier.committee_bytes(rec)],
                "trust_limit": "Synthetic supplied anchor; no canonical-network authentication."}

    valid = chain(["A", "B", "B"])
    expected_anchor = anchor(valid)
    cases = []

    def case(name, pairs, supplied_anchor, expected_accept, expected_reason=None):
        math = [verifier.signature_valid(*pairs[e]) for e in range(3)]
        try:
            verifier.verify_chain(pairs, supplied_anchor)
        except ValueError as exc:
            accepted, reason = False, str(exc)
        else:
            accepted, reason = True, "accepted under the supplied anchor"
        require(accepted == expected_accept, f"Unexpected synthetic outcome: {name}")
        if expected_reason:
            require(reason == expected_reason, f"Unexpected rejection stage: {name}: {reason}")
        cases.append({"case": name, "expected_acceptance": expected_accept,
                      "accepted": accepted, "reason": reason,
                      "individual_signature_equations_valid": math,
                      "pairs": [{"record": pairs[e][0], "certificate": pairs[e][1]}
                                for e in range(3)], "supplied_anchor": supplied_anchor})

    case("authorized handoff and linked chain", valid, expected_anchor, True)

    broken_parent = copy.deepcopy(valid)
    broken_parent[1][0]["parent_hash"] = fake_hash("a different parent")
    broken_parent[1] = (broken_parent[1][0], sign(broken_parent[1][0]))
    broken_parent[2][0]["parent_hash"] = broken_parent[1][1]["epoch_hash"]
    broken_parent[2] = (broken_parent[2][0], sign(broken_parent[2][0]))
    case("valid signatures but wrong parent link", broken_parent, expected_anchor,
         False, "parent link mismatch")

    unauthorized = copy.deepcopy(valid)
    for epoch in [1, 2]:
        parent = unauthorized[epoch - 1][1]["epoch_hash"]
        rec = record(epoch, "C", "C", parent)
        unauthorized[epoch] = (rec, sign(rec))
    case("valid linked signatures but unauthorized committee handoff", unauthorized,
         expected_anchor, False, "unexpected committee")

    low_quorum = copy.deepcopy(valid)
    low_quorum[1] = (low_quorum[1][0], sign(low_quorum[1][0], (0, 1)))
    case("valid aggregate equation but only two of four signers", low_quorum,
         expected_anchor, False, "insufficient signer quorum")

    bitmap = copy.deepcopy(valid)
    bitmap[1][1]["signed_authorities"] = base58.b58encode(BitMap([1, 2, 3]).serialize()).decode()
    case("quorum-sized bitmap does not match aggregate signature", bitmap,
         expected_anchor, False, "BLS verification failed")

    wrong_anchor = dict(expected_anchor, record_hash="0x" + "00" * 32)
    case("valid chain with a different expected anchor", valid, wrong_anchor,
         False, "anchor mismatch")

    alternative = chain(["C", "C", "C"])
    case("alternative synthetic chain with its own supplied anchor", alternative,
         anchor(alternative), True)

    require(len(cases) == 7, "Synthetic scenario coverage")
    require(sum(c["accepted"] for c in cases) == 2, "Synthetic positive coverage")
    for c in cases:
        expected = [True, False, True] if "bitmap" in c["case"] else [True] * 3
        require(c["individual_signature_equations_valid"] == expected,
                "Signature validity was not isolated from authority checks")
    return {"scope": "Seven synthetic offline verifier scenarios; no Rayls records submitted.",
            "public_test_scalars": scalars, "scenarios": cases,
            "positive_controls": 2, "expected_rejections": 5,
            "lesson": "Valid signatures alone do not establish chain links, authorized committee handoffs, quorum, or the provenance of a supplied initial anchor."}


def main():
    if not __debug__:
        raise SystemExit("Run without -O or -OO; the preserved input readers use assertions.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    publication = Path(args.publication).resolve()
    output = Path(args.output).resolve()
    require(not output.is_relative_to(publication), "Keep follow-up outputs outside the publication")
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    common = load_common(publication)
    v, original, recaptured, observed_anchor = common.inputs()
    # Both complete sequences retain the original observed anchor.
    v.verify_chain(original, observed_anchor)
    v.verify_chain(recaptured, observed_anchor)
    require(all(original[e][0] == recaptured[e][0] for e in range(175)),
            "Saved record commitments differ")

    unique = {}
    for capture, pairs in [("A", original), ("B", recaptured)]:
        for epoch, pair in sorted(pairs.items()):
            identity = hashlib.sha256(json.dumps(pair, sort_keys=True,
                                                separators=(",", ":")).encode()).hexdigest()
            entry = unique.setdefault(identity, {"record": pair[0], "certificate": pair[1],
                                                "observations": []})
            entry["observations"].append({"capture": capture, "epoch": epoch})
    require(len(unique) == 187, "Expected 175 original plus 12 different saved certificates")

    rows = []
    for index, (identity, entry) in enumerate(unique.items(), 1):
        ok = v.py_ecc_crosscheck(entry["record"], entry["certificate"])
        require(ok, f"py_ecc rejected certificate {identity}")
        rows.append({"certificate_identity_sha256": identity,
                     "record_hash": entry["certificate"]["epoch_hash"],
                     "epoch": entry["record"]["epoch"],
                     "observations": entry["observations"], "py_ecc_valid": True})
        if index == 1 or index % 20 == 0 or index == len(unique):
            print(f"py_ecc: {index}/{len(unique)} distinct certificates passed", flush=True)
    (output / "all-certificates-pyecc.json").write_text(
        json.dumps({"checks": rows}, indent=2) + "\n", encoding="utf-8")
    controls = synthetic_controls(v)
    (output / "synthetic-chain-controls.json").write_text(
        json.dumps(controls, indent=2) + "\n", encoding="utf-8")
    summary = {"status": "passed", "review_date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "python": sys.version, "captured_observations": 350,
               "distinct_record_commitments": 175, "distinct_certificates_checked_with_py_ecc": 187,
               "covered_observations": sum(len(r["observations"]) for r in rows),
               "second_library_passes": len(rows), "synthetic_scenarios": len(controls["scenarios"]),
               "synthetic_positive_controls": 2, "synthetic_expected_rejections": 5,
               "seconds": round(time.monotonic() - started, 3),
               "scope": "Complete saved-certificate second-library review and separate synthetic offline verifier controls; no live RPC queries or transactions.",
               "trust_limit": "Initial mainnet committee remains observed, not independently authenticated. Deduplicated certificates are not additional checkpoints or independent experiments."}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
