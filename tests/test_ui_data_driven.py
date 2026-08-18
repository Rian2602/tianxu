"""Test pembersihan hardcode arc-1 dari UI — F1.4 (ENGINE_ADAPTATION_PLAN).

Dua lapis verifikasi:
1. BEHAVIOR: fungsi UI CLI menampilkan data (nama pemain, resep, NPC spar)
   — bukan literal arc-1.
2. STATIS: file frontend (`index.html`, `app.js`) bebas id/terminologi arc-1.
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


# ---------- behavior: CLI ----------

def test_cli_header_academy_without_hanzi_no_crash(registry, session, capsys):
    """B3 (audit opencode): akademi tanpa hanzi/pinyin (sah kontrak) → tidak crash."""
    from src.cli import print_header
    session.state.player.academy = "akademi_bambu"  # fixture: tanpa hanzi/pinyin
    print_header(session)
    out = capsys.readouterr().out
    assert "Akademi Bambu" in out


def test_cli_header_uses_player_name(registry, session, capsys):
    """F1.4: print_header menampilkan nama dari data — ganti nama → tampil nama baru."""
    from src.cli import print_header
    session.state.player.name = "Lin Feng"
    print_header(session)
    out = capsys.readouterr().out
    assert "Lin Feng" in out


def test_cli_explore_menu_lists_recipes_from_data(registry, session, capsys):
    """F1.4: menu racik derive dari registry.recipes — bukan material_herba."""
    from src.cli import explore_menu
    # tambahkan resep agar menu racik muncul (lokasi awal aman)
    registry.recipes.append({
        "id": "r_eliksir",
        "result": "pil_qi",
        "ingredients": [{"item": "pil_qi", "count": 1}],
    })
    explore_menu(session)
    out = capsys.readouterr().out
    assert "[racik]" in out
    assert "r_eliksir" in out
    assert "material_herba" not in out
    assert "rc_pil_qi" not in out


def test_cli_spar_npcs_from_data(registry, session):
    """F1.4: daftar NPC sparing derive dari can_spar — bukan literal id NPC."""
    npcs = [n["id"] for n in registry.npcs if session.can_spar(n)]
    assert "npc_guru" in npcs  # can_spar dari data (combat + spar_require terpenuhi)
    assert not any(x in ("hanxiu", "gucanghai") for x in npcs)


def test_cli_racik_requires_recipe_argument():
    """F1.4: cabang craft tanpa default literal resep (resep wajib disebut)."""
    import src.cli as cli
    src_text = Path(cli.__file__).read_text(encoding="utf-8")
    assert 'else "rc_pil_qi"' not in src_text
    assert "material_herba" not in src_text


# ---------- statis: file frontend ----------

@pytest.mark.parametrize("fname", ["index.html", "app.js"])
def test_frontend_no_arc1_strings(fname):
    """F1.4: file statis web bebas id/terminologi arc-1 (selain komentar docs)."""
    text = (WEB_STATIC / fname).read_text(encoding="utf-8")
    for bad in FORBIDDEN:
        assert bad not in text, f"{fname} masih memuat {bad!r}"


def test_cli_py_no_arc1_literals():
    """F1.4: src/cli.py bebas literal id/terminologi arc-1 (termasuk komentar)."""
    import src.cli as cli
    text = Path(cli.__file__).read_text(encoding="utf-8")
    for bad in FORBIDDEN:
        assert bad not in text, f"src/cli.py masih memuat {bad!r}"


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
