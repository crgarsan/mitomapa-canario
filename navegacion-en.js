/* Vistas de la expedición. Se conserva el DOM y el progreso de las actividades. */
(() => {
  "use strict";
  let context;
  let current = "inicio";
  let resumePoint = null;
  const RESUME_KEY = "mitomapa-canario-ultimo-apartado-v1";
  const STEPS = {cuento:"Story",retos:"Challenges",taller:"Workshop"};
  const LEVELS = ["early","middle","advanced","secondary"];
  const titles = {inicio:"Home",islas:"Islands",juegos:"Games",recursos:"Resources",puzle:"Puzzle",comparar:"Compare stories",crear:"Create and share","nombres-islas":"Island names","piezas-islas":"Match the pieces to their islands","gran-reto":"Final challenge",ruta:"Story"};
  const aliases = {main:"inicio",exploreMap:"islas",islandGrid:"islas",missionTitle:"puzle",compareStories:"comparar",finalMission:"gran-reto",finalTitle:"gran-reto",reuseTitle:"recursos",pintaderas3d:"recursos",vasijacanaria3d:"recursos","lapa-blanca":"recursos",patrimonioNatural3d:"recursos",creditsTitle:"recursos",passportTitle:"recursos",studentFeedback:"recursos",feedbackTitle:"recursos",acknowledgements:"recursos",acknowledgementsTitle:"recursos"};
  const byId = id => document.getElementById(id);
  function validResume(value) {
    return value && typeof value === "object" && !Array.isArray(value)
      && typeof value.routeId === "string" && context.routes.some(route => route.id === value.routeId)
      && typeof value.step === "string" && Object.hasOwn(STEPS,value.step) && LEVELS.includes(value.level)
      ? {routeId:value.routeId,step:value.step,level:value.level} : null;
  }
  function readResume() {
    try {
      if (context.readJSON) return validResume(context.readJSON(RESUME_KEY,null));
      const raw = localStorage.getItem(RESUME_KEY);
      return raw && raw.length < 1000 ? validResume(JSON.parse(raw)) : null;
    } catch (_) { return null; }
  }
  function remember(id,step) {
    const point = validResume({routeId:id,step,level:document.body.dataset.learningLevel});
    if (!point) return;
    resumePoint = point;
    if (context.writeJSON) context.writeJSON(RESUME_KEY,point);
    else try { localStorage.setItem(RESUME_KEY,JSON.stringify(point)); } catch (_) { /* Resume remains available in this visit. */ }
    updateResume();
  }
  function continuation() {
    if (!context) return null;
    const last = context.routes.find(route => route.id === context.lastRoute());
    if (!last) return null;
    const point = resumePoint?.routeId === last.id && resumePoint.level === document.body.dataset.learningLevel ? resumePoint : null;
    return {route:last,step:point?.step || "cuento"};
  }
  function updateResume() {
    const button = byId("resumeRoute"),point = continuation();
    if (!button) return;
    button.disabled = !point;
    button.hidden = !point;
    button.textContent = point ? `Continue your route · ${point.route.island} · ${STEPS[point.step]}` : "Return to my last island";
  }
  function resume() {
    const point = continuation();
    if (!point) return false;
    context.openRoute(point.route.id,{step:point.step});
    return true;
  }
  function resetResume() {
    resumePoint = null;
    if (context.writeJSON) context.writeJSON(RESUME_KEY,null);
    else try { localStorage.removeItem(RESUME_KEY); } catch (_) { /* No stored pupil responses are involved. */ }
    updateResume();
  }
  function record(hash, replace = false) {
    if (location.hash === hash) return;
    history[replace ? "replaceState" : "pushState"](null, "", hash);
  }
  function reveal(screen) {
    if (screen !== "piezas-islas") window.MitoMapaPieces?.cancelDrag();
    current = screen;
    document.querySelectorAll("[data-screen]").forEach(pane => {pane.hidden = pane.dataset.screen !== screen;});
    const group = screen === "ruta" ? "islas" : ["puzle","comparar","crear","nombres-islas","piezas-islas","gran-reto"].includes(screen) ? "juegos" : screen;
    document.querySelectorAll(".main-navigation a").forEach(link => {
      if (link.dataset.nav === group) link.setAttribute("aria-current","page");
      else link.removeAttribute("aria-current");
    });
    const crumb = byId("navigationLocation");
    if (crumb) {
      crumb.hidden = ["inicio","islas","juegos","recursos"].includes(screen);
      crumb.textContent = screen === "ruta" ? "Islands · " + (context.routes.find(r => r.id === context.lastRoute())?.island || "Story") : titles[screen];
    }
    document.title = `${titles[screen]} · MitoMapa Canario`;
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
    if (name === "pistas") {
      go("islas",{history:addHistory,focus,replace});
      byId("exploreMap")?.querySelector(".explore-actions button")?.click();
      return true;
    }
    if (name === "ordenar") {
      const last = context.routes.find(route => route.id === context.lastRoute());
      if (!last) return go("islas",{history:addHistory,focus,replace});
      context.openRoute(last.id,{step:"cuento",history:addHistory});
      const sequence = byId(`route-${last.id}`)?.querySelector(".route-flow-sequence");
      if (sequence) {sequence.open=true;focusTarget(sequence.querySelector("summary"));}
      return true;
    }
    const routeMatch = /^(?:isla\/|route-)([a-z-]+)(?:\/(cuento|retos|taller))?$/.exec(name);
    if (routeMatch && context.routes.some(r => r.id === routeMatch[1])) {
      context.openRoute(routeMatch[1], {history:addHistory,step:routeMatch[2] || "cuento"});
      return true;
    }
    const screen = aliases[name] || name;
    if (!Object.hasOwn(titles,screen) || screen === "ruta") return false;
    context.stopNarration();
    if (screen === "crear") {
      const agreed=window.MitoMapaJourney?.exportState?.()?.levels?.[document.body.dataset.learningLevel] || [];
      const selected=agreed.length?agreed:[context.lastRoute()].filter(Boolean);
      if (selected.length) window.MitoMapaLearning?.initializeClosureRoutes?.(selected);
    }
    reveal(screen);
    if (screen === "puzle") document.querySelector(".puzzle-disclosure").open = true;
    if (name === "islandGrid") byId("exploreMap")?.querySelector('[aria-controls="exploreListPanel"]')?.click();
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
    byId("navigationLocation").textContent = `Islands · ${route?.island || "Story"}`;
    document.title = `${route?.island || "Story"} · MitoMapa Canario`;
    const selected = step || byId(`route-${id}`)?.dataset.routeFlowStep || "cuento";
    if (selected !== "cuento") context.stopNarration();
    remember(id,selected);
    if (addHistory) record(`#isla/${id}/${selected}`);
    return selected;
  }
  function resourceCard(section, id, label, description, icon) {
    const details = document.createElement("details");
    details.className = "resource-disclosure";
    details.id = id;
    const summary = document.createElement("summary");
    summary.className = "activity-choice resource-choice";
    const symbol = document.createElement("span");
    symbol.className = "choice-symbol";
    symbol.setAttribute("aria-hidden", "true");
    if (icon.startsWith("assets/")) {
      const image = document.createElement("img");
      image.src = icon;
      image.alt = "";
      image.width = 36;
      image.height = 36;
      image.loading = "lazy";
      symbol.append(image);
    } else {
      symbol.textContent = icon;
    }
    const title = document.createElement("span");
    title.className = "choice-title";
    title.id = id + "Title";
    title.textContent = label;
    const text = document.createElement("span");
    text.className = "choice-description";
    text.id = id + "Description";
    text.textContent = description;
    summary.setAttribute("aria-labelledby", title.id);
    summary.setAttribute("aria-describedby", text.id);
    const action = document.createElement("span");
    action.className = "choice-action";
    action.setAttribute("aria-hidden", "true");
    action.innerHTML = "<span class=\"resource-action-open\">Open section ↓</span><span class=\"resource-action-close\">Close section ↑</span>";
    summary.append(symbol, title, text, action);
    details.append(summary, section);
    return details;
  }
  function mount(options) {
    context = options;
    resumePoint = readResume();
    document.body.dataset.navigationInput = "pointer";
    document.addEventListener("keydown",event => {
      if (["Tab","Enter"," ","ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Home","End"].includes(event.key)) document.body.dataset.navigationInput = "keyboard";
    },true);
    document.addEventListener("pointerdown",() => {document.body.dataset.navigationInput = "pointer";},true);
    const main = byId("main");
    const hero = main.querySelector(".hero");hero.dataset.screen = "inicio";
    const invitation = hero.querySelector("h1")?.nextElementSibling;
    if (invitation?.tagName === "P") invitation.textContent = "Discover an island, listen to its story and make something to share.";
    const firstAction = byId("homeActions")?.querySelector("a");
    if (firstAction) {firstAction.href="#islas";firstAction.textContent="Choose an island →";}
    const visual = hero.querySelector(".hero-visual");
    if (visual) {
      const link = document.createElement("a");link.id="homeMapLink";link.href="#islas";link.className="hero-visual-link";
      link.setAttribute("aria-label","Choose an island on the map or from the list");
      visual.before(link);link.append(visual);
      const caption=document.createElement("span");caption.className="hero-map-action";caption.textContent="Eight islands, eight stories. Choose where to start →";link.append(caption);
    }
    const map = byId("exploreMap");map.dataset.screen = "islas";
    const islandChooser = document.createElement("details");
    islandChooser.className = "island-list-disclosure";
    islandChooser.innerHTML = "<summary>Show all eight islands as a list</summary>";
    islandChooser.append(byId("islandGrid"));map.append(islandChooser);
    window.MitoMapaExplorer?.attachList?.(islandChooser);
    const passport = byId("passportTitle").closest("section");
    byId("passportTitle").textContent = "Passport";
    passport.querySelector(":scope > h3")?.remove();
    const games = document.createElement("section");
    games.className = "section screen-intro";games.dataset.screen = "juegos";
    games.innerHTML = `<p class="eyebrow">Keep exploring</p><h1>Games to play together</h1><p>Choose an activity. You can come back to the stories at any time.</p><div class="activity-choices"><a href="#puzle" class="activity-choice"><span class="choice-symbol" aria-hidden="true">▦</span><h2>Rebuild the map</h2><p>Put the twelve pieces of the archipelago together.</p><span class="choice-action">Open the puzzle →</span></a><a href="#comparar" class="activity-choice"><span class="choice-symbol" aria-hidden="true">↔</span><h2>Compare two stories</h2><p>Find what the stories have in common and save your ideas.</p><span class="choice-action">Choose stories →</span></a><a href="#gran-reto" class="activity-choice"><span class="choice-symbol" aria-hidden="true">✦</span><h2>Connect the eight islands</h2><p>Collect the eight pieces to unlock the final challenge.</p><span class="choice-action">View the final challenge →</span></a></div>`;
    main.append(games);
    const namesChoice = document.createElement("a");
    namesChoice.href = "#nombres-islas";namesChoice.className = "activity-choice";
    namesChoice.innerHTML = "<span class=\"choice-symbol\" aria-hidden=\"true\">⌖</span><h2>Island names</h2><p>Match historical names to their islands on a map inspired by old charts.</p><span class=\"choice-action\">Explore the names →</span>";
    games.querySelector(".activity-choices").append(namesChoice);
    const piecesChoice = document.createElement("a");
    piecesChoice.href = "#piezas-islas";piecesChoice.className = "activity-choice";
    piecesChoice.innerHTML = "<span class=\"choice-symbol\" aria-hidden=\"true\">◈</span><h2>Match the pieces to their islands</h2><p>Look at the seven vessels and the shell, then match each piece to its island.</p><span class=\"choice-action\">Match the pieces →</span>";
    games.querySelector(".activity-choices").append(piecesChoice);
    const createChoice = document.createElement("a");createChoice.href="#crear";createChoice.className="activity-choice";
    createChoice.innerHTML="<span class=\"choice-symbol\" aria-hidden=\"true\">✎</span><h2>Make something to share</h2><p>Finish your route with a story, a scene or a drawing you can explain. You can work with one or two islands.</p><span class=\"choice-action\">Plan something to share →</span>";
    games.querySelector(".activity-choices").append(createChoice);
    const extension=games.querySelector('.activity-choice[href="#gran-reto"]');
    extension.querySelector("p").textContent="Optional extension: collect all eight pieces to connect the eight stories.";
    games.querySelector(".activity-choices").append(extension);
    const purposes={"#puzle":"Find your way around","#comparar":"Connect the stories","#nombres-islas":"Explore names and sources","#piezas-islas":"Observe and remember","#crear":"Create and review","#gran-reto":"Optional activities"};
    games.querySelectorAll(".activity-choice").forEach(card=>{const label=document.createElement("span");label.className="choice-purpose";label.textContent=purposes[card.getAttribute("href")];card.prepend(label);});
    const otherGames=document.createElement("p");otherGames.className="games-context-links";
    otherGames.innerHTML="<a href=\"#pistas\">Solve five map clues</a> · <a href=\"#ordenar\">Put the events in your last story in order</a>";
    games.append(otherGames);
    const closure=window.MitoMapaLearning?.buildClosure?.();
    if (closure) {closure.dataset.screen="crear";main.append(closure);}
    const gamePanes = [[byId("missionTitle").closest("section"),"puzle"],[byId("compareStories"),"comparar"],[byId("namesMapGame"),"nombres-islas"],[byId("piecesMapGame"),"piezas-islas"],[byId("finalMission"),"gran-reto"]];
    for (const [pane, screen] of gamePanes) {
      pane.dataset.screen = screen;
      const back = document.createElement("a");back.href = "#juegos";back.className = "view-back";back.textContent = "← Back to games";pane.prepend(back);
    }
    byId("missionTitle").textContent = "Rebuild the map";
    byId("finalTitle").textContent = "Connect the eight islands";
    byId("routes").dataset.screen = "ruta";
    const resources = document.createElement("section");
    resources.className = "section screen-intro";resources.dataset.screen = "recursos";
    resources.innerHTML = "<p class=\"eyebrow\">Materials to use as you explore</p><h1>Resources and help</h1>";
    const naturalSection = byId("patrimonioNatural3d")?.closest("section");
    const resourceChoices = document.createElement("div");
    resourceChoices.className = "activity-choices resource-choices";
    resourceChoices.append(
      resourceCard(byId("reuseTitle").closest("section"), "resourceDownloads",
        "Downloads and editable materials", "Download the storybooks, editable project and classroom materials.", "↓"),
      resourceCard(byId("pintaderas3d").closest("section"), "resourcePintaderas",
        "Pintaderas in 3D", "Explore the recreated pieces and download the clay stamps.", "assets/images/pintadera_roseta.webp"),
      resourceCard(byId("vasijacanaria3d").closest("section"), "resourceVasija",
        "Canarian pottery in 3D", "Rotate the vessels in the viewer and download models for 3D printing.", "assets/images/insignia_tenerife.webp"),
      ...(naturalSection ? [resourceCard(naturalSection, "resourceNatural3d",
        "Natural heritage in 3D", "Explore the white limpet from La Graciosa and download the model.", "assets/lapa-blanca/miniatura.webp?revision=4746669da950")] : []),
      resourceCard(byId("creditsTitle").closest("section"), "resourceCredits",
        "Teacher guide, credits, sources and acknowledgements", "Find teaching guidance, credits and sources for each island.", "▤"),
      resourceCard(main.querySelector(".historical-review"), "resourceHistory",
        "History and interpretation of the illustrations", "Read how the scenes were created and what we know about the past.", "◫"),
      resourceCard(passport, "resourcePassport",
        "Passport and challenge criteria", "Review the pieces you’ve earned and the challenge criteria.", "◈"),
      resourceCard(byId("studentFeedback"), "resourceFeedback",
        "Share feedback", "Tell us how you got on with the stories and activities.", "✎")
    );
    resources.append(resourceChoices);
    main.append(resources);
    const tools = hero.querySelector(".experience-tools");
    if (tools) {
      const settings = document.createElement("details");settings.className = "reading-settings";settings.id = "readingSettings";
      settings.innerHTML = "<summary>Learning stage and reading settings</summary>";
      tools.before(settings);settings.append(tools);
      const heading=tools.querySelector("h2");if(heading)heading.classList.add("visually-hidden");
      const resume = byId("resumeRoute");resume.textContent = "Return to my last island";resume.className = "button secondary";
      byId("homeActions").append(resume);
    }
    updateResume();
    const reset = byId("resetProgress");
    reset.classList.add("teacher-reset");(byId("teacherResetSection")||byId("teacherToolsPanel")).append(reset);
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
      if (!context.routes.some(route=>route.id===routeId) || !Object.hasOwn(STEPS,step)) return;
      if (step !== "cuento") context.stopNarration();
      remember(routeId,step);
      record(`#isla/${routeId}/${step}`);
    });
    if (!go(location.hash,{history:false,focus:Boolean(location.hash)})) go("inicio",{history:false,focus:false});
  }
  function refresh() {
    updateResume();
    if (current === "ruta" && !document.querySelector(".route.active")) go(location.hash,{history:false});
  }
  window.MitoMapaNavigation = {mount,go,activateRoute,refresh,resume,resetResume,refreshResume:updateResume};
})();
