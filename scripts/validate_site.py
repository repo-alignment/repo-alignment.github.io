from __future__ import annotations

import json
import re
import sys
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


def validate_json_contracts() -> None:
    results = load_json(ROOT / "data" / "results_main.json")
    links = load_json(ROOT / "data" / "links.json")
    meta = load_json(ROOT / "data" / "site_meta.json")

    if not isinstance(results, list) or not results:
        fail("data/results_main.json must be a non-empty list")

    required_result_keys = {"experiment_id", "dataset", "model", "method", "lc", "wr", "source"}
    valid_datasets = {"ultrafeedback", "multipref"}
    valid_models = {"mistral", "llama"}
    valid_methods = {"dpo", "re_dpo"}

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

    required_links = {"paper_url", "code_url", "arxiv_url", "issues_url", "slides_url"}
    if set(links.keys()) != required_links:
        fail("data/links.json keys mismatch")

    required_meta = {"project_name", "tagline", "conference", "year", "contact_email", "license"}
    if set(meta.keys()) != required_meta:
        fail("data/site_meta.json keys mismatch")


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
        local = (ROOT / ref).resolve()
        if not local.exists():
            fail(f"broken local reference in index.html: {ref}")


if __name__ == "__main__":
    validate_json_contracts()
    validate_html_and_links()
    print("OK: site validation passed")
