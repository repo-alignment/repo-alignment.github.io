# RE-PO Project Website (v1.5)

Static GitHub Pages site for **RE-PO: Robust Enhanced Policy Optimization for LLM Alignment**.

## v1.5 Highlights

- Conference-first hero with a single badge: **🏆 Accepted to ICLR 2026**.
- Lean information architecture: `Hero`, `Key Contributions`, `Method`, `Results`, `Citation`.
- Removed duplicated summary cards and removed the entire contact panel.
- Paper/Code are icon+text CTA buttons in the hero and Code points to the real repository.
- Added static asset versioning (`?v=1.5`) to reduce cache-related blank-page issues.

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
- `code_url` (must be `https://github.com/XiaoyangCao1113/RE-PO`)

### `data/site_meta.json`

- `project_name`
- `tagline`
- `conference`
- `year`
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
