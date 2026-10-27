/* Ayudas voluntarias: no cambian respuestas, piezas, revisión ni datos guardados.
 * init({openStory}) recibe openStory(routeId, {paragraphId}) para abrir el cuento
 * y enfocar el párrafo de su propia ruta. enhance(section, route) es idempotente.
 * feedback(id, 'source'|'quiz', index, correct, explanation, hint) devuelve un
 * estado breve para el feedback existente; la explicación requiere su botón.
 * buildClosure() devuelve la vista (el coordinador la inserta y navega a ella).
 * setClosureRoutes(ids) elige una o dos islas en la vista, sin persistencia.
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
    help.setAttribute("aria-label", `Ayudas para la pregunta ${index + 1}`);
    const prefix = `learning-${route.id}-${kind}-${index}`;
    const first = create("p", "learning-hint learning-hint-one", `Localicen el párrafo ${paragraph} del cuento y lean qué ocurre antes de decidir.`);
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
      revealControl("Pista 1", first),
      revealControl("Pista 2", second),
      revealControl("Ver explicación", explanation),
      button("Volver al fragmento del cuento", "text-button learning-return", () => openFragment(route.id, paragraph))
    );
    const prompt = kind === "source"
      ? "Para conversar o anotar en el cuaderno: ¿qué palabras del fragmento sostienen su respuesta? Expliquen con sus palabras por qué descartan otra opción."
      : "Para conversar o anotar en el cuaderno: ¿qué palabras del fragmento permiten aceptar o corregir la afirmación? Justifiquen su decisión y distingan el relato de un dato histórico que necesitarían contrastar.";
    help.append(create("summary", "", "Ayudas para pensar y explicar"), controls, first, second, explanation, create("p", "learning-oral-prompt", prompt));
    fieldset.append(help);
  }

  function enhanceResearch(section, id) {
    const evidence = section.querySelector("[data-research-evidence]");
    if (!evidence || section.querySelector(`#learning-source-guide-${id}`)) return;
    const guide = create("details", "learning-source-guide");
    guide.id = `learning-source-guide-${id}`;
    guide.append(create("summary", "", "Cómo contrastar una fuente"));
    const steps = create("ol");
    [
      "Identifiquen el autor o la institución, el título, la fecha si consta y el enlace o la página que consultaron.",
      "Elijan una afirmación concreta del cuento. Localicen qué dice la fuente sobre ella y con qué evidencias la sostiene.",
      "Expliquen una coincidencia o una diferencia y separen el motivo documentado de la recreación literaria del cuento.",
      "Indiquen un límite: ¿qué no permite asegurar esta fuente? Una leyenda o una imagen ilustrativa no demuestra por sí sola cómo ocurrió un hecho histórico."
    ].forEach(text => steps.append(create("li", "", text)));
    guide.append(steps, create("p", "", "Pueden comentarlo oralmente o en el cuaderno y, si quieren, resumirlo en el campo que ya tienen debajo. Su docente orienta la revisión del contraste."));
    const reminder = create("p", "learning-source-reminder", "El cuento dice… La fuente indica… Todavía no podemos asegurar… Pueden usar estas tres frases oralmente o en su nota opcional.");
    reminder.id = `learning-source-reminder-${id}`;
    const label = evidence.closest("label") || evidence;
    label.before(guide, reminder);
    const describedBy = new Set((evidence.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean));
    describedBy.add(reminder.id);
    evidence.setAttribute("aria-describedby", [...describedBy].join(" "));
    evidence.placeholder = "El cuento dice… La fuente (autor o institución, título y enlace) indica… Todavía no podemos asegurar…";
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
      ? "La respuesta coincide con el cuento. Pueden justificarla y consultar la explicación."
      : "Revisen las pistas o vuelvan al fragmento del cuento antes de intentarlo de nuevo.";
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
    practice.append(create("summary", "", "Situamos las islas con palabras · alternativa al puzle"));
    practice.append(create("p", "", "Practiquen la situación relativa de las ocho islas sin arrastrar. El norte queda arriba, el sur abajo, el este a la derecha y el oeste a la izquierda. Pueden responder oralmente antes de elegir. Es una actividad opcional, sin piezas ni puntuaciones."));
    practice.append(create("p", "learning-geography-note", "Las orientaciones son aproximadas: sirven para relacionar las islas, no representan distancias ni rutas de navegación."));
    const directions = ["norte", "noreste", "este", "sureste", "sur", "suroeste", "oeste", "noroeste"];
    const list = create("ol", "learning-geography-list");
    GEOGRAPHY.forEach(([island, reference], index) => {
      const item = create("li");
      const label = create("label", "learning-geography-row");
      label.append(create("span", "", `${island}, respecto de ${reference}, está aproximadamente al…`));
      const select = create("select");
      select.id = `learning-geography-${index}`;
      select.append(create("option", "", "Elijan una orientación"));
      select.firstChild.value = "";
      directions.forEach(direction => {
        const option = create("option", "", direction);
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
    const compare = button("Comparar con la referencia textual", "button secondary", () => {
      [...list.children].forEach((item, index) => {
        const selected = item.querySelector("select").value;
        const [island, reference, direction] = GEOGRAPHY[index];
        const result = item.querySelector(".learning-geography-feedback");
        result.textContent = !selected
          ? "Pueden elegir una orientación o consultar la referencia."
          : selected === direction
            ? `Coincide con la referencia: ${island} está aproximadamente al ${direction} de ${reference}.`
            : `Revisen la orientación: la referencia sitúa ${island} aproximadamente al ${direction} de ${reference}.`;
      });
      status.textContent = "Referencia disponible junto a cada elección. Comenten qué relación les ayudó a situar las islas.";
    });
    const reference = create("details", "learning-geography-reference");
    reference.append(create("summary", "", "Consultar la referencia de orientación"));
    const referenceList = create("ul");
    GEOGRAPHY.forEach(([island, other, direction]) => referenceList.append(create("li", "", `${island} está aproximadamente al ${direction} de ${other}.`)));
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
      const none = create("option", "", optional ? "Trabajaremos con una isla" : "Elijan una isla");
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
    closure.querySelector(".creative-route-context").textContent = selected.length ? `Su propuesta parte de ${names.join(" y ")}. Elijan un episodio${selected.length>1?" o relacionen un motivo de ambos cuentos":" de ese cuento"}; expliquen qué conservan y qué añaden.` : "Elijan la isla o las islas de su propuesta. Pueden empezar por cualquiera.";
    const note = closure.querySelector(".creative-route-note");
    note.hidden = !selected.includes("la-graciosa");
    note.textContent = "En La Graciosa, la pieza es una caracola contemporánea: no representa un hallazgo arqueológico. La ruta vincula literariamente San Borondón con estas aguas; no documenta allí un avistamiento.";
    const returns = closure.querySelector(".creative-story-returns");
    returns.replaceChildren();
    selected.forEach((id, index) => returns.append(button(`Volver al cuento de ${names[index]}`, "button secondary", () => openFragment(id, 1))));
  }

  function setClosureRoutes(ids) {
    if (!closure || !Array.isArray(ids)) return;
    const selected = [...new Set(ids.filter(safeRoute))].slice(0, 2);
    if (!selected.length) return;
    closure.querySelector("#creative-first-island").value = selected[0];
    closure.querySelector("#creative-second-island").value = selected[1] || "";
    updateClosure();
  }

  function buildClosure() {
    if (closure) return closure;
    closure = create("section", "section panel creative-closure");
    closure.id = "creativeClosure";
    closure.setAttribute("aria-labelledby", "creativeClosureTitle");
    const heading = create("h2", "section-title", "Creen y compartan un relato");
    heading.id = "creativeClosureTitle";
    closure.append(heading, create("p", "lead", "Pueden cerrar su expedición con una o dos islas, según lo acordado con su docente. No necesitan reunir las ocho piezas. Preparen una producción breve, oral, gráfica, escrita o combinada."));
    closure.append(create("p", "creative-audience", "Destinatario: otro grupo de su aula. Acuerden qué quieren que ese público comprenda sobre el cuento, su isla y la diferencia entre tradición, fuente y recreación."));
    const choices = create("div", "creative-island-choices");
    choices.append(islandSelect("Primera isla", false), islandSelect("Segunda isla (opcional)", true));
    choices.addEventListener("change", updateClosure);
    closure.append(choices, create("p", "creative-route-context"), create("p", "creative-route-note"), create("div", "creative-story-returns"));
    const project = document.querySelector(".final-project");
    if (project) closure.append(project); // Conserva el nodo y la pauta ya existente.
    const example = create("details", "creative-example");
    example.append(create("summary", "", "Un ejemplo breve y comentado"));
    example.append(create("p", "", "«Sobre Echeyde volvió una línea dorada. Dácil contó a su grupo lo que había visto». Podrían narrarlo y acompañarlo de dos viñetas con texto para que se comprenda sin sonido."));
    example.append(create("p", "", "El regreso de la luz parte del cuento de Tenerife; estas palabras de la narración son una recreación propia. Al presentarlo, citen la fuente consultada y expliquen que el episodio legendario no demuestra un hecho histórico. Pueden transformar este modelo o elegir otro formato."));
    const review = create("section", "creative-review");
    review.setAttribute("aria-labelledby", "creativeReviewTitle");
    const reviewHeading = create("h3", "", "Revisen antes de compartir");
    reviewHeading.id = "creativeReviewTitle";
    const criteria = create("ul");
    [
      "¿El público puede situar la isla y comprender el conflicto y el estribillo?",
      "¿Se distingue qué procede del cuento o de una fuente y qué han recreado? ¿Se reconocen los límites de la información?",
      "¿Se comprende sin depender solo del sonido o de la imagen? ¿Han indicado las fuentes y los créditos de los materiales utilizados?",
      "Tras escucharse o mostrar el borrador, expliquen qué funciona y qué mejorarían. Acuerden una revisión concreta con su docente o con otro grupo."
    ].forEach(text => criteria.append(create("li", "", text)));
    review.append(reviewHeading, criteria, create("p", "", "Conversen sobre estas preguntas o úsenlas en el cuaderno. La revisión es cualitativa: no genera puntos ni califica su producción. Compartan en el aula por el medio que acuerden con su docente."));
    closure.append(example, review);
    const activeId = document.querySelector(".route.active")?.id.replace(/^route-/, "");
    if (safeRoute(activeId)) setClosureRoutes([activeId]);
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
      closure.querySelectorAll(".creative-island-choices select").forEach(select=>{select.value="";});
      updateClosure();
      closure.querySelector(".creative-example").open = false;
    }
    focusTarget?.focus({ preventScroll: true });
  }

  window.MitoMapaLearning = Object.freeze({ init, enhance, feedback, buildClosure, setClosureRoutes, reset });
}());
