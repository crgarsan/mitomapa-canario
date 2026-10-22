/* La ruta acordada registra la revisión docente, sin cerrar la exploración libre. */
(() => {
  "use strict";
  const STORAGE_KEY = "mitomapa-canario-ruta-acordada-v1";
  const LEVELS = ["early", "middle", "advanced", "secondary"];
  let context = null;
  let state = {version: 1, levels: {}};
  let renderedLevel = null;
  const byId = id => document.getElementById(id);

  function sanitize(value) {
    const allowed = new Set(context?.routes.map(route => route.id) || []);
    const result = {version: 1, levels: {}};
    for (const level of LEVELS) {
      const selected = Array.isArray(value?.levels?.[level]) ? value.levels[level] : [];
      result.levels[level] = [...new Set(selected.filter(id => typeof id === "string" && allowed.has(id)))];
    }
    return result;
  }

  function selection() {
    return state.levels[context.getLevel()] || [];
  }

  function exportState() {
    return sanitize(state);
  }

  function persist() {
    return context.writeJSON(STORAGE_KEY, state);
  }

  function renderChoices() {
    const choices = byId("agreedRouteChoices");
    if (!choices) return;
    const level = context.getLevel();
    if (renderedLevel !== level || !choices.children.length) {
      choices.replaceChildren();
      const legend = document.createElement("legend");
      legend.textContent = "Islas que vamos a trabajar";
      choices.append(legend);
      for (const route of context.routes) {
        const label = document.createElement("label");
        const input = document.createElement("input");
        input.type = "checkbox";
        input.dataset.agreedRoute = route.id;
        const text = document.createElement("span");
        text.textContent = route.island;
        label.append(input, text);
        choices.append(label);
      }
      renderedLevel = level;
    }
    const selected = new Set(selection());
    choices.querySelectorAll("[data-agreed-route]").forEach(input => {
      input.checked = selected.has(input.dataset.agreedRoute);
    });
  }

  function summary() {
    const ids = selection();
    const reviewed = ids.filter(id => context.isReviewed(id)).length;
    return {selected: ids.length, reviewed, complete: ids.length > 0 && reviewed === ids.length};
  }

  function refresh() {
    if (!context) return;
    renderChoices();
    const result = summary();
    const message = result.selected
      ? `Ruta acordada: ${result.reviewed}/${result.selected} islas revisadas con tu docente.`
      : "Acuerden las islas que van a trabajar. La exploración sigue siendo libre.";
    const status = byId("agreedRouteSummary");
    if (status) {
      status.hidden = result.selected === 0;
      status.textContent = message;
    }
    const teacherStatus = byId("agreedRouteTeacherStatus");
    if (teacherStatus) teacherStatus.textContent = message;
    const collection = byId("agreedRouteCollection");
    if (collection) collection.textContent = `Colección completa: ${context.badgeCount()}/${context.routes.length} piezas. Es independiente de la ruta acordada.`;
    const completion = byId("agreedRouteCompletion");
    if (completion) {
      completion.hidden = !result.complete;
      const text = byId("agreedRouteCompletionText");
      if (text) text.textContent = `Han revisado el trabajo acordado en ${result.selected} ${result.selected === 1 ? "isla" : "islas"}. Comparte qué has aprendido y qué probarías la próxima vez. Puedes seguir explorando otras rutas cuando quieras.`;
    }
    const itinerarySummary = byId("itinerarySummary");
    if (itinerarySummary && result.selected) itinerarySummary.textContent = `${message} Colección: ${context.badgeCount()}/${context.routes.length} piezas.`;
    const progress = byId("progressText");
    if (progress) progress.title = "Colección de ocho piezas; no mide las tareas acordadas con tu docente";
  }

  function importState(value) {
    if (!context) return;
    state = sanitize(value);
    persist();
    refresh();
  }

  function reset() {
    importState(null);
  }

  function init(options) {
    context = options;
    state = sanitize(context.readJSON(STORAGE_KEY, null));
    byId("agreedRouteChoices")?.addEventListener("change", event => {
      const input = event.target.closest("[data-agreed-route]");
      if (!input) return;
      const ids = new Set(selection());
      if (input.checked) ids.add(input.dataset.agreedRoute);
      else ids.delete(input.dataset.agreedRoute);
      state.levels[context.getLevel()] = context.routes.filter(route => ids.has(route.id)).map(route => route.id);
      persist();
      refresh();
      context.onChange?.();
    });
    byId("clearAgreedRoute")?.addEventListener("click", () => {
      state.levels[context.getLevel()] = [];
      persist();
      refresh();
      context.onChange?.();
    });
    refresh();
  }

  window.MitoMapaJourney = {init, refresh, exportState, importState, reset, summary};
})();
