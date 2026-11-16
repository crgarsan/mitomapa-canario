/* Secuencias opcionales de lectura. Solo guardan el orden de las tarjetas. */
(function () {
  "use strict";

  const STORAGE_KEY = "mitomapa-canario-secuencias-v1";
  const EVENTS = Object.freeze({
    tenerife: Object.freeze([
      "A black cloud covers Echeyde, and the light of Magec fails to appear.",
      "Dácil gathers the children by the fire, and they ask Achamán for help.",
      "Achamán defeats Guayota, frees Magec and seals the volcano.",
      "The light returns, and Dácil tells the story to her community."
    ]),
    "gran-canaria": Object.freeze([
      "At sunset, Guayarmina gathers the herd near a cave.",
      "A creature with black fur appears among the tabaibas.",
      "The goatherds raise their torches, and Guayarmina asks Acorán for protection.",
      "At dawn, the creature disappears, and Guayarmina tells the village what happened."
    ]),
    "la-palma": Object.freeze([
      "Acerina goes with her grandfather and carries a pot to Idafe.",
      "The ground trembles, and the group moves away from the cliff.",
      "The noise stops. Idafe still stands, and Acerina leaves her pot.",
      "Years later, Acerina takes the children to a safe spot and tells them what happened."
    ]),
    "la-gomera": Object.freeze([
      "At a spring, Gara hears a warning to stay away from fire.",
      "Jonay crosses the sea from Tenerife and meets Gara.",
      "Their families oppose them, and the pair flee towards the summit.",
      "After the sad ending, people remember the harm caused when communities stop listening to each other."
    ]),
    "el-hierro": Object.freeze([
      "Agarfa collects the water that drips from the Garoé into the stone basins.",
      "Unfamiliar sails appear, and the elders fear for the water supply.",
      "The community hides the path, and Agarfa carries the jars along another route.",
      "Long afterwards, families still tell the story of the Garoé."
    ]),
    fuerteventura: Object.freeze([
      "Guise and Ayose use wood from a cross to light a fire.",
      "A light comes out of the flames and follows the goatherds.",
      "The goatherds promise to mend the cross, and the light disappears.",
      "The next day, they mend the cross and tell others what happened."
    ]),
    lanzarote: Object.freeze([
      "The council decides to put Ico to an unfair test.",
      "An older woman gives Ico a wet sponge before the test.",
      "Ico breathes through the sponge and walks out of the room.",
      "Ico thanks the older woman and questions the council’s decision."
    ]),
    "la-graciosa": Object.freeze([
      "Guadarfía sees an unknown land behind the mist.",
      "The crew changes course to get closer.",
      "Thick fog forces the crew to lower the sails and wait.",
      "At dawn, there is only sea. The crew records what they remember of the island."
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
      note.textContent = stored ? "" : "The browser could not save your change. You can keep practising during this visit.";
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
    if (level === "early") return "With an adult, listen to each card and decide what happens first. Use “Move up” and “Move down” to order the cards. Then retell the story in your own words.";
    if (level === "secondary") return "Use “Move up” and “Move down” to put the events in order. Explain how one event leads to another and which details would need to be checked against historical sources.";
    return "Use “Move up” and “Move down” to order the four cards. Check the order and explain what happened before and after.";
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
    if (!entry.checked) return "Move the cards and check the order when you are ready.";
    const correct = entry.order.filter((value, index) => value === index).length;
    if (correct === 4) return `Result: 4 out of 4. You put the story in order${entry.support ? " using the reference order" : ""}. Now explain with your words.`;
    return `Result: ${correct} of 4 in the right place. Read the hints, return to the story and try again.`;
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
      const up = button("↑ Move up", "up");
      const down = button("↓ Move down", "down");
      up.disabled = index === 0;
      down.disabled = index === 3;
      [up, down].forEach(control => {
        control.setAttribute("aria-label", `${control.dataset.action === "up" ? "Move up" : "Move down"} this event`);
        control.setAttribute("aria-describedby", `${text.id} story-sequence-feedback-${id}-${eventId}`);
      });
      controls.append(up, down);
      const feedback = element("p", "story-sequence-feedback");
      feedback.id = `story-sequence-feedback-${id}-${eventId}`;
      if (entry.checked) {
        const correct = eventId === index;
        item.classList.add(correct ? "story-sequence-correct" : "story-sequence-revise");
        feedback.textContent = correct ? "✓ Correct. This event is in the right place." : `Check again. This event happens ${eventId < index ? "antes" : "after"} in the story.`;
      }
      item.append(position, text, controls, feedback);
      list.append(item);
    });
    panel.querySelector(".story-sequence-instruction").textContent = instruction();
    const hint = panel.querySelector(".story-sequence-hint");
    hint.hidden = !entry.hint;
    hint.textContent = `Hint. The first event is “${EVENTS[id][0]}»`;
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
      announcement = `Event moved to position ${next + 1} of 4. Check the order when you are ready.`;
    } else if (action === "check") {
      entry.checked = true;
    } else if (action === "hint") {
      entry.hint = true;
      announcement = `Hint. The first event is “${EVENTS[id][0]}»`;
    } else if (action === "support") {
      entry.support = true;
      announcement = "The reference order appears below the cards. Compare it with yours or shuffle the cards again to practise.";
    } else if (action === "shuffle") {
      entry.order = shuffledOrder(entry.order);
      entry.checked = false;
      entry.hint = false;
      entry.support = false;
      announcement = "Cards shuffled. Put the story in order at your own pace.";
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
    const kicker = element("p", "story-sequence-kicker", "Optional practice · At your own pace");
    const title = element("h3", "", "Put the story in order");
    title.id = `story-sequence-title-${id}`;
    const instructions = element("p", "story-sequence-instruction");
    const note = element("p", "story-sequence-note", "Use the hints and reference order as often as you need. Your order is saved in this browser when storage is available.");
    const list = element("ol", "story-sequence-list");
    list.setAttribute("aria-label", "Story events. Use the buttons to change their order.");
    const actions = element("div", "story-sequence-actions");
    actions.append(
      button("Check the order", "check", "story-sequence-button story-sequence-check"),
      button("Hint for the first event", "hint"),
      button("Show the reference order", "support"),
      button("Volver a mezclar", "shuffle")
    );
    const status = element("p", "story-sequence-status");
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    status.setAttribute("aria-atomic", "true");
    const hint = element("p", "story-sequence-hint");
    const support = element("div", "story-sequence-support");
    const supportTitle = element("h4", "", "Reference order");
    const supportList = element("ol", "");
    EVENTS[id].forEach(text => supportList.append(element("li", "", text)));
    support.append(supportTitle, supportList);
    const source = element("p", "story-sequence-source", "These cards summarise the fictional story on this route. To explore its historical background, open the sources at the end of the story in “Explore in depth”. ");
    const credits = element("a", "", "View the credits and sources");
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
