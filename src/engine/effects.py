"""Penerapan efek — format type-based (ENGINE_ARCHITECTURE §5.2).

Jenis efek: morality, relation, reputation, flag, item, gold, start_quest,
technique, npc_state, grant_companion, exp, unlock_realm_bonus, status_effect.
`start_quest` hanya valid di konteks dialog (mengaktifkan side quest).
`technique` (C1) memberi teknik baru ke pemain (reward quest/dialog).
`exp` menambah exp ke dantian pemain.
`unlock_realm_bonus` membuka bonus ranah (dari item kultivasi).
`status_effect` menambah efek sementara (debuff/buff).
"""

from __future__ import annotations

from ..loader import DataRegistry
from .events import add_log
from .morality import adjust as adjust_morality
from .state import GameState

# Field wajib per jenis efek — dicek validator saat load.
EFFECT_REQUIRED_FIELDS: dict[str, set[str]] = {
    "flag": {"key"},
    "item": {"id"},
    "relation": {"npc", "value"},
    "reputation": {"faksi", "value"},
    "technique": {"id"},
    "start_quest": {"quest"},
    "npc_state": {"npc"},
    "grant_companion": {"id"},
    "exp": {"value"},
    "unlock_realm_bonus": {"realm"},
    "status_effect": {"effect_type", "days"},
}

EFFECT_TYPES = {
    "morality", "relation", "reputation", "flag", "item", "gold",
    "technique", "start_quest", "npc_state", "grant_companion",
    "exp", "unlock_realm_bonus", "status_effect",
}


def apply(state: GameState, registry: DataRegistry, effects: list | None) -> None:
    for fx in effects or []:
        t = fx.get("type")
        if t == "morality":
            adjust_morality(state, registry, int(fx.get("value", 0)))
        elif t == "relation":
            nid = fx.get("npc")
            if nid:
                state.relations[nid] = state.relations.get(nid, 0) + int(fx.get("value", 0))
        elif t == "reputation":
            faksi = fx.get("faksi", "")
            if faksi:
                state.factions[faksi] = state.factions.get(faksi, 0) + int(fx.get("value", 0))
        elif t == "flag":
            key = fx.get("key")
            if key:
                state.flags[key] = fx.get("value", True)
        elif t == "item":
            iid = fx.get("id")
            count = int(fx.get("count", 1))
            if iid:
                state.inventory[iid] = state.inventory.get(iid, 0) + count
                if state.inventory[iid] <= 0:
                    del state.inventory[iid]
        elif t == "gold":
            state.player.gold += int(fx.get("value", 0))
            if state.player.gold < 0:
                state.player.gold = 0
        elif t == "technique":
            ids = fx.get("id")
            for tid in (ids if isinstance(ids, list) else [ids]):
                if tid and tid not in state.player.techniques:
                    state.player.techniques.append(tid)
        elif t == "start_quest":
            pass  # ditangani khusus oleh dialog/session
        elif t == "npc_state":
            nid = fx.get("npc")
            if nid:
                ov = state.npc_states.setdefault(nid, {})
                if fx.get("location"):
                    ov["location"] = fx["location"]
                if "available" in fx:
                    ov["available"] = fx["available"]
        elif t == "grant_companion":
            cid = fx.get("id")
            if cid and not any(c.get("id") == cid for c in state.companions):
                comp = next((x for x in registry.companions if x.get("id") == cid), None)
                if comp:
                    scale = registry.config.get("companion", {})
                    hp_max = int(comp.get("base_hp", 10)) + state.player.realm_level * int(scale.get("hp_per_level", 12))
                    state.companions.append({"id": cid, "hp": hp_max, "active": True})
                    if not state.active_companion:
                        state.active_companion = cid
                    add_log(state, "narration", f"{comp['name']} mendekat dan menempel padamu.")
        elif t == "exp":
            val = int(fx.get("value", 0))
            state.player.dantian_exp += val
            r = registry.realm_by_id(state.player.realm)
            cap = int(r["dantian_capacity"]) if r and r.get("dantian_capacity") else 20
            if state.player.dantian_exp > cap:
                state.player.dantian_exp = cap
            add_log(state, "system", f"[Sistem] +{val} exp dantian.")
        elif t == "unlock_realm_bonus":
            realm_id = fx.get("realm")
            if realm_id and realm_id not in state.realms_unlocked:
                state.realms_unlocked.append(realm_id)
                r = registry.realm_by_id(realm_id)
                name = r["name"] if r and r.get("name") else realm_id
                add_log(state, "system", f"[Sistem] Bonus ranah terbuka: {name}!")
        elif t == "status_effect":
            eff_type = fx.get("effect_type", "")
            days = int(fx.get("days", 1))
            hp_mult = fx.get("hp_mult")
            atk_mult = fx.get("atk_mult")
            qi_mult = fx.get("qi_mult")
            state.status_effects.append({
                "type": eff_type,
                "days_left": days,
                **({"hp_mult": hp_mult} if hp_mult is not None else {}),
                **({"atk_mult": atk_mult} if atk_mult is not None else {}),
                **({"qi_mult": qi_mult} if qi_mult is not None else {}),
            })
            add_log(state, "system", f"[Sistem] Efek sementara: {eff_type} ({days} hari).")
        else:
            add_log(state, "system", f"[Sistem] Efek tak dikenal: {t}.")
