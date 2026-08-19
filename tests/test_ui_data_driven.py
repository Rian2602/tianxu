"""Test pembersihan hardcode arc-1 dari UI — F1.4 (ENGINE_ADAPTATION_PLAN).

Verifikasi statis: file frontend (`index.html`, `app.js`) bebas id/terminologi arc-1.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

WEB_STATIC = Path(__file__).resolve().parent.parent / "web" / "static"

# string/id yang TIDAK boleh muncul lagi di UI (selain di komentar docs)
FORBIDDEN = [
    "material_herba",
    "rc_pil_qi",
    "rc_pil_pemulihan",
    "loc_wilayah_berburu",
    "hanxiu",
    "gucanghai",
    "Arc 1 Tamat",
    "Bukti Konsep",
    "Arc Akademi",
]


# ---------- behavior: engine data ----------

def test_spar_npcs_data_driven(registry, session):
    """F1.4: daftar NPC sparing derive dari can_spar — bukan literal id NPC."""
    npcs = [n["id"] for n in registry.npcs if session.can_spar(n)]
    assert "npc_guru" in npcs  # can_spar dari data (combat + spar_require terpenuhi)
    assert not any(x in ("hanxiu", "gucanghai") for x in npcs)


# ---------- statis: file frontend ----------

@pytest.mark.parametrize("fname", ["index.html", "app.js"])
def test_frontend_no_arc1_strings(fname):
    """F1.4: file statis web bebas id/terminologi arc-1 (selain komentar docs)."""
    text = (WEB_STATIC / fname).read_text(encoding="utf-8")
    for bad in FORBIDDEN:
        assert bad not in text, f"{fname} masih memuat {bad!r}"


def test_appjs_hunt_data_driven():
    """F1.4/F2.3: renderExplore memakai c.hunts (multi-zona), bukan id lokasi literal."""
    text = (WEB_STATIC / "app.js").read_text(encoding="utf-8")
    assert "c.hunts" in text
    assert "c.hunt." not in text  # akses lama dict tunggal sudah diganti
    assert "loc_wilayah_berburu" not in text


def test_appjs_academy_label_generic():
    """F1.4: label 'Paviliun' diganti 'Akademi' (istilah config), semua kemunculan."""
    text = (WEB_STATIC / "app.js").read_text(encoding="utf-8")
    assert "Paviliun" not in text
    assert "Akademi" in text
