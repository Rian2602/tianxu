"""TDD test for unlock_arc mechanic — RED phase.

Bug: techniques.csv has no unlock_arc column → mechanic dead.
Fix: Add unlock_arc column + populate data for cross-academy techniques.
"""

from __future__ import annotations


def test_technique_csv_has_unlock_arc_column():
    """techniques.csv harus punya kolom unlock_arc."""
    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from src.loader import DataRegistry
    registry = DataRegistry(str(ROOT / "data"))
    # Check that the raw CSV data has unlock_arc as a key
    for tid, tech in registry.techniques.items():
        assert "unlock_arc" in tech, \
            f"Technique {tid} missing 'unlock_arc' column in CSV"


def test_unlock_arc_tech_available_after_arc_completion(session, registry):
    """Technique dengan unlock_arc tersedia setelah arc selesai."""
    # Find a technique with unlock_arc (or skip if none)
    tech_with_arc = None
    for t in registry.techniques.values():
        if t.get("unlock_arc"):
            tech_with_arc = t
            break
    if not tech_with_arc:
        import pytest
        pytest.skip("No technique has unlock_arc value — add data first")

    arc_id = tech_with_arc["unlock_arc"]
    # Find the arc's final quest
    arc = next((a for a in registry.config.get("arcs", []) if a["id"] == arc_id), None)
    if not arc:
        import pytest
        pytest.skip(f"Arc {arc_id} not found in config")

    final_quest = arc["final_quest"]

    # Before completing arc: technique should NOT be available
    techniques_before = registry.player_techniques(
        "akademi_bambu", "realm_chuji",
        completed_quests=frozenset(),
        owned=()
    )
    assert tech_with_arc["id"] not in [t["id"] for t in techniques_before], \
        f"Technique {tech_with_arc['id']} should not be available before arc completion"

    # After completing arc: technique SHOULD be available
    techniques_after = registry.player_techniques(
        "akademi_bambu", "realm_chuji",
        completed_quests=frozenset([final_quest]),
        owned=()
    )
    assert tech_with_arc["id"] in [t["id"] for t in techniques_after], \
        f"Technique {tech_with_arc['id']} should be available after completing {final_quest}"
