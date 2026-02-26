# RE-PO Project Website (v1.4)

Static GitHub Pages site for **RE-PO: Robust Enhanced Policy Optimization for LLM Alignment**.

## v1.4 Highlights

- Explicit positioning as an **ICLR 2026 Conference Paper**.
- Simplified information architecture: `Hero`, `TL;DR`, `Method`, `Results`, `Citation`.
- Removed dynamic media modules and duel-case sections for cleaner reading flow.
- Kept citation copy workflow and minimal contact entry.

## Local Development

```bash
cd re-po-project-page
python scripts/validate_site.py
python -m http.server 8000
# open http://localhost:8000
```

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

## Deployment (GitHub Pages)

1. Push to `main`.
2. Repository `Settings -> Pages`.
3. Source: `Deploy from a branch`.
4. Branch: `main`, Folder: `/ (root)`.
5. Wait for Pages build and verify live URL.
