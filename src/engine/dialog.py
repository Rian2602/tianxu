"""Dialog engine — ENGINE_ARCHITECTURE §5.2/§7.

- Entri kondisional: node ber-`condition` di level atas dialog dipilih yang
  pertama (urutan JSON) kondisinya benar; jika tidak ada, pakai `start`.
- Opsi (choice) disembunyikan jika `condition`-nya salah, atau ber-efek
  `start_quest` untuk quest yang tidak dapat ditawarkan.
- Saat dialog berakhir, sesi menangani objektif quest (talk/spar) & pilihan cabang.
"""

from __future__ import annotations

from typing import Any

from ..loader import DataRegistry
from .effects import apply as apply_effects
from .state import GameState


class DialogEngine:
    def __init__(self, registry: DataRegistry, state: GameState, quest_engine) -> None:
        self.reg = registry
        self.state = state
        self.quest_engine = quest_engine
        self.current: dict | None = None
        self.node_id: str | None = None
        self.last_npc: str | None = None
        self.chosen_option: str | None = None
        self.visited: set[str] = set()  # A3: semua node yang dimainkan

    # ---------- mulai / lanjut ----------

    def start(self, dialog_id: str, forced_node: str | None = None) -> dict | None:
        """Mulai dialog. `forced_node` (A3: objective talk quest) memaksa node awal
        bila node itu ada di dialog; jika tidak ada → fallback `_resolve_entry`."""
        dlg = self.reg.dialog(dialog_id)
        if not dlg:
            return None
        self.current = dlg
        self.last_npc = dlg.get("npc") or None
        self.chosen_option = None
        self.visited = set()  # reset per dialog
        nodes = dlg.get("nodes", {})
        if forced_node and forced_node in nodes:
            self.node_id = forced_node
        else:
            self.node_id = self._resolve_entry(dlg)
        self.visited.add(self.node_id)
        self.state.pending_dialog = dialog_id
        return self.view()

    def choose(self, choice_index: int) -> dict | None:
        if not self.current or not self.node_id:
            return None
        node = self.current["nodes"][self.node_id]
        choices = self._visible_choices(node)
        if choice_index < 0 or choice_index >= len(choices):
            return self.view()
        ch = choices[choice_index]
        apply_effects(self.state, self.reg, ch.get("effects"))
        # efek start_quest diaktifkan di sini (side quest mulai aktif)
        for fx in ch.get("effects", []):
            if fx.get("type") == "start_quest":
                self.quest_engine.start_side(fx["quest"])
        if ch.get("option"):
            self.chosen_option = ch["option"]
        nxt = ch.get("next")
        if nxt:
            self.node_id = nxt
            self.visited.add(nxt)
            return self.view()
        return self._end()

    def advance(self) -> dict | None:
        """Lanjut node TANPA pilihan (tekan enter)."""
        if not self.current or not self.node_id:
            return None
        node = self.current["nodes"][self.node_id]
        if node.get("choices"):
            return self.view()
        nxt = node.get("next")
        if nxt:
            self.node_id = nxt
            self.visited.add(nxt)
            return self.view()
        return self._end()

    # ---------- internal ----------

    def _resolve_entry(self, dlg: dict) -> str:
        nodes = dlg.get("nodes", {})
        for nid, node in nodes.items():
            cond = node.get("condition")
            if cond and self._eval(cond):
                return nid
        return dlg.get("start", next(iter(nodes), ""))

    def _visible_choices(self, node: dict) -> list[dict]:
        out = []
        for ch in node.get("choices", []):
            if ch.get("condition") and not self._eval(ch["condition"]):
                continue
            if any(fx.get("type") == "start_quest" for fx in ch.get("effects", [])):
                qid = next(fx.get("quest") for fx in ch["effects"] if fx.get("type") == "start_quest")
                if not self.quest_engine.is_offerable(qid):
                    continue
            out.append(ch)
        return out

    def _end(self) -> dict | None:
        self.last_node = self.node_id
        self.last_nodes = set(self.visited)  # A3: snapshot semua node yang dimainkan
        self.node_id = None
        self.current = None
        self.state.pending_dialog = None
        return {"ended": True}

    def view(self) -> dict:
        node = self.current["nodes"][self.node_id]
        choices = self._visible_choices(node)
        return {
            "dialog_id": self.current["id"],
            "node_id": self.node_id,
            "speaker": node.get("speaker", ""),
            "text": node.get("text", ""),
            "choices": [{"index": i, "label": c["label"]} for i, c in enumerate(choices)],
            "ended": False,
        }

    # ---------- kondisi ----------

    @staticmethod
    def _eval_condition(state: GameState, cond: dict[str, Any], registry: DataRegistry | None = None) -> bool:
        s = state
        # C3: `flag` adalah cek AND biasa — TIDAK boleh early-return (bug laten:
        # kombinasi `flag` + kondisi lain mengabaikan kondisi lain). Data dialog
        # existing memakai flag tunggal; kombinasi multi-kunci kini benar-benar AND.
        if "flag" in cond:
            f = cond["flag"]
            # flag yang tidak pernah diset dianggap False (bukan None)
            if s.flags.get(f["key"], False) != f.get("value", True):
                return False
        if "morality_min" in cond:
            if s.player.morality < cond["morality_min"]:
                return False
        if "morality_max" in cond:
            if s.player.morality > cond["morality_max"]:
                return False
        if "has_item" in cond:
            if s.inventory.get(cond["has_item"], 0) < 1:
                return False
        if "has_items" in cond:
            # jumlah spesifik: { "item": "material_herba", "value": 3 }
            h = cond["has_items"]
            if s.inventory.get(h.get("item", ""), 0) < h.get("value", 1):
                return False
        if "defeated_min" in cond:
            # progres kill side quest: { "quest": "q_side_berburu", "value": 2 }
            dm = cond["defeated_min"]
            prog = s.active_side_quests.get(dm.get("quest", ""), {})
            if prog.get("defeated", 0) < dm.get("value", 1):
                return False
        if "realm_min" in cond:
            if registry is None:
                return False
            order_cur = int(registry.realms[s.player.realm]["order"])
            order_min = int(registry.realms[cond["realm_min"]]["order"])
            if order_cur < order_min:
                return False
        if "academy" in cond:
            if s.player.academy != cond["academy"]:
                return False
        if "quest_active" in cond:
            qid = cond["quest_active"]
            if qid != s.current_quest and qid not in s.active_side_quests:
                return False
        if "quest_not_active" in cond:
            qid = cond["quest_not_active"]
            if qid == s.current_quest or qid in s.active_side_quests:
                return False
        if "month_min" in cond:
            if registry is None:
                return False
            if s.month(registry) < int(cond["month_min"]):
                return False
        if "month_max" in cond:
            if registry is None:
                return False
            if s.month(registry) > int(cond["month_max"]):
                return False
        if "relation_min" in cond:
            r = cond["relation_min"]
            if s.relations.get(r["npc"], 0) < r["value"]:
                return False
        if "relation_max" in cond:
            r = cond["relation_max"]
            if s.relations.get(r["npc"], 0) > r["value"]:
                return False
        if "memory" in cond:
            if cond["memory"] not in s.memories:
                return False
        return True

    def _eval(self, cond: dict[str, Any]) -> bool:
        return DialogEngine._eval_condition(self.state, cond, self.reg)
