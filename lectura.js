/* Apoyos visuales personales: independientes de la etapa y del progreso. */
(function () {
  "use strict";

  const KEY = "mitomapa-canario-lectura-v1";
  const DEFAULTS = Object.freeze({ size: "normal", spacing: "normal", width: "medium" });
  const OPTIONS = Object.freeze({
    size: [["normal", "Habitual"], ["large", "Grande"], ["xlarge", "Muy grande"]],
    spacing: [["normal", "Habitual"], ["spacious", "Más separado"]],
    width: [["medium", "Habitual"], ["narrow", "Más estrecho"], ["wide", "Más ancho"]]
  });
  let context = {};
  let preferences = { ...DEFAULTS };

  function clean(raw) {
    const result = { ...DEFAULTS };
    Object.keys(DEFAULTS).forEach(key => {
      if (OPTIONS[key].some(([value]) => value === raw?.[key])) result[key] = raw[key];
    });
    return result;
  }

  function synchronize() {
    Object.keys(DEFAULTS).forEach(key => {
      document.body.dataset[`reading${key[0].toUpperCase()}${key.slice(1)}`] = preferences[key];
      document.querySelectorAll(`.reading-${key}`).forEach(select => { select.value = preferences[key]; });
    });
  }

  function save() {
    synchronize();
    try { context.writeJSON?.(KEY, { ...preferences }); } catch (error) { /* La lectura sigue disponible sin guardado. */ }
  }

  function init(options) {
    context = options || {};
    let stored;
    try { stored = context.readJSON?.(KEY, DEFAULTS); } catch (error) { stored = DEFAULTS; }
    preferences = clean(stored);
    synchronize();
  }

  function makeSetting(key, text, id) {
    const label = document.createElement("label");
    label.htmlFor = `reading-${key}-${id}`;
    label.append(document.createTextNode(text));
    const select = document.createElement("select");
    select.id = label.htmlFor;
    select.className = `reading-${key}`;
    OPTIONS[key].forEach(([value, title]) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = title;
      select.append(option);
    });
    select.value = preferences[key];
    select.addEventListener("change", () => {
      preferences = clean({ ...preferences, [key]: select.value });
      save();
    });
    label.append(select);
    return label;
  }

  function enhance(section, route) {
    const id = route?.id || section?.id?.replace(/^route-/, "");
    if (!section || typeof id !== "string" || !/^[a-z0-9-]+$/.test(id)) return null;
    const previous = section.querySelector(".reading-support");
    if (previous) return previous;
    const grid = section.querySelector(".route-grid");
    const narrator = section.querySelector(".narrator");
    if (!grid || !narrator) return null;

    const support = document.createElement("div");
    support.className = "reading-support";
    support.id = `reading-support-${id}`;
    support.dataset.routeFlowGroup = "cuento";
    grid.before(support);
    support.append(narrator);

    const settings = document.createElement("details");
    settings.className = "reading-settings";
    const summary = document.createElement("summary");
    summary.textContent = "Ajustar lectura";
    const help = document.createElement("p");
    help.textContent = "Estos ajustes se guardan en este navegador y no cambian la etapa ni las actividades.";
    const controls = document.createElement("div");
    controls.className = "reading-controls";
    controls.append(makeSetting("size", "Tamaño del texto", id), makeSetting("spacing", "Interlineado", id), makeSetting("width", "Ancho del texto", id));
    const reset = document.createElement("button");
    reset.type = "button";
    reset.className = "text-button reading-reset";
    reset.textContent = "Restablecer lectura";
    const status = document.createElement("p");
    status.className = "reading-status";
    status.setAttribute("role", "status");
    reset.addEventListener("click", () => {
      preferences = { ...DEFAULTS };
      save();
      status.textContent = "Tamaño, interlineado y ancho restablecidos.";
    });
    controls.append(reset);
    settings.append(summary, help, controls, status);
    support.append(settings);
    return support;
  }

  window.MitoMapaReading = Object.freeze({ init, enhance });
})();
