"""Fixtures bersama untuk test."""

from __future__ import annotations

import pytest

from src.engine.battle import BattleEngine
from src.engine.session import GameSession
from src.loader import DataRegistry


@pytest.fixture
def registry() -> DataRegistry:
    return DataRegistry()


@pytest.fixture
def session(registry: DataRegistry) -> GameSession:
    return GameSession.new(registry)


@pytest.fixture
def god_mode(monkeypatch):
    """Battle selalu menang 1 serangan (deterministik untuk test alur)."""
    monkeypatch.setattr(BattleEngine, "_calc_damage", lambda self, attack, defense, ea, ed: (99999, False))
    monkeypatch.setattr(BattleEngine, "_try_flee", lambda self, pc, b: True)


def finish_dialog(session: GameSession, choices: tuple = ()) -> None:
    """Jalankan dialog sampai selesai; ambil pilihan sesuai urutan `choices`."""
    ci = 0
    guard = 0
    while session.state.pending_dialog and guard < 200:
        guard += 1
        v = session.dialog.view()
        if v["choices"]:
            idx = choices[ci] if ci < len(choices) else 0
            ci += 1
            session.apply_action({"type": "dialog_choice", "choice_index": idx})
        else:
            session.apply_action({"type": "dialog_choice", "choice_index": -1})


def move_path(session: GameSession, locs: list[str]) -> None:
    """Pindah lewat jalur koneksi yang valid (satu langkah per aksi)."""
    for lid in locs:
        session.apply_action({"type": "move", "to": lid})


def play_to_incident(session: GameSession, academy: str = "akademi_elemen") -> None:
    """Main dari awal sampai insiden malam (dialog pilih sikap muncul)."""
    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    finish_dialog(session, [0])

    session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    finish_dialog(session, [0])

    session.apply_action({"type": "move", "to": "loc_arena"})
    session.apply_action({"type": "talk", "npc": "npc_hanxiu"})
    finish_dialog(session, [])
    session.apply_action({"type": "battle_action", "action": "attack"})  # menang spar

    session.apply_action({"type": "choose", "option": academy})

    # arena → aula ujian → paviliun
    move_path(session, ["loc_aula_ujian", "loc_paviliun"])
    session.apply_action({"type": "talk", "npc": "npc_suqing"})
    finish_dialog(session, [0])

    session.apply_action({"type": "move", "to": "loc_perpustakaan"})
    session.apply_action({"type": "advance_time", "hours": 12})  # malam
    session.apply_action({"type": "move", "to": "loc_ruang_lonceng"})
