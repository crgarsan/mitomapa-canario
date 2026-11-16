/* Memoria visual de las piezas: práctica opcional, sin guardado ni premios. */
(function () {
  'use strict';

  const CAUTION = "The pieces are contemporary designs. Seven vessels draw on ceramic references, and a seashell represents La Graciosa. Their shapes are artistic interpretations, and their assignment to islands is part of MitoMapa.";
  const MAP_NOTE = "A contemporary map made for the game.";
  const islands = [
    {id: 'el-hierro', current: 'El Hierro', name: "Piece 1", centre: [15.3, 74.8], label: [10, 88], description: "A rounded vessel with a short neck and two small handles.", hint: "Look for the island furthest south-west in the archipelago."},
    {id: 'la-palma', current: 'La Palma', name: "Piece 2", centre: [18, 41.7], label: [16, 27], description: "A low, rounded vessel with a wide opening and incised lines.", hint: "Look for the western island north of El Hierro."},
    {id: 'la-gomera', current: 'La Gomera', name: "Piece 3", centre: [28.1, 61], label: [27, 79], description: "A low, open bowl with an uneven rim and no handles.", hint: "Look for the small, nearly round island west of Tenerife."},
    {id: 'tenerife', current: 'Tenerife', name: "Piece 4", centre: [38.9, 54.9], label: [39, 38], description: "A tall, narrow vessel with a pointed base, a long neck and incised lines.", hint: "Look for the triangular island between La Gomera and Gran Canaria."},
    {id: 'gran-canaria', current: 'Gran Canaria', name: "Piece 5", centre: [53.6, 66.9], label: [56, 84], description: "A broad vessel with two handles and a triangle pattern.", hint: "Look for the nearly circular island east of Tenerife."},
    {id: 'fuerteventura', current: 'Fuerteventura', name: "Piece 6", centre: [76.7, 51.5], label: [77, 78], description: "A small vessel with an elongated end that forms a spout.", hint: "Look for the long island south of Lanzarote."},
    {id: 'lanzarote', current: 'Lanzarote', name: "Piece 7", centre: [84.3, 28.3], label: [88, 44], description: "A pale, wide-mouthed bowl with horizontal beige bands.", hint: "Look for the island north of Fuerteventura and south of La Graciosa."},
    {id: 'la-graciosa', current: 'La Graciosa', name: "Piece 8", centre: [85.7, 21.5], label: [90, 10], description: "A spiral seashell with a long tip and an opening on one side.", hint: "Look for the small island north of Lanzarote."}
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
  let cancelAlternativeReveal = null;

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

  function keepAlternativeFeedbackVisible() {
    cancelAlternativeReveal?.();
    if (document.activeElement !== controls.place) return;
    const details = controls.alternativeFeedback.closest('details');
    const headers = [...document.querySelectorAll('.topbar,.main-navigation')];
    let frame = null;
    let intersection = null;
    let observedTop = -1;
    let stopped = false;
    const request = () => {
      if (!stopped && frame === null) frame = requestAnimationFrame(reveal);
    };
    const resize = new ResizeObserver(request);
    const stop = () => {
      stopped = true;
      if (frame !== null) cancelAnimationFrame(frame);
      resize.disconnect();
      intersection?.disconnect();
      controls.place.removeEventListener('blur', stop);
      window.removeEventListener('resize', request);
      window.removeEventListener('blur', stop);
      ['wheel', 'touchstart', 'pointerdown'].forEach(type => window.removeEventListener(type, stop, true));
      window.removeEventListener('keydown', stopForScrollKey, true);
      if (cancelAlternativeReveal === stop) cancelAlternativeReveal = null;
    };
    function stopForScrollKey(event) {
      if (['Tab', 'Escape', 'PageUp', 'PageDown', 'Home', 'End', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) stop();
    }
    function reveal() {
      frame = null;
      if (stopped || document.activeElement !== controls.place || !details.open || !section.getClientRects().length) {
        stop();
        return;
      }
      // Run after the input event and layout. Later geometry changes are
      // observed while this action keeps focus; manual scrolling releases it.
      window.scrollTo({top: window.scrollY, left: window.scrollX, behavior: 'instant'});
      const covered = Math.max(0, ...headers
        .filter(header => ['sticky', 'fixed'].includes(getComputedStyle(header).position))
        .map(header => header.getBoundingClientRect().bottom));
      const topEdge = covered + 8;
      const bottomEdge = window.innerHeight - 8;
      const buttonBox = controls.place.getBoundingClientRect();
      const messageBox = controls.alternativeFeedback.getBoundingClientRect();
      let top = Math.min(buttonBox.top, messageBox.top);
      let bottom = Math.max(buttonBox.bottom, messageBox.bottom);
      // Very large text may exceed the available height; reveal the response
      // without creating a scroll loop trying to fit an impossible union.
      if (bottom - top > bottomEdge - topEdge) {
        top = messageBox.top;
        bottom = Math.min(messageBox.bottom, top + Math.max(0, bottomEdge - topEdge));
      }
      const adjustment = top < topEdge ? top - topEdge : bottom > bottomEdge ? bottom - bottomEdge : 0;
      if (Math.abs(adjustment) > 1) window.scrollBy({top: adjustment, behavior: 'instant'});
      if (Math.abs(observedTop - topEdge) > 1) {
        intersection?.disconnect();
        observedTop = topEdge;
        intersection = new IntersectionObserver(entries => {
          if (entries.some(entry => entry.intersectionRatio < 1)) request();
        }, {rootMargin: `-${Math.max(0, topEdge)}px 0px -8px 0px`, threshold: [0, 1]});
        intersection.observe(controls.place);
        intersection.observe(controls.alternativeFeedback);
      }
    }
    cancelAlternativeReveal = stop;
    resize.observe(details);
    headers.forEach(header => resize.observe(header));
    controls.place.addEventListener('blur', stop);
    window.addEventListener('resize', request);
    window.addEventListener('blur', stop);
    ['wheel', 'touchstart', 'pointerdown'].forEach(type => window.addEventListener(type, stop, {capture: true, passive: true}));
    window.addEventListener('keydown', stopForScrollKey, true);
    request();
  }

  function announce(message, kind) {
    controls.feedback.textContent = message;
    controls.feedback.dataset.kind = kind || 'note';
    controls.alternativeFeedback.textContent = message;
    controls.alternativeFeedback.dataset.kind = kind || 'note';
    if (document.activeElement === controls.place) keepAlternativeFeedbackVisible();
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
    controls.reference.textContent = reference ? "Return to practice" : "Show the reference map";
    controls.reference.setAttribute('aria-pressed', String(reference));
    controls.progress.textContent = reference
      ? placed.size + " of 8 matched. The reference map shows the associations for guidance."
      : placed.size === islands.length
        ? "You have matched all eight pieces. Check the reference or practise again, at your own pace and without a score."
        : placed.size + " of 8 pieces matched. Try again or ask for a hint.";
    controls.selection.textContent = reference
      ? "Reference map shown. Select “Return to practice” to continue."
      : selected ? byId(selected).name + ': ' + byId(selected).description + " Choose its island."
      : "Select a piece and then its island, or drag the piece onto the island’s label.";
    islands.forEach(island => {
      const card = cards.get(island.id), target = targets.get(island.id);
      const done = placed.has(island.id);
      card.setAttribute('aria-pressed', String(selected === island.id));
      card.setAttribute('aria-disabled', String(done || reference));
      card.dataset.placed = String(done);
      card.setAttribute('aria-label', island.name + '. ' + island.description + ' ' + (done ? "Placed on " + island.current + '.' : reference ? "Unplaced. Reference map shown." : "Unplaced."));
      card.querySelector('.pieces-card-state').textContent = done ? 'Matched to ' + island.current : 'Select or drag';
      target.dataset.placed = String(done);
      target.dataset.reference = String(reference);
      target.querySelector('.pieces-target-image').hidden = !(done || reference);
      target.querySelector('.pieces-target-answer').textContent = done || reference ? island.name : "Place a piece";
      target.querySelector('.pieces-target-state').textContent = reference ? 'Reference' : done ? '✓ Matched' : '';
      target.setAttribute('aria-label', island.current + '. ' + (reference ? 'Reference: ' + island.name + '. ' + island.description : done ? island.name + '. ' + island.description + " Already placed." : "Empty. Place the selected piece here."));
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
    if (reference) { announce("You are viewing the reference map. Select “Return to practice” to place pieces."); return; }
    if (placed.has(id)) { announce(piece.name + " is already matched to " + piece.current + ". Pick another piece."); return; }
    selected = id;
    update();
    announce("You selected " + piece.name + ". Choose its island on the map or ask for a hint.");
  }

  function place(id, chosenId) {
    if (reference) { announce("Reference map shown. Select “Return to practice” to continue."); return; }
    const pieceId = chosenId || selected;
    if (!pieceId) { announce("Select a piece first. You can also choose “Match using lists”."); return; }
    const piece = byId(pieceId), destination = byId(id);
    if (placed.has(pieceId)) { announce(piece.name + " is already matched to " + piece.current + ". Choose an unmatched piece."); return; }
    if (pieceId !== id) {
      announce("This piece does not match " + destination.current + " in MitoMapa. Try again or ask for a hint. Your matches stay in place.", 'retry');
      return;
    }
    placed.add(id);
    selected = null;
    update();
    announce(piece.name + " matches " + piece.current + " in MitoMapa. The project chose this match for the activity.", 'success');
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
      else announce("The piece is still selected. Drop it onto an island label, tap an island or choose “Match using lists”.");
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
    announce("The map is ready. Start with any piece and practise at your own pace.");
  }

  function buildMap() {
    const figure = node('figure', 'pieces-map-figure');
    const viewport = node('div', 'pieces-map-viewport');
    viewport.id = 'piecesMapViewport';
    viewport.tabIndex = 0;
    viewport.setAttribute('role', 'region');
    viewport.setAttribute('aria-label', "Map of the Canary Islands for matching pieces");
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
      target.append(node('span', 'pieces-target-current', island.current), pieceImage(island, 'pieces-target-image'), node('span', 'pieces-target-answer', "Place a piece"), node('span', 'pieces-target-state'));
      targets.set(island.id, target);
      board.append(target);
    });
    viewport.append(board);
    const pan = node('div', 'pieces-pan-controls');
    const panBy = direction => viewport.scrollBy({left: direction * Math.max(180, viewport.clientWidth * .65), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
    const left = button('←', 'pieces-button pieces-pan-button', () => panBy(-1));
    left.setAttribute('aria-label', "Show the western part of the map");
    const right = button('→', 'pieces-button pieces-pan-button', () => panBy(1));
    right.setAttribute('aria-label', "Show the eastern part of the map");
    const help = node('p', 'pieces-pan-help', "On a small screen, scroll the map or use the arrow buttons. When dragging, move towards an edge to scroll.");
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
    figure.append(viewport, pan, node('figcaption', 'pieces-map-caption', MAP_NOTE + " The illustrations retain the shapes and positions of the islands on the base map. North is at the top."));
    requestAnimationFrame(updatePan);
    return figure;
  }

  function buildAlternative() {
    const details = node('details', 'pieces-details pieces-alternative');
    details.id = 'piecesAlternative';
    const summary = node('summary', '', "Match using lists");
    const description = node('p', '', "Choose a piece by its number and description, then select its island. This gives you the same practice as the map.");
    const form = node('div', 'pieces-place-form');
    const nameLabel = node('label');
    nameLabel.append(node('span', '', "Piece and description"));
    controls.pieceSelect = node('select');
    controls.pieceSelect.id = 'piecesPieceSelect';
    controls.pieceSelect.append(new Option("Choose a piece", ''));
    const islandLabel = node('label');
    islandLabel.append(node('span', '', "Present-day island"));
    controls.islandSelect = node('select');
    controls.islandSelect.id = 'piecesIslandSelect';
    controls.islandSelect.append(new Option("Choose an island", ''));
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
    controls.place = button("Place the piece", 'pieces-button', () => {
      if (!controls.pieceSelect.value || !controls.islandSelect.value) {
        announce("Use the two lists to choose a piece and an island.");
        return;
      }
      place(controls.islandSelect.value, controls.pieceSelect.value);
    }, 'piecesPlaceButton');
    form.append(nameLabel, islandLabel, controls.place);
    controls.alternativeFeedback = node('p', 'pieces-feedback pieces-alternative-feedback');
    controls.alternativeFeedback.id = 'piecesAlternativeFeedback';
    controls.pieceSelect.setAttribute('aria-describedby', controls.alternativeFeedback.id);
    controls.islandSelect.setAttribute('aria-describedby', controls.alternativeFeedback.id);
    details.append(summary, description, form, controls.alternativeFeedback);
    controls.withoutDrag = button("Use lists", 'pieces-button pieces-button-secondary pieces-alternative-access', () => {
      clearDrag();
      details.open = true;
      controls.withoutDrag.setAttribute('aria-expanded', 'true');
      (controls.pieceSelect.disabled ? summary : controls.pieceSelect).focus();
    }, 'piecesWithoutDrag');
    controls.withoutDrag.setAttribute('aria-controls', details.id);
    controls.withoutDrag.setAttribute('aria-expanded', 'false');
    details.addEventListener('toggle', () => controls.withoutDrag.setAttribute('aria-expanded', String(details.open)));
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
    const kicker = node('p', 'pieces-kicker', 'Look closely, remember and match');
    const title = node('h1', 'section-title', "Match the pieces to their islands");
    title.id = 'piecesMapTitle';
    section.append(kicker, title, node('p', 'pieces-intro', "Match each piece to its island in MitoMapa. Tap the piece and choose its island, or drag it there. This is an unscored practice activity and passport progress is independent of it."));
    const alternative = buildAlternative();
    section.append(controls.withoutDrag, alternative);
    const note = node('p', 'pieces-source-note', CAUTION);
    const instructions = node('details', 'pieces-details pieces-context');
    instructions.append(node('summary', '', "How to play and use the reference"));
    const instructionList = node('ul');
    ["Look at each piece’s shape. If you need a reminder, use the reference map to see which islands go with which pieces.", "Tap a piece and then an island. On the keyboard, press Tab to move and Enter or Space to select and place a piece. Press Escape to cancel.", "You can also drag a piece with a mouse or touchscreen, or choose “Match using lists” and use the drop-down menus.", "Use the reference map to see MitoMapa’s matches and the clues to locate the islands. Your own matches are recorded separately for this visit. Closing or reloading the page resets the practice."].forEach(text => instructionList.append(node('li', '', text)));
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
    bank.setAttribute('aria-label', "Pieces to match to islands");
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
    controls.hint = button("Ask for a hint", 'pieces-button pieces-button-secondary', () => {
      const island = byId(selected || controls.pieceSelect.value);
      if (!island) { announce("Select a piece to get a hint about where it goes."); return; }
      announce(island.name + ': ' + island.hint, 'hint');
    }, 'piecesHint');
    controls.reference = button("Show the reference map", 'pieces-button pieces-button-secondary', () => {
      clearDrag();
      reference = !reference;
      selected = null;
      update();
      announce(reference ? "All matches are shown for reference. Your matches stay where you placed them, and your progress stays the same. Select “Return to practice” to continue." : "Continue practising. Only the matches you made are shown.");
    }, 'piecesReference');
    controls.reset = button("Reset this practice", 'pieces-button pieces-button-secondary', reset, 'piecesReset');
    actions.append(controls.hint, controls.reference, controls.reset);
    controls.feedback = node('p', 'pieces-feedback');
    controls.feedback.id = 'piecesFeedback';
    controls.feedback.setAttribute('role', 'status');
    controls.feedback.setAttribute('aria-live', 'polite');
    controls.feedback.setAttribute('aria-atomic', 'true');
    controls.progress = node('p', 'pieces-progress');
    controls.progress.id = 'piecesProgress';
    section.append(actions, controls.feedback, controls.progress);
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
        announce("Selection cancelled. Choose another piece.");
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
