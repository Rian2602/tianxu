"""Test objektif `choose` generik — F2.2b (ENGINE_ADAPTATION_PLAN).

Kontrak final (keputusan desain F2.2): `options[].set` menulis field state
pemain (closed-set `CHOOSE_SET_FIELDS`, bukan DSL). Field `academy` bersifat
inti — selain ditulis, starter kit & companion tetap digrant otomatis dari
config.academies. Opsi tanpa `set` = pilihan naratif (boleh). Validator
menolak field set tak dikenal / tipe salah saat load.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from src.engine.quest import CHOOSE_SET_FIELDS
from src.loader import DataRegistry
from src.engine.session import GameSession
from src.validate import DataContractError

FIX = Path(__file__).parent / "fixtures" / "minimal_data"


def _copy(tmp_path: Path) -> Path:
    dst = tmp_path / "choose_data"
    shutil.copytree(FIX, dst)
    return dst


def _load(dst: Path, rel: str):
    with open(dst / rel, encoding="utf-8") as f:
        return json.load(f)


def _dump(dst: Path, rel: str, data) -> None:
    with open(dst / rel, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# quest tambahan yang disuntikkan helper (bukan bagian baseline minimal)
EXTRA_QUESTS = {
    "q_identitas": {
        "id": "q_identitas", "kind": "main", "title": "Siapa dirimu?",
        "objective": {
            "kind": "choose", "hint": "Pilih identitasmu.",
            "options": [
                {"value": "bayu", "label": "Bayu", "set": {"name": "Bayu", "gold": 10}}
            ],
        },
        "on_complete": {"system_msg": "Identitas dipilih."},
    },
    "q_naratif": {
        "id": "q_naratif", "kind": "main", "title": "Keputusan",
        "objective": {
            "kind": "choose", "hint": "Apa keputusanmu?",
            "options": [
                {"value": "setuju", "label": "Setuju"},
                {"value": "tolak", "label": "Tolak"},
            ],
        },
        "on_complete": {"system_msg": "Keputusan dicatat."},
    },
}


def _session_for(tmp_path: Path, main_quest: str):
    """Registry + session baru dengan quest utama aktif yang ditentukan."""
    dst = _copy(tmp_path)
    qs = _load(dst, "quests/minimal.json")
    if main_quest in EXTRA_QUESTS:
        qs["quests"].append(EXTRA_QUESTS[main_quest])
        _dump(dst, "quests/minimal.json", qs)
    cfg = _load(dst, "config.json")
    cfg["starting"]["current_quest"] = main_quest
    _dump(dst, "config.json", cfg)
    reg = DataRegistry(data_dir=dst)
    return reg, GameSession.new(reg)


# ---------- perilaku: set field ----------

def test_choose_academy_grants_from_config(tmp_path):
    """Field inti academy: ditulis + starter kit & companion dari config akademi."""
    reg, session = _session_for(tmp_path, "q_min_pilih")
    session.apply_action({"type": "choose", "option": "akademi_bambu"})
    assert session.state.player.academy == "akademi_bambu"
    assert session.state.companion and session.state.companion["id"] == "companion_serigala"
    assert session.state.inventory.get("pil_qi", 0) >= 2 + 1  # 2 awal + 1 starter kit
    assert "q_min_pilih" in session.state.completed_quests


def test_choose_academy_without_grants_no_crash(tmp_path):
    """Akademi valid di config tapi tanpa companion/starter_kit → grant no-op aman."""
    reg, session = _session_for(tmp_path, "q_min_pilih")
    session.apply_action({"type": "choose", "option": "akademi_batu"})
    assert session.state.player.academy == "akademi_batu"
    assert session.state.companion is None
    assert session.state.inventory.get("pil_qi", 0) == 2  # tanpa starter kit tambahan
    assert "q_min_pilih" in session.state.completed_quests


def test_choose_sets_non_academy_fields(tmp_path):
    """`set` field non-akademi (name/gold) ditulis ke state pemain."""
    reg, session = _session_for(tmp_path, "q_identitas")
    session.apply_action({"type": "choose", "option": "bayu"})
    assert session.state.player.name == "Bayu"
    assert session.state.player.gold == 10  # MENULIS (assign), bukan menambah


def test_choose_option_without_set_is_narrative(tmp_path):
    """Opsi tanpa `set` = pilihan naratif — quest selesai tanpa perubahan state."""
    reg, session = _session_for(tmp_path, "q_naratif")
    name_before = session.state.player.name
    session.apply_action({"type": "choose", "option": "setuju"})
    assert "q_naratif" in session.state.completed_quests
    assert session.state.player.name == name_before


def test_choose_unknown_option_does_not_complete(tmp_path):
    """Option tak dikenal → log peringatan, quest TIDAK selesai, state tidak berubah."""
    reg, session = _session_for(tmp_path, "q_min_pilih")
    session.apply_action({"type": "choose", "option": "tidak_ada"})
    assert "q_min_pilih" not in session.state.completed_quests
    assert session.state.player.academy is None
    msgs = "\n".join(e["text"] for e in session.state.log)
    assert "tidak_ada" in msgs


# ---------- kontrak: CHOOSE_SET_FIELDS ----------

def test_choose_set_fields_closed_set():
    assert set(CHOOSE_SET_FIELDS) == {"academy", "name", "roots", "morality", "gold"}


def test_choose_unknown_set_field_rejected(tmp_path):
    """Typo field di `set` → ditolak saat load (bukan no-op diam-diam)."""
    dst = _copy(tmp_path)
    q = _load(dst, "quests/minimal.json")
    q["quests"][1]["objective"]["options"][0]["set"] = {"academyy": "x"}
    _dump(dst, "quests/minimal.json", q)
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    msg = str(ei.value)
    assert "academyy" in msg and "set" in msg


def test_choose_unknown_academy_rejected(tmp_path):
    """`set.academy` value yang tidak ada di config.academies → ditolak saat load
    (bukan grant no-op diam-diam — arah kontrak ketat)."""
    dst = _copy(tmp_path)
    q = _load(dst, "quests/minimal.json")
    q["quests"][1]["objective"]["options"][0]["set"] = {"academy": "akademi_ghost"}
    _dump(dst, "quests/minimal.json", q)
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    msg = str(ei.value)
    assert "akademi_ghost" in msg and "config.academies" in msg


def test_choose_wrong_type_rejected(tmp_path):
    """Tipe salah di `set` → ditolak saat load."""
    dst = _copy(tmp_path)
    q = _load(dst, "quests/minimal.json")
    q["quests"][1]["objective"]["options"][0]["set"] = {"gold": "banyak"}
    _dump(dst, "quests/minimal.json", q)
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    msg = str(ei.value)
    assert "gold" in msg and "angka" in msg


def test_choose_set_must_be_object(tmp_path):
    dst = _copy(tmp_path)
    q = _load(dst, "quests/minimal.json")
    q["quests"][1]["objective"]["options"][0]["set"] = "akademi_bambu"
    _dump(dst, "quests/minimal.json", q)
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    assert "objek" in str(ei.value)
