(() => {
  "use strict";

  const SETLIST = window.MCAESE_SETLIST || { songs: [] };
  const SONGS = Array.isArray(SETLIST.songs) ? SETLIST.songs : [];
  const TOTAL = SONGS.length;
  const STORAGE_KEY = "mcaese.setlist.v1";
  const BASE_FONT = 1.05;
  const FONT_MIN = 0.85;
  const FONT_MAX = 1.8;
  const RING_CIRCUMFERENCE = 2 * Math.PI * 16;

  const STATUS = [
    { label: "Por ver" },
    { label: "Repasar" },
    { label: "Lista" }
  ];

  const byId = new Map(SONGS.map((song, index) => [song.id, { song, index }]));

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  const els = {
    navConcert: $("#navConcert"),
    heroConcert: $("#heroConcert"),
    ringFg: $("#ringFg"),
    readyCount: $("#readyCount"),
    totalCount: $("#totalCount"),
    progressPill: $("#progressPill"),
    cdTiles: $("#cdTiles"),
    cdDays: $("#cdDays"),
    cdHours: $("#cdHours"),
    cdMins: $("#cdMins"),
    cdSecs: $("#cdSecs"),
    cdLive: $("#cdLive"),
    totalSongs: $("#totalSongs"),
    lyricsCount: $("#lyricsCount"),
    readyNote: $("#readyNote"),
    readyLabel: $("#readyLabel"),
    search: $("#search"),
    filters: $("#filters"),
    songGrid: $("#songGrid"),
    emptyState: $("#emptyState"),
    visibleCount: $("#visibleCount"),
    sheetOverlay: $("#sheetOverlay"),
    sheet: $("#sheet"),
    sheetIndex: $("#sheetIndex"),
    sheetTotal: $("#sheetTotal"),
    sheetTitle: $("#sheetTitle"),
    sheetTabs: $("#sheetTabs"),
    sheetParts: $("#sheetParts"),
    sheetClose: $("#sheetClose"),
    fontMinus: $("#fontMinus"),
    fontPlus: $("#fontPlus"),
    searchLyrics: $("#searchLyrics"),
    pasteLyrics: $("#pasteLyrics"),
    clearLyrics: $("#clearLyrics"),
    editLyrics: $("#editLyrics"),
    lyricsView: $("#lyricsView"),
    concertFromSheet: $("#concertFromSheet"),
    lyricsInput: $("#lyricsInput"),
    saveState: $("#saveState"),
    sheetPrev: $("#sheetPrev"),
    sheetNext: $("#sheetNext"),
    prevName: $("#prevName"),
    nextName: $("#nextName"),
    sheetStatus: $("#sheetStatus"),
    concert: $("#concert"),
    concertClose: $("#concertClose"),
    concertBar: $("#concertBar"),
    concertIndex: $("#concertIndex"),
    concertTag: $("#concertTag"),
    concertTitle: $("#concertTitle"),
    concertTabs: $("#concertTabs"),
    concertLyrics: $("#concertLyrics"),
    concertEmpty: $("#concertEmpty"),
    addLyricsBtn: $("#addLyricsBtn"),
    upNext: $("#upNext"),
    concertBody: $("#concertBody"),
    concertPrev: $("#concertPrev"),
    concertNext: $("#concertNext"),
    concertMinus: $("#concertMinus"),
    concertPlus: $("#concertPlus"),
    exportBtn: $("#exportBtn"),
    importBtn: $("#importBtn"),
    importFile: $("#importFile"),
    resetBtn: $("#resetBtn"),
    toast: $("#toast")
  };

  const state = {
    lyrics: {},
    status: {},
    fontSize: BASE_FONT,
    lastSong: null,
    filter: "all",
    query: "",
    current: null,
    currentPart: 0,
    editing: false,
    concertIndex: 0,
    concertPart: 0,
    concertOpen: false,
    lastFocused: null
  };

  let saveTimer = null;
  let saveLabelTimer = null;
  let toastTimer = null;
  let wakeLock = null;

  /* ---------- Utilidades ---------- */

  const esc = (value) =>
    String(value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    }[char]));

  const normalize = (value) =>
    String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();

  const pad = (value) => String(value).padStart(2, "0");

  const statusOf = (id) => {
    const value = Number(state.status[id]);
    return Number.isInteger(value) && value >= 0 && value <= 2 ? value : 0;
  };

  function tracksOf(song) {
    if (Array.isArray(song.parts) && song.parts.length > 0) {
      return song.parts.map((part, index) => ({
        id: part.id || `${song.id}--${index + 1}`,
        title: part.title || song.title,
        note: part.note || "",
        lyrics: typeof part.lyrics === "string" ? part.lyrics : ""
      }));
    }

    return [{
      id: song.id,
      title: song.title,
      note: song.note || "",
      lyrics: typeof song.lyrics === "string" ? song.lyrics : ""
    }];
  }

  const trackById = new Map();
  SONGS.forEach((song) => {
    tracksOf(song).forEach((track) => trackById.set(track.id, track));
  });

  const defaultLyricsOf = (id) => {
    const track = trackById.get(id);
    return track && typeof track.lyrics === "string" ? track.lyrics : "";
  };

  const lyricsOf = (id) => {
    if (typeof state.lyrics[id] === "string" && state.lyrics[id].length > 0) {
      return state.lyrics[id];
    }
    if (state.lyrics[id] === undefined) {
      return defaultLyricsOf(id);
    }
    return state.lyrics[id];
  };

  const hasLyrics = (id) => lyricsOf(id).trim().length > 0;

  const songHasLyrics = (song) => tracksOf(song).some((track) => hasLyrics(track.id));

  const songLyricsCount = (song) => tracksOf(song).filter((track) => hasLyrics(track.id)).length;

  const allTrackIds = () => [...trackById.keys()];

  function buzz(ms = 8) {
    if (navigator.vibrate) {
      try {
        navigator.vibrate(ms);
      } catch (_) {
        /* sin vibración */
      }
    }
  }

  function toast(message) {
    els.toast.textContent = message;
    els.toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => els.toast.classList.remove("show"), 2600);
  }

  /* ---------- Persistencia ---------- */

  function load() {
    trackById.forEach((track) => {
      if (typeof track.lyrics === "string" && track.lyrics.trim()) {
        state.lyrics[track.id] = track.lyrics;
      }
    });

    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const data = JSON.parse(raw);
      if (!data || typeof data !== "object") return;

      const validIds = new Set(allTrackIds());

      if (data.lyrics && typeof data.lyrics === "object") {
        Object.entries(data.lyrics).forEach(([id, value]) => {
          if (validIds.has(id) && typeof value === "string") {
            if (value.trim().length > 0 || !state.lyrics[id]) {
              state.lyrics[id] = value;
            }
          }
        });
      }

      if (data.status && typeof data.status === "object") {
        Object.entries(data.status).forEach(([id, value]) => {
          const status = Number(value);
          if (byId.has(id) && Number.isInteger(status) && status >= 0 && status <= 2) {
            state.status[id] = status;
          }
        });
      }

      const font = Number(data.fontSize);
      if (Number.isFinite(font)) {
        state.fontSize = Math.min(FONT_MAX, Math.max(FONT_MIN, font));
      }

      if (typeof data.lastSong === "string" && byId.has(data.lastSong)) {
        state.lastSong = data.lastSong;
      }
    } catch (error) {
      console.warn("No se pudo leer el guardado local.", error);
    }
  }

  function snapshot() {
    return {
      lyrics: state.lyrics,
      status: state.status,
      fontSize: state.fontSize,
      lastSong: state.lastSong
    };
  }

  function persistSoon() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(persistNow, 260);
  }

  function persistNow() {
    clearTimeout(saveTimer);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot()));
    } catch (error) {
      console.warn("No se pudo guardar.", error);
      toast("No se pudo guardar en este navegador");
    }
  }

  /* ---------- Filtros y tarjetas ---------- */

  function matchesFilter(song) {
    switch (state.filter) {
      case "lyrics":
        return songHasLyrics(song);
      case "empty":
        return !songHasLyrics(song);
      case "review":
        return statusOf(song.id) === 1;
      case "ready":
        return statusOf(song.id) === 2;
      default:
        return true;
    }
  }

  function matchesSearch(song) {
    if (!state.query) return true;
    const tracks = tracksOf(song).map((track) => `${track.title} ${track.note}`);
    const haystack = normalize([song.title, song.note, ...tracks].join(" "));
    return haystack.includes(state.query);
  }

  function metaMarkup(song) {
    const tracks = tracksOf(song);
    const count = songLyricsCount(song);
    const has = count > 0;
    const status = STATUS[statusOf(song.id)];
    const label = !has
      ? "Sin letra"
      : tracks.length > 1
        ? `Con letra ${count}/${tracks.length}`
        : "Con letra";
    return `${has ? `<span class="lyrics-flag">${label}</span>` : label}<span class="sep">·</span><span class="status-text">${status.label}</span>`;
  }

  function cardMarkup(song, index) {
    const status = statusOf(song.id);
    const isMedley = tracksOf(song).length > 1;
    const badges = [
      isMedley ? '<span class="mini-badge medley">Medley</span>' : "",
      song.note ? `<span class="mini-badge note">${esc(song.note)}</span>` : ""
    ].join("");

    return `
      <li class="song" data-id="${esc(song.id)}" data-status="${status}" style="--i:${index}">
        <button class="song-open" type="button" data-open="${esc(song.id)}">
          <span class="num">${pad(index + 1)}</span>
          <span class="song-info">
            <span class="song-top">
              <span class="song-title">${esc(song.title)}</span>
              ${badges}
            </span>
            <span class="song-meta">${metaMarkup(song)}</span>
          </span>
          <svg class="song-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">
            <path d="M7 17 17 7M9 7h8v8"></path>
          </svg>
        </button>
        <button class="song-status" type="button" data-status-cycle="${esc(song.id)}"
          aria-label="Estado de ${esc(song.title)}: ${STATUS[status].label}. Toca para cambiar."
          title="${STATUS[status].label}">
          <span class="status-dot" aria-hidden="true"></span>
        </button>
      </li>`;
  }

  function renderGrid() {
    if (!els.songGrid) return;

    const visible = SONGS
      .map((song, index) => ({ song, index }))
      .filter(({ song }) => matchesFilter(song) && matchesSearch(song));

    els.songGrid.innerHTML = visible.map(({ song, index }) => cardMarkup(song, index)).join("");
    els.emptyState.hidden = visible.length > 0;
    els.visibleCount.textContent = visible.length;
  }

  function updateCard(id, bump = false) {
    const entry = byId.get(id);
    if (!entry) return;

    const card = els.songGrid.querySelector(`.song[data-id="${id}"]`);
    if (!card) return;

    const status = statusOf(id);
    card.dataset.status = String(status);

    const meta = card.querySelector(".song-meta");
    if (meta) meta.innerHTML = metaMarkup(entry.song);

    const button = card.querySelector(".song-status");
    if (button) {
      button.title = STATUS[status].label;
      button.setAttribute(
        "aria-label",
        `Estado de ${entry.song.title}: ${STATUS[status].label}. Toca para cambiar.`
      );
    }

    card.classList.remove("bump");
    if (bump) {
      void card.offsetWidth;
      card.classList.add("bump");
    }
  }

  function cycleStatus(id) {
    if (!byId.has(id)) return;
    state.status[id] = (statusOf(id) + 1) % STATUS.length;
    persistNow();
    updateCard(id, true);
    updateStats();

    if (state.current === id) updateSheetStatus();

    if (state.filter === "review" || state.filter === "ready") {
      renderGrid();
    }

    buzz(6);
  }

  function updateStats() {
    const ready = SONGS.filter((song) => statusOf(song.id) === 2).length;
    const withLyrics = SONGS.filter((song) => songHasLyrics(song)).length;
    const total = TOTAL || 1;

    if (els.readyCount) els.readyCount.textContent = ready;
    if (els.totalCount) els.totalCount.textContent = TOTAL;
    if (els.totalSongs) els.totalSongs.textContent = TOTAL;
    if (els.lyricsCount) els.lyricsCount.textContent = withLyrics;
    if (els.readyNote) els.readyNote.textContent = ready;
    if (els.readyLabel) els.readyLabel.textContent = ready === 1 ? "lista" : "listas";

    if (els.ringFg) {
      els.ringFg.style.strokeDasharray = String(RING_CIRCUMFERENCE);
      els.ringFg.style.strokeDashoffset = String(RING_CIRCUMFERENCE * (1 - ready / total));
    }

    if (els.progressPill) {
      els.progressPill.setAttribute(
        "aria-label",
        `${ready} de ${TOTAL} canciones marcadas como listas`
      );
    }
  }

  /* ---------- Panel de canción ---------- */

  function applyFontSize() {
    document.documentElement.style.setProperty("--lyric-size", `${state.fontSize}rem`);
    if (els.fontMinus) els.fontMinus.disabled = state.fontSize <= FONT_MIN + 0.001;
    if (els.fontPlus) els.fontPlus.disabled = state.fontSize >= FONT_MAX - 0.001;
    if (els.concertMinus) els.concertMinus.disabled = state.fontSize <= FONT_MIN + 0.001;
    if (els.concertPlus) els.concertPlus.disabled = state.fontSize >= FONT_MAX - 0.001;
  }

  function setFontSize(next) {
    state.fontSize = Math.min(FONT_MAX, Math.max(FONT_MIN, Math.round(next * 100) / 100));
    applyFontSize();
    persistNow();
  }

  function sheetNeighbors(index) {
    const prevIndex = (index - 1 + TOTAL) % TOTAL;
    const nextIndex = (index + 1) % TOTAL;
    return {
      prev: SONGS[prevIndex],
      next: SONGS[nextIndex]
    };
  }

  function updateSheetStatus() {
    if (!state.current) return;
    const status = statusOf(state.current);
    els.sheetStatus.textContent = STATUS[status].label;
    els.sheetStatus.dataset.status = String(status);
    els.sheetStatus.setAttribute(
      "aria-label",
      `Estado: ${STATUS[status].label}. Toca para cambiar.`
    );
  }

  function currentTracks() {
    const entry = byId.get(state.current);
    return entry ? tracksOf(entry.song) : [];
  }

  function currentTrack() {
    const tracks = currentTracks();
    if (!tracks.length) return null;
    return tracks[Math.min(state.currentPart, tracks.length - 1)];
  }

  function renderSheetTabs(song) {
    if (!els.sheetTabs) return;
    const tracks = tracksOf(song);

    if (tracks.length < 2) {
      els.sheetTabs.hidden = true;
      els.sheetTabs.innerHTML = "";
      return;
    }

    els.sheetTabs.hidden = false;
    els.sheetTabs.innerHTML = tracks.map((track, index) => {
      const active = index === state.currentPart;
      return `
        <button class="track-tab${active ? " is-active" : ""}" type="button" role="tab"
          aria-selected="${active}" data-part="${index}">
          <span class="track-tab-num">${pad(index + 1)}</span>
          <span class="track-tab-name">${esc(track.title)}</span>
          <span class="track-tab-flag${hasLyrics(track.id) ? " has-lyrics" : ""}">${hasLyrics(track.id) ? "Con letra" : "Sin letra"}</span>
        </button>`;
    }).join("");
  }

  function renderLyricsView() {
    if (!els.lyricsView) return;
    const track = currentTrack();
    const text = track ? lyricsOf(track.id) : "";
    const empty = !text.trim();
    els.lyricsView.textContent = empty
      ? "Todavía no hay letra para esta canción. Toca «Editar letra» para agregarla o pegarla."
      : text;
    els.lyricsView.classList.toggle("is-empty", empty);
  }

  function applyEditingUI() {
    const editing = Boolean(state.editing);
    if (els.lyricsView) els.lyricsView.hidden = editing;
    if (els.lyricsInput) els.lyricsInput.hidden = !editing;
    if (els.editLyrics) {
      els.editLyrics.textContent = editing ? "Listo ✓" : "Editar letra";
      els.editLyrics.classList.toggle("is-done", editing);
      els.editLyrics.setAttribute("aria-pressed", String(editing));
    }
    if (els.sheet) els.sheet.classList.toggle("is-editing", editing);
  }

  function setEditing(next) {
    const editing = Boolean(next);
    state.editing = editing;
    applyEditingUI();

    if (editing) {
      requestAnimationFrame(() => {
        els.lyricsInput.focus({ preventScroll: true });
        els.lyricsInput.scrollTop = 0;
      });
      return;
    }

    persistNow();
    renderLyricsView();
    updateCard(state.current);
    updateStats();
  }

  function syncActiveTrack() {
    const track = currentTrack();
    if (!track) return;

    els.lyricsInput.value = lyricsOf(track.id);
    els.saveState.textContent = hasLyrics(track.id)
      ? "Guardado en este dispositivo"
      : "Se guarda automáticamente en tu dispositivo";
    const queryTitle = track.title.replace(/\s*\((?:pendiente|mitad)\)\s*$/i, "").trim();
    els.searchLyrics.href = `https://www.google.com/search?q=${encodeURIComponent(`MC Aese ${queryTitle} letra`)}`;
    els.lyricsInput.scrollTop = 0;
    if (els.lyricsView) els.lyricsView.scrollTop = 0;
    renderLyricsView();
  }

  function selectSheetPart(index) {
    if (!currentTracks()[index]) return;
    state.currentPart = index;
    const entry = byId.get(state.current);
    if (entry) renderSheetTabs(entry.song);
    syncActiveTrack();
    buzz(4);
  }

  function fillSheet(index) {
    const song = SONGS[index];
    if (!song) return;

    const tracks = tracksOf(song);
    state.currentPart = Math.min(state.currentPart, Math.max(tracks.length - 1, 0));

    els.sheetIndex.textContent = pad(index + 1);
    els.sheetTotal.textContent = TOTAL;
    els.sheetTitle.textContent = song.title;

    renderSheetTabs(song);

    els.sheetParts.innerHTML = song.note
      ? `<span class="part-chip note">${esc(song.note)}</span>`
      : "";

    syncActiveTrack();

    const neighbors = sheetNeighbors(index);
    els.prevName.textContent = neighbors.prev ? neighbors.prev.title : "—";
    els.nextName.textContent = neighbors.next ? neighbors.next.title : "—";

    updateSheetStatus();
  }

  function openSheet(id, part = 0) {
    const entry = byId.get(id);
    if (!entry) return;

    if (els.concert.hidden === false) closeConcert({ restoreFocus: false });

    state.current = id;
    state.currentPart = part;
    state.editing = false;
    state.lastSong = id;
    persistNow();

    fillSheet(entry.index);
    applyEditingUI();
    state.lastFocused = document.activeElement;
    els.sheetOverlay.hidden = false;
    document.body.classList.add("locked");

    requestAnimationFrame(() => {
      els.sheetClose.focus({ preventScroll: true });
    });
  }

  function closeSheet(options = {}) {
    if (els.sheetOverlay.hidden) return;

    persistNow();
    els.sheetOverlay.hidden = true;
    state.current = null;

    if (els.concert.hidden) document.body.classList.remove("locked");

    if (state.filter === "lyrics" || state.filter === "empty") renderGrid();
    updateStats();

    if (options.restoreFocus !== false && state.lastFocused && document.contains(state.lastFocused)) {
      state.lastFocused.focus({ preventScroll: true });
    }
  }

  function stepSheet(direction) {
    const entry = byId.get(state.current);
    if (!entry) return;
    const nextIndex = (entry.index + direction + TOTAL) % TOTAL;
    const nextSong = SONGS[nextIndex];
    state.current = nextSong.id;
    state.currentPart = 0;
    state.lastSong = nextSong.id;
    persistNow();
    fillSheet(nextIndex);
    els.lyricsInput.scrollTop = 0;
    buzz(6);
  }

  function clearLyrics() {
    const track = currentTrack();
    if (!track || !hasLyrics(track.id)) return;

    if (!window.confirm(`¿Borrar la letra de "${track.title}"? No se puede deshacer.`)) return;

    state.lyrics[track.id] = "";
    els.lyricsInput.value = "";
    persistNow();
    els.saveState.textContent = "Letra borrada";
    renderLyricsView();
    const entry = byId.get(state.current);
    if (entry) renderSheetTabs(entry.song);
    updateCard(state.current);
    updateStats();
    toast("Letra borrada");
  }

  async function pasteFromClipboard() {
    const track = currentTrack();
    if (!track) return;

    if (!navigator.clipboard || typeof navigator.clipboard.readText !== "function") {
      toast("Tu navegador no permite pegar automáticamente. Usa una pulsación larga en el campo.");
      return;
    }

    try {
      const text = await navigator.clipboard.readText();
      if (!text.trim()) {
        toast("El portapapeles está vacío");
        return;
      }

      if (
        els.lyricsInput.value.trim() &&
        !window.confirm("Ya hay texto en esta canción. ¿Reemplazarlo por lo del portapapeles?")
      ) {
        return;
      }

      els.lyricsInput.value = text;
      state.lyrics[track.id] = text;
      persistNow();
      renderLyricsView();
      const entry = byId.get(state.current);
      if (entry) renderSheetTabs(entry.song);
      updateCard(state.current);
      updateStats();
      els.saveState.textContent = "Letra pegada ✓";
      toast("Letra pegada");
    } catch (error) {
      console.warn("No se pudo leer el portapapeles", error);
      toast("No se pudo leer el portapapeles. Pega manualmente con una pulsación larga.");
    }
  }

  /* ---------- Modo concierto ---------- */

  async function requestWakeLock() {
    if (!("wakeLock" in navigator) || document.visibilityState !== "visible") return;
    try {
      wakeLock = await navigator.wakeLock.request("screen");
      wakeLock.addEventListener("release", () => {
        wakeLock = null;
      });
    } catch (_) {
      wakeLock = null;
    }
  }

  function releaseWakeLock() {
    if (!wakeLock) return;
    try {
      wakeLock.release();
    } catch (_) {
      /* nada */
    }
    wakeLock = null;
  }

  function flatTracks() {
    const list = [];
    SONGS.forEach((song, songIndex) => {
      const tracks = tracksOf(song);
      tracks.forEach((track, trackIndex) => {
        list.push({ song, songIndex, track, trackIndex, partCount: tracks.length });
      });
    });
    return list;
  }

  function renderConcertTabs(item) {
    if (!els.concertTabs) return;

    if (item.partCount < 2) {
      els.concertTabs.hidden = true;
      els.concertTabs.innerHTML = "";
      return;
    }

    const tracks = tracksOf(item.song);
    els.concertTabs.hidden = false;
    els.concertTabs.innerHTML = tracks.map((track, index) => {
      const active = index === item.trackIndex;
      return `
        <button class="track-tab${active ? " is-active" : ""}" type="button" role="tab"
          aria-selected="${active}" data-concert-part="${index}">
          <span class="track-tab-num">${pad(index + 1)}</span>
          <span class="track-tab-name">${esc(track.title)}</span>
        </button>`;
    }).join("");
  }

  function renderConcert() {
    const flat = flatTracks();
    const item = flat[state.concertIndex];
    if (!item) return;

    const lyrics = lyricsOf(item.track.id).trim();
    els.concertIndex.textContent = pad(item.songIndex + 1);
    els.concertTag.textContent = item.partCount > 1
      ? `${item.trackIndex + 1}/${item.partCount}`
      : (item.song.note || "Setlist");
    els.concertTitle.textContent = item.track.title;
    renderConcertTabs(item);
    els.concertLyrics.textContent = lyrics;
    els.concertLyrics.hidden = !lyrics;
    els.concertEmpty.hidden = Boolean(lyrics);

    const next = flat[state.concertIndex + 1];
    els.upNext.textContent = next ? next.track.title : "Fin del setlist";

    const progress = ((state.concertIndex + 1) / (flat.length || 1)) * 100;
    els.concertBar.style.width = `${progress}%`;
    els.concertBody.scrollTop = 0;
  }

  function selectConcertPart(index) {
    const flat = flatTracks();
    const current = flat[state.concertIndex];
    if (!current || !tracksOf(current.song)[index]) return;

    const target = flat.findIndex(
      (item) => item.song.id === current.song.id && item.trackIndex === index
    );
    if (target < 0) return;

    state.concertIndex = target;
    state.lastSong = current.song.id;
    persistNow();
    renderConcert();
    buzz(4);
  }

  function openConcert(id, part = 0) {
    const flat = flatTracks();
    if (!flat.length) return;

    if (!els.sheetOverlay.hidden) closeSheet({ restoreFocus: false });

    let index = 0;
    if (id && byId.has(id)) {
      const track = tracksOf(byId.get(id).song)[part];
      if (track) {
        const found = flat.findIndex((item) => item.track.id === track.id);
        if (found >= 0) index = found;
      }
    } else if (state.lastSong && byId.has(state.lastSong)) {
      const found = flat.findIndex((item) => item.song.id === state.lastSong);
      if (found >= 0) index = found;
    }

    state.concertIndex = index;
    state.concertOpen = true;
    state.lastFocused = document.activeElement;
    els.concert.hidden = false;
    document.body.classList.add("locked");
    renderConcert();

    requestAnimationFrame(() => els.concertClose.focus({ preventScroll: true }));
    requestWakeLock();
  }

  function closeConcert(options = {}) {
    if (els.concert.hidden) return;

    state.concertOpen = false;
    els.concert.hidden = true;
    if (els.sheetOverlay.hidden) document.body.classList.remove("locked");
    releaseWakeLock();

    if (options.restoreFocus !== false && state.lastFocused && document.contains(state.lastFocused)) {
      state.lastFocused.focus({ preventScroll: true });
    }
  }

  function stepConcert(direction) {
    const flat = flatTracks();
    const next = state.concertIndex + direction;

    if (next < 0) {
      toast("Estás en la primera canción");
      return;
    }

    if (next >= flat.length) {
      toast("Eso es todo. ¡Disfruta el show!");
      return;
    }

    state.concertIndex = next;
    state.lastSong = flat[next].song.id;
    persistNow();
    renderConcert();
    buzz(8);
  }

  /* ---------- Cuenta atrás ---------- */

  function tickCountdown() {
    const target = new Date(SETLIST.date).getTime();
    if (!Number.isFinite(target)) return;

    const diff = target - Date.now();

    if (diff <= 0) {
      els.cdTiles.hidden = true;
      els.cdLive.hidden = false;
      els.cdLive.textContent = diff > -48 * 60 * 60 * 1000
        ? "¡Es hoy! Disfruta el show."
        : "¡Que lo hayas disfrutado!";
      return;
    }

    els.cdTiles.hidden = false;
    els.cdLive.hidden = true;

    const seconds = Math.floor(diff / 1000);
    els.cdDays.textContent = pad(Math.floor(seconds / 86400));
    els.cdHours.textContent = pad(Math.floor((seconds % 86400) / 3600));
    els.cdMins.textContent = pad(Math.floor((seconds % 3600) / 60));
    els.cdSecs.textContent = pad(seconds % 60);
  }

  /* ---------- Importar / exportar ---------- */

  function exportBackup() {
    const payload = {
      app: "mc-aese-setlist",
      version: 1,
      exportedAt: new Date().toISOString(),
      ...snapshot()
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `setlist-mc-aese-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1200);
    toast("Respaldo descargado");
  }

  async function importBackup(file) {
    try {
      const data = JSON.parse(await file.text());
      if (!data || typeof data !== "object" || !data.lyrics || typeof data.lyrics !== "object") {
        throw new Error("Formato no válido");
      }

      if (!window.confirm("Esto reemplazará las letras y estados guardados en este dispositivo. ¿Continuar?")) {
        return;
      }

      const ids = new Set(allTrackIds());
      const lyrics = {};
      trackById.forEach((track) => {
        if (typeof track.lyrics === "string" && track.lyrics.trim()) {
          lyrics[track.id] = track.lyrics;
        }
      });
      const status = {};

      Object.entries(data.lyrics).forEach(([id, value]) => {
        if (ids.has(id) && typeof value === "string") lyrics[id] = value;
      });

      if (data.status && typeof data.status === "object") {
        Object.entries(data.status).forEach(([id, value]) => {
          const parsed = Number(value);
          if (byId.has(id) && Number.isInteger(parsed) && parsed >= 0 && parsed <= 2) {
            status[id] = parsed;
          }
        });
      }

      state.lyrics = lyrics;
      state.status = status;
      state.lastSong = byId.has(data.lastSong) ? data.lastSong : null;

      const font = Number(data.fontSize);
      if (Number.isFinite(font)) state.fontSize = Math.min(FONT_MAX, Math.max(FONT_MIN, font));

      persistNow();
      applyFontSize();
      renderGrid();
      updateStats();
      toast("Respaldo importado");
    } catch (error) {
      console.warn(error);
      toast("Ese archivo no es un respaldo válido");
    }
  }

  function resetAll() {
    if (!window.confirm("Se borrarán todas las letras y estados de este dispositivo. ¿Seguro?")) return;

    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (_) {
      /* nada */
    }

    state.lyrics = {};
    trackById.forEach((track) => {
      if (typeof track.lyrics === "string" && track.lyrics.trim()) {
        state.lyrics[track.id] = track.lyrics;
      }
    });
    state.status = {};
    state.lastSong = null;
    state.fontSize = BASE_FONT;
    state.filter = "all";
    state.query = "";

    els.search.value = "";
    $$(".chip", els.filters).forEach((chip) => {
      chip.classList.toggle("is-active", chip.dataset.filter === "all");
    });

    applyFontSize();
    renderGrid();
    updateStats();
    if (!els.sheetOverlay.hidden) closeSheet({ restoreFocus: false });
    toast("Todo borrado");
  }

  /* ---------- Eventos ---------- */

  function trapFocus(event, container) {
    if (event.key !== "Tab" || !container) return;

    const focusables = $$(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
      container
    ).filter((element) => element.offsetParent !== null);

    if (!focusables.length) return;

    const first = focusables[0];
    const last = focusables[focusables.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  function bindEvents() {
    els.songGrid.addEventListener("click", (event) => {
      const statusButton = event.target.closest("[data-status-cycle]");
      if (statusButton) {
        cycleStatus(statusButton.dataset.statusCycle);
        return;
      }

      const openButton = event.target.closest("[data-open]");
      if (openButton) openSheet(openButton.dataset.open);
    });

    els.songGrid.addEventListener("pointermove", (event) => {
      const card = event.target.closest(".song");
      if (!card) return;
      const rect = card.getBoundingClientRect();
      card.style.setProperty("--x", `${event.clientX - rect.left}px`);
      card.style.setProperty("--y", `${event.clientY - rect.top}px`);
    });

    els.search.addEventListener("input", () => {
      state.query = normalize(els.search.value.trim());
      renderGrid();
    });

    els.filters.addEventListener("click", (event) => {
      const chip = event.target.closest("[data-filter]");
      if (!chip) return;
      state.filter = chip.dataset.filter;
      $$(".chip", els.filters).forEach((item) => {
        item.classList.toggle("is-active", item === chip);
      });
      renderGrid();
    });

    els.sheetClose.addEventListener("click", () => closeSheet());
    els.sheetOverlay.addEventListener("click", (event) => {
      if (event.target === els.sheetOverlay) closeSheet();
    });

    els.lyricsInput.addEventListener("input", () => {
      const track = currentTrack();
      if (!track) return;

      state.lyrics[track.id] = els.lyricsInput.value;
      els.saveState.textContent = "Guardando…";
      persistSoon();
      updateStats();
      updateCard(state.current);

      clearTimeout(saveLabelTimer);
      saveLabelTimer = setTimeout(() => {
        els.saveState.textContent = els.lyricsInput.value.trim()
          ? "Guardado ✓"
          : "Se guarda automáticamente en tu dispositivo";
      }, 550);
    });

    if (els.sheetTabs) {
      els.sheetTabs.addEventListener("click", (event) => {
        const tab = event.target.closest("[data-part]");
        if (tab) selectSheetPart(Number(tab.dataset.part));
      });
    }

    els.fontMinus.addEventListener("click", () => setFontSize(state.fontSize - 0.05));
    els.fontPlus.addEventListener("click", () => setFontSize(state.fontSize + 0.05));
    els.concertMinus.addEventListener("click", () => setFontSize(state.fontSize - 0.05));
    els.concertPlus.addEventListener("click", () => setFontSize(state.fontSize + 0.05));

    els.clearLyrics.addEventListener("click", clearLyrics);
    els.pasteLyrics.addEventListener("click", pasteFromClipboard);
    els.editLyrics.addEventListener("click", () => {
      if (state.editing) {
        setEditing(false);
        els.saveState.textContent = "Guardado ✓";
        toast("Letra guardada");
      } else {
        setEditing(true);
      }
    });

    els.sheetPrev.addEventListener("click", () => stepSheet(-1));
    els.sheetNext.addEventListener("click", () => stepSheet(1));

    els.sheetStatus.addEventListener("click", () => {
      if (state.current) cycleStatus(state.current);
    });

    els.concertFromSheet.addEventListener("click", () => {
      const id = state.current;
      if (!id) return;
      const part = state.currentPart;
      closeSheet({ restoreFocus: false });
      openConcert(id, part);
    });

    els.heroConcert.addEventListener("click", () => openConcert());
    els.navConcert.addEventListener("click", () => openConcert());

    els.concertClose.addEventListener("click", () => closeConcert());
    els.concertPrev.addEventListener("click", () => stepConcert(-1));
    els.concertNext.addEventListener("click", () => stepConcert(1));

    if (els.concertTabs) {
      els.concertTabs.addEventListener("click", (event) => {
        const tab = event.target.closest("[data-concert-part]");
        if (tab) selectConcertPart(Number(tab.dataset.concertPart));
      });
    }

    els.addLyricsBtn.addEventListener("click", () => {
      const item = flatTracks()[state.concertIndex];
      closeConcert({ restoreFocus: false });
      if (item) openSheet(item.song.id, item.trackIndex);
    });

    let touchStart = null;
    els.concertBody.addEventListener(
      "touchstart",
      (event) => {
        const touch = event.changedTouches[0];
        touchStart = { x: touch.clientX, y: touch.clientY };
      },
      { passive: true }
    );

    els.concertBody.addEventListener(
      "touchend",
      (event) => {
        if (!touchStart) return;
        const touch = event.changedTouches[0];
        const dx = touch.clientX - touchStart.x;
        const dy = touch.clientY - touchStart.y;
        touchStart = null;

        if (Math.abs(dx) > 70 && Math.abs(dx) > Math.abs(dy) * 1.6) {
          stepConcert(dx < 0 ? 1 : -1);
        }
      },
      { passive: true }
    );

    els.exportBtn.addEventListener("click", exportBackup);
    els.importBtn.addEventListener("click", () => els.importFile.click());
    els.importFile.addEventListener("change", async () => {
      const file = els.importFile.files && els.importFile.files[0];
      if (file) await importBackup(file);
      els.importFile.value = "";
    });
    els.resetBtn.addEventListener("click", resetAll);

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        if (state.concertOpen) {
          closeConcert();
        } else if (!els.sheetOverlay.hidden) {
          closeSheet();
        }
        return;
      }

      if (state.concertOpen) {
        if (event.key === "ArrowRight" || event.key === "PageDown") {
          event.preventDefault();
          stepConcert(1);
        } else if (event.key === "ArrowLeft" || event.key === "PageUp") {
          event.preventDefault();
          stepConcert(-1);
        }
        trapFocus(event, els.concert);
        return;
      }

      if (!els.sheetOverlay.hidden) {
        trapFocus(event, els.sheet);
        return;
      }

      const target = event.target;
      const typing = target && /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName);
      if (event.key === "/" && !typing) {
        event.preventDefault();
        els.search.focus();
      }
    });

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible" && state.concertOpen) requestWakeLock();
    });
  }

  /* ---------- Inicio ---------- */

  function init() {
    load();
    applyFontSize();
    renderGrid();
    updateStats();
    tickCountdown();
    setInterval(tickCountdown, 1000);
    bindEvents();

    if (els.ringFg) {
      els.ringFg.style.strokeDasharray = String(RING_CIRCUMFERENCE);
    }

    // Si la letra cambia en otra pestaña, avisar al volver.
    window.addEventListener("focus", () => {
      if (state.current || state.concertOpen) return;
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return;
        const data = JSON.parse(raw);
        if (data && data.lyrics && JSON.stringify(data.lyrics) !== JSON.stringify(state.lyrics)) {
          state.lyrics = { ...state.lyrics, ...data.lyrics };
          state.status = data.status || state.status;
          renderGrid();
          updateStats();
        }
      } catch (_) {
        /* nada */
      }
    });
  }

  init();
})();
