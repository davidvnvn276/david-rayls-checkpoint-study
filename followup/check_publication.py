"""Check article counts, figure dimensions, displayed samples and unchanged logos."""
import base64
import hashlib
import json
from pathlib import Path
import re
import struct
from xml.etree import ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def logos(svg):
    return [base64.b64decode(value.split(",", 1)[1])
            for node in ET.fromstring(svg).iter()
            for key, value in node.attrib.items()
            if key.endswith("href") and value.startswith("data:image/")]


def main():
    article = (ROOT / "ARTICLE_COPY.md").read_text()
    illustrated = (ROOT / "ARTICLE.md").read_text()
    html = (ROOT / "ARTICLE.html").read_text()
    data = json.loads((ROOT / "figure-data.json").read_text())
    summary = json.loads((ROOT / "followup/results/summary.json").read_text())
    headers = json.loads((ROOT / "followup/results/headers-20261029.json").read_text())
    certificates = json.loads((ROOT / "followup/results/all-certificates-pyecc.json").read_text())
    controls = json.loads((ROOT / "followup/results/synthetic-chain-controls.json").read_text())
    require(summary["second_library_passes"] == len(certificates["checks"]) == 187, "Second-library coverage")
    require(sum(len(c["observations"]) for c in certificates["checks"]) == 350, "Observation mapping")
    require(headers["headers_verified"] == len(headers["headers"]) == 175, "Header coverage")
    require({r["epoch"] for r in headers["headers"]} == set(range(175)), "Header epoch coverage")
    require(len(controls["scenarios"]) == 7 and controls["positive_controls"] == 2 and controls["expected_rejections"] == 5, "Control coverage")
    require(data["distinct_certificates_pyecc"] == 187 and data["new_execution_headers"] == 175 and data["new_synthetic_scenarios"] == 7, "Figure-data counts")
    for phrase in ["187 distinct", "175 reconstructed execution-header hashes", "350 saved observations", "seven offline scenarios"]:
        require(phrase in article, "Missing article claim: " + phrase)
    require("![" not in article, "Clean copy contains image syntax")
    require(illustrated.count("![") == html.count("<img ") == 4, "Illustrated figure coverage")
    require("40817105726" not in article + illustrated + html, "Unrelated Enygma CI run linked")
    with zipfile.ZipFile(ROOT / "original-publication.zip") as archive:
        expected_logo = logos(archive.read("DAVID_Week4_Publication/images/01-checkpoint-banner.svg").decode())
    require(len(expected_logo) == 1, "Original logo coverage")
    figures = []
    for index, path in enumerate(sorted((ROOT / "images").glob("*.png")), 1):
        raw = path.read_bytes()
        require(raw[:8] == b"\x89PNG\r\n\x1a\n", "Invalid PNG")
        size = struct.unpack(">II", raw[16:24])
        require(size == (3200, 1280 if index == 1 else 1800), "Figure dimensions")
        svg = path.with_suffix(".svg").read_text()
        require(logos(svg) == expected_logo, "Original logo bytes changed")
        figures.append({"file": path.name, "pixels": list(size),
                        "original_logo_sha256": hashlib.sha256(expected_logo[0]).hexdigest()})
    require(len(figures) == 4, "Expected four figures")
    svg = (ROOT / "images/04-authority-and-header-commitments.svg").read_text()
    require("175 reconstructed execution headers" in svg and "all 175 matches" in svg,
            "Updated header coverage label")
    require("Three example rows shown" in svg, "Sample-row boundary")
    for epoch in [0, 173, 174]:
        row = next(r for r in headers["headers"] if r["epoch"] == epoch)
        require(data["figure_04_header_hashes"][str(epoch)] == row["signed_hash"], "Example header data")
        short = row["signed_hash"][:10] + "..." + row["signed_hash"][-6:]
        require(short in svg, "Displayed abbreviated header hash")
    print(json.dumps({"status": "passed", "figures": figures,
                      "article_words": len(article.split()), "scope": "Publication consistency, not a substitute for cryptographic execution."}, indent=2))


if __name__ == "__main__":
    main()
