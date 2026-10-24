/* Memoria visual de las piezas: práctica opcional, sin guardado ni premios. */
(function () {
  'use strict';

  const CAUTION = 'Las piezas son recreaciones contemporáneas: siete vasijas inspiradas en referencias cerámicas y una caracola para La Graciosa. No son réplicas arqueológicas ni acreditan su presencia histórica en cada isla.';
  const MAP_NOTE = 'Carta de juego contemporánea, no un mapa histórico.';
  const islands = [
    {id: 'el-hierro', current: 'El Hierro', name: 'Pieza 1', centre: [15.3, 74.8], label: [10, 88], description: 'Vasija redondeada de cuello corto, con dos asas laterales pequeñas.', hint: 'Busca la isla situada más al suroeste del archipiélago.'},
    {id: 'la-palma', current: 'La Palma', name: 'Pieza 2', centre: [18, 41.7], label: [16, 27], description: 'Vasija redondeada y baja, de boca ancha, decorada con líneas incisas.', hint: 'Busca la isla situada al norte de El Hierro, en el extremo occidental.'},
    {id: 'la-gomera', current: 'La Gomera', name: 'Pieza 3', centre: [28.1, 61], label: [27, 79], description: 'Cuenco bajo y abierto, de borde irregular y sin asas.', hint: 'Busca la pequeña isla casi redonda que está al oeste de Tenerife.'},
    {id: 'tenerife', current: 'Tenerife', name: 'Pieza 4', centre: [38.9, 54.9], label: [39, 38], description: 'Vasija alta y estrecha, de base apuntada, cuello largo y líneas incisas.', hint: 'Busca la isla de forma triangular situada entre La Gomera y Gran Canaria.'},
    {id: 'gran-canaria', current: 'Gran Canaria', name: 'Pieza 5', centre: [53.6, 66.9], label: [56, 84], description: 'Vasija de cuerpo ancho, dos asas y decoración de triángulos.', hint: 'Busca la isla casi circular situada al este de Tenerife.'},
    {id: 'fuerteventura', current: 'Fuerteventura', name: 'Pieza 6', centre: [76.7, 51.5], label: [77, 78], description: 'Recipiente pequeño con un extremo alargado que forma un pico.', hint: 'Busca la isla alargada situada al sur de Lanzarote.'},
    {id: 'lanzarote', current: 'Lanzarote', name: 'Pieza 7', centre: [84.3, 28.3], label: [88, 44], description: 'Cuenco claro de boca ancha, con bandas horizontales de color beige.', hint: 'Busca la isla situada al norte de Fuerteventura y al sur de La Graciosa.'},
    {id: 'la-graciosa', current: 'La Graciosa', name: 'Pieza 8', centre: [85.7, 21.5], label: [90, 10], description: 'Caracola en espiral, con punta alargada y abertura lateral.', hint: 'Busca la pequeña isla situada al norte de Lanzarote.'}
  ];
  let assetContext = {routes: [], assets: {}};
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

  function imageFor(island) {
    const route = assetContext.routes.find(item => item.id === island.id);
    const name = route?.badge || 'insignia_' + island.id.replaceAll('-', '_') + '.webp';
    return assetContext.assets[name] || 'assets/images/' + name;
  }

  function pieceImage(island, className) {
    const image = node('img', className);
    image.src = imageFor(island);
    image.alt = island.description;
    image.width = 64;
    image.height = 64;
    image.draggable = false;
    image.decoding = 'async';
    return image;
  }

  function update() {
    if (!section) return;
    section.classList.toggle('pieces-reference-visible', reference);
    controls.reference.textContent = reference ? 'Volver a practicar' : 'Mostrar mapa de referencia';
    controls.reference.setAttribute('aria-pressed', String(reference));
    controls.progress.textContent = reference
      ? placed.size + ' de 8 colocadas por ti. Mapa de referencia: las relaciones mostradas no se añaden a tu práctica.'
      : placed.size === islands.length
        ? 'Has relacionado las ocho piezas. Puedes revisar la referencia y volver a practicar, sin puntuación ni premios.'
        : placed.size + ' de 8 piezas colocadas por ti. Puedes volver a intentarlo y pedir ayuda.';
    controls.selection.textContent = reference
      ? 'Referencia visible. Pulsa «Volver a practicar» para continuar.'
      : selected ? byId(selected).name + ': ' + byId(selected).description + ' Elige su isla.'
      : 'Elige una pieza y después una isla, o arrástrala a su cartela.';
    islands.forEach(island => {
      const card = cards.get(island.id), target = targets.get(island.id);
      const done = placed.has(island.id);
      card.setAttribute('aria-pressed', String(selected === island.id));
      card.setAttribute('aria-disabled', String(done || reference));
      card.dataset.placed = String(done);
      card.querySelector('.pieces-card-state').textContent = done ? 'Colocada · ' + island.current : 'Elegir o arrastrar';
      target.dataset.placed = String(done);
      target.dataset.reference = String(reference);
      target.querySelector('.pieces-target-image').hidden = !(done || reference);
      target.querySelector('.pieces-target-answer').textContent = done || reference ? island.name : 'Coloca una pieza';
      target.querySelector('.pieces-target-state').textContent = reference ? 'Referencia' : done ? '✓ Relacionada' : '';
      target.setAttribute('aria-label', island.current + '. ' + (reference ? 'Referencia: ' + island.name + '. ' + island.description : done ? island.name + ', ya relacionada.' : 'Colocar aquí la pieza seleccionada.'));
      controls.pieceSelect.querySelector('option[value="' + island.id + '"]').disabled = done;
    });
    controls.pieceSelect.disabled = reference;
    controls.islandSelect.disabled = reference;
    controls.place.disabled = reference;
    controls.hint.disabled = reference;
    if (selected && !placed.has(selected)) controls.pieceSelect.value = selected;
    else if (placed.has(controls.pieceSelect.value)) controls.pieceSelect.value = '';
  }

  function choose(id) {
    const piece = byId(id);
    if (reference) { announce('Estás viendo la referencia. Pulsa «Volver a practicar» para colocar piezas.'); return; }
    if (placed.has(id)) { announce(piece.name + ' ya está relacionada con ' + piece.current + '. Elige otra pieza.'); return; }
    selected = id;
    update();
    announce('Has elegido ' + piece.name + '. Selecciona su isla en el mapa o pide una pista.');
  }

  function place(id, chosenId) {
    if (reference) { announce('La referencia está visible. Pulsa «Volver a practicar» para continuar.'); return; }
    const pieceId = chosenId || selected;
    if (!pieceId) { announce('Elige primero una pieza. También puedes usar «Colocar sin arrastrar».'); return; }
    const piece = byId(pieceId), destination = byId(id);
    if (placed.has(pieceId)) { announce(piece.name + ' ya está relacionada con ' + piece.current + '. Elige una pendiente.'); return; }
    if (pieceId !== id) {
      announce('Esta pieza no es la que tiene asignada ' + destination.current + ' en MitoMapa. Puedes volver a intentarlo o pedir una pista; tus colocaciones se conservan.', 'retry');
      return;
    }
    placed.add(id);
    selected = null;
    update();
    announce(piece.name + ' se relaciona en este recurso con ' + piece.current + '. Esta asociación no es una atribución arqueológica.', 'success');
  }

  function clearDrag() {
    const previousDrag = drag;
    drag = null;
    if (previousDrag?.active) suppressClickUntil = performance.now() + 500;
    if (dragFrame !== null) cancelAnimationFrame(dragFrame);
    dragFrame = null;
    if (dragOver) dragOver.classList.remove('pieces-drag-over');
    dragOver = null;
    if (ghost) ghost.remove();
    ghost = null;
    section?.classList.remove('pieces-is-dragging');
    if (previousDrag) {
      previousDrag.card.classList.remove('pieces-card-dragging');
      if (previousDrag.card.hasPointerCapture?.(previousDrag.pointerId)) previousDrag.card.releasePointerCapture(previousDrag.pointerId);
    }
  }

  function targetAt(x, y) {
    const target = document.elementFromPoint(x, y)?.closest('[data-piece-island]');
    return target && section.contains(target) ? target : null;
  }

  function markDragTarget() {
    if (!drag?.active) return;
    const target = targetAt(drag.x, drag.y);
    if (dragOver !== target) {
      dragOver?.classList.remove('pieces-drag-over');
      dragOver = target;
      dragOver?.classList.add('pieces-drag-over');
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
      ghost = node('div', 'pieces-drag-ghost');
      ghost.append(pieceImage(byId(drag.id), 'pieces-ghost-image'), node('span', '', byId(drag.id).name));
      ghost.setAttribute('aria-hidden', 'true');
      document.body.append(ghost);
      drag.card.classList.add('pieces-card-dragging');
      section.classList.add('pieces-is-dragging');
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
      if (destination) place(destination.dataset.pieceIsland, currentDrag.id);
      else announce('La pieza sigue seleccionada. Suéltala sobre una cartela del mapa, toca una isla o usa «Colocar sin arrastrar».');
    }
  }

  function reset() {
    clearDrag();
    selected = null;
    reference = false;
    placed.clear();
    if (!section) return;
    controls.pieceSelect.value = '';
    controls.islandSelect.value = '';
    update();
    announce('Mapa preparado. Elige la pieza por la que quieras empezar; no hay orden ni puntuación.');
  }

  function buildMap() {
    const figure = node('figure', 'pieces-map-figure');
    const viewport = node('div', 'pieces-map-viewport');
    viewport.id = 'piecesMapViewport';
    viewport.tabIndex = 0;
    viewport.setAttribute('role', 'region');
    viewport.setAttribute('aria-label', 'Mapa de Canarias para relacionar las piezas');
    viewport.setAttribute('aria-describedby', 'piecesPanHelp');
    controls.viewport = viewport;
    const board = node('div', 'pieces-map-board');
    board.id = 'piecesMapBoard';
    const drawing = svg('svg', {id: 'piecesMapImage', viewBox: '0 0 3000 1514', 'aria-hidden': 'true', focusable: 'false', preserveAspectRatio: 'xMidYMid meet'});
    const defs = svg('defs');
    const filter = svg('filter', {id: 'piecesParchment', 'color-interpolation-filters': 'sRGB'});
    filter.append(svg('feColorMatrix', {type: 'matrix', values: '-.45 .15 .75 0 .30  -.45 .15 .75 0 .25  -.45 .15 .75 0 .15  0 0 0 1 0'}));
    defs.append(filter);
    drawing.append(defs, svg('image', {href: 'assets/images/mapa_canarias.webp', width: '3000', height: '1514', preserveAspectRatio: 'xMidYMid meet', filter: 'url(#piecesParchment)'}));
    const rhumbs = svg('g', {class: 'pieces-rhumb-lines'});
    [[450, 210, 2660, 1400], [180, 1410, 2700, 100], [80, 800, 2800, 800], [1940, 120, 1940, 1430], [200, 110, 2810, 1280], [700, 1400, 2300, 110]].forEach(points => {
      rhumbs.append(svg('line', {x1: points[0], y1: points[1], x2: points[2], y2: points[3]}));
    });
    drawing.append(rhumbs);
    islands.forEach(island => {
      const [cx, cy] = [island.centre[0] * 30, island.centre[1] * 15.14];
      drawing.append(svg('line', {'data-piece-leader': island.id, x1: cx, y1: cy, x2: island.label[0] * 30, y2: island.label[1] * 15.14, class: 'pieces-leader'}));
      drawing.append(svg('circle', {'data-piece-anchor': island.id, cx, cy, r: '9', class: 'pieces-island-anchor'}));
    });
    board.append(drawing);
    islands.forEach(island => {
      const target = button('', 'pieces-map-target', () => place(island.id));
      target.dataset.pieceIsland = island.id;
      target.style.setProperty('--pieces-x', island.label[0] + '%');
      target.style.setProperty('--pieces-y', island.label[1] + '%');
      target.append(node('span', 'pieces-target-current', island.current), pieceImage(island, 'pieces-target-image'), node('span', 'pieces-target-answer', 'Coloca una pieza'), node('span', 'pieces-target-state'));
      targets.set(island.id, target);
      board.append(target);
    });
    viewport.append(board);
    const pan = node('div', 'pieces-pan-controls');
    const panBy = direction => viewport.scrollBy({left: direction * Math.max(180, viewport.clientWidth * .65), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
    const left = button('←', 'pieces-button pieces-pan-button', () => panBy(-1));
    left.setAttribute('aria-label', 'Ver la parte occidental del mapa');
    const right = button('→', 'pieces-button pieces-pan-button', () => panBy(1));
    right.setAttribute('aria-label', 'Ver la parte oriental del mapa');
    const help = node('p', 'pieces-pan-help', 'En pantallas pequeñas, desplaza el mapa o usa las flechas. Al arrastrar, acércate a un borde para desplazarlo.');
    help.id = 'piecesPanHelp';
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
    figure.append(viewport, pan, node('figcaption', 'pieces-map-caption', MAP_NOTE + ' Se conserva la forma y la posición de las islas del mapa base; el norte está arriba.'));
    requestAnimationFrame(updatePan);
    return figure;
  }

  function buildAlternative() {
    const details = node('details', 'pieces-details pieces-alternative');
    const summary = node('summary', '', 'Colocar sin arrastrar');
    const description = node('p', '', 'Elige una pieza por su número y descripción, y una isla. Este modo realiza la misma práctica que el mapa.');
    const form = node('div', 'pieces-place-form');
    const nameLabel = node('label');
    nameLabel.append(node('span', '', 'Pieza y descripción'));
    controls.pieceSelect = node('select');
    controls.pieceSelect.id = 'piecesPieceSelect';
    controls.pieceSelect.append(new Option('Elige una pieza', ''));
    const islandLabel = node('label');
    islandLabel.append(node('span', '', 'Isla actual'));
    controls.islandSelect = node('select');
    controls.islandSelect.id = 'piecesIslandSelect';
    controls.islandSelect.append(new Option('Elige una isla', ''));
    islands.forEach(island => {
      controls.pieceSelect.append(new Option(island.name + ' · ' + island.description, island.id));
      controls.islandSelect.append(new Option(island.current, island.id));
    });
    controls.pieceSelect.addEventListener('change', () => {
      if (controls.pieceSelect.value) choose(controls.pieceSelect.value);
      else { selected = null; update(); }
    });
    nameLabel.append(controls.pieceSelect);
    islandLabel.append(controls.islandSelect);
    controls.place = button('Colocar la pieza', 'pieces-button', () => {
      if (!controls.pieceSelect.value || !controls.islandSelect.value) {
        announce('Elige una pieza y una isla en los dos desplegables.');
        return;
      }
      place(controls.islandSelect.value, controls.pieceSelect.value);
    }, 'piecesPlaceButton');
    form.append(nameLabel, islandLabel, controls.place);
    details.append(summary, description, form);
    return details;
  }

  function mount(options = {}) {
    if (section) return section;
    assetContext = {routes: options.routes || [], assets: options.assets || {}};
    const main = document.getElementById('main') || document.querySelector('main');
    if (!main) return null;
    section = node('section', 'section panel pieces-map-game');
    section.id = 'piecesMapGame';
    section.setAttribute('aria-labelledby', 'piecesMapTitle');
    const kicker = node('p', 'pieces-kicker', 'Observa, recuerda y relaciona');
    const title = node('h1', 'section-title', 'Las piezas y sus islas');
    title.id = 'piecesMapTitle';
    section.append(kicker, title, node('p', 'pieces-intro', 'Relaciona cada pieza con la isla que tiene asignada en MitoMapa. Tócala y elige su isla, o arrástrala. Sin puntuación, premios ni cambios en tu pasaporte.'));
    const note = node('p', 'pieces-source-note', CAUTION);
    const instructions = node('details', 'pieces-details pieces-context');
    instructions.append(node('summary', '', 'Cómo jugar y qué muestra la referencia'));
    const instructionList = node('ul');
    ['Observa la forma de cada pieza. Las tarjetas no indican su isla antes de colocarlas; puedes consultar el mapa de referencia para recordarlas.', 'Toca una pieza y después una isla. Con teclado, utiliza Tab y Enter o Espacio; Escape cancela la selección o el arrastre.', 'También puedes arrastrar con ratón o pantalla táctil, o abrir «Colocar sin arrastrar» y usar los desplegables.', 'La referencia muestra las asociaciones del recurso y no las cuenta como colocadas por ti. Las pistas ayudan a situar las islas. No se guarda la práctica al cerrar o recargar.'].forEach(text => instructionList.append(node('li', '', text)));
    instructions.append(instructionList);
    const contextRow = node('div', 'pieces-context-row');
    contextRow.append(note, instructions);
    section.append(contextRow);
    const workspace = node('div', 'pieces-workspace');
    workspace.id = 'piecesWorkspace';
    const cardPane = node('div', 'pieces-card-pane');
    const mapPane = node('div', 'pieces-map-pane');
    const bank = node('div', 'pieces-card-bank');
    bank.id = 'piecesCardBank';
    bank.setAttribute('role', 'group');
    bank.setAttribute('aria-label', 'Piezas para relacionar con las islas');
    const shuffled = [...islands];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    shuffled.forEach(island => {
      const card = button('', 'pieces-piece-card', () => {
        if (performance.now() < suppressClickUntil) return;
        choose(island.id);
      });
      card.dataset.pieceCard = island.id;
      card.append(pieceImage(island, 'pieces-card-image'), node('strong', 'pieces-card-name', island.name), node('span', 'pieces-card-state'));
      card.addEventListener('pointerdown', event => beginPointer(event, island, card));
      card.addEventListener('lostpointercapture', event => {
        if (drag && event.pointerId === drag.pointerId) clearDrag();
      });
      cards.set(island.id, card);
      bank.append(card);
    });
    controls.selection = node('p', 'pieces-selection');
    controls.selection.id = 'piecesSelection';
    cardPane.append(bank, controls.selection);
    mapPane.append(buildMap());
    workspace.append(cardPane, mapPane);
    section.append(workspace);
    const actions = node('div', 'pieces-actions');
    controls.hint = button('Pedir una pista', 'pieces-button pieces-button-secondary', () => {
      const island = byId(selected || controls.pieceSelect.value);
      if (!island) { announce('Selecciona una pieza para recibir una pista sobre dónde colocarla.'); return; }
      announce(island.name + ': ' + island.hint, 'hint');
    }, 'piecesHint');
    controls.reference = button('Mostrar mapa de referencia', 'pieces-button pieces-button-secondary', () => {
      clearDrag();
      reference = !reference;
      selected = null;
      update();
      announce(reference ? 'Se muestran todas las relaciones como referencia. Tus colocaciones se conservan y no se añaden aciertos. Pulsa «Volver a practicar» para continuar.' : 'Continúa la práctica. Hemos conservado solo las relaciones que colocaste tú.');
    }, 'piecesReference');
    controls.reset = button('Reiniciar esta práctica', 'pieces-button pieces-button-secondary', reset, 'piecesReset');
    actions.append(controls.hint, controls.reference, controls.reset);
    controls.feedback = node('p', 'pieces-feedback');
    controls.feedback.id = 'piecesFeedback';
    controls.feedback.setAttribute('role', 'status');
    controls.feedback.setAttribute('aria-live', 'polite');
    controls.feedback.setAttribute('aria-atomic', 'true');
    controls.progress = node('p', 'pieces-progress');
    controls.progress.id = 'piecesProgress';
    section.append(actions, controls.feedback, controls.progress, buildAlternative());
    section.addEventListener('keydown', event => {
      if (event.key !== 'Escape') return;
      const previous = selected;
      const wasDragging = Boolean(drag?.active);
      clearDrag();
      selected = null;
      controls.pieceSelect.value = '';
      update();
      if (previous || wasDragging) {
        event.preventDefault();
        announce('Selección cancelada. Puedes elegir otra pieza.');
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

  window.MitoMapaPieces = Object.freeze({mount, reset, cancelDrag: clearDrag});
}());
