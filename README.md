# RE-PO Project Website

Static project page for **RE-PO: Robust Enhanced Policy Optimization for LLM Alignment**.

## Stack

- Plain static files: `index.html`, `assets/`, `data/`
- No framework dependency
- GitHub Pages ready

## Local Preview

```bash
cd re-po-project-page
python scripts/validate_site.py
python -m http.server 8000
# open http://localhost:8000
```

## File Layout

- `index.html`
- `assets/css/site.css`
- `assets/js/site.js`
- `assets/img/flow_chart.png`
- `assets/img/one_annotator_eta.png`
- `assets/img/two_annotators_eta.png`
- `assets/paper/iclr2026_conference.pdf`
- `data/results_main.json`
- `data/links.json`
- `data/site_meta.json`
- `scripts/validate_site.py`
- `.github/workflows/ci.yml`

## Data Contracts

### `data/results_main.json`

Each row uses:

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

Empty string values are automatically hidden on the page.

### `data/site_meta.json`

- `project_name`
- `tagline`
- `conference`
- `year`
- `contact_email`
- `license`

## Deployment (GitHub Pages)

1. Push this repo to GitHub.
2. In repository settings, enable **Pages**.
3. Set source to **Deploy from a branch**.
4. Select branch `main` and folder `/ (root)`.
5. Save and wait for deployment.

## Notes

- Replace `data/links.json` values once final paper/arXiv/slide URLs are public.
- Current results are text values extracted from the camera-ready tables.
