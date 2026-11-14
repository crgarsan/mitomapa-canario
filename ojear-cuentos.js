(() => {
  const dialog = document.getElementById("storyBookPreview");
  const cover = document.querySelector("#storyBookDownloads .story-book-cover");
  if (!cover || typeof dialog?.showModal !== "function") return;

  const byId = id => document.getElementById(id);
  const opener = document.createElement("button");
  opener.type = "button";
  opener.id = "openStoryBookPreview";
  opener.className = "book-preview-open";
  opener.setAttribute("aria-haspopup", "dialog");
  opener.setAttribute("aria-controls", dialog.id);
  cover.before(opener);
  cover.alt = "";
  const caption = document.createElement("span");
  caption.textContent = "Ojear en la web";
  opener.append(cover, caption);

  const previous = byId("bookPreviewPrevious");
  const next = byId("bookPreviewNext");
  const position = byId("bookPreviewPosition");
  const image = byId("bookPreviewPage");
  const figure = byId("bookPreviewFigure");
  const details = byId("bookPreviewText");
  const text = byId("bookPreviewTextBody");
  const folder = "assets/ojear-cuentos/";
  let pages;
  let edition = "cuentos";
  let pageIndex = 0;

  function showPage() {
    const sample = pages[edition];
    const page = sample[pageIndex];
    previous.setAttribute("aria-disabled", String(pageIndex === 0));
    next.setAttribute("aria-disabled", String(pageIndex === sample.length - 1));
    image.alt = page.label;
    image.width = page.width;
    image.height = page.height;
    image.src = folder + page.file;
    figure.hidden = false;
    details.hidden = false;
    text.textContent = page.text;
    position.textContent = `Muestra ${pageIndex + 1} de ${sample.length} · página ${page.number} del libro`;
  }

  function movePage(delta) {
    if (!pages) return;
    const target = pageIndex + delta;
    if (target < 0 || target >= pages[edition].length) return;
    pageIndex = target;
    showPage();
  }

  previous.addEventListener("click", () => movePage(-1));
  next.addEventListener("click", () => movePage(1));
  dialog.addEventListener("change", event => {
    if (event.target.name !== "previewEdition") return;
    edition = event.target.value;
    pageIndex = 0;
    if (pages) showPage();
  });
  opener.addEventListener("click", async () => {
    dialog.showModal();
    dialog.scrollTop = 0;
    if (pages) return;
    position.textContent = "Cargando la muestra…";
    try {
      const response = await fetch(folder + "paginas.json");
      if (!response.ok) throw new Error("Muestra no disponible");
      pages = await response.json();
      showPage();
    } catch {
      pages = undefined;
      position.textContent = "No se pudo cargar la muestra. Cierra el visor y vuelve a abrirlo.";
    }
  });
  byId("bookPreviewClose").addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => {
    if (!dialog.open) opener.focus({ preventScroll: true });
  });
})();
