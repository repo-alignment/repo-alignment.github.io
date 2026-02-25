# RE-PO Project Website (v1.3)

Static GitHub Pages site for **RE-PO: Robust Enhanced Policy Optimization for LLM Alignment**.

## v1.3 Highlights

- ICLR 2026 badge + author and affiliation strip.
- Homepage sections: `Hero`, `TL;DR`, `Method`, `Preference Duel Cases`, `Results`, `Resources`, `Citation`.
- New `Preference Duel Carousel` with 6 Phase A qualitative cases from camera-ready appendix.
- GIF-first duel media (`gif`) with backup `mp4/webm` links.
- Existing method animations remain available via `method_media.json`.

## Local Development

```bash
cd re-po-project-page
python scripts/validate_site.py
python -m http.server 8000
# open http://localhost:8000
```

## Media Generation

```bash
cd re-po-project-page
pip install -r scripts/requirements-anim.txt
python scripts/generate_method_media.py
python scripts/build_preference_case_media.py
python scripts/validate_site.py
```

Generated duel outputs:

- `assets/cases/<case_id>.gif`
- `assets/cases/<case_id>.mp4`
- `assets/cases/<case_id>.webm`
- `assets/cases/<case_id>.png`

## Data Contracts

### `data/results_main.json`

- `experiment_id` (string)
- `dataset` (`ultrafeedback|multipref`)
- `model` (`mistral|llama`)
- `method` (`dpo|re_dpo`)
- `lc` (number)
- `wr` (number)
- `source` (`paper_camera_ready`)

### `data/links.json`

- `paper_url`
- `code_url`
- `arxiv_url`
- `issues_url`
- `slides_url`

Empty URL values are hidden automatically in the UI.

### `data/site_meta.json`

- `project_name`
- `tagline`
- `conference`
- `year`
- `contact_email`
- `license`
- `paper_badge_text`
- `authors` (string array)
- `affiliations` (string array)

### `data/method_media.json`

Top-level keys: `flow`, `reliability`.

Each entry includes:

- `title`
- `mp4`
- `webm`
- `gif`
- `poster`
- `alt`
- `caption`

### `data/preference_cases.json`

- `case_id`
- `phase` (`appendix|model_pair`)
- `dataset`
- `model_pair`
- `prompt`
- `left_label`
- `right_label`
- `left_text`
- `right_text`
- `winner` (`left|right|tie`)
- `reason_short`
- `confidence_signal`
- `source`
- `source_ref`
- `source_badge`

### `data/preference_media.json`

Object keyed by `case_id`.

Each item includes:

- `gif`
- `mp4`
- `webm`
- `poster`
- `alt`
- `duration_ms`

## Deployment (GitHub Pages)

1. Push to `main`.
2. Repository `Settings -> Pages`.
3. Source: `Deploy from a branch`.
4. Branch: `main`, Folder: `/ (root)`.
5. Wait for Pages build and verify live URL.
