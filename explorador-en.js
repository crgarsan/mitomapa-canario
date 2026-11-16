/* Exploración y pistas: una actividad voluntaria que no modifica las piezas. */
(function () {
  'use strict';

  const positions = {
    tenerife: [38.32, 43.5], 'gran-canaria': [53.59, 58], 'la-palma': [18.10, 34.5],
    'la-gomera': [26.5, 55.5], 'el-hierro': [12.4, 69.5],
    fuerteventura: [89.5, 65], lanzarote: [93, 44], 'la-graciosa': [92.5, 23]
  };
  const clues = [
    { id: 'tenerife', text: "In this story, Magec returns and a golden line lights up Echeyde. Which island should I choose?", help: "Dácil looks after goats near the island’s great volcano.", explanation: "In “Dácil and the Return of Magec”, the community asks Achamán to bring back the light." },
    { id: 'gran-canaria', text: "A creature called a tibicena appears among the tabaibas in a ravine. The goatherds stay together. Which island is this story set on?", help: "Guayarmina is the main character in this story.", explanation: "In the Gran Canaria story, Guayarmina and the goatherds keep one another safe and raise their torches." },
    { id: 'la-palma', text: "Acerina hears about Idafe, a rock that seems to hold up the sky. Which island is her story set on?", help: "In the story, the island is called Benahoare.", explanation: "Acerina’s story takes place in the Caldera de Taburiente on La Palma, near Roque Idafe." },
    { id: 'la-gomera', text: "The legend of Gara and Jonay invites us to listen and speak to one another. Where do they meet?", help: "Jonay leaves Tenerife and travels to another island. Look for Gara’s island.", explanation: "They meet on La Gomera. The story invites us to think about the pain that can follow when people stop listening to one another." },
    { id: 'el-hierro', text: "Agarfa collects drops of water from the Garoé. Mist gathers on its branches and water drips into stone basins. Which island is it?", help: "Look for the island furthest to the south-west on the map.", explanation: "In the El Hierro story, the Garoé collects water from the mist, and people keep its memory alive by telling its story." },
    { id: 'fuerteventura', text: "The light of Mafasca follows two goatherds. At dawn, they repair the cross they broke. Which island is this story set on?", help: "It is the long island just south of Lanzarote.", explanation: "The Fuerteventura story retells the legend of the light of Mafasca and a promise to put things right." },
    { id: 'lanzarote', text: "An older woman gives Ico a wet sponge. Ico questions an unfair test. Which island should I choose?", help: "This volcanic island lies next to La Graciosa.", explanation: "The Lanzarote story shows how Ico receives help and questions a test that puts people in danger." },
    { id: 'la-graciosa', text: "Guadarfía and the captain see an island through the mist. It is San Borondón. Which island route includes this story?", help: "Look for the smallest of the eight islands on the map. San Borondón is a separate, legendary island.", explanation: "You can read this story on the La Graciosa route. San Borondón is a legendary island in its own right." }
  ];
  const invitations = {
    tenerife: "How does light return to Echeyde?",
    'gran-canaria': "Why do the goatherds stay together?",
    'la-palma': "How does Acerina keep the memory of Idafe alive?",
    'la-gomera': "What happens when we stop listening?",
    'el-hierro': "How does the Garoé collect water from the mist?",
    fuerteventura: "How can the goatherds put things right?",
    lanzarote: "Why does Ico question an unfair test?",
    'la-graciosa': "How much of what they see might be shaped by their imagination?"
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
    const action = playing && !complete ? "choose this island as your answer" : "open the story";
    const state = pin.classList.contains('explore-pin-earned') ? "earned at the selected learning stage" : "still to earn at the selected learning stage";
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
      const action = answering ? "Answer the clue" : "Open the story";
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
    list.setAttribute('aria-label', "List of eight island routes");
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
      lastMessage = "You found it! " + clue.explanation;
      announce(lastMessage, 'success');
    } else {
      lastMessage = "You chose " + route.island + ". This clue points to another island. Try again, ask for a hint or read the story.";
      announce(lastMessage, 'retry');
    }
    controls.next.hidden = false;
    controls.read.hidden = false;
    controls.pins.forEach(pin => pin.classList.toggle('explore-pin-found', solved && pin.dataset.route === clue.id));
    refreshList();
    controls.gameNote.textContent = "The clues are based on the stories in MitoMapa. Try again or skip to the next clue. You can make as many attempts as you need.";
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
      ? "Choose the island that answers the clue, either on the map or in the list. Press Tab to move between islands and Enter to choose one."
      : "Start with any island. Choose a piece or card to open its story. Press Tab to move between islands and Enter to open a story.";
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
      controls.counter.textContent = "Expedition: " + expedition.length + " clues complete";
      controls.clue.textContent = "You have finished all five clues. Would you like to discover more stories?";
      controls.gameNote.textContent = "Start another expedition or return to the map. You can play independently of the passport and its pieces.";
      announce("Expedition complete. All eight routes are open for reading, rereading and comparing stories.", 'success');
      return;
    }
    const clue = expedition[clueIndex];
    controls.counter.textContent = "Clue " + (clueIndex + 1) + " of " + expedition.length;
    controls.clue.textContent = clue.text;
    controls.hint.textContent = clue.help;
    controls.gameNote.textContent = "These clues draw on MitoMapa’s stories. Read about the legendary island of San Borondón on the La Graciosa route.";
    controls.next.textContent = clueIndex + 1 === expedition.length ? "End the expedition" : "Next clue";
    controls.hintButton.setAttribute('aria-expanded', String(hintVisible));
    announce(lastMessage || "Choose an island. Ask for a hint, read the story or skip a clue. You can try as many times as you need.", solved ? 'success' : 'note');
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
      pin.querySelector('.explore-pin-state-value').textContent = earned ? "Earned" : "Still to earn";
      updatePinLabel(pin);
    });
    controls.progress.textContent = "At the selected learning stage: " + earnedCount + " of " + controls.pins.length + " pieces earned. The optional clue game leaves your progress as it is.";
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
    intro.appendChild(element('p', 'explore-kicker', "Explore the archipelago at your own pace"));
    const title = element('h2', 'section-title', "Choose an island");
    title.id = 'exploreMapTitle';
    intro.appendChild(title);
    intro.appendChild(element('p', 'explore-description', "Eight islands, eight stories. Choose whichever interests you. All the routes are open."));
    section.appendChild(intro);
    const viewSwitch = element('div', 'explore-view-switch');
    viewSwitch.setAttribute('role', 'group');
    viewSwitch.setAttribute('aria-label', "How to choose an island");
    controls.mapView = button("Map", 'explore-button explore-button-secondary', () => setView('map'));
    controls.mapView.setAttribute('aria-controls', 'exploreMapPanel');
    controls.listView = button("List", 'explore-button explore-button-secondary', () => setView('list'));
    controls.listView.disabled = true;
    viewSwitch.append(controls.mapView, controls.listView);
    section.appendChild(viewSwitch);
    const toolbar = element('div', 'explore-actions');
    controls.start = button("Solve five clues", 'explore-button', startGame);
    controls.resume = button("Resume the clues", 'explore-button explore-button-secondary', resumeGame);
    controls.leave = button("Return to free exploration", 'explore-button explore-button-secondary', leaveGame);
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
    controls.hintButton = button("Give me a hint", 'explore-button explore-button-secondary', () => {
      hintVisible = !hintVisible;
      controls.hint.hidden = !hintVisible;
      controls.hintButton.setAttribute('aria-expanded', String(hintVisible));
    });
    controls.hintButton.setAttribute('aria-controls', 'exploreHint');
    controls.read = button("Read the story for this clue", 'explore-button explore-button-secondary', () => openStory(expedition[clueIndex].id));
    controls.next = button("Next clue", 'explore-button', nextClue);
    controls.restart = button("Start another clue expedition", 'explore-button', startGame);
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
    const zoom = button("Zoom in on the map", 'explore-button explore-button-secondary', () => {
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
    image.alt = "Relief map of the eight Canary Islands. Choose a piece or a name on or beside an island to open its story.";
    stage.appendChild(image);
    const islands = element('div', 'explore-map-islands');
    islands.setAttribute('role', 'group');
    islands.setAttribute('aria-label', "Choose one of the eight island routes");
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
      state.append(element('span', 'explore-visually-hidden', "Piece: "), element('span', 'explore-pin-state-value'));
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
    viewport.setAttribute('aria-label', "Map with eight selectable islands");
    viewport.setAttribute('aria-describedby', 'exploreMapInstruction explorePanHelp');
    viewport.appendChild(stage);
    controls.mapPanel.appendChild(viewport);
    const panControls = element('div', 'explore-pan-controls');
    panControls.hidden = true;
    const panHelp = element('p', 'explore-pan-help', "Use the arrow buttons or keyboard to move around the map. Press Tab to bring each island into view.");
    panHelp.id = 'explorePanHelp';
    const pan = direction => viewport.scrollBy({
      left: direction * Math.max(200, viewport.clientWidth * .8),
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
    });
    const previous = button('←', 'explore-button explore-button-secondary', () => pan(-1));
    previous.setAttribute('aria-label', "Show islands further west");
    const next = button('→', 'explore-button explore-button-secondary', () => pan(1));
    next.setAttribute('aria-label', "Show islands further east");
    panControls.append(previous, panHelp, next);
    controls.mapPanel.appendChild(panControls);
    section.appendChild(controls.mapPanel);
    const refreshPan = () => {
      const compact = viewport.clientWidth < parseFloat(getComputedStyle(section).fontSize) * 58;
      viewport.classList.toggle('explore-map-compact', compact);
      controls.mapHelp.textContent = zoomed
        ? "Map zoomed in. Move around to explore the islands. Choose “Zoom in on the map” again to return to the overview."
        : compact
          ? "Overview of the archipelago. Choose a piece below or zoom in and choose directly on the map."
          : "Overview of the archipelago. Choose a piece or zoom in to take a closer look.";
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
