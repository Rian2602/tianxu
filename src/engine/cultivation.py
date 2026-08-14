"""Progresi kultivasi — 10 tingkat per ranah, berbasis aktivitas.

Aturan (ENGINE_ARCHITECTURE §9.1):
- exp dari aktivitas dikali multiplier akar spiritual (`roots.exp_multiplier`)
- exp_needed(level) = round(base × growth^(level-1))
- level maks → breakthrough otomatis ke ranah berikutnya (order+1)
"""

from __future__ import annotations

from ..loader import DataRegistry
from .events import add_log
from .state import GameState


def gain_exp(state: GameState, registry: DataRegistry, amount: int) -> None:
    if amount <= 0:
        return
    amount = round(amount * state.exp_multiplier(registry))
    state.player.exp += amount
    while state.player.exp >= state.exp_next(registry):
        state.player.exp -= state.exp_next(registry)
        _level_up(state, registry)
    # jaga HP/Qi tidak melebihi maks baru setelah level-up
    state.player.hp = min(state.player.hp, state.max_hp(registry))
    state.player.qi = min(state.player.qi, state.max_qi(registry))


def gain_grind_exp(state: GameState, registry: DataRegistry, amount: int) -> None:
    """A2: exp dari sumber grinding (berburu/spar/side quest) dibatasi cap harian.
    `cultivation.daily_grind_exp_cap` (0 = tanpa batas). Main quest & grounding
    tidak terpengaruh (grounding sudah dibatasi jam per hari)."""
    if amount <= 0:
        return
    cap = int(registry.config.get("cultivation", {}).get("daily_grind_exp_cap", 0))
    if cap > 0:
        room = max(0, cap - state.exp_grind_today)
        amount = min(amount, room)
        if amount <= 0:
            return
    state.exp_grind_today += amount
    gain_exp(state, registry, amount)


def _level_up(state: GameState, registry: DataRegistry) -> None:
    c = registry.config.get("cultivation", {})
    levels = int(registry.realms[state.player.realm]["levels"])
    state.player.realm_level += 1
    if state.player.realm_level > levels:
        _breakthrough(state, registry)
    else:
        add_log(state, "system", f"[Sistem] Ranah naik: {state.player.realm_level}.")
    state.player.hp = state.max_hp(registry)
    state.player.qi = state.max_qi(registry)


def _breakthrough(state: GameState, registry: DataRegistry) -> None:
    realm_id = state.player.realm
    order = int(registry.realms[realm_id]["order"])
    nxt = None
    for rid, r in registry.realms.items():
        if int(r["order"]) == order + 1:
            nxt = rid
            break
    if not nxt:
        # ranah tertinggi — tetap di level maks
        state.player.realm_level = int(registry.realms[realm_id]["levels"])
        add_log(state, "system", "[Sistem] Kau mencapai puncak ranah ini.")
        return
    old = registry.realms[realm_id]["name_pinyin"]
    new = registry.realms[nxt]["name_pinyin"]
    state.player.realm = nxt
    state.player.realm_level = 1
    add_log(state, "system", f"[Sistem] Terobosan! {old} → {new}.")
