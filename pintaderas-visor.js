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
    chevron: "Silueta triangular con bandas en forma de uve.",
    circulos: "Cara ovalada que combina anillos concéntricos y tres triángulos.",
    dentada: "Disco con borde dentado y anillos concéntricos.",
    doble_triangulo: "Dos formas triangulares unidas por el centro, con marcas repetidas.",
    espiral_cuadrada: "Cara cuadrada con un recorrido en espiral y detalles en el borde.",
    rombos: "Pieza alargada con cinco rombos en fila y marcas triangulares pequeñas.",
    roseta: "Disco con una flor central de seis pétalos rodeada por anillos de relieve.",
    seis_triangulos: "Cara triangular con seis triángulos dispuestos en filas.",
    sol: "Disco con ocho rayos alrededor de un centro circular.",
    triangulo: "Cara triangular con pequeñas incisiones agrupadas hacia las esquinas."
  };

  const models = new Map();
  let selectedModel;
  let opener;
  let pending;
  let scene;
  let fixedView = false;

  function makeViewButton(model, label, cssClass) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = cssClass;
    button.textContent = label;
    button.dataset.pintaderaOpen = model.key;
    button.setAttribute("aria-haspopup", "dialog");
    return button;
  }

  for (const actions of document.querySelectorAll("[data-pintadera-collection]")) {
    const collection = actions.dataset.pintaderaCollection;
    const card = actions.closest(".download-card");
    for (const link of card.querySelectorAll(".pintadera-files li a[download]")) {
      const id = link.pathname.match(/\/pintadera_([a-z_]+)\.stl$/)?.[1];
      if (!id || !Object.hasOwn(motifs, id)) continue;
      const name = link.textContent.trim().replace(/^(Modelo|Sello) /, "").replace(/ \(STL\)$/, "");
      const label = link.nextElementSibling;
      const model = {
        id, name, collection,
        key: collection + "/" + id,
        dimensions: label.textContent,
        url: link.href,
        filename: link.download
      };
      models.set(model.key, model);
      if (collection === "recreaciones") motif.add(new Option(name, id));

      const row = link.closest("li");
      row.classList.add("pintadera-file-row");
      const caption = document.createElement("div");
      caption.className = "pintadera-file-label";
      const nameText = document.createElement("strong");
      nameText.textContent = name;
      caption.append(nameText, label);
      const rowActions = document.createElement("div");
      rowActions.className = "pintadera-row-actions";
      const view = makeViewButton(model, "Ver en 3D", "pintadera-file-view");
      view.setAttribute("aria-label", "Ver en 3D: " + name + ", " + (collection === "sellos" ? "sello para arcilla" : "modelo recreado"));
      link.textContent = "Descargar STL";
      link.setAttribute("aria-label", "Descargar STL: " + name + ", " + (collection === "sellos" ? "sello para arcilla" : "modelo recreado"));
      rowActions.append(view, link);
      row.append(caption, rowActions);
    }
    const starter = models.get([collection, "roseta"].join("/"));
    if (starter) {
      const explore = makeViewButton(starter, "Explorar en 3D", "button");
      explore.setAttribute("aria-label", collection === "sellos" ? "Explorar en 3D los sellos para arcilla" : "Explorar en 3D los modelos recreados");
      actions.querySelector("a").classList.add("secondary");
      actions.prepend(explore);
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
    toggle.textContent = "Volver al visor 3D";
    const {collection, id, name} = selectedModel;
    still.alt = "Cara, perfil y reverso de " + name + ".";
    still.src = ["assets/pintaderas-3d/vistas", collection, "pintadera_" + id + ".webp"].join("/");
    status.textContent = message;
  }

  async function showInteractive() {
    clearScene();
    fixedView = false;
    fallback.hidden = true;
    stage.hidden = false;
    stage.setAttribute("aria-busy", "true");
    toggle.textContent = "Ver imágenes fijas";
    status.textContent = "Cargando la pieza 3D…";
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
      status.textContent = "Pieza 3D lista.";
    } catch {
      if (!request.signal.aborted) showFixed("El visor 3D no está disponible en este momento. Puedes explorar las imágenes fijas.");
    }
  }

  function showModel(model) {
    if (!model) return;
    selectedModel = model;
    const stamp = model.collection === "sellos";
    kind.textContent = stamp ? "Sello para arcilla" : "Modelo recreado en 3D";
    title.textContent = model.name;
    size.textContent = "Medida aproximada de la cara · " + model.dimensions;
    stage.setAttribute("aria-label", "Vista 3D de " + model.name + ", " + kind.textContent.toLowerCase());
    description.textContent = motifs[model.id] + (stamp
      ? " Rebaje lateral para sujetarlo entre el pulgar y el índice. El motivo está reflejado y su relieve está invertido para estamparlo."
      : " Modelo educativo con el reverso plano.");
    series.value = model.collection;
    motif.value = model.id;
    download.href = model.url;
    download.download = model.filename;
    if (fixedView) {
      showFixed("Mostrando imágenes fijas.");
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
      showFixed("Mostrando imágenes fijas.");
    }
  });
  stage.addEventListener("pintadera-webgl-lost", () => {
    if (dialog.open && !fixedView) showFixed("El visor 3D se ha interrumpido. Puedes explorar las imágenes fijas.");
  });
  still.addEventListener("error", () => {
    if (fixedView && dialog.open) status.textContent = "La imagen fija no está disponible. Puedes consultar la descripción y descargar el STL.";
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
