"""Anti-regresi alur story — integritas connection_gates & kolisi item.

Latar: audit reachability menemukan backdoor Arsip Publik → Terlarang →
Terdalam → Bawah Terdalam tanpa gate (konten Arc 4–7 reachable sejak Arc 2),
kolisi item id catatan_siklus antara main reward dan gather side quest, serta
slot jadwal NPC ke lokasi yang tidak ada, dan gerbang ending yang mengecek
nilai status kompanion yang tak pernah di-set. Test ini mengunci perbaikannya.
"""

from __future__ import annotations

import json

import pytest

from src.loader import DataRegistry, DATA_DIR

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "quests" / "arc02.json").exists(),
    reason="data story belum ada di data/",
)


@pytest.fixture(scope="module")
def registry() -> DataRegistry:
    return DataRegistry()


def _loc(registry: DataRegistry, loc_id: str) -> dict:
    match = [l for l in registry.locations if l["id"] == loc_id]
    assert match, f"lokasi {loc_id} tidak ditemukan"
    return match[0]


def test_archive_chain_gated(registry: DataRegistry):
    """Backdoor Arc 2 → konten Arc 4–7 harus tertutup gate bertingkat."""
    assert _loc(registry, "loc_archive_public")["connection_gates"] == {
        "loc_forbidden_archive": "flag_version_iii_read",
        "loc_jiang_yan_records": "flag_name_jiang_yan_known",
    }
    assert _loc(registry, "loc_forbidden_archive")["connection_gates"] == {
        "loc_tianxu_deepest_chamber": "flag_stakes_of_stopping_source_known",
    }
    assert _loc(registry, "loc_tianxu_deepest_chamber")["connection_gates"] == {
        "loc_below_deepest": "flag_last_night_complete",
        "loc_tianxu_main_hall": "state_final_principle",
    }


def test_late_game_unreachable_before_arc4(registry: DataRegistry):
    """Simulasi BFS dengan flag setelah quest_a02_c02_005 (Arc 2 bab 2):
    ruang endgame TIDAK boleh reachable dari Training Hall."""
    flags = {
        "flag_first_lesson_done", "flag_disturbance_investigated",
        "flag_evidence_missing_disciple",
    }
    seen = {"loc_training_hall"}
    frontier = ["loc_training_hall"]
    while frontier:
        cur = frontier.pop()
        loc = _loc(registry, cur)
        gates = loc.get("connection_gates") or {}
        for nxt in loc.get("connections", []):
            gate = gates.get(nxt)
            if nxt in seen or (gate and gate not in flags):
                continue
            seen.add(nxt)
            frontier.append(nxt)
    for forbidden in ("loc_below_deepest", "loc_jiang_yan_records",
                      "loc_tianxu_main_hall", "loc_forbidden_archive",
                      "loc_tianxu_deepest_chamber"):
        assert forbidden not in seen, f"{forbidden} bocor sejak Arc 2"


def test_reform_evidence_item_separated(registry: DataRegistry):
    """Gather reform_002 memakai item sendiri bersumber dari Hutan Akademi,
    bukan reward main quest catatan_siklus (gather engine = hitung inventory)."""
    obj = registry.quest("quest_faction_reform_002")["objective"]
    assert obj["item"] == "catatan_korupsi_formasi"

    item = registry.items.get("catatan_korupsi_formasi")
    assert item and item.get("type") == "key_item"
    assert "catatan_korupsi_formasi" in registry.key_items
    # sumber nyata di Hutan Akademi — hint tidak lagi palsu
    hunt = next(h for h in registry.config["world"]["hunts"]
                if h["location"] == "loc_hutan_akademi")
    assert any(s["item"] == "catatan_korupsi_formasi" for s in hunt["search_items"])
    # catatan_siklus tetap eksklusif reward Arc 2
    assert registry.quest("quest_a02_c02_005")["on_complete"]["effects"][1]["id"] \
        == "catatan_siklus"


def test_reform_003_requires_cave_gate_flag(registry: DataRegistry):
    """reach Gua Tersembunyi tidak boleh tersedia sebelum gerbangnya terbuka."""
    avail = registry.quest("quest_faction_reform_003").get("available_from", {})
    assert "flag_disturbance_investigated" in avail.get("requires_flags", [])


def test_no_schedule_references_unknown_location(registry: DataRegistry):
    """Slot jadwal ke lokasi yang tidak ada = NPC untalkable di jam itu."""
    known = {l["id"] for l in registry.locations}
    for nid, slots in registry.npc_schedules.items():
        for slot in slots or []:
            loc = slot.get("location")
            assert loc is None or loc in known, \
                f"{nid} dijadwalkan ke lokasi tak dikenal: {loc}"


def _walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def _status_refs_and_setters() -> tuple[set, set]:
    """Kumpulkan (key, value) status yang DIREFERENSI kondisi vs DI-SET efek."""
    refs: set = set()
    setters: set = set()
    for folder in ("dialogs", "quests"):
        for path in sorted((DATA_DIR / folder).glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            for d in _walk(data):
                key = d.get("key")
                if not (isinstance(key, str) and key.startswith("state_")
                        and key.endswith("_status")) or "value" not in d:
                    continue
                pair = (key, str(d["value"]))
                if d.get("type") == "flag":
                    setters.add(pair)
                else:
                    refs.add(pair)
    return refs, setters


def test_second_life_gate_blocks_separated_lin_yue():
    """Gerbang ending true harus mengecek nilai yang BENAR-benar bisa di-set.

    Audit: flag_not memeriksa 'disillusioned' padahal setter state_lin_yue_status
    hanya menghasilkan loyal/separated — cek mati. Desain: Lin Yue yang berpisah
    ('separated') mengunci Second Life, konsisten tema Arc 5."""
    found = []
    for path in sorted((DATA_DIR / "dialogs").glob("*.json")):
        for d in _walk(json.loads(path.read_text(encoding="utf-8"))):
            if d.get("option") == "second_life":
                found.append((path.name, d))
    assert len(found) == 1, f"opsi second_life harus unik, dapat: {found}"
    _, opt = found[0]
    entry = [f for f in opt["condition"]["flag_not"]
             if f.get("key") == "state_lin_yue_status"]
    assert entry and entry[0]["value"] == "separated", \
        f"gerbang harus cek 'separated', dapat: {entry}"


def test_status_flag_conditions_have_setters():
    """Setiap (key,value) state_*_status yang dicek kondisi wajib punya setter.

    Kelas bug: copy-paste gerbang antar kompanion menghasilkan referensi ke
    nilai yang tidak pernah di-set siapa pun (cek mati senyap)."""
    refs, setters = _status_refs_and_setters()
    dead = sorted(refs - setters)
    assert not dead, (
        f"kondisi mengecek status yang tak pernah di-set efek mana pun: {dead}")


def test_no_premature_reachable_locations():
    """Sweep chain penuh: temuan reachability harus persis snapshot di bawah.

    Setiap id di bawah ini SUDAH ditelaah & diterima (bukan bug baru):
    - selisih 2-3 = pacing normal (gerbang terbuka, dipakai cerita belakangan)
    - loc_pavilion_yanzhi (22)  : pavilion adalah hub kampus yang memang
      terbuka sejak awal; cerita baru menargetinya di Arc 5
    - loc_grandmaster_chamber   : kebocoran routes.general yang sudah
      dievaluasi & diterima pengguna
    - loc_jiang_yan_records(13) : konsekuensi keputusan gerbang Arc 3
      (flag_name_jiang_yan_known, arc03.json) — ruangan dibuka sejak itu,
      kontennya baru penting Arc 6
    Temuan DI LUAR daftar ini = kebocoran baru → test gagal."""
    from tools.audit_location_gates import audit_rows
    got = {(r["loc_id"], r["gap"]) for r in audit_rows()}
    expected = {
        ("loc_pavilion_yanzhi", 22),
        ("loc_outer_region", 2),
        ("loc_grandmaster_chamber", 2),
        ("loc_archive_public", 2),
        ("loc_mo_chen_meeting", 2),
        ("loc_jiang_yan_records", 13),
        ("loc_mountain_gate", 2),
        ("loc_mentor_ground", 3),
    }
    baru = got - expected
    hilang = expected - got
    assert not baru, f"kebocoran BARU terdeteksi (telaah dulu!): {sorted(baru)}"
    assert not hilang, f"snapshot berubah (gerbang berubah?): {sorted(hilang)}"
