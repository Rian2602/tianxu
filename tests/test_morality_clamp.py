"""TDD test for morality clamp in resolve_choose — RED phase.

Bug: resolve_choose sets morality directly without clamp_morality().
Fix: Add clamp_morality() call after morality set.
"""

from __future__ import annotations


def test_resolve_choose_clamps_morality(session, registry):
    """resolve_choose harus clamp morality ke config bounds."""
    # Setup: config bounds [-50, 50]
    registry.config["morality"] = {"min": -50, "max": 50}
    session.state.player.morality = 0

    # Setup: current quest dengan choose option yang set morality=999
    session.state.current_quest = "q_test_morality"
    registry.quest_by_id["q_test_morality"] = {
        "id": "q_test_morality",
        "title": "Test Morality",
        "kind": "main",
        "objective": {
            "kind": "choose",
            "options": [
                {"value": "evil", "set": {"morality": 999}}
            ],
        },
    }

    # Call resolve_choose directly
    session.quest.resolve_choose("evil")

    # Verify: morality harus clamp ke max (50), bukan 999
    assert session.state.player.morality == 50, \
        f"morality harus clamp ke 50, got {session.state.player.morality}"


def test_resolve_choose_clamps_morality_negative(session, registry):
    """resolve_choose harus clamp morality negatif juga."""
    registry.config["morality"] = {"min": -50, "max": 50}
    session.state.player.morality = 0

    session.state.current_quest = "q_test_morality2"
    registry.quest_by_id["q_test_morality2"] = {
        "id": "q_test_morality2",
        "title": "Test Morality 2",
        "kind": "main",
        "objective": {
            "kind": "choose",
            "options": [
                {"value": "very_evil", "set": {"morality": -999}}
            ],
        },
    }

    session.quest.resolve_choose("very_evil")

    # Verify: morality harus clamp ke min (-50), bukan -999
    assert session.state.player.morality == -50, \
        f"morality harus clamp ke -50, got {session.state.player.morality}"
