/* Comparación opcional de relatos. No modifica los retos ni las pintaderas. */
(function () {
  "use strict";

  const storageKey = "mitomapa-canario-comparaciones-v1";
  const maxNotes = 64;
  const maxLength = 700;
  let context = null;
  let state = null;
  let section = null;
  let saveTimer = null;
  let currentLevel = "middle";
  let controls = null;

  function canonicalKey(pair) {
    return [...pair].sort().join("|");
  }

  function defaultPair() {
    const ids = context.routes.map(route => route.id);
    const first = ids.includes("tenerife") ? "tenerife" : ids[0];
    const second = ids.includes("el-hierro") && first !== "el-hierro"
      ? "el-hierro" : ids.find(id => id !== first);
    return [first, second];
  }

  function sanitize(raw) {
    const ids = new Set(context.routes.map(route => route.id));
    const pair = Array.isArray(raw?.pair) && raw.pair.length === 2 &&
      raw.pair.every(id => typeof id === "string" && ids.has(id)) && raw.pair[0] !== raw.pair[1]
      ? [...raw.pair] : defaultPair();
    const notes = Object.create(null);
    if (raw?.notes && typeof raw.notes === "object" && !Array.isArray(raw.notes)) {
      for (const [key, value] of Object.entries(raw.notes).slice(0, maxNotes)) {
        const notePair = key.split("|");
        if (notePair.length !== 2 || notePair[0] === notePair[1] ||
          !notePair.every(id => ids.has(id)) || typeof value !== "string") continue;
        const bounded = value.slice(0, maxLength);
        if (bounded) notes[canonicalKey(notePair)] = bounded;
      }
    }
    return { pair, notes };
  }

  function save() {
    if (!context || !state) return false;
    if (saveTimer !== null) {
      window.clearTimeout(saveTimer);
      saveTimer = null;
    }
    let result = false;
    try { result = context.writeJSON(storageKey, exportState()) !== false; }
    catch (error) { result = false; }
    if (controls) controls.saved.textContent = result
      ? "Comparación guardada en este navegador. Puedes retomarla al elegir estas dos islas."
      : "La comparación sigue en pantalla, pero no se pudo guardar. Descárgala antes de cerrar.";
    return result;
  }

  function scheduleSave() {
    if (saveTimer !== null) window.clearTimeout(saveTimer);
    controls.saved.textContent = "Guardando la comparación…";
    saveTimer = window.setTimeout(save, 400);
  }

  function node(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function makeCard(index) {
    const card = node("article", "compare-card");
    const heading = node("h3", "compare-card-island");
    const title = node("p", "compare-card-title");
    const figure = node("figure", "compare-card-figure");
    const image = document.createElement("img");
    image.loading = "lazy";
    image.decoding = "async";
    figure.append(image, node("figcaption", "compare-card-caption", "Ilustración contemporánea de la recreación literaria."));
    const eventsHeading = node("h4", "compare-events-title", "Cuatro acontecimientos del cuento");
    const events = node("ol", "compare-events");
    const button = node("button", "button secondary compare-open");
    button.type = "button";
    button.addEventListener("click", () => context.openRoute(state.pair[index]));
    card.append(heading, title, figure, eventsHeading, events, button);
    return { card, heading, title, image, events, button };
  }

  function renderPair() {
    controls.selects.forEach((select, index) => { select.value = state.pair[index]; });
    controls.cards.forEach((card, index) => {
      const route = context.routes.find(item => item.id === state.pair[index]);
      card.heading.textContent = route.island;
      card.title.textContent = route.title;
      card.image.src = context.assets[route.image] || route.image;
      card.image.alt = route.imageAlt || `Ilustración del cuento de ${route.island}.`;
      card.events.replaceChildren();
      const events = context.eventsFor(route.id);
      if (Array.isArray(events)) {
        events.slice(0, 4).forEach(event => card.events.append(node("li", "", String(event))));
      }
      card.button.textContent = `Abrir el cuento de ${route.island}`;
    });
    controls.note.value = state.notes[canonicalKey(state.pair)] || "";
    renderNote();
  }

  function renderNote() {
    controls.counter.textContent = `${controls.note.value.length} de ${maxLength} caracteres.`;
    controls.download.disabled = controls.note.value.trim().length === 0;
  }

  function changeIsland(index, selected) {
    if (!context.routes.some(route => route.id === selected)) return;
    const other = 1 - index;
    const previous = state.pair[index];
    state.pair[index] = selected;
    const adjusted = state.pair[other] === selected;
    if (adjusted) state.pair[other] = previous;
    renderPair();
    save();
    const names = state.pair.map(id => context.routes.find(route => route.id === id).island);
    controls.pairStatus.textContent = `${adjusted ? "La otra selección se ha ajustado para comparar dos islas distintas. " : ""}Comparas ${names[0]} y ${names[1]}. Cada pareja conserva su propia reflexión.`;
  }

  function setLevel(level) {
    currentLevel = ["early", "middle", "advanced", "secondary"].includes(level) ? level : "middle";
    if (!controls) return;
    const prompts = {
      early: "Con una persona adulta, cuenta o señala algo que se parezca y algo que cambie. Puedes responder oralmente; escribir es opcional.",
      middle: "Cuenta una semejanza y una diferencia entre los dos cuentos. Puedes hablar con tu pareja o anotarlas brevemente.",
      advanced: "Explica una semejanza y una diferencia. Relaciona una acción con su consecuencia y utiliza un ejemplo de cada cuento.",
      secondary: "Compara las causas y consecuencias del conflicto. Distingue lo que cuenta esta recreación de lo que podrías sostener con una fuente; anota qué necesitarías contrastar."
    };
    controls.levelPrompt.textContent = prompts[currentLevel];
  }

  function download() {
    const reflection = controls.note.value.trim();
    if (!reflection) return;
    save();
    const names = state.pair.map(id => context.routes.find(route => route.id === id).island);
    const text = [
      "MitoMapa canario — Dos cuentos, una conversación",
      `Islas: ${names.join(" y ")}`,
      "Actividad opcional sobre recreaciones literarias; no acredita hechos históricos ni concede pintaderas.",
      "", "Nuestra comparación", reflection, "",
      "Para continuar: ¿qué se parece?, ¿qué cambia?, ¿cómo influyen las decisiones de los personajes?"
    ].join("\n");
    context.downloadText(text, "comparacion-mitomapa.txt", "text/plain;charset=utf-8");
    controls.saved.textContent = "Comparación preparada para descargar. Compártela si tu docente te lo indica.";
  }

  function init(options) {
    if (section || !options || !Array.isArray(options.routes) || options.routes.length < 2) return;
    const anchor = document.getElementById("finalMission");
    if (!anchor) return;
    context = options;
    let raw;
    try { raw = context.readJSON(storageKey, {}); }
    catch (error) { raw = {}; }
    state = sanitize(raw);
    section = node("section", "section panel compare-stories");
    section.id = "compareStories";
    section.setAttribute("aria-labelledby", "compareStoriesTitle");
    const eyebrow = node("p", "compare-kicker", "Exploración opcional");
    const heading = node("h2", "section-title", "Dos cuentos, una conversación");
    heading.id = "compareStoriesTitle";
    const intro = node("p", "compare-intro", "Elige dos islas y busca conexiones entre sus relatos. Las tarjetas resumen acontecimientos de las recreaciones literarias de MitoMapa: no son pruebas de hechos históricos. Esta conversación no cambia las pintaderas ni el diploma.");
    const selectorRow = node("div", "compare-selectors");
    const selects = [0, 1].map(index => {
      const label = node("label", "compare-select-label");
      label.append(node("span", "", index === 0 ? "Primer cuento" : "Segundo cuento"));
      const select = document.createElement("select");
      context.routes.forEach(route => {
        const option = node("option", "", route.island);
        option.value = route.id;
        select.append(option);
      });
      select.addEventListener("change", () => changeIsland(index, select.value));
      label.append(select);
      selectorRow.append(label);
      return select;
    });
    const swap = node("button", "button secondary compare-swap", "Intercambiar cuentos");
    swap.type = "button";
    selectorRow.append(swap);
    const pairStatus = node("p", "compare-pair-status");
    pairStatus.setAttribute("role", "status");
    const cardGrid = node("div", "compare-card-grid");
    const cards = [makeCard(0), makeCard(1)];
    cards.forEach(card => cardGrid.append(card.card));
    const conversation = node("div", "compare-conversation");
    conversation.append(node("h3", "", "Pistas para conversar"));
    const questions = node("ul", "compare-questions");
    ["¿Qué paisaje o elemento de la naturaleza importa en cada cuento?", "¿Qué problema aparece y quién ayuda a afrontarlo?", "¿Qué decisión de un personaje cambia el desenlace?", "¿Qué se parece y qué es diferente? Usa un acontecimiento de cada relato."].forEach(question => questions.append(node("li", "", question)));
    const levelPrompt = node("p", "compare-level-prompt");
    levelPrompt.id = "compareLevelPrompt";
    conversation.append(questions, levelPrompt);
    const noteLabel = node("label", "compare-note-label", "Nuestra comparación (opcional)");
    noteLabel.htmlFor = "compareNote";
    const note = node("textarea", "compare-note");
    note.id = "compareNote";
    note.maxLength = maxLength;
    note.rows = 5;
    note.setAttribute("aria-describedby", "compareLevelPrompt compareNoteHelp compareNoteCounter");
    const help = node("p", "compare-note-help", "Se guarda solo en este navegador, por pareja de islas. Puedes responder oralmente. No incluyas nombres ni otros datos personales.");
    help.id = "compareNoteHelp";
    const counter = node("p", "compare-note-counter");
    counter.id = "compareNoteCounter";
    const downloadButton = node("button", "button compare-download", "Descargar nuestra comparación");
    downloadButton.type = "button";
    downloadButton.addEventListener("click", download);
    const saved = node("p", "compare-saved");
    saved.setAttribute("role", "status");
    controls = { selects, cards, pairStatus, levelPrompt, note, counter, download: downloadButton, saved };
    note.addEventListener("input", () => {
      const key = canonicalKey(state.pair);
      const text = note.value.slice(0, maxLength);
      if (text) state.notes[key] = text;
      else delete state.notes[key];
      renderNote();
      scheduleSave();
    });
    note.addEventListener("change", save);
    window.addEventListener("pagehide", () => {
      if (saveTimer !== null) save();
    });
    document.addEventListener("visibilitychange", () => {
      if (document.hidden && saveTimer !== null) save();
    });
    swap.addEventListener("click", () => {
      state.pair.reverse();
      renderPair();
      save();
      pairStatus.textContent = "Cuentos intercambiados. La reflexión de esta pareja se conserva.";
    });
    section.append(eyebrow, heading, intro, selectorRow, pairStatus, cardGrid, conversation, noteLabel, note, help, counter, downloadButton, saved);
    anchor.before(section);
    renderPair();
    setLevel(options.level);
  }

  function exportState() {
    if (!state) return undefined;
    return { pair: [...state.pair], notes: { ...state.notes } };
  }

  function importState(raw) {
    if (!context) return;
    if (saveTimer !== null) window.clearTimeout(saveTimer);
    saveTimer = null;
    state = sanitize(raw);
    if (controls) {
      renderPair();
      controls.pairStatus.textContent = "Comparaciones actualizadas. Cada pareja conserva su propia reflexión.";
    }
    save();
  }

  function reset() { importState(undefined); }

  window.MitoMapaCompare = { init, setLevel, reset, exportState, importState };
}());
