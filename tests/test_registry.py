"""Test registry/dispatch table — F2.1 (ENGINE_ADAPTATION_PLAN).

Membuktikan:
1. Satu sumber kebenaran — himpunan jenis yang dipakai validator = kunci dict
   dispatch di modul engine (menambah handler otomatis dikenali validator).
2. Jenis dikenal jalan (efek, kondisi, objektif) — dispatch benar-benar dieksekusi.
3. Jenis tak dikenal AMAN saat runtime (pertahanan berlapis setelah validator):
   - efek   → log sistem, tidak crash;
   - teknik → Qi TIDAK hangus (fix temuan audit v3 §1.4);
   - status → dilaporkan + diabaikan, tidak menempel-inert;
   - objektif/efek tanpa field wajib → ditolak validator saat load.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from src.engine.battle import (
    STATUS_KINDS,
    TECHNIQUE_KINDS,
    player_combat,
)
from src.engine.dialog import CONDITION_CHECKERS, CONDITION_KEYS
from src.engine.effects import EFFECT_TYPES, apply as apply_effects
from src.engine.quest import OBJECTIVE_HANDLERS
from src.loader import DataRegistry
from src.validate import DataContractError

FIX = Path(__file__).parent / "fixtures" / "minimal_data"


# ---------- 1. satu sumber kebenaran ----------

def test_validator_kind_sets_match_registry_keys():
    """Set yang divalidasi = kunci dispatch — mustahil validator basi terhadap executor.
    (subsumes cek "tabel terisi": perbandingan himpunan eksplisit di bawah ini
    sudah memastikan set tidak kosong dan tidak berubah dari kontrak)."""
    assert EFFECT_TYPES == {"morality", "relation", "reputation", "flag",
                            "item", "gold", "technique", "start_quest", "npc_state",
                            "grant_companion", "exp", "unlock_realm_bonus",
                            "status_effect", "dialog"}
    assert set(OBJECTIVE_HANDLERS) == {"talk", "defeat", "gather", "reach", "choose",
                                       "spar", "advance_time", "rest"}
    assert TECHNIQUE_KINDS == {"attack", "defend", "heal"}
    assert STATUS_KINDS == {"dot", "stun", "debuff", "hot", "buff"}
    assert CONDITION_KEYS == set(CONDITION_CHECKERS)
    # validator memakai set yang sama (bukan salinan) — cek via import langsung
    from src.validate import (
        CONDITION_KEYS as V_COND,
        EFFECT_TYPES as V_EFFECT,
        OBJECTIVE_KINDS as V_OBJ,
        STATUS_KINDS as V_STATUS,
        TECHNIQUE_KINDS as V_TECH,
    )
    assert V_OBJ == set(OBJECTIVE_HANDLERS)
    # validator sengaja menambah start_quest (dialog-only) ke set eksekusi
    assert V_EFFECT == EFFECT_TYPES
    assert V_COND == CONDITION_KEYS
    assert V_TECH == TECHNIQUE_KINDS
    assert V_STATUS == STATUS_KINDS


# ---------- 2. jenis dikenal jalan ----------

def test_known_effects_apply(session, registry):
    apply_effects(session.state, registry, [
        {"type": "flag", "key": "petunjuk", "value": True},
        {"type": "gold", "value": 100},
        {"type": "item", "id": "pil_qi", "count": 2},
    ])
    assert session.state.flags.get("petunjuk") is True
    assert session.state.player.gold == 50 + 100  # 50 dari config starting + 100 efek
    assert session.state.inventory.get("pil_qi", 0) == 2 + 2  # 2 dari config starting + 2 efek


def test_known_condition_checkers_used(session, registry):
    session.state.flags["sudah_kenal"] = True
    cond = {"flag": {"key": "sudah_kenal", "value": True}}
    from src.engine.dialog import DialogEngine
    assert DialogEngine._eval_condition(session.state, cond, registry) is True


def test_known_objective_dispatch_used(session, registry):
    """Quest talk selesai via OBJECTIVE_HANDLERS — jalur dispatch nyata, bukan if/elif."""
    assert set(OBJECTIVE_HANDLERS["talk"].__dataclass_fields__) >= {"text", "on_dialog_end"}
    nid = registry.npcs[0]["id"]
    session.apply_action({"type": "talk", "npc": nid})
    session.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert "q_min_intro" in session.state.completed_quests


# ---------- 3. jenis tak dikenal — aman saat runtime ----------

def test_known_technique_attack_executes(session, registry):
    """Dispatch teknik dikenal benar-benar dieksekusi: attack → foe HP turun, Qi turun."""
    session.state.player.techniques.append("tebasan")
    session.apply_action({"type": "move", "to": registry.hunts[0]["location"]})
    session.apply_action({"type": "hunt"})
    b = session.state.pending_battle
    pc = player_combat(session.state, registry)
    foe_hp_before = b["foes"][0]["hp"]
    qi_before = pc["qi"]

    session.battle._technique(pc, b, "tebasan")

    assert b["foes"][0]["hp"] < foe_hp_before, "attack harus mengurangi HP musuh"
    assert pc["qi"] == qi_before - 3, "attack harus memakai Qi (qi_cost 3)"
    msgs = "\n".join(e["text"] for e in session.state.log)
    assert "Tebasan" in msgs


def test_known_status_dot_executes(session, registry):
    """Dispatch status dikenal dieksekusi: dot → HP turun sesuai power, bukan stun."""
    session.apply_action({"type": "move", "to": registry.hunts[0]["location"]})
    session.apply_action({"type": "hunt"})
    b = session.state.pending_battle
    b["player_statuses"] = {"racun": 2}  # status dot dari fixture config
    pc = player_combat(session.state, registry)
    hp_before = pc["hp"]

    stunned = session.battle._apply_player_statuses(pc, b)

    assert stunned is False
    assert pc["hp"] == hp_before - 2, "racun (power 2) harus mengurangi HP 2"
    msgs = "\n".join(e["text"] for e in session.state.log)
    assert "Racun" in msgs


def test_unknown_effect_logs_without_crash(session, registry):
    before = len(session.state.log)
    apply_effects(session.state, registry, [{"type": "ledakan_nuklir"}])
    assert len(session.state.log) == before + 1
    assert "ledakan_nuklir" in session.state.log[-1]["text"]
    assert "tak dikenal" in session.state.log[-1]["text"]


def test_technique_unknown_kind_does_not_waste_qi(session, registry):
    """Fix temuan audit v3 §1.4: kind tak dikenal TIDAK boleh menghanguskan Qi."""
    registry.techniques["tek_buff"] = {
        "id": "tek_buff", "name": "Tebasan Bayangan", "kind": "buff",
        "qi_cost": 5, "power": 10, "realm_required": "Ranah Awal",
    }
    session.state.player.techniques.append("tek_buff")
    session.apply_action({"type": "move", "to": registry.hunts[0]["location"]})
    session.apply_action({"type": "hunt"})
    b = session.state.pending_battle
    pc = player_combat(session.state, registry)
    qi_before = pc["qi"]
    hp_before = b["foes"][0]["hp"]

    session.battle._technique(pc, b, "tek_buff")

    assert pc["qi"] == qi_before, "Qi tidak boleh hangus untuk kind tak dikenal"
    assert b["foes"][0]["hp"] == hp_before, "tidak boleh ada efek tanpa handler"
    msgs = "\n".join(e["text"] for e in session.state.log)
    assert "buff" in msgs and "tak dikenal" in msgs


def test_unknown_status_kind_reported_not_inert(session, registry):
    """Fix temuan audit v3 §1.5: status kind tak dikenal dilaporkan, tidak menempel-inert."""
    registry.config.setdefault("battle", {})["statuses"]["st_mystery"] = {
        "name": "Aura Misterius", "kind": "mystery", "duration": 3,
    }
    session.apply_action({"type": "move", "to": registry.hunts[0]["location"]})
    session.apply_action({"type": "hunt"})
    b = session.state.pending_battle
    b["player_statuses"] = {"st_mystery": 2}
    pc = player_combat(session.state, registry)
    hp_before = pc["hp"]

    stunned = session.battle._apply_player_statuses(pc, b)

    assert stunned is False, "status tak dikenal tidak boleh stun"
    assert pc["hp"] == hp_before, "status tak dikenal tidak boleh menimbulkan efek"
    msgs = "\n".join(e["text"] for e in session.state.log)
    assert "Aura Misterius" in msgs and "mystery" in msgs and "tak dikenal" in msgs


# ---------- 4. field wajib efek — ditolak validator ----------

def _copy(tmp_path: Path) -> Path:
    dst = tmp_path / "registry_broken"
    shutil.copytree(FIX, dst)
    return dst


def test_effect_missing_required_field_rejected(tmp_path):
    """`{"type": "flag"}` tanpa `key` → ditolak saat load (temuan #3 evaluasi F1)."""
    dst = _copy(tmp_path)
    dlg = json.loads((dst / "dialogs" / "minimal.json").read_text(encoding="utf-8"))
    dlg["dialogs"][1]["nodes"]["n1"]["choices"][1]["effects"] = [{"type": "flag"}]
    (dst / "dialogs" / "minimal.json").write_text(
        json.dumps(dlg, ensure_ascii=False, indent=2), encoding="utf-8")

    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    msg = str(ei.value)
    assert "flag" in msg and "key" in msg


def test_effect_missing_required_field_all_kinds(tmp_path):
    """Field wajib per jenis efek dieksekusi (bukan cuma flag).
    morality/gold sengaja tanpa field wajib — `value` punya default 0 (no-op
    aman, konsisten arah hardening); sisanya wajib."""
    dst = _copy(tmp_path)
    dlg = json.loads((dst / "dialogs" / "minimal.json").read_text(encoding="utf-8"))
    dlg["dialogs"][1]["nodes"]["n1"]["choices"][1]["effects"] = [
        {"type": "morality"},          # tanpa field wajib (default 0)
        {"type": "gold"},              # tanpa field wajib (default 0)
        {"type": "relation"},          # butuh npc + value
        {"type": "item"},              # butuh id
        {"type": "technique"},         # butuh id
        {"type": "npc_state"},         # butuh npc
    ]
    (dst / "dialogs" / "minimal.json").write_text(
        json.dumps(dlg, ensure_ascii=False, indent=2), encoding="utf-8")

    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    msg = str(ei.value)
    for kind in ("relation", "item", "technique", "npc_state"):
        assert kind in msg, f"pelanggaran {kind} harus dilaporkan"
    # morality/gold TANPA field wajib — efek tanpa value valid (default 0)
    assert "morality" not in msg and "gold" not in msg


def test_dialog_effect_missing_id_rejected(tmp_path):
    """dialog tanpa id → ditolak validator (silent no-op tanpa id)."""
    dst = _copy(tmp_path)
    dlg = json.loads((dst / "dialogs" / "minimal.json").read_text(encoding="utf-8"))
    dlg["dialogs"][1]["nodes"]["n1"]["choices"][1]["effects"] = [{"type": "dialog"}]
    (dst / "dialogs" / "minimal.json").write_text(
        json.dumps(dlg, ensure_ascii=False, indent=2), encoding="utf-8")

    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    msg = str(ei.value)
    assert "dialog" in msg and "id" in msg
