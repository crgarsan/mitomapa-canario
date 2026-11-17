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
      legend.textContent = "Islands to work on";
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

  function routeBriefs() {
    const selected = new Set(selection());
    for (const section of document.querySelectorAll(".route")) {
      const id = section.id.replace(/^route-/,"");
      if (!context.routes.some(route=>route.id===id)) continue;
      let brief=section.querySelector(".route-session-brief");
      if (!brief) {
        brief=document.createElement("div");brief.className="route-session-brief";
        const title=document.createElement("p"),strong=document.createElement("strong");strong.textContent="Today’s work";title.append(strong);
        const task=document.createElement("p");task.className="route-session-task";
        const links=document.createElement("p");links.className="route-session-links";
        const workshop=document.createElement("a");workshop.href=`#isla/${id}/taller`;workshop.textContent="Go to the workshop";
        const closure=document.createElement("a");closure.href="#crear";closure.textContent="Create and share";
        links.append(workshop,closure);brief.append(title,task,links);
        section.querySelector(".route-head")?.after(brief);
      }
      const assignment=context.assignment?.(id);
      const tasks=Array.isArray(assignment?.selectedTasks)?assignment.selectedTasks:[];
      const names={words:"explore vocabulary",research:"check a source",creation:"create something to share"};
      const extra=tasks.filter(key=>Object.hasOwn(names,key)).map(key=>names[key]);
      const agreed=typeof assignment?.tasks==="string"?assignment.tasks.trim():"";
      brief.querySelector(".route-session-task").textContent=agreed || `${selected.has(id)?"Agreed route":"Suggested activity"}: read or listen to the story${extra.length?", "+extra.join(", "):" and discuss what happens"}.`;
    }
  }

  function refresh() {
    if (!context) return;
    renderChoices();
    const result = summary();
    const message = result.selected
      ? `Agreed route: ${result.reviewed}/${result.selected} islands reviewed with your teacher.`
      : "Agree on the islands you will work on. You can still explore all the islands.";
    const status = byId("agreedRouteSummary");
    if (status) {
      status.hidden = result.selected === 0;
      status.textContent = message;
    }
    const teacherStatus = byId("agreedRouteTeacherStatus");
    if (teacherStatus) teacherStatus.textContent = message;
    const collection = byId("agreedRouteCollection");
    if (collection) collection.textContent = `Full collection: ${context.badgeCount()}/${context.routes.length} pieces. The collection is separate from the agreed route.`;
    const completion = byId("agreedRouteCompletion");
    if (completion) {
      completion.hidden = !result.complete;
      const text = byId("agreedRouteCompletionText");
      if (text) text.textContent = `You have reviewed the agreed work on ${result.selected} ${result.selected === 1 ? "island" : "islands"}. Share what you learned and what you would try next time. You can continue exploring other routes whenever you like.`;
    }
    const itinerarySummary = byId("itinerarySummary");
    if (itinerarySummary && result.selected) itinerarySummary.textContent = `${message} Collection: ${context.badgeCount()}/${context.routes.length} pieces.`;
    const progress = byId("progressText");
    if (progress) {
      progress.textContent=result.selected?`My route: ${result.reviewed}/${result.selected} islands reviewed`:"Free exploration";
      progress.title=result.selected?"Review of the agreed route with the teacher. The piece collection is separate.":"Choose any island. The passport shows your collection.";
      const wrapper=progress.closest(".progress-wrap");
      if(wrapper){wrapper.classList.add("session-progress");wrapper.dataset.routeAgreed=String(result.selected>0);wrapper.setAttribute("aria-label","Agreed route progress");}
    }
    routeBriefs();
    window.MitoMapaNavigation?.refreshResume?.();
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
