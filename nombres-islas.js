/* Práctica voluntaria de nombres: no guarda respuestas ni modifica las piezas. */
(function () {
  'use strict';

  const CAUTION = 'Las denominaciones y sus grafías no son completamente seguras: las fuentes difieren y a menudo son posteriores a la conquista. Según la información aportada por la autoría, esta selección se ha consultado con especialistas en la época prehispánica de Canarias; esa consulta no elimina las incertidumbres.';
  const GRACIOSA_NOTE = 'No se ha establecido aquí una denominación aborigen documentada. La ausencia de un poblado permanente no excluye visitas o usos ocasionales.';
  const MAP_NOTE = 'Recreación contemporánea inspirada en cartas antiguas; no es un mapa histórico.';
  const islands = [
    {id: 'el-hierro', current: 'El Hierro', name: 'Esero / Eceró', centre: [15.3, 74.8], label: [10, 88], hint: 'Busca la isla situada más al suroeste del archipiélago.'},
    {id: 'la-palma', current: 'La Palma', name: 'Benahoare', centre: [18, 41.7], label: [16, 27], hint: 'Busca la isla situada al norte de El Hierro, en el extremo occidental.'},
    {id: 'la-gomera', current: 'La Gomera', name: 'Gomara', centre: [28.1, 61], label: [27, 79], hint: 'Busca la pequeña isla casi redonda que está al oeste de Tenerife.'},
    {id: 'tenerife', current: 'Tenerife', name: 'Achinech', centre: [38.9, 54.9], label: [39, 38], hint: 'Busca la isla de forma triangular situada entre La Gomera y Gran Canaria.'},
    {id: 'gran-canaria', current: 'Gran Canaria', name: 'Canaria', centre: [53.6, 66.9], label: [56, 84], hint: 'Busca la isla casi circular situada al este de Tenerife.'},
    {id: 'fuerteventura', current: 'Fuerteventura', name: 'Erbania', centre: [76.7, 51.5], label: [77, 78], hint: 'Busca la isla alargada situada al sur de Lanzarote.'},
    {id: 'lanzarote', current: 'Lanzarote', name: 'Tyterogaka', centre: [84.3, 28.3], label: [88, 44], hint: 'Busca la isla situada al norte de Fuerteventura y al sur de La Graciosa.'},
    {id: 'la-graciosa', current: 'La Graciosa', name: 'Sin nombre documentado', centre: [85.7, 21.5], label: [90, 10], hint: 'Esta ficha expresa una falta de documentación. Busca la pequeña isla situada al norte de Lanzarote.', category: true}
  ];
  const byId = id => islands.find(island => island.id === id);
  const svgNS = 'http://www.w3.org/2000/svg';
  let section = null;
  let selected = null;
  let reference = false;
  const placed = new Set();
  const controls = {};
  const cards = new Map();
  const targets = new Map();
  let drag = null;
  let ghost = null;
  let dragOver = null;
  let dragFrame = null;
  let suppressClickUntil = 0;

  function node(tag, className, text) {
    const result = document.createElement(tag);
    if (className) result.className = className;
    if (text) result.textContent = text;
    return result;
  }

  function button(text, className, handler, id) {
    const result = node('button', className, text);
    result.type = 'button';
    if (id) result.id = id;
    result.addEventListener('click', handler);
    return result;
  }

  function svg(tag, attributes) {
    const result = document.createElementNS(svgNS, tag);
    Object.entries(attributes || {}).forEach(([key, value]) => result.setAttribute(key, value));
    return result;
  }

  function announce(message, kind) {
    controls.feedback.textContent = message;
    controls.feedback.dataset.kind = kind || 'note';
  }

  function update() {
    if (!section) return;
    section.classList.toggle('names-reference-visible', reference);
    controls.reference.textContent = reference ? 'Volver a practicar' : 'Mostrar mapa de referencia';
    controls.reference.setAttribute('aria-pressed', String(reference));
    controls.progress.textContent = reference
      ? 'Mapa de referencia: las relaciones mostradas no se cuentan como colocadas por ti.'
      : placed.size === islands.length
        ? 'Has relacionado las ocho fichas. Puedes revisar las cautelas y volver a practicar cuando quieras.'
        : placed.size + ' de 8 relaciones colocadas por ti. Puedes probar de nuevo y pedir ayuda.';
    controls.selection.textContent = reference
      ? 'Referencia visible. Pulsa «Volver a practicar» para continuar.'
      : selected
        ? 'Ficha: ' + byId(selected).name + '. Elige su isla.'
        : 'Elige una ficha y después su isla, o arrástrala a su cartela.';
    islands.forEach(island => {
      const card = cards.get(island.id);
      const target = targets.get(island.id);
      const done = placed.has(island.id);
      card.setAttribute('aria-pressed', String(selected === island.id));
      card.setAttribute('aria-disabled', String(done || reference));
      card.dataset.placed = String(done);
      card.querySelector('.names-card-state').textContent = done ? 'Colocado · ' + island.current : island.category ? 'Categoría, no un nombre antiguo' : 'Elegir o arrastrar';
      target.dataset.placed = String(done);
      target.dataset.reference = String(reference);
      target.querySelector('.names-target-answer').textContent = done || reference ? island.name : 'Coloca una ficha';
      target.querySelector('.names-target-state').textContent = reference ? 'Referencia' : done ? '✓ Relacionado' : '';
      target.setAttribute('aria-label', island.current + '. ' + (reference ? 'Referencia: ' + island.name + '.' : done ? island.name + ', ya relacionado.' : 'Colocar aquí el nombre seleccionado.'));
      const option = controls.nameSelect.querySelector('option[value="' + island.id + '"]');
      option.disabled = done;
    });
    controls.nameSelect.disabled = reference;
    controls.islandSelect.disabled = reference;
    controls.place.disabled = reference;
    controls.hint.disabled = reference;
    if (selected && !placed.has(selected)) controls.nameSelect.value = selected;
    else if (placed.has(controls.nameSelect.value)) controls.nameSelect.value = '';
  }

  function choose(id) {
    const island = byId(id);
    if (reference) {
      announce('Estás viendo el mapa de referencia. Pulsa «Volver a practicar» para colocar fichas.');
      return;
    }
    if (placed.has(id)) {
      announce(island.name + ' ya está relacionado con ' + island.current + '. Puedes elegir otra ficha.');
      return;
    }
    selected = id;
    update();
    announce('Has elegido ' + island.name + '. Selecciona su isla en el mapa o pide una pista.');
  }

  function place(id, chosenId) {
    if (reference) {
      announce('El mapa de referencia está visible. Pulsa «Volver a practicar» para continuar.');
      return;
    }
    const nameId = chosenId || selected;
    if (!nameId) {
      announce('Elige primero una ficha con un nombre. También puedes usar «Colocar sin arrastrar».');
      return;
    }
    const name = byId(nameId);
    const destination = byId(id);
    if (placed.has(nameId)) {
      announce(name.name + ' ya está relacionado con ' + name.current + '. Elige una ficha pendiente.');
      return;
    }
    if (nameId !== id) {
      announce('Esta selección no corresponde a ' + destination.current + '. Conservamos las relaciones que ya has colocado. Puedes volver a intentarlo o pedir una pista.', 'retry');
      return;
    }
    placed.add(id);
    selected = null;
    update();
    announce(name.category
      ? 'La ficha «Sin nombre documentado» corresponde aquí a La Graciosa. ' + GRACIOSA_NOTE
      : name.name + ' se relaciona aquí con ' + name.current + '. Recuerda que las denominaciones y sus grafías presentan incertidumbres.', 'success');
  }

  function clearDrag() {
    const previousDrag = drag;
    drag = null;
    if (previousDrag?.active) suppressClickUntil = performance.now() + 500;
    if (dragFrame !== null) cancelAnimationFrame(dragFrame);
    dragFrame = null;
    if (dragOver) dragOver.classList.remove('names-drag-over');
    dragOver = null;
    if (ghost) ghost.remove();
    ghost = null;
    section?.classList.remove('names-is-dragging');
    if (previousDrag) {
      previousDrag.card.classList.remove('names-card-dragging');
      if (previousDrag.card.hasPointerCapture?.(previousDrag.pointerId)) previousDrag.card.releasePointerCapture(previousDrag.pointerId);
    }
  }

  function targetAt(x, y) {
    const target = document.elementFromPoint(x, y)?.closest('[data-name-island]');
    return target && section.contains(target) ? target : null;
  }

  function markDragTarget() {
    if (!drag?.active) return;
    const target = targetAt(drag.x, drag.y);
    if (dragOver !== target) {
      dragOver?.classList.remove('names-drag-over');
      dragOver = target;
      dragOver?.classList.add('names-drag-over');
    }
  }

  function animateDrag() {
    if (!drag?.active) return;
    // The cards may begin above the map on a small screen. Keep that path usable
    // with a finger without changing the page layout or moving the islands.
    if (drag.y > window.innerHeight - 55) window.scrollBy(0, 10);
    else if (drag.y < 65) window.scrollBy(0, -10);
    const rect = controls.viewport.getBoundingClientRect();
    if (drag.y >= rect.top && drag.y <= rect.bottom) {
      const edge = Math.min(55, rect.width / 5);
      if (drag.x < rect.left + edge && drag.x >= rect.left - 10) controls.viewport.scrollLeft -= 9;
      else if (drag.x > rect.right - edge && drag.x <= rect.right + 10) controls.viewport.scrollLeft += 9;
    }
    markDragTarget();
    dragFrame = requestAnimationFrame(animateDrag);
  }

  function beginPointer(event, island, card) {
    if (event.button !== 0 || !event.isPrimary || reference || placed.has(island.id)) return;
    clearDrag();
    drag = {id: island.id, card, pointerId: event.pointerId, startX: event.clientX, startY: event.clientY, x: event.clientX, y: event.clientY, active: false};
    card.setPointerCapture(event.pointerId);
  }

  function movePointer(event) {
    if (!drag || event.pointerId !== drag.pointerId) return;
    drag.x = event.clientX;
    drag.y = event.clientY;
    if (!drag.active && Math.hypot(drag.x - drag.startX, drag.y - drag.startY) >= 8) {
      drag.active = true;
      choose(drag.id);
      ghost = node('div', 'names-drag-ghost', byId(drag.id).name);
      ghost.setAttribute('aria-hidden', 'true');
      document.body.append(ghost);
      drag.card.classList.add('names-card-dragging');
      section.classList.add('names-is-dragging');
      dragFrame = requestAnimationFrame(animateDrag);
    }
    if (!drag.active) return;
    event.preventDefault();
    ghost.style.left = drag.x + 'px';
    ghost.style.top = drag.y + 'px';
    markDragTarget();
  }

  function finishPointer(event) {
    if (!drag || event.pointerId !== drag.pointerId) return;
    const currentDrag = drag;
    const destination = currentDrag.active ? targetAt(event.clientX, event.clientY) : null;
    if (currentDrag.active) suppressClickUntil = performance.now() + 500;
    clearDrag();
    if (currentDrag.active) {
      event.preventDefault();
      currentDrag.card.focus({preventScroll: true});
      if (destination) place(destination.dataset.nameIsland, currentDrag.id);
      else announce('La ficha sigue seleccionada. Suéltala sobre una cartela del mapa, toca una isla o usa «Colocar sin arrastrar».');
    }
  }

  function reset() {
    clearDrag();
    selected = null;
    reference = false;
    placed.clear();
    if (!section) return;
    controls.nameSelect.value = '';
    controls.islandSelect.value = '';
    controls.showCurrent.checked = true;
    section.classList.remove('names-hide-current');
    update();
    announce('Mapa preparado. Elige la ficha por la que quieras empezar; no hay orden ni puntuación.');
  }

  function buildMap() {
    const figure = node('figure', 'names-map-figure');
    const viewport = node('div', 'names-map-viewport');
    viewport.id = 'namesMapViewport';
    viewport.tabIndex = 0;
    viewport.setAttribute('role', 'region');
    viewport.setAttribute('aria-label', 'Mapa de Canarias para relacionar los nombres');
    viewport.setAttribute('aria-describedby', 'namesPanHelp');
    controls.viewport = viewport;
    const board = node('div', 'names-map-board');
    board.id = 'namesMapBoard';
    const drawing = svg('svg', {id: 'namesMapImage', viewBox: '0 0 3000 1514', 'aria-hidden': 'true', focusable: 'false', preserveAspectRatio: 'xMidYMid meet'});
    const defs = svg('defs');
    const filter = svg('filter', {id: 'namesParchment', 'color-interpolation-filters': 'sRGB'});
    filter.append(svg('feColorMatrix', {type: 'matrix', values: '-.45 .15 .75 0 .30  -.45 .15 .75 0 .25  -.45 .15 .75 0 .15  0 0 0 1 0'}));
    defs.append(filter);
    drawing.append(defs, svg('image', {href: 'assets/images/mapa_canarias.webp', width: '3000', height: '1514', preserveAspectRatio: 'xMidYMid meet', filter: 'url(#namesParchment)'}));
    const rhumbs = svg('g', {class: 'names-rhumb-lines'});
    [[450, 210, 2660, 1400], [180, 1410, 2700, 100], [80, 800, 2800, 800], [1940, 120, 1940, 1430], [200, 110, 2810, 1280], [700, 1400, 2300, 110]].forEach(points => {
      rhumbs.append(svg('line', {x1: points[0], y1: points[1], x2: points[2], y2: points[3]}));
    });
    drawing.append(rhumbs);
    islands.forEach(island => {
      const [cx, cy] = [island.centre[0] * 30, island.centre[1] * 15.14];
      drawing.append(svg('line', {'data-name-leader': island.id, x1: cx, y1: cy, x2: island.label[0] * 30, y2: island.label[1] * 15.14, class: 'names-leader'}));
      drawing.append(svg('circle', {'data-name-anchor': island.id, cx, cy, r: '9', class: 'names-island-anchor'}));
    });
    board.append(drawing);
    islands.forEach(island => {
      const target = button('', 'names-map-target', () => place(island.id));
      target.dataset.nameIsland = island.id;
      target.style.setProperty('--names-x', island.label[0] + '%');
      target.style.setProperty('--names-y', island.label[1] + '%');
      target.append(node('span', 'names-target-current', island.current), node('span', 'names-target-answer', 'Coloca una ficha'), node('span', 'names-target-state'));
      targets.set(island.id, target);
      board.append(target);
    });
    viewport.append(board);
    const pan = node('div', 'names-pan-controls');
    const panBy = direction => viewport.scrollBy({left: direction * Math.max(180, viewport.clientWidth * .65), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
    const left = button('←', 'names-button names-pan-button', () => panBy(-1));
    left.setAttribute('aria-label', 'Ver la parte occidental del mapa');
    const right = button('→', 'names-button names-pan-button', () => panBy(1));
    right.setAttribute('aria-label', 'Ver la parte oriental del mapa');
    const help = node('p', 'names-pan-help', 'En pantallas pequeñas, desplaza el mapa o usa las flechas. Al arrastrar, acércate a un borde para desplazarlo.');
    help.id = 'namesPanHelp';
    pan.append(left, help, right);
    function updatePan() {
      pan.hidden = viewport.scrollWidth <= viewport.clientWidth + 2;
      left.disabled = viewport.scrollLeft < 2;
      right.disabled = viewport.scrollLeft + viewport.clientWidth >= viewport.scrollWidth - 2;
    }
    viewport.addEventListener('scroll', updatePan, {passive: true});
    viewport.addEventListener('keydown', event => {
      if (event.target !== viewport || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      if (event.key === 'Home') viewport.scrollLeft = 0;
      else if (event.key === 'End') viewport.scrollLeft = viewport.scrollWidth;
      else panBy(event.key === 'ArrowLeft' ? -1 : 1);
    });
    if (typeof ResizeObserver !== 'undefined') new ResizeObserver(updatePan).observe(viewport);
    else window.addEventListener('resize', updatePan);
    figure.append(viewport, pan, node('figcaption', 'names-map-caption', MAP_NOTE + ' Se conserva la forma y la posición de las islas del mapa base; el norte está arriba.'));
    requestAnimationFrame(updatePan);
    return figure;
  }

  function buildAlternative() {
    const details = node('details', 'names-details names-alternative');
    const summary = node('summary', '', 'Colocar sin arrastrar');
    const description = node('p', '', 'Elige un nombre y una isla actual. Este modo realiza la misma práctica que el mapa.');
    const form = node('div', 'names-place-form');
    const nameLabel = node('label');
    nameLabel.append(node('span', '', 'Nombre o categoría'));
    controls.nameSelect = node('select');
    controls.nameSelect.id = 'namesNameSelect';
    controls.nameSelect.append(new Option('Elige una ficha', ''));
    const islandLabel = node('label');
    islandLabel.append(node('span', '', 'Isla actual'));
    controls.islandSelect = node('select');
    controls.islandSelect.id = 'namesIslandSelect';
    controls.islandSelect.append(new Option('Elige una isla', ''));
    islands.forEach(island => {
      controls.nameSelect.append(new Option(island.name, island.id));
      controls.islandSelect.append(new Option(island.current, island.id));
    });
    controls.nameSelect.addEventListener('change', () => {
      if (controls.nameSelect.value) choose(controls.nameSelect.value);
      else { selected = null; update(); }
    });
    nameLabel.append(controls.nameSelect);
    islandLabel.append(controls.islandSelect);
    controls.place = button('Colocar la ficha', 'names-button', () => {
      if (!controls.nameSelect.value || !controls.islandSelect.value) {
        announce('Elige un nombre o categoría y una isla actual en los dos desplegables.');
        return;
      }
      place(controls.islandSelect.value, controls.nameSelect.value);
    }, 'namesPlaceButton');
    form.append(nameLabel, islandLabel, controls.place);
    details.append(summary, description, form);
    return details;
  }

  function mount() {
    if (section) return section;
    const main = document.getElementById('main') || document.querySelector('main');
    if (!main) return null;
    section = node('section', 'section panel names-map-game');
    section.id = 'namesMapGame';
    section.setAttribute('aria-labelledby', 'namesMapTitle');
    const kicker = node('p', 'names-kicker', 'Un archipiélago, distintas memorias');
    const title = node('h1', 'section-title', 'Los nombres de las islas');
    title.id = 'namesMapTitle';
    section.append(kicker, title, node('p', 'names-intro', 'Elige una ficha y su isla, o arrástrala a su cartela. Practica en cualquier orden, sin puntuación.'));
    const note = node('p', 'names-source-note', 'Los nombres antiguos presentan dudas y variantes. La ficha de La Graciosa indica que no se ha documentado un nombre aborigen.');
    const instructions = node('details', 'names-details names-context');
    instructions.append(node('summary', '', 'Qué sabemos de estos nombres y cómo jugar'));
    instructions.append(node('p', '', CAUTION), node('p', '', 'La Graciosa: ' + GRACIOSA_NOTE), node('p', '', 'Las siete denominaciones son la selección aportada por la autoría tras sus consultas. «Gomara» se incorpora en ese marco; el juego no afirma una etimología demostrada ni la misma certeza documental para todos los nombres.'));
    const instructionList = node('ul');
    ['Toca o pulsa una ficha y después la cartela de su isla. Con teclado, utiliza Tab para recorrerlas y Enter o Espacio para elegir y colocar.', 'También puedes arrastrar las fichas con ratón o pantalla táctil. Escape cancela la selección o el arrastre.', 'Si prefieres desplegables, abre «Colocar sin arrastrar». Las relaciones colocadas se conservan al volver a intentarlo.', 'El mapa de referencia muestra las relaciones como apoyo; no las cuenta como colocadas por ti. Nada se guarda cuando cierras o recargas la página.'].forEach(text => instructionList.append(node('li', '', text)));
    instructions.append(instructionList);
    const contextRow = node('div', 'names-context-row');
    contextRow.append(note, instructions);
    section.append(contextRow);
    const workspace = node('div', 'names-workspace');
    workspace.id = 'namesWorkspace';
    const cardPane = node('div', 'names-card-pane');
    const mapPane = node('div', 'names-map-pane');
    const bank = node('div', 'names-card-bank');
    bank.id = 'namesCardBank';
    bank.setAttribute('role', 'group');
    bank.setAttribute('aria-label', 'Fichas de nombres para colocar');
    islands.forEach(island => {
      const card = button('', 'names-name-card' + (island.category ? ' names-category-card' : ''), () => {
        if (performance.now() < suppressClickUntil) return;
        choose(island.id);
      });
      card.dataset.nameCard = island.id;
      card.append(node('strong', 'names-card-name', island.name), node('span', 'names-card-state'));
      card.addEventListener('pointerdown', event => beginPointer(event, island, card));
      card.addEventListener('lostpointercapture', event => {
        if (drag && event.pointerId === drag.pointerId) clearDrag();
      });
      cards.set(island.id, card);
      bank.append(card);
    });
    controls.selection = node('p', 'names-selection');
    controls.selection.id = 'namesSelection';
    cardPane.append(bank, controls.selection);
    const mapToolbar = node('div', 'names-map-toolbar');
    const label = node('label', 'names-current-toggle');
    controls.showCurrent = node('input');
    controls.showCurrent.type = 'checkbox';
    controls.showCurrent.id = 'namesShowCurrent';
    controls.showCurrent.checked = true;
    controls.showCurrent.addEventListener('change', () => section.classList.toggle('names-hide-current', !controls.showCurrent.checked));
    label.append(controls.showCurrent, node('span', '', 'Mostrar nombres actuales como apoyo'));
    mapToolbar.append(label);
    mapPane.append(mapToolbar, buildMap());
    workspace.append(cardPane, mapPane);
    section.append(workspace);
    const actions = node('div', 'names-actions');
    controls.hint = button('Pedir una pista', 'names-button names-button-secondary', () => {
      const island = byId(selected || controls.nameSelect.value);
      if (!island) { announce('Selecciona una ficha para recibir una pista sobre dónde colocarla.'); return; }
      announce(island.name + ': ' + island.hint, 'hint');
    }, 'namesHint');
    controls.reference = button('Mostrar mapa de referencia', 'names-button names-button-secondary', () => {
      clearDrag();
      reference = !reference;
      selected = null;
      update();
      announce(reference ? 'Se muestran todas las relaciones como referencia. Tus colocaciones se conservan y no se añaden aciertos. Pulsa «Volver a practicar» para continuar.' : 'Continúa la práctica. Hemos conservado solo las relaciones que colocaste tú.');
    }, 'namesReference');
    controls.reset = button('Reiniciar esta práctica', 'names-button names-button-secondary', reset, 'namesReset');
    actions.append(controls.hint, controls.reference, controls.reset);
    controls.feedback = node('p', 'names-feedback');
    controls.feedback.id = 'namesFeedback';
    controls.feedback.setAttribute('role', 'status');
    controls.feedback.setAttribute('aria-live', 'polite');
    controls.feedback.setAttribute('aria-atomic', 'true');
    controls.progress = node('p', 'names-progress');
    controls.progress.id = 'namesProgress';
    section.append(actions, controls.feedback, controls.progress, buildAlternative());
    section.addEventListener('keydown', event => {
      if (event.key !== 'Escape') return;
      const previous = selected;
      const wasDragging = Boolean(drag?.active);
      clearDrag();
      selected = null;
      controls.nameSelect.value = '';
      update();
      if (previous || wasDragging) {
        event.preventDefault();
        announce('Selección cancelada. Puedes elegir otra ficha.');
      }
    });
    document.addEventListener('pointermove', movePointer, {passive: false});
    document.addEventListener('pointerup', finishPointer);
    document.addEventListener('pointercancel', event => {
      if (drag && event.pointerId === drag.pointerId) clearDrag();
    });
    window.addEventListener('hashchange', clearDrag);
    document.addEventListener('visibilitychange', () => { if (document.hidden) clearDrag(); });
    window.addEventListener('blur', clearDrag);
    main.append(section);
    reset();
    return section;
  }

  window.MitoMapaNames = Object.freeze({mount, reset});
}());
