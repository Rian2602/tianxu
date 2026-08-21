/* ═══ Tian Xu: Second Life — frontend (vanilla JS, tanpa build) ═══ */

"use strict";

// ═══ Audio Manager ═══
// Single HTMLAudioElement for main theme, loop, volume, mute, persistence
const AudioManager = (() => {
  const STORAGE_KEY_ENABLED = "tian_xu_audio_enabled";
  const STORAGE_KEY_VOLUME = "tian_xu_audio_volume";
  const DEFAULT_VOLUME = 0.3;
  const AUDIO_PATH = "/static/assets/audio/dawn-over-tian-xu.mp3";

  let audio = null;
  let enabled = true;
  let volume = DEFAULT_VOLUME;
  let started = false; // track if user gesture has initiated playback
  let pendingPlay = false;

  function init() {
    // Load preferences from localStorage
    try {
      const storedEnabled = localStorage.getItem(STORAGE_KEY_ENABLED);
      const storedVolume = localStorage.getItem(STORAGE_KEY_VOLUME);
      if (storedEnabled !== null) enabled = storedEnabled === "true";
      if (storedVolume !== null) volume = Math.max(0, Math.min(1, parseFloat(storedVolume)));
    } catch (e) {
      // localStorage unavailable — use defaults
    }

    // Create audio element
    audio = new Audio(AUDIO_PATH);
    audio.loop = true;
    audio.preload = "auto";
    audio.volume = enabled ? volume : 0;

    // Error handling — graceful degradation (configure() dapat membuat ulang
    // dengan path data-driven bila lagu default tidak tersedia untuk tema baru)
    audio.addEventListener("error", (e) => {
      console.warn("[AudioManager] Audio load error:", e);
      audio = null; // prevent further attempts
    });

    // Update UI after init
    updateUI();
  }

  function configure(path) {
    // Data-driven (config.web.audio) — tema story baru boleh memakai lagu
    // sendiri; dipanggil setelah ctx termuat (startNew/loadGame).
    if (!path) return;
    if (audio && audio.getAttribute("src") === path) return;
    const el = new Audio(path);
    el.loop = true;
    el.preload = "auto";
    el.volume = enabled ? volume : 0;
    el.addEventListener("error", (e) => {
      console.warn("[AudioManager] Audio load error:", e);
      audio = null;
    });
    audio = el;
    started = true; // konteks user-gesture (tombol Mulai/Lanjut)
    if (enabled) el.play().catch(() => { /* autoplay ditolak — diam */ });
  }

  function persist() {
    try {
      localStorage.setItem(STORAGE_KEY_ENABLED, String(enabled));
      localStorage.setItem(STORAGE_KEY_VOLUME, String(volume));
    } catch (e) {
      // ignore
    }
  }

  function updateUI() {
    const muteBtn = document.getElementById("btn-audio-mute");
    const volumeSlider = document.getElementById("audio-volume");
    const volumeLabel = document.getElementById("audio-volume-label");
    const muteBtnTopbar = document.getElementById("btn-audio-mute-topbar");
    const volumeSliderTopbar = document.getElementById("audio-volume-topbar");
    const volumeLabelTopbar = document.getElementById("audio-volume-label-topbar");

    [muteBtn, muteBtnTopbar].forEach((btn) => {
      if (btn) {
        btn.textContent = enabled ? "♫" : "🔇";
        btn.setAttribute("aria-label", enabled ? "Matikan musik" : "Nyalakan musik");
        btn.classList.toggle("muted", !enabled);
      }
    });
    [volumeSlider, volumeSliderTopbar].forEach((slider) => {
      if (slider) {
        slider.value = volume;
        slider.disabled = !enabled;
      }
    });
    [volumeLabel, volumeLabelTopbar].forEach((label) => {
      if (label) {
        label.textContent = Math.round(volume * 100) + "%";
      }
    });
  }

  function ensureAudio() {
    if (!audio) return false;
    return true;
  }

  async function start() {
    if (!ensureAudio()) return;
    if (started) return;
    started = true;
    if (enabled) {
      try {
        await audio.play();
      } catch (e) {
        // Autoplay rejected — wait for user gesture via pendingPlay
        pendingPlay = true;
      }
    }
  }

  function play() {
    if (!ensureAudio()) return;
    if (!enabled) return;
    audio.play().catch((e) => {
      console.warn("[AudioManager] Play rejected:", e);
    });
  }

  function pause() {
    if (!ensureAudio()) return;
    audio.pause();
  }

  function resume() {
    play();
  }

  function stop() {
    if (!ensureAudio()) return;
    audio.pause();
    audio.currentTime = 0;
  }

  function setVolume(v) {
    volume = Math.max(0, Math.min(1, v));
    if (audio) audio.volume = enabled ? volume : 0;
    persist();
    updateUI();
  }

  function toggleMute() {
    enabled = !enabled;
    if (audio) audio.volume = enabled ? volume : 0;
    persist();
    updateUI();
  }

  function isPlaying() {
    return audio && !audio.paused && !audio.ended;
  }

  function getVolume() {
    return volume;
  }

  function isEnabled() {
    return enabled;
  }

  // Initialize on module load
  if (typeof document !== "undefined") {
    // Defer init until DOM ready to avoid blocking
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  }

  return {
    init,
    configure,
    start,
    play,
    pause,
    resume,
    stop,
    setVolume,
    toggleMute,
    isPlaying,
    getVolume,
    isEnabled,
    updateUI,
  };
})();

let currentSave = "save1";

// B8: focus trap sederhana untuk modal — simpan fokus sebelum buka, restore saat tutup
let lastFocus = null;

// D1 (2026-08-15): fade+scale saat buka/tutup — .modal-visible di-toggle lewat
// requestAnimationFrame (buka) / setTimeout selaras durasi CSS (tutup) agar
// transition sempat ter-trigger sebelum display:none (lihat style.css §Modals).
const MODAL_TRANSITION_MS = 200;

function showModal(id) {
  $(id).classList.remove("hidden");
  $("modal-overlay").classList.remove("hidden");
  requestAnimationFrame(() => {
    $(id).classList.add("modal-visible");
    $("modal-overlay").classList.add("modal-visible");
  });
  lastFocus = document.activeElement;
  const first = $(id).querySelector("button, a, input, select");
  if (first) first.focus();
}
function closeModal(id) {
  $(id).classList.remove("modal-visible");
  $("modal-overlay").classList.remove("modal-visible");
  setTimeout(() => {
    if (!$(id).classList.contains("modal-visible")) {
      $(id).classList.add("hidden");
      $("modal-overlay").classList.add("hidden");
    }
  }, MODAL_TRANSITION_MS);
  if (lastFocus && lastFocus.focus) lastFocus.focus();
}

document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  ["modal-shop", "modal-arc-summary"].forEach((id) => {
    if (!$("modal-overlay").classList.contains("hidden") && !$(id).classList.contains("hidden")) {
      closeModal(id);
    }
  });
  closeTianyuan();
  closeRightDrawer();
});

const $ = (id) => document.getElementById(id);

let view = null;      // respons /api/state → {view, context}
let ctx = null;

// ---------- API ----------

let busy = false;

async function api(path, opts) {
  const opt = { method: (opts && opts.method) || "POST", headers: { "Content-Type": "application/json" } };
  if (opts && opts.body !== undefined) opt.body = JSON.stringify(opts.body);
  try {
    const res = await fetch(path, opt);
    return await res.json();
  } catch (e) {
    return { ok: false, error: "Koneksi gagal: " + (e.message || e) };
  }
}

// ---------- aman HTML ----------

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

// ---------- C2: icon Lucide (self-host, inline SVG) ----------
// SVG di-fetch dari /static/assets/icons/ sekali lalu di-cache; dipakai via
// `icon(name, size)` → `<svg class="lucide" ...>` dengan stroke currentColor.
const ICON_CACHE = {};

async function loadIcons() {
  const names = ["sword", "shield", "book-open", "map-pin", "message-circle", "x",
                 "heart", "backpack", "scroll-text", "target", "sparkles", "landmark",
                 "trophy", "ancient-symbol", "cycle-notes", "first-artifact",
                 "scroll", "flask", "gem", "leaf", "crystal", "pill"];
  await Promise.all(names.map(async (n) => {
    try {
      const r = await fetch(`/static/assets/icons/${n}.svg`);
      const t = await r.text();
      ICON_CACHE[n] = t.replace(/^<!--[\s\S]*?-->\s*/, "").replace(/^\s*/, "");
    } catch (e) { ICON_CACHE[n] = ""; }
  }));
  // re-render bila icon tiba setelah layar game aktif
  if (view) render();
}

function icon(name, size) {
  const s = size || 14;
  let svg = ICON_CACHE[name] || "";
  if (!svg) return "";
  svg = svg.replace("width=\"24\"", `width="${s}"`).replace("height=\"24\"", `height="${s}"`);
  svg = svg.replace("<svg", `<svg style="vertical-align:-2px; margin-right:5px;"`);
  return svg;
}

// ---------- layar judul ----------

async function refreshSaveSlots() {
  const data = await api("/api/saves", { method: "GET" });
  const box = $("save-slots");
  box.innerHTML = "";
  if (!data.saves || data.saves.length === 0) {
    box.innerHTML = '<p class="hint">Belum ada save. Mulai baru.</p>';
    return;
  }
  data.saves.forEach((name) => {
    const b = document.createElement("button");
    b.className = "save-slot";
    b.textContent = "Lanjut — " + name;
    b.onclick = () => { AudioManager.start(); loadGame(name); };
    box.appendChild(b);
  });
}

function showGame() {
  const ts = $("title-screen");
  ts.classList.add("screen-out");
  setTimeout(() => {
    ts.classList.add("hidden");
    $("game-screen").classList.remove("hidden");
  }, 400);
}

// Judul game data-driven (config.web) — tema story baru boleh punya judul sendiri
function applyMeta(m) {
  if (!m) return;
  const title = m.title || "天缘灵";
  const subtitle = m.subtitle || "TIAN XU: SECOND LIFE";
  const tagline = m.tagline || "天缘灵 · Tian Xu: Second Life";
  const panel = m.panel || "Tianyuan Ling";
  document.title = tagline;
  const gt = $("game-title");   if (gt) gt.textContent = title;
  const gs = $("game-subtitle"); if (gs) gs.textContent = subtitle;
  const tg = $("game-tagline");  if (tg) tg.textContent = tagline;
  const bt = $("btn-tianyuan");  if (bt) bt.textContent = `${title} · Panel`;
}

async function startNew() {
  const data = await api("/api/new");
  if (data.ok) {
    currentSave = "save1"; view = data.view; ctx = data.context;
    applyMeta(ctx.meta);
    AudioManager.configure((ctx.meta || {}).audio); // lagu dari config.web
    showGame(); render();
  }
  else { window.alert(data.error || "Gagal memulai."); }
}

async function loadGame(name) {
  const data = await api("/api/load", { body: { name } });
  if (!data.ok) { $("title-msg").textContent = data.error || "Gagal memuat."; return; }
  currentSave = name; view = data.view; ctx = data.context;
  applyMeta(ctx.meta);
  AudioManager.configure((ctx.meta || {}).audio);
  showGame(); render();
}

async function reloadData() {
  await api("/api/reload", { method: "GET" });
  if (currentSave) {
    await loadGame(currentSave);
  } else {
    const data = await api("/api/state", { method: "GET" });
    if (data.view) { view = data.view; ctx = data.context; render(); }
  }
}

// ---------- render utama ----------

function render() {
  if (!view) return;
  // C4: ambience lokasi saat ini → class di body untuk atmosfer visual
  document.body.className = document.body.className
    .split(" ").filter((c) => !c.startsWith("ambience-")).join(" ")
    + (view.location && view.location.ambience ? ` ambience-${esc(view.location.ambience)}` : "");
  renderHeader(view);
  renderLeft(view);
  renderRight(view);
  renderCenter(view, ctx);
  const logEl = $("log");
  logEl.scrollTop = logEl.scrollHeight;

  // arc_summary per-arc: simpan JUDUL arc yang sudah di-dismiss — bukan flag
  // sekali-saja — agar seluruh 7 arc menampilkan summary-nya masing-masing.
  if (view.arc_summary && localStorage.getItem("arc-seen:" + currentSave) !== view.arc_summary.title) {
    openArcSummaryModal(view.arc_summary);
  }
}

function renderHeader(v) {
  const loc = v.location;
  $("header-title").textContent =
    `Bulan ${v.month} — Hari ${v.day} — ${loc.name}`;
}

function statRow(label, value, cls) {
  // Label boleh mengandung icon dari icon() (SVG) atau customIcon() (<img>) — aman.
  // Escape hanya segmen TEKS; markup <svg>...</svg> dan <img ...> dibiarkan utuh.
  const labelHtml = String(label ?? "").split(/(<svg[\s\S]*?<\/svg>|<img[^>]*>)/g)
    .map((part) => (part.startsWith("<svg") || part.startsWith("<img")) ? part : esc(part)).join("");
  return `<div class="stat-row"><span class="stat-label">${labelHtml}</span>` +
         `<span class="stat-value ${cls || ""}">${esc(value)}</span></div>`;
}

// D1 (2026-08-15): stat dengan bar pelengkap (HP/Qi) — ENGINE_ARCHITECTURE §12.5:
// angka tetap WAJIB tampil (statRow di dalamnya), bar TIDAK menggantikannya.
// current/max dipakai untuk hitung persentase fill; barCls mewarnai fill (mis. "red" saat HP kritis).
function statBarRow(label, current, max, barCls) {
  const pct = max > 0 ? Math.max(0, Math.min(100, Math.round((current / max) * 100))) : 0;
  return `
    <div class="stat-bar-wrap">
      <div class="stat-bar-head"><span class="stat-bar-label">${label}</span><span class="stat-bar-num">${current}/${max}</span></div>
      <div class="stat-bar-track"><div class="stat-bar-fill ${barCls || ""}" data-target="${pct}%" style="width:${pct}%"></div></div>
    </div>
  `;
}

function customIcon(name) {
  const map = {
    gold: "/static/assets/img/ui/icon_coin_1.png",
    qi: "/static/assets/img/ui/icon_water.png",
    moral: "/static/assets/img/ui/icon_jade.png"
  };
  if (map[name]) {
    // onerror → sembunyikan bila PNG khusus tema tidak ada (fallback rapi,
    // bukan ikon rusak); icon Lucide (map miss) sudah generic lintas tema
    return `<img src="${map[name]}" onerror="this.style.display='none'" style="width:16px;height:16px;vertical-align:text-bottom;margin-right:6px;filter:drop-shadow(0 2px 3px rgba(0,0,0,0.5))">`;
  }
  return icon(name);
}

function renderLeft(v) {
  const p = v.player;
  const names = (ctx && ctx.item_names) || {};
  const wid = p.equipment && p.equipment.weapon;
  const w = wid ? (names[wid] || wid) : "—";
  const comp = v.companion;
  
  // avatar data-driven (config.web.avatar); bila gagal dimuat → fallback
  // inisial nama pemain (tema baru boleh tanpa avatar.jpg)
  const avatarPath = (ctx && ctx.meta && ctx.meta.avatar) || "/static/assets/img/avatar.jpg";
  let html = `
    <div style="text-align: center; margin-bottom: 16px;">
      <img src="${esc(avatarPath)}" alt="Avatar" onerror="this.style.display='none';var f=document.getElementById('avatar-fallback');if(f)f.style.display='flex';" style="width: 120px; height: 120px; border-radius: 50%; border: 2px solid var(--gold); object-fit: cover; box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);">
      <div id="avatar-fallback" class="avatar-fallback" style="display:none;">${esc((p.name || "?").charAt(0))}</div>
    </div>
    <div class="player-name-row">
      <div class="seal">Lv${p.realm_level || 1}</div>
      <div>
        <div class="player-name">${esc(p.name)}</div>
        <div class="stat-label" style="font-size:11px">${esc(p.realm)} · ${p.roots ? esc(p.roots) : "Akar Biasa"}</div>
      </div>
    </div>
    <div class="ink-divider"></div>
  `;

  html += statBarRow("HP", p.hp, p.hp_max, "hp");
  html += statBarRow("Qi", p.qi, p.qi_max, "qi");
  html += statBarRow("Dantian", p.dantian_exp || 0, p.dantian_capacity || 20, "exp");

  // time display
  const hour = v.hour || 0;
  const remaining = 24 - hour;
  html += `<div style="margin: 8px 0; font-size: 12px; color: var(--gray);">` +
    `${icon("clock")} Jam ${String(hour).padStart(2, "0")}:00 · Sisa ${remaining} jam</div>`;

  // fatigue warning
  if (!p.rested_today) {
    const pen = p.fatigue_days * 2;
    html += `<div style="margin: 2px 0; font-size: 11px; color: #d96b5f;">⚠ Belum istirahat! (−${pen} HP max)</div>`;
  }

  // meditasi weekly counter
  const medLimit = (ctx && ctx.meditate_weekly_limit) || 3;
  const medCount = p.meditate_week_count || 0;
  html += `<div style="margin: 4px 0 8px; font-size: 12px; color: var(--gray);">` +
    `${icon("moon")} Meditasi: ${medCount}/${medLimit} minggu ini</div>`;

  // status effects
  if (p.status_effects && p.status_effects.length > 0) {
    p.status_effects.forEach(e => {
      const name = e.type === "cultivation_deviation" ? "Debuff Qi Deviasi" : e.type;
      html += `<div style="margin: 2px 0; font-size: 11px; color: #d96b5f;">⚠ ${esc(name)} (${e.days_left} hari)</div>`;
    });
  }
  if (p.pil_sukses_active) {
    html += `<div style="margin: 2px 0; font-size: 11px; color: #8fbf8f;">✦ Pil Sukses aktif (+30%)</div>`;
  }
  if (p.pil_aman_active) {
    html += `<div style="margin: 2px 0; font-size: 11px; color: #8fbf8f;">✦ Pil Aman aktif</div>`;
  }

  const ic = customIcon;
  html += statRow(ic("gold") + "Koin Emas", p.gold, "gold");
  html += statRow(ic("moral") + "Moral", p.morality, p.morality > 0 ? "green" : (p.morality < 0 ? "red" : ""));
  html += statRow(icon("landmark") + "Akademi", (ctx && ctx.academy) || "—");
  html += statRow(ic("sword") + "Senjata", w);
  if (comp) {
    html += `<h3 class="stat-title" style="margin-top:18px">✦ Roh</h3>`;
    html += statRow(comp.name, `HP ${comp.hp}/${comp.hp_max}`, comp.hp <= 0 ? "red" : "");
  }
  // Companion list (multi-companion)
  const companions = v.companions || [];
  if (companions.length > 1) {
    html += `<h3 class="stat-title" style="margin-top:18px">✦ Kawan</h3>`;
    for (const c of companions) {
      const sel = c.selected ? " selected" : "";
      const dead = c.hp <= 0 ? " dead" : "";
      const safe = v.location && v.location.is_safe;
      const onclick = (safe && !c.selected) ? ` onclick="act({type:'switch_companion',companion:'${esc(c.id)}'})"` : "";
      html += `<div class="companion-row${sel}${dead}"${onclick}>`;
      html += `<span class="companion-name">${c.selected ? "▸ " : ""}${esc(c.name)}</span>`;
      html += `<span class="companion-hp">HP ${c.hp}/${c.hp_max}</span>`;
      html += `</div>`;
    }
  }
  $("col-left").innerHTML = html;
}

// Task 4: 5 tingkat hubungan (rekomendasi hostile/distrustful/neutral/friendly/close)
function getRelationTier(score) {
  const num = Number(score) || 0;
  if (num <= -20) return { label: "Bermusuhan", cls: "hostile" };
  if (num < 0)   return { label: "Kurang Akrab", cls: "distrustful" };
  if (num === 0) return { label: "Netral", cls: "neutral" };
  if (num < 20)  return { label: "Bersahabat", cls: "friendly" };
  return { label: "Akrab", cls: "close" };
}

function renderRight(v) {
  let html = "";
  // quest utama
  html += `<div class="section"><h3 class="stat-title">${icon("target")}Quest Utama</h3>`;
  if (v.current_quest) {
    html += `<div class="quest-row"><span class="seal seal-sm">主</span><div>`;
    html += `<div class="quest-title">${esc(v.current_quest.title)}</div>`;
    html += `<div class="quest-objective">${esc(v.current_quest.objective)}</div>`;
    html += `</div></div>`;
  } else {
    html += `<div class="quest-done">Tidak ada quest utama aktif.</div>`;
  }
  html += `</div>`;
  
  // side quest
  if (v.side_quests && v.side_quests.length) {
    html += `<div class="section"><h3 class="stat-title">${icon("scroll-text")}Quest Sampingan</h3>`;
    v.side_quests.forEach((q) => {
      html += `<div class="quest-row"><span class="seal seal-ghost seal-sm">支</span><div>`;
      html += `<div class="quest-title">${esc(q.title)}</div>`;
      html += `<div class="quest-objective">${esc(q.objective)}</div>`;
      html += `</div></div>`;
    });
    html += `</div>`;
  }
  
  // kurikulum paviliun
  if (ctx && ctx.curriculum && ctx.curriculum.length) {
    html += `<div class="section"><h3 class="stat-title">${icon("book-open")}Kurikulum Akademi</h3>`;
    ctx.curriculum.forEach((t) => {
      let badge = "";
      if (t.status === "learned") {
        badge = `<span class="badge badge-learned">Dikuasai${t.level ? ` (Lv.${t.level})` : ""}</span>`;
      } else if (t.status === "available") {
        badge = `<span class="badge badge-available">Tersedia</span>`;
      } else {
        badge = `<span class="badge badge-locked">Terkunci</span>`;
      }
      html += `<div class="curriculum-row ${esc(t.status)}"><span class="item-name">${esc(t.name)}</span>` +
              `<span class="item-status">${badge}</span></div>`;
    });
    html += `</div>`;
  }
  
  // hubungan NPC
  html += `<div class="section"><h3 class="stat-title">${icon("heart")}Hubungan</h3>`;
  const relEntries = (ctx && ctx.relations) ? Object.entries(ctx.relations) : [];
  if (relEntries.length > 0) {
    relEntries.forEach(([nid, score]) => {
      const name = (ctx.npc_names && ctx.npc_names[nid]) || nid;
      const tier = getRelationTier(score);
      const num = Number(score) || 0;
      const sign = num > 0 ? `+${num}` : `${num}`;
      html += `<div class="relation-row"><span class="item-name">${esc(name)}</span>` +
              `<span class="badge badge-${esc(tier.cls)}">${esc(tier.label)} (${sign})</span></div>`;
    });
  } else {
    html += `<div class="quest-done">Belum ada catatan hubungan khusus.</div>`;
  }
  html += `</div>`;
  
  // NPC Codex button
  html += `<div class="section"><button class="codex-btn" onclick="openNpcCodex()">${icon("users")}Kodex NPC</button></div>`;
  
  // status karakter (docs 04: Family Crisis state_*_status per anggota) —
  // data-driven dari context.character_status; label + warna tema-agnostik
  if (ctx && ctx.character_status && ctx.character_status.length) {
    const statusLabel = { loyal: "Setia", separated: "Terpisah", disillusioned: "Kecewa" };
    const statusCls = { loyal: "badge-close", separated: "badge-locked", disillusioned: "badge-hostile" };
    html += `<div class="section"><h3 class="stat-title">${icon("heart")}Status Karakter</h3>`;
    ctx.character_status.forEach((cs) => {
      const label = statusLabel[cs.status] || cs.status;
      const cls = statusCls[cs.status] || "badge-neutral";
      html += `<div class="relation-row"><span class="item-name">${esc(cs.name)}</span>` +
              `<span class="badge ${esc(cls)}">${esc(label)}</span></div>`;
    });
    html += `</div>`;
  }

  // faksi (docs 05/13: state_rep_* — reputasi per faksi dari data)
  if (v.factions && v.factions.length) {
    html += `<div class="section"><h3 class="stat-title">${icon("landmark")}Fraksi</h3>`;
    v.factions.forEach((f) => {
      const num = Number(f.score) || 0;
      const tier = getRelationTier(num);
      const sign = num > 0 ? `+${num}` : `${num}`;
      html += `<div class="relation-row"><span class="item-name">${esc(f.name)}</span>` +
              `<span class="badge badge-${esc(tier.cls)}">${esc(tier.label)} (${sign})</span></div>`;
    });
    html += `</div>`;
  }

  // inventori
  html += `<div class="section"><h3 class="stat-title">${icon("backpack")}Inventori</h3>`;
  if (v.inventory && v.inventory.length) {
    v.inventory.forEach((i) => {
      html += `<div class="item-row"><span class="item-name rarity-${esc(i.rarity || 'common')}">${esc(i.name)}</span>` +
              `<span class="item-count">×${i.count}</span></div>`;
    });
  } else {
    html += `<div class="quest-done">Kosong.</div>`;
  }
  html += `</div>`;
  
  // ingatan — judul panel data-driven (config.web.title)
  const gameTitle = (ctx && ctx.meta && ctx.meta.title) || "天缘灵";
  html += `<div class="section"><h3 class="stat-title">${icon("sparkles")}${esc(gameTitle)} · Ingatan</h3>`;
  if (v.memories && v.memories.length) {
    v.memories.forEach((m, idx) => {
      let num = String(idx+1).padStart(2, '0');
      html += `<div class="mem-row" onclick="openTianyuan()"><span class="seal seal-sm">${num}</span> ${esc(m.title)}</div>`;
    });
  } else {
    html += `<div class="mem-row locked"><span class="seal seal-ghost seal-sm">？</span> Belum Terbuka</div>`;
  }
  html += `</div>`;

  // GAP-C3: Pencapaian
  if (unlockedAchievements.size > 0) {
    html += `<div class="section"><h3 class="stat-title">${icon("trophy")}Pencapaian</h3>`;
    unlockedAchievements.forEach(id => {
      const a = ACHIEVEMENTS[id];
      if (a) html += `<div class="achievement-badge badge-achievement">${a.icon} ${esc(a.title)}</div> `;
    });
    html += `</div>`;
  }

  $("col-right").innerHTML = html;
}

// ---------- NPC Codex ----------

function openNpcCodex() {
  const profiles = (ctx && ctx.npc_profiles) || {};
  const relations = (ctx && ctx.relations) || {};
  
  let html = `<div class="codex-overlay" onclick="closeNpcCodex(event)">`;
  html += `<div class="codex-panel" onclick="event.stopPropagation()">`;
  html += `<div class="codex-header">`;
  html += `<h2>${icon("users")}Kodex NPC</h2>`;
  html += `<button class="codex-close" onclick="closeNpcCodex()">&times;</button>`;
  html += `</div>`;
  html += `<div class="codex-list">`;
  
  // Sort NPCs by relation score (highest first)
  const sorted = Object.entries(profiles).sort((a, b) => {
    const relA = (a[1].relation || 0);
    const relB = (b[1].relation || 0);
    return relB - relA;
  });
  
  for (const [nid, data] of sorted) {
    const profile = data.profile || {};
    const relation = data.relation || 0;
    const tier = getRelationTier(relation);
    
    // Progressive reveal based on relation tier
    let revealLevel = 0;
    if (relation >= -20) revealLevel = 1; // Name + title
    if (relation < 0) revealLevel = 1; // Distrustful — still shows name
    if (relation === 0) revealLevel = 1; // Neutral
    if (relation > 0) revealLevel = 2; // Friendly — shows bio
    if (relation >= 5) revealLevel = 3; // Close — shows all stats
    if (relation >= 20) revealLevel = 4; // Very close — shows everything
    
    html += `<div class="codex-card" onclick="showNpcDetail('${esc(nid)}')">`;
    html += `<div class="codex-card-header">`;
    html += `<div class="codex-card-initial">${esc((data.name || "?").charAt(0))}</div>`;
    html += `<div class="codex-card-info">`;
    html += `<div class="codex-card-name">${esc(data.name)}</div>`;
    html += `<div class="codex-card-tier badge badge-${esc(tier.cls)}">${esc(tier.label)}</div>`;
    html += `</div>`;
    html += `</div>`;
    
    if (revealLevel >= 2 && profile.bio) {
      html += `<div class="codex-card-bio">${esc(profile.bio)}</div>`;
    }
    if (revealLevel >= 3) {
      html += `<div class="codex-card-stats">`;
      if (profile.realm) html += `<span>${icon("star")}${esc(profile.realm)}</span>`;
      if (profile.weapon && profile.weapon !== "Tidak Ada") html += `<span>${icon("sword")}${esc(profile.weapon)}</span>`;
      if (profile.element && profile.element !== "tidak ada") html += `<span>${icon("flame")}${esc(profile.element)}</span>`;
      html += `</div>`;
    }
    if (revealLevel >= 4) {
      html += `<div class="codex-card-extra">`;
      if (profile.faction) html += `<span>${icon("landmark")}${esc(profile.faction)}</span>`;
      if (profile.companion) html += `<span>${icon("heart")}${esc(profile.companion)}</span>`;
      html += `</div>`;
    }
    
    html += `</div>`;
  }
  
  html += `</div></div></div>`;
  
  // Add overlay to body
  const overlay = document.createElement("div");
  overlay.innerHTML = html;
  document.body.appendChild(overlay.firstElementChild);
}

function closeNpcCodex(e) {
  if (e && e.target && !e.target.classList.contains("codex-overlay")) return;
  const overlay = document.querySelector(".codex-overlay");
  if (overlay) overlay.remove();
}

function showNpcDetail(nid) {
  const profiles = (ctx && ctx.npc_profiles) || {};
  const data = profiles[nid];
  if (!data) return;
  
  const profile = data.profile || {};
  const relation = data.relation || 0;
  const tier = getRelationTier(relation);
  
  // Determine reveal level
  let revealLevel = 0;
  if (relation >= -20) revealLevel = 1;
  if (relation < 0) revealLevel = 1;
  if (relation === 0) revealLevel = 1;
  if (relation > 0) revealLevel = 2;
  if (relation >= 5) revealLevel = 3;
  if (relation >= 20) revealLevel = 4;
  
  let html = `<div class="codex-overlay" onclick="closeNpcCodex(event)">`;
  html += `<div class="codex-detail" onclick="event.stopPropagation()">`;
  html += `<div class="codex-detail-header">`;
  html += `<div class="codex-detail-initial">${esc((data.name || "?").charAt(0))}</div>`;
  html += `<div class="codex-detail-info">`;
  html += `<h2>${esc(data.name)}</h2>`;
  html += `<div class="badge badge-${esc(tier.cls)}">${esc(tier.label)} (${relation > 0 ? "+" : ""}${relation})</div>`;
  html += `</div>`;
  html += `<button class="codex-close" onclick="closeNpcCodex()">&times;</button>`;
  html += `</div>`;
  
  html += `<div class="codex-detail-body">`;
  
  if (revealLevel >= 2 && profile.bio) {
    html += `<div class="codex-detail-section">`;
    html += `<h3>${icon("scroll-text")}Bio</h3>`;
    html += `<p>${esc(profile.bio)}</p>`;
    html += `</div>`;
  }
  
  if (revealLevel >= 3) {
    html += `<div class="codex-detail-section">`;
    html += `<h3>${icon("star")}Status</h3>`;
    html += `<div class="codex-stat-grid">`;
    if (profile.realm) html += `<div class="codex-stat"><span class="codex-stat-label">Ranah</span><span class="codex-stat-value">${esc(profile.realm)}</span></div>`;
    if (profile.realm_level) html += `<div class="codex-stat"><span class="codex-stat-label">Level</span><span class="codex-stat-value">${profile.realm_level}</span></div>`;
    if (profile.weapon && profile.weapon !== "Tidak Ada") html += `<div class="codex-stat"><span class="codex-stat-label">Senjata</span><span class="codex-stat-value">${esc(profile.weapon)}</span></div>`;
    if (profile.element && profile.element !== "tidak ada") html += `<div class="codex-stat"><span class="codex-stat-label">Elemen</span><span class="codex-stat-value">${esc(profile.element)}</span></div>`;
    html += `</div></div>`;
    
    if (profile.hp_max || profile.qi_max) {
      html += `<div class="codex-detail-section">`;
      html += `<h3>${icon("heart")}Kekuatan</h3>`;
      html += `<div class="codex-stat-grid">`;
      if (profile.hp_max) html += `<div class="codex-stat"><span class="codex-stat-label">HP</span><span class="codex-stat-value">${profile.hp_max}</span></div>`;
      if (profile.qi_max) html += `<div class="codex-stat"><span class="codex-stat-label">Qi</span><span class="codex-stat-value">${profile.qi_max}</span></div>`;
      html += `</div></div>`;
    }
  }
  
  if (revealLevel >= 4) {
    html += `<div class="codex-detail-section">`;
    html += `<h3>${icon("landmark")}Lainnya</h3>`;
    html += `<div class="codex-stat-grid">`;
    if (profile.faction) html += `<div class="codex-stat"><span class="codex-stat-label">Faksi</span><span class="codex-stat-value">${esc(profile.faction)}</span></div>`;
    if (profile.companion) html += `<div class="codex-stat"><span class="codex-stat-label">Kawan</span><span class="codex-stat-value">${esc(profile.companion)}</span></div>`;
    html += `</div></div>`;
  }
  
  if (revealLevel < 4) {
    html += `<div class="codex-detail-section codex-locked">`;
    html += `<p>${icon("lock")}Tingkatkan hubungan untuk membuka lebih banyak informasi.</p>`;
    html += `</div>`;
  }
  
  html += `</div></div></div>`;
  
  // Close existing overlay and show detail
  const existing = document.querySelector(".codex-overlay");
  if (existing) existing.remove();
  
  const overlay = document.createElement("div");
  overlay.innerHTML = html;
  document.body.appendChild(overlay.firstElementChild);
}

// ---------- kolom tengah ----------

// B4: log dengan perlakuan speaker & separator antar-scene (berbasis waktu game)
function renderLog(v) {
  let html = "";
  let prev = null;
  v.log.forEach((e) => {
    const scene = prev && (e.day !== prev.day || e.hour !== prev.hour);
    const cls = `log-entry log-${esc(e.type)}${scene ? " log-scene" : ""}`;
    // deteksi baris percakapan: hanya tipe npc/player yang jadi speaker line
    // (system/narration/battle TIDAK — mis. "Quest utama diperbarui: ..." bukan dialog)
    const isTalk = e.type === "npc" || e.type === "player";
    const m = isTalk ? /^([^:\n]{2,24}):\s?/.exec(e.text) : null;
    const speaker = m
      ? `<span class="log-speaker-label">${esc(m[1])}</span>: ${esc(e.text.slice(m[0].length))}`
      : esc(e.text);
    html += `<div class="${cls}${m ? " speaker-line" : ""}">${speaker}</div>`;
    prev = e;
  });
  $("log").innerHTML = html;
}

function renderCenter(v, c) {
  renderLog(v);

  const box = $("interact");
  if (v.mode === "dialog") renderDialog(v, box);
  else if (v.mode === "battle") renderBattle(v, c, box);
  else if (v.mode === "choose") renderChoose(v, box);
  else renderExplore(v, c, box);
}

// B9: indikator loading — tombol sumber dinonaktifkan + label "Memproses…" (tanpa animasi)
function setLoading(on) {
  const btns = document.querySelectorAll("button, .choice-btn");
  btns.forEach((b) => { b.disabled = on; });
  document.body.classList.toggle("is-loading", on);
}

async function act(action) {
  if (busy) return;
  busy = true;
  setLoading(true);
  closeTianyuan();
  try {
    const prevState = view ? JSON.parse(JSON.stringify(view)) : null;
    const data = await api("/api/action", { body: { action } });
    if (data.ok) {
      const prevBattle = prevState;
      view = data.view; ctx = data.context;
      detectBattleChanges(prevBattle, view);
      checkAchievements(view);
      render();
      if (data.error) window.alert(data.error);  // penolakan aksi (guard dialog/battle, dll)
    }
    else { window.alert(data.error || "Aksi ditolak."); }
  } finally { busy = false; setLoading(false); }
}

// ---------- explore ----------

function renderExplore(v, c, box) {
  const loc = v.location;
  let html = `<div class="interact-box"><p class="hint">${esc(loc.description)}</p>`;
  html += `<h3 class="stat-title">Kau bisa</h3>`;

  // NPC di lokasi
  (c.npcs || []).forEach((n) => {
    const tag = n.can_spar ? " (sparing)" : n.shop ? " (toko)" : "";
    const npcAvatar = n.avatar ? `<img src="${esc(n.avatar)}" style="width:24px;height:24px;border-radius:50%;object-fit:cover;vertical-align:middle;margin-right:4px;" onerror="this.style.display='none'">` : "";
    html += `<div class="action-row"><button class="btn" onclick='act({type:"talk",npc:"${n.id}"})'>${npcAvatar}${icon("message-circle")}Bicara ${esc(n.name)}${tag}</button></div>`;
    if (n.can_spar) {
      html += `<div class="action-row"><button class="btn" onclick='act({type:"spar",npc:"${n.id}"})'>Sparring vs ${esc(n.name)}</button></div>`;
    }
  });

  // Toko Pedagang (jika ada)
  if (c.merchant_shop) {
    html += `<div class="action-row"><button class="btn btn-gold" onclick="openShop()">Buka Toko Pedagang</button></div>`;
  }

  // tujuan
  (loc.connections || []).forEach((cid) => {
    html += `<div class="action-row"><button class="btn" onclick='act({type:"move",to:"${cid}"})'>${icon("map-pin")}Pindah → ${esc(ctx.loc_names[cid] || cid)}</button></div>`;
  });

  // wilayah berburu (data-driven — multi-zona; kirim hunt id agar zona eksplisit)
  const huntsHere = (c.hunts || []).filter((h) => h.location === loc.id);
  if (huntsHere.length) {
    huntsHere.forEach((h) => {
      const searchLabel = h.search_item_name ? `Cari ${h.search_item_name.split(",")[0].trim()}` : "Cari";
      html += `<div class="action-row"><button class="btn" onclick='act({type:"hunt",hunt:"${esc(h.id)}"})'>${esc(h.name || "Berburu")}</button>` +
              `<button class="btn" onclick='act({type:"search"})'>${esc(searchLabel)}</button></div>`;
    });
  }

  // menambang (unsafe locations with mines)
  if (!loc.is_safe) {
    html += `<div class="action-row"><button class="btn" onclick='act({type:"mine"})'>${icon("pickaxe")}Menambang</button></div>`;
  }

  // lokasi aman
  if (loc.is_safe) {
    // meditasi hanya setelah pelajaran pertama selesai
    const flags = (ctx && ctx.flags) || {};
    const canMeditate = flags.flag_first_lesson_done === true;
    if (canMeditate) {
      html += `<div class="action-row"><span class="action-label">Meditasi:</span>` +
              `<button class="btn" onclick='act({type:"meditate"})'>Meditasi</button>`;
      // istirahat hanya di kamar pemain
      if (v.player.is_rest_location) {
        html += `<button class="btn" onclick='act({type:"rest"})'>Istirahat</button>`;
      }
      html += `</div>`;
    }
    // meracik (crafting)
    const ownedRecipes = v.recipes || [];
    if (ownedRecipes.length) {
      html += `<div class="action-row"><span class="action-label">Meracik:</span>` +
              `<select id="sel-craft">${ownedRecipes.map((r) => {
                const ings = r.ingredients.map(i => `${i.count}×${esc(i.name || i.item)}`).join("+");
                return `<option value="${r.id}">${esc(r.name)} (${ings})</option>`;
              }).join("")}</select>` +
              `<button class="btn" onclick='act({type:"craft",recipe:$("sel-craft").value})'>Meracik</button></div>`;
    }
    // C1: tingkatkan teknik yang dimiliki
    if (c.techniques && c.techniques.length) {
      html += `<div class="action-row"><span class="action-label">Tingkatkan teknik:</span>` +
              `<select id="sel-upgrade">${c.techniques.map((t) => `<option value="${t.id}">${esc(t.name)} (Lv.${t.level})</option>`).join("")}</select>` +
              `<button class="btn" onclick='act({type:"upgrade_technique",technique:$("sel-upgrade").value})'>Tingkatkan</button></div>`;
    }
    html += `<div class="action-row"><span class="action-label">Simpan (nama):</span>` +
            `<input type="text" id="inp-save" value="save1">` +
            `<button class="btn" onclick='act({type:"save",save_name:$("inp-save").value})'>Simpan</button></div>`;
  }

  // pakai item (consumable)
  const consumables = (v.inventory || []).filter((i) => i.type === "consumable");
  if (consumables.length) {
    html += `<div class="action-row"><span class="action-label">Pakai:</span>` +
            `<select id="sel-use">${consumables.map((i) => `<option value="${i.id}">${esc(i.name)} (×${i.count})</option>`).join("")}</select>` +
            `<button class="btn" onclick='act({type:"use_item",item:$("sel-use").value})'>Pakai</button></div>`;
  }

  // gunakan kunci (key_item)
  const keyItems = (v.inventory || []).filter((i) => i.type === "key_item");
  if (keyItems.length) {
    html += `<div class="action-row"><span class="action-label">Kunci:</span>` +
            `<select id="sel-key">${keyItems.map((i) => `<option value="${i.id}">${esc(i.name)} (×${i.count})</option>`).join("")}</select>` +
            `<button class="btn" onclick='act({type:"use_key_item",item:$("sel-key").value})'>Gunakan</button></div>`;
  }

  // racik (hanya di lokasi aman)
  if (loc.is_safe && c.recipes && c.recipes.length) {
    const invMap = {};
    (v.inventory || []).forEach((i) => { invMap[i.id] = i.count; });

    const availableRecipes = c.recipes.filter((r) => {
      return r.ingredients.every((ing) => (invMap[ing.item] || 0) >= ing.count);
    });

    if (availableRecipes.length) {
      let craftHtml = `<div class="action-row"><span class="action-label">Racik:</span>`;
      availableRecipes.forEach((r) => {
        const ingText = r.ingredients.map((ing) => `${ing.count} ${ing.name}`).join(", ");
        craftHtml += `<button class="btn" onclick='act({type:"craft",recipe:"${r.id}"})'>` +
                     `Racik ${esc(r.result_name)} (${esc(ingText)})</button> `;
      });
      craftHtml += `</div>`;
      html += craftHtml;
    }
  }

  // pasang senjata
  const weapons = (v.inventory || []).filter((i) => i.type === "weapon");
  if (weapons.length) {
    html += `<div class="action-row"><span class="action-label">Pasang:</span>` +
            `<select id="sel-weapon">${weapons.map((i) => `<option value="${i.id}">${esc(i.name)}</option>`).join("")}</select>` +
            `<button class="btn" onclick='act({type:"equip",item:$("sel-weapon").value})'>Pasang</button></div>`;
  }

  // ingatan
  if (v.memories && v.memories.length) {
    html += `<div class="action-row"><button class="btn" onclick="openTianyuan()">${icon("book-open")}Baca Ingatan</button></div>`;
  }

  html += `</div>`;
  box.innerHTML = html;
}

// ---------- dialog ----------

function renderDialog(v, box) {
  const d = v.dialog;
  if (!d) { box.innerHTML = ""; return; }
  const npcNames = (ctx && ctx.npc_names) || {};
  const npcAvatars = (ctx && ctx.npc_avatars) || {};
  let speaker = d.speaker;
  let speakerNpcId = null;
  if (speaker.startsWith("npc:")) {
    speakerNpcId = speaker.slice(4);
    speaker = npcNames[speakerNpcId] || speakerNpcId;
  }
  else if (speaker === "narration") speaker = "Narasi";
  
  let html = `<div class="interact-box">`;
  const avatarPath = speakerNpcId ? npcAvatars[speakerNpcId] : null;
  if (speaker === "Narasi") {
    html += `<div class="dialog-speaker-row"><div class="dialog-speaker">${esc(speaker)}</div></div>`;
  } else if (avatarPath) {
    html += `<div class="dialog-speaker-row"><img src="${esc(avatarPath)}" style="width:48px;height:48px;border-radius:50%;object-fit:cover;border:2px solid var(--gold);margin-right:8px;" onerror="this.style.display='none'"><div class="dialog-speaker">${esc(speaker)}</div></div>`;
  } else {
    html += `<div class="dialog-speaker-row"><div class="seal seal-ghost seal-sm">${esc(speaker[0])}</div><div class="dialog-speaker">${esc(speaker)}</div></div>`;
  }
  
  const dlgCls = speaker === "Narasi" ? "dialog-text" : "dialog-text npc-dialog";
  html += `<div class="${dlgCls}" id="dlg-text-live"></div>`;
  if (d.choices && d.choices.length) {
    d.choices.forEach((c) => {
      html += `<button class="choice-btn" onclick='act({type:"dialog_choice",choice_index:${c.index}})'><span class="seal seal-sm">${c.index + 1}</span> ${esc(c.label)}</button>`;
    });
  } else {
    html += `<button class="btn btn-gold" onclick='act({type:"dialog_choice",choice_index:-1})'>Lanjut</button>`;
  }
  html += `</div>`;
  box.innerHTML = html;
  typewriter($("dlg-text-live"), d.text, 20);
}

// ---------- battle ----------

function renderBattle(v, c, box) {
  const b = v.battle;
  if (!b) { box.innerHTML = ""; return; }
  const p = b.player;
  let html = `<div class="interact-box">`;
  html += `<div class="dialog-speaker-row"><div class="dialog-speaker">⚔ Pertarungan</div></div>`;
  
  const pct = (hp, max) => max > 0 ? Math.max(0, Math.min(100, Math.round((hp / max) * 100))) : 0;
  
  // Player
  html += `<div class="combatant-card ally">
    <span class="c-name">Kau</span>
    <div class="c-bar"><div class="stat-bar-track"><div class="stat-bar-fill hp" data-target="${pct(p.hp, p.hp_max)}%" style="width:${pct(p.hp, p.hp_max)}%"></div></div></div>
  </div>`;
  
  // Companion
  if (b.companion) {
    html += `<div class="combatant-card ally">
      <span class="c-name">${esc(b.companion.name)}</span>
      <div class="c-bar"><div class="stat-bar-track"><div class="stat-bar-fill hp" data-target="${pct(b.companion.hp, b.companion.hp_max)}%" style="width:${pct(b.companion.hp, b.companion.hp_max)}%"></div></div></div>
    </div>`;
  }
  
  // Sekutu ujian kelompok
  if (b.allies && b.allies.length) {
    const allyIdx = b.active_ally_index;
    b.allies.forEach((a, i) => {
      const activeCls = i === allyIdx ? " ally-active" : "";
      html += `<div class="combatant-card ally${activeCls}">
        <span class="c-name">${esc(a.name)}</span>
        <div class="c-bar"><div class="stat-bar-track"><div class="stat-bar-fill hp" data-target="${pct(a.hp, a.hp_max)}%" style="width:${pct(a.hp, a.hp_max)}%"></div></div></div>
      </div>`;
    });
  }
  
  // Foes
  b.foes.forEach((f) => {
    html += `<div class="combatant-card foe">
      <span class="c-name">${esc(f.name)}</span>
      <div class="c-bar"><div class="stat-bar-track"><div class="stat-bar-fill hp" data-target="${pct(f.hp, f.hp_max)}%" style="width:${pct(f.hp, f.hp_max)}%"></div></div></div>
    </div>`;
  });
  
  html += `<div class="action-row" style="margin-top: 15px;"><button class="btn" onclick='act({type:"battle_action",action:"attack"})'>${icon("sword")}Serang</button>` +
          `<button class="btn" onclick='act({type:"battle_action",action:"guard"})'>${icon("shield")}Bertahan</button>` +
          `<button class="btn" onclick='act({type:"battle_action",action:"flee"})'>${icon("x")}Kabur</button></div>`;

  // teknik
  if (c.techniques && c.techniques.length) {
    const qi = p.qi;
    const usable = c.techniques.filter((t) => t.qi_cost <= qi);
    if (usable.length) {
      html += `<div class="action-row"><span class="action-label">Teknik:</span>` +
              `<select id="sel-tek">${usable.map((t) => `<option value="${t.id}">${esc(t.name)} (Qi ${t.qi_cost})</option>`).join("")}</select>` +
              `<button class="btn" onclick='act({type:"battle_action",action:"technique",technique:$("sel-tek").value})'>Gunakan</button></div>`;
    }
  }

  // item
  const consumables = (v.inventory || []).filter((i) => i.type === "consumable");
  if (consumables.length) {
    html += `<div class="action-row"><span class="action-label">Item:</span>` +
            `<select id="sel-item">${consumables.map((i) => `<option value="${i.id}">${esc(i.name)} (×${i.count})</option>`).join("")}</select>` +
            `<button class="btn" onclick='act({type:"battle_action",action:"item",item:$("sel-item").value})'>Pakai</button></div>`;
  }
  html += `</div>`;
  box.innerHTML = html;
}

// ---------- choose ----------

function renderChoose(v, box) {
  const ch = v.choose;
  if (!ch) { box.innerHTML = ""; return; }
  let html = `<div class="interact-box"><div class="dialog-speaker-row"><div class="dialog-speaker">Pilihan</div></div>`;
  html += `<div class="dialog-text">${esc(ch.prompt)}</div>`;
  ch.options.forEach((o, i) => {
    html += `<button class="choice-btn" onclick='act({type:"choose",option:"${o.value}"})'><span class="seal seal-sm">${i + 1}</span> ${esc(o.label)}</button>`;
  });
  html += `</div>`;
  box.innerHTML = html;
}

// ---------- Modals (Shop & Arc Summary) ----------

let currentShopTab = "buy";

function openShop() {
  currentShopTab = "buy";
  renderShop();
  showModal("modal-shop");
}

function renderShop() {
  if (!ctx || !ctx.merchant_shop) return;
  const s = ctx.merchant_shop;
  const p = view.player;
  const invMap = {};
  (view.inventory || []).forEach((i) => { invMap[i.id] = i.count; });
  
  let html = `<h3>Toko: ${esc(s.merchant_name)}</h3>`;
  html += `<div style="margin-bottom: 12px; font-size: 14px;">Koin Emas: <span style="color:var(--gold)">${p.gold}</span></div>`;
  
  html += `<div class="shop-tabs">
    <div class="shop-tab ${currentShopTab === 'buy' ? 'active' : ''}" onclick="currentShopTab='buy';renderShop()">Beli</div>
    <div class="shop-tab ${currentShopTab === 'sell' ? 'active' : ''}" onclick="currentShopTab='sell';renderShop()">Jual</div>
  </div>`;
  
  html += `<div>`;
  if (currentShopTab === "buy") {
    s.buy.forEach(item => {
      const disabled = p.gold < item.price ? "disabled" : "";
      html += `<div class="shop-item-row">
        <div class="shop-item-info">
          <span class="item-name">${esc(item.name)}</span>
          <span class="shop-item-price">${item.price} Emas</span>
        </div>
        <button class="btn btn-small" ${disabled} onclick="actShop('shop_buy', '${item.item}')">Beli (1×)</button>
      </div>`;
    });
  } else {
    const owned = s.sell.filter(i => (invMap[i.item] || 0) >= 1);
    if (owned.length < s.sell.length) {
      html += `<p class="hint" style="margin-bottom:10px">Pedagang hanya membeli bahan yang kamu punya — item tanpa tombol berarti belum kamu miliki (dapatkan dari berburu / mencari herba).</p>`;
    }
    s.sell.forEach(item => {
      const count = invMap[item.item] || 0;
      if (count < 1) {
        html += `<div class="shop-item-row shop-item-empty">
          <div class="shop-item-info">
            <span class="item-name">${esc(item.name)}</span>
            <span class="shop-item-price">${item.price} Emas</span>
          </div>
          <span class="shop-item-soldout">Belum punya</span>
        </div>`;
      } else {
        html += `<div class="shop-item-row">
          <div class="shop-item-info">
            <span class="item-name">${esc(item.name)} (Punya: ${count})</span>
            <span class="shop-item-price">${item.price} Emas</span>
          </div>
          <button class="btn btn-small" onclick="actShop('shop_sell', '${item.item}')">Jual (1×)</button>
        </div>`;
      }
    });
  }
  html += `</div>`;
  html += `<div style="margin-top:20px; text-align:right;"><button class="btn" onclick="closeModal('modal-shop')">Tutup</button></div>`;
  
  $("modal-shop").innerHTML = html;
}

async function actShop(type, itemId) {
  if (busy) return;
  busy = true;
  setLoading(true);
  try {
    const data = await api("/api/action", { body: { action: { type: type, item: itemId, count: 1 } } });
    if (data.ok) {
      view = data.view; ctx = data.context; render(); renderShop();
      if (data.error) window.alert(data.error);  // penolakan aksi
    }
    else { window.alert(data.error || "Aksi ditolak."); }
  } finally { busy = false; setLoading(false); }
}

function openArcSummaryModal(s) {
  let html = `<h3 style="text-align:center; font-size: 24px;">${esc(s.title)}</h3>`;
  html += `<div style="margin-bottom: 20px;">
    ${statRow("Kultivator", s.player_name)}
    ${statRow("Ranah", `${s.realm} Lv.${s.realm_level}`)}
    ${statRow("Akademi", s.academy || "—")}
    ${statRow("Moralitas", s.morality)}
    ${statRow("Ingatan Terbuka", s.memories_unlocked)}
    ${statRow("Waktu Berlalu", `Hari ${s.day}`)}
    ${statRow("Pilihan Akhir", s.branch, "gold")}
  </div>`;
  if (s.ending) {
    html += `<div class="dialog-text" style="text-align:center; margin-bottom: 12px;">` +
            `<span style="color:var(--gold); font-size: 18px;">Ending: ${esc(s.ending.title)}</span><br>` +
            `${esc(s.ending.desc)}</div>`;
  }
  html += `<div class="dialog-text" style="font-style:italic; color:var(--gray); text-align:center; margin-bottom: 24px;">"${esc(s.teaser)}"</div>`;
  html += `<button class="btn btn-gold" style="width:100%" onclick="dismissArcSummary()">Lanjut Eksplorasi Bebas</button>`;
  
  $("modal-arc-summary").innerHTML = html;
  showModal("modal-arc-summary");
}

function dismissArcSummary() {
  localStorage.setItem("arc-seen:" + currentSave,
                      (view && view.arc_summary && view.arc_summary.title) || "1");
  closeModal("modal-arc-summary");
  render();
}

// ---------- B6: drawer mobile untuk panel kanan (quest/inventori/ingatan) ----------
// D1 (2026-08-15): overlay fade selaras geser drawer (lihat style.css @media 1023px,
// harus sama persis dengan durasi transform/opacity 0.22s di sana)
const DRAWER_TRANSITION_MS = 220;

function toggleRightDrawer() {
  const el = $("col-right");
  const open = el.classList.toggle("drawer-open");
  let ov = $("drawer-overlay");
  if (open) {
    if (!ov) {
      ov = document.createElement("div");
      ov.id = "drawer-overlay";
      ov.addEventListener("click", closeRightDrawer);
      document.body.appendChild(ov);
    }
    ov.classList.remove("hidden");
    requestAnimationFrame(() => ov.classList.add("drawer-visible"));
  } else {
    closeRightDrawer();
  }
}

function closeRightDrawer() {
  const el = $("col-right");
  if (el) el.classList.remove("drawer-open");
  const ov = $("drawer-overlay");
  if (ov) {
    ov.classList.remove("drawer-visible");
    setTimeout(() => {
      if (!ov.classList.contains("drawer-visible")) ov.classList.add("hidden");
    }, DRAWER_TRANSITION_MS);
  }
}

// ---------- panel Tianyuan Ling ----------

async function openTianyuan() {
  const data = await api("/api/tianyuan", { method: "GET" });
  const t = data.tianyuan;
  const meta = (ctx && ctx.meta) || {};
  let html = `<h3>${esc(meta.title || "天缘灵")} · ${esc(meta.panel || "Tianyuan Ling")}</h3>`;
  
  html += `<h3 style="margin-top:18px;font-size:15px">Status Misi</h3>`;
  if (t.mission.main) {
    html += `<div class="mem-full"><div class="mem-title">[Misi Utama] ${esc(t.mission.main.title)}</div>` +
            `<div class="mem-text">${esc(t.mission.main.objective)}</div></div>`;
  } else {
    html += `<p class="hint">[Misi Utama] Belum ada misi utama aktif (Eksplorasi Bebas).</p>`;
  }
  if (t.mission.side_quests && t.mission.side_quests.length) {
    t.mission.side_quests.forEach(sq => {
      html += `<div class="mem-full"><div class="mem-title" style="color:var(--blue)">[Misi Sampingan] ${esc(sq.title)}</div>` +
              `<div class="mem-text">${esc(sq.objective)}</div></div>`;
    });
  }
  
  html += `<h3 style="margin-top:18px;font-size:15px">Ingatan (${t.unlocked_count}/${t.total_count})</h3>`;
  if (t.memories && t.memories.length) {
    t.memories.forEach((m) => {
      if (m.unlocked) {
        const rel = (m.reliability && m.reliability !== "unknown")
          ? ` <span class="badge badge-reliability">${esc(m.reliability)}</span>` : "";
        html += `<div class="mem-full"><div class="mem-title">${esc(m.title)}${rel}</div>` +
                `<div class="mem-text">${esc(m.text)}</div></div>`;
      } else {
        html += `<div class="mem-locked">• ${esc(m.title)} (Belum Terbuka)</div>`;
      }
    });
  }
  
  html += `<h3 style="margin-top:18px;font-size:15px">Log Sistem</h3>`;
  (t.system_log || []).reverse().forEach((s) => {
    html += `<div class="sys-log-entry">${esc(s)}</div>`;
  });
  
  html += `<div style="margin-top:20px"><button class="btn btn-gold" onclick="closeTianyuan()">Tutup</button></div>`;
  $("tianyuan").innerHTML = html;
  $("tianyuan").classList.remove("hidden");
  requestAnimationFrame(() => {
    $("tianyuan").classList.add("tianyuan-open");
  });
}

function closeTianyuan() { 
  $("tianyuan").classList.remove("tianyuan-open");
  setTimeout(() => {
    if (!$("tianyuan").classList.contains("tianyuan-open")) {
      $("tianyuan").classList.add("hidden");
    }
  }, DRAWER_TRANSITION_MS);
}

// ---------- inisialisasi ----------

$("btn-new").onclick = () => { AudioManager.start(); startNew(); };
$("btn-tianyuan").onclick = openTianyuan;
refreshSaveSlots();
loadIcons();  // C2: icon Lucide self-host — dimuat async, re-render bila sudah masuk

// judul data-driven dari config.web — di-fetch sekali saat halaman dimuat
// (bekerja tanpa sesi: context.meta selalu ada di /api/state)
(async () => {
  const metaData = await api("/api/state", { method: "GET" });
  if (metaData.ok && metaData.context) applyMeta(metaData.context.meta);
})();

// ---------- Audio Controls Event Handlers ----------

function setupAudioControls() {
  // Title screen controls
  const muteBtn = $("btn-audio-mute");
  const volumeSlider = $("audio-volume");
  
  // Topbar controls
  const muteBtnTopbar = $("btn-audio-mute-topbar");
  const volumeSliderTopbar = $("audio-volume-topbar");

  function onMuteClick() {
    AudioManager.toggleMute();
  }

  function onVolumeChange(e) {
    const v = parseFloat(e.target.value);
    AudioManager.setVolume(v);
    // Sync both sliders
    if (volumeSlider) volumeSlider.value = v;
    if (volumeSliderTopbar) volumeSliderTopbar.value = v;
    const label = $("audio-volume-label");
    const labelTopbar = $("audio-volume-label-topbar");
    if (label) label.textContent = Math.round(v * 100) + "%";
    if (labelTopbar) labelTopbar.textContent = Math.round(v * 100) + "%";
  }

  if (muteBtn) muteBtn.addEventListener("click", onMuteClick);
  if (muteBtnTopbar) muteBtnTopbar.addEventListener("click", onMuteClick);
  if (volumeSlider) volumeSlider.addEventListener("input", onVolumeChange);
  if (volumeSliderTopbar) volumeSliderTopbar.addEventListener("input", onVolumeChange);

  // Keyboard accessibility: Enter/Space on mute button
  [muteBtn, muteBtnTopbar].forEach((btn) => {
    if (!btn) return;
    btn.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        onMuteClick();
      }
    });
  });
}

// Initialize audio controls after DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", setupAudioControls);
} else {
  setupAudioControls();
}

function typewriter(el, text, speed) {
  speed = speed || 22;
  el.textContent = "";
  let i = 0;
  let cursor = document.createElement("span");
  cursor.className = "tw-cursor";
  function step() {
    if (!el.isConnected) return; // Prevent memory leak when DOM updates
    if (i <= text.length) {
      el.textContent = text.slice(0, i);
      el.appendChild(cursor);
      i++;
      setTimeout(step, speed);
    } else {
      cursor.remove();
    }
  }
  step();
}

// ═══ GAP-C2: Battle Animation System ═══

let lastBattleState = null;
let battleAnimQueue = [];

function animateDamage(element, type, value) {
  const dmg = document.createElement("span");
  dmg.className = "damage-number " + type;
  if (type === "miss") dmg.textContent = "Miss";
  else if (type === "heal") dmg.textContent = "+" + value;
  else dmg.textContent = "-" + value;
  element.style.position = "relative";
  element.appendChild(dmg);
  setTimeout(() => dmg.remove(), 1000);
}

function animateCardHit(element, type) {
  element.classList.remove("hit", "healed");
  void element.offsetWidth;
  element.classList.add(type === "heal" ? "healed" : "hit");
  setTimeout(() => element.classList.remove("hit", "healed"), 500);
}

function animateHpBar(element, isDamage) {
  element.classList.remove("damage", "heal");
  void element.offsetWidth;
  element.classList.add(isDamage ? "damage" : "heal");
  setTimeout(() => element.classList.remove("damage", "heal"), 600);
}

function detectBattleChanges(oldState, newState) {
  if (!oldState || !newState || !newState.battle) return;
  const nb = newState.battle;
  const ob = oldState.battle;
  if (!ob) return;

  // Player HP change
  if (ob.player.hp !== nb.player.hp) {
    const card = document.querySelector(".combatant-card.ally");
    const bar = card ? card.querySelector(".stat-bar-fill") : null;
    if (bar) animateHpBar(bar, nb.player.hp < ob.player.hp);
    if (card) animateCardHit(card, nb.player.hp < ob.player.hp ? "damage" : "heal");
    const val = Math.abs(nb.player.hp - ob.player.hp);
    const type = nb.player.hp < ob.player.hp ? "damage" : "heal";
    if (card) animateDamage(card, type, val);
  }

  // Foe HP changes
  (nb.foes || []).forEach((nf, idx) => {
    const of_ = (ob.foes || [])[idx];
    if (!of_ || of_.hp === nf.hp) return;
    const cards = document.querySelectorAll(".combatant-card.foe");
    const card = cards[idx];
    if (!card) return;
    const bar = card.querySelector(".stat-bar-fill");
    if (bar) animateHpBar(bar, nf.hp < of_.hp);
    animateCardHit(card, "damage");
    const val = Math.abs(nf.hp - of_.hp);
    animateDamage(card, "damage", val);
  });

  // Perubahan HP sekutu tim; kartu ally pertama adalah pemain.
  (nb.allies || []).forEach((na, idx) => {
    const oa = (ob.allies || [])[idx];
    if (!oa || oa.hp === na.hp) return;
    const allyCards = document.querySelectorAll(".combatant-card.ally");
    const card = allyCards[idx + (nb.companion ? 2 : 1)];
    if (!card) return;
    const bar = card.querySelector(".stat-bar-fill");
    const isDmg = na.hp < oa.hp;
    if (bar) animateHpBar(bar, isDmg);
    animateCardHit(card, isDmg ? "damage" : "heal");
    animateDamage(card, isDmg ? "damage" : "heal", Math.abs(na.hp - oa.hp));
  });
}

// Patch act() to capture pre-action state
const _origAct = typeof act === "function" ? act : null;

// ═══ GAP-C3: Achievement System ═══

const ACHIEVEMENTS = {
  "first_battle": { icon: "⚔️", title: "Pejuang Pertama", desc: "Menyelesaikan pertarungan pertama" },
  "first_memory": { icon: "🧠", title: "Ingatan Kembali", desc: "Membuka ingatan pertama" },
  "arc_complete_1": { icon: "📜", title: "Lulusan Akademi", desc: "Menyelesaikan Arc I" },
  "arc_complete_all": { icon: "🏆", title: "Kultivator Sejati", desc: "Menyelesaikan ketujuh Arc" },
  "friendship_max": { icon: "💎", title: "Sahabat Sejati", desc: "Mencapai kedekatan maksimal dengan NPC" },
  "faction_leader": { icon: "👑", title: "Pemimpin Faksi", desc: "Mencapai reputasi tinggi dengan faksi" },
  "memory_investigator": { icon: "🔍", title: "Peneliti Ingatan", desc: "Menyelidiki 3 ingatan berbeda" },
  "hidden_ending": { icon: "🌟", title: "Second Life", desc: "Mencapai ending tersembunyi" },
};

let unlockedAchievements = new Set();

function checkAchievements(v) {
  if (!v) return;
  const newUnlocks = [];

  // first_battle
  if (!unlockedAchievements.has("first_battle") && v.battle && v.battle.foes && v.battle.foes.length > 0) {
    unlockedAchievements.add("first_battle");
    newUnlocks.push("first_battle");
  }

  // first_memory
  if (!unlockedAchievements.has("first_memory") && v.memories && v.memories.length > 0) {
    unlockedAchievements.add("first_memory");
    newUnlocks.push("first_memory");
  }

  // arc_complete_1
  if (!unlockedAchievements.has("arc_complete_1") && v.completed_quests && v.completed_quests.includes("quest_a01_c05_005")) {
    unlockedAchievements.add("arc_complete_1");
    newUnlocks.push("arc_complete_1");
  }

  // arc_complete_all
  if (!unlockedAchievements.has("arc_complete_all") && v.flags && v.flags["state_ending_achieved"]) {
    unlockedAchievements.add("arc_complete_all");
    newUnlocks.push("arc_complete_all");
  }

  // memory_investigator
  if (!unlockedAchievements.has("memory_investigator")) {
    let investigated = 0;
    if (v.flags) {
      Object.keys(v.flags).forEach(k => {
        if (k.startsWith("state_memory_") && k.endsWith("_reinterpretation")) investigated++;
      });
    }
    if (investigated >= 3) {
      unlockedAchievements.add("memory_investigator");
      newUnlocks.push("memory_investigator");
    }
  }

  newUnlocks.forEach(id => showAchievement(id));
}

function showAchievement(id) {
  const a = ACHIEVEMENTS[id];
  if (!a) return;
  const popup = document.createElement("div");
  popup.className = "achievement-popup";
  popup.innerHTML = `<div class="achievement-icon">${a.icon}</div><div class="achievement-title">PENCAPAIAN TERBUKA</div><div class="achievement-name">${a.title}</div><div class="achievement-desc">${a.desc}</div>`;
  document.body.appendChild(popup);
  setTimeout(() => {
    popup.classList.add("hiding");
    setTimeout(() => popup.remove(), 500);
  }, 4000);
}
