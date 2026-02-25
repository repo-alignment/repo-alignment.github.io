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


def validate_json_contracts() -> None:
    results = load_json(ROOT / "data" / "results_main.json")
    links = load_json(ROOT / "data" / "links.json")
    meta = load_json(ROOT / "data" / "site_meta.json")
    method_media = load_json(ROOT / "data" / "method_media.json")
    pref_cases = load_json(ROOT / "data" / "preference_cases.json")
    pref_media = load_json(ROOT / "data" / "preference_media.json")

    validate_results_contract(results)

    required_links = {"paper_url", "code_url", "arxiv_url", "issues_url", "slides_url"}
    if set(links.keys()) != required_links:
        fail("data/links.json keys mismatch")
    for key in required_links:
        if not isinstance(links[key], str):
            fail(f"data/links.json {key} must be a string")

    required_meta = {
        "project_name",
        "tagline",
        "conference",
        "year",
        "contact_email",
        "license",
        "paper_badge_text",
        "authors",
        "affiliations",
    }
    if set(meta.keys()) != required_meta:
        fail("data/site_meta.json keys mismatch")
    if not isinstance(meta["year"], int):
        fail("data/site_meta.json year must be an integer")
    for field in ("project_name", "tagline", "conference", "contact_email", "license", "paper_badge_text"):
        if not isinstance(meta[field], str) or not meta[field].strip():
            fail(f"data/site_meta.json {field} must be a non-empty string")
    for field in ("authors", "affiliations"):
        if not isinstance(meta[field], list) or not meta[field]:
            fail(f"data/site_meta.json {field} must be a non-empty list")
        if not all(isinstance(v, str) and v.strip() for v in meta[field]):
            fail(f"data/site_meta.json {field} must only contain non-empty strings")

    required_method_media_keys = {"title", "mp4", "webm", "gif", "poster", "alt", "caption"}
    for media_name in ("flow", "reliability"):
        if media_name not in method_media:
            fail(f"data/method_media.json missing {media_name}")
        media_item = method_media[media_name]
        if set(media_item.keys()) != required_method_media_keys:
            fail(f"data/method_media.json {media_name} keys mismatch")
        for field in required_method_media_keys:
            if not isinstance(media_item[field], str) or not media_item[field].strip():
                fail(f"data/method_media.json {media_name}.{field} must be a non-empty string")
        for path_field in ("mp4", "webm", "gif", "poster"):
            path = (ROOT / media_item[path_field]).resolve()
            if not path.exists():
                fail(f"missing media asset for {media_name}.{path_field}: {media_item[path_field]}")

    required_case_keys = {
        "case_id",
        "phase",
        "dataset",
        "model_pair",
        "prompt",
        "left_label",
        "right_label",
        "left_text",
        "right_text",
        "winner",
        "reason_short",
        "confidence_signal",
        "source",
        "source_ref",
        "source_badge",
    }
    if not isinstance(pref_cases, list) or len(pref_cases) != 6:
        fail("data/preference_cases.json must contain exactly 6 cases")

    case_ids = []
    for idx, item in enumerate(pref_cases):
        if set(item.keys()) != required_case_keys:
            fail(f"preference_cases row {idx} has wrong keys")
        if item["phase"] not in {"appendix", "model_pair"}:
            fail(f"preference_cases row {idx} has invalid phase")
        if item["winner"] not in {"left", "right", "tie"}:
            fail(f"preference_cases row {idx} has invalid winner")
        for field in required_case_keys - {"winner"}:
            if not isinstance(item[field], str) or not item[field].strip():
                fail(f"preference_cases row {idx} field {field} must be non-empty string")
        if item["phase"] == "appendix" and item["source_badge"] != "camera-ready appendix":
            fail(f"preference_cases row {idx} appendix phase must use source_badge='camera-ready appendix'")
        case_ids.append(item["case_id"])

    if len(set(case_ids)) != len(case_ids):
        fail("preference_cases case_id must be unique")

    if not isinstance(pref_media, dict):
        fail("data/preference_media.json must be an object")

    if set(pref_media.keys()) != set(case_ids):
        fail("preference_media keys must match preference_cases case_id set")

    required_pref_media_keys = {"gif", "mp4", "webm", "poster", "alt", "duration_ms"}
    for case_id in case_ids:
        media_item = pref_media[case_id]
        if set(media_item.keys()) != required_pref_media_keys:
            fail(f"preference_media {case_id} keys mismatch")

        for field in ("gif", "mp4", "webm", "poster", "alt"):
            if not isinstance(media_item[field], str) or not media_item[field].strip():
                fail(f"preference_media {case_id}.{field} must be a non-empty string")

        if not isinstance(media_item["duration_ms"], int) or media_item["duration_ms"] <= 0:
            fail(f"preference_media {case_id}.duration_ms must be a positive integer")

        for path_field in ("gif", "mp4", "webm", "poster"):
            path = (ROOT / media_item[path_field]).resolve()
            if not path.exists():
                fail(f"missing preference media asset {case_id}.{path_field}: {media_item[path_field]}")


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
        local = (ROOT / ref).resolve()
        if not local.exists():
            fail(f"broken local reference in index.html: {ref}")


def validate_content_contract() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")

    required_nav = ["#tldr", "#method", "#preference-duel", "#results", "#resources", "#citation"]
    for anchor in required_nav:
        if f'href="{anchor}"' not in html:
            fail(f"missing nav anchor {anchor}")

    if html.count('id="preference-duel"') != 1:
        fail("index.html must contain exactly one preference-duel section")

    forbidden_tokens = ['id="repro"', 'href="#repro"', ">Reproducibility<"]
    for token in forbidden_tokens:
        if token in html:
            fail("reproducibility section/nav should not exist")

    required_snippets = [
        "ICLR 2026 Conference Paper",
        "<h2 id=\"results-title\">Key Results</h2>",
        "<strong>Research Gap:</strong>",
        "<strong>Method:</strong>",
        "<strong>Performance:</strong>",
        "RE-PO consistently improves AlpacaEval 2 LC/WR across UltraFeedback and MultiPref settings.",
        "AlpacaEval 2 Length-Controlled Win Rate (LC) and Win Rate (WR).",
        "Preference Duel Cases",
        "Real response-level differences under noisy preferences.",
        "camera-ready appendix",
    ]
    for snippet in required_snippets:
        if snippet not in html:
            fail(f"missing required content snippet: {snippet}")


if __name__ == "__main__":
    validate_json_contracts()
    validate_html_and_links()
    validate_content_contract()
    print("OK: site validation passed")
