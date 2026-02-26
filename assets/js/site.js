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

function formatSigned(value) {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}`;
}

function normalizeRows(entries) {
  const grouped = new Map();

  for (const item of entries) {
    const key = `${item.dataset}::${item.model}`;
    if (!grouped.has(key)) {
      grouped.set(key, { dataset: item.dataset, model: item.model, dpo: null, re_dpo: null });
    }
    grouped.get(key)[item.method] = item;
  }

  const order = [
    ["ultrafeedback", "mistral"],
    ["ultrafeedback", "llama"],
    ["multipref", "mistral"],
    ["multipref", "llama"]
  ];

  return order
    .map(([dataset, model]) => grouped.get(`${dataset}::${model}`))
    .filter(Boolean);
}

function renderResults(rows) {
  const tbody = document.getElementById("results-body");
  tbody.innerHTML = "";

  for (const row of rows) {
    if (!row.dpo || !row.re_dpo) continue;

    const deltaLc = row.re_dpo.lc - row.dpo.lc;
    const deltaWr = row.re_dpo.wr - row.dpo.wr;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${DATASET_LABEL[row.dataset] || row.dataset}</td>
      <td>${MODEL_LABEL[row.model] || row.model}</td>
      <td>${row.dpo.lc.toFixed(1)} / ${row.dpo.wr.toFixed(1)}</td>
      <td>${row.re_dpo.lc.toFixed(1)} / ${row.re_dpo.wr.toFixed(1)}</td>
      <td class="${deltaLc >= 0 ? "delta-pos" : "delta-neg"}">${formatSigned(deltaLc)}</td>
      <td class="${deltaWr >= 0 ? "delta-pos" : "delta-neg"}">${formatSigned(deltaWr)}</td>
    `;
    tbody.appendChild(tr);
  }
}

function applyMeta(meta) {
  document.getElementById("project-name").textContent = meta.project_name;
  document.getElementById("project-year").textContent = String(meta.year);
  document.getElementById("project-license").textContent = meta.license;
  document.getElementById("project-kicker").textContent = `${meta.conference} ${meta.year}`;
  document.getElementById("hero-tagline").textContent = meta.tagline;

  if (meta.paper_badge_text) {
    document.getElementById("paper-badge").textContent = meta.paper_badge_text;
  }

  if (Array.isArray(meta.authors) && meta.authors.length > 0) {
    document.getElementById("author-line").textContent = meta.authors.join(", ");
  }

  if (Array.isArray(meta.affiliations) && meta.affiliations.length > 0) {
    document.getElementById("affiliation-line").textContent = meta.affiliations.join(" · ");
  }

  const emailNode = document.getElementById("contact-email");
  emailNode.textContent = meta.contact_email;
  emailNode.setAttribute("href", `mailto:${meta.contact_email}`);
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
  safeSetLink("contact-code-link", links.code_url);
}

function setupCitationCopy() {
  const button = document.getElementById("copy-citation");
  const source = document.getElementById("citation-text");
  const status = document.getElementById("copy-status");

  button.addEventListener("click", async () => {
    const text = source.textContent || "";
    try {
      await navigator.clipboard.writeText(text);
      status.textContent = "BibTeX copied.";
    } catch (err) {
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

async function boot() {
  const [linksRes, metaRes, resultsRes] = await Promise.all([
    fetch(DATA_FILES.links),
    fetch(DATA_FILES.meta),
    fetch(DATA_FILES.results)
  ]);

  const [links, meta, results] = await Promise.all([
    linksRes.json(),
    metaRes.json(),
    resultsRes.json()
  ]);

  applyMeta(meta);
  applyLinks(links);
  renderResults(normalizeRows(results));
  setupCitationCopy();
  setupRevealAnimation();
}

boot().catch((err) => {
  console.error("Failed to initialize website:", err);
});
