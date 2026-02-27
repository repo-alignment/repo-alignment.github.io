from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    raise SystemExit(1)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid json {path}: {exc}")


def validate_results_contract(results) -> None:
    if not isinstance(results, list) or not results:
        fail("data/results_main.json must be a non-empty list")

    required_result_keys = {"experiment_id", "dataset", "model", "method", "lc", "wr", "source"}
    valid_datasets = {"ultrafeedback", "multipref"}
    valid_models = {"mistral", "llama"}
    valid_methods = {"dpo", "re_dpo", "ipo", "re_ipo", "simpo", "re_simpo", "cpo", "re_cpo"}

    for idx, item in enumerate(results):
        if set(item.keys()) != required_result_keys:
            fail(f"results_main.json row {idx} has wrong keys")
        if item["dataset"] not in valid_datasets:
            fail(f"invalid dataset at row {idx}")
        if item["model"] not in valid_models:
            fail(f"invalid model at row {idx}")
        if item["method"] not in valid_methods:
            fail(f"invalid method at row {idx}")
        if not isinstance(item["lc"], (int, float)) or not isinstance(item["wr"], (int, float)):
            fail(f"lc/wr must be numeric at row {idx}")


def validate_json_contracts() -> None:
    results = load_json(ROOT / "data" / "results_main.json")
    links = load_json(ROOT / "data" / "links.json")
    meta = load_json(ROOT / "data" / "site_meta.json")

    validate_results_contract(results)

    required_links = {"paper_url", "code_url"}
    if set(links.keys()) != required_links:
        fail("data/links.json keys mismatch")
    for key in required_links:
        if not isinstance(links[key], str) or not links[key].strip():
            fail(f"data/links.json {key} must be a non-empty string")

    if links["code_url"] != "https://github.com/XiaoyangCao1113/RE-PO":
        fail("data/links.json code_url must point to https://github.com/XiaoyangCao1113/RE-PO")
    if links["paper_url"] != "https://arxiv.org/abs/2509.24159":
        fail("data/links.json paper_url must point to https://arxiv.org/abs/2509.24159")

    required_meta = {
        "project_name",
        "tagline",
        "conference",
        "year",
        "license",
        "paper_badge_text",
        "authors",
        "affiliations",
    }
    if set(meta.keys()) != required_meta:
        fail("data/site_meta.json keys mismatch")
    if not isinstance(meta["year"], int):
        fail("data/site_meta.json year must be an integer")
    for field in ("project_name", "tagline", "conference", "license", "paper_badge_text"):
        if not isinstance(meta[field], str) or not meta[field].strip():
            fail(f"data/site_meta.json {field} must be a non-empty string")
    for field in ("authors", "affiliations"):
        if not isinstance(meta[field], list) or not meta[field]:
            fail(f"data/site_meta.json {field} must be a non-empty list")
        if not all(isinstance(v, str) and v.strip() for v in meta[field]):
            fail(f"data/site_meta.json {field} must only contain non-empty strings")


class ImgAltChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.img_without_alt = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "img":
            return
        attr = dict(attrs)
        if "alt" not in attr or not str(attr["alt"]).strip():
            self.img_without_alt.append(attr.get("src", "<unknown>"))


def validate_html_and_links() -> None:
    html_path = ROOT / "index.html"
    html = html_path.read_text(encoding="utf-8")

    if "<title>" not in html or "</title>" not in html:
        fail("index.html missing <title>")

    checker = ImgAltChecker()
    checker.feed(html)
    if checker.img_without_alt:
        fail(f"images missing alt text: {checker.img_without_alt}")

    refs = re.findall(r"(?:href|src)=\"([^\"]+)\"", html)
    for ref in refs:
        if ref.startswith(("http://", "https://", "#", "mailto:", "javascript:")):
            continue
        if ref == "":
            continue
        local_ref = ref.split("?", 1)[0].split("#", 1)[0]
        local = (ROOT / local_ref).resolve()
        if not local.exists():
            fail(f"broken local reference in index.html: {ref}")


def validate_content_contract() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")

    required_nav = ["#contributions", "#method", "#results", "#citation"]
    for anchor in required_nav:
        if f'href="{anchor}"' not in html:
            fail(f"missing nav anchor {anchor}")

    forbidden_tokens = [
        'href="#tldr"',
        'id="tldr"',
        "Core Idea",
        "Target Metrics",
        "<h2>Scope</h2>",
        "Contact",
        "mailto:",
    ]
    for token in forbidden_tokens:
        if token in html:
            fail(f"forbidden content token found: {token}")

    required_snippets = [
        "Accepted to ICLR 2026",
        '<h2 id="contributions-title">Key Contributions</h2>',
        "🔴 The Problem",
        "💡 Our Method (RE-PO)",
        "🚀 Key Results",
        '<h2 id="results-title">Key Results</h2>',
        "DPO, IPO, SimPO, and CPO",
        '<h3 id="noise-robustness-title">Noise Robustness</h3>',
        "one_annotator_eta.png",
        "two_annotators_eta.png",
        '<h2 id="citation-title">Citation</h2>',
        'id="cta-code"',
    ]
    for snippet in required_snippets:
        if snippet not in html:
            fail(f"missing required content snippet: {snippet}")
    if not all(label in html for label in (">Paper<", ">Code<", ">Citation<")):
        fail("Hero section must expose Paper/Code/Citation text buttons")



if __name__ == "__main__":
    validate_json_contracts()
    validate_html_and_links()
    validate_content_contract()
    print("OK: site validation passed")
