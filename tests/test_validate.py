"""Test validator kontrak data — F1.1 (ENGINE_ADAPTATION_PLAN).

Strategi (rekomendasi evaluasi F0 §5): SETIAP pelanggaran dibuat dengan
MEMODIFIKASI copy dataset minimal (`tests/fixtures/minimal_data`) — satu sumber
kebenaran, bukan dataset rusak terpisah. Setiap test memeriksa ISI pesan error
(file + field + nilai + nilai valid), bukan sekadar `raises`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.loader import DataRegistry
from src.validate import DataContractError


def _load(dst: Path, rel: str):
    with open(dst / rel, encoding="utf-8") as f:
        return json.load(f)


def _dump(dst: Path, rel: str, data) -> None:
    with open(dst / rel, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _csv(dst: Path, rel: str) -> list[str]:
    return (dst / rel).read_text(encoding="utf-8").splitlines()


def _write_csv(dst: Path, rel: str, lines: list[str]) -> None:
    (dst / rel).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _expect_error(dst: Path, *needles: str) -> DataContractError:
    """DataRegistry pada data rusak harus menolak; kembalikan error untuk assert."""
    with pytest.raises(DataContractError) as ei:
        DataRegistry(data_dir=dst)
    msg = str(ei.value)
    for n in needles:
        assert n in msg, f"pesan error tidak memuat {n!r}:\n{msg}"
    return ei.value


# ---------- baseline: dataset minimal valid ----------

def test_minimal_dataset_valid(data_dir):
    """Aturan: minimal valid → pass (regression gate — dipakai semua suite F0)."""
    r = DataRegistry(data_dir=data_dir)
    assert len(r.quests) == 3  # intro → choose (chain) + side
    assert len(r.dialogs) == 2


# ---------- aturan #1: skema per file ----------

def test_quest_without_id(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][0].pop("id")
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "[quests/minimal.json]", "quest tanpa field 'id'")


def test_quest_bad_kind(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][0]["kind"] = "epic"
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "kind quest tak dikenal", "epic", "main", "side")


def test_dialog_node_without_text(data_dir):
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    data["dialogs"][0]["nodes"]["n1"].pop("text")
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "text", "random_text")


def test_dialog_start_bad_node(data_dir):
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    data["dialogs"][0]["start"] = "n99"
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "node start tak dikenal", "n99")


# ---------- aturan #2: duplikat id ----------

def test_duplicate_quest_id(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    dup = dict(data["quests"][0], id="q_min_intro", title="Duplikat")
    data["quests"].append(dup)
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "duplikat id quest", "q_min_intro", "2×")


def test_duplicate_item_id(data_dir):
    dst = data_dir
    lines = _csv(dst, "items.csv")
    lines.append("pil_qi,Pil Qi,consumable,20,10,")
    _write_csv(dst, "items.csv", lines)
    _expect_error(dst, "duplikat id item", "pil_qi")


# ---------- aturan #4: jenis tak dikenal ----------

def test_unknown_objective_kind(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][0]["objective"]["kind"] = "escort"
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "[quests/minimal.json]", "jenis objektif tak dikenal",
                  "escort", "talk", "defeat", "gather")


def test_unknown_effect_type_in_quest(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][1]["on_complete"]["effects"] = [{"type": "bless"}]
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "[quests/minimal.json]", "jenis efek tak dikenal", "bless", "flag", "gold")


def test_unknown_condition_key(data_dir):
    """Typo moralty_min (bukan morality_min) — footgun terbesar (F1.3)."""
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    data["dialogs"][1]["nodes"]["n1"]["choices"][1]["condition"] = {"moralty_min": 50}
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "kunci kondisi tak dikenal", "moralty_min", "morality_min")


def test_unknown_technique_kind(data_dir):
    dst = data_dir
    lines = _csv(dst, "techniques.csv")
    lines[1] = lines[1].replace(",attack,", ",buff,")
    _write_csv(dst, "techniques.csv", lines)
    _expect_error(dst, "jenis teknik tak dikenal", "buff", "attack", "defend", "heal")


def test_unknown_status_kind(data_dir):
    dst = data_dir
    cfg = _load(dst, "config.json")
    cfg["battle"]["statuses"]["racun"]["kind"] = "charm"
    _dump(dst, "config.json", cfg)
    _expect_error(dst, "jenis status tak dikenal", "charm", "dot", "stun")


def test_unknown_item_type(data_dir):
    dst = data_dir
    lines = _csv(dst, "items.csv")
    lines[1] = lines[1].replace(",consumable,", ",scroll,")
    _write_csv(dst, "items.csv", lines)
    _expect_error(dst, "jenis item tak dikenal", "scroll", "consumable", "weapon")


def test_key_item_type_accepted(data_dir):
    """B2 (Arc 1): tipe `key_item` valid — item naratif tersimpan, tidak dipakai."""
    dst = data_dir
    lines = _csv(dst, "items.csv")
    lines.append("kunci_kuno,Simbol Kuno,key_item,,,")
    _write_csv(dst, "items.csv", lines)
    r = DataRegistry(data_dir=dst)  # tidak boleh error
    assert r.item("kunci_kuno")["type"] == "key_item"


# ---------- aturan #3: referensi silang ----------

def test_broken_npc_reference(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][0]["objective"]["npc"] = "npc_tidak_ada"
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "NPC tak dikenal", "npc_tidak_ada")


def test_broken_quest_next_reference(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][0]["next"] = [{"quest": "q_tidak_ada"}]
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "quest tak dikenal", "q_tidak_ada")


def test_broken_recipe_reference(data_dir):
    dst = data_dir
    data = _load(dst, "recipes.json")
    data["recipes"] = [{"id": "r_broken", "result": "item_ghost", "ingredients": []}]
    _dump(dst, "recipes.json", data)
    _expect_error(dst, "recipe 'r_broken'.result", "item_ghost")


def test_broken_dialog_next(data_dir):
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    data["dialogs"][1]["nodes"]["n1"]["choices"][0]["next"] = "n99"
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "node tak dikenal", "n99")


def test_broken_location_connection(data_dir):
    dst = data_dir
    data = _load(dst, "locations.json")
    data["locations"][0]["connections"] = ["loc_ghost"]
    _dump(dst, "locations.json", data)
    _expect_error(dst, "lokasi tak dikenal", "loc_ghost")


def test_broken_shop_item(data_dir):
    dst = data_dir
    data = _load(dst, "npcs.json")
    data["npcs"][0]["shop"] = {"buy": [{"item": "item_ghost", "price": 10}]}
    _dump(dst, "npcs.json", data)
    _expect_error(dst, "shop.buy", "item_ghost")


def test_npc_spar_without_combat(data_dir):
    dst = data_dir
    data = _load(dst, "npcs.json")
    data["npcs"][0].pop("combat")
    _dump(dst, "npcs.json", data)
    _expect_error(dst, "can_spar=true", "combat")


def test_spar_debuff_rejects_unknown_key(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][0]["objective"]["kind"] = "spar"
    data["quests"][0]["objective"]["spar_debuff"] = {"hp_mult": 0.6, "crit_mult": 2}
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "spar_debuff", "crit_mult")


def test_spar_allies_require_known_combat_npcs(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][0]["objective"]["kind"] = "spar"
    data["quests"][0]["objective"]["allies"] = ["npc_ghost"]
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "allies", "npc_ghost")


def test_no_safe_location(data_dir):
    dst = data_dir
    data = _load(dst, "locations.json")
    for l in data["locations"]:
        l["is_safe"] = False
    _dump(dst, "locations.json", data)
    _expect_error(dst, "is_safe=true")


# ---------- aturan #5: jebakan start_quest ----------

def test_start_quest_in_on_complete_rejected(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][1]["on_complete"]["effects"] = [
        {"type": "start_quest", "quest": "q_min_side"}
    ]
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "start_quest", "tidak sah", "choices[].effects")


def test_start_quest_in_dialog_accepted(data_dir):
    """Baseline: start_quest di choices[].effects dialog = satu-satunya tempat sah."""
    # dataset minimal sudah berisi contoh ini (dlg_side_offer) — harus lolos
    DataRegistry(data_dir=data_dir)


def test_start_quest_bad_quest_ref(data_dir):
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    data["dialogs"][1]["nodes"]["n1"]["choices"][0]["effects"] = [
        {"type": "start_quest", "quest": "q_ghost"}
    ]
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "quest tak dikenal", "q_ghost")


# ---------- aturan #6: branch quest ----------

def test_branch_without_choice_id(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][0]["next"] = [
        {"quest": "q_a", "option": "a"},
        {"quest": "q_b", "option": "b"},
    ]
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "choice_id", "quest bercabang")


def test_branch_duplicate_option(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][0]["next"] = [
        {"quest": "q_min_side", "option": "sama", "choice_id": "dlg_pilih"},
        {"quest": "q_min_side", "option": "sama", "choice_id": "dlg_pilih"},
    ]
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "option", "sama")


# ---------- aturan #7: timeout tanpa fail_next ----------

def test_main_timeout_without_fail_next(data_dir):
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][0]["timeout"] = {"hours": 24}
    _dump(dst, "quests/minimal.json", data)
    _expect_error(dst, "fail_next", "timeout")


def test_side_timeout_without_fail_next_ok(data_dir):
    """Side quest timeout TIDAK butuh fail_next (kode hanya menghapus dari aktif)."""
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    side = next(q for q in data["quests"] if q["kind"] == "side")
    side["timeout"] = {"hours": 24}
    _dump(dst, "quests/minimal.json", data)
    DataRegistry(data_dir=dst)  # tidak boleh error


# ---------- _inactive/ di luar cakupan ----------

def test_inactive_folder_not_validated(data_dir):
    """Folder `_inactive/` tidak ikut load/validate — draft arc boleh rusak di sana."""
    dst = data_dir
    inactive = dst / "quests" / "_inactive"
    inactive.mkdir(exist_ok=True)  # fixture sudah menyertakan folder + draft
    (inactive / "draft_broken.json").write_text(
        json.dumps({"quests": [{"id": "q_draft", "kind": "epic", "objective": {"kind": "nope"}}]}),
        encoding="utf-8")
    DataRegistry(data_dir=dst)  # tidak boleh error


# ---------- B1 (audit opencode): kondisi value-cacat ditolak saat load ----------

def test_condition_missing_required_field_rejected(data_dir):
    """B1: {'flag': {}} (field wajib hilang) → ditolak load, bukan KeyError runtime."""
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    dlg = next(x for x in data["dialogs"] if x["id"] == "dlg_side_offer")
    dlg["nodes"]["n1"]["choices"][0]["condition"] = {"flag": {}}
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "condition", "'flag'", "'key'")


def test_condition_relation_min_missing_value_rejected(data_dir):
    """B1: relation_min tanpa field 'value' → ditolak (KeyError('value') dulu)."""
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    dlg = next(x for x in data["dialogs"] if x["id"] == "dlg_side_offer")
    dlg["nodes"]["n1"]["choices"][0]["condition"] = {"relation_min": {"npc": "npc_guru"}}
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "condition", "relation_min", "'value'")


def test_condition_scalar_wrong_type_rejected(data_dir):
    """B1 (GAP-1): key skalar bernilai objek → ditolak (TypeError runtime dulu)."""
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    dlg = next(x for x in data["dialogs"] if x["id"] == "dlg_side_offer")
    dlg["nodes"]["n1"]["choices"][0]["condition"] = {"morality_min": {}}
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "condition", "morality_min")


def test_condition_month_non_numeric_rejected(data_dir):
    """B1 (GAP-1): month_min string non-digit → ditolak (ValueError runtime dulu)."""
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    dlg = next(x for x in data["dialogs"] if x["id"] == "dlg_side_offer")
    dlg["nodes"]["n1"]["choices"][0]["condition"] = {"month_min": "abc"}
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "condition", "month_min")


def test_condition_has_item_object_rejected(data_dir):
    """B1 (GAP-1): has_item bernilai objek → ditolak (unhashable runtime dulu)."""
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    dlg = next(x for x in data["dialogs"] if x["id"] == "dlg_side_offer")
    dlg["nodes"]["n1"]["choices"][0]["condition"] = {"has_item": {}}
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "condition", "has_item")


def test_condition_dict_value_non_numeric_rejected(data_dir):
    """T-A (review independen): field 'value' di dict-keys wajib angka —
    string/bool/None lolos dulu → TypeError '>=' runtime."""
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    dlg = next(x for x in data["dialogs"] if x["id"] == "dlg_side_offer")
    dlg["nodes"]["n1"]["choices"][0]["condition"] = \
        {"relation_min": {"npc": "npc_guru", "value": "abc"}}
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "relation_min", "'value'", "angka")


def test_condition_has_items_value_non_numeric_rejected(data_dir):
    """T-A: has_items dengan value string → ditolak (TypeError '>=' runtime dulu)."""
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    dlg = next(x for x in data["dialogs"] if x["id"] == "dlg_side_offer")
    dlg["nodes"]["n1"]["choices"][0]["condition"] = \
        {"has_items": {"item": "pil_qi", "value": "x"}}
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "has_items", "'value'", "angka")


def test_condition_string_null_still_allowed(data_dir):
    """Regresi Q3c: pola lama {'academy': null} (belum pilih akademi) tetap diterima."""
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    dlg = next(x for x in data["dialogs"] if x["id"] == "dlg_side_offer")
    dlg["nodes"]["n1"]["choices"][0]["condition"] = {"academy": None}
    _dump(dst, "dialogs/minimal.json", data)
    DataRegistry(data_dir=dst)  # tidak boleh error


def test_condition_numeric_null_rejected(data_dir):
    """Regresi Q3c: None untuk kunci numerik tetap ditolak (runtime int(None) TypeError)."""
    dst = data_dir
    data = _load(dst, "dialogs/minimal.json")
    dlg = next(x for x in data["dialogs"] if x["id"] == "dlg_side_offer")
    dlg["nodes"]["n1"]["choices"][0]["condition"] = {"month_min": None}
    _dump(dst, "dialogs/minimal.json", data)
    _expect_error(dst, "month_min")


# ---------- B2 (audit opencode): koneksi lokasi wajib timbal balik ----------

def test_location_connection_symmetric_rejected(data_dir):
    """B2: A→B tanpa B→A → ditolak saat load (softlock topologi)."""
    dst = data_dir
    data = _load(dst, "locations.json")
    hutan = next(x for x in data["locations"] if x["id"] == "loc_hutan")
    hutan["connections"] = []
    _dump(dst, "locations.json", data)
    _expect_error(dst, "loc_gerbang", "loc_hutan", "tidak menunjuk balik")


# ---------- agregasi: semua pelanggaran dilaporkan sekaligus ----------

def test_hunt_without_id_or_location_rejected(data_dir):
    """F2.3: zona berburu wajib id + location — tanpa itu web/_hunt crash
    (h["id"]/h["location"] diakses langsung) & zona tak pernah terpilih."""
    for target in ("id", "location"):
        cfg = json.loads((data_dir / "config.json").read_text(encoding="utf-8"))
        cfg.setdefault("world", {})["hunts"] = [{"id": "h1", "location": "loc_gerbang",
                                                  "pool": ["musuh_hutan"]}]
        cfg["world"]["hunts"][0].pop(target, None)
        (data_dir / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
        with pytest.raises(DataContractError) as ei:
            DataRegistry(data_dir=data_dir)
        assert f"wajib punya '{target}'" in str(ei.value)


def test_all_violations_collected(data_dir):
    """Bukan berhenti di error pertama — penulis data dapat gambaran lengkap."""
    dst = data_dir
    data = _load(dst, "quests/minimal.json")
    data["quests"][0]["objective"]["kind"] = "escort"
    data["quests"][1]["on_complete"]["effects"] = [{"type": "bless"}]
    _dump(dst, "quests/minimal.json", data)
    err = _expect_error(dst, "2 pelanggaran", "escort", "bless")
    assert "2 pelanggaran" in str(err)


def test_npc_default_dialog_root_level_validated(data_dir):
    """Bug #4: default_dialog di root NPC (bukan dialog_routes) harus divalidasi.

    session.py memakai npc.get('default_dialog') di root, tapi validator lama
    mengecek routes.get('default_dialog') yang selalu None — typo lolos."""
    dst = data_dir
    data = _load(dst, "npcs.json")
    data["npcs"][0]["default_dialog"] = "dlg_ghost_typo"
    _dump(dst, "npcs.json", data)
    _expect_error(dst, "dialog tak dikenal", "dlg_ghost_typo")
