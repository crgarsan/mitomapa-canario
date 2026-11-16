/* Ayudas voluntarias: no cambian respuestas, piezas, revisión ni datos guardados.
 * init({openStory}) recibe openStory(routeId, {paragraphId}) para abrir el cuento
 * y enfocar el párrafo de su propia ruta. enhance(section, route) es idempotente.
 * feedback(id, 'source'|'quiz', index, correct, explanation, hint) devuelve un
 * estado breve para el feedback existente; la explicación requiere su botón.
 * buildClosure() devuelve la vista (el coordinador la inserta y navega a ella).
 * setClosureRoutes(ids) elige una o dos islas en la vista, sin persistencia.
 * initializeClosureRoutes(ids) actualiza la propuesta hasta una elección explícita.
 * reset() cierra las ayudas y limpia elecciones efímeras entre estudiantes.
 */
(function () {
  "use strict";

  const ISLANDS = Object.freeze([
    ["tenerife", "Tenerife"], ["gran-canaria", "Gran Canaria"],
    ["la-palma", "La Palma"], ["la-gomera", "La Gomera"],
    ["el-hierro", "El Hierro"], ["fuerteventura", "Fuerteventura"],
    ["lanzarote", "Lanzarote"], ["la-graciosa", "La Graciosa"]
  ]);
  // Números de los siete párrafos narrativos originales; contexto, estribillo
  // y radar de fuentes quedan fuera. Se revisa cada pregunta contra su texto.
  const FRAGMENTS = Object.freeze({
    "tenerife": { source: [2, 4, 6], quiz: [2, 5, 1] },
    "gran-canaria": { source: [2, 3, 5], quiz: [1, 3, 5] },
    "la-palma": { source: [1, 4, 6], quiz: [1, 6, 4] },
    "la-gomera": { source: [2, 4, 6], quiz: [2, 6, 4] },
    "el-hierro": { source: [1, 3, 6], quiz: [1, 2, 6] },
    "fuerteventura": { source: [2, 4, 6], quiz: [1, 4, 6] },
    "lanzarote": { source: [1, 2, 5], quiz: [5, 2, 6] },
    "la-graciosa": { source: [1, 4, 6], quiz: [5, 5, 1] }
  });
  const GEOGRAPHY = Object.freeze([
    ["La Palma", "Tenerife", "noroeste"],
    ["El Hierro", "La Gomera", "suroeste"],
    ["La Gomera", "Tenerife", "oeste"],
    ["Gran Canaria", "Tenerife", "sureste"],
    ["Fuerteventura", "Gran Canaria", "noreste"],
    ["Lanzarote", "Fuerteventura", "noreste"],
    ["La Graciosa", "Lanzarote", "norte"]
  ]);
  let context = {};
  let closure = null;
  let closureExplicitChoice = false;

  function create(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function button(text, className, action) {
    const node = create("button", className || "text-button", text);
    node.type = "button";
    if (action) node.addEventListener("click", action);
    return node;
  }

  function safeRoute(id) {
    return typeof id === "string" && Object.hasOwn(FRAGMENTS, id);
  }

  function narrativeParagraphs(section) {
    const story = section.querySelector(".story");
    return story ? [...story.children].filter(node =>
      node.tagName === "P" && !node.matches(".route-meta,.story-intro")
    ) : [];
  }

  function openFragment(id, paragraph) {
    if (!safeRoute(id)) return;
    const paragraphId = `story-fragment-${id}-${paragraph}`;
    if (typeof context.openStory === "function") context.openStory(id, { paragraphId });
  }

  function revealControl(label, target) {
    const control = button(label, "text-button learning-reveal", () => {
      target.hidden = !target.hidden;
      control.setAttribute("aria-expanded", String(!target.hidden));
    });
    control.setAttribute("aria-controls", target.id);
    control.setAttribute("aria-expanded", "false");
    return control;
  }

  function enhanceQuestion(fieldset, route, kind, question, index) {
    if (fieldset.querySelector(".learning-help")) return;
    const paragraph = FRAGMENTS[route.id][kind][index];
    if (!paragraph) return;
    const help = create("details", "learning-help");
    help.dataset.learningKind = kind;
    help.dataset.learningIndex = String(index);
    help.setAttribute("aria-label", `Help with this question ${index + 1}`);
    const prefix = `learning-${route.id}-${kind}-${index}`;
    const first = create("p", "learning-hint learning-hint-one", `Find paragraph ${paragraph} and read what happens before deciding.`);
    first.id = `${prefix}-hint-one`;
    first.hidden = true;
    const second = create("p", "learning-hint learning-hint-two", kind === "source" ? question.error : question.hint);
    second.id = `${prefix}-hint-two`;
    second.hidden = true;
    const explanation = create("p", "learning-explanation", kind === "source" ? question.hit : question.feedback);
    explanation.id = `${prefix}-explanation`;
    explanation.hidden = true;
    const controls = create("div", "learning-help-controls");
    controls.append(
      revealControl("Hint 1", first),
      revealControl("Hint 2", second),
      revealControl("See the explanation", explanation),
      button("Back to the story passage", "text-button learning-return", () => openFragment(route.id, paragraph))
    );
    const prompt = kind === "source"
      ? "Discuss or write in your notebook. Which words support your answer? Explain in your own words why you ruled out another option."
      : "Discuss or write in your notebook. Which words support or correct the statement? Explain your choice and identify a historical claim you would need to check.";
    help.append(create("summary", "", "Help with thinking and explaining"), controls, first, second, explanation, create("p", "learning-oral-prompt", prompt));
    fieldset.append(help);
  }

  function enhanceResearch(section, id) {
    const evidence = section.querySelector("[data-research-evidence]");
    if (!evidence || section.querySelector(`#learning-source-guide-${id}`)) return;
    const guide = create("details", "learning-source-guide");
    guide.id = `learning-source-guide-${id}`;
    guide.append(create("summary", "", "How to check a source"));
    const steps = create("ol");
    [
      "Record the author or organisation, the title, the date if available, and the link or page you consulted.",
      "Choose a specific claim from the story. Find what the source says about it and what evidence it gives.",
      "Explain one similarity or difference. Identify which details are documented and which were written for the story.",
      "Say what this source leaves uncertain. A legend or an illustration on its own provides limited evidence about a historical event."
    ].forEach(text => steps.append(create("li", "", text)));
    guide.append(steps, create("p", "", "Discuss your findings aloud or in your notebook. You can also summarise them in the optional space below. Your teacher will guide the review."));
    const reminder = create("p", "learning-source-reminder", "The story says… The source explains… We still do not know… Use these prompts aloud or in your optional note.");
    reminder.id = `learning-source-reminder-${id}`;
    const label = evidence.closest("label") || evidence;
    label.before(guide, reminder);
    const describedBy = new Set((evidence.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean));
    describedBy.add(reminder.id);
    evidence.setAttribute("aria-describedby", [...describedBy].join(" "));
    evidence.placeholder = "The story says… The source (author or organisation, title and link) explains… We still do not know…";
  }

  function enhance(section, route) {
    if (!section || !safeRoute(route?.id)) return null;
    const paragraphs = narrativeParagraphs(section);
    // No se inventa un anclaje si cambia la estructura del cuento.
    if (paragraphs.length !== 7) return null;
    paragraphs.forEach((paragraph, index) => {
      paragraph.id = `story-fragment-${route.id}-${index + 1}`;
      paragraph.dataset.learningFragment = String(index + 1);
      paragraph.setAttribute("tabindex", "-1");
    });
    [["source", route.quick], ["quiz", route.questions]].forEach(([kind, questions]) => {
      if (!Array.isArray(questions)) return;
      const fields = section.querySelectorAll(`#${kind}-${route.id} .question`);
      questions.forEach((question, index) => {
        if (fields[index]) enhanceQuestion(fields[index], route, kind, question, index);
      });
    });
    enhanceResearch(section, route.id);
    return section;
  }

  function feedback(routeId, kind, index, correct, explanation, hint) {
    const status = correct
      ? "Your answer agrees with the story. Explain why and open the explanation to check."
      : "Read the hints or return to the passage before trying again.";
    if (!safeRoute(routeId) || !["source", "quiz"].includes(kind) || !Number.isInteger(index) || index < 0 || index > 2) return status;
    const help = document.getElementById(`${kind}-${routeId}`)?.querySelectorAll(".question")[index]?.querySelector(".learning-help");
    if (help) {
      if (typeof explanation === "string") help.querySelector(".learning-explanation").textContent = explanation;
      if (typeof hint === "string" && hint.trim()) help.querySelector(".learning-hint-two").textContent = hint;
    }
    return status;
  }

  function buildGeography() {
    const disclosure = document.getElementById("puzzleBoard")?.closest(".puzzle-disclosure");
    if (!disclosure || document.querySelector(".learning-geography")) return;
    const practice = create("details", "learning-geography");
    practice.append(create("summary", "", "Locate the islands with words · an alternative to the puzzle"));
    practice.append(create("p", "", "Practise describing where the eight islands are in relation to one another. North is up, south is down, east is right and west is left. Say your answer before choosing if you like. This is an optional, unscored activity."));
    practice.append(create("p", "learning-geography-note", "The directions are approximate. They describe where islands lie in relation to one another. Use a navigation map for distances and routes."));
    const directions = {
      norte: "north", noreste: "north-east", este: "east", sureste: "south-east",
      sur: "south", suroeste: "south-west", oeste: "west", noroeste: "north-west"
    };
    const list = create("ol", "learning-geography-list");
    GEOGRAPHY.forEach(([island, reference], index) => {
      const item = create("li");
      const label = create("label", "learning-geography-row");
      label.append(create("span", "", `${island}, in relation to ${reference}, lies roughly to the…`));
      const select = create("select");
      select.id = `learning-geography-${index}`;
      select.append(create("option", "", "Choose a direction"));
      select.firstChild.value = "";
      Object.entries(directions).forEach(([direction, name]) => {
        const option = create("option", "", name);
        option.value = direction;
        select.append(option);
      });
      label.append(select);
      const result = create("p", "learning-geography-feedback");
      result.id = `${select.id}-feedback`;
      select.setAttribute("aria-describedby", result.id);
      select.addEventListener("change", () => { result.textContent = ""; });
      item.append(label, result);
      list.append(item);
    });
    const status = create("p", "learning-geography-status");
    status.setAttribute("role", "status");
    const compare = button("Check against the written reference", "button secondary", () => {
      [...list.children].forEach((item, index) => {
        const selected = item.querySelector("select").value;
        const [island, reference, direction] = GEOGRAPHY[index];
        const result = item.querySelector(".learning-geography-feedback");
        result.textContent = !selected
          ? "Choose a direction or open the reference for help."
          : selected === direction
            ? `Matches the reference: ${island} lies roughly to the ${directions[direction]} of ${reference}.`
            : `Check again. The reference places ${island} roughly to the ${directions[direction]} of ${reference}.`;
      });
      status.textContent = "The reference is available beside each choice. Discuss which clue helped you locate the islands.";
    });
    const reference = create("details", "learning-geography-reference");
    reference.append(create("summary", "", "Open the directions reference"));
    const referenceList = create("ul");
    GEOGRAPHY.forEach(([island, other, direction]) => referenceList.append(create("li", "", `${island} lies roughly to the ${directions[direction]} of ${other}.`)));
    reference.append(referenceList);
    practice.append(list, compare, status, reference);
    disclosure.before(practice);
  }

  function islandSelect(labelText, optional) {
    const label = create("label", "creative-island-choice");
    label.append(create("span", "", labelText));
    const select = create("select");
    select.id = optional ? "creative-second-island" : "creative-first-island";
    {
      const none = create("option", "", optional ? "We will work with one island" : "Choose an island");
      none.value = "";
      select.append(none);
    }
    ISLANDS.forEach(([id, name]) => {
      const option = create("option", "", name);
      option.value = id;
      select.append(option);
    });
    label.append(select);
    return label;
  }

  function updateClosure() {
    if (!closure) return;
    const first = closure.querySelector("#creative-first-island").value;
    const second = closure.querySelector("#creative-second-island").value;
    const selected = [...new Set([first, second].filter(safeRoute))];
    const names = selected.map(id => ISLANDS.find(item => item[0] === id)[1]);
    closure.querySelector(".creative-route-context").textContent = selected.length ? `Base your work on ${names.join(" and ")}. Choose an episode${selected.length>1?" or connect an element that both stories share":" from that story"}. Explain what you keep and what you add.` : "Choose the island or islands for your work. You can start with any of them.";
    const note = closure.querySelector(".creative-route-note");
    note.hidden = !selected.includes("la-graciosa");
    note.textContent = "A modern seashell design represents La Graciosa in the passport. The story links San Borondón to these waters by setting a fictional sighting here.";
    const returns = closure.querySelector(".creative-story-returns");
    returns.replaceChildren();
    selected.forEach((id, index) => returns.append(button(`Back to the story of ${names[index]}`, "button secondary", () => openFragment(id, 1))));
  }

  function setClosureRoutes(ids, { explicit = true } = {}) {
    if (!closure || !Array.isArray(ids)) return;
    const selected = [...new Set(ids.filter(safeRoute))].slice(0, 2);
    if (!selected.length) return;
    if (explicit) closureExplicitChoice = true;
    closure.querySelector("#creative-first-island").value = selected[0];
    closure.querySelector("#creative-second-island").value = selected[1] || "";
    updateClosure();
  }

  function initializeClosureRoutes(ids) {
    if (!closureExplicitChoice) setClosureRoutes(ids, { explicit: false });
  }

  function buildClosure() {
    if (closure) return closure;
    closure = create("section", "section panel creative-closure");
    closure.id = "creativeClosure";
    closure.setAttribute("aria-labelledby", "creativeClosureTitle");
    const heading = create("h2", "section-title", "Create and share a story");
    heading.id = "creativeClosureTitle";
    closure.append(heading, create("p", "lead", "Bring your expedition to a close with one or two islands, as agreed with your teacher. Prepare something short to share. You can speak, draw, write or combine formats."));
    closure.append(create("p", "creative-audience", "Your audience is another group in your class. Agree what you want them to understand about the story, its island, the tradition, its sources and what was created for this version."));
    const choices = create("div", "creative-island-choices");
    choices.append(islandSelect("First island", false), islandSelect("Second island (optional)", true));
    choices.addEventListener("change", () => { closureExplicitChoice = true; updateClosure(); });
    closure.append(choices, create("p", "creative-route-context"), create("p", "creative-route-note"), create("div", "creative-story-returns"));
    const project = document.querySelector(".final-project");
    if (project) closure.append(project); // Conserva el nodo y la pauta ya existente.
    const example = create("details", "creative-example");
    example.append(create("summary", "", "A short example with notes"));
    example.append(create("p", "", "“A golden line appeared over Echeyde again. Dácil told her group what she had seen.” Add two pictures with captions to a spoken version so your audience can follow it with the sound off."));
    example.append(create("p", "", "The return of the light comes from the Tenerife story. The words above were written for this example. When you share it, cite the source you consulted and identify the episode as part of a legend. Adapt the example or choose a different format."));
    const review = create("section", "creative-review");
    review.setAttribute("aria-labelledby", "creativeReviewTitle");
    const reviewHeading = create("h3", "", "Review before sharing");
    reviewHeading.id = "creativeReviewTitle";
    const criteria = create("ul");
    [
      "Can your audience locate the island and understand the conflict and refrain?",
      "Can your audience tell which details come from the story or a source, and which details you created? Have you explained what remains uncertain?",
      "Can your audience follow your work using the alternatives you provide for sound or images? Have you credited the sources and materials you used?",
      "After listening to or showing the draft, explain what works and what you would improve. Agree one specific change with your teacher or another group."
    ].forEach(text => criteria.append(create("li", "", text)));
    review.append(reviewHeading, criteria, create("p", "", "Discuss these questions or use them in your notebook. The review is for feedback and carries no score or grade. Share your work in class in the format agreed with your teacher."));
    closure.append(example, review);
    const activeId = document.querySelector(".route.active")?.id.replace(/^route-/, "");
    if (safeRoute(activeId)) initializeClosureRoutes([activeId]);
    else updateClosure();
    return closure;
  }

  function init(options) {
    context = options || {};
    buildGeography();
  }

  function reset() {
    const active = document.activeElement;
    let focusTarget = null;
    document.querySelectorAll(".learning-help,.learning-source-guide,.learning-geography,.learning-geography-reference").forEach(disclosure => {
      if (!focusTarget && disclosure.contains(active)) focusTarget = disclosure.querySelector(":scope > summary");
      disclosure.open = false;
    });
    document.querySelectorAll(".learning-hint-one,.learning-hint-two,.learning-explanation").forEach(node => { node.hidden = true; });
    document.querySelectorAll(".learning-reveal").forEach(control => control.setAttribute("aria-expanded", "false"));
    document.querySelectorAll(".learning-geography select").forEach(select => { select.value = ""; });
    document.querySelectorAll(".learning-geography-feedback,.learning-geography-status").forEach(node => { node.textContent = ""; });
    if (closure) {
      closureExplicitChoice = false;
      closure.querySelectorAll(".creative-island-choices select").forEach(select=>{select.value="";});
      updateClosure();
      closure.querySelector(".creative-example").open = false;
    }
    focusTarget?.focus({ preventScroll: true });
  }

  window.MitoMapaLearning = Object.freeze({ init, enhance, feedback, buildClosure, setClosureRoutes, initializeClosureRoutes, reset });
}());
