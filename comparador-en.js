/* Comparación opcional de relatos. No modifica los retos ni las piezas. */
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
      ? "Comparison saved in this browser. Choose the same two islands to continue."
      : "Your comparison is still on screen. Download it before closing, as saving in this browser failed.";
    return result;
  }

  function scheduleSave() {
    if (saveTimer !== null) window.clearTimeout(saveTimer);
    controls.saved.textContent = "Saving your comparison…";
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
    figure.append(image, node("figcaption", "compare-card-caption", "Contemporary illustration from the story."));
    const eventsHeading = node("h4", "compare-events-title", "Four events in the story");
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
      card.image.alt = route.imageAlt || `Illustration from the story of ${route.island}.`;
      card.events.replaceChildren();
      const events = context.eventsFor(route.id);
      if (Array.isArray(events)) {
        events.slice(0, 4).forEach(event => card.events.append(node("li", "", String(event))));
      }
      card.button.textContent = `Open the story from ${route.island}`;
    });
    controls.note.value = state.notes[canonicalKey(state.pair)] || "";
    renderNote();
  }

  function renderNote() {
    controls.counter.textContent = `${controls.note.value.length} of ${maxLength} characters.`;
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
    controls.pairStatus.textContent = `${adjusted ? "The other selection changed so you can compare two different islands. " : ""}Comparas ${names[0]} and ${names[1]}. Each couple retains its own reflection.`;
  }

  function setLevel(level) {
    currentLevel = ["early", "middle", "advanced", "secondary"].includes(level) ? level : "middle";
    if (!controls) return;
    const prompts = {
      early: "With an adult, say or point to one similarity and one difference. You can speak your answer. Writing is optional.",
      middle: "Name one similarity and one difference between the stories. Talk about them with a partner or write a short note.",
      advanced: "Explain one similarity and one difference. Link an action to its consequence and use one example from each story.",
      secondary: "Compare the causes and consequences of the conflicts. Distinguish what happens in the stories from what a source could support, and note what you would need to check."
    };
    controls.levelPrompt.textContent = prompts[currentLevel];
  }

  function download() {
    const reflection = controls.note.value.trim();
    if (!reflection) return;
    save();
    const names = state.pair.map(id => context.routes.find(route => route.id === id).island);
    const text = [
      "MitoMapa Canario — Two stories, one conversation",
      `Islas: ${names.join(" and ")}`,
      "An optional activity for comparing fictional stories. Passport progress is independent of this activity.",
      "", "Our comparison", reflection, "",
      "Keep talking. What is similar? What is different? How do the characters’ choices affect what happens?"
    ].join("\n");
    context.downloadText(text, "comparacion-mitomapa.txt", "text/plain;charset=utf-8");
    controls.saved.textContent = "Your comparison is ready to download. Share it if your teacher asks.";
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
    const eyebrow = node("p", "compare-kicker", "Optional exploration");
    const heading = node("h2", "section-title", "Two stories, one conversation");
    heading.id = "compareStoriesTitle";
    const intro = node("p", "compare-intro", "Choose two islands and look for connections between their stories. The cards summarise events created for MitoMapa. The discussion is optional and passport and diploma progress are independent of it.");
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
    conversation.append(node("h3", "", "Questions to talk about"));
    const questions = node("ul", "compare-questions");
    ["Which landscape or feature of nature matters in each story?", "What problem comes up, and who helps to deal with it?", "Which choice by a character changes the ending?", "What is similar and what is different? Use one event from each story."].forEach(question => questions.append(node("li", "", question)));
    const levelPrompt = node("p", "compare-level-prompt");
    levelPrompt.id = "compareLevelPrompt";
    conversation.append(questions, levelPrompt);
    const noteLabel = node("label", "compare-note-label", "Our comparison (optional)");
    noteLabel.htmlFor = "compareNote";
    const note = node("textarea", "compare-note");
    note.id = "compareNote";
    note.maxLength = maxLength;
    note.rows = 5;
    note.setAttribute("aria-describedby", "compareLevelPrompt compareNoteHelp compareNoteCounter");
    const help = node("p", "compare-note-help", "This browser saves a separate comparison for each pair of islands. You can also give your answer aloud. Leave out names and other personal information.");
    help.id = "compareNoteHelp";
    const counter = node("p", "compare-note-counter");
    counter.id = "compareNoteCounter";
    const downloadButton = node("button", "button compare-download", "Download our comparison");
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
      pairStatus.textContent = "Stories swapped. Your notes for this pair of islands are still here.";
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
      controls.pairStatus.textContent = "Comparisons updated. Each pair of islands has its own notes.";
    }
    save();
  }

  function reset() { importState(undefined); }

  window.MitoMapaCompare = { init, setLevel, reset, exportState, importState };
}());
