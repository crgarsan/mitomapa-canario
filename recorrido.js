/* Navegación por pasos: conserva los nodos y el estado de cada actividad. */
(function () {
  "use strict";

  const STEPS = Object.freeze(["cuento", "retos", "taller"]);
  const LABELS = Object.freeze({ cuento: "Cuento", retos: "Retos", taller: "Taller" });
  const ALIASES = Object.freeze({ story: "cuento", reading: "cuento", challenges: "retos", workshop: "taller" });
  const knownRoutes = new WeakMap();

  function normalizeStep(step) {
    return STEPS.includes(step) ? step : ALIASES[step] || null;
  }

  function create(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function directChild(section, selector) {
    return [...section.children].find(node => node.matches(selector)) || null;
  }

  function routeId(section, route) {
    const id = route?.id || section?.id?.replace(/^route-/, "");
    return typeof id === "string" && /^[a-z0-9-]+$/.test(id) ? id : null;
  }

  function group(node, step, fallbackId) {
    if (!node) return;
    node.dataset.routeFlowGroup = step;
    if (!node.id) node.id = fallbackId;
  }

  function makeControl(label, step, className) {
    const button = create("button", className || "route-flow-button", label);
    button.type = "button";
    button.dataset.routeFlowTarget = step;
    return button;
  }

  function quizNodes(section) {
    return {
      source: directChild(section, ".source-quiz"),
      truth: directChild(section, ".quiz:not(.source-quiz)")
    };
  }

  function truthAvailable(section) {
    const truth = quizNodes(section).truth;
    return Boolean(truth && !truth.hidden);
  }

  function stepCopy(section, step) {
    if (step === "cuento") return "Lee o escucha el cuento. Si quieres, abre el juego de ordenar la historia.";
    if (step === "retos") return truthAvailable(section) ? "Completa la comprensión y el verdadero o falso. Puedes volver al cuento cuando lo necesites." : "Responde las tres preguntas de comprensión. Puedes volver al cuento cuando lo necesites.";
    return "Realiza las tareas acordadas con tu docente y prepara tu producción.";
  }

  function makeNavigation(section, id, island) {
    let navigation = directChild(section, ".route-flow-nav");
    if (navigation) return navigation;
    navigation = create("nav", "route-flow-nav");
    navigation.setAttribute("aria-label", `Pasos de la ruta${island ? ` de ${island}` : ""}`);
    const controls = create("div", "route-flow-steps");
    STEPS.forEach((step, index) => {
      const button = makeControl(`${index + 1}. ${LABELS[step]}`, step);
      button.setAttribute("aria-describedby", `route-flow-description-${id}`);
      controls.append(button);
    });
    const description = create("p", "route-flow-description");
    description.id = `route-flow-description-${id}`;
    navigation.append(controls, description);
    const heading = directChild(section, ".route-head");
    if (heading) heading.after(navigation);
    else section.prepend(navigation);
    navigation.addEventListener("click", event => {
      const button = event.target.closest("button[data-route-flow-target]");
      if (button && navigation.contains(button)) showStep(section, button.dataset.routeFlowTarget, { focus: true, notify: true });
    });
    return navigation;
  }

  function foldSequence(section, id) {
    const sequence = section.querySelector(".story-sequence");
    if (!sequence) return;
    let disclosure = sequence.parentElement;
    if (!disclosure.matches("details.route-flow-sequence")) {
      const active = document.activeElement;
      disclosure = create("details", "route-flow-sequence");
      const summary = create("summary", "", "Ordena el cuento · juego opcional");
      sequence.before(disclosure);
      disclosure.append(summary, sequence);
      if (active && sequence.contains(active)) {
        disclosure.open = true;
        active.focus({ preventScroll: true });
      }
    }
    sequence.removeAttribute("data-route-flow-group");
    group(disclosure, "cuento", `route-flow-sequence-${id}`);
  }

  function selectQuiz(section, requested, focus) {
    const next = requested === "verdad" && truthAvailable(section) ? "verdad" : "comprension";
    section.dataset.routeFlowQuiz = next;
    const navigation = directChild(section, ".route-flow-quiz-nav");
    if (!navigation) return;
    navigation.querySelectorAll("button[data-route-flow-quiz-target]").forEach(button => {
      const selected = button.dataset.routeFlowQuizTarget === next;
      if (selected) button.setAttribute("aria-current", "step");
      else button.removeAttribute("aria-current");
      if (button.dataset.routeFlowQuizTarget === "verdad") button.hidden = !truthAvailable(section);
    });
    const nextButton = section.querySelector(".route-flow-next-quiz");
    if (nextButton) nextButton.hidden = next !== "comprension" || !truthAvailable(section);
    if (focus) {
      const button = navigation.querySelector(`[data-route-flow-quiz-target="${next}"]`);
      button?.focus({ preventScroll: true });
      navigation.scrollIntoView({ block: "start", behavior: motionPreference() });
    }
  }

  function makeQuizNavigation(section, id) {
    const nodes = quizNodes(section);
    if (!nodes.source) return;
    nodes.source.dataset.routeFlowQuizPanel = "comprension";
    if (nodes.truth) nodes.truth.dataset.routeFlowQuizPanel = "verdad";
    let navigation = directChild(section, ".route-flow-quiz-nav");
    if (!navigation) {
      navigation = create("nav", "route-flow-quiz-nav");
      navigation.setAttribute("aria-label", "Elige el reto de comprensión");
      [["Comprensión", "comprension", nodes.source], ["Verdadero o falso", "verdad", nodes.truth]].forEach(([label, target, panel]) => {
        if (!panel) return;
        const button = create("button", "route-flow-button", label);
        button.type = "button";
        button.dataset.routeFlowQuizTarget = target;
        button.setAttribute("aria-controls", panel.id);
        navigation.append(button);
      });
      nodes.source.before(navigation);
      navigation.addEventListener("click", event => {
        const button = event.target.closest("button[data-route-flow-quiz-target]");
        if (button && navigation.contains(button) && !button.hidden) selectQuiz(section, button.dataset.routeFlowQuizTarget, true);
      });
    }
    group(navigation, "retos", `route-flow-quiz-nav-${id}`);
    selectQuiz(section, section.dataset.routeFlowQuiz, false);
  }

  function makeTransitions(section, id) {
    const nodes = quizNodes(section);
    let reading = directChild(section, ".route-flow-reading-next");
    if (!reading) {
      reading = create("div", "route-flow-transition route-flow-reading-next");
      reading.append(makeControl("Ir a los retos →", "retos", "route-flow-button route-flow-primary"));
      if (nodes.source) {
        const quizNavigation = directChild(section, ".route-flow-quiz-nav");
        (quizNavigation || nodes.source).before(reading);
      } else directChild(section, ".route-nav")?.before(reading);
      reading.addEventListener("click", () => showStep(section, "retos", { focus: true, notify: true }));
    }
    group(reading, "cuento", `route-flow-reading-next-${id}`);
    let challenges = directChild(section, ".route-flow-challenges-next");
    if (!challenges) {
      challenges = create("div", "route-flow-transition route-flow-challenges-next");
      const nextQuiz = create("button", "route-flow-button route-flow-next-quiz", "Ir al verdadero o falso →");
      nextQuiz.type = "button";
      nextQuiz.addEventListener("click", () => selectQuiz(section, "verdad", true));
      const workshop = makeControl("Abrir el taller →", "taller", "route-flow-button route-flow-primary");
      workshop.addEventListener("click", () => showStep(section, "taller", { focus: true, notify: true }));
      challenges.append(nextQuiz, workshop);
      const routeNavigation = directChild(section, ".route-nav");
      if (routeNavigation) routeNavigation.before(challenges);
      else section.append(challenges);
    }
    group(challenges, "retos", `route-flow-challenges-next-${id}`);
    selectQuiz(section, section.dataset.routeFlowQuiz, false);
  }

  function markGroups(section, id) {
    group(directChild(section, ".route-grid"), "cuento", `route-flow-reading-${id}`);
    foldSequence(section, id);
    const nodes = quizNodes(section);
    group(nodes.source, "retos", `source-${id}`);
    group(nodes.truth, "retos", `quiz-${id}`);
    group(directChild(section, ".reward"), "retos", `route-flow-reward-${id}`);
    group(directChild(section, ".activity-workshop"), "taller", `activity-${id}`);
    group(directChild(section, ".level-route-note"), "taller", `route-flow-itinerary-${id}`);
    makeQuizNavigation(section, id);
    makeTransitions(section, id);
  }

  function motionPreference() {
    return window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
  }

  function synchronize(section) {
    const step = normalizeStep(section.dataset.routeFlowStep) || "cuento";
    section.dataset.routeFlowStep = step;
    const navigation = directChild(section, ".route-flow-nav");
    if (!navigation) return;
    navigation.querySelectorAll("button[data-route-flow-target]").forEach(button => {
      const target = button.dataset.routeFlowTarget;
      if (target === step) button.setAttribute("aria-current", "step");
      else button.removeAttribute("aria-current");
      const ids = [...section.children].filter(node => node.dataset.routeFlowGroup === target && node.id).map(node => node.id);
      if (ids.length) button.setAttribute("aria-controls", ids.join(" "));
      else button.removeAttribute("aria-controls");
    });
    navigation.querySelector(".route-flow-description").textContent = stepCopy(section, step);
  }

  function showStep(section, requested, options) {
    const step = normalizeStep(requested);
    if (!section || !step) return false;
    if (!knownRoutes.has(section) && !enhance(section)) return false;
    const settings = options || {};
    section.dataset.routeFlowStep = step;
    synchronize(section);
    if (settings.focus !== false) {
      const button = section.querySelector(`.route-flow-nav [data-route-flow-target="${step}"]`);
      button?.focus({ preventScroll: true });
      section.scrollIntoView({ block: "start", behavior: motionPreference() });
    }
    if (settings.notify === true) {
      document.dispatchEvent(new CustomEvent("mitomapa:route-step", { detail: { routeId: knownRoutes.get(section), step } }));
    }
    return true;
  }

  function refreshOne(section) {
    const id = knownRoutes.get(section);
    if (!id) return;
    const active = document.activeElement;
    markGroups(section, id);
    synchronize(section);
    if (!active || !section.contains(active)) return;
    const activeGroup = active.closest("[data-route-flow-group]");
    const activeQuiz = active.closest("[data-route-flow-quiz-panel]");
    const groupHidden = activeGroup && activeGroup.dataset.routeFlowGroup !== section.dataset.routeFlowStep;
    const quizHidden = activeQuiz && (activeQuiz.hidden || activeQuiz.dataset.routeFlowQuizPanel !== section.dataset.routeFlowQuiz);
    if (groupHidden || quizHidden) section.querySelector(`.route-flow-nav [data-route-flow-target="${section.dataset.routeFlowStep}"]`)?.focus({ preventScroll: true });
  }

  function refresh(section) {
    if (section) refreshOne(section);
    else document.querySelectorAll(".route.route-flow").forEach(refreshOne);
  }

  function enhance(section, route) {
    const id = routeId(section, route);
    if (!section || !id) return null;
    knownRoutes.set(section, id);
    makeNavigation(section, id, route?.island);
    section.classList.add("route-flow");
    if (!normalizeStep(section.dataset.routeFlowStep)) section.dataset.routeFlowStep = "cuento";
    refreshOne(section);
    return section;
  }

  window.MitoMapaRouteFlow = Object.freeze({ enhance, showStep, refresh });
}());
