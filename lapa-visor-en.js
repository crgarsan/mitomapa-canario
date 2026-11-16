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
    toggle.textContent = "Back to the 3D viewer";
    status.textContent = message;
  }

  async function showInteractive() {
    clearScene();
    fallback.hidden = true;
    stage.hidden = false;
    stage.setAttribute("aria-busy", "true");
    toggle.textContent = "View still images";
    status.textContent = "Loading the shell…";
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
      status.textContent = "3D shell ready.";
    } catch {
      if (!request.signal.aborted) showFixed("The 3D viewer is unavailable. You can explore the still images.");
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
    if (fallback.hidden) showFixed("Showing still images.");
    else void showInteractive();
  });
  stage.addEventListener("pintadera-webgl-lost", () => {
    if (dialog.open && fallback.hidden) showFixed("The 3D viewer stopped. You can explore the still images.");
  });
  still.addEventListener("error", () => {
    if (dialog.open && !fallback.hidden) status.textContent = "The still images are unavailable. You can download the STL.";
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
