"""Ingatan naratif (Tianyuan Ling) — murni cerita, TANPA kekuatan mekanik.

Aturan kunci (GDD §2.1): membuka ingatan tidak memberi skill/power.
Ingatan hanya muncul di panel Tianyuan Ling + pesan Sistem.
"""

from __future__ import annotations

from ..loader import DataRegistry
from .events import add_log
from .state import GameState


def _memory_ids(state: GameState) -> set[str]:
    """Return set of memory IDs from state (handles both string and dict formats)."""
    return {
        m["id"] if isinstance(m, dict) else m
        for m in state.memories
    }


def unlock(state: GameState, registry: DataRegistry, memory_id: str | None,
           reliability: str | None = None) -> None:
    if not memory_id:
        return
    ids = memory_id if isinstance(memory_id, list) else [memory_id]
    existing = _memory_ids(state)
    for mid in ids:
        if mid in existing:
            continue
        mem = registry.memory(mid)
        if not mem:
            continue
        state.memories.append({
            "id": mid,
            "reliability": reliability or mem.get("reliability", "unknown"),
        })
        add_log(state, "system", f"[Sistem] Ingatan baru terbuka: '{mem.get('title', mid)}'.")


def update_reliability(state: GameState, memory_id: str, new_reliability: str) -> None:
    """Update reliability of an existing memory (for correction events)."""
    for m in state.memories:
        mid = m["id"] if isinstance(m, dict) else m
        if mid == memory_id:
            if isinstance(m, dict):
                m["reliability"] = new_reliability
            break
