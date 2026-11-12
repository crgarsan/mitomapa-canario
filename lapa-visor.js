const byId = id => document.getElementById(id);
const dialog = byId("lapaViewer");

if (typeof dialog?.showModal === "function") {
  const opener = byId("openLapaViewer");
  const stillLink = byId("lapaStillLink");
  const stage = byId("lapaStage");
  const fallback = byId("lapaFallback");
  const still = byId("lapaStill");
  const status = byId("lapaStatus");
  const gesture = byId("lapaGesture");
  const tools = byId("lapaTools");
  const toggle = byId("lapaToggle");
  let pending;
  let scene;

  function clearScene() {
    pending?.abort();
    pending = undefined;
    scene?.destroy();
    scene = undefined;
    tools.hidden = true;
    gesture.hidden = true;
  }

  function showFixed(message) {
    clearScene();
    stage.hidden = true;
    stage.removeAttribute("aria-busy");
    still.src = stillLink.getAttribute("href");
    fallback.hidden = false;
    toggle.textContent = "Volver al visor 3D";
    status.textContent = message;
  }

  async function showInteractive() {
    clearScene();
    fallback.hidden = true;
    stage.hidden = false;
    stage.setAttribute("aria-busy", "true");
    toggle.textContent = "Ver imágenes fijas";
    status.textContent = "Cargando la concha…";
    const request = new AbortController();
    pending = request;
    try {
      const { createPintaderaScene } = await import("./pintaderas-escena.js");
      if (request.signal.aborted) return;
      const stl = byId("lapaDownload").getAttribute("href");
      const loadedScene = await createPintaderaScene(stage, stl, request.signal, { color: 0xd6c3a1 });
      if (request.signal.aborted) {
        loadedScene.destroy();
        return;
      }
      pending = undefined;
      scene = loadedScene;
      stage.removeAttribute("aria-busy");
      tools.hidden = false;
      gesture.hidden = false;
      status.textContent = "Concha 3D lista.";
    } catch {
      if (!request.signal.aborted) showFixed("El visor 3D no está disponible. Pueden explorar las imágenes fijas.");
    }
  }

  stillLink.hidden = true;
  opener.hidden = false;
  opener.addEventListener("click", () => {
    if (dialog.open) return;
    dialog.showModal();
    dialog.scrollTop = 0;
    void showInteractive();
  });
  byId("lapaClose").addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => {
    if (dialog.open) return;
    clearScene();
    still.removeAttribute("src");
    status.textContent = "";
    opener.focus({ preventScroll: true });
  });
  toggle.addEventListener("click", () => {
    if (fallback.hidden) showFixed("Mostrando imágenes fijas.");
    else void showInteractive();
  });
  stage.addEventListener("pintadera-webgl-lost", () => {
    if (dialog.open && fallback.hidden) showFixed("El visor 3D se ha interrumpido. Pueden explorar las imágenes fijas.");
  });
  still.addEventListener("error", () => {
    if (dialog.open && !fallback.hidden) status.textContent = "Las imágenes fijas no están disponibles. Pueden descargar el STL.";
  });
  tools.addEventListener("click", event => {
    const button = event.target.closest("button");
    if (!scene || !button) return;
    const { lapaView, lapaTurn, lapaTilt, lapaZoom } = button.dataset;
    if (lapaView) scene.setView(lapaView);
    else if (lapaTurn) scene.rotate(Number(lapaTurn), 0);
    else if (lapaTilt) scene.rotate(0, Number(lapaTilt));
    else if (lapaZoom) scene.zoom(Number(lapaZoom));
  });
}
