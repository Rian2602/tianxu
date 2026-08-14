"""Test progresi kultivasi — multiplier akar spiritual & breakthrough (§9.1).

Matematika deterministik: exp_next(level 10) = round(10 × 1.2⁹) = 52, jadi
gain_exp(20) tidak menaikkan level dan gain_exp(52) memicu breakthrough.
"""

from __future__ import annotations

from src.engine.cultivation import gain_exp


def test_multiplier_akar_diterapkan(session):
    session.state.player.realm_level = 10  # exp_next = 52, aman untuk exp kecil
    session.state.player.exp = 0
    session.state.player.roots = "akar_low"  # 0.8×
    gain_exp(session.state, session.reg, 20)
    assert session.state.player.exp == 16
    session.state.player.roots = "akar_high"  # 1.25×
    gain_exp(session.state, session.reg, 20)
    assert session.state.player.exp == 16 + 25


def test_breakthrough_level_10_ke_ranah_berikutnya(session):
    session.state.player.realm = "realm_pengumpul_qi"
    session.state.player.realm_level = 10
    session.state.player.exp = 0
    gain_exp(session.state, session.reg, 52)  # exp_next di level 10
    assert session.state.player.realm == "realm_pembangun_fondasi"
    assert session.state.player.realm_level == 1
    assert any("Terobosan" in e["text"] for e in session.state.log)


def test_ranah_tertinggi_tidak_breakthrough(session):
    session.state.player.realm = "realm_penantang_surga"
    session.state.player.realm_level = 10
    session.state.player.exp = 0
    gain_exp(session.state, session.reg, 52)
    assert session.state.player.realm == "realm_penantang_surga"
    assert session.state.player.realm_level == 10


def test_ranah_tertinggi_exp_dicap_tidak_hang(session):
    """A1: di puncak ranah, exp berlebih di-cap (tidak hang loop tak berujung).
    Tepat di threshold (52) — pre-fix: loop jalan, level di-reset, pesan lama;
    post-fix: cap exp = 51 + pesan baru 'exp tertahan'."""
    session.state.player.realm = "realm_penantang_surga"
    session.state.player.realm_level = 10
    session.state.player.exp = 0
    gain_exp(session.state, session.reg, 52)  # exp_next di level 10
    assert session.state.player.realm == "realm_penantang_surga"
    assert session.state.player.realm_level == 10
    assert session.state.player.exp == 51  # di-cap di bawah threshold
    assert any("exp tertahan" in e["text"] for e in session.state.log)


def test_ranah_tertinggi_exp_raksasa_selesai_cepat(session):
    """A1: exp raksasa (10 juta) di puncak ranah selesai cepat — post-fix langsung
    cap di iterasi pertama (bukan ~192 ribu iterasi)."""
    import time

    session.state.player.realm = "realm_penantang_surga"
    session.state.player.realm_level = 10
    session.state.player.exp = 0
    t0 = time.monotonic()
    gain_exp(session.state, session.reg, 10_000_000)
    dt = time.monotonic() - t0
    assert session.state.player.realm_level == 10
    assert session.state.player.exp < session.state.exp_next(session.reg)
    assert dt < 0.5  # cap langsung — bukan ratusan detik
    assert any("exp tertahan" in e["text"] for e in session.state.log)
