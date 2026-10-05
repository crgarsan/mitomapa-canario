/* Secuencias opcionales de lectura. Solo guardan el orden de las tarjetas. */
(function () {
  "use strict";

  const STORAGE_KEY = "mitomapa-canario-secuencias-v1";
  const EVENTS = Object.freeze({
    tenerife: Object.freeze([
      "Una nube negra cubre Echeyde y la luz de Magec no llega.",
      "Dácil reúne a los niños junto al fuego y piden ayuda a Achamán.",
      "Achamán vence a Guayota, libera a Magec y cierra el volcán.",
      "La luz regresa y Dácil cuenta la historia a su comunidad."
    ]),
    "gran-canaria": Object.freeze([
      "Guayarmina reúne el rebaño junto a una cueva al ponerse el sol.",
      "Una criatura de pelo negro aparece entre las tabaibas.",
      "Los pastores levantan sus teas y Guayarmina pide protección a Acorán.",
      "Al clarear, la criatura desaparece y Guayarmina cuenta lo ocurrido."
    ]),
    "la-palma": Object.freeze([
      "Acerina acompaña a su abuelo y lleva una vasija hasta Idafe.",
      "La tierra vibra y el grupo se aleja del risco.",
      "El ruido termina; Idafe sigue en pie y Acerina deja su vasija.",
      "Con los años, Acerina cuenta lo vivido a los niños desde un lugar seguro."
    ]),
    "la-gomera": Object.freeze([
      "Gara escucha en un manantial la advertencia de apartarse del fuego.",
      "Jonay cruza el mar desde Tenerife y conoce a Gara.",
      "Sus familias se oponen y los jóvenes huyen hacia la cumbre.",
      "Tras el final triste, las comunidades recuerdan el daño de la falta de escucha."
    ]),
    "el-hierro": Object.freeze([
      "Agarfa recoge el agua que cae del Garoé en las piletas.",
      "Aparecen velas desconocidas y las personas mayores temen por la fuente.",
      "La comunidad oculta el sendero y Agarfa lleva las vasijas por otro camino.",
      "Mucho después, las familias siguen contando la historia del Garoé."
    ]),
    fuerteventura: Object.freeze([
      "Guise y Ayose usan madera de una cruz para encender una hoguera.",
      "De las llamas sale una luz que sigue a los pastores.",
      "Los pastores prometen reparar la cruz y la claridad desaparece.",
      "Al día siguiente, reparan la cruz y cuentan lo sucedido."
    ]),
    lanzarote: Object.freeze([
      "El consejo decide someter a Ico a una prueba injusta.",
      "Una anciana le entrega una esponja mojada antes de la prueba.",
      "Ico respira a través de la esponja y sale caminando del recinto.",
      "Ico agradece la ayuda y cuestiona la decisión del consejo."
    ]),
    "la-graciosa": Object.freeze([
      "Guadarfía ve una tierra desconocida detrás de la bruma.",
      "La tripulación cambia de rumbo para acercarse a ella.",
      "Una niebla espesa obliga a bajar las velas y esperar.",
      "Al amanecer solo queda el mar y dibujan la isla que recuerdan."
    ])
  });
  const LEVELS = new Set(["early", "middle", "advanced", "secondary"]);
  const panels = new Map();
  let readJSON = null;
  let writeJSON = null;
  let level = "middle";
  let initialized = false;
  let state = { version: 1, routes: {} };

  function isRecord(value) {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
  }

  function validOrder(order) {
    return Array.isArray(order) && order.length === 4 &&
      order.every(value => Number.isInteger(value) && value >= 0 && value < 4) &&
      new Set(order).size === 4;
  }

  function isSolved(order) {
    return order.every((value, index) => value === index);
  }

  function sanitize(raw) {
    const clean = { version: 1, routes: {} };
    if (!isRecord(raw) || !isRecord(raw.routes)) return clean;
    Object.keys(EVENTS).forEach(id => {
      if (!Object.prototype.hasOwnProperty.call(raw.routes, id)) return;
      const entry = raw.routes[id];
      if (!isRecord(entry) || !validOrder(entry.order)) return;
      clean.routes[id] = {
        order: entry.order.slice(),
        checked: entry.checked === true,
        hint: entry.hint === true,
        support: entry.support === true
      };
    });
    return clean;
  }

  function exportState() {
    const result = sanitize(state);
    Object.values(result.routes).forEach(entry => {
      entry.passed = entry.checked && isSolved(entry.order);
    });
    return result;
  }

  function persist() {
    if (!writeJSON) return;
    let stored = false;
    try { stored = writeJSON(STORAGE_KEY, exportState()) !== false; }
    catch (error) { stored = false; }
    panels.forEach(panel => {
      const note = panel.querySelector(".story-sequence-storage");
      note.hidden = stored;
      note.textContent = stored ? "" : "El navegador no pudo guardar el cambio. Puedes seguir practicando durante esta sesión.";
    });
  }

  function shuffledOrder(previous) {
    for (let attempt = 0; attempt < 12; attempt += 1) {
      const order = [0, 1, 2, 3];
      for (let index = 3; index > 0; index -= 1) {
        const other = Math.floor(Math.random() * (index + 1));
        [order[index], order[other]] = [order[other], order[index]];
      }
      if (!isSolved(order) && (!previous || order.some((value, index) => value !== previous[index]))) return order;
    }
    return previous && previous.join(",") === "2,0,3,1" ? [1, 3, 0, 2] : [2, 0, 3, 1];
  }

  function routeState(id) {
    if (!state.routes[id]) {
      state.routes[id] = { order: shuffledOrder(), checked: false, hint: false, support: false };
    }
    return state.routes[id];
  }

  function instruction() {
    if (level === "early") return "Con una persona adulta, escucha cada tarjeta y decide qué ocurre primero. Muévelas con Subir y Bajar. Después, cuenta el cuento con tus palabras.";
    if (level === "secondary") return "Reconstruye la secuencia con Subir y Bajar. Después, explica una relación de causa y consecuencia y distingue el relato de la información histórica.";
    return "Ordena las cuatro tarjetas con Subir y Bajar. Comprueba el resultado y explica qué pasó antes y después.";
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function button(text, action, className) {
    const control = element("button", className || "story-sequence-button", text);
    control.type = "button";
    control.dataset.action = action;
    return control;
  }

  function resultText(entry) {
    if (!entry.checked) return "Mueve las tarjetas y comprueba tu secuencia cuando estés preparado.";
    const correct = entry.order.filter((value, index) => value === index).length;
    if (correct === 4) return `Resultado: 4 de 4. Has reconstruido el orden del cuento${entry.support ? " con el orden de apoyo" : ""}. Ahora explícalo con tus palabras.`;
    return `Resultado: ${correct} de 4 en su lugar. Lee las pistas de cada tarjeta, vuelve al cuento y prueba de nuevo.`;
  }

  function render(panel, focusTarget, announcement) {
    const id = panel.dataset.route;
    const entry = routeState(id);
    const list = panel.querySelector(".story-sequence-list");
    list.replaceChildren();
    entry.order.forEach((eventId, index) => {
      const item = element("li", "story-sequence-card");
      item.dataset.event = String(eventId);
      const position = element("span", "story-sequence-position", String(index + 1));
      position.setAttribute("aria-hidden", "true");
      const text = element("p", "story-sequence-text", EVENTS[id][eventId]);
      text.id = `story-sequence-text-${id}-${eventId}`;
      const controls = element("div", "story-sequence-move");
      const up = button("↑ Subir", "up");
      const down = button("↓ Bajar", "down");
      up.disabled = index === 0;
      down.disabled = index === 3;
      [up, down].forEach(control => {
        control.setAttribute("aria-label", `${control.dataset.action === "up" ? "Subir" : "Bajar"} este acontecimiento`);
        control.setAttribute("aria-describedby", `${text.id} story-sequence-feedback-${id}-${eventId}`);
      });
      controls.append(up, down);
      const feedback = element("p", "story-sequence-feedback");
      feedback.id = `story-sequence-feedback-${id}-${eventId}`;
      if (entry.checked) {
        const correct = eventId === index;
        item.classList.add(correct ? "story-sequence-correct" : "story-sequence-revise");
        feedback.textContent = correct ? "✓ Correcto: está en su lugar en el cuento." : `Revisa: este acontecimiento ocurre ${eventId < index ? "antes" : "después"} en el cuento.`;
      }
      item.append(position, text, controls, feedback);
      list.append(item);
    });
    panel.querySelector(".story-sequence-instruction").textContent = instruction();
    const hint = panel.querySelector(".story-sequence-hint");
    hint.hidden = !entry.hint;
    hint.textContent = `Pista: el primer acontecimiento es «${EVENTS[id][0]}»`;
    panel.querySelector(".story-sequence-support").hidden = !entry.support;
    panel.querySelector(".story-sequence-status").textContent = announcement || resultText(entry);
    panel.classList.toggle("story-sequence-passed", entry.checked && isSolved(entry.order));
    if (focusTarget) {
      const item = [...list.children].find(card => Number(card.dataset.event) === focusTarget.eventId);
      const preferred = item?.querySelector(`[data-action="${focusTarget.direction}"]`);
      const control = preferred && !preferred.disabled ? preferred : item?.querySelector("button:not(:disabled)");
      control?.focus();
    }
  }

  function handleAction(panel, event) {
    const control = event.target.closest("button[data-action]");
    if (!control || !panel.contains(control) || control.disabled) return;
    const id = panel.dataset.route;
    const entry = routeState(id);
    const action = control.dataset.action;
    let focusTarget = null;
    let announcement = "";
    if (action === "up" || action === "down") {
      const eventId = Number(control.closest(".story-sequence-card").dataset.event);
      const index = entry.order.indexOf(eventId);
      const next = index + (action === "up" ? -1 : 1);
      if (next < 0 || next > 3) return;
      [entry.order[index], entry.order[next]] = [entry.order[next], entry.order[index]];
      entry.checked = false;
      focusTarget = { eventId, direction: action };
      announcement = `Acontecimiento movido a la posición ${next + 1} de 4. Comprueba tu secuencia cuando estés preparado.`;
    } else if (action === "check") {
      entry.checked = true;
    } else if (action === "hint") {
      entry.hint = true;
      announcement = `Pista: el primer acontecimiento es «${EVENTS[id][0]}»`;
    } else if (action === "support") {
      entry.support = true;
      announcement = "El orden de apoyo está visible debajo de las tarjetas. Compáralo con tu secuencia o vuelve a mezclar para practicar.";
    } else if (action === "shuffle") {
      entry.order = shuffledOrder(entry.order);
      entry.checked = false;
      entry.hint = false;
      entry.support = false;
      announcement = "Tarjetas mezcladas de nuevo. Reconstruye el cuento a tu ritmo.";
    } else return;
    render(panel, focusTarget, announcement);
    persist();
  }

  function enhanceRoute(section, route, currentLevel) {
    const id = typeof route === "string" ? route : route?.id;
    if (!section || !Object.prototype.hasOwnProperty.call(EVENTS, id)) return null;
    if (LEVELS.has(currentLevel)) level = currentLevel;
    const existing = section.querySelector(".story-sequence");
    if (existing) {
      panels.set(id, existing);
      render(existing);
      return existing;
    }
    const comprehension = section.querySelector(".source-quiz");
    const reading = section.querySelector(".route-grid");
    if (!comprehension && !reading) return null;
    const panel = element("section", "story-sequence");
    panel.dataset.route = id;
    panel.setAttribute("aria-labelledby", `story-sequence-title-${id}`);
    const kicker = element("p", "story-sequence-kicker", "Práctica opcional · A tu ritmo");
    const title = element("h3", "", "Ordena el cuento");
    title.id = `story-sequence-title-${id}`;
    const instructions = element("p", "story-sequence-instruction");
    const note = element("p", "story-sequence-note", "Puedes usar las pistas y el orden de apoyo tantas veces como necesites. Tu orden se guarda en este navegador cuando el almacenamiento está disponible.");
    const list = element("ol", "story-sequence-list");
    list.setAttribute("aria-label", "Acontecimientos del cuento: cambia su orden con los botones");
    const actions = element("div", "story-sequence-actions");
    actions.append(
      button("Comprobar el orden", "check", "story-sequence-button story-sequence-check"),
      button("Pista del comienzo", "hint"),
      button("Mostrar orden de apoyo", "support"),
      button("Volver a mezclar", "shuffle")
    );
    const status = element("p", "story-sequence-status");
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    status.setAttribute("aria-atomic", "true");
    const hint = element("p", "story-sequence-hint");
    const support = element("div", "story-sequence-support");
    const supportTitle = element("h4", "", "Orden de apoyo");
    const supportList = element("ol", "");
    EVENTS[id].forEach(text => supportList.append(element("li", "", text)));
    support.append(supportTitle, supportList);
    const source = element("p", "story-sequence-source", "Estos resúmenes proceden del cuento de esta ruta, una recreación literaria. Su orden narrativo no demuestra hechos históricos. La fundamentación se explica al final del cuento en «Explora a fondo». ");
    const credits = element("a", "", "Consultar créditos y fuentes del recurso");
    credits.href = "#creditsTitle";
    source.append(credits);
    const storage = element("p", "story-sequence-storage");
    storage.hidden = true;
    panel.append(kicker, title, instructions, note, list, actions, status, hint, support, source, storage);
    panel.addEventListener("click", event => handleAction(panel, event));
    if (comprehension) comprehension.before(panel);
    else reading.after(panel);
    panels.set(id, panel);
    render(panel);
    persist();
    return panel;
  }

  function refreshPanels() {
    panels.forEach((panel, id) => {
      if (!panel.isConnected) {
        panels.delete(id);
        return;
      }
      render(panel);
    });
  }

  function setLevel(currentLevel) {
    if (LEVELS.has(currentLevel)) level = currentLevel;
    panels.forEach(panel => {
      panel.querySelector(".story-sequence-instruction").textContent = instruction();
    });
  }

  function init(context) {
    const options = context || {};
    if (typeof options.readJSON === "function") readJSON = options.readJSON;
    if (typeof options.writeJSON === "function") writeJSON = options.writeJSON;
    if (!initialized) {
      let saved = null;
      if (readJSON) {
        try { saved = readJSON(STORAGE_KEY, null); }
        catch (error) { saved = null; }
      }
      state = sanitize(saved);
      initialized = true;
      refreshPanels();
    }
    setLevel(options.level);
    return exportState();
  }

  function reset() {
    state = { version: 1, routes: {} };
    refreshPanels();
    persist();
    return exportState();
  }

  function importState(raw) {
    state = sanitize(raw);
    refreshPanels();
    persist();
    return exportState();
  }

  function eventsFor(id) {
    return Object.prototype.hasOwnProperty.call(EVENTS, id) ? EVENTS[id].slice() : [];
  }

  window.MitoMapaStories = Object.freeze({ init, enhanceRoute, setLevel, reset, exportState, importState, eventsFor });
}());
