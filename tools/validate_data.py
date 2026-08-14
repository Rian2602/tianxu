#!/usr/bin/env python3
"""Validator data Fase 1 — cek konsistensi seluruh file data.

Menjalankan aturan validasi ENGINE_ARCHITECTURE §14:
 1. Semua JSON parse & CSV well-formed
 2. Semua referensi valid (quest, dialog, NPC, item, musuh, lokasi, teknik, ingatan)
 3. Graf quest acyclic (DAG)
 4. Quest dengan >1 sisi punya choice_id & semua option terpetakan ke dialog
 5. Tidak ada konflik NPC/lokasi/objek antar quest yang bisa aktif bersamaan
 6. ID unik
 7. config.json valid
 8. Side quest butuh available_from {day, hour}; cooldown valid jika ada
 9. repeatable hanya untuk kind side
10. Quest repeatable tidak memakai NPC/lokasi/objek quest utama
11. Resep alkimia valid
12. Toko NPC valid
13. Item weapon punya power; config.roots valid
14. Lokasi is_safe & connections valid
15. Kompanion valid
16. config.battle valid

Pemakaian: python3 tools/validate_data.py  (dari root proyek)
Exit code non-zero jika ada error.
"""

import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

ELEMENTS = {"logam", "kayu", "tanah", "air", "api"}
OBJECTIVE_KINDS = {"talk", "defeat", "gather", "reach", "choose", "spar", "advance_time"}
EFFECT_TYPES = {"morality", "reputation", "relation", "flag", "item", "gold", "start_quest", "branch_select", "technique"}


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.id_sets: dict[str, set[str]] = {}

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    # ---------- baca data ----------

    def read_json(self, rel: str) -> dict | list | None:
        path = DATA / rel
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            self.error(f"{rel}: file tidak ditemukan")
            return None
        except json.JSONDecodeError as e:
            self.error(f"{rel}: JSON rusak — {e}")
            return None

    def read_csv_rows(self, rel: str) -> list[dict]:
        path = DATA / rel
        try:
            with open(path, encoding="utf-8", newline="") as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            self.error(f"{rel}: file tidak ditemukan")
            return []
        except csv.Error as e:
            self.error(f"{rel}: CSV rusak — {e}")
            return []

    # ---------- helper ----------

    def register_ids(self, kind: str, ids: list[str]) -> None:
        self.id_sets.setdefault(kind, set()).update(ids)
        seen: set[str] = set()
        for i in ids:
            if i in seen:
                self.error(f"duplikat id '{i}' di {kind}")
            seen.add(i)

    def has(self, kind: str, id_: str) -> bool:
        return id_ in self.id_sets.get(kind, set())

    # ---------- aturan ----------

    def validate(self) -> bool:
        self._load_all()
        if not self.id_sets.get("quest"):
            return False
        self._check_config()
        self._check_quests()
        self._check_dialogs()
        self._check_memories()
        self._check_recipes()
        self._check_npc_shops()
        self._check_dag()
        self._check_conflicts()
        self._check_reachability()
        return len(self.errors) == 0

    def _load_all(self) -> None:
        # config dimuat paling awal — cek teknik (aturan 13) butuh config.arcs
        self.config = self.read_json("config.json")

        # CSV
        items = self.read_csv_rows("items.csv")
        self.register_ids("item", [r["id"] for r in items])
        enemies = self.read_csv_rows("enemies.csv")
        self.register_ids("enemy", [r["id"] for r in enemies])
        realms = self.read_csv_rows("realms.csv")
        self.register_ids("realm", [r["id"] for r in realms])
        techniques = self.read_csv_rows("techniques.csv")
        self.register_ids("technique", [r["id"] for r in techniques])

        # CSV well-formed & field checks (aturan 1, 13)
        for rows, name, int_fields in [
            (items, "items.csv", ["price", "hp_restore", "qi_restore", "power"]),
            (enemies, "enemies.csv", ["hp", "qi", "attack", "defense", "speed", "exp_reward"]),
            (realms, "realms.csv", ["order", "levels", "base_hp", "base_qi", "hp_per_level", "qi_per_level", "technique_slots"]),
            (techniques, "techniques.csv", ["qi_cost", "power"]),
        ]:
            for r in rows:
                for f in int_fields:
                    try:
                        int(r.get(f, ""))
                    except (TypeError, ValueError):
                        self.error(f"{name}: baris '{r.get('id', '?')}' kolom '{f}' bukan angka")
        for r in items:
            if r["type"] == "weapon" and not r.get("power"):
                self.error(f"items.csv: weapon '{r['id']}' tanpa power (aturan 13)")
        for r in enemies:
            if r.get("element") and r["element"] not in ELEMENTS:
                self.error(f"enemies.csv: elemen '{r['element']}' tidak valid")
        arc_ids = {a.get("id") for a in (self.config or {}).get("arcs", [])}
        for r in techniques:
            if r.get("academy") not in {"elemen", "senjata", "summoning"}:
                self.error(f"techniques.csv: akademi '{r.get('academy')}' tidak valid")
            if r.get("element") and r["element"] not in ELEMENTS:
                self.error(f"techniques.csv: elemen '{r.get('element')}' tidak valid")
            if r.get("kind") not in {"attack", "defend", "heal"}:
                self.error(f"techniques.csv: kind '{r.get('kind')}' tidak valid")
            if r.get("unlock_arc") and r["unlock_arc"] not in arc_ids:
                self.error(f"techniques.csv: unlock_arc '{r.get('unlock_arc')}' bukan arc di config.arcs (aturan 13)")

        # JSON
        quests_main = self.read_json("quests/quests_akademi.json")
        quests_side = self.read_json("quests/quests_side.json")
        quests = (quests_main or {}).get("quests", []) + (quests_side or {}).get("quests", [])
        self.register_ids("quest", [q["id"] for q in quests])
        self.quests = quests

        dialogs_main = self.read_json("dialogs/dialogs_akademi.json")
        self.dialogs = (dialogs_main or {}).get("dialogs", [])
        self.register_ids("dialog", [d["id"] for d in self.dialogs])

        npcs = self.read_json("npcs.json")
        self.npcs = (npcs or {}).get("npcs", [])
        self.register_ids("npc", [n["id"] for n in self.npcs])

        locs = self.read_json("locations.json")
        self.locations = (locs or {}).get("locations", [])
        self.register_ids("location", [l["id"] for l in self.locations])

        memories = self.read_json("memories.json")
        self.memories = (memories or {}).get("memories", [])
        self.register_ids("memory", [m["id"] for m in self.memories])

        recipes = self.read_json("recipes.json")
        self.recipes = (recipes or {}).get("recipes", [])

        companions = self.read_json("companions.json")
        self.companions = (companions or {}).get("companions", [])

    def _check_config(self) -> None:
        cfg = self.config
        if not isinstance(cfg, dict):
            return
        start = cfg.get("starting", {})
        player = start.get("player", {})
        if player.get("realm") and not self.has("realm", player["realm"]):
            self.error(f"config.starting.player.realm '{player['realm']}' tidak ada (aturan 7)")
        if start.get("current_quest") and not self.has("quest", start["current_quest"]):
            self.error(f"config.starting.current_quest tidak ditemukan (aturan 7)")
        if start.get("location") and not self.has("location", start["location"]):
            self.error(f"config.starting.location '{start['location']}' tidak ada")
        roots = cfg.get("roots", {})
        tiers = roots.get("tiers", [])
        tier_ids = {t.get("id") for t in tiers}
        if player.get("roots") and player["roots"] not in tier_ids:
            self.error(f"config.starting.player.roots '{player.get('roots')}' tidak ada di config.roots.tiers")
        for t in tiers:
            m = t.get("exp_multiplier")
            if not isinstance(m, (int, float)) or m <= 0:
                self.error(f"config.roots: tier '{t.get('id')}' exp_multiplier tidak valid (aturan 13)")
        if roots.get("default") not in tier_ids:
            self.error(f"config.roots.default '{roots.get('default')}' tidak ada di tiers (aturan 13)")

        tm = cfg.get("time", {})
        mld = tm.get("month_length_days")
        if mld is not None and (not isinstance(mld, int) or mld <= 0):
            self.error("config.time.month_length_days: harus int > 0 (aturan 7)")
        mn = tm.get("month_names")
        if mn is not None and (not isinstance(mn, list) or len(mn) != 12 or not all(isinstance(x, str) and x for x in mn)):
            self.error("config.time.month_names: harus list 12 nama string non-kosong (aturan 7)")

        cult = cfg.get("cultivation", {})
        tub = cult.get("technique_upgrade_cost_base")
        if tub is not None and (not isinstance(tub, (int, float)) or tub <= 0):
            self.error(f"config.cultivation.technique_upgrade_cost_base: harus > 0 (aturan 7)")
        tg = cult.get("technique_power_growth_per_level")
        if tg is not None and (not isinstance(tg, (int, float)) or tg < 0):
            self.error(f"config.cultivation.technique_power_growth_per_level: harus ≥ 0 (aturan 7)")

        battle = cfg.get("battle", {})
        crit = battle.get("crit_chance")
        if crit is not None and not (isinstance(crit, (int, float)) and 0 <= crit <= 1):
            self.error(f"config.battle.crit_chance: harus 0–1 (aturan 16)")
        if battle.get("turn_order") not in {"fixed_alternate", "speed"}:
            self.error(f"config.battle.turn_order tidak valid (aturan 16)")
        if battle.get("damage_formula") not in {"percent", "flat"}:
            self.error(f"config.battle.damage_formula tidak valid (aturan 16)")

        for a in cfg.get("academies", []):
            if not a.get("skill_pool"):
                self.error(f"config.academies: '{a.get('id')}' tanpa skill_pool")

        # B1: arcs — final_quest harus ada, title/teaser non-kosong, memories_total > 0, branches non-kosong
        seen_arcs: set[str] = set()
        for arc in cfg.get("arcs", []):
            aid = arc.get("id")
            if not aid or aid in seen_arcs:
                self.error(f"config.arcs: id arc kosong/duplikat '{aid}' (aturan 7)")
            seen_arcs.add(aid)
            if not arc.get("final_quest") or not self.has("quest", arc["final_quest"]):
                self.error(f"config.arcs: final_quest '{arc.get('final_quest')}' tidak ada di quest (aturan 7)")
            if not arc.get("title") or not isinstance(arc["title"], str):
                self.error(f"config.arcs: title arc '{aid}' kosong/bukan string (aturan 7)")
            if not arc.get("teaser") or not isinstance(arc["teaser"], str):
                self.error(f"config.arcs: teaser arc '{aid}' kosong/bukan string (aturan 7)")
            mt = arc.get("memories_total")
            if not isinstance(mt, int) or mt <= 0:
                self.error(f"config.arcs: memories_total arc '{aid}' harus int > 0 (aturan 7)")
            if not arc.get("branches") or not isinstance(arc["branches"], dict):
                self.error(f"config.arcs: branches arc '{aid}' kosong/bukan dict (aturan 7)")
            # C3: endings opsional — id unik, title/desc string, condition valid (pola _check_dialog_condition)
            seen_endings: set[str] = set()
            for end in arc.get("endings") or []:
                eid = end.get("id")
                if not eid or eid in seen_endings:
                    self.error(f"config.arcs.{aid}.endings: id ending kosong/duplikat '{eid}' (aturan 7)")
                seen_endings.add(eid)
                if not end.get("title") or not isinstance(end["title"], str):
                    self.error(f"config.arcs.{aid}.endings: title ending '{eid}' kosong/bukan string (aturan 7)")
                if "desc" in end and not isinstance(end.get("desc"), str):
                    self.error(f"config.arcs.{aid}.endings: desc ending '{eid}' bukan string (aturan 7)")
                cond = end.get("condition") or {}
                if not isinstance(cond, dict):
                    self.error(f"config.arcs.{aid}.endings: condition ending '{eid}' bukan dict (aturan 7)")
                else:
                    self._check_dialog_condition(
                        f"arc.{aid}.ending.{eid}", "condition", cond, "condition")

        # B2: fallback lokasi aman saat KO — harus lokasi yang ada dan is_safe
        sfl = cfg.get("world", {}).get("safe_fallback_location")
        if sfl:
            loc = self.has("location", sfl)
            if not loc:
                self.error(f"config.world.safe_fallback_location: lokasi '{sfl}' tidak ada (aturan 7)")
            elif not any(l["id"] == sfl and l.get("is_safe") for l in self.locations):
                self.error(f"config.world.safe_fallback_location: '{sfl}' bukan lokasi aman (aturan 7)")

        for k, v in cfg.get("element_advantage", {}).items():
            if k not in ELEMENTS or v not in ELEMENTS:
                self.error(f"config.element_advantage: '{k}→{v}' tidak valid (aturan 7)")

        # A2: aktivitas berburu data-driven — referensi di config.world.hunt wajib valid
        hunt = cfg.get("world", {}).get("hunt")
        if hunt:
            for eid in hunt.get("pool", []):
                if not self.has("enemy", eid):
                    self.error(f"config.world.hunt.pool: musuh '{eid}' tidak ada di enemies.csv (aturan 7)")
            mb = hunt.get("mini_boss")
            if mb and not self.has("enemy", mb):
                self.error(f"config.world.hunt.mini_boss: musuh '{mb}' tidak ada di enemies.csv (aturan 7)")
            hl = hunt.get("location")
            if hl and not self.has("location", hl):
                self.error(f"config.world.hunt.location: lokasi '{hl}' tidak ada (aturan 7)")
            si = hunt.get("search_item")
            if si and not self.has("item", si):
                self.error(f"config.world.hunt.search_item: item '{si}' tidak ada di items.csv (aturan 7)")
            mbc = hunt.get("mini_boss_chance")
            if mbc is not None and not (isinstance(mbc, (int, float)) and 0 <= mbc <= 1):
                self.error(f"config.world.hunt.mini_boss_chance: harus 0–1 (aturan 7)")
            # P1-3: pool malam + window (GDD §8)
            for eid in hunt.get("night_pool", []):
                if not self.has("enemy", eid):
                    self.error(f"config.world.hunt.night_pool: musuh '{eid}' tidak ada di enemies.csv (aturan 7)")
            nw = hunt.get("night_window")
            if nw:
                for k in ("hour_start", "hour_end"):
                    v = nw.get(k)
                    if not isinstance(v, int) or not 0 <= v <= 23:
                        self.error(f"config.world.hunt.night_window.{k}: harus int 0–23 (aturan 7)")

    def _check_quests(self) -> None:
        for q in self.quests:
            qid = q["id"]
            # referensi objektif (aturan 2)
            obj = q.get("objective", {})
            kind = obj.get("kind")
            if kind not in OBJECTIVE_KINDS:
                self.error(f"quest {qid}: objective.kind '{kind}' tidak dikenal")
            if kind in {"talk", "spar"} and obj.get("npc") and not self.has("npc", obj["npc"]):
                self.error(f"quest {qid}: objective.npc '{obj['npc']}' tidak ada")
            if kind == "defeat":
                for e in obj.get("enemies", []):
                    if not self.has("enemy", e):
                        self.error(f"quest {qid}: objective.enemies '{e}' tidak ada")
                # A2: lapor ke pemberi — npc harus ada (keputusan §17)
                if obj.get("report_to") and not self.has("npc", obj["report_to"]):
                    self.error(f"quest {qid}: objective.report_to '{obj['report_to']}' tidak ada")
            if kind == "gather" and obj.get("item") and not self.has("item", obj["item"]):
                self.error(f"quest {qid}: objective.item '{obj['item']}' tidak ada")
            if kind == "reach" and obj.get("location") and not self.has("location", obj["location"]):
                self.error(f"quest {qid}: objective.location '{obj['location']}' tidak ada")
            if kind == "choose":
                for o in obj.get("options", []):
                    if not o.get("value"):
                        self.error(f"quest {qid}: opsi choose tanpa value")
            if kind == "advance_time":
                if not obj.get("hour") and not obj.get("day_offset"):
                    self.error(f"quest {qid}: objective.advance_time butuh hour/day_offset")

            # on_complete
            oc = q.get("on_complete", {})
            mu = oc.get("memory_unlock")
            if mu:
                for m in (mu if isinstance(mu, list) else [mu]):
                    if not self.has("memory", m):
                        self.error(f"quest {qid}: memory_unlock '{m}' tidak ada")
            for fx in oc.get("effects", []):
                self._check_effect(fx, f"quest {qid} on_complete")
                if fx.get("type") == "item" and not self.has("item", fx.get("id", "")):
                    self.error(f"quest {qid}: efek item '{fx.get('id')}' tidak ada")
                if fx.get("type") == "relation" and not self.has("npc", fx.get("npc", "")):
                    self.error(f"quest {qid}: efek relation npc '{fx.get('npc')}' tidak ada")
                if fx.get("type") == "technique":
                    for tid in (fx.get("id") if isinstance(fx.get("id"), list) else [fx.get("id")]):
                        if tid and not self.has("technique", tid):
                            self.error(f"quest {qid}: efek technique '{tid}' tidak ada di techniques.csv (aturan 13)")

            # giver (aturan 2)
            if q.get("giver") and not self.has("npc", q["giver"]):
                self.error(f"quest {qid}: giver '{q['giver']}' tidak ada")

            # aturan 8: side quest butuh available_from {day, hour} & cooldown valid
            if q.get("kind") == "side":
                af = q.get("available_from")
                if not (isinstance(af, dict) and isinstance(af.get("day"), int) and isinstance(af.get("hour"), int)):
                    self.error(f"quest {qid}: side quest butuh available_from {{day, hour}} (aturan 8)")
                cd = q.get("cooldown")
                if cd is not None and (not isinstance(cd, (int, float)) or cd <= 0):
                    self.error(f"quest {qid}: cooldown harus > 0 (aturan 8)")

            # aturan 9: repeatable hanya side
            if q.get("repeatable") and q.get("kind") != "side":
                self.error(f"quest {qid}: repeatable=true tapi kind='{q.get('kind')}' (aturan 9)")

    def _check_effect(self, fx, where) -> None:
        if not isinstance(fx, dict) or fx.get("type") not in EFFECT_TYPES:
            self.error(f"{where}: efek tidak valid: {fx}")

    def _check_dialogs(self) -> None:
        for d in self.dialogs:
            did = d["id"]
            npc_id = d.get("npc", "")
            if npc_id and not self.has("npc", npc_id):
                self.error(f"dialog {did}: npc '{npc_id}' tidak ada")
            if d.get("start") not in d.get("nodes", {}):
                self.error(f"dialog {did}: start node '{d.get('start')}' tidak ada")
            for nid, node in d.get("nodes", {}).items():
                sp = node.get("speaker", "")
                if sp.startswith("npc:"):
                    if not self.has("npc", sp[4:]):
                        self.error(f"dialog {did} node {nid}: speaker '{sp}' tidak ada")
                elif sp not in {"player", "system", "narration", ""}:
                    self.error(f"dialog {did} node {nid}: speaker '{sp}' tidak dikenal")
                if node.get("next") and node["next"] not in d["nodes"]:
                    self.error(f"dialog {did} node {nid}: next '{node['next']}' tidak ada")
                if node.get("end") and node.get("next"):
                    self.error(f"dialog {did} node {nid}: punya end & next sekaligus")
                self._check_dialog_condition(did, nid, node.get("condition"), "node")
                for c in node.get("choices", []):
                    if c.get("next") and c["next"] not in d["nodes"]:
                        self.error(f"dialog {did} node {nid}: choice next '{c['next']}' tidak ada")
                    self._check_dialog_condition(did, nid, c.get("condition"), "choice")
                    for fx in c.get("effects", []):
                        self._check_effect(fx, f"dialog {did} node {nid}")
                        if fx.get("type") == "start_quest" and not self.has("quest", fx.get("quest", "")):
                            self.error(f"dialog {did}: start_quest '{fx.get('quest')}' tidak ada")
                        if fx.get("type") == "technique":
                            for tid in (fx.get("id") if isinstance(fx.get("id"), list) else [fx.get("id")]):
                                if tid and not self.has("technique", tid):
                                    self.error(f"dialog {did}: efek technique '{tid}' tidak ada di techniques.csv (aturan 13)")

    def _check_dialog_condition(self, did: str, nid: str, cond: dict | None, where: str) -> None:
        """Validasi referensi kondisi dialog (P1-2 relation, P1-1 memory, C2 month).
        C3: dipakai ulang untuk ending — kunci tak dikenal (mis. `mood_min`) ditolak
        agar skema kondisi konsisten dengan `_eval_condition` (subset kondisi dialog)."""
        if not cond:
            return
        # kunci kondisi yang didukung `dialog.py::_eval_condition` (AND multi-kunci)
        allowed = {"flag", "morality_min", "morality_max", "has_item", "realm_min",
                   "academy", "quest_active", "quest_not_active",
                   "relation_min", "relation_max", "memory", "month_min", "month_max"}
        for ck in cond:
            if ck not in allowed:
                self.error(f"dialog {did} {where} {nid}: kunci kondisi '{ck}' tidak dikenal (aturan 7)")
        for ck in ("relation_min", "relation_max"):
            r = cond.get(ck) or {}
            if r.get("npc") and not self.has("npc", r["npc"]):
                self.error(f"dialog {did} {where} {nid}: kondisi {ck} npc '{r['npc']}' tidak ada")
        if cond.get("memory") and not self.has("memory", cond["memory"]):
            self.error(f"dialog {did} {where} {nid}: kondisi memory '{cond['memory']}' tidak ada")
        # C2: kondisi bulan — int 1..12 (12 bulan dalam setahun, month_length_days ≥ 1)
        for ck in ("month_min", "month_max"):
            m = cond.get(ck)
            if m is not None and not (isinstance(m, int) and 1 <= m <= 12):
                self.error(f"dialog {did} {where} {nid}: kondisi {ck} harus int 1..12 (aturan 7)")

    def _check_memories(self) -> None:
        for m in self.memories:
            ub = m.get("unlocked_by_quest")
            for qid in (ub if isinstance(ub, list) else [ub]):
                if qid and not self.has("quest", qid):
                    self.error(f"memory {m['id']}: unlocked_by_quest '{qid}' tidak ada")

    def _check_recipes(self) -> None:
        for r in self.recipes:  # aturan 11
            if not self.has("item", r.get("result", "")):
                self.error(f"resep {r['id']}: hasil '{r.get('result')}' tidak ada (aturan 11)")
            for ing in r.get("ingredients", []):
                if not self.has("item", ing.get("item", "")):
                    self.error(f"resep {r['id']}: bahan '{ing.get('item')}' tidak ada (aturan 11)")
                if ing.get("item") == r.get("result"):
                    self.error(f"resep {r['id']}: bahan sama dengan hasil (aturan 11)")

    def _check_npc_shops(self) -> None:
        for n in self.npcs:  # aturan 12
            if n.get("location") and not self.has("location", n["location"]):
                self.error(f"npc {n['id']}: location '{n['location']}' tidak ada")
            if n.get("default_dialog") and not self.has("dialog", n["default_dialog"]):
                self.error(f"npc {n['id']}: default_dialog '{n['default_dialog']}' tidak ada")
            shop = n.get("shop")
            if shop:
                for side in ("buy", "sell"):
                    for s in shop.get(side, []):
                        if not self.has("item", s.get("item", "")):
                            self.error(f"npc {n['id']}: shop.{side} item '{s.get('item')}' tidak ada (aturan 12)")
            combat = n.get("combat")
            if combat:
                if combat.get("element") not in ELEMENTS:
                    self.error(f"npc {n['id']}: combat.element tidak valid")

        loc_by_id = {l["id"]: l for l in self.locations}
        if self.locations and not any(l.get("is_safe") for l in self.locations):
            self.error("tidak ada lokasi dengan is_safe: true — respawn KO butuh minimal 1 titik aman (aturan 14)")
        for l in self.locations:  # aturan 14
            if not isinstance(l.get("is_safe"), bool):
                self.error(f"lokasi {l['id']}: is_safe harus bool (aturan 14)")
            for c in l.get("connections", []):
                if not self.has("location", c):
                    self.error(f"lokasi {l['id']}: connections '{c}' tidak ditemukan (aturan 14)")
                # koneksi harus dua arah (aturan 14)
                elif l["id"] not in loc_by_id[c].get("connections", []):
                    self.error(f"lokasi {l['id']} ↔ {c}: koneksi tidak simetris (aturan 14)")

        ids = set()
        for c in self.companions:  # aturan 15
            if c.get("element") not in ELEMENTS:
                self.error(f"kompanion {c['id']}: elemen tidak valid (aturan 15)")
            if c["id"] in ids:
                self.error(f"kompanion id duplikat: {c['id']} (aturan 15)")
            ids.add(c["id"])
            for k in ("base_hp", "base_attack", "base_defense", "base_speed"):
                if not isinstance(c.get(k), (int, float)):
                    self.error(f"kompanion {c['id']}: {k} harus angka (aturan 15)")
        # akademi dengan field `companion` harus merujuk kompanion yang ada (aturan 15)
        for a in (self.config or {}).get("academies", []):
            cid = a.get("companion")
            if cid and cid not in ids:
                self.error(f"akademi {a['id']}: companion '{cid}' tidak ditemukan (aturan 15)")

    def _check_dag(self) -> None:
        # aturan 3: acyclic + aturan 4: choice mapping
        by_id = {q["id"]: q for q in self.quests}
        state: dict[str, int] = {}  # 0=belum, 1=diproses, 2=selesai

        def visit(qid: str, path: list[str]) -> None:
            if state.get(qid) == 1:
                self.error(f"siklus terdeteksi: {' → '.join(path + [qid])} (aturan 3)")
                return
            if state.get(qid) == 2:
                return
            state[qid] = 1
            q = by_id[qid]
            for edge in q.get("next", []):
                nxt = edge.get("quest")
                if not nxt:
                    continue
                if nxt not in by_id:
                    self.error(f"quest {qid}: next.quest '{nxt}' tidak ada (aturan 2)")
                    continue
                visit(nxt, path + [qid])
            state[qid] = 2

        for qid in by_id:
            if state.get(qid) != 2:
                visit(qid, [])

        # aturan 4: quest dengan >1 sisi wajib punya choice_id & option terpetakan
        for q in self.quests:
            nexts = q.get("next", [])
            if len(nexts) > 1:
                choices = [e.get("choice_id") for e in nexts]
                if not all(choices):
                    self.error(f"quest {q['id']}: >1 sisi tanpa choice_id (aturan 4)")
                    continue
                cid = choices[0]
                dlg = next((d for d in self.dialogs if d["id"] == cid), None)
                if dlg is None:
                    self.error(f"quest {q['id']}: choice_id '{cid}' tidak ada (aturan 4)")
                    continue
                dialog_options = set()
                for node in dlg.get("nodes", {}).values():
                    for c in node.get("choices", []):
                        if c.get("option"):
                            dialog_options.add(c["option"])
                for e in nexts:
                    if e.get("option") not in dialog_options:
                        self.error(f"quest {q['id']}: sisi '{e.get('branch')}' option '{e.get('option')}' tidak ada di dialog {cid} (aturan 4)")


    def _check_reachability(self) -> None:
        # Semua quest utama harus terjangkau dari quest awal; dan arc harus punya quest terminal (next kosong)
        by_id = {q["id"]: q for q in self.quests}
        start_id = (self.config or {}).get("starting", {}).get("current_quest")
        if not start_id:
            return
        reachable: set[str] = set()
        stack = [start_id]
        while stack:
            qid = stack.pop()
            if qid in reachable:
                continue
            reachable.add(qid)
            q = by_id.get(qid)
            if not q:
                continue
            for e in q.get("next", []):
                if e.get("quest") and e["quest"] not in reachable:
                    stack.append(e["quest"])
        for q in self.quests:
            if q.get("kind") == "main" and q["id"] not in reachable:
                self.error(f"quest utama {q['id']} tidak terjangkau dari quest awal (dead-end/terpencil)")
        mains = [q for q in self.quests if q.get("kind") == "main"]
        if not any(not q.get("next") for q in mains):
            self.error("arc utama tidak punya quest terminal (next kosong) — tidak bisa selesai")

    def _check_conflicts(self) -> None:
        # aturan 5 & 10: quest tidak boleh saling menuntut NPC/lokasi yang sama saat aktif bersamaan
        def claims(q: dict) -> set[str]:
            obj = q.get("objective", {})
            out: set[str] = set()
            if obj.get("kind") in {"talk", "spar"} and obj.get("npc"):
                out.add(f"npc:{obj['npc']}")
            if obj.get("kind") == "reach" and obj.get("location"):
                out.add(f"loc:{obj['location']}")
            return out

        main_q = [q for q in self.quests if q.get("kind") == "main"]
        side_q = [q for q in self.quests if q.get("kind") == "side"]
        main_claims: set[str] = set()
        for q in main_q:
            main_claims |= claims(q)
        for q in side_q:
            overlap = claims(q) & main_claims
            if overlap:
                self.error(f"quest {q['id']}: menuntut {', '.join(sorted(overlap))} yang dipakai quest utama (aturan 5/10)")


def main() -> None:
    v = Validator()
    ok = v.validate()
    if v.errors:
        print(f"VALIDASI GAGAL — {len(v.errors)} error:")
        for e in v.errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    nq = len(v.id_sets.get("quest", set()))
    print(f"VALIDASI LULUS — quest: {nq}, dialog: {len(v.id_sets.get('dialog', set()))}, "
          f"npc: {len(v.id_sets.get('npc', set()))}, lokasi: {len(v.id_sets.get('location', set()))}, "
          f"item: {len(v.id_sets.get('item', set()))}, musuh: {len(v.id_sets.get('enemy', set()))}, "
          f"ingatan: {len(v.id_sets.get('memory', set()))}")


if __name__ == "__main__":
    main()
