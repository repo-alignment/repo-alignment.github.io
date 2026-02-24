const DATA_FILES = {
  links: "data/links.json",
  meta: "data/site_meta.json",
  results: "data/results_main.json",
  media: "data/method_media.json"
};

const DATASET_LABEL = {
  ultrafeedback: "UltraFeedback",
  multipref: "MultiPref"
};

const MODEL_LABEL = {
  mistral: "Mistral-7B-Instruct",
  llama: "Llama-3-8B-Instruct"
};

let mediaConfig = null;

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
    if (!row.dpo || !row.re_dpo) {
      continue;
    }

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

  safeSetLink("resource-paper-link", links.paper_url);
  safeSetLink("resource-code-link", links.code_url);
  safeSetLink("resource-issues-link", links.issues_url);
  safeSetLink("resource-arxiv-link", links.arxiv_url);
  safeSetLink("resource-slides-link", links.slides_url);

  safeSetLink("issues-link", links.issues_url);
  safeSetLink("arxiv-link", links.arxiv_url);
  safeSetLink("slides-link", links.slides_url);
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

function setActiveTab(kind) {
  for (const btn of document.querySelectorAll(".tab-btn")) {
    const isActive = btn.dataset.media === kind;
    btn.classList.toggle("is-active", isActive);
    btn.setAttribute("aria-selected", isActive ? "true" : "false");
  }
}

function showGifFallback(cfg) {
  const video = document.getElementById("method-video");
  const gif = document.getElementById("method-gif-fallback");
  gif.src = cfg.gif;
  gif.alt = cfg.alt;
  gif.hidden = false;
  video.hidden = true;
}

function applyMedia(kind) {
  if (!mediaConfig || !mediaConfig[kind]) return;

  const cfg = mediaConfig[kind];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const panel = document.getElementById("media-panel");
  const caption = document.getElementById("method-media-caption");
  const video = document.getElementById("method-video");
  const gif = document.getElementById("method-gif-fallback");
  const webmSource = document.getElementById("method-webm-source");
  const mp4Source = document.getElementById("method-mp4-source");

  panel.setAttribute("aria-labelledby", kind === "flow" ? "tab-flow" : "tab-reliability");
  caption.textContent = cfg.caption;

  video.hidden = false;
  gif.hidden = true;

  webmSource.src = cfg.webm;
  mp4Source.src = cfg.mp4;
  video.poster = cfg.poster;
  video.setAttribute("aria-label", cfg.alt);
  video.muted = true;
  video.loop = true;
  video.playsInline = true;

  video.load();

  const tryPlay = () => {
    if (reduceMotion) {
      video.removeAttribute("autoplay");
      video.controls = true;
      video.pause();
      return;
    }

    video.setAttribute("autoplay", "");
    video.controls = false;
    const playPromise = video.play();
    if (playPromise && typeof playPromise.catch === "function") {
      playPromise.catch(() => showGifFallback(cfg));
    }
  };

  if (!video.canPlayType || (video.canPlayType("video/webm") === "" && video.canPlayType("video/mp4") === "")) {
    showGifFallback(cfg);
  } else {
    tryPlay();
  }

  video.onerror = () => showGifFallback(cfg);
  setActiveTab(kind);
}

function setupMethodTabs(media) {
  mediaConfig = media;
  for (const btn of document.querySelectorAll(".tab-btn")) {
    btn.addEventListener("click", () => applyMedia(btn.dataset.media));
  }
  applyMedia("flow");
}

async function boot() {
  const [linksRes, metaRes, resultsRes, mediaRes] = await Promise.all([
    fetch(DATA_FILES.links),
    fetch(DATA_FILES.meta),
    fetch(DATA_FILES.results),
    fetch(DATA_FILES.media)
  ]);

  const [links, meta, results, media] = await Promise.all([
    linksRes.json(),
    metaRes.json(),
    resultsRes.json(),
    mediaRes.json()
  ]);

  applyMeta(meta);
  applyLinks(links);
  renderResults(normalizeRows(results));
  setupMethodTabs(media);
  setupCitationCopy();
  setupRevealAnimation();
}

boot().catch((err) => {
  console.error("Failed to initialize website:", err);
});
