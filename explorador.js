/* Exploración y pistas: una actividad voluntaria que no modifica las piezas. */
(function () {
  'use strict';

  const positions = {
    tenerife: [38.32, 43.5], 'gran-canaria': [53.59, 58], 'la-palma': [18.10, 34.5],
    'la-gomera': [26.5, 55.5], 'el-hierro': [12.4, 69.5],
    fuerteventura: [89.5, 65], lanzarote: [93, 44], 'la-graciosa': [92.5, 23]
  };
  const clues = [
    { id: 'tenerife', text: 'Busco el cuento en el que Magec regresa y una línea dorada ilumina Echeyde. ¿Qué isla debo elegir?', help: 'Dácil cuida cabras cerca del gran volcán de esta isla.', explanation: 'En «Dácil y el regreso de Magec», la comunidad pide ayuda a Achamán para que vuelva la luz.' },
    { id: 'gran-canaria', text: 'Una criatura llamada tibicena aparece entre las tabaibas del barranco. Los pastores permanecen juntos. ¿En qué isla ocurre este cuento?', help: 'La protagonista de esta ruta es Guayarmina.', explanation: 'Guayarmina y los pastores se protegen juntos y levantan las teas en el cuento de Gran Canaria.' },
    { id: 'la-palma', text: 'Acerina escucha una historia sobre Idafe, un roque que parece sostener el cielo. ¿Qué isla guarda esta ruta?', help: 'El relato presenta esta isla con el nombre de Benahoare.', explanation: 'La ruta de La Palma sitúa a Acerina en la Caldera de Taburiente, junto al roque de Idafe.' },
    { id: 'la-gomera', text: 'Gara y Jonay protagonizan una leyenda que invita a escuchar y dialogar. ¿Dónde transcurre su encuentro?', help: 'Jonay llega desde Tenerife a otra isla; buscamos la isla de Gara.', explanation: 'El encuentro ocurre en La Gomera. El cuento invita a reflexionar sobre el dolor que causa la falta de diálogo.' },
    { id: 'el-hierro', text: 'Agarfa recoge gotas de agua del Garoé. La niebla queda en sus ramas y alimenta las piletas. ¿Qué isla es?', help: 'Buscamos la isla situada más al suroeste del mapa.', explanation: 'En el cuento de El Hierro, el Garoé recoge agua de la niebla y su memoria continúa en los relatos.' },
    { id: 'fuerteventura', text: 'La luz de Mafasca sigue a dos pastores. Al amanecer, ellos reparan la cruz que habían roto. ¿En qué isla está este cuento?', help: 'Es la isla alargada que se encuentra al sur de Lanzarote.', explanation: 'La ruta de Fuerteventura recrea la leyenda de la luz de Mafasca y una promesa de reparación.' },
    { id: 'lanzarote', text: 'Una anciana entrega una esponja mojada a Ico, que cuestiona una prueba injusta. ¿Qué isla debo abrir?', help: 'Esta isla volcánica está junto a La Graciosa.', explanation: 'El cuento de Lanzarote presenta la ayuda a Ico y su rechazo a una prueba que pone a una persona en peligro.' },
    { id: 'la-graciosa', text: 'Guadarfía y el capitán ven una isla entre la bruma: San Borondón. ¿A qué ruta del recurso pertenece esta historia?', help: 'El recurso invita a leer esta leyenda desde la más pequeña de sus ocho islas. San Borondón es una isla legendaria distinta.', explanation: 'Esta historia se lee en la ruta de La Graciosa. San Borondón es una isla legendaria; no es otro nombre de La Graciosa.' }
  ];
  const invitations = {
    tenerife: '¿Cómo vuelve la luz a Echeyde?',
    'gran-canaria': '¿Por qué se mantienen juntos los pastores?',
    'la-palma': '¿Cómo conserva Acerina la memoria de Idafe?',
    'la-gomera': '¿Qué ocurre cuando dejamos de escuchar?',
    'el-hierro': '¿Cómo recoge el Garoé el agua de la niebla?',
    fuerteventura: '¿Cómo pueden reparar los pastores lo que han hecho?',
    lanzarote: '¿Por qué cuestiona Ico una prueba injusta?',
    'la-graciosa': '¿Qué hay entre lo que ven y lo que imaginan?'
  };
  let context = null;
  let section = null;
  let list = null;
  let viewMode = 'map';
  let zoomed = false;
  let expedition = [];
  let clueIndex = 0;
  let playing = false;
  let complete = false;
  let solved = false;
  let lastMessage = '';
  let hintVisible = false;
  let controls = {};

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function button(text, className, handler) {
    const node = element('button', className, text);
    node.type = 'button';
    node.addEventListener('click', handler);
    return node;
  }

  function announce(message, kind) {
    controls.feedback.textContent = message;
    controls.feedback.dataset.kind = kind || 'note';
  }

  function openStory(id) {
    if (context && typeof context.openRoute === 'function') context.openRoute(id, {step: 'cuento'});
  }

  function updatePinLabel(pin) {
    const action = playing && !complete ? 'responder a la pista con esta isla' : 'abrir su cuento';
    const state = pin.classList.contains('explore-pin-earned') ? 'conseguida en la etapa seleccionada' : 'por conseguir en la etapa seleccionada';
    pin.setAttribute('aria-label', pin.dataset.island + ': ' + action + '. ' + pin.dataset.badgeName + ', ' + state + '.');
  }

  function refreshList() {
    if (!list || !context) return;
    const answering = playing && !complete;
    list.querySelectorAll('#islandGrid [data-route]').forEach(card => {
      const route = context.routes.find(item => item.id === card.dataset.route);
      if (!route) return;
      if (!card.querySelector('.explore-card-question')) {
        card.querySelector('.card-action').before(element('span', 'explore-card-question', invitations[route.id]));
      }
      const action = answering ? 'Responder a la pista' : 'Abrir cuento';
      card.setAttribute('aria-label', route.island + ': ' + route.title + '. ' + invitations[route.id] + ' ' + action + '.');
      card.setAttribute('aria-describedby', 'exploreMapInstruction');
      card.querySelector('.card-action').textContent = action + ' →';
      card.classList.toggle('explore-card-found', answering && solved && card.dataset.route === expedition[clueIndex].id);
    });
  }

  function renderView() {
    if (!section) return;
    const showList = viewMode === 'list' && Boolean(list);
    controls.mapView.setAttribute('aria-pressed', String(!showList));
    controls.listView.setAttribute('aria-pressed', String(showList));
    controls.mapPanel.hidden = showList;
    if (list) list.hidden = !showList;
    requestAnimationFrame(controls.refreshPan);
  }

  function setView(name) {
    viewMode = name;
    renderView();
  }

  function attachList(detailsElement) {
    if (!section || !detailsElement || detailsElement.tagName !== 'DETAILS' || !detailsElement.querySelector('#islandGrid')) return;
    if (list === detailsElement) return;
    list = detailsElement;
    list.id = list.id || 'exploreListPanel';
    list.classList.add('explore-list-panel');
    list.setAttribute('aria-label', 'Ocho rutas insulares en lista');
    list.open = true;
    const summary = list.querySelector(':scope > summary');
    if (summary) summary.hidden = true;
    // The existing card listeners still open stories in free exploration.
    // Capture answers only while playing, before those navigation listeners run.
    list.addEventListener('click', event => {
      const card = event.target.closest('#islandGrid [data-route]');
      if (!card || !playing || complete) return;
      const route = context.routes.find(item => item.id === card.dataset.route);
      if (!route) return;
      event.preventDefault();
      event.stopPropagation();
      chooseIsland(route);
    }, true);
    controls.mapPanel.after(list);
    controls.listView.disabled = false;
    controls.listView.setAttribute('aria-controls', list.id);
    viewMode = window.matchMedia('(max-width: 760px)').matches ? 'list' : 'map';
    refreshList();
    renderView();
  }

  function chooseIsland(route) {
    if (!playing || complete) {
      openStory(route.id);
      return;
    }
    const clue = expedition[clueIndex];
    if (route.id === clue.id) {
      solved = true;
      lastMessage = '¡La han encontrado! ' + clue.explanation;
      announce(lastMessage, 'success');
    } else {
      lastMessage = 'Han elegido ' + route.island + '. Esta pista corresponde a otra ruta. Pueden intentarlo de nuevo, pedir apoyo o leer el cuento.';
      announce(lastMessage, 'retry');
    }
    controls.next.hidden = false;
    controls.read.hidden = false;
    controls.pins.forEach(pin => pin.classList.toggle('explore-pin-found', solved && pin.dataset.route === clue.id));
    refreshList();
    controls.gameNote.textContent = 'Son pistas de las recreaciones literarias del recurso. Pueden volver a intentarlo o pasar a la siguiente sin penalización.';
  }

  function startGame() {
    const available = clues.filter(clue => context.routes.some(route => route.id === clue.id));
    for (let i = available.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [available[i], available[j]] = [available[j], available[i]];
    }
    expedition = available.slice(0, 5);
    clueIndex = 0;
    complete = false;
    playing = true;
    solved = false;
    lastMessage = '';
    hintVisible = false;
    renderMode();
    controls.clue.focus();
  }

  function resumeGame() {
    playing = true;
    renderMode();
    controls.clue.focus();
  }

  function leaveGame() {
    playing = false;
    renderMode();
    controls.resume.hidden ? controls.start.focus() : controls.resume.focus();
  }

  function nextClue() {
    if (clueIndex + 1 >= expedition.length) {
      complete = true;
      renderMode();
      controls.clue.focus();
      return;
    }
    clueIndex += 1;
    solved = false;
    lastMessage = '';
    hintVisible = false;
    renderMode();
    controls.clue.focus();
  }

  function renderMode() {
    if (!section) return;
    section.dataset.mode = playing ? 'game' : 'free';
    controls.start.hidden = playing;
    controls.resume.hidden = playing || expedition.length === 0 || complete;
    controls.leave.hidden = !playing;
    controls.game.hidden = !playing;
    controls.mapInstruction.textContent = playing && !complete
      ? 'Elijan la isla que responde a la pista, en el mapa o en la lista. Con el teclado, usen Tab para recorrer las islas y Enter para elegir.'
      : 'Empiecen por la isla que quieran. Elijan una pieza o una tarjeta para abrir su cuento. Con el teclado, usen Tab para recorrer las islas y Enter para abrir.';
    controls.pins.forEach(pin => {
      pin.classList.remove('explore-pin-found');
      pin.setAttribute('aria-describedby', 'exploreMapInstruction');
      updatePinLabel(pin);
    });
    refreshList();
    if (!playing) return;
    controls.restart.hidden = !complete;
    controls.hintButton.hidden = complete;
    controls.read.hidden = complete;
    controls.next.hidden = complete;
    controls.hint.hidden = complete || !hintVisible;
    if (complete) {
      controls.counter.textContent = 'Expedición de ' + expedition.length + ' pistas completada';
      controls.clue.textContent = 'Han recorrido las cinco pistas. ¿Quieren descubrir otros cuentos?';
      controls.gameNote.textContent = 'Pueden comenzar otra expedición o volver a explorar el mapa. Este juego no cambia su pasaporte ni concede piezas.';
      announce('Expedición terminada. Las ocho rutas siguen abiertas para que lean, relean y comparen sus historias.', 'success');
      return;
    }
    const clue = expedition[clueIndex];
    controls.counter.textContent = 'Pista ' + (clueIndex + 1) + ' de ' + expedition.length;
    controls.clue.textContent = clue.text;
    controls.hint.textContent = clue.help;
    controls.gameNote.textContent = 'Estas pistas se basan en las recreaciones literarias del recurso. San Borondón es una isla legendaria y su cuento se lee en la ruta de La Graciosa.';
    controls.next.textContent = clueIndex + 1 === expedition.length ? 'Terminar expedición' : 'Siguiente pista';
    controls.hintButton.setAttribute('aria-expanded', String(hintVisible));
    announce(lastMessage || 'Elijan una isla. Pueden pedir apoyo, leer el cuento o pasar una pista; tienen todos los intentos que necesiten.', solved ? 'success' : 'note');
    controls.pins.forEach(pin => pin.classList.toggle('explore-pin-found', solved && pin.dataset.route === clue.id));
  }

  function refresh() {
    if (!section || !context) return;
    let earnedCount = 0;
    controls.pins.forEach(pin => {
      const route = context.routes.find(item => item.id === pin.dataset.route);
      const earned = typeof context.isEarned === 'function' && context.isEarned(route.id);
      if (earned) earnedCount += 1;
      pin.classList.toggle('explore-pin-earned', Boolean(earned));
      pin.querySelector('.explore-pin-state-value').textContent = earned ? 'Conseguida' : 'Por conseguir';
      updatePinLabel(pin);
    });
    controls.progress.textContent = 'En la etapa seleccionada: ' + earnedCount + ' de ' + controls.pins.length + ' piezas conseguidas. Las pistas son una actividad libre y no modifican ese progreso.';
    refreshList();
  }

  function reset() {
    expedition = [];
    clueIndex = 0;
    playing = false;
    complete = false;
    solved = false;
    lastMessage = '';
    hintVisible = false;
    if (section) {
      renderMode();
      refresh();
    }
  }

  function init(nextContext) {
    if (!nextContext || !Array.isArray(nextContext.routes)) return;
    context = nextContext;
    if (section && section.isConnected) {
      refresh();
      return;
    }
    const mission = document.getElementById('missionTitle');
    const anchor = mission && mission.closest('section');
    if (!anchor || !anchor.parentNode) return;
    section = element('section', 'section panel map-explorer');
    section.id = 'exploreMap';
    section.setAttribute('aria-labelledby', 'exploreMapTitle');
    const intro = element('div', 'explore-intro');
    intro.appendChild(element('p', 'explore-kicker', 'El archipiélago, a su ritmo'));
    const title = element('h2', 'section-title', 'Elijan una isla');
    title.id = 'exploreMapTitle';
    intro.appendChild(title);
    intro.appendChild(element('p', 'explore-description', 'Ocho islas, ocho historias. Elijan la que despierte su curiosidad: todas las rutas están abiertas.'));
    section.appendChild(intro);
    const viewSwitch = element('div', 'explore-view-switch');
    viewSwitch.setAttribute('role', 'group');
    viewSwitch.setAttribute('aria-label', 'Cómo elegir una isla');
    controls.mapView = button('Mapa', 'explore-button explore-button-secondary', () => setView('map'));
    controls.mapView.setAttribute('aria-controls', 'exploreMapPanel');
    controls.listView = button('Lista', 'explore-button explore-button-secondary', () => setView('list'));
    controls.listView.disabled = true;
    viewSwitch.append(controls.mapView, controls.listView);
    section.appendChild(viewSwitch);
    const toolbar = element('div', 'explore-actions');
    controls.start = button('Jugar con cinco pistas', 'explore-button', startGame);
    controls.resume = button('Retomar mis pistas', 'explore-button explore-button-secondary', resumeGame);
    controls.leave = button('Volver a explorar libremente', 'explore-button explore-button-secondary', leaveGame);
    toolbar.append(controls.start, controls.resume, controls.leave);
    section.appendChild(toolbar);

    controls.game = element('div', 'explore-game');
    controls.game.setAttribute('aria-labelledby', 'exploreClue');
    controls.counter = element('p', 'explore-counter');
    controls.clue = element('h3', 'explore-clue');
    controls.clue.id = 'exploreClue';
    controls.clue.tabIndex = -1;
    controls.gameNote = element('p', 'explore-game-note');
    const gameActions = element('div', 'explore-actions');
    controls.hintButton = button('Dame una pista de apoyo', 'explore-button explore-button-secondary', () => {
      hintVisible = !hintVisible;
      controls.hint.hidden = !hintVisible;
      controls.hintButton.setAttribute('aria-expanded', String(hintVisible));
    });
    controls.hintButton.setAttribute('aria-controls', 'exploreHint');
    controls.read = button('Leer el cuento de esta pista', 'explore-button explore-button-secondary', () => openStory(expedition[clueIndex].id));
    controls.next = button('Siguiente pista', 'explore-button', nextClue);
    controls.restart = button('Otra expedición de pistas', 'explore-button', startGame);
    gameActions.append(controls.hintButton, controls.read, controls.next, controls.restart);
    controls.hint = element('p', 'explore-hint');
    controls.hint.id = 'exploreHint';
    controls.feedback = element('p', 'explore-feedback');
    controls.feedback.setAttribute('role', 'status');
    controls.feedback.setAttribute('aria-atomic', 'true');
    controls.game.append(controls.counter, controls.clue, controls.gameNote, gameActions, controls.hint, controls.feedback);
    section.appendChild(controls.game);

    controls.mapInstruction = element('p', 'explore-map-instruction');
    controls.mapInstruction.id = 'exploreMapInstruction';
    section.appendChild(controls.mapInstruction);
    controls.mapPanel = element('div', 'explore-map-panel');
    controls.mapPanel.id = 'exploreMapPanel';
    const mapTools = element('div', 'explore-map-tools');
    controls.mapHelp = element('p', 'explore-overview-help');
    const zoom = button('Acercar mapa', 'explore-button explore-button-secondary', () => {
      zoomed = !zoomed;
      viewport.classList.toggle('explore-map-zoomed', zoomed);
      zoom.setAttribute('aria-pressed', String(zoomed));
      viewport.scrollLeft = 0;
      controls.refreshPan();
    });
    zoom.setAttribute('aria-pressed', 'false');
    zoom.setAttribute('aria-controls', 'exploreMapViewport');
    mapTools.append(zoom, controls.mapHelp);
    controls.mapPanel.appendChild(mapTools);
    const stage = element('div', 'explore-map-stage');
    const image = element('img', 'explore-map-image');
    image.src = context.assets && context.assets['mapa_canarias_interactivo.webp'] || 'assets/images/mapa_canarias_interactivo.webp';
    image.width = 3000;
    image.height = 1514;
    image.alt = 'Mapa de relieve de las ocho islas de Canarias. Las piezas y los nombres situados encima o al lado de las islas permiten abrir cada cuento.';
    stage.appendChild(image);
    const islands = element('div', 'explore-map-islands');
    islands.setAttribute('role', 'group');
    islands.setAttribute('aria-label', 'Elijan una de las ocho rutas insulares');
    controls.pins = context.routes.filter(route => positions[route.id]).map(route => {
      const pin = button('', 'explore-pin', () => chooseIsland(route));
      pin.dataset.route = route.id;
      pin.dataset.island = route.island;
      pin.dataset.badgeName = route.badgeName;
      pin.style.setProperty('--explore-x', positions[route.id][0] + '%');
      pin.style.setProperty('--explore-y', positions[route.id][1] + '%');
      const marker = element('span', 'explore-pin-badge');
      marker.setAttribute('aria-hidden', 'true');
      const badge = element('img', 'explore-pin-image');
      badge.src = context.assets && context.assets[route.badge] || 'assets/images/' + route.badge;
      badge.alt = '';
      badge.width = 44;
      badge.height = 44;
      badge.decoding = 'async';
      marker.appendChild(badge);
      const label = element('span', 'explore-pin-label');
      const state = element('span', 'explore-pin-state');
      state.append(element('span', 'explore-visually-hidden', 'Pieza: '), element('span', 'explore-pin-state-value'));
      label.append(element('strong', 'explore-pin-name', route.island), state);
      pin.append(marker, label);
      islands.appendChild(pin);
      return pin;
    });
    stage.appendChild(islands);
    const viewport = element('div', 'explore-map-viewport');
    viewport.id = 'exploreMapViewport';
    viewport.tabIndex = 0;
    viewport.setAttribute('role', 'region');
    viewport.setAttribute('aria-label', 'Mapa de Canarias con ocho islas seleccionables');
    viewport.setAttribute('aria-describedby', 'exploreMapInstruction explorePanHelp');
    viewport.appendChild(stage);
    controls.mapPanel.appendChild(viewport);
    const panControls = element('div', 'explore-pan-controls');
    panControls.hidden = true;
    const panHelp = element('p', 'explore-pan-help', 'Desplacen el mapa con las flechas o el teclado. Al elegir con Tab, cada isla entra en la zona visible.');
    panHelp.id = 'explorePanHelp';
    const pan = direction => viewport.scrollBy({
      left: direction * Math.max(200, viewport.clientWidth * .8),
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
    });
    const previous = button('←', 'explore-button explore-button-secondary', () => pan(-1));
    previous.setAttribute('aria-label', 'Ver las islas hacia el oeste');
    const next = button('→', 'explore-button explore-button-secondary', () => pan(1));
    next.setAttribute('aria-label', 'Ver las islas hacia el este');
    panControls.append(previous, panHelp, next);
    controls.mapPanel.appendChild(panControls);
    section.appendChild(controls.mapPanel);
    const refreshPan = () => {
      const compact = viewport.clientWidth < parseFloat(getComputedStyle(section).fontSize) * 58;
      viewport.classList.toggle('explore-map-compact', compact);
      controls.mapHelp.textContent = zoomed
        ? 'Mapa ampliado. Desplácense para explorar las islas. Pulsen «Acercar mapa» de nuevo para volver a la vista general.'
        : compact
          ? 'Vista general del archipiélago. Elijan una pieza debajo o acerquen el mapa para elegir sobre él.'
          : 'Vista general del archipiélago. Elijan una pieza o acerquen el mapa para observarlo con más detalle.';
      panControls.hidden = viewport.clientWidth === 0 || viewport.scrollWidth <= viewport.clientWidth + 1;
      previous.disabled = viewport.scrollLeft <= 1;
      next.disabled = viewport.scrollLeft + viewport.clientWidth >= viewport.scrollWidth - 1;
    };
    controls.refreshPan = refreshPan;
    viewport.addEventListener('scroll', refreshPan, {passive: true});
    window.addEventListener('resize', refreshPan);
    if (window.ResizeObserver) new ResizeObserver(refreshPan).observe(viewport);
    requestAnimationFrame(refreshPan);
    controls.progress = element('p', 'explore-progress');
    section.appendChild(controls.progress);
    anchor.parentNode.insertBefore(section, anchor);
    renderMode();
    refresh();
    renderView();
  }

  window.MitoMapaExplorer = Object.freeze({ init, refresh, reset, attachList });
})();
