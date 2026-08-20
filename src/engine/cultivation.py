"""Progresi kultivasi — dantian-based, meditasi untuk breakthrough.

Aturan baru:
- exp HANYA dari consumable items (pil kultivasi, beast core)
- exp mengisi dantian (dantian_exp), bukan auto-level
- Dantian penuh → meditasi → RNG breakthrough
- Breakthrough sukses: advance tier/realm, reset dantian
- Breakthrough gagal: reset dantian, efek sementara (debuff)
"""

from __future__ import annotations

import random

from ..loader import DataRegistry
from .events import add_log
from .state import GameState


def gain_exp(state: GameState, registry: DataRegistry, amount: int) -> None:
    """Tambah exp ke dantian — dari consumable items."""
    if amount <= 0:
        return
    amount = round(amount * state.exp_multiplier(registry))
    state.player.dantian_exp += amount
    cap = state.exp_next(registry)
    if state.player.dantian_exp > cap:
        state.player.dantian_exp = cap
    add_log(state, "system", f"[Sistem] Dantian +{amount} exp ({state.player.dantian_exp}/{cap}).")


def meditate(state: GameState, registry: DataRegistry) -> dict:
    """Meditasi — coba breakthrough jika dantian penuh.

    Returns dict with keys: success (bool), message (str), detail (str).
    Checks pil_sukses_active for +30% success, pil_aman_active for no debuff.
    """
    cap = state.exp_next(registry)
    if state.player.dantian_exp < cap:
        return {"success": False, "message": "Dantian belum penuh.", "detail": f"{state.player.dantian_exp}/{cap}"}

    realm_data = registry.realms.get(state.player.realm)
    if not realm_data:
        return {"success": False, "message": "Ranah tak dikenal.", "detail": state.player.realm}

    tiers = int(realm_data.get("tiers", 1) or 1)
    success_rate = float(realm_data.get("meditation_success_rate", 0.5) or 0.5)
    # pil_sukses: +30% success rate
    if state.pil_sukses_active:
        success_rate = min(1.0, success_rate + 0.3)

    roll = random.random()
    if roll < success_rate:
        # Success — advance tier or breakthrough
        state.player.dantian_exp = 0
        if state.player.realm_level < tiers:
            state.player.realm_level += 1
            tier_name = _tier_name(state.player.realm_level)
            realm_name = realm_data.get("name_pinyin", state.player.realm)
            msg = f"Meditasi berhasil! {realm_name} {tier_name}."
            if state.pil_sukses_active:
                msg += " (Pil Sukses membantu!)"
            add_log(state, "system", f"[Sistem] {msg}")
            state.player.hp = state.max_hp(registry)
            state.player.qi = state.max_qi(registry)
            return {"success": True, "message": msg, "detail": tier_name}
        else:
            ok = _breakthrough(state, registry)
            if ok:
                new_realm = registry.realms.get(state.player.realm)
                name = new_realm.get("name_pinyin", state.player.realm) if new_realm else state.player.realm
                msg = f"Meditasi berhasil! Terobosan ke {name}!"
                if state.pil_sukses_active:
                    msg += " (Pil Sukses membantu!)"
                add_log(state, "system", f"[Sistem] {msg}")
                state.player.hp = state.max_hp(registry)
                state.player.qi = state.max_qi(registry)
                return {"success": True, "message": msg, "detail": name}
            else:
                msg = "Kau di puncak ranah ini — tidak ada yang lebih tinggi."
                add_log(state, "system", f"[Sistem] {msg}")
                return {"success": True, "message": msg, "detail": "puncak"}
    else:
        # Failure
        lost = state.player.dantian_exp
        state.player.dantian_exp = 0
        if state.pil_aman_active:
            msg = f"Meditasi gagal! Dantian kosong, tapi Pil Aman melindungimu dari deviasi."
            add_log(state, "system", f"[Sistem] {msg} (-{lost} exp dantian)")
        else:
            state.status_effects.append({
                "type": "cultivation_deviation",
                "days_left": 3,
                "hp_mult": 0.9,
                "atk_mult": 0.9,
            })
            msg = f"Meditasi gagal! Qi deviasi — dantian kosong, -10% stat selama 3 hari."
            add_log(state, "system", f"[Sistem] {msg} (-{lost} exp dantian)")
        return {"success": False, "message": msg, "detail": f"-{lost} exp"}


def tick_status_effects(state: GameState) -> list[str]:
    """Kurangi durasi status effects, hapus yang expired. Return list expired effect types."""
    expired = []
    remaining = []
    for eff in state.status_effects:
        eff["days_left"] = eff.get("days_left", 1) - 1
        if eff["days_left"] <= 0:
            expired.append(eff.get("type", "unknown"))
        else:
            remaining.append(eff)
    state.status_effects = remaining
    return expired


def _breakthrough(state: GameState, registry: DataRegistry) -> bool:
    """Terobosan ke ranah berikutnya. Return False jika sudah max."""
    realm_id = state.player.realm
    cur = registry.realms.get(realm_id)
    if not cur:
        return False
    order = int(cur["order"])
    nxt = None
    for rid, r in registry.realms.items():
        if int(r["order"]) == order + 1:
            nxt = rid
            break
    if not nxt:
        state.player.realm_level = int(cur.get("tiers", 1) or 1)
        add_log(state, "system", "[Sistem] Kau mencapai puncak ranah ini.")
        return False
    old = registry.realms[realm_id]["name_pinyin"]
    new = registry.realms[nxt]["name_pinyin"]
    state.player.realm = nxt
    state.player.realm_level = 1
    state.player.dantian_exp = 0
    add_log(state, "system", f"[Sistem] Terobosan! {old} → {new}.")
    return True


def _tier_name(level: int) -> str:
    """Nama tier berdasarkan level dalam ranah."""
    names = {1: "Awal", 2: "Tengah", 3: "Atas"}
    return names.get(level, f"Tier {level}")
