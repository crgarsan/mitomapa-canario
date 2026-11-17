/* Práctica voluntaria de nombres: no guarda respuestas ni modifica las piezas. */
(function () {
  'use strict';

  const CAUTION = "The names and their spellings are uncertain. Sources differ and many were written after the conquest. The authors report consulting specialists in the pre-Hispanic Canary Islands. Uncertainties remain.";
  const GRACIOSA_NOTE = "This selection gives no verified Indigenous name for La Graciosa. Occasional visits or uses were possible in the absence of permanent settlement.";
  const MAP_NOTE = "A modern illustration inspired by early charts. The map was created for this activity.";
  const islands = [
    {id: 'el-hierro', current: 'El Hierro', name: 'Esero / Eceró', centre: [15.3, 74.8], label: [10, 88], hint: "Look for the island furthest south-west in the archipelago."},
    {id: 'la-palma', current: 'La Palma', name: 'Benahoare', centre: [18, 41.7], label: [16, 27], hint: "Look for the western island north of El Hierro."},
    {id: 'la-gomera', current: 'La Gomera', name: 'Gomara', centre: [28.1, 61], label: [27, 79], hint: "Look for the small, nearly round island west of Tenerife."},
    {id: 'tenerife', current: 'Tenerife', name: 'Achinech', centre: [38.9, 54.9], label: [39, 38], hint: "Look for the triangular island between La Gomera and Gran Canaria."},
    {id: 'gran-canaria', current: 'Gran Canaria', name: 'Canaria', centre: [53.6, 66.9], label: [56, 84], hint: "Look for the nearly circular island east of Tenerife."},
    {id: 'fuerteventura', current: 'Fuerteventura', name: 'Erbania', centre: [76.7, 51.5], label: [77, 78], hint: "Look for the long island south of Lanzarote."},
    {id: 'lanzarote', current: 'Lanzarote', name: 'Tyterogaka', centre: [84.3, 28.3], label: [88, 44], hint: "Look for the island north of Fuerteventura and south of La Graciosa."},
    {id: 'la-graciosa', current: 'La Graciosa', name: "No documented name", centre: [85.7, 21.5], label: [90, 10], hint: "This card records a gap in the sources. Look for the small island north of Lanzarote.", category: true}
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

  function update() {
    if (!section) return;
    section.classList.toggle('names-reference-visible', reference);
    controls.reference.textContent = reference ? "Return to practice" : "Show the reference map";
    controls.reference.setAttribute('aria-pressed', String(reference));
    controls.progress.textContent = reference
      ? "Reference map. These matches are provided for guidance and leave your progress as it is."
      : placed.size === islands.length
        ? "You have matched all eight cards. Check the notes on the names and practise again whenever you like."
        : placed.size + " of 8 matches made. Try again or ask for a hint.";
    controls.selection.textContent = reference
      ? "Reference map shown. Select “Return to practice” to continue."
      : selected
        ? 'Selected card: ' + byId(selected).name + ". Choose its island."
        : "Select a card and then its island, or drag it onto the island’s label.";
    islands.forEach(island => {
      const card = cards.get(island.id);
      const target = targets.get(island.id);
      const done = placed.has(island.id);
      card.setAttribute('aria-pressed', String(selected === island.id));
      card.setAttribute('aria-disabled', String(done || reference));
      card.dataset.placed = String(done);
      card.setAttribute('aria-label', island.name + '. ' + (island.category ? "This is a category label. " : '') + (done ? "Placed on " + island.current + '.' : reference ? "Unplaced. Reference map shown." : "Unplaced."));
      card.querySelector('.names-card-state').textContent = done ? 'Matched to ' + island.current : island.category ? "Category label" : 'Select or drag';
      target.dataset.placed = String(done);
      target.dataset.reference = String(reference);
      target.querySelector('.names-target-answer').textContent = done || reference ? island.name : "Place a card";
      target.querySelector('.names-target-state').textContent = reference ? 'Reference' : done ? '✓ Matched' : '';
      target.setAttribute('aria-label', island.current + '. ' + (reference ? 'Reference: ' + island.name + '.' : done ? island.name + ", already matched." : "Empty. Place the selected name here."));
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
      announce("You are viewing the reference map. Select “Return to practice” to place cards.");
      return;
    }
    if (placed.has(id)) {
      announce(island.name + " is already matched to " + island.current + ". Choose another card.");
      return;
    }
    selected = id;
    update();
    announce("You selected " + island.name + ". Choose its island on the map or ask for a hint.");
  }

  function place(id, chosenId) {
    if (reference) {
      announce("Reference map shown. Select “Return to practice” to continue.");
      return;
    }
    const nameId = chosenId || selected;
    if (!nameId) {
      announce("Select a name card first. You can also choose “Match using lists”.");
      return;
    }
    const name = byId(nameId);
    const destination = byId(id);
    if (placed.has(nameId)) {
      announce(name.name + " is already matched to " + name.current + ". Choose an unmatched card.");
      return;
    }
    if (nameId !== id) {
      announce("This card does not match " + destination.current + ". Try again or ask for a hint. Your matches stay in place.", 'retry');
      return;
    }
    placed.add(id);
    selected = null;
    update();
    announce(name.category
      ? "The “No documented name” card matches La Graciosa in this activity. " + GRACIOSA_NOTE
      : name.name + " matches " + name.current + " in this activity. Historical names and their spellings remain uncertain.", 'success');
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
      else announce("The card is still selected. Drop it onto an island label, tap an island or choose “Match using lists”.");
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
    announce("The map is ready. Start with any card and practise at your own pace.");
  }

  function buildMap() {
    const figure = node('figure', 'names-map-figure');
    const viewport = node('div', 'names-map-viewport');
    viewport.id = 'namesMapViewport';
    viewport.tabIndex = 0;
    viewport.setAttribute('role', 'region');
    viewport.setAttribute('aria-label', "Map of the Canary Islands for matching names");
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
      target.append(node('span', 'names-target-current', island.current), node('span', 'names-target-answer', "Place a card"), node('span', 'names-target-state'));
      targets.set(island.id, target);
      board.append(target);
    });
    viewport.append(board);
    const pan = node('div', 'names-pan-controls');
    const panBy = direction => viewport.scrollBy({left: direction * Math.max(180, viewport.clientWidth * .65), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
    const left = button('←', 'names-button names-pan-button', () => panBy(-1));
    left.setAttribute('aria-label', "Show the western part of the map");
    const right = button('→', 'names-button names-pan-button', () => panBy(1));
    right.setAttribute('aria-label', "Show the eastern part of the map");
    const help = node('p', 'names-pan-help', "On a small screen, scroll the map or use the arrow buttons. When dragging, move towards an edge to scroll.");
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
    figure.append(viewport, pan, node('figcaption', 'names-map-caption', MAP_NOTE + " The illustrations retain the shapes and positions of the islands on the base map. North is at the top."));
    requestAnimationFrame(updatePan);
    return figure;
  }

  function buildAlternative() {
    const details = node('details', 'names-details names-alternative');
    details.id = 'namesAlternative';
    const summary = node('summary', '', "Match using lists");
    const description = node('p', '', "Choose a historical name and its present-day island. This gives you the same practice as the map.");
    const form = node('div', 'names-place-form');
    const nameLabel = node('label');
    nameLabel.append(node('span', '', "Name or category"));
    controls.nameSelect = node('select');
    controls.nameSelect.id = 'namesNameSelect';
    controls.nameSelect.append(new Option("Select a card", ''));
    const islandLabel = node('label');
    islandLabel.append(node('span', '', "Present-day island"));
    controls.islandSelect = node('select');
    controls.islandSelect.id = 'namesIslandSelect';
    controls.islandSelect.append(new Option("Choose an island", ''));
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
    controls.place = button("Place the card", 'names-button', () => {
      if (!controls.nameSelect.value || !controls.islandSelect.value) {
        announce("Use the two lists to choose a name or category and a present-day island.");
        return;
      }
      place(controls.islandSelect.value, controls.nameSelect.value);
    }, 'namesPlaceButton');
    form.append(nameLabel, islandLabel, controls.place);
    controls.alternativeFeedback = node('p', 'names-feedback names-alternative-feedback');
    controls.alternativeFeedback.id = 'namesAlternativeFeedback';
    controls.nameSelect.setAttribute('aria-describedby', controls.alternativeFeedback.id);
    controls.islandSelect.setAttribute('aria-describedby', controls.alternativeFeedback.id);
    details.append(summary, description, form, controls.alternativeFeedback);
    controls.withoutDrag = button("Use lists", 'names-button names-button-secondary names-alternative-access', () => {
      clearDrag();
      details.open = true;
      controls.withoutDrag.setAttribute('aria-expanded', 'true');
      (controls.nameSelect.disabled ? summary : controls.nameSelect).focus();
    }, 'namesWithoutDrag');
    controls.withoutDrag.setAttribute('aria-controls', details.id);
    controls.withoutDrag.setAttribute('aria-expanded', 'false');
    details.addEventListener('toggle', () => controls.withoutDrag.setAttribute('aria-expanded', String(details.open)));
    return details;
  }

  function mount() {
    if (section) return section;
    const main = document.getElementById('main') || document.querySelector('main');
    if (!main) return null;
    section = node('section', 'section panel names-map-game');
    section.id = 'namesMapGame';
    section.setAttribute('aria-labelledby', 'namesMapTitle');
    const kicker = node('p', 'names-kicker', "One archipelago, many memories");
    const title = node('h1', 'section-title', "Island names");
    title.id = 'namesMapTitle';
    section.append(kicker, title, node('p', 'names-intro', "Select a card and its island, or drag the card onto the island’s label. Practise in any order and at your own pace."));
    const alternative = buildAlternative();
    section.append(controls.withoutDrag, alternative);
    const note = node('p', 'names-source-note', "Historical names have variants, and evidence can be uncertain. The La Graciosa card records the lack of a documented Indigenous name.");
    const instructions = node('details', 'names-details names-context');
    instructions.append(node('summary', '', "What we know about the names and how to play"));
    instructions.append(node('p', '', CAUTION), node('p', '', 'La Graciosa: ' + GRACIOSA_NOTE), node('p', '', "The authors selected these seven names after consulting specialists. “Gomara” is part of that selection. The evidence differs from one name to another, and some origins remain uncertain."));
    const instructionList = node('ul');
    ["Tap or click a card and then its island’s label. On the keyboard, press Tab to move and Enter or Space to select and place cards.", "You can also drag cards with a mouse or touchscreen. Press Escape to cancel your selection or stop dragging.", "Choose “Match using lists” to use the drop-down menus. Your matches stay in place when you try again.", "Use the reference map for guidance. Your own matches are recorded separately for this visit. Closing or reloading the page resets the practice."].forEach(text => instructionList.append(node('li', '', text)));
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
    bank.setAttribute('aria-label', "Name cards to match");
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
    label.append(controls.showCurrent, node('span', '', "Show present-day names for help"));
    mapToolbar.append(label);
    mapPane.append(mapToolbar, buildMap());
    workspace.append(cardPane, mapPane);
    section.append(workspace);
    const actions = node('div', 'names-actions');
    controls.hint = button("Ask for a hint", 'names-button names-button-secondary', () => {
      const island = byId(selected || controls.nameSelect.value);
      if (!island) { announce("Select a card to get a hint about where it goes."); return; }
      announce(island.name + ': ' + island.hint, 'hint');
    }, 'namesHint');
    controls.reference = button("Show the reference map", 'names-button names-button-secondary', () => {
      clearDrag();
      reference = !reference;
      selected = null;
      update();
      announce(reference ? "All matches are shown for reference. Your matches stay where you placed them, and your progress stays the same. Select “Return to practice” to continue." : "Continue practising. Only the matches you made are shown.");
    }, 'namesReference');
    controls.reset = button("Reset this practice", 'names-button names-button-secondary', reset, 'namesReset');
    actions.append(controls.hint, controls.reference, controls.reset);
    controls.feedback = node('p', 'names-feedback');
    controls.feedback.id = 'namesFeedback';
    controls.feedback.setAttribute('role', 'status');
    controls.feedback.setAttribute('aria-live', 'polite');
    controls.feedback.setAttribute('aria-atomic', 'true');
    controls.progress = node('p', 'names-progress');
    controls.progress.id = 'namesProgress';
    section.append(actions, controls.feedback, controls.progress);
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
        announce("Selection cancelled. Choose another card.");
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
