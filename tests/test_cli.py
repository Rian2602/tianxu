"""Smoke test CLI — playthrough terskrip lewat input() tiruan (deterministik).

Menjalankan `src.cli.main` dari awal sampai akhir Arc Akademi (cabang 3aa)
dengan battle dipercepat (1 serangan menang). Memastikan loop CLI, alur
quest-dialog-battle-choose, dan deteksi akhir arc bekerja end-to-end.
"""

from __future__ import annotations

import os
from pathlib import Path

from src.engine.battle import BattleEngine

ROOT = Path(__file__).resolve().parent.parent


def test_cli_playthrough_3aa(monkeypatch, capsys):
    # battle selalu menang dalam 1 serangan (deterministik)
    monkeypatch.setattr(BattleEngine, "_calc_damage", lambda self, a, d, ea, ed: (99999, False))

    script = [
        "talk npc_penjaga", "1", "lanjut", "lanjut",
        "pindah loc_aula_ujian",
        "talk npc_gucanghai", "lanjut", "1", "lanjut", "lanjut", "lanjut",
        "pindah loc_arena",
        "talk npc_hanxiu", "lanjut", "lanjut",
        "serang",                       # menang spar
        "pilih akademi_elemen",
        "pindah loc_aula_ujian", "pindah loc_paviliun",
        "talk npc_suqing", "1", "lanjut",
        "pindah loc_perpustakaan", "tunggu 12", "pindah loc_ruang_lonceng",
        "lanjut", "1", "1", "lanjut",   # cabang 3aa (node_scene → pilih → cara → aa)
        "pindah loc_perpustakaan", "pindah loc_paviliun",
        "talk npc_penatua", "1", "lanjut", "lanjut",
        "pindah loc_perpustakaan",
        "talk npc_moyun", "lanjut", "lanjut",
        # pasca arc: CLI tidak boleh langsung berhenti — pemain bisa pindah & simpan
        "pindah loc_paviliun", "pindah loc_aula_ujian", "pindah loc_asrama",
        "simpan test_arc_end",
    ]
    inputs = iter(script + ["keluar"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    from src.cli import main

    main()
    out = capsys.readouterr().out
    assert "AKHIR ARC AKADEMI" in out, "arc tidak selesai di CLI"
    assert "Ingatan" in out, "ingatan tidak ditampilkan di CLI"
    assert "Moral" in out
    save_path = ROOT / "saves" / "test_arc_end.json"
    assert save_path.exists(), "loop CLI berhenti sebelum pemain bisa menyimpan"
    os.remove(save_path)
