"""Pembaca data — memuat semua file JSON/CSV ke struktur Python.

Data dipegang sebagai dict (data-driven): menambah field di data tidak
memerlukan perubahan kode. Lookup disediakan lewat dict index.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


class DataRegistry:
    """Indeks semua data game (dibaca sekali saat startup)."""

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = Path(data_dir)

        self.config = self._json("config.json")

        # Per-arc files — glob (bukan hardcode nama file): arc baru = taruh file
        # baru di folder, nol sentuhan kode. Subfolder (mis. `_inactive/`) tidak
        # ikut terbaca — file arc berikutnya yang belum aktif ditaruh di sana.
        self.quests: list[dict] = []
        self.quest_src_list: list[str] = []
        for f in sorted((self.data_dir / "quests").glob("*.json")):
            fname = f"quests/{f.name}"
            for q in self._json(fname)["quests"]:
                self.quests.append(q)
                self.quest_src_list.append(fname)

        self.dialogs: list[dict] = []
        self.dialog_src_list: list[str] = []
        for f in sorted((self.data_dir / "dialogs").glob("*.json")):
            fname = f"dialogs/{f.name}"
            for d in self._json(fname)["dialogs"]:
                self.dialogs.append(d)
                self.dialog_src_list.append(fname)
        self.npcs = self._json("npcs.json")["npcs"]
        self.locations = self._json("locations.json")["locations"]
        # Fitur opsional — tema baru boleh tidak punya ingatan/roh/resep/kunci.
        # Tanpa guard ini, mengganti data story = FileNotFoundError saat boot.
        self.memories = []
        try:
            self.memories = self._json("memories.json")["memories"]
        except (FileNotFoundError, KeyError):
            pass
        try:
            self.recipes = self._json("recipes.json")["recipes"]
        except (FileNotFoundError, KeyError):
            self.recipes = []
        self.companions = []
        try:
            self.companions = self._json("companions.json")["companions"]
        except (FileNotFoundError, KeyError):
            pass

        # Key items — separate file for use effects (CSV can't handle nested JSON).
        # PER-INSTANCE (bukan global modul): dua DataRegistry dengan data dir
        # berbeda dalam satu proses tidak boleh saling mencemari key item.
        self.key_items: dict[str, dict] = {}
        try:
            ki_data = self._json("key_items.json")["key_items"]
            for ki in ki_data:
                if ki.get("id"):
                    self.key_items[ki["id"]] = ki
        except (FileNotFoundError, KeyError, TypeError):
            pass  # key_items.json is optional

        # Faksi — OPSIONAL (tema tanpa faksi boleh tidak punya file ini). Bila
        # ada, validator memakai `registry.factions` untuk cross-reference
        # effect `reputation` & condition `faction_min`/`faction_max` (docs 05).
        self.factions: list[dict] = []
        try:
            self.factions = self._json("factions.json")["factions"]
        except (FileNotFoundError, KeyError, TypeError):
            pass  # factions.json is optional

        self.items_raw = self._csv("items.csv")
        self.items = {r["id"]: r for r in self.items_raw}
        self.enemies_raw = self._csv("enemies.csv")
        self.enemies = {r["id"]: r for r in self.enemies_raw}
        self.realms_raw = self._csv("realms.csv")
        self.realms = {r["id"]: r for r in self.realms_raw}
        self.techniques_raw = self._csv("techniques.csv")
        self.techniques = {r["id"]: r for r in self.techniques_raw}

        # lookup index — entri tanpa id dilewati (validator #1 melaporkannya
        # dengan pesan jelas; tanpa guard ini loader KeyError duluan)
        self.quest_by_id = {q["id"]: q for q in self.quests if q.get("id")}
        self.dialog_by_id = {d["id"]: d for d in self.dialogs if d.get("id")}
        self.npc_by_id = {n["id"]: n for n in self.npcs if n.get("id")}
        self.location_by_id = {l["id"]: l for l in self.locations if l.get("id")}
        self.memory_by_id = {m["id"]: m for m in self.memories if m.get("id")}
        self.faction_by_id = {f["id"]: f for f in self.factions if f.get("id")}

        # konfigurasi turunan
        self.roots_tier = {t["id"]: t for t in self.config.get("roots", {}).get("tiers", [])}
        self.element_advantage = self.config.get("element_advantage", {})

        # hunting zones — multi-zone (F2.3): world.hunts[] kanonik, world.hunt legacy
        self.hunts: list[dict] = []
        world_cfg = self.config.get("world") or {}
        hunts_list = world_cfg.get("hunts")
        if isinstance(hunts_list, list):
            self.hunts = list(hunts_list)
        elif isinstance(world_cfg.get("hunt"), dict):
            legacy = dict(world_cfg["hunt"])
            legacy["id"] = "legacy"
            self.hunts = [legacy]

        from .validate import validate
        validate(self)

    # ---------- pembaca file ----------

    def _json(self, rel: str):
        with open(self.data_dir / rel, encoding="utf-8") as f:
            return json.load(f)

    def _csv(self, rel: str) -> list[dict]:
        with open(self.data_dir / rel, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    # ---------- bantuan umum ----------

    def realm_by_id(self, realm_id: str) -> dict | None:
        return self.realms.get(realm_id)

    def quest(self, qid: str) -> dict | None:
        return self.quest_by_id.get(qid)

    def dialog(self, did: str) -> dict | None:
        return self.dialog_by_id.get(did)

    def npc(self, nid: str) -> dict | None:
        return self.npc_by_id.get(nid)

    def location(self, lid: str) -> dict | None:
        return self.location_by_id.get(lid)

    def item(self, iid: str) -> dict | None:
        return self.items.get(iid)

    def enemy(self, eid: str) -> dict | None:
        return self.enemies.get(eid)

    def memory(self, mid: str) -> dict | None:
        return self.memory_by_id.get(mid)

    def technique(self, tid: str) -> dict | None:
        return self.techniques.get(tid)

    def hunts_for_location(self, location_id: str) -> list[dict]:
        return [h for h in self.hunts if h.get("location") == location_id]

    def academy_curriculum(self, academy: str) -> list[dict]:
        """Daftar teknik kurikulum untuk suatu akademi/paviliun (berurutan)."""
        for a in self.config.get("academies", []):
            if a.get("id") == academy:
                curr = a.get("curriculum", [])
                return [self.techniques[tid] for tid in curr if tid in self.techniques]
        return []

    # ---------- pemain ----------

    def player_techniques(self, academy: str, realm: str | None = None,
                          completed_quests: frozenset = frozenset(),
                          owned: tuple = ()) -> list[dict]:
        """Teknik yang tersedia untuk pemain: hanya teknik yang benar-benar telah
        dipelajari (`owned` / `state.player.techniques`) dan teknik lintas-arc yang terbuka (`unlock_arc`),
        dibatasi oleh ranah pemain (H4)."""
        out: list[dict] = []
        # teknik yang dimiliki / dipelajari (C1 / Skill Learning System)
        for tid in owned:
            t = self.techniques.get(tid)
            if t and t not in out:
                out.append(t)
        # teknik lintas akademi: unlock_arc → arc selesai bila final_quest-nya di completed_quests
        done_arcs = {
            a["id"] for a in self.config.get("arcs", [])
            if a.get("final_quest") in completed_quests
        }
        out += [
            t for t in self.techniques.values()
            if t.get("unlock_arc") and t["unlock_arc"] in done_arcs
            and t not in out
        ]
        if realm:
            cur_r = self.realms.get(realm)
            if cur_r:
                order_cur = int(cur_r["order"])
                out = [
                    t for t in out
                    if int(self.realms.get(t.get("realm_required", realm), cur_r)["order"]) <= order_cur
                ]
        return out

