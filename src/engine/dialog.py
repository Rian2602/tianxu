"""Dialog engine — ENGINE_ARCHITECTURE §5.2/§7.

- Entri kondisional: node ber-`condition` di level atas dialog dipilih yang
  pertama (urutan JSON) kondisinya benar; jika tidak ada, pakai `start`.
- Opsi (choice) disembunyikan jika `condition`-nya salah, atau ber-efek
  `start_quest` untuk quest yang tidak dapat ditawarkan.
- Saat dialog berakhir, sesi menangani objektif quest (talk/spar) & pilihan cabang.
"""

from __future__ import annotations

import random
from typing import Any

from ..loader import DataRegistry
from .effects import apply as apply_effects
from .events import add_log
from .state import GameState


class DialogEngine:
    """Mesin dialog — mengelola percakapan NPC, pilihan, dan integrasi quest."""

    def __init__(self, registry: DataRegistry, state: GameState, quest_engine) -> None:
        self.reg = registry
        self.state = state
        self.quest_engine = quest_engine
        self.current: dict | None = None
        self.node_id: str | None = None
        self.last_node: str | None = None
        self.last_nodes: set[str] = set()  # A3: semua node yang dimainkan
        self.last_npc: str | None = None
        self.chosen_option: str | None = None
        self.visited: set[str] = set()  # A3: semua node yang dimainkan
        self.last_dialog_id: str | None = None
        self.resolved_random_texts: dict[str, str] = {}
        if self.state.pending_dialog:
            self.start(self.state.pending_dialog)

    # ---------- mulai / lanjut ----------

    def start(self, dialog_id: str, forced_node: str | None = None) -> dict | None:
        """Mulai dialog. `forced_node` (A3: objective talk quest) memaksa node awal
        bila node itu ada di dialog; jika tidak ada → fallback `_resolve_entry`."""
        dlg = self.reg.dialog(dialog_id)
        if not dlg:
            self.state.pending_dialog = None
            return None
        self.current = dlg
        self.last_npc = dlg.get("npc") or None
        self.chosen_option = None
        self.visited = set()  # reset per dialog
        self.resolved_random_texts = {}
        nodes = dlg.get("nodes", {})
        if forced_node and forced_node in nodes:
            self.node_id = forced_node
        else:
            self.node_id = self._resolve_entry(dlg)
        if not self.node_id or self.node_id not in nodes:
            self.current = None
            self.node_id = None
            self.state.pending_dialog = None
            return None
        self._mark_once()
        self.visited.add(self.node_id)
        self.state.pending_dialog = dialog_id
        return self.view()

    def can_start(self, dialog_id: str) -> bool:
        """Apakah dialog bisa dimulai dalam state saat ini (non-mutatif).

        Dipakai resolver routing dialog: slot yang tak punya entry terjangkau
        (mis. semua node `once` sudah dimainkan, atau start node ber-condition
        salah) jatuh ke slot prioritas berikutnya. Semantik mengikuti
        `_resolve_entry`."""
        dlg = self.reg.dialog(dialog_id)
        return bool(dlg) and bool(self._resolve_entry(dlg))

    def has_pending_once_entry(self, dialog_id: str) -> bool:
        """Apakah dialog punya reaksi naratif tertunda — entry yang ter-resolve
        ber-`once` dan belum dimainkan (non-mutatif).

        Dipakai resolver routing (langkah 4): reaksi naratif (mis. node `once`
        cabang 3a/3b) harus dimainkan dulu — selama masih ada, side offer rutin
        tidak boleh menimpanya. Hanya node `once` yang memblokir; entry
        kondisional biasa (mis. story gate `node_belum_kenal`) tidak — kontennya
        tetap muncul via fallback umum, offer/intimacy tetap bisa menang sesuai
        prioritasnya."""
        dlg = self.reg.dialog(dialog_id)
        if not dlg:
            return False
        nid = self._resolve_entry(dlg)
        if not nid:
            return False
        node = dlg.get("nodes", {}).get(nid, {})
        return bool(node.get("once") and not self._once_seen(dialog_id, nid))

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
            self._mark_once()
            self.visited.add(nxt)
            return self.view()
        return self._end()

    def advance(self) -> dict | None:
        """Lanjut node TANPA pilihan (tekan enter) — auto-lewati node perantara.

        Alur teks murni (node ber-`choices` dipilih opsi pertama, node ber-`next`
        diikuti) diteruskan sampai dialog berakhir atau berhenti di node yang
        butuh pilihan eksplisit. Guard iterasi mencegah loop tak hingga bila data
        dialog punya siklus (defense-in-depth; data valid tidak akan begini)."""
        if not self.current or not self.node_id:
            return None
        guard = 0
        while self.current and self.node_id and guard < 100:
            guard += 1
            node = self.current["nodes"][self.node_id]
            choices = self._visible_choices(node)
            if choices:
                res = self.choose(0)
                if not res or res.get("ended"):
                    return res
                continue
            nxt = node.get("next")
            if nxt:
                self.node_id = nxt
                self._mark_once()
                self.visited.add(nxt)
                continue
            return self._end()
        return self.view()

    # ---------- internal ----------

    def _resolve_entry(self, dlg: dict) -> str:
        nodes = dlg.get("nodes", {})
        for nid, node in nodes.items():
            if node.get("once") and self._once_seen(dlg.get("id", ""), nid):
                continue
            cond = node.get("condition")
            if cond and self._eval(cond):
                return nid
        start = dlg.get("start", next(iter(nodes), ""))
        if start and start in nodes:
            snode = nodes[start]
            if snode.get("once") and self._once_seen(dlg.get("id", ""), start):
                return ""
            sc = snode.get("condition")
            if sc and not self._eval(sc):
                return ""
            return start
        return ""

    @staticmethod
    def _once_key(dialog_id: str, node_id: str) -> str:
        return f"dialog_once:{dialog_id}:{node_id}"

    def _once_seen(self, dialog_id: str, node_id: str) -> bool:
        return bool(self.state.flags.get(self._once_key(dialog_id, node_id), False))

    def _mark_once(self) -> None:
        """Node `once` hanya dimainkan sekali — tandai di flags (round-trip save)."""
        if not self.current or not self.node_id:
            return
        node = self.current.get("nodes", {}).get(self.node_id)
        if node and node.get("once"):
            self.state.flags[self._once_key(self.current["id"], self.node_id)] = True

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
        self.last_dialog_id = self.current["id"] if self.current else None
        self.last_node = self.node_id
        self.last_nodes = set(self.visited)  # A3: snapshot semua node yang dimainkan
        self.node_id = None
        self.current = None
        self.state.pending_dialog = None
        self.resolved_random_texts = {}
        return {"ended": True}

    def view(self) -> dict | None:
        """Tampilan dialog untuk UI — speaker, text, choices."""
        if not self.current or not self.node_id:
            if self.state.pending_dialog:
                started = self.start(self.state.pending_dialog)
                if started:
                    return started
                self.state.pending_dialog = None
            return None
        nodes = self.current.get("nodes", {})
        node = nodes.get(self.node_id)
        if not node:
            return None
        if "random_text" in node:
            if not hasattr(self, "resolved_random_texts") or not isinstance(self.resolved_random_texts, dict):
                self.resolved_random_texts = {}
            if self.node_id not in self.resolved_random_texts:
                opts = node["random_text"]
                self.resolved_random_texts[self.node_id] = random.choice(opts) if opts else ""
            text = self.resolved_random_texts[self.node_id]
        else:
            text = node.get("text", "")
        choices = self._visible_choices(node)
        return {
            "dialog_id": self.current["id"],
            "node_id": self.node_id,
            "speaker": node.get("speaker", ""),
            "text": text,
            "choices": [{"index": i, "label": c["label"]} for i, c in enumerate(choices)],
            "ended": False,
        }

    # ---------- kondisi ----------

    @staticmethod
    def _eval_condition(state: GameState, cond: dict[str, Any], registry: DataRegistry | None = None) -> bool:
        s = state
        if not cond:
            return True
        # Kunci tak dikenal → False (fail-safe) + log peringatan.
        unknown = set(cond) - CONDITION_KEYS
        if unknown:
            for k in sorted(unknown):
                add_log(s, "system", f"[Sistem] Kondisi dialog tak dikenal: '{k}'.")
            return False
        # C3: `flag` adalah cek AND biasa — TIDAK boleh early-return (bug laten:
        # kombinasi `flag` + kondisi lain mengabaikan kondisi lain). Data dialog
        # existing memakai flag tunggal; kombinasi multi-kunci kini benar-benar AND.
        if "flag" in cond:
            f = cond["flag"]
            # flag yang tidak pernah diset dianggap False (bukan None)
            if s.flags.get(f["key"], False) != f.get("value", True):
                return False
        if "flags" in cond:
            # A07: multi-flag AND — Hidden Resolution (docs 11) butuh kombinasi
            # SEMUA kondisi independen terpenuhi, bukan satu flag.
            for f in cond["flags"]:
                if s.flags.get(f["key"], False) != f.get("value", True):
                    return False
        if "flag_not" in cond:
            # A07: negasi flag — forbidden condition (docs 11): flag TIDAK boleh
            # bernilai value. Menerima dict tunggal ATAU list (multi-negasi AND).
            # Flag belum diset = False → lolos selama value != False.
            items = cond["flag_not"]
            if isinstance(items, dict):
                items = [items]
            for f in items:
                if s.flags.get(f["key"], False) == f.get("value", True):
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
            cur_r = registry.realms.get(s.player.realm)
            min_r = registry.realms.get(cond["realm_min"])
            if not cur_r or not min_r:
                return False
            if int(cur_r["order"]) < int(min_r["order"]):
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
            mid = cond["memory"]
            found = False
            for m in s.memories:
                if (m["id"] if isinstance(m, dict) else m) == mid:
                    found = True
                    break
            if not found:
                return False
        if "faction_min" in cond:
            fm = cond["faction_min"]
            if s.factions.get(fm["faksi"], 0) < fm["value"]:
                return False
        if "faction_max" in cond:
            fm = cond["faction_max"]
            if s.factions.get(fm["faksi"], 0) > fm["value"]:
                return False
        return True

    def _eval(self, cond: dict[str, Any]) -> bool:
        return DialogEngine._eval_condition(self.state, cond, self.reg)


# Kunci kondisi yang dikenal engine — satu sumber kebenaran untuk validator.
CONDITION_KEYS = frozenset({
    "flag", "flags", "flag_not", "morality_min", "morality_max", "has_item",
    "has_items", "defeated_min", "realm_min", "academy", "quest_active",
    "quest_not_active", "month_min", "month_max", "relation_min",
    "relation_max", "memory", "faction_min", "faction_max",
})

CONDITION_NUMERIC_KEYS = frozenset(
    {"morality_min", "morality_max", "month_min", "month_max"})

CONDITION_VALUE_NUMERIC_KEYS = frozenset(
    {"has_items", "defeated_min", "relation_min", "relation_max",
     "faction_min", "faction_max"})

CONDITION_STRING_KEYS = frozenset(
    {"has_item", "realm_min", "academy", "quest_active", "quest_not_active", "memory"})

CONDITION_REQUIRED_FIELDS: dict[str, set[str]] = {
    "flag": {"key"},
    "flag_not": {"key"},
    "has_items": {"item"},
    "defeated_min": {"quest"},
    "relation_min": {"npc", "value"},
    "relation_max": {"npc", "value"},
    "faction_min": {"faksi", "value"},
    "faction_max": {"faksi", "value"},
}

# Dispatch table — validate & tests derive kind sets from these.
CONDITION_CHECKERS: dict[str, object] = {k: None for k in CONDITION_KEYS}
