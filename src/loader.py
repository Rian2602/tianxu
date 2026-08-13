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

        main_quests = self._json("quests/quests_akademi.json")["quests"]
        side_quests = self._json("quests/quests_side.json")["quests"]
        self.quests = main_quests + side_quests

        self.dialogs = self._json("dialogs/dialogs_akademi.json")["dialogs"]
        self.npcs = self._json("npcs.json")["npcs"]
        self.locations = self._json("locations.json")["locations"]
        self.memories = self._json("memories.json")["memories"]
        self.recipes = self._json("recipes.json")["recipes"]
        self.companions = self._json("companions.json")["companions"]

        self.items = {r["id"]: r for r in self._csv("items.csv")}
        self.enemies = {r["id"]: r for r in self._csv("enemies.csv")}
        self.realms = {r["id"]: r for r in self._csv("realms.csv")}
        self.techniques = {r["id"]: r for r in self._csv("techniques.csv")}

        # lookup index
        self.quest_by_id = {q["id"]: q for q in self.quests}
        self.dialog_by_id = {d["id"]: d for d in self.dialogs}
        self.npc_by_id = {n["id"]: n for n in self.npcs}
        self.location_by_id = {l["id"]: l for l in self.locations}
        self.memory_by_id = {m["id"]: m for m in self.memories}

        # konfigurasi turunan
        self.roots_tier = {t["id"]: t for t in self.config.get("roots", {}).get("tiers", [])}
        self.element_advantage = self.config.get("element_advantage", {})

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

    # ---------- pemain ----------

    def player_techniques(self, academy: str) -> list[dict]:
        """Teknik yang tersedia untuk akademi pilihan pemain (skill_pool)."""
        pool = ""
        for a in self.config.get("academies", []):
            if a["id"] == academy:
                pool = a.get("skill_pool", [""])[0] if a.get("skill_pool") else ""
                break
        if not pool:
            return []
        prefix = pool.rstrip("*")
        return [t for t in self.techniques.values() if t["id"].startswith(prefix)]
