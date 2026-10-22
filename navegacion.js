/* Vistas de la expedición. Se conserva el DOM y el progreso de las actividades. */
(() => {
  "use strict";
  let context;
  let current = "inicio";
  const titles = {inicio:"Inicio",islas:"Islas",juegos:"Juegos",recursos:"Recursos",puzle:"Puzle",comparar:"Comparar cuentos","nombres-islas":"Los nombres de las islas","piezas-islas":"Las piezas y sus islas","gran-reto":"Gran reto",ruta:"Cuento"};
  const aliases = {main:"inicio",exploreMap:"islas",islandGrid:"islas",missionTitle:"puzle",compareStories:"comparar",finalMission:"gran-reto",finalTitle:"gran-reto",reuseTitle:"recursos",creditsTitle:"recursos",passportTitle:"recursos",studentFeedback:"recursos",feedbackTitle:"recursos",acknowledgements:"recursos",acknowledgementsTitle:"recursos"};
  const byId = id => document.getElementById(id);
  function record(hash, replace = false) {
    if (location.hash === hash) return;
    history[replace ? "replaceState" : "pushState"](null, "", hash);
  }
  function reveal(screen) {
    if (screen !== "piezas-islas") window.MitoMapaPieces?.cancelDrag();
    current = screen;
    document.querySelectorAll("[data-screen]").forEach(pane => {pane.hidden = pane.dataset.screen !== screen;});
    const group = screen === "ruta" ? "islas" : ["puzle","comparar","nombres-islas","piezas-islas","gran-reto"].includes(screen) ? "juegos" : screen;
    document.querySelectorAll(".main-navigation a").forEach(link => {
      if (link.dataset.nav === group) link.setAttribute("aria-current","page");
      else link.removeAttribute("aria-current");
    });
    const crumb = byId("navigationLocation");
    if (crumb) crumb.textContent = screen === "ruta" ? "Islas · " + (context.routes.find(r => r.id === context.lastRoute())?.island || "Cuento") : titles[screen];
    document.title = `${titles[screen]} · MitoMapa canario`;
  }
  function focusTarget(target) {
    if (!target) return;
    for (let parent = target.parentElement; parent; parent = parent.parentElement) if (parent.tagName === "DETAILS") parent.open = true;
    target.setAttribute("tabindex","-1");
    target.scrollIntoView({block:"start",behavior:"auto"});
    target.focus({preventScroll:true});
  }
  function go(raw, {history: addHistory = true, focus = true, replace = false} = {}) {
    const name = String(raw || "inicio").replace(/^#/, "");
    const routeMatch = /^(?:isla\/|route-)([a-z-]+)(?:\/(cuento|retos|taller))?$/.exec(name);
    if (routeMatch && context.routes.some(r => r.id === routeMatch[1])) {
      context.openRoute(routeMatch[1], {history:addHistory,step:routeMatch[2] || "cuento"});
      return true;
    }
    const screen = aliases[name] || name;
    if (!Object.hasOwn(titles,screen) || screen === "ruta") return false;
    context.stopNarration();
    reveal(screen);
    if (screen === "puzle") document.querySelector(".puzzle-disclosure").open = true;
    if (addHistory) record(`#${aliases[name] ? name : screen}`,replace);
    if (focus) {
      const pane = document.querySelector(`[data-screen="${screen}"]`);
      focusTarget(aliases[name] && byId(name) ? byId(name) : pane?.querySelector("h1,h2"));
    }
    return true;
  }
  function activateRoute(id, {history: addHistory = true, step} = {}) {
    reveal("ruta");
    const route = context.routes.find(r => r.id === id);
    byId("navigationLocation").textContent = `Islas · ${route?.island || "Cuento"}`;
    document.title = `${route?.island || "Cuento"} · MitoMapa canario`;
    const selected = step || byId(`route-${id}`)?.dataset.routeFlowStep || "cuento";
    if (selected !== "cuento") context.stopNarration();
    if (addHistory) record(`#isla/${id}/${selected}`);
    return selected;
  }
  function disclosure(section, label, id) {
    const details = document.createElement("details");
    details.className = "resource-disclosure";
    details.id = id;
    const summary = document.createElement("summary");summary.textContent = label;
    details.append(summary,section);
    return details;
  }
  function mount(options) {
    context = options;
    document.body.dataset.navigationInput = "pointer";
    document.addEventListener("keydown",event => {
      if (["Tab","Enter"," ","ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Home","End"].includes(event.key)) document.body.dataset.navigationInput = "keyboard";
    },true);
    document.addEventListener("pointerdown",() => {document.body.dataset.navigationInput = "pointer";},true);
    const main = byId("main");
    const hero = main.querySelector(".hero");hero.dataset.screen = "inicio";
    const map = byId("exploreMap");map.dataset.screen = "islas";
    const islandChooser = document.createElement("details");
    islandChooser.className = "island-list-disclosure";
    islandChooser.innerHTML = '<summary>Ver las ocho islas en una lista</summary>';
    islandChooser.append(byId("islandGrid"));map.append(islandChooser);
    const passport = byId("passportTitle").closest("section");
    byId("passportTitle").textContent = "Pasaporte de piezas";
    passport.querySelector(":scope > h3")?.remove();
    const games = document.createElement("section");
    games.className = "section screen-intro";games.dataset.screen = "juegos";
    games.innerHTML = `<p class="eyebrow">Sigue explorando</p><h1>Juegos para compartir</h1><p>Elige una actividad. Puedes volver a los cuentos cuando quieras.</p><div class="activity-choices"><a href="#puzle" class="activity-choice"><span class="choice-symbol" aria-hidden="true">▦</span><h2>Reconstruye el mapa</h2><p>Coloca las doce piezas del archipiélago.</p><span class="choice-action">Abrir puzle →</span></a><a href="#comparar" class="activity-choice"><span class="choice-symbol" aria-hidden="true">↔</span><h2>Compara dos cuentos</h2><p>Descubre sus semejanzas y guarda tus ideas.</p><span class="choice-action">Elegir cuentos →</span></a><a href="#gran-reto" class="activity-choice"><span class="choice-symbol" aria-hidden="true">✦</span><h2>Conecta las ocho islas</h2><p>Reúne las ocho piezas para abrir el reto final.</p><span class="choice-action">Ver gran reto →</span></a></div>`;
    main.append(games);
    const namesChoice = document.createElement("a");
    namesChoice.href = "#nombres-islas";namesChoice.className = "activity-choice";
    namesChoice.innerHTML = '<span class="choice-symbol" aria-hidden="true">⌖</span><h2>Los nombres de las islas</h2><p>Relaciona denominaciones históricas con sus islas en una carta de aspecto antiguo.</p><span class="choice-action">Explorar los nombres →</span>';
    games.querySelector(".activity-choices").append(namesChoice);
    const piecesChoice = document.createElement("a");
    piecesChoice.href = "#piezas-islas";piecesChoice.className = "activity-choice";
    piecesChoice.innerHTML = '<span class="choice-symbol" aria-hidden="true">◈</span><h2>Las piezas y sus islas</h2><p>Observa las siete vasijas y la caracola y relaciona cada pieza con su isla en el recurso.</p><span class="choice-action">Colocar las piezas →</span>';
    games.querySelector(".activity-choices").append(piecesChoice);
    const gamePanes = [[byId("missionTitle").closest("section"),"puzle"],[byId("compareStories"),"comparar"],[byId("namesMapGame"),"nombres-islas"],[byId("piecesMapGame"),"piezas-islas"],[byId("finalMission"),"gran-reto"]];
    for (const [pane, screen] of gamePanes) {
      pane.dataset.screen = screen;
      const back = document.createElement("a");back.href = "#juegos";back.className = "view-back";back.textContent = "← Volver a Juegos";pane.prepend(back);
    }
    byId("missionTitle").textContent = "Reconstruye el mapa";
    byId("finalTitle").textContent = "Conecta las ocho islas";
    byId("routes").dataset.screen = "ruta";
    const resources = document.createElement("section");
    resources.className = "section screen-intro";resources.dataset.screen = "recursos";
    resources.innerHTML = '<p class="eyebrow">Para consultar cuando lo necesites</p><h1>Recursos y ayuda</h1><p>Abre el apartado que buscas.</p>';
    resources.append(
      disclosure(byId("reuseTitle").closest("section"),"Descargas y materiales editables","resourceDownloads"),
      disclosure(byId("creditsTitle").closest("section"),"Guía, autoría, fuentes y agradecimientos","resourceCredits"),
      disclosure(main.querySelector(".historical-review"),"Historia e interpretación de las imágenes","resourceHistory"),
      disclosure(passport,"Pasaporte de piezas y criterios de los retos","resourcePassport"),
      disclosure(byId("studentFeedback"),"Compartir mi opinión","resourceFeedback")
    );
    main.append(resources);
    const tools = hero.querySelector(".experience-tools");
    if (tools) {
      const settings = document.createElement("details");settings.className = "reading-settings";settings.id = "readingSettings";
      settings.innerHTML = '<summary>Etapa y ajustes de lectura</summary>';
      tools.before(settings);settings.append(tools);
      tools.querySelector("h2")?.remove();
      const resume = byId("resumeRoute");resume.textContent = "Continuar mi última isla";resume.className = "button secondary";
      byId("homeActions").append(resume);
    }
    const reset = byId("resetProgress");
    reset.classList.add("teacher-reset");(byId("teacherToolsPanel")||byId("teacherDialog")).append(reset);
    document.body.classList.add("navigation-ready");
    document.addEventListener("click", event => {
      const link = event.target.closest("a[href^='#']");
      if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      if (link.classList.contains("skip-link")) {
        event.preventDefault();
        focusTarget(current === "ruta" ? document.querySelector(".route.active h2") : document.querySelector(`[data-screen="${current}"] h1,[data-screen="${current}"] h2`));
        return;
      }
      if (go(link.getAttribute("href"))) event.preventDefault();
    });
    window.addEventListener("hashchange", () => {if (!go(location.hash,{history:false})) go("inicio",{history:false});});
    document.addEventListener("mitomapa:route-step", event => {
      if (current !== "ruta") return;
      const {routeId,step} = event.detail;
      if (step !== "cuento") context.stopNarration();
      record(`#isla/${routeId}/${step}`);
    });
    if (!go(location.hash,{history:false,focus:Boolean(location.hash)})) go("inicio",{history:false,focus:false});
  }
  function refresh() {
    if (current === "ruta" && !document.querySelector(".route.active")) go(location.hash,{history:false});
  }
  window.MitoMapaNavigation = {mount,go,activateRoute,refresh};
})();
