/* ═══ Tian Xu: Second Life — frontend (vanilla JS, tanpa build) ═══ */

"use strict";

window.arcSummaryDismissed = false;

function showModal(id) {
  $(id).classList.remove("hidden");
  $("modal-overlay").classList.remove("hidden");
}
function closeModal(id) {
  $(id).classList.add("hidden");
  $("modal-overlay").classList.add("hidden");
}

const $ = (id) => document.getElementById(id);

let view = null;      // respons /api/state → {view, context}
let ctx = null;

// ---------- API ----------

async function api(path, opts) {
  const opt = { method: (opts && opts.method) || "POST", headers: { "Content-Type": "application/json" } };
  if (opts && opts.body !== undefined) opt.body = JSON.stringify(opts.body);
  const res = await fetch(path, opt);
  return res.json();
}

// ---------- aman HTML ----------

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
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
    b.onclick = () => loadGame(name);
    box.appendChild(b);
  });
}

function showGame() {
  $("title-screen").classList.add("hidden");
  $("game-screen").classList.remove("hidden");
}

async function startNew() {
  const data = await api("/api/new");
  if (data.ok) { view = data.view; ctx = data.context; showGame(); render(); }
}

async function loadGame(name) {
  const data = await api("/api/load", { body: { name } });
  if (!data.ok) { $("title-msg").textContent = data.error || "Gagal memuat."; return; }
  view = data.view; ctx = data.context; showGame(); render();
}

// ---------- render utama ----------

function render() {
  if (!view) return;
  renderHeader(view);
  renderLeft(view);
  renderRight(view);
  renderCenter(view, ctx);
  const logEl = $("log");
  logEl.scrollTop = logEl.scrollHeight;

  if (view.arc_summary && !window.arcSummaryDismissed) {
    openArcSummaryModal(view.arc_summary);
  }
}

function renderHeader(v) {
  const loc = v.location;
  $("header-title").textContent =
    `Hari ${v.day}, jam ${String(v.hour).padStart(2, "0")}:00 — ${loc.name}`;
}

function statRow(label, value, cls) {
  return `<div class="stat-row"><span class="stat-label">${esc(label)}</span>` +
         `<span class="stat-value ${cls || ""}">${esc(value)}</span></div>`;
}

function renderLeft(v) {
  const p = v.player;
  const names = (ctx && ctx.item_names) || {};
  const wid = p.equipment && p.equipment.weapon;
  const w = wid ? (names[wid] || wid) : "—";
  const comp = v.companion;
  let html = `<h3 class="stat-title">✦ ${esc(p.name)}</h3>`;
  html += statRow("Ranah", `${p.realm} Lv.${p.realm_level}`);
  html += statRow("HP", `${p.hp}/${p.hp_max}`, p.hp < p.hp_max ? "red" : "");
  html += statRow("Qi", `${p.qi}/${p.qi_max}`, "blue");
  html += statRow("Exp", `${p.exp}/${p.exp_next}`);
  html += statRow("Koin Emas", p.gold, "gold");
  html += statRow("Moral", p.morality);
  html += statRow("Akar", p.roots);
  html += statRow("Akademi", (ctx && ctx.academy) || "—");
  html += statRow("Senjata", w);
  if (comp) {
    html += `<h3 class="stat-title" style="margin-top:18px">✦ Roh</h3>`;
    html += statRow(comp.name, `HP ${comp.hp}/${comp.hp_max}`, comp.hp <= 0 ? "red" : "");
  }
  $("col-left").innerHTML = html;
}

function renderRight(v) {
  let html = "";
  // quest utama
  html += `<div class="section"><h3 class="stat-title">Quest Utama</h3>`;
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
  // inventori
  html += `<div class="section"><h3 class="stat-title">Inventori</h3>`;
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
  html += `<div class="section"><h3 class="stat-title">天缘灵 · Ingatan</h3>`;
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

function renderCenter(v, c) {
  $("log").innerHTML = v.log.map((e) =>
    `<div class="log-entry log-${esc(e.type)}">${esc(e.text)}</div>`).join("");

  const box = $("interact");
  if (v.mode === "dialog") renderDialog(v, box);
  else if (v.mode === "battle") renderBattle(v, c, box);
  else if (v.mode === "choose") renderChoose(v, box);
  else renderExplore(v, c, box);
}

async function act(action) {
  const data = await api("/api/action", { body: { action } });
  if (data.ok) { view = data.view; ctx = data.context; render(); }
}

// ---------- explore ----------

function renderExplore(v, c, box) {
  const loc = v.location;
  let html = `<div class="interact-box"><p class="hint">${esc(loc.description)}</p>`;
  html += `<h3 class="stat-title">Kau bisa</h3>`;

  // NPC di lokasi
  (c.npcs || []).forEach((n) => {
    const tag = n.can_spar ? " (sparing)" : n.shop ? " (toko)" : "";
    html += `<div class="action-row"><button class="btn" onclick='act({type:"talk",npc:"${n.id}"})'>Bicara ${esc(n.name)}${tag}</button></div>`;
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
    html += `<div class="action-row"><button class="btn" onclick='act({type:"move",to:"${cid}"})'>Pindah → ${esc(cid)}</button></div>`;
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
    html += `<div class="action-row"><button class="btn" onclick="openTianyuan()">Baca Ingatan</button></div>`;
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
  html += `<div class="action-row"><button class="btn" onclick='act({type:"battle_action",action:"attack"})'>Serang</button>` +
          `<button class="btn" onclick='act({type:"battle_action",action:"guard"})'>Bertahan</button>` +
          `<button class="btn" onclick='act({type:"battle_action",action:"flee"})'>Kabur</button></div>`;

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
  
  html += `<div class="shop-content">`;
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
    s.sell.forEach(item => {
      const count = invMap[item.item] || 0;
      const disabled = count < 1 ? "disabled" : "";
      html += `<div class="shop-item-row">
        <div class="shop-item-info">
          <span class="item-name">${esc(item.name)} (Punya: ${count})</span>
          <span class="shop-item-price">${item.price} Emas</span>
        </div>
        <button class="btn btn-small" ${disabled} onclick="actShop('shop_sell', '${item.item}')">Jual (1×)</button>
      </div>`;
    });
  }
  html += `</div>`;
  html += `<div style="margin-top:20px; text-align:right;"><button class="btn" onclick="closeModal('modal-shop')">Tutup</button></div>`;
  
  $("modal-shop").innerHTML = html;
}

async function actShop(type, itemId) {
  const data = await api("/api/action", { body: { action: { type: type, item: itemId, count: 1 } } });
  if (data.ok) { view = data.view; ctx = data.context; render(); renderShop(); }
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
  html += `<div class="dialog-text" style="font-style:italic; color:var(--gray); text-align:center; margin-bottom: 24px;">"${esc(s.teaser)}"</div>`;
  html += `<button class="btn btn-gold" style="width:100%" onclick="dismissArcSummary()">Lanjut Eksplorasi Bebas</button>`;
  
  $("modal-arc-summary").innerHTML = html;
  showModal("modal-arc-summary");
}

function dismissArcSummary() {
  window.arcSummaryDismissed = true;
  closeModal("modal-arc-summary");
  render();
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

$("btn-new").onclick = startNew;
$("btn-tianyuan").onclick = openTianyuan;
refreshSaveSlots();
