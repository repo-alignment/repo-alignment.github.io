const DATA_FILES = {
  links: "data/links.json",
  meta: "data/site_meta.json",
  results: "data/results_main.json",
  media: "data/method_media.json",
  preferenceCases: "data/preference_cases.json",
  preferenceMedia: "data/preference_media.json"
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
let duelState = {
  cases: [],
  mediaByCase: {},
  idx: 0,
  timer: null,
  running: true,
  reduceMotion: false
};

function formatSigned(value) {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}`;
}

function clipText(text, maxLen = 320) {
  if (!text) return "";
  const normalized = String(text).replace(/\s+/g, " ").trim();
  if (normalized.length <= maxLen) return normalized;
  return `${normalized.slice(0, maxLen - 3)}...`;
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

function winnerLabel(item) {
  if (item.winner === "left") return item.left_label;
  if (item.winner === "right") return item.right_label;
  return "Tie";
}

function renderDuelCase() {
  const item = duelState.cases[duelState.idx];
  if (!item) return;

  const media = duelState.mediaByCase[item.case_id];
  if (!media) return;

  document.getElementById("duel-index").textContent = `Case ${duelState.idx + 1}/${duelState.cases.length}`;
  document.getElementById("duel-phase-badge").textContent = item.phase === "appendix"
    ? "Phase A evidence (dataset-level)"
    : "Phase B evidence (model-pair)";
  document.getElementById("duel-source-badge").textContent = item.source_badge;

  document.getElementById("duel-prompt-text").textContent = clipText(item.prompt, 360);
  document.getElementById("duel-left-label").textContent = item.left_label;
  document.getElementById("duel-right-label").textContent = item.right_label;
  document.getElementById("duel-left-text").textContent = clipText(item.left_text, 340);
  document.getElementById("duel-right-text").textContent = clipText(item.right_text, 340);
  document.getElementById("duel-winner").textContent = winnerLabel(item);
  document.getElementById("duel-reason").textContent = item.reason_short;
  document.getElementById("duel-signal").textContent = item.confidence_signal;
  document.getElementById("duel-source-line").textContent = `${item.source} (${item.source_ref})`;

  const gifNode = document.getElementById("duel-gif");
  const captionNode = document.getElementById("duel-media-caption");
  const reduced = duelState.reduceMotion;

  gifNode.alt = media.alt;
  gifNode.src = reduced ? media.poster : media.gif;
  gifNode.onerror = () => {
    gifNode.src = media.poster;
  };

  const durationSec = Number(media.duration_ms || 0) / 1000;
  captionNode.textContent = reduced
    ? `${item.case_id} static preview (reduced motion mode).`
    : `${item.case_id} animated comparison (${durationSec.toFixed(1)}s loop).`;

  const mp4 = document.getElementById("duel-mp4-link");
  const webm = document.getElementById("duel-webm-link");
  mp4.href = media.mp4;
  webm.href = media.webm;
}

function stopDuelAuto() {
  if (duelState.timer) {
    clearInterval(duelState.timer);
    duelState.timer = null;
  }
}

function startDuelAuto() {
  stopDuelAuto();
  if (!duelState.running || duelState.reduceMotion || duelState.cases.length < 2) {
    return;
  }
  duelState.timer = setInterval(() => {
    duelState.idx = (duelState.idx + 1) % duelState.cases.length;
    renderDuelCase();
  }, 5200);
}

function moveDuel(delta) {
  if (duelState.cases.length === 0) return;
  const n = duelState.cases.length;
  duelState.idx = (duelState.idx + delta + n) % n;
  renderDuelCase();
}

function setupPreferenceDuel(cases, mediaMap) {
  const section = document.getElementById("preference-duel");
  if (!section) return;

  if (!Array.isArray(cases) || cases.length === 0 || !mediaMap || typeof mediaMap !== "object") {
    section.hidden = true;
    return;
  }

  duelState.cases = cases;
  duelState.mediaByCase = mediaMap;
  duelState.idx = 0;
  duelState.running = true;
  duelState.reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  renderDuelCase();

  const prev = document.getElementById("duel-prev");
  const next = document.getElementById("duel-next");
  const pause = document.getElementById("duel-pause");
  const shell = document.getElementById("duel-shell");

  prev.addEventListener("click", () => {
    moveDuel(-1);
    startDuelAuto();
  });

  next.addEventListener("click", () => {
    moveDuel(1);
    startDuelAuto();
  });

  pause.addEventListener("click", () => {
    duelState.running = !duelState.running;
    pause.textContent = duelState.running ? "Pause" : "Resume";
    startDuelAuto();
  });

  shell.addEventListener("keydown", (evt) => {
    if (evt.key === "ArrowLeft") {
      evt.preventDefault();
      moveDuel(-1);
      startDuelAuto();
    }
    if (evt.key === "ArrowRight") {
      evt.preventDefault();
      moveDuel(1);
      startDuelAuto();
    }
  });

  if (duelState.reduceMotion) {
    duelState.running = false;
    pause.textContent = "Auto Off";
    pause.disabled = true;
  }

  startDuelAuto();
}

async function boot() {
  const [linksRes, metaRes, resultsRes, mediaRes, prefCasesRes, prefMediaRes] = await Promise.all([
    fetch(DATA_FILES.links),
    fetch(DATA_FILES.meta),
    fetch(DATA_FILES.results),
    fetch(DATA_FILES.media),
    fetch(DATA_FILES.preferenceCases),
    fetch(DATA_FILES.preferenceMedia)
  ]);

  const [links, meta, results, media, preferenceCases, preferenceMedia] = await Promise.all([
    linksRes.json(),
    metaRes.json(),
    resultsRes.json(),
    mediaRes.json(),
    prefCasesRes.json(),
    prefMediaRes.json()
  ]);

  applyMeta(meta);
  applyLinks(links);
  renderResults(normalizeRows(results));
  setupMethodTabs(media);
  setupPreferenceDuel(preferenceCases, preferenceMedia);
  setupCitationCopy();
  setupRevealAnimation();
}

boot().catch((err) => {
  console.error("Failed to initialize website:", err);
});
