"""Penerapan efek — format type-based (ENGINE_ARCHITECTURE §5.2).

Jenis efek: morality, relation, reputation, flag, item, gold, start_quest, technique.
`start_quest` hanya valid di konteks dialog (mengaktifkan side quest).
`technique` (C1) memberi teknik baru ke pemain (reward quest/dialog).
"""

from __future__ import annotations

from ..loader import DataRegistry
from .events import add_log
from .morality import adjust as adjust_morality
from .state import GameState


def apply(state: GameState, registry: DataRegistry, effects: list | None) -> None:
    for fx in effects or []:
        t = fx.get("type")
        if t == "morality":
            adjust_morality(state, registry, fx.get("value", 0))
        elif t == "relation":
            nid = fx.get("npc")
            if nid:
                state.relations[nid] = state.relations.get(nid, 0) + fx.get("value", 0)
        elif t == "reputation":
            key = "rep_" + fx.get("faksi", "?")
            state.flags[key] = state.flags.get(key, 0) + fx.get("value", 0)
        elif t == "flag":
            state.flags[fx["key"]] = fx.get("value", True)
        elif t == "item":
            iid = fx.get("id")
            count = fx.get("count", 1)
            if iid:
                state.inventory[iid] = state.inventory.get(iid, 0) + count
                if state.inventory[iid] <= 0:
                    del state.inventory[iid]
        elif t == "gold":
            state.player.gold += fx.get("value", 0)
            if state.player.gold < 0:
                state.player.gold = 0
        elif t == "technique":
            ids = fx.get("id")
            for tid in (ids if isinstance(ids, list) else [ids]):
                if tid and tid not in state.player.techniques:
                    state.player.techniques.append(tid)
        elif t == "start_quest":
            pass  # ditangani khusus oleh dialog/session
        else:
            add_log(state, "system", f"[System] Efek tak dikenal: {t}.")
