const dialog = document.getElementById("pintaderaViewer");

if (typeof dialog?.showModal === "function") {
  initPintaderaViewer();
}

function initPintaderaViewer() {
  const title = document.getElementById("pintaderaTitle");
  const kind = document.getElementById("pintaderaKind");
  const size = document.getElementById("pintaderaSize");
  const stage = document.getElementById("pintaderaStage");
  const fallback = document.getElementById("pintaderaFallback");
  const still = document.getElementById("pintaderaStill");
  const status = document.getElementById("pintaderaStatus");
  const gesture = document.getElementById("pintaderaGesture");
  const description = document.getElementById("pintaderaDescription");
  const tools = document.getElementById("pintaderaTools");
  const series = document.getElementById("pintaderaSeries");
  const motif = document.getElementById("pintaderaMotif");
  const toggle = document.getElementById("pintaderaToggle");
  const spin = document.getElementById("pintaderaSpin");
  const download = document.getElementById("pintaderaDownload");

  const motifs = {
    chevron: "A triangular outline with V-shaped bands.",
    circulos: "An oval face with concentric rings and three triangles.",
    dentada: "A disc with a toothed edge and concentric rings.",
    doble_triangulo: "Two triangular shapes joined at the centre, with repeated markings.",
    espiral_cuadrada: "A square face with a spiral path and details along the edge.",
    rombos: "An elongated piece with a row of five diamonds and small triangular marks.",
    roseta: "A disc with a central six-petalled flower surrounded by raised rings.",
    seis_triangulos: "A triangular face with six triangles arranged in rows.",
    sol: "A disc with eight rays around a circular centre.",
    triangulo: "A triangular face with small incisions grouped near the corners."
  };

  const models = new Map();
  let selectedModel;
  let opener;
  let pending;
  let scene;
  let fixedView = false;

  for (const gallery of document.querySelectorAll("[data-pintadera-collection]")) {
    const collection = gallery.dataset.pintaderaCollection;
    for (const tile of gallery.querySelectorAll(".pintadera-tile")) {
      const view = tile.querySelector("[data-pintadera-open]");
      const link = tile.querySelector("a[download]");
      const stillLink = tile.querySelector("[data-pintadera-still]");
      const key = view.dataset.pintaderaOpen;
      const id = key.split("/")[1];
      if (!Object.hasOwn(motifs, id)) continue;
      const name = tile.querySelector("h4").textContent;
      models.set(key, {
        id, name, collection,
        dimensions: tile.querySelector(".pintadera-tile-size").textContent,
        url: link.href,
        filename: link.download,
        stillUrl: stillLink.href
      });
      if (collection === "recreaciones") motif.add(new Option(name, id));
      stillLink.hidden = true;
      view.hidden = false;
    }
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
    fixedView = true;
    stage.hidden = true;
    stage.removeAttribute("aria-busy");
    fallback.hidden = false;
    toggle.textContent = "Back to the 3D viewer";
    still.alt = "Face, side and back of " + selectedModel.name + ".";
    still.src = selectedModel.stillUrl;
    status.textContent = message;
  }

  async function showInteractive() {
    clearScene();
    fixedView = false;
    fallback.hidden = true;
    stage.hidden = false;
    stage.setAttribute("aria-busy", "true");
    toggle.textContent = "View still images";
    status.textContent = "Loading the 3D model…";
    const request = new AbortController();
    pending = request;
    try {
      const {createPintaderaScene} = await import("./pintaderas-escena.js");
      if (request.signal.aborted) return;
      const nextScene = await createPintaderaScene(stage, selectedModel.url, request.signal);
      if (request.signal.aborted) {
        nextScene.destroy();
        return;
      }
      pending = undefined;
      scene = nextScene;
      stage.removeAttribute("aria-busy");
      tools.hidden = false;
      gesture.hidden = false;
      status.textContent = "3D model ready.";
    } catch {
      if (!request.signal.aborted) showFixed("The 3D viewer is currently unavailable. You can explore the still images.");
    }
  }

  function showModel(model) {
    if (!model) return;
    selectedModel = model;
    const stamp = model.collection === "sellos";
    kind.textContent = stamp ? "Clay stamp" : "Recreated 3D model";
    title.textContent = model.name;
    size.textContent = "Approximate face dimensions · " + model.dimensions;
    stage.setAttribute("aria-label", "3D view of " + model.name + ", " + kind.textContent.toLowerCase());
    description.textContent = motifs[model.id] + (stamp
      ? " A recessed grip for your thumb and index finger. The motif is mirrored and its relief is inverted for stamping."
      : " Teaching model with a flat back.");
    series.value = model.collection;
    motif.value = model.id;
    download.href = model.url;
    download.download = model.filename;
    if (fixedView) {
      showFixed("Showing still images.");
    } else {
      void showInteractive();
    }
  }

  document.querySelector(".pintaderas-3d").addEventListener("click", event => {
    const button = event.target.closest("[data-pintadera-open]");
    const model = models.get(button?.dataset.pintaderaOpen);
    if (!model) return;
    opener = button;
    fixedView = false;
    dialog.showModal();
    dialog.scrollTop = 0;
    showModel(model);
  });

  const showSelectedModel = () => showModel(models.get(series.value + "/" + motif.value));
  series.addEventListener("change", showSelectedModel);
  motif.addEventListener("change", showSelectedModel);

  document.getElementById("pintaderaClose").addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => {
    if (dialog.open) return;
    clearScene();
    still.removeAttribute("src");
    status.textContent = "";
    opener?.focus({preventScroll: true});
    opener = undefined;
  });

  toggle.addEventListener("click", () => {
    if (fixedView) {
      void showInteractive();
    } else {
      showFixed("Showing still images.");
    }
  });
  stage.addEventListener("pintadera-webgl-lost", () => {
    if (dialog.open && !fixedView) showFixed("The 3D viewer stopped. You can explore the still images.");
  });
  still.addEventListener("error", () => {
    if (fixedView && dialog.open) status.textContent = "The still image is unavailable. You can read the description and download the STL.";
  });
  tools.addEventListener("click", event => {
    const button = event.target.closest("button");
    if (!scene || !button) return;
    if (button.dataset.pintaderaView) {
      scene.setAutoRotate(false);
      spin.setAttribute("aria-pressed", "false");
      scene.setView(button.dataset.pintaderaView);
    } else if (button.dataset.pintaderaTurn) {
      scene.rotate(Number(button.dataset.pintaderaTurn), 0);
    } else if (button.dataset.pintaderaTilt) {
      scene.rotate(0, Number(button.dataset.pintaderaTilt));
    } else if (button.dataset.pintaderaZoom) {
      scene.zoom(Number(button.dataset.pintaderaZoom));
    } else if (button === spin) {
      const enabled = spin.getAttribute("aria-pressed") !== "true";
      spin.setAttribute("aria-pressed", String(enabled));
      scene.setAutoRotate(enabled);
    }
  });
}
