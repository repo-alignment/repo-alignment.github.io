const DATA_FILES = {
  links: "data/links.json",
  meta: "data/site_meta.json",
  results: "data/results_main.json"
};

const DATASET_LABEL = {
  ultrafeedback: "UltraFeedback",
  multipref: "MultiPref"
};

const MODEL_LABEL = {
  mistral: "Mistral-7B-Instruct",
  llama: "Llama-3-8B-Instruct"
};

const METHOD_LABEL = {
  dpo: "DPO",
  ipo: "IPO",
  simpo: "SimPO",
  cpo: "CPO"
};

const RESULTS_ORDER = [
  { dataset: "ultrafeedback", model: "mistral", family: "dpo" },
  { dataset: "ultrafeedback", model: "mistral", family: "ipo" },
  { dataset: "ultrafeedback", model: "mistral", family: "simpo" },
  { dataset: "ultrafeedback", model: "mistral", family: "cpo" },
  { dataset: "ultrafeedback", model: "llama", family: "dpo" },
  { dataset: "ultrafeedback", model: "llama", family: "ipo" },
  { dataset: "ultrafeedback", model: "llama", family: "simpo" },
  { dataset: "ultrafeedback", model: "llama", family: "cpo" },
  { dataset: "multipref", model: "mistral", family: "dpo" },
  { dataset: "multipref", model: "llama", family: "dpo" }
];

function formatSigned(value) {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}`;
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (!node || value == null) return;
  node.textContent = String(value);
}

function getMethodFamily(method) {
  return method.startsWith("re_") ? method.slice(3) : method;
}

function isRepoMethod(method) {
  return method.startsWith("re_");
}

function normalizeRows(entries) {
  const grouped = new Map();

  for (const item of entries) {
    const family = getMethodFamily(item.method);
    const key = `${item.dataset}::${item.model}::${family}`;

    if (!grouped.has(key)) {
      grouped.set(key, {
        dataset: item.dataset,
        model: item.model,
        methodFamily: family,
        standard: null,
        repo: null
      });
    }

    const row = grouped.get(key);
    if (isRepoMethod(item.method)) {
      row.repo = item;
    } else {
      row.standard = item;
    }
  }

  const orderedKeys = RESULTS_ORDER.map((item) => `${item.dataset}::${item.model}::${item.family}`);
  const rows = [];

  for (const key of orderedKeys) {
    if (grouped.has(key)) rows.push(grouped.get(key));
  }

  for (const [key, value] of grouped.entries()) {
    if (!orderedKeys.includes(key)) rows.push(value);
  }

  return rows;
}

function renderResults(rows) {
  const tbody = document.getElementById("results-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  for (const row of rows) {
    if (!row.standard || !row.repo) continue;

    const deltaLc = row.repo.lc - row.standard.lc;
    const deltaWr = row.repo.wr - row.standard.wr;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${DATASET_LABEL[row.dataset] || row.dataset}</td>
      <td>${MODEL_LABEL[row.model] || row.model}</td>
      <td>${METHOD_LABEL[row.methodFamily] || row.methodFamily.toUpperCase()}</td>
      <td>${row.standard.lc.toFixed(1)} / ${row.standard.wr.toFixed(1)}</td>
      <td>${row.repo.lc.toFixed(1)} / ${row.repo.wr.toFixed(1)}</td>
      <td class="${deltaLc >= 0 ? "delta-pos" : "delta-neg"}">${formatSigned(deltaLc)}</td>
      <td class="${deltaWr >= 0 ? "delta-pos" : "delta-neg"}">${formatSigned(deltaWr)}</td>
    `;
    tbody.appendChild(tr);
  }
}

function applyMeta(meta) {
  setText("project-name", meta.project_name);
  setText("project-year", meta.year);
  setText("project-license", meta.license);
  setText("hero-tagline", meta.tagline);

  if (meta.paper_badge_text) {
    setText("paper-badge", meta.paper_badge_text);
  }

  if (Array.isArray(meta.affiliations) && meta.affiliations.length > 0) {
    setText("affiliation-line", meta.affiliations.join(" · "));
  }
}

function safeSetLink(id, url) {
  const node = document.getElementById(id);
  if (!node) return;

  if (!url || url.trim() === "") {
    node.hidden = true;
    return;
  }

  node.hidden = false;
  node.setAttribute("href", url);
}

function applyLinks(links) {
  safeSetLink("cta-paper", links.paper_url);
  safeSetLink("cta-code", links.code_url);
}

function setupCitationCopy() {
  const button = document.getElementById("copy-citation");
  const source = document.getElementById("citation-text");
  const status = document.getElementById("copy-status");
  if (!button || !source || !status) return;

  button.addEventListener("click", async () => {
    const text = source.textContent || "";
    try {
      await navigator.clipboard.writeText(text);
      status.textContent = "BibTeX copied.";
    } catch (_err) {
      status.textContent = "Copy failed. Please copy manually.";
    }
  });
}

function setupRevealAnimation() {
  const items = Array.from(document.querySelectorAll(".reveal"));
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      }
    }, { threshold: 0.14 });

    for (const item of items) observer.observe(item);
  } else {
    for (const item of items) item.classList.add("is-visible");
  }
}

function forceRevealAll() {
  for (const item of document.querySelectorAll(".reveal")) {
    item.classList.add("is-visible");
  }
}

async function fetchJson(path) {
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} for ${path}`);
  }
  return res.json();
}

async function boot() {
  setupRevealAnimation();

  const [links, meta, results] = await Promise.all([
    fetchJson(DATA_FILES.links),
    fetchJson(DATA_FILES.meta),
    fetchJson(DATA_FILES.results)
  ]);

  applyMeta(meta);
  applyLinks(links);
  renderResults(normalizeRows(results));
  setupCitationCopy();
}

boot().catch((err) => {
  console.error("Failed to initialize website:", err);
  forceRevealAll();
});
