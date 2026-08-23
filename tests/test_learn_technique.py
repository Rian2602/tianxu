"""Sistem belajar teknik dari guru paviliun (playtest lanjutan).

Kurikulum paviliun GRATIS, hanya di paviliun sendiri, urutan kurikulum
wajib berurutan. Pola real-data (data/) seperti test_arc2_data.
"""

from __future__ import annotations

import pytest

from src.loader import DataRegistry, DATA_DIR
from src.engine.session import GameSession

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "quests" / "arc01.json").exists(),
    reason="data story belum ada di data/",
)


def _wuxin_student() -> GameSession:
    """Sesi baru dengan murid Wuxin yang sedang berada di pavilionnya."""
    s = GameSession.new(DataRegistry())
    while s.state.pending_dialog:
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
    s.state.player.academy = "pavilion_wuxin"
    s.state.location = "loc_pavilion_wuxin"
    return s


def _learn(s: GameSession, tid: str) -> dict:
    return s.apply_action({"type": "learn_technique", "technique": tid})


def test_learn_first_curriculum_technique_free(registry=None):
    s = _wuxin_student()
    before_gold = s.state.player.gold
    v = _learn(s, "teknik_dasar")
    assert "teknik_dasar" in s.state.player.techniques
    assert s.state.player.gold == before_gold  # gratis
    assert not any("ditolak" in str(e) for e in [v.get("error")] if e)


def test_learn_rejects_duplicate():
    s = _wuxin_student()
    _learn(s, "teknik_dasar")
    v = _learn(s, "teknik_dasar")
    assert v.get("error")


def test_learn_requires_previous_curriculum():
    s = _wuxin_student()
    v = _learn(s, "teknik_wuxin")  # teknik_dasar belum dikuasai
    assert v.get("error")
    assert "teknik_wuxin" not in s.state.player.techniques


def test_learn_sequence_then_signature():
    s = _wuxin_student()
    _learn(s, "teknik_dasar")
    v = _learn(s, "teknik_wuxin")
    assert not v.get("error"), v.get("error")
    assert {"teknik_dasar", "teknik_wuxin"} <= set(s.state.player.techniques)


def test_learn_rejects_wrong_location():
    s = _wuxin_student()
    s.state.location = "loc_training_hall"
    v = _learn(s, "teknik_dasar")
    assert v.get("error")
    assert "teknik_dasar" not in s.state.player.techniques


def test_learn_rejects_other_pavilion_curriculum():
    s = _wuxin_student()
    v = _learn(s, "teknik_jianxin")  # kurikulum Jianxin, bukan milik Wuxin
    assert v.get("error")
    assert "teknik_jianxin" not in s.state.player.techniques


def test_learn_without_academy_rejected():
    s = GameSession.new(DataRegistry())
    while s.state.pending_dialog:
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
    s.state.location = "loc_training_hall"
    v = _learn(s, "teknik_dasar")
    assert v.get("error")
