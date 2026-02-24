# RE-PO Project Website (v1.1)

Static GitHub Pages site for **RE-PO: Robust Enhanced Policy Optimization for LLM Alignment**.

## MVP v1.1 Highlights

- ICLR 2026 badge + author/affiliation strip.
- Homepage sections: `Hero`, `TL;DR`, `Method`, `Results`, `Resources`, `Citation`.
- Updated TL;DR terminology: `Research Gap / Method / Performance`.
- Animated method module with tabbed `Flow` and `Reliability` views.
- Video-first delivery (`WebM/MP4`) with `GIF` fallback.

## Local Development

```bash
cd re-po-project-page
python scripts/validate_site.py
python -m http.server 8000
# open http://localhost:8000
```

## Animation Asset Generation

```bash
cd re-po-project-page
pip install -r scripts/requirements-anim.txt
python scripts/generate_method_media.py
python scripts/validate_site.py
```

Generated files:

- `assets/media/flow_method.mp4`
- `assets/media/flow_method.webm`
- `assets/media/flow_method.gif`
- `assets/media/reliability_method.mp4`
- `assets/media/reliability_method.webm`
- `assets/media/reliability_method.gif`

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

## Deployment (GitHub Pages)

1. Push to `main`.
2. Repository `Settings -> Pages`.
3. Source: `Deploy from a branch`.
4. Branch: `main`, Folder: `/ (root)`.
5. Wait for Pages build and verify live URL.
