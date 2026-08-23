"""TDD test for exp multiplier bypass fix — RED phase.

Bug: effects.py exp handler bypasses gain_exp() → roots multiplier not applied.
Fix: Replace direct dantian_exp += with gain_exp() call.
"""

from __future__ import annotations


def test_effect_exp_applies_roots_multiplier(session, registry):
    """Effect 'exp' harus pakai gain_exp() agar roots multiplier diterapkan."""
    # Setup: tambah root tier dengan multiplier 1.5x
    registry.roots_tier["akar_tinggi"] = {"id": "akar_tinggi", "exp_multiplier": 1.5}
    session.state.player.roots = "akar_tinggi"

    # Verify setup
    mult = session.state.exp_multiplier(registry)
    assert mult == 1.5, f"exp_multiplier harus 1.5, got {mult}"

    # Apply exp effect langsung (bukan via use_item)
    from src.engine.effects import apply
    apply(session.state, registry, [{"type": "exp", "value": 10}])

    # Verify: exp harus 10 * 1.5 = 15, bukan 10
    expected = round(10 * 1.5)
    assert session.state.player.dantian_exp == expected, \
        f"dantian_exp harus {expected} (10 × 1.5), got {session.state.player.dantian_exp}"
