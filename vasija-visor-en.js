const byId = id => document.getElementById(id);
const dialog = byId("vasijaViewer");
const collection = document.querySelector(".vasija-collection");
const cards = [...collection.querySelectorAll("[data-vasija-open]")];
const items = new Map();
const fichaTenerife = byId("vasijaTenerifeFicha");
const tenerife = "tenerife";
const requiredFields = ["title", "description", "modelDimensions", "adaptations"];

function validFields(item, fields) {
  return item && fields.every(key => typeof item[key] === "string" && item[key].trim());
}

function httpsReference(url) {
  const reference = new URL(url);
  if (reference.protocol !== "https:" || reference.username || reference.password) {
    throw new Error("Invalid reference");
  }
  return reference.href;
}

function showReference(section, key, href, label) {
  const link = section.querySelector(`[data-vasija-${key}]`);
  link.closest("li").hidden = !href;
  if (href) {
    link.href = href;
    link.textContent = label;
  } else {
    link.removeAttribute("href");
    link.textContent = "";
  }
}

function showDetails(section, item) {
  section.querySelectorAll("[data-vasija-field]").forEach(element => {
    element.textContent = item[element.dataset.vasijaField] ?? "";
  });
  showReference(section, "reference", item.referenceUrl, item.referenceLabel);
  showReference(section, "supplemental", item.supplementalReferenceUrl, item.supplementalReferenceLabel);
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error("Model details unavailable");
  return response.json();
}

async function loadTenerife() {
  const item = await fetchJson("assets/vasija/ficha-en.json");
  const fields = [...requiredFields, "documentedDimensions", "referenceLabel", "referenceUrl"];
  if (!validFields(item, fields) || item.badgePath !== "assets/images/insignia_tenerife.webp") {
    throw new Error("Incomplete model details");
  }
  item.referenceUrl = httpsReference(item.referenceUrl);
  if (item.supplementalReferenceUrl || item.supplementalReferenceLabel) {
    if (!validFields(item, ["supplementalReferenceLabel", "supplementalReferenceUrl"])) {
      throw new Error("Incomplete supplementary reference");
    }
    item.supplementalReferenceUrl = httpsReference(item.supplementalReferenceUrl);
  }
  items.set(tenerife, item);
  showDetails(fichaTenerife, item);
  const badge = byId("vasijaBadge");
  badge.src = item.badgePath;
  badge.alt = "Clay vessel from Tenerife";
  byId("vasijaBadgeFigure").hidden = false;
}

async function loadCollection() {
  const list = await fetchJson("assets/vasijas/coleccion-en.json");
  if (!Array.isArray(list)) throw new Error("Collection unavailable");
  for (const card of cards) {
    const id = card.dataset.vasijaOpen;
    if (id === tenerife) continue;
    const item = list.find(entry => entry?.id === id);
    if (validFields(item, requiredFields)) {
      const {title, description, modelDimensions, adaptations} = item;
      const model = {title, description, modelDimensions, adaptations};
      if (validFields(item, ["documentedDimensions"])) model.documentedDimensions = item.documentedDimensions;
      if (validFields(item, ["referenceUrl", "referenceLabel"])) {
        try {
          model.referenceUrl = httpsReference(item.referenceUrl);
          model.referenceLabel = item.referenceLabel;
        } catch {
          // A missing reference leaves the model and the common PDF available.
        }
      }
      items.set(id, model);
    }
  }
}

const fichaLoad = {loaded: false, pending: null};
const collectionLoad = {loaded: false, pending: null};

function loadOnce(source, loader, complete) {
  if (source.loaded) return Promise.resolve();
  if (!source.pending) {
    source.pending = loader().then(() => {
      source.loaded = complete();
    }).finally(() => { source.pending = null; });
  }
  return source.pending;
}

async function loadWhenOpened(details) {
  if (details?.id !== "resourceVasija" || !details.open) return;
  const [ficha] = await Promise.allSettled([
    loadOnce(fichaLoad, loadTenerife, () => items.has(tenerife)),
    loadOnce(collectionLoad, loadCollection, () => cards.every(card =>
      card.dataset.vasijaOpen === tenerife || items.has(card.dataset.vasijaOpen))),
  ]);
  if (ficha.status === "rejected" && !items.has(tenerife)) {
    fichaTenerife.querySelectorAll('[data-vasija-field$="Dimensions"]').forEach(element => {
      element.textContent = "Model details unavailable.";
    });
  }
  if (typeof dialog?.showModal !== "function") return;
  for (const card of cards) {
    const id = card.dataset.vasijaOpen;
    if (items.has(id)) {
      const tile = card.closest(".vasija-tile");
      const heading = tile.querySelector("h3");
      const selector = byId("vasijaSelect");
      if (![...selector.options].some(option => option.value === id)) {
        selector.add(new Option(heading.textContent, id));
      }
      heading.textContent = items.get(id).title;
      tile.querySelector("[data-vasija-still]").hidden = true;
      card.hidden = false;
    }
  }
}

document.addEventListener("toggle", event => void loadWhenOpened(event.target), true);
void loadWhenOpened(byId("resourceVasija"));

if (typeof dialog?.showModal === "function") {
  const selector = byId("vasijaSelect");
  const stage = byId("vasijaStage");
  const fallback = byId("vasijaFallback");
  const still = byId("vasijaStill");
  const status = byId("vasijaStatus");
  const gesture = byId("vasijaGesture");
  const tools = byId("vasijaTools");
  const toggle = byId("vasijaToggle");
  const spin = byId("vasijaSpin");
  let opener;
  let scene;
  let pending;
  let downloadUrl;
  let stillUrl;

  function selectModel() {
    const id = selector.value;
    const item = items.get(id);
    const tile = cards.find(card => card.dataset.vasijaOpen === id).closest(".vasija-tile");
    const link = tile.querySelector("[download]");
    const dialogDownload = byId("vasijaDownload");
    downloadUrl = link.getAttribute("href");
    stillUrl = tile.querySelector("[data-vasija-still]").getAttribute("href");
    dialogDownload.href = downloadUrl;
    dialogDownload.download = link.download;
    dialogDownload.setAttribute("aria-label", link.getAttribute("aria-label"));
    showDetails(dialog, item);
    byId("vasijaViewerDocumented").hidden = !item.documentedDimensions;
    stage.setAttribute("aria-label", `Interactive view. ${item.title}`);
    still.alt = `${item.title}. Still views of the inside, side and base.`;
  }

  function clearScene() {
    pending?.abort();
    pending = undefined;
    scene?.destroy();
    scene = undefined;
    spin.setAttribute("aria-pressed", "false");
    tools.hidden = true;
    gesture.hidden = true;
  }

  function showFixed(message) {
    clearScene();
    stage.hidden = true;
    stage.removeAttribute("aria-busy");
    fallback.hidden = false;
    still.src = stillUrl;
    toggle.textContent = "Back to the 3D viewer";
    status.textContent = message;
  }

  function showView(view) {
    if (view === "perspectiva") {
      scene.setView("perfil");
      scene.rotate(-9, -14);
    } else {
      scene.setView(view);
    }
  }

  async function showInteractive() {
    clearScene();
    fallback.hidden = true;
    stage.hidden = false;
    stage.setAttribute("aria-busy", "true");
    toggle.textContent = "View still images";
    status.textContent = "Loading the vessel…";
    const request = new AbortController();
    pending = request;
    try {
      const {createPintaderaScene} = await import("./pintaderas-escena.js");
      if (request.signal.aborted) return;
      const color = selector.value === "lanzarote" ? 0xe1cbaa : undefined;
      const loadedScene = await createPintaderaScene(stage, downloadUrl, request.signal, {color});
      if (request.signal.aborted) {
        loadedScene.destroy();
        return;
      }
      pending = undefined;
      scene = loadedScene;
      showView("perspectiva");
      stage.removeAttribute("aria-busy");
      tools.hidden = false;
      gesture.hidden = false;
      status.textContent = "3D vessel ready.";
    } catch {
      if (!request.signal.aborted) showFixed("The 3D viewer is unavailable. You can explore the still images.");
    }
  }

  collection.addEventListener("click", event => {
    const card = event.target.closest("[data-vasija-open]");
    if (!card || dialog.open) return;
    opener = card;
    selector.value = card.dataset.vasijaOpen;
    selectModel();
    dialog.showModal();
    dialog.scrollTop = 0;
    void showInteractive();
  });
  selector.addEventListener("change", () => {
    selectModel();
    if (fallback.hidden) void showInteractive();
    else showFixed("Showing still images.");
  });
  byId("vasijaClose").addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => {
    if (dialog.open) return;
    clearScene();
    still.removeAttribute("src");
    status.textContent = "";
    opener?.focus({preventScroll: true});
  });
  toggle.addEventListener("click", () => {
    if (fallback.hidden) showFixed("Showing still images.");
    else void showInteractive();
  });
  stage.addEventListener("pintadera-webgl-lost", () => {
    if (dialog.open && fallback.hidden) showFixed("The 3D viewer stopped. You can explore the still images.");
  });
  still.addEventListener("error", () => {
    if (dialog.open && !fallback.hidden) status.textContent = "The still images are unavailable. You can read the description and download the STL.";
  });
  tools.addEventListener("click", event => {
    const button = event.target.closest("button");
    if (!scene || !button) return;
    if (button.dataset.vasijaView) {
      scene.setAutoRotate(false);
      spin.setAttribute("aria-pressed", "false");
      showView(button.dataset.vasijaView);
    } else if (button.dataset.vasijaTurn) {
      scene.rotate(Number(button.dataset.vasijaTurn), 0);
    } else if (button.dataset.vasijaTilt) {
      scene.rotate(0, Number(button.dataset.vasijaTilt));
    } else if (button.dataset.vasijaZoom) {
      scene.zoom(Number(button.dataset.vasijaZoom));
    } else if (button === spin) {
      const enabled = spin.getAttribute("aria-pressed") !== "true";
      spin.setAttribute("aria-pressed", String(enabled));
      scene.setAutoRotate(enabled);
    }
  });
}
