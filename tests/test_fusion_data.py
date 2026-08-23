"""Anti-regresi data fusion & passives — audit round 2.

Latar: 3 dari 5 resep fusion salah `result` (copy-paste ke
teknik_pedang_api_membara) dan dua passive tertukar pavilion sumber.
Test ini mengunci perbaikannya.
"""

from __future__ import annotations

import pytest

from src.loader import DataRegistry, DATA_DIR

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "quests" / "arc02.json").exists(),
    reason="data story belum ada di data/",
)


@pytest.fixture(scope="module")
def registry() -> DataRegistry:
    return DataRegistry()


def _fusion(registry: DataRegistry, fid: str) -> dict:
    match = [f for f in registry.fusions if f["id"] == fid]
    assert match, f"fusion {fid} tidak ditemukan"
    return match[0]


def test_fusion_results_unique(registry: DataRegistry):
    results = [f["result"] for f in registry.fusions if f.get("result")]
    dupes = {r for r in results if results.count(r) > 1}
    assert not dupes, f"result fusion duplikat antar resep: {sorted(dupes)}"


def test_pavilion_fusion_results_thematic(registry: DataRegistry):
    """Result fusion harus teknik capstone sesuai tema pavilion, bukan pedang-api."""
    expected = {
        "fusion_wuxin_qi": ("teknik_aliran_qi_sejati", "attack", "air"),
        "fusion_yanzhi_hutan": ("teknik_nafas_hutan_suci", "heal", "kayu"),
        "fusion_liuguang_arus": ("teknik_arus_laut_dalam", "defend", "air"),
    }
    for fid, (rid, kind, element) in expected.items():
        assert _fusion(registry, fid)["result"] == rid, f"{fid} salah result"
        tek = registry.technique(rid)
        assert tek, f"teknik hasil {rid} tidak ada di techniques.csv"
        assert tek["kind"] == kind, f"{rid} kind {tek['kind']} != {kind}"
        assert tek["element"] == element, f"{rid} elemen {tek['element']} != {element}"


def test_passive_pavilion_assignment(registry: DataRegistry):
    """Flowing Qi milik Wuxin (+1 Qi guard), Earth Guardian milik Liuguang (-5% dmg)."""
    sources = {p["id"]: p.get("source") for p in registry.passives}
    assert sources["passive_flowing_qi"] == "pavilion_wuxin"
    assert sources["passive_earth_guardian"] == "pavilion_liuguang"
