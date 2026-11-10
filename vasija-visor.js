const byId = id => document.getElementById(id);
const dialog = byId("vasijaViewer");
const stl = "downloads/vasija/vasija_canaria.stl";
const stillUrl = "assets/vasija/vistas.webp";

const passportBadges = {
  "assets/images/insignia_la_gomera.webp": "Vasija de barro de La Gomera",
  "assets/images/insignia_tenerife.webp": "Vasija de barro de Tenerife",
};

function httpsReference(url) {
  const reference = new URL(url);
  if (reference.protocol !== "https:" || reference.username || reference.password) {
    throw new Error("Referencia inválida");
  }
  return reference.href;
}

function showReference(key, href, label) {
  document.querySelectorAll(`[data-vasija-${key}]`).forEach(link => {
    link.href = href;
    link.textContent = label;
    link.closest("li").hidden = false;
  });
}

async function showFicha() {
  try {
    const response = await fetch("assets/vasija/ficha.json");
    if (!response.ok) throw new Error("Ficha no disponible");
    const ficha = await response.json();
    const fields = ["title", "description", "documentedDimensions", "modelDimensions", "adaptations", "referenceLabel", "referenceUrl", "badgePath"];
    if (!ficha || fields.some(key => typeof ficha[key] !== "string" || !ficha[key].trim())
        || !Object.hasOwn(passportBadges, ficha.badgePath)) {
      throw new Error("Ficha incompleta");
    }
    const reference = httpsReference(ficha.referenceUrl);
    const hasSupplemental = ficha.supplementalReferenceUrl || ficha.supplementalReferenceLabel;
    if (hasSupplemental && (typeof ficha.supplementalReferenceUrl !== "string"
        || typeof ficha.supplementalReferenceLabel !== "string"
        || !ficha.supplementalReferenceLabel.trim())) {
      throw new Error("Referencia complementaria incompleta");
    }
    const supplemental = hasSupplemental ? httpsReference(ficha.supplementalReferenceUrl) : null;
    document.querySelectorAll("[data-vasija-field]").forEach(element => {
      element.textContent = ficha[element.dataset.vasijaField];
    });
    const badge = byId("vasijaBadge");
    badge.src = ficha.badgePath;
    badge.alt = passportBadges[ficha.badgePath];
    byId("vasijaBadgeFigure").hidden = false;
    showReference("reference", reference, ficha.referenceLabel);
    if (supplemental) showReference("supplemental", supplemental, ficha.supplementalReferenceLabel);
  } catch {
    document.querySelectorAll('[data-vasija-field$="Dimensions"]').forEach(element => {
      element.textContent = "Ficha no disponible.";
    });
  }
}

void showFicha();

if (typeof dialog?.showModal === "function") {
  const opener = byId("openVasijaViewer");
  const stage = byId("vasijaStage");
  const fallback = byId("vasijaFallback");
  const still = byId("vasijaStill");
  const status = byId("vasijaStatus");
  const gesture = byId("vasijaGesture");
  const tools = byId("vasijaTools");
  const toggle = byId("vasijaToggle");
  const spin = byId("vasijaSpin");
  let scene;
  let pending;

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
    toggle.textContent = "Volver al visor 3D";
    status.textContent = message;
  }

  async function showInteractive() {
    clearScene();
    fallback.hidden = true;
    stage.hidden = false;
    stage.setAttribute("aria-busy", "true");
    toggle.textContent = "Ver imágenes fijas";
    status.textContent = "Cargando la vasija…";
    const request = new AbortController();
    pending = request;
    try {
      const {createPintaderaScene} = await import("./pintaderas-escena.js");
      if (request.signal.aborted) return;
      const loadedScene = await createPintaderaScene(stage, stl, request.signal);
      if (request.signal.aborted) {
        loadedScene.destroy();
        return;
      }
      pending = undefined;
      scene = loadedScene;
      stage.removeAttribute("aria-busy");
      tools.hidden = false;
      gesture.hidden = false;
      status.textContent = "Vasija 3D lista.";
    } catch {
      if (!request.signal.aborted) showFixed("El visor 3D no está disponible. Pueden explorar las imágenes fijas.");
    }
  }

  opener.hidden = false;
  opener.addEventListener("click", () => {
    if (dialog.open) return;
    dialog.showModal();
    dialog.scrollTop = 0;
    void showInteractive();
  });
  byId("vasijaClose").addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => {
    if (dialog.open) return;
    clearScene();
    still.removeAttribute("src");
    status.textContent = "";
    opener.focus({preventScroll: true});
  });
  toggle.addEventListener("click", () => {
    if (fallback.hidden) showFixed("Mostrando imágenes fijas.");
    else void showInteractive();
  });
  stage.addEventListener("pintadera-webgl-lost", () => {
    if (dialog.open && fallback.hidden) showFixed("El visor 3D se ha interrumpido. Pueden explorar las imágenes fijas.");
  });
  still.addEventListener("error", () => {
    if (dialog.open && !fallback.hidden) status.textContent = "Las imágenes fijas no están disponibles. Pueden consultar la descripción y descargar el STL.";
  });
  tools.addEventListener("click", event => {
    const button = event.target.closest("button");
    if (!scene || !button) return;
    if (button.dataset.vasijaView) {
      scene.setAutoRotate(false);
      spin.setAttribute("aria-pressed", "false");
      scene.setView(button.dataset.vasijaView);
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
