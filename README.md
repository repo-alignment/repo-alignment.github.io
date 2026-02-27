# RE-PO Project Website (v1.6)

Static GitHub Pages site for **RE-PO: Robust Enhanced Policy Optimization for LLM Alignment**.

## v1.6 Highlights

- Conference-first hero with a single badge: **🏆 Accepted to ICLR 2026**.
- Lean information architecture: `Hero`, `Key Contributions`, `Method`, `Results`, `Citation`.
- Removed duplicated summary cards and removed the entire contact panel.
- Paper/Code are icon+text CTA buttons in the hero; Paper points to arXiv and Code points to the real repository.
- Results expanded to four method families (`DPO/IPO/SimPO/CPO`) using `Standard` vs `RE-PO` comparisons.
- Added two static reliability figures in `Results` (`one_annotator_eta.png`, `two_annotators_eta.png`).
- Added static asset versioning (`?v=1.6`) to reduce cache-related blank-page issues.

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
- `method` (`dpo|re_dpo|ipo|re_ipo|simpo|re_simpo|cpo|re_cpo`)
- `lc` (number)
- `wr` (number)
- `source` (`paper_camera_ready`)

### `data/links.json`

- `paper_url` (must be `https://arxiv.org/abs/2509.24159`)
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
