"""Validasi kontrak data saat load — Fase 1 (ENGINE_ADAPTATION_PLAN F1.1).

Arah pemilik proyek: **kontrak ketat + error jelas**. Semua pelanggaran
dikumpulkan lalu dilempar SATU exception agregat saat startup (`DataRegistry.__init__`),
sehingga CLI & web gagal cepat dengan pesan yang menyebut file + konteks + nilai
+ daftar nilai valid — bukan softlock diam-diam saat main.

Himpunan jenis (objective/efek/kondisi/teknik/status) di-import dari modul
engine yang sama yang dipakai eksekusi — satu sumber kebenaran (Fase 2:
diganti `.keys()` dari dispatch registry). `ITEM_TYPES`/`EQUIPMENT_SLOTS`
masih konstanta lokal (belum ada registry di engine — F2.4).

Aturan (plan F1.1 #1–#7 + evaluasi plan):
1. Skema per file + field wajib per jenis objektif
2. Duplikat id
3. Referensi silang 14 pasangan (fokus: resep & toko — satu-satunya crash 500)
4. Jenis tak dikenal: objective.kind, effect.type, kunci condition,
   technique.kind, status.kind, item.type
5. Jebakan `start_quest`: hanya sah di `choices[].effects` (dialog) — di
   `on_complete.effects`/`fail_effects` = diam-diam tidak terjadi → error
6. Branch quest: `nexts[0].choice_id` wajib bila >1 edge + tiap edge punya
   `option` unik
7. `timeout.hours` (main) → `fail_next` wajib

Trade-off (disepakati): `saves/*.json` TIDAK divalidasi (jalur kompatibilitas
sendiri); `_inactive/` otomatis di luar cakupan (glob non-rekursif loader);
tanpa toggle lenient.
"""

from __future__ import annotations

from collections import Counter

from .engine.battle import STATUS_KINDS, SUPPORTED_ELEMENTS, TECHNIQUE_KINDS
from .engine.dialog import (
    CONDITION_KEYS,
    CONDITION_NUMERIC_KEYS,
    CONDITION_REQUIRED_FIELDS,
    CONDITION_STRING_KEYS,
    CONDITION_VALUE_NUMERIC_KEYS,
)
from .engine.effects import EFFECT_TYPES, EFFECT_REQUIRED_FIELDS
from .engine.items import ITEM_TYPES
from .engine.quest import CHOOSE_SET_FIELDS, OBJECTIVE_HANDLERS, SIDE_UNSUPPORTED

# OBJECTIVE_KINDS kini diturunkan dari registry (F2.1c) — satu sumber kebenaran
OBJECTIVE_KINDS = set(OBJECTIVE_HANDLERS)
CHOOSE_SET_FIELDS = CHOOSE_SET_FIELDS
# Field wajib per jenis efek (F2.1a, menutup temuan #3 evaluasi F1)
EFFECT_REQUIRED_FIELDS = EFFECT_REQUIRED_FIELDS


class DataContractError(Exception):
    """Data konten melanggar kontrak engine — berisi daftar semua pelanggaran."""


def _add(errors: list[str], src: str, context: str, message: str, allowed=None) -> None:
    """Tambah satu baris pelanggaran dengan format konsisten:
    `[file] konteks — pesan` + baris daftar nilai valid bila relevan."""
    line = f"[{src}] {context} — {message}"
    if allowed:
        line += f" Jenis valid: {', '.join(sorted(allowed))}."
    errors.append(line)


def _check_faction(errors, src, context, faksi, registry) -> None:
    """Cross-reference faksi — hanya bila `factions.json` ada (faksi = closed
    set, typo id ditolak). Tanpa file faksi, dict reputasi bebas (kompatibel
    tema tanpa sistem faksi)."""
    if registry.faction_by_id and faksi and faksi not in registry.faction_by_id:
        _add(errors, src, context, f"faksi tak dikenal: '{faksi}'.",
             sorted(registry.faction_by_id))


def _check_condition(errors, cond, src, context, registry) -> None:
    """Aturan #4: kunci kondisi tak dikenal → error. B1 (audit opencode): field
    wajib per kunci (pola EFFECT_REQUIRED_FIELDS) + tipe value — cegah
    KeyError/TypeError/ValueError runtime dari nilai cacat yang lolos load."""
    if not isinstance(cond, dict):
        _add(errors, src, context, f"kondisi bukan objek (type: {type(cond).__name__}).")
        return
    unknown = set(cond) - CONDITION_KEYS
    for k in sorted(unknown):
        _add(errors, src, context, f"kunci kondisi tak dikenal: '{k}'.", CONDITION_KEYS)
    for key in sorted(set(cond) & CONDITION_KEYS):
        val = cond[key]
        req = CONDITION_REQUIRED_FIELDS.get(key)
        if key in ("flags", "flag_not"):
            # A07: multi-flag AND / multi-negasi — wajib list objek {key, value?}
            # (docs 11 Hidden Resolution: kombinasi SEMUA kondisi independen).
            # `flag_not` juga menerima dict tunggal (kompatibel pola lama).
            items = val if isinstance(val, list) else [val]
            if not isinstance(val, list) and not isinstance(val, dict):
                _add(errors, src, context,
                     f"kunci kondisi '{key}' wajib objek atau list objek.", {"key"})
                continue
            for i, f in enumerate(items):
                if not isinstance(f, dict) or "key" not in f:
                    _add(errors, src, context,
                         f"kunci kondisi '{key}[{i}]' wajib objek dengan 'key'.", {"key"})
            continue
        if req is not None:
            if not isinstance(val, dict):
                _add(errors, src, context,
                     f"kunci kondisi '{key}' wajib objek.", req)
                continue
            for f in sorted(req - set(val)):
                _add(errors, src, context,
                     f"kunci kondisi '{key}' tanpa field wajib '{f}'.", req)
            # T-A (review independen): field `value` (OPSIONAL, default 1) di
            # dict-keys wajib angka bila ada — string/bool/None lolos dulu →
            # TypeError '>=' runtime. Float diterima (runtime `>=` aman).
            if key in CONDITION_VALUE_NUMERIC_KEYS and "value" in val:
                vv = val["value"]
                if isinstance(vv, bool) or not isinstance(vv, (int, float)):
                    _add(errors, src, context,
                         f"kunci kondisi '{key}' field 'value' wajib angka (int/float).")
        elif key in CONDITION_NUMERIC_KEYS:
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                _add(errors, src, context,
                     f"kunci kondisi '{key}' wajib angka (int/float).")
        elif key in CONDITION_STRING_KEYS:
            # None SAH: pola lama {"academy": null} = "belum diset" (None == None
            # di runtime, mis. cek "belum pilih akademi" / "tak ada quest utama").
            if not (val is None or isinstance(val, str)):
                _add(errors, src, context,
                     f"kunci kondisi '{key}' wajib string id (atau null untuk 'belum diset').")
        # cross-reference faksi (docs 05) — dict-keys faction_min/max wajib
        # menunjuk faksi terdaftar bila factions.json ada
        if key in ("faction_min", "faction_max") and isinstance(val, dict):
            _check_faction(errors, src, f"{context}.{key}.faksi",
                           val.get("faksi"), registry)


def _check_effects(errors, effects, src, context, registry, *, allow_start_quest: bool) -> None:
    """Aturan #4 + #5 + F2.1a: jenis efek tak dikenal → error; `start_quest`
    hanya sah bila `allow_start_quest` (dialog); field wajib per jenis efek
    (EFFECT_REQUIRED_FIELDS) dicek — menutup temuan #3 evaluasi F1."""
    if effects is None:
        return
    if not isinstance(effects, list):
        _add(errors, src, context, "effects bukan list.")
        return
    for i, fx in enumerate(effects):
        # context dari pemanggil sudah menyertakan nama field (mis. ...choices[1].effects)
        ctx = f"{context}[{i}]"
        if not isinstance(fx, dict):
            _add(errors, src, ctx, "efek bukan objek.")
            continue
        t = fx.get("type")
        if t not in EFFECT_TYPES:
            _add(errors, src, ctx, f"jenis efek tak dikenal: '{t}'.", EFFECT_TYPES)
            continue
        if t == "start_quest":
            if not allow_start_quest:
                _add(errors, src, ctx,
                     "efek 'start_quest' tidak sah di sini — hanya diproses dialog "
                     "(choices[].effects); taruh di dialog, bukan di efek quest.")
            # R6 (BUG-8): start_quest hanya untuk quest SIDE — start_side()
            # guard kind side; menunjuk quest main = no-op diam-diam.
            target = registry.quest_by_id.get(fx.get("quest"))
            if target is None:
                _add(errors, src, ctx, f"quest tak dikenal: '{fx.get('quest')}'.")
            elif target.get("kind") != "side":
                _add(errors, src, ctx,
                     f"efek 'start_quest' harus menunjuk quest side — '{fx.get('quest')}' "
                     "adalah quest utama (dimulai via next/starting, bukan efek).")
        # field wajib per jenis (F2.1a) — flag tanpa key dkk. ditolak saat load
        missing = EFFECT_REQUIRED_FIELDS.get(t, set()) - set(fx)
        if missing:
            _add(errors, src, ctx,
                 f"efek '{t}' kekurangan field wajib: {', '.join(sorted(missing))}.",
                 sorted(EFFECT_REQUIRED_FIELDS.get(t, set())))
        # R5 (BUG-5/6/7): referensi efek divalidasi — item/teknik/NPC/lokasi
        # ghost = silent drop / state kotor yang arah proyek tolak.
        if t == "item" and fx.get("id") not in registry.items:
            _add(errors, src, ctx, f"item tak dikenal: '{fx.get('id')}'.",
                 sorted(registry.items)[:12])
        if t == "technique" and fx.get("id") not in registry.techniques:
            _add(errors, src, ctx, f"teknik tak dikenal: '{fx.get('id')}'.",
                 sorted(registry.techniques)[:12])
        if t == "npc_state":
            if fx.get("npc") not in registry.npc_by_id:
                _add(errors, src, ctx, f"NPC tak dikenal: '{fx.get('npc')}'.")
            if fx.get("location") and fx["location"] not in registry.location_by_id:
                _add(errors, src, ctx,
                     f"lokasi tak dikenal pada npc_state: '{fx.get('location')}'.")
        if t == "reputation":
            # cross-reference faksi (docs 05) — reputasi wajib menunjuk faksi
            # terdaftar bila factions.json ada
            _check_faction(errors, src, f"{ctx}.faksi", fx.get("faksi"), registry)


def _validate_config(registry, errors) -> None:
    cfg = registry.config
    src = "config.json"

    # aturan F2.1a (temuan #2 evaluasi F1): `starting` WAJIB ada — engine
    # membacanya (GameSession.new); tanpa itu game jalan dengan default
    # diam-diam, bertentangan dengan kontrak ketat.
    if "starting" not in cfg or not isinstance(cfg.get("starting"), dict):
        _add(errors, src, "starting",
             "config wajib punya 'starting' (objek awal pemain) — dibaca engine.")
    start = cfg.get("starting", {}) or {}
    p = start.get("player", {}) or {}
    realm = p.get("realm")
    if realm and realm not in registry.realms:
        _add(errors, src, "starting.player.realm", f"ranah tak dikenal: '{realm}'.")
    if start.get("location") and start["location"] not in registry.location_by_id:
        _add(errors, src, "starting.location",
             f"lokasi tak dikenal: '{start['location']}'.")
    qid = start.get("current_quest")
    if qid and qid not in registry.quest_by_id:
        _add(errors, src, "starting.current_quest", f"quest tak dikenal: '{qid}'.")
    for it in start.get("inventory", []) or []:
        if isinstance(it, dict) and it.get("id") not in registry.items:
            _add(errors, src, f"starting.inventory[].id",
                 f"item tak dikenal: '{it.get('id')}'.")

    # aturan #3: akademi → teknik/kompanion/item valid
    for a in cfg.get("academies", []) or []:
        aid = a.get("id", "?")
        for tid in a.get("curriculum", []) or []:
            if tid not in registry.techniques:
                _add(errors, src, f"academies[{aid}].curriculum[]",
                     f"teknik tak dikenal: '{tid}'.")
        cid = a.get("companion")
        if cid and cid not in {c.get("id") for c in registry.companions}:
            _add(errors, src, f"academies[{aid}].companion",
                 f"kompanion tak dikenal: '{cid}'.")
        for sk in a.get("starter_kit", []) or []:
            iid = sk.get("id") if isinstance(sk, dict) else sk
            if isinstance(sk, dict) and not sk.get("id"):
                _add(errors, src, f"academies[{aid}].starter_kit[]",
                     "item starter tanpa field 'id'.")
            elif iid not in registry.items:
                _add(errors, src, f"academies[{aid}].starter_kit[]",
                     f"item tak dikenal: '{iid}'.")

    # aturan #3: zona berburu (F2.3 — `world.hunts[]` kanonik, `world.hunt`
    # legacy tetap divalidasi untuk config lama) → musuh/item/lokasi valid
    def _check_hunt(hunt, ctx, *, require_id: bool):
        if not isinstance(hunt, dict):
            _add(errors, src, ctx, "zona berburu harus objek.")
            return
        # F2.3 (evaluasi): id + location WAJIB — web/_hunt memakai keduanya
        # (hunts_for_location, cooldown per zona); tanpa itu = crash render/
        # zona tak pernah bisa dipilih. `world.hunt` legacy dikecualikan dari
        # id (loader menyuntik id "legacy"); lokasi tetap wajib di semua bentuk.
        if require_id and not hunt.get("id"):
            _add(errors, src, f"{ctx}.id", "zona berburu wajib punya 'id'.")
        if not hunt.get("location"):
            _add(errors, src, f"{ctx}.location", "zona berburu wajib punya 'location'.")
        elif hunt["location"] not in registry.location_by_id:
            _add(errors, src, f"{ctx}.location",
                 f"lokasi tak dikenal: '{hunt['location']}'.")
        for field in ("pool", "night_pool"):
            for eid in hunt.get(field, []) or []:
                if eid not in registry.enemies:
                    _add(errors, src, f"{ctx}.{field}[]",
                         f"musuh tak dikenal: '{eid}'.")
        mb = hunt.get("mini_boss")
        if mb and mb not in registry.enemies:
            _add(errors, src, f"{ctx}.mini_boss", f"musuh tak dikenal: '{mb}'.")
        si = hunt.get("search_item")
        if si and si not in registry.items:
            _add(errors, src, f"{ctx}.search_item", f"item tak dikenal: '{si}'.")

    world_cfg = cfg.get("world") or {}
    hunts = world_cfg.get("hunts")
    if hunts is not None:
        if not isinstance(hunts, list):
            _add(errors, src, "world.hunts", "'world.hunts' harus list zona berburu.")
        else:
            seen = set()
            for i, h in enumerate(hunts):
                ctx = f"world.hunts[{i}]"
                if isinstance(h, dict) and h.get("id"):
                    if h["id"] in seen:
                        _add(errors, src, f"{ctx}.id", f"id zona berburu duplikat: '{h['id']}'.")
                    seen.add(h["id"])
                _check_hunt(h, ctx, require_id=True)
    if isinstance(world_cfg.get("hunt"), dict):
        _check_hunt(world_cfg["hunt"], "world.hunt", require_id=False)

    # mining zones — world.mines[]
    mines = world_cfg.get("mines")
    if mines is not None:
        if not isinstance(mines, list):
            _add(errors, src, "world.mines", "'world.mines' harus list zona tambang.")
        else:
            mine_ids = set()
            for i, m in enumerate(mines):
                ctx = f"world.mines[{i}]"
                if not isinstance(m, dict):
                    _add(errors, src, ctx, "zona tambang harus objek.")
                    continue
                mid = m.get("id")
                if not mid:
                    _add(errors, src, f"{ctx}.id", "zona tambang wajib punya 'id'.")
                elif mid in mine_ids:
                    _add(errors, src, f"{ctx}.id", f"id zona tambang duplikat: '{mid}'.")
                mine_ids.add(mid)
                loc_id = m.get("location")
                if not loc_id:
                    _add(errors, src, f"{ctx}.location", "zona tambang wajib punya 'location'.")
                elif loc_id not in registry.location_by_id:
                    _add(errors, src, f"{ctx}.location", f"lokasi tak dikenal: '{loc_id}'.")
                for entry in m.get("pool", []) or []:
                    iid = entry.get("item") if isinstance(entry, dict) else None
                    if iid and iid not in registry.items:
                        _add(errors, src, f"{ctx}.pool[].item", f"item tak dikenal: '{iid}'.")

    # search_items per hunt zone
    for i, h in enumerate(hunts or []):
        if not isinstance(h, dict):
            continue
        search_items = h.get("search_items")
        if search_items is not None:
            if not isinstance(search_items, list):
                _add(errors, src, f"world.hunts[{i}].search_items", "harus list.")
            else:
                for j, si in enumerate(search_items):
                    if isinstance(si, dict) and si.get("item") and si["item"] not in registry.items:
                        _add(errors, src, f"world.hunts[{i}].search_items[{j}].item",
                             f"item tak dikenal: '{si['item']}'.")

    # aturan #4: status.kind dari config.battle.statuses
    statuses_cfg = ((cfg.get("battle") or {}).get("statuses") or {})
    for sid, sc in statuses_cfg.items():
        if not isinstance(sc, dict):
            _add(errors, src, f"battle.statuses[{sid}]",
                 f"status config harus dict, ditemukan: {type(sc).__name__}.")
            continue
        kind = sc.get("kind")
        if kind not in STATUS_KINDS:
            _add(errors, src, f"battle.statuses[{sid}].kind",
                 f"jenis status tak dikenal: '{kind}'.", STATUS_KINDS)
        max_dur = sc.get("max_duration")
        if max_dur is None:
            _add(errors, src, f"battle.statuses[{sid}].max_duration",
                 f"max_duration wajib ada dan > 0.")
        elif int(max_dur) <= 0:
            _add(errors, src, f"battle.statuses[{sid}].max_duration",
                 f"max_duration harus > 0, ditemukan: {max_dur}.")

    # aturan #3 (tambahan): arcs[].endings[].condition → kunci kondisi valid
    for arc in cfg.get("arcs", []) or []:
        aid = arc.get("id", "?")
        if arc.get("final_quest") and arc["final_quest"] not in registry.quest_by_id:
            _add(errors, src, f"arcs[{aid}].final_quest",
                 f"quest tak dikenal: '{arc['final_quest']}'.")
        for end in arc.get("endings", []) or []:
            # C3/H1 (docs 11): ending wajib punya id + title — engine & CLI
            # merender keduanya (tanpa itu = baris kosong/absen diam-diam)
            if not end.get("id"):
                _add(errors, src, f"arcs[{aid}].endings[]", "ending wajib punya 'id'.")
            if not end.get("title"):
                _add(errors, src, f"arcs[{aid}].endings[]", "ending wajib punya 'title'.")
            cond = end.get("condition")
            if cond:
                _check_condition(errors, cond, src, f"arcs[{aid}].endings[].condition", registry)


def _validate_quests(registry, errors) -> None:
    for i, q in enumerate(registry.quests):
        qid = q.get("id", "?")
        src = registry.quest_src_list[i] if i < len(registry.quest_src_list) else "quests/?"
        ctx = f"quest '{qid}'"

        # aturan #1: skema quest
        if not q.get("id"):
            _add(errors, src, ctx, "quest tanpa field 'id'.")
        if q.get("kind") not in ("main", "side"):
            _add(errors, src, ctx, f"kind quest tak dikenal: '{q.get('kind')}'.", {"main", "side"})
        obj = q.get("objective")
        if not isinstance(obj, dict):
            _add(errors, src, ctx, "quest tanpa 'objective'.")
            continue
        kind = obj.get("kind")
        if kind not in OBJECTIVE_KINDS:
            _add(errors, src, f"{ctx}.objective.kind",
                 f"jenis objektif tak dikenal: '{kind}'.", OBJECTIVE_KINDS)
            continue  # field wajib per kind tidak relevan untuk kind tak dikenal

        # R1 (BUG-1): side quest dengan jenis yang tidak didukung side → tolak
        # (softlock diam-diam). Engine melayani side untuk semua kind via
        # registry; `choose` butuh UI main-only — itulah satu-satunya yang ditolak.
        if q.get("kind") == "side" and kind in SIDE_UNSUPPORTED:
            _add(errors, src, f"{ctx}.objective.kind",
                 f"side quest tidak mendukung objektif '{kind}' — engine hanya "
                 f"menyelesaikannya untuk quest utama (butuh UI mode).",
                 sorted(set(OBJECTIVE_KINDS) - SIDE_UNSUPPORTED))

        # aturan #1: field wajib per kind objektif — dari spec registry (F2.1c),
        # bukan dict hardcode (satu sumber kebenaran)
        spec = OBJECTIVE_HANDLERS[kind]
        for f in spec.required_fields:
            if f not in obj or obj[f] in (None, ""):
                _add(errors, src, f"{ctx}.objective.{f}",
                     f"field wajib untuk objektif '{kind}' tidak ada.",
                     sorted(spec.required_fields))
        if kind == "choose":
            opts = obj.get("options")
            if not isinstance(opts, list) or not opts:
                _add(errors, src, f"{ctx}.objective.options",
                     "objektif 'choose' wajib punya options non-kosong.")
            else:
                for i, o in enumerate(opts):
                    if not isinstance(o, dict) or not o.get("value") or not o.get("label"):
                        _add(errors, src, f"{ctx}.objective.options[{i}]",
                             "tiap option wajib punya 'value' dan 'label' non-kosong.")
                    # F2.2b: `set` opsional — field dikenal + tipe benar (closed-set
                    # CHOOSE_SET_FIELDS dari quest.py, satu sumber kebenaran)
                    oset = o.get("set") if isinstance(o, dict) else None
                    if oset is not None and not isinstance(oset, dict):
                        _add(errors, src, f"{ctx}.objective.options[{i}].set",
                             "'set' harus objek.")
                    elif isinstance(oset, dict):
                        for field, val in oset.items():
                            fctx = f"{ctx}.objective.options[{i}].set.{field}"
                            if field not in CHOOSE_SET_FIELDS:
                                _add(errors, src, fctx,
                                     f"field state tak dikenal pada opsi choose: '{field}'.",
                                     sorted(CHOOSE_SET_FIELDS))
                            elif CHOOSE_SET_FIELDS[field] == "str" and not isinstance(val, str):
                                _add(errors, src, fctx, "field string — nilai harus teks.")
                            elif CHOOSE_SET_FIELDS[field] == "int" and not isinstance(val, int):
                                _add(errors, src, fctx, "field angka — nilai harus bilangan bulat.")
                            elif field == "academy":
                                # F2.2b (evaluasi F2): akademi yang ditulis harus ADA di
                                # config.academies — kalau tidak, grant starter kit/companion
                                # diam-diam no-op (silent drop yang arah proyek tolak).
                                academy_ids = {a.get("id") for a in registry.config.get("academies", []) or []}
                                if val not in academy_ids:
                                    _add(errors, src, fctx,
                                         f"akademi tak dikenal pada opsi choose: '{val}' — "
                                         "tidak ada di config.academies.",
                                         sorted(academy_ids))
                            elif field == "gold" and val < 0:
                                # R3: gold tidak boleh negatif (konsisten _fx_gold)
                                _add(errors, src, fctx, "gold tidak boleh negatif.")
                            elif field == "morality":
                                # R3: morality harus dalam range config (konsisten adjust_morality)
                                m = registry.config.get("morality") or {}
                                lo, hi = m.get("min", -100), m.get("max", 100)
                                if not (lo <= val <= hi):
                                    _add(errors, src, fctx,
                                         f"morality di luar range {lo}..{hi}.")
                            elif field == "roots":
                                # R4: akar harus dikenal (roots_tier lookup → None = silent fallback)
                                root_ids = {t.get("id") for t in registry.config.get("roots", {}).get("tiers", []) or []}
                                if val not in root_ids:
                                    _add(errors, src, fctx,
                                     f"akar tak dikenal pada opsi choose: '{val}' — "
                                     "tidak ada di config.roots.tiers.",
                                     sorted(root_ids))

        if kind == "spar":
            debuff = obj.get("spar_debuff")
            if debuff is not None:
                if not isinstance(debuff, dict):
                    _add(errors, src, f"{ctx}.objective.spar_debuff",
                         "spar_debuff harus objek.")
                else:
                    allowed = {"hp_mult", "atk_mult", "def_mult"}
                    for field, val in debuff.items():
                        fctx = f"{ctx}.objective.spar_debuff.{field}"
                        if field not in allowed:
                            _add(errors, src, fctx,
                                 f"field spar_debuff tak dikenal: '{field}'.",
                                 allowed)
                        elif isinstance(val, bool) or not isinstance(val, (int, float)) or val <= 0:
                            _add(errors, src, fctx,
                                 "nilai spar_debuff harus angka lebih besar dari 0.")
            allies = obj.get("allies")
            if allies is not None:
                if not isinstance(allies, list) or not allies:
                    _add(errors, src, f"{ctx}.objective.allies",
                         "allies harus list NPC non-kosong.")
                else:
                    for i, npc_id in enumerate(allies):
                        ally = registry.npc_by_id.get(npc_id)
                        if not ally:
                            _add(errors, src, f"{ctx}.objective.allies[{i}]",
                                 f"NPC tak dikenal: '{npc_id}'.")
                        elif not isinstance(ally.get("combat"), dict):
                            _add(errors, src, f"{ctx}.objective.allies[{i}]",
                                 f"NPC sekutu wajib punya combat: '{npc_id}'.")

        # aturan #3: referensi silang objektif
        if kind in ("talk", "spar") and obj.get("npc") not in registry.npc_by_id:
            _add(errors, src, f"{ctx}.objective.npc",
                 f"NPC tak dikenal: '{obj.get('npc')}'.")
        if obj.get("report_to") and obj["report_to"] not in registry.npc_by_id:
            _add(errors, src, f"{ctx}.objective.report_to",
                 f"NPC tak dikenal: '{obj['report_to']}'.")
        if kind == "gather" and obj.get("item") and obj["item"] not in registry.items:
            _add(errors, src, f"{ctx}.objective.item",
                 f"item tak dikenal: '{obj['item']}'.")
        if kind == "reach" and obj.get("location") and obj["location"] not in registry.location_by_id:
            _add(errors, src, f"{ctx}.objective.location",
                 f"lokasi tak dikenal: '{obj['location']}'.")

        # aturan #3 (R2): next/fail_next hanya utk quest main (DAG current_quest);
        # target wajib quest main — side quest jadi "current main" = alur rusak.
        is_side = q.get("kind") == "side"
        for field in ("next", "fail_next"):
            edges = q.get(field, []) or []
            if is_side and edges:
                _add(errors, src, f"{ctx}.{field}",
                     f"side quest tidak boleh punya '{field}' (hanya quest utama "
                     "yang ber-DAG next/fail_next).")
            for edge in edges:
                target = registry.quest_by_id.get(edge.get("quest"))
                if target is None:
                    _add(errors, src, f"{ctx}.{field}[].quest",
                         f"quest tak dikenal: '{edge.get('quest')}'.")
                elif target.get("kind") != "main":
                    _add(errors, src, f"{ctx}.{field}[].quest",
                         f"'{field}' harus menunjuk quest utama — '{edge.get('quest')}' "
                         f"adalah quest side.")

        # aturan #6: branch quest — >1 edge → choice_id wajib + option unik
        nexts = q.get("next", []) or []
        if len(nexts) > 1:
            if not nexts[0].get("choice_id"):
                _add(errors, src, f"{ctx}.next",
                     "quest bercabang (>1 edge) wajib punya 'choice_id' di edge pertama "
                     "(dialog pemilih cabang).")
            opts = [e.get("option") for e in nexts]
            if any(not o for o in opts):
                _add(errors, src, f"{ctx}.next",
                     "quest bercabang: tiap edge wajib punya 'option' (nilai pilihan).")
            elif len(set(opts)) != len(opts):
                _add(errors, src, f"{ctx}.next",
                     f"quest bercabang: 'option' harus unik per edge — dapat {opts}.")

        # aturan #7: main quest ber-timeout → fail_next wajib
        timeout = q.get("timeout") or {}
        if q.get("kind") == "main" and timeout.get("hours") and not q.get("fail_next"):
            _add(errors, src, f"{ctx}.timeout",
                 "main quest ber-timeout wajib punya 'fail_next' (jalur gagal).")

        # aturan #5: start_quest TIDAK boleh di on_complete/fail_effects
        _check_effects(errors, q.get("on_complete", {}).get("effects"),
                       src, f"{ctx}.on_complete.effects", registry, allow_start_quest=False)
        _check_effects(errors, q.get("fail_effects"),
                       src, f"{ctx}.fail_effects", registry, allow_start_quest=False)

        # aturan #3: on_complete.memory_unlock → ingatan valid
        mu = q.get("on_complete", {}).get("memory_unlock")
        if mu and mu not in registry.memory_by_id:
            _add(errors, src, f"{ctx}.on_complete.memory_unlock",
                 f"ingatan tak dikenal: '{mu}'.")


def _validate_dialogs(registry, errors) -> None:
    for i, d in enumerate(registry.dialogs):
        did = d.get("id", "?")
        src = registry.dialog_src_list[i] if i < len(registry.dialog_src_list) else "dialogs/?"
        ctx = f"dialog '{did}'"

        # aturan #3: dialog.npc → NPC valid
        if d.get("npc") and d["npc"] not in registry.npc_by_id:
            _add(errors, src, f"{ctx}.npc", f"NPC tak dikenal: '{d['npc']}'.")

        nodes = d.get("nodes")
        if not isinstance(nodes, dict) or not nodes:
            _add(errors, src, f"{ctx}.nodes", "dialog tanpa 'nodes' (non-kosong).")
            continue

        # aturan #1: start → node valid; tiap node punya text|random_text
        if d.get("start") and d["start"] not in nodes:
            _add(errors, src, f"{ctx}.start",
                 f"node start tak dikenal: '{d['start']}'.")
        for nid, node in nodes.items():
            nctx = f"{ctx}.nodes.{nid}"
            if not isinstance(node, dict):
                _add(errors, src, nctx, "node bukan objek.")
                continue
            has_text = bool(node.get("text"))
            rt = node.get("random_text")
            has_rt = isinstance(rt, list) and len(rt) > 0
            if not has_text and not has_rt:
                _add(errors, src, nctx,
                     "node wajib punya 'text' ATAU 'random_text' (list non-kosong).")
            cond = node.get("condition")
            if cond:
                _check_condition(errors, cond, src, f"{nctx}.condition", registry)
            nxt = node.get("next")
            if nxt and nxt not in nodes:
                _add(errors, src, f"{nctx}.next", f"node tak dikenal: '{nxt}'.")
            for i, ch in enumerate(node.get("choices", []) or []):
                cctx = f"{nctx}.choices[{i}]"
                if not isinstance(ch, dict):
                    _add(errors, src, cctx, "choice bukan objek.")
                    continue
                if not ch.get("label"):
                    _add(errors, src, cctx, "choice wajib punya 'label'.")
                if ch.get("next") and ch["next"] not in nodes:
                    _add(errors, src, f"{cctx}.next",
                         f"node tak dikenal: '{ch['next']}'.")
                ccond = ch.get("condition")
                if ccond:
                    _check_condition(errors, ccond, src, f"{cctx}.condition", registry)
                # aturan #4+#5: efek choice — start_quest SAH di sini (satu-satunya);
                # ref quest + kind side ditangani `_check_effects` (R6)
                _check_effects(errors, ch.get("effects"), src, f"{cctx}.effects",
                               registry, allow_start_quest=True)


def _validate_npcs(registry, errors) -> None:
    for n in registry.npcs:
        nid = n.get("id", "?")
        src = "npcs.json"
        ctx = f"npc '{nid}'"

        # aturan #3: lokasi & dialog valid
        if n.get("location") and n["location"] not in registry.location_by_id:
            _add(errors, src, f"{ctx}.location", f"lokasi tak dikenal: '{n['location']}'.")
        routes = n.get("dialog_routes") or {}
        for slot in ("general", "first_meeting"):
            did = routes.get(slot)
            if did and did not in registry.dialog_by_id:
                _add(errors, src, f"{ctx}.dialog_routes.{slot}",
                     f"dialog tak dikenal: '{did}'.")
        # default_dialog berada di level NPC root (bukan di dialog_routes) —
        # session.py: npc.get("default_dialog", "").
        # default_dialog berada di level NPC root (bukan di dialog_routes) —
        # session.py: npc.get("default_dialog", "").
        if n.get("default_dialog") and n["default_dialog"] not in registry.dialog_by_id:
            _add(errors, src, f"{ctx}.default_dialog",
                 f"dialog tak dikenal: '{n['default_dialog']}'.")
        inti = routes.get("intimacy") or {}
        if inti.get("dialog") and inti["dialog"] not in registry.dialog_by_id:
            _add(errors, src, f"{ctx}.dialog_routes.intimacy.dialog",
                 f"dialog tak dikenal: '{inti['dialog']}'.")
        for qid, did in (routes.get("main") or {}).items():
            if did not in registry.dialog_by_id:
                _add(errors, src, f"{ctx}.dialog_routes.main[{qid}]",
                     f"dialog tak dikenal: '{did}'.")
            if qid not in registry.quest_by_id:
                _add(errors, src, f"{ctx}.dialog_routes.main[{qid}]",
                     f"quest tak dikenal: '{qid}'.")
        for qid, mapping in (routes.get("side") or {}).items():
            if isinstance(mapping, dict):
                for slot in ("offer", "report"):
                    did = mapping.get(slot)
                    if did and did not in registry.dialog_by_id:
                        _add(errors, src, f"{ctx}.dialog_routes.side[{qid}].{slot}",
                             f"dialog tak dikenal: '{did}'.")
            if qid not in registry.quest_by_id:
                _add(errors, src, f"{ctx}.dialog_routes.side[{qid}]",
                     f"quest tak dikenal: '{qid}'.")

        # aturan #4: kondisi spar_require & schedule
        sr = n.get("spar_require")
        if sr:
            _check_condition(errors, sr, src, f"{ctx}.spar_require", registry)
        for i, s in enumerate(n.get("schedule", []) or []):
            cond = s.get("condition")
            if cond:
                _check_condition(errors, cond, src, f"{ctx}.schedule[{i}].condition", registry)

        # aturan #3: toko → item valid
        shop = n.get("shop") or {}
        for slot in ("buy", "sell"):
            for s in shop.get(slot, []) or []:
                if s.get("item") not in registry.items:
                    _add(errors, src, f"{ctx}.shop.{slot}[].item",
                         f"item tak dikenal: '{s.get('item')}'.")

        # kontrak spar: can_spar wajib punya combat (kode `_spar` KeyError tanpa itu)
        if n.get("can_spar") and not isinstance(n.get("combat"), dict):
            _add(errors, src, f"{ctx}.combat",
                 "NPC dengan can_spar=true wajib punya 'combat' (stat musuh sparing).")


def _validate_locations(registry, errors) -> None:
    for loc in registry.locations:
        lid = loc.get("id", "?")
        src = "locations.json"
        for c in loc.get("connections", []) or []:
            if c not in registry.location_by_id:
                _add(errors, src, f"location '{lid}'.connections[]",
                     f"lokasi tak dikenal: '{c}'.")
            elif lid not in (registry.location_by_id[c].get("connections", []) or []):
                # B2 (audit opencode): koneksi wajib timbal balik — A→B ⇒ B→A.
                # Graf asimetris lolos dulu → pemain terjebak (escape hanya via KO).
                _add(errors, src, f"location '{lid}'.connections[]",
                     f"koneksi tidak timbal balik: '{c}' tidak menunjuk balik ke '{lid}'.")
    if not any(l.get("is_safe") for l in registry.locations):
        _add(errors, "locations.json", "locations",
             "setidaknya satu lokasi wajib is_safe=true (respawn KO & titik aman).")


def _validate_memories(registry, errors) -> None:
    """Kontrak memories.json (E1, docs 06) — id/title/text wajib; reliability
    opsional (default 'unknown'). Memory tanpa teks tidak bisa ditampilkan
    (CLI/web merender title+text) — data cacat ditolak saat load."""
    src = "memories.json"
    for m in registry.memories:
        mid = m.get("id", "?")
        ctx = f"memory '{mid}'"
        if not m.get("id"):
            _add(errors, src, ctx, "memory tanpa field 'id'.")
        if not m.get("title"):
            _add(errors, src, ctx, "memory wajib punya 'title' (judul ingatan).")
        if not m.get("text"):
            _add(errors, src, ctx, "memory wajib punya 'text' (isi ingatan).")
        rel = m.get("reliability")
        if rel is not None and not isinstance(rel, str):
            _add(errors, src, ctx, "field 'reliability' wajib string (opsional).")


def _validate_companions(registry, errors) -> None:
    """Kontrak companions.json (C5, docs 04) — id/name wajib; stat base
    opsional (engine memberi default). Companion tanpa name tidak bisa
    ditampilkan di battle/view."""
    src = "companions.json"
    for c in registry.companions:
        cid = c.get("id", "?")
        ctx = f"companion '{cid}'"
        if not c.get("id"):
            _add(errors, src, ctx, "companion tanpa field 'id'.")
        if not c.get("name"):
            _add(errors, src, ctx, "companion wajib punya 'name'.")
        elem = c.get("element", "")
        if elem and elem not in SUPPORTED_ELEMENTS:
            _add(errors, src, f"{ctx}.element",
                 f"elemen tak dikenal: '{elem}'.", sorted(SUPPORTED_ELEMENTS))


def _validate_recipes(registry, errors) -> None:
    src = "recipes.json"
    for r in registry.recipes:
        rid = r.get("id", "?")
        if r.get("result") and r["result"] not in registry.items:
            _add(errors, src, f"recipe '{rid}'.result",
                 f"item tak dikenal: '{r['result']}'.")
        recipe_item = r.get("recipe_item")
        if recipe_item and recipe_item not in registry.items:
            _add(errors, src, f"recipe '{rid}'.recipe_item",
                 f"item tak dikenal: '{recipe_item}'.")
        for ing in r.get("ingredients", []) or []:
            if ing.get("item") not in registry.items:
                _add(errors, src, f"recipe '{rid}'.ingredients[].item",
                     f"item tak dikenal: '{ing.get('item')}'.")


def _validate_csv(registry, errors) -> None:
    # items.csv — aturan #4: item.type tak dikenal
    for it in registry.items_raw:
        iid = it.get("id", "?")
        if it.get("type") not in ITEM_TYPES:
            _add(errors, "items.csv", f"item '{iid}'.type",
                 f"jenis item tak dikenal: '{it.get('type')}'.", ITEM_TYPES)
    # enemies.csv — drop_item → item valid; element wajib
    for en in registry.enemies_raw:
        eid = en.get("id", "?")
        if en.get("drop_item") and en["drop_item"] not in registry.items:
            _add(errors, "enemies.csv", f"enemy '{eid}'.drop_item",
                 f"item tak dikenal: '{en['drop_item']}'.")
        elem = en.get("element", "")
        if elem and elem not in SUPPORTED_ELEMENTS:
            _add(errors, "enemies.csv", f"enemy '{eid}'.element",
                 f"elemen tak dikenal: '{elem}'.", sorted(SUPPORTED_ELEMENTS))
    # techniques.csv — aturan #4: kind tak dikenal; realm_required → ranah valid;
    # element ∈ SUPPORTED_ELEMENTS; guard_pct ∈ [0, 80]
    for tek in registry.techniques_raw:
        tid = tek.get("id", "?")
        if tek.get("kind") not in TECHNIQUE_KINDS:
            _add(errors, "techniques.csv", f"technique '{tid}'.kind",
                 f"jenis teknik tak dikenal: '{tek.get('kind')}'.", TECHNIQUE_KINDS)
        if tek.get("realm_required") and tek["realm_required"] not in registry.realms:
            _add(errors, "techniques.csv", f"technique '{tid}'.realm_required",
                 f"ranah tak dikenal: '{tek['realm_required']}'.")
        elem = tek.get("element", "")
        if elem and elem not in SUPPORTED_ELEMENTS:
            _add(errors, "techniques.csv", f"technique '{tid}'.element",
                 f"elemen tak dikenal: '{elem}'.", sorted(SUPPORTED_ELEMENTS))
        gpct = tek.get("guard_pct", "")
        if gpct not in ("", "0"):
            gpct_val = int(gpct)
            if gpct_val < 0 or gpct_val > 80:
                _add(errors, "techniques.csv", f"technique '{tid}'.guard_pct",
                     f"guard_pct harus 0-80, ditemukan: {gpct_val}.")
        apply_st = tek.get("apply_status", "")
        if apply_st:
            statuses_keys = set(((registry.config.get("battle") or {}).get("statuses") or {}).keys())
            if apply_st not in statuses_keys:
                _add(errors, "techniques.csv", f"technique '{tid}'.apply_status",
                     f"status tak dikenal: '{apply_st}'.", sorted(statuses_keys))


def _validate_key_items(registry, errors) -> None:
    """Validasi key_items.json — efek harus valid, id harus ada di items."""
    src = "key_items.json"
    for kid, ki in registry.key_items.items():
        ctx = f"key_item '{kid}'"
        if kid not in registry.items:
            _add(errors, src, ctx, f"item tak dikenal: '{kid}'.")
            continue
        if registry.items[kid].get("type") != "key_item":
            _add(errors, src, ctx, f"item '{kid}' bukan key_item (type: {registry.items[kid].get('type')}).")
        # validate use_effects
        effects = ki.get("use_effects")
        if effects is not None:
            _check_effects(errors, effects, src, ctx + ".use_effects", registry, allow_start_quest=False)


def _validate_duplicates(registry, errors) -> None:
    """Aturan #2: duplikat id — deteksi dari LIST mentah (dict index menimpa)."""
    groups = [
        ("quest", registry.quests, "quests/*"),
        ("dialog", registry.dialogs, "dialogs/*"),
        ("npc", registry.npcs, "npcs.json"),
        ("location", registry.locations, "locations.json"),
        ("memory", registry.memories, "memories.json"),
        ("recipe", registry.recipes, "recipes.json"),
        ("companion", registry.companions, "companions.json"),
        ("faction", registry.factions, "factions.json"),
        ("item", registry.items_raw, "items.csv"),
        ("enemy", registry.enemies_raw, "enemies.csv"),
        ("realm", registry.realms_raw, "realms.csv"),
        ("technique", registry.techniques_raw, "techniques.csv"),
    ]
    for kind, items, src in groups:
        ids = [it.get("id") for it in items if isinstance(it, dict) and it.get("id")]
        for iid, count in Counter(ids).items():
            if count > 1:
                _add(errors, src, f"duplikat id {kind}",
                     f"id '{iid}' muncul {count}×.")


def validate(registry) -> None:
    """Validasi semua konten yang sudah dimuat DataRegistry. Raise
    DataContractError bila ada pelanggaran — kumpulkan SEMUA dulu, baru lempar."""
    errors: list[str] = []
    _validate_duplicates(registry, errors)
    _validate_config(registry, errors)
    _validate_quests(registry, errors)
    _validate_dialogs(registry, errors)
    _validate_npcs(registry, errors)
    _validate_locations(registry, errors)
    _validate_memories(registry, errors)
    _validate_companions(registry, errors)
    _validate_recipes(registry, errors)
    _validate_csv(registry, errors)
    _validate_key_items(registry, errors)
    if errors:
        head = f"{len(errors)} pelanggaran kontrak data ditemukan saat load:"
        raise DataContractError("\n".join([head] + [f"  {e}" for e in errors]))
