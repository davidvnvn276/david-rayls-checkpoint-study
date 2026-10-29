"""Capture or verify all 175 execution headers referenced by the fixed study.

Only --capture queries the documented public RPC. The default check uses saved
responses and proves header commitments relative to the original observed anchor,
not full transaction execution or independently authenticated chain identity.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import urllib.request


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inputs(publication):
    common = load(publication / "evidence/review/review_common.py", "headers_review_common")
    verifier, original, recaptured, anchor = common.inputs()
    verifier.verify_chain(original, anchor)
    sys.path.insert(0, str(publication / "evidence/original"))
    header = load(publication / "evidence/original/verify_headers.py", "headers_review_encoder")
    return original, anchor, header


def capture(directory, pairs, endpoint):
    require(endpoint.startswith("https://"), "An HTTPS public endpoint is required")
    directory.mkdir(parents=True, exist_ok=False)

    def request(name, batch):
        body = json.dumps(batch, separators=(",", ":")).encode()
        item = {"endpoint": endpoint,
                "requested_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "request": batch, "request_body_utf8": body.decode()}
        req = urllib.request.Request(endpoint, data=body,
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0",
                     "Origin": "https://dapp.rayls.com"})
        try:
            with urllib.request.urlopen(req, timeout=35) as response:
                raw = response.read()
                item["http_status"] = response.status
                item["response_body_utf8"] = raw.decode()
                item["response"] = json.loads(raw)
        except Exception as exc:
            item["capture_error"] = f"{type(exc).__name__}: {exc}"
            (directory / name).write_text(json.dumps(item, indent=2) + "\n")
            raise
        item["received_at_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (directory / name).write_text(json.dumps(item, indent=2) + "\n")
        return item["response"]

    meta = request("metadata.json", [
        {"jsonrpc": "2.0", "id": 0, "method": "eth_chainId", "params": []},
        {"jsonrpc": "2.0", "id": 1, "method": "web3_clientVersion", "params": []}])
    require(next(x for x in meta if x["id"] == 0).get("result") == hex(72957),
            "Wrong reported chain ID; capture stopped")
    for start in range(0, 175, 10):
        epochs = range(start, min(start + 10, 175))
        batch = [{"jsonrpc": "2.0", "id": epoch,
                  "method": "eth_getBlockByNumber",
                  "params": [hex(pairs[epoch][0]["parent_state"]["number"]), False]}
                 for epoch in epochs]
        request(f"headers-{start:03d}.json", batch)
        print(f"Captured checkpoint headers for epochs {start} through {min(start + 9, 174)}", flush=True)
        time.sleep(0.15)


def verify(directory, pairs, anchor, header):
    from Crypto.Hash import keccak

    metadata = json.loads((directory / "metadata.json").read_text())
    require(json.loads(metadata["request_body_utf8"]) == metadata["request"], "Metadata request body")
    require(json.loads(metadata["response_body_utf8"]) == metadata["response"], "Metadata response body")
    require(metadata["http_status"] == 200, "Metadata HTTP status")
    meta = {x["id"]: x for x in metadata["response"]}
    require(meta[0].get("result") == hex(72957), "Captured reported chain ID")
    require(metadata["request"] == [
        {"jsonrpc": "2.0", "id": 0, "method": "eth_chainId", "params": []},
        {"jsonrpc": "2.0", "id": 1, "method": "web3_clientVersion", "params": []}], "Metadata methods")
    rows = []
    seen = set()
    manifest = {}
    for path in sorted(directory.glob("headers-*.json")):
        raw = path.read_bytes();manifest[path.name] = hashlib.sha256(raw).hexdigest()
        item = json.loads(raw)
        require(item["endpoint"] == metadata["endpoint"] and item["http_status"] == 200, "Captured endpoint/status")
        require(json.loads(item["request_body_utf8"]) == item["request"], "Raw request body binding")
        require(json.loads(item["response_body_utf8"]) == item["response"], "Raw response body binding")
        reqs = {x["id"]: x for x in item["request"]}
        replies = {x["id"]: x for x in item["response"]}
        require(len(reqs) == len(item["request"]) == len(replies) == len(item["response"]), "Unique batch IDs")
        require(set(reqs) == set(replies), "Complete batch response coverage")
        for epoch in sorted(reqs):
            require(epoch in pairs and epoch not in seen, "Unique referenced epoch")
            seen.add(epoch)
            number = pairs[epoch][0]["parent_state"]["number"]
            expected = pairs[epoch][0]["parent_state"]["hash"]
            req, response = reqs[epoch], replies[epoch]
            require(req["method"] == "eth_getBlockByNumber" and req["params"] == [hex(number), False], "Requested header binding")
            require("error" not in response and isinstance(response.get("result"), dict), "Unavailable header is not a zero header")
            block = response["result"]
            require(int(block["number"], 16) == number, "Returned block number")
            encoded = header.encode_header(block)
            digest = "0x" + keccak.new(digest_bits=256, data=encoded).hexdigest()
            require(digest == block["hash"] == expected, "RLP/RPC/signed-header commitment mismatch")
            changed = dict(block, gasUsed=hex(int(block["gasUsed"], 16) + 1))
            changed_hash = "0x" + keccak.new(digest_bits=256, data=header.encode_header(changed)).hexdigest()
            require(changed_hash != expected, "gasUsed mutation was not detected")
            rows.append({"epoch": epoch, "block": number, "signed_hash": expected,
                         "reconstructed_hash": digest, "rlp_bytes": len(encoded),
                         "gasUsed_mutation_detected": True,
                         "source_batch": path.name})
    require(seen == set(range(175)), "Expected header coverage for all 175 original epochs")
    manifest["metadata.json"] = hashlib.sha256((directory / "metadata.json").read_bytes()).hexdigest()
    return {"status": "passed", "headers_verified": len(rows),
            "local_header_mutations_detected": sum(r["gasUsed_mutation_detected"] for r in rows),
            "original_epoch_range": [0, 174], "observed_anchor_record_hash": anchor["record_hash"],
            "reported_chain_id": 72957, "reported_client_version": meta[1].get("result"),
            "capture_started_at_utc": metadata["requested_at_utc"],
            "raw_capture_sha256": manifest, "headers": sorted(rows, key=lambda x: x["epoch"]),
            "scope": "All execution-header commitments referenced by the original 175 records; no transaction replay, receipt inclusion proof or independent starting-anchor authentication."}


def main():
    if not __debug__:
        raise SystemExit("Run without Python optimization; preserved input readers use assertions.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication", required=True)
    parser.add_argument("--capture-dir", required=True)
    parser.add_argument("--output", required=True, help="New JSON result file")
    parser.add_argument("--capture", action="store_true", help="Perform fresh read-only public RPC requests")
    parser.add_argument("--endpoint", default="https://mainnet-rpc.rayls.com/")
    args = parser.parse_args()
    directory = Path(args.capture_dir).resolve()
    output = Path(args.output).resolve()
    require(not output.exists(), "Result file already exists")
    pairs, anchor, header = inputs(Path(args.publication).resolve())
    if args.capture:
        capture(directory, pairs, args.endpoint)
    result = verify(directory, pairs, anchor, header)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["status", "headers_verified", "local_header_mutations_detected", "reported_chain_id", "reported_client_version", "scope"]}, indent=2))


if __name__ == "__main__":
    main()
