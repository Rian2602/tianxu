"""Ingatan naratif (Tianyuan Ling) — murni cerita, TANPA kekuatan mekanik.

Aturan kunci (GDD §2.1): membuka ingatan tidak memberi skill/power.
Ingatan hanya muncul di panel Tianyuan Ling + pesan Sistem.
"""

from __future__ import annotations

from ..loader import DataRegistry
from .events import add_log
from .state import GameState


def unlock(state: GameState, registry: DataRegistry, memory_id: str | None) -> None:
    if not memory_id:
        return
    ids = memory_id if isinstance(memory_id, list) else [memory_id]
    for mid in ids:
        if mid in state.memories:
            continue
        mem = registry.memory(mid)
        if not mem:
            continue
        state.memories.append(mid)
        add_log(state, "system", f"[Sistem] Ingatan baru terbuka: '{mem['title']}'.")
