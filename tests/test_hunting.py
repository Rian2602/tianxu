"""Test multi-zona berburu — F2.3 (ENGINE_ADAPTATION_PLAN).

`world.hunts[]` menggantikan `world.hunt` dict tunggal: tiap zona punya
location/pool/search_item sendiri, timer respawn PER ZONA (`last_hunt_time`
menjadi dict → SCHEMA_VERSION 2 + migrator v1→v2). Legacy `world.hunt` tetap
dibungkus loader jadi zona id "legacy" agar config/save lama tetap berfungsi.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from src.loader import DataRegistry
from src.engine.session import GameSession
from src.engine.state import GameState, SCHEMA_VERSION
from src.validate import DataContractError

FIX = Path(__file__).parent / "fixtures" / "minimal_data"


def _copy(tmp_path: Path) -> Path:
    dst = tmp_path / "hunt_data"
    shutil.copytree(FIX, dst)
    return dst


def _two_zone_data(tmp_path: Path) -> Path:
    """Copy dataset dengan 2 zona berburu di lokasi yang sama (pool & item beda)."""
    dst = _copy(tmp_path)
    enemies = (dst / "enemies.csv").read_text(encoding="utf-8").splitlines()
    enemies.append("musuh_hutan_b,Hantu Batu,20,5,2,7,6")
    (dst / "enemies.csv").write_text("\n".join(enemies) + "\n", encoding="utf-8")

    cfg = json.loads((dst / "config.json").read_text(encoding="utf-8"))
    cfg["world"]["hunts"].append({
        "id": "hunt_hutan_b", "location": "loc_hutan",
        "pool": ["musuh_hutan_b"], "search_item": "pedang_kayu",
    })
    (dst / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return dst


def _session(dst: Path):
    reg = DataRegistry(data_dir=dst)
    return reg, GameSession.new(reg)


# ---------- zona per lokasi ----------

def test_hunts_here_per_location(registry, session):
    assert registry.hunts_for_location("loc_gerbang") == []
    assert [h["id"] for h in registry.hunts_for_location("loc_hutan")] == ["hunt_hutan"]
    assert session.hunts_here() == []  # di gerbang


def test_can_hunt_only_at_hunt_location(registry, session):
    assert session.can_hunt() is False
    session.apply_action({"type": "move", "to": "loc_hutan"})
    assert session.can_hunt() is True


# ---------- pool & search item per zona ----------

def test_hunt_uses_zone_pool(tmp_path):
    reg, session = _session(_two_zone_data(tmp_path))
    session.apply_action({"type": "move", "to": "loc_hutan"})
    # zona A eksplisit → musuh dari pool zona A
    session.apply_action({"type": "hunt", "hunt": "hunt_hutan"})
    assert session.state.pending_battle["foes"][0]["id"] == "musuh_hutan"
    session.state.pending_battle = None
    # zona B eksplisit → musuh dari pool zona B
    session.apply_action({"type": "hunt", "hunt": "hunt_hutan_b"})
    assert session.state.pending_battle["foes"][0]["id"] == "musuh_hutan_b"


def test_hunt_defaults_to_first_zone(tmp_path):
    reg, session = _session(_two_zone_data(tmp_path))
    session.apply_action({"type": "move", "to": "loc_hutan"})
    session.apply_action({"type": "hunt"})  # tanpa id → zona pertama
    assert session.state.pending_battle["foes"][0]["id"] == "musuh_hutan"


def test_hunt_unknown_zone_id_logs_and_falls_back(tmp_path):
    """Id zona tak dikenal → log peringatan (bukan diam-diam) + fallback zona pertama."""
    reg, session = _session(_two_zone_data(tmp_path))
    session.apply_action({"type": "move", "to": "loc_hutan"})
    session.apply_action({"type": "hunt", "hunt": "hunt_tidak_ada"})
    assert session.state.pending_battle is not None
    assert session.state.pending_battle["foes"][0]["id"] == "musuh_hutan"  # zona pertama
    msgs = "\n".join(e["text"] for e in session.state.log)
    assert "hunt_tidak_ada" in msgs and "tidak ditemukan" in msgs


def test_search_uses_zone_search_item(tmp_path):
    """Search memakai search_item zona pertama (pil_qi) — sukses (60%) atau
    gagal keduanya valid; yang dilarang: menambah item dari zona lain."""
    reg, session = _session(_two_zone_data(tmp_path))
    session.apply_action({"type": "move", "to": "loc_hutan"})
    session.apply_action({"type": "search"})  # zona pertama → search_item pil_qi
    # item zona B (pedang_kayu) tidak boleh bertambah dari search zona pertama
    assert session.state.inventory.get("pedang_kayu", 0) == 1  # 1 dari starter


def test_search_item_per_second_zone(tmp_path):
    reg, session = _session(_two_zone_data(tmp_path))
    session.apply_action({"type": "move", "to": "loc_hutan"})
    before = session.state.inventory.get("pedang_kayu", 0)
    # search memakai zona pertama (hunt_hutan → pil_qi); verifikasi zona B
    # punya search_item sendiri via data (bukan logika global)
    hunt_b = next(h for h in reg.hunts if h["id"] == "hunt_hutan_b")
    assert hunt_b["search_item"] == "pedang_kayu"


# ---------- timer respawn per zona ----------

def test_hunt_timer_per_zone_independent(tmp_path):
    reg, session = _session(_two_zone_data(tmp_path))
    session.apply_action({"type": "move", "to": "loc_hutan"})
    session.apply_action({"type": "hunt", "hunt": "hunt_hutan"})
    assert session.state.pending_battle is not None
    assert session.state.last_hunt_time.get("hunt_hutan") is not None
    session.state.pending_battle = None
    # majukan waktu melewati respawn zona A (respawn_hours = 1)
    session._pass_time(2)
    session.apply_action({"type": "hunt", "hunt": "hunt_hutan_b"})
    # zona B belum pernah diburu → harus langsung bisa, tidak terblokir zona A
    assert session.state.pending_battle is not None
    assert session.state.last_hunt_time.get("hunt_hutan_b") is not None


def test_hunt_cooldown_blocks_same_zone(tmp_path):
    dst = _copy(tmp_path)
    cfg = json.loads((dst / "config.json").read_text(encoding="utf-8"))
    cfg["world"]["monster_respawn_hours"] = 5
    (dst / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    reg, session = _session(dst)
    session.apply_action({"type": "move", "to": "loc_hutan"})
    session.apply_action({"type": "hunt", "hunt": "hunt_hutan"})
    session.state.pending_battle = None
    session.apply_action({"type": "hunt", "hunt": "hunt_hutan"})
    assert session.state.pending_battle is None  # masih cooldown (2h time cost < 5h respawn)
    msgs = "\n".join(e["text"] for e in session.state.log)
    assert "sepi" in msgs


# ---------- legacy world.hunt (config v1) ----------

def test_legacy_world_hunt_wrapped_as_legacy_zone(tmp_path):
    dst = _copy(tmp_path)
    cfg = json.loads((dst / "config.json").read_text(encoding="utf-8"))
    cfg["world"] = {"hunt": {"location": "loc_hutan", "pool": ["musuh_hutan"]},
                    "monster_respawn_hours": 1}
    (dst / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    reg = DataRegistry(data_dir=dst)
    assert [h["id"] for h in reg.hunts] == ["legacy"]
    assert reg.hunts[0]["location"] == "loc_hutan"


# ---------- save: v1 → v2 migrasi ----------

def test_schema_version_bumped():
    assert SCHEMA_VERSION == 9


def test_save_v1_last_hunt_time_int_migrates():
    d = {
        "schema_version": 1,
        "player": {"name": "X", "hp": 10, "qi": 5, "realm": "realm_chuji", "realm_level": 1},
        "location": "loc_gerbang", "day": 1, "hour": 8,
        "last_hunt_time": 120,  # v1: int global
    }
    gs = GameState.from_dict(d)
    assert gs.last_hunt_time == {"legacy": 120}


def test_save_future_schema_rejected(registry, tmp_path, monkeypatch):
    """B5 (M-1): save versi lebih baru → SaveError (gate regresi kompatibilitas)."""
    import src.engine.session as sess_mod
    monkeypatch.setattr(sess_mod, "SAVES_DIR", tmp_path)
    session = GameSession.new(registry)
    session.apply_action({"type": "save", "save_name": "v99"})
    data = json.loads((tmp_path / "v99.json").read_text(encoding="utf-8"))
    data["schema_version"] = 99
    (tmp_path / "v99.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(sess_mod.SaveError):
        GameSession.load(registry, "v99")


def test_save_v0_legacy_tolerated(registry, tmp_path, monkeypatch):
    """B5 (M-1): save tanpa schema_version (v0) → dimuat, tidak crash."""
    import src.engine.session as sess_mod
    monkeypatch.setattr(sess_mod, "SAVES_DIR", tmp_path)
    session = GameSession.new(registry)
    session.apply_action({"type": "save", "save_name": "v0"})
    data = json.loads((tmp_path / "v0.json").read_text(encoding="utf-8"))
    data.pop("schema_version", None)
    (tmp_path / "v0.json").write_text(json.dumps(data), encoding="utf-8")
    loaded = GameSession.load(registry, "v0")
    assert loaded.state.location == session.state.location
    assert loaded.state.player.gold == session.state.player.gold
    # B6 (audit opencode): round-trip tidak cukup 4 field — inventori, quest
    # aktif, flags, equipment ikut diverifikasi agar regresi serialisasi tertangkap.
    assert loaded.state.inventory == session.state.inventory
    assert loaded.state.current_quest == session.state.current_quest
    assert loaded.state.flags == session.state.flags
    assert loaded.state.player.equipment == session.state.player.equipment


def test_save_v2_roundtrip_dict(registry, session):
    session.apply_action({"type": "move", "to": "loc_hutan"})
    session.apply_action({"type": "hunt"})
    session.state.pending_battle = None
    d = session.state.to_dict()
    assert isinstance(d["last_hunt_time"], dict)
    gs2 = GameState.from_dict(d)
    assert gs2.last_hunt_time == session.state.last_hunt_time


def test_save_without_last_hunt_time_defaults_empty():
    d = {
        "schema_version": 2,
        "player": {"name": "X", "hp": 10, "qi": 5, "realm": "realm_chuji", "realm_level": 1},
        "location": "loc_gerbang", "day": 1, "hour": 8,
    }
    gs = GameState.from_dict(d)
    assert gs.last_hunt_time == {}


# ---------- validator: zona rusak ditolak ----------

def test_validate_unknown_hunt_pool_rejected(tmp_path):
    dst = _copy(tmp_path)
    cfg = json.loads((dst / "config.json").read_text(encoding="utf-8"))
    cfg["world"]["hunts"][0]["pool"] = ["musuh_hantu_palsu"]
    (dst / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    msg = str(ei.value)
    assert "musuh_hantu_palsu" in msg and "hunts[0].pool" in msg


def test_validate_unknown_hunt_location_rejected(tmp_path):
    dst = _copy(tmp_path)
    cfg = json.loads((dst / "config.json").read_text(encoding="utf-8"))
    cfg["world"]["hunts"][0]["location"] = "loc_tidak_ada"
    (dst / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    assert "loc_tidak_ada" in str(ei.value)


def test_validate_duplicate_hunt_id_rejected(tmp_path):
    dst = _copy(tmp_path)
    cfg = json.loads((dst / "config.json").read_text(encoding="utf-8"))
    cfg["world"]["hunts"].append(dict(cfg["world"]["hunts"][0]))
    (dst / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    assert "duplikat" in str(ei.value)
