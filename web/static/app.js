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

    // Error handling — graceful degradation
    audio.addEventListener("error", (e) => {
      console.warn("[AudioManager] Audio load error:", e);
      audio = null; // prevent further attempts
    });

    // Update UI after init
    updateUI();
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

function showModal(id) {
  $(id).classList.remove("hidden");
  $("modal-overlay").classList.remove("hidden");
  lastFocus = document.activeElement;
  const first = $(id).querySelector("button, a, input, select");
  if (first) first.focus();
}
function closeModal(id) {
  $(id).classList.add("hidden");
  $("modal-overlay").classList.add("hidden");
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
  const names = ["heart", "sparkles", "sword", "shield", "backpack", "scroll-text",
                 "book-open", "map-pin", "message-circle", "save", "x", "flame",
                 "orbit", "target", "circle-check"];
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
  $("title-screen").classList.add("hidden");
  $("game-screen").classList.remove("hidden");
}

async function startNew() {
  const data = await api("/api/new");
  if (data.ok) { currentSave = "save1"; view = data.view; ctx = data.context; showGame(); render(); }
  else { window.alert(data.error || "Gagal memulai."); }
}

async function loadGame(name) {
  const data = await api("/api/load", { body: { name } });
  if (!data.ok) { $("title-msg").textContent = data.error || "Gagal memuat."; return; }
  currentSave = name; view = data.view; ctx = data.context; showGame(); render();
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

  if (view.arc_summary && localStorage.getItem("arc-seen:" + currentSave) !== "1") {
    openArcSummaryModal(view.arc_summary);
  }
}

function renderHeader(v) {
  const loc = v.location;
  $("header-title").textContent =
    `Bulan ${v.month} — Hari ${v.day}, jam ${String(v.hour).padStart(2, "0")}:00 — ${loc.name}`;
}

function statRow(label, value, cls) {
  // Label boleh mengandung icon SVG dari icon() — aman (bukan input pemain).
  // Escape hanya segmen TEKS; markup <svg>...</svg> dibiarkan utuh agar tampil
  // sebagai ikon, bukan teks mentah (bug: seluruh label di-esc → SVG bocor).
  const labelHtml = String(label ?? "").split(/(<svg[\s\S]*?<\/svg>)/g)
    .map((part) => part.startsWith("<svg") ? part : esc(part)).join("");
  return `<div class="stat-row"><span class="stat-label">${labelHtml}</span>` +
         `<span class="stat-value ${cls || ""}">${esc(value)}</span></div>`;
}

// B3: Ranah = hero stat dengan progress exp statis (bukan cuma 1 row kecil)
function renderLeft(v) {
  const p = v.player;
  const names = (ctx && ctx.item_names) || {};
  const wid = p.equipment && p.equipment.weapon;
  const w = wid ? (names[wid] || wid) : "—";
  const comp = v.companion;
  let html = `<div style="text-align: center; margin-bottom: 16px;">
    <img src="/static/assets/img/avatar.jpg" alt="Avatar" style="width: 120px; height: 120px; border-radius: 50%; border: 2px solid var(--gold); object-fit: cover; box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);">
  </div>`;
  html += `<h3 class="stat-title" style="text-align: center; border-bottom: none;">✦ ${esc(p.name)} ✦</h3>`;
  const pct = p.exp_next > 0 ? Math.min(100, Math.round((p.exp / p.exp_next) * 100)) : 0;
  const ic = icon;
  html += `<div class="realm-hero">`;
  html += `<span class="realm-name">${esc(p.realm)}</span>`;
  html += `<span class="realm-level">Lv.${p.realm_level}</span>`;
  html += `<div class="progress-track"><div class="progress-fill" style="width:${pct}%"></div></div>`;
  html += `<div class="progress-caption">${p.exp}/${p.exp_next} EXP</div>`;
  html += `</div>`;
  html += statRow(ic("heart") + "HP", `${p.hp}/${p.hp_max}`, p.hp < p.hp_max ? "red" : "");
  html += statRow(ic("sparkles") + "Qi", `${p.qi}/${p.qi_max}`, "blue");
  html += statRow(ic("orbit") + "Koin Emas", p.gold, "gold");
  html += statRow(ic("target") + "Moral", p.morality);
  html += statRow("Akar", p.roots);
  html += statRow("Paviliun", (ctx && ctx.academy) || "—");
  html += statRow(ic("sword") + "Senjata", w);
  if (comp) {
    html += `<h3 class="stat-title" style="margin-top:18px">✦ Roh</h3>`;
    html += statRow(comp.name, `HP ${comp.hp}/${comp.hp_max}`, comp.hp <= 0 ? "red" : "");
  }
  $("col-left").innerHTML = html;
}

function getRelationTier(score) {
  const num = Number(score) || 0;
  if (num > 0) {
    return { label: "Bersahabat", cls: "friendly" };
  } else if (num < 0) {
    return { label: "Bermusuhan", cls: "hostile" };
  } else {
    return { label: "Netral", cls: "neutral" };
  }
}

function renderRight(v) {
  let html = "";
  // quest utama
  html += `<div class="section"><h3 class="stat-title">${icon("scroll-text")}Quest Utama</h3>`;
  if (v.current_quest) {
    html += `<div class="quest-title">${esc(v.current_quest.title)}</div>`;
    html += `<div class="quest-objective">${esc(v.current_quest.objective)}</div>`;
  } else {
    html += `<div class="quest-done">Tidak ada quest utama aktif.</div>`;
  }
  html += `</div>`;
  // side quest
  if (v.side_quests && v.side_quests.length) {
    html += `<div class="section"><h3 class="stat-title">Quest Sampingan</h3>`;
    v.side_quests.forEach((q) => {
      html += `<div class="quest-title">${esc(q.title)}</div>`;
      html += `<div class="quest-objective">${esc(q.objective)}</div>`;
    });
    html += `</div>`;
  }
  // kurikulum paviliun
  if (ctx && ctx.curriculum && ctx.curriculum.length) {
    html += `<div class="section"><h3 class="stat-title">${icon("sparkles")}Kurikulum Paviliun</h3>`;
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
  // inventori
  html += `<div class="section"><h3 class="stat-title">${icon("backpack")}Inventori</h3>`;
  if (v.inventory && v.inventory.length) {
    v.inventory.forEach((i) => {
      html += `<div class="item-row"><span class="item-name">${esc(i.name)}</span>` +
              `<span class="item-count">×${i.count}</span></div>`;
    });
  } else {
    html += `<div class="quest-done">Kosong.</div>`;
  }
  html += `</div>`;
  // ingatan
  html += `<div class="section"><h3 class="stat-title">${icon("book-open")}天缘灵 · Ingatan</h3>`;
  if (v.memories && v.memories.length) {
    v.memories.forEach((m) => {
      html += `<div class="mem-row" onclick="openTianyuan()">${esc(m.title)}</div>`;
    });
  } else {
    html += `<div class="quest-done">Belum ada.</div>`;
  }
  html += `</div>`;
  $("col-right").innerHTML = html;
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
    const data = await api("/api/action", { body: { action } });
    if (data.ok) {
      view = data.view; ctx = data.context; render();
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
    html += `<div class="action-row"><button class="btn" onclick='act({type:"talk",npc:"${n.id}"})'>${icon("message-circle")}Bicara ${esc(n.name)}${tag}</button></div>`;
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

  // wilayah berburu
  if (loc.id === "loc_wilayah_berburu") {
    html += `<div class="action-row"><button class="btn" onclick='act({type:"hunt"})'>Berburu</button>` +
            `<button class="btn" onclick='act({type:"search"})'>Cari herba</button></div>`;
  }

  // lokasi aman
  if (loc.is_safe) {
    html += `<div class="action-row"><span class="action-label">Meditasi (jam):</span>` +
            `<input type="number" id="inp-ground" min="1" max="8" value="4">` +
            `<button class="btn" onclick='act({type:"grounding",hours:Number($("inp-ground").value)})'>Meditasi</button>` +
            `<button class="btn" onclick='act({type:"rest"})'>Istirahat</button></div>`;
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

  // tunggu
  html += `<div class="action-row"><span class="action-label">Tunggu (jam):</span>` +
          `<input type="number" id="inp-wait" min="1" max="12" value="4">` +
          `<button class="btn" onclick='act({type:"advance_time",hours:Number($("inp-wait").value)})'>Tunggu</button></div>`;

  // pakai item (consumable)
  const consumables = (v.inventory || []).filter((i) => i.type === "consumable");
  if (consumables.length) {
    html += `<div class="action-row"><span class="action-label">Pakai:</span>` +
            `<select id="sel-use">${consumables.map((i) => `<option value="${i.id}">${esc(i.name)} (×${i.count})</option>`).join("")}</select>` +
            `<button class="btn" onclick='act({type:"use_item",item:$("sel-use").value})'>Pakai</button></div>`;
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
  let speaker = d.speaker;
  if (speaker.startsWith("npc:")) speaker = npcNames[speaker.slice(4)] || speaker.slice(4);
  else if (speaker === "narration") speaker = "Narasi";
  let html = `<div class="interact-box">`;
  html += `<div class="dialog-speaker">${esc(speaker)}</div>`;
  html += `<div class="dialog-text">${esc(d.text)}</div>`;
  if (d.choices && d.choices.length) {
    d.choices.forEach((c) => {
      html += `<button class="choice-btn" onclick='act({type:"dialog_choice",choice_index:${c.index}})'>${c.index + 1}. ${esc(c.label)}</button>`;
    });
  } else {
    html += `<button class="btn btn-gold" onclick='act({type:"dialog_choice",choice_index:-1})'>Lanjut</button>`;
  }
  html += `</div>`;
  box.innerHTML = html;
}

// ---------- battle ----------

function renderBattle(v, c, box) {
  const b = v.battle;
  if (!b) { box.innerHTML = ""; return; }
  const p = b.player;
  let html = `<div class="interact-box">`;
  html += `<div class="dialog-speaker">⚔ Battle</div>`;
  html += `<div class="battle-foe"><span class="foe-name">Kau</span> — HP ${p.hp}/${p.hp_max} | Qi ${p.qi}/${p.qi_max}</div>`;
  b.foes.forEach((f) => {
    html += `<div class="battle-foe"><span class="foe-name">${esc(f.name)}</span> — HP ${f.hp}/${f.hp_max}</div>`;
  });
  if (b.companion) {
    html += `<div class="battle-foe"><span class="foe-name">${esc(b.companion.name)}</span> (otomatis) — HP ${b.companion.hp}/${b.companion.hp_max}</div>`;
  }
  html += `<div class="action-row"><button class="btn" onclick='act({type:"battle_action",action:"attack"})'>${icon("sword")}Serang</button>` +
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
  let html = `<div class="interact-box"><div class="dialog-speaker">Pilihan</div>`;
  html += `<div class="dialog-text">${esc(ch.prompt)}</div>`;
  ch.options.forEach((o, i) => {
    html += `<button class="choice-btn" onclick='act({type:"choose",option:"${o.value}"})'>${i + 1}. ${esc(o.label)}</button>`;
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
    ${statRow("Paviliun", s.academy || "—")}
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
  localStorage.setItem("arc-seen:" + currentSave, "1");
  closeModal("modal-arc-summary");
  render();
}

// ---------- B6: drawer mobile untuk panel kanan (quest/inventori/ingatan) ----------

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
  } else {
    closeRightDrawer();
  }
}

function closeRightDrawer() {
  const el = $("col-right");
  if (el) el.classList.remove("drawer-open");
  const ov = $("drawer-overlay");
  if (ov) ov.classList.add("hidden");
}

// ---------- panel Tianyuan Ling ----------

async function openTianyuan() {
  const data = await api("/api/tianyuan", { method: "GET" });
  const t = data.tianyuan;
  let html = `<h3>天缘灵 · Tianyuan Ling</h3>`;
  
  html += `<h3 style="margin-top:18px;font-size:15px">Status Misi</h3>`;
  if (t.mission.main) {
    html += `<div class="mem-full"><div class="mem-title">[Misi Utama] ${esc(t.mission.main.title)}</div>` +
            `<div class="mem-text">${esc(t.mission.main.objective)}</div></div>`;
  } else {
    html += `<p class="hint">[Misi Utama] Belum ada misi utama aktif (Arc 1 Tamat / Eksplorasi Bebas).</p>`;
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
        html += `<div class="mem-full"><div class="mem-title">${esc(m.title)}</div>` +
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
}

function closeTianyuan() { $("tianyuan").classList.add("hidden"); }

// ---------- inisialisasi ----------

$("btn-new").onclick = () => { AudioManager.start(); startNew(); };
$("btn-tianyuan").onclick = openTianyuan;
refreshSaveSlots();
loadIcons();  // C2: icon Lucide self-host — dimuat async, re-render bila sudah masuk

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
