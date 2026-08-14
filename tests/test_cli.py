"""Smoke test CLI — playthrough terskrip lewat input() tiruan (deterministik).

Menjalankan `src.cli.main` dari awal sampai akhir Arc Akademi (cabang 3aa)
dengan battle dipercepat (1 serangan menang). Memastikan loop CLI, alur
quest-dialog-battle-choose, dan deteksi akhir arc bekerja end-to-end.
"""

from __future__ import annotations

import os
from pathlib import Path

from src.engine.battle import BattleEngine
from src.engine.session import GameSession

ROOT = Path(__file__).resolve().parent.parent


def test_cli_playthrough_3aa(monkeypatch, capsys):
    # battle selalu menang dalam 1 serangan (deterministik)
    monkeypatch.setattr(BattleEngine, "_calc_damage", lambda self, a, d, ea, ed: (99999, False))
    monkeypatch.setattr("src.engine.session.GameSession._is_npc_available", lambda self, npc: True)

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
    assert "AKHIR ARC 1: AKADEMI CHANGFENG" in out, "arc tidak selesai di CLI"
    assert "Konfrontasi Terbuka Penatua An" in out, "branch tidak ada di CLI"
    assert "Ingatan" in out, "ingatan tidak ditampilkan di CLI"
    assert "Moral" in out
    save_path = ROOT / "saves" / "test_arc_end.json"
    assert save_path.exists(), "loop CLI berhenti sebelum pemain bisa menyimpan"
    os.remove(save_path)


def test_cli_full_playthrough_commands(monkeypatch, capsys):
    """Satu run terskrip: perintah jelajah + arc penuh (3aa) + pasca-arc
    (side quest, battle hunt, ingatan, pasang senjata) — semua deterministik."""
    monkeypatch.setattr(BattleEngine, "_calc_damage", lambda self, a, d, ea, ed: (99999, False))
    monkeypatch.setattr(BattleEngine, "_try_flee", lambda self, pc, b: False)
    monkeypatch.setattr(BattleEngine, "_enemy_turn", lambda self, pc, b: None)
    monkeypatch.setattr("src.engine.session.GameSession._is_npc_available", lambda self, npc: True)
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, b: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)
    monkeypatch.setattr("src.engine.session.random.choice", lambda seq: "eno_serigala_qi")
    monkeypatch.setattr("src.engine.session.random.random", lambda: 0.9)

    script = [
        "",                        # input kosong di mode explore → lanjut
        "pindah",                  # pindah tanpa tujuan
        "bicara",                  # bicara tanpa NPC
        "pasang",                  # pasang tanpa senjata
        "spar",                    # spar tanpa NPC
        "bantuan",
        "meditasi 1",              # ditolak (gerbang tidak aman)
        "istirahat 1",             # ditolak
        "simpan cli_awal",         # ditolak
        "beli pil_qi 1",           # tidak ada pedagang
        "jual material_tulang 1",  # tidak ada pedagang
        "racik rc_pil_qi",         # ditolak (tidak aman)
        "cari",                    # ditolak (bukan Wilayah Berburu)
        "berburu",                 # ditolak (bukan Wilayah Berburu)
        "pakai pil_qi",            # item tidak dimiliki
        "ingatan",                 # belum ada ingatan
        "bicara npc_penjaga", "1", "lanjut", "lanjut",
        "pindah loc_aula_ujian",
        "talk npc_gucanghai", "lanjut", "1", "lanjut", "lanjut", "lanjut",
        "pindah loc_arena",
        "talk npc_hanxiu", "lanjut", "lanjut",
        "teknik", "serang",               # teknik tanpa akademi → attack → menang spar
        "pilih akademi_elemen",
        "pindah loc_aula_ujian", "pindah loc_paviliun",
        "talk npc_suqing", "1", "lanjut",
        "pindah loc_perpustakaan", "tunggu 12", "pindah loc_ruang_lonceng",
        "lanjut", "1", "1", "lanjut",   # cabang 3aa
        "pindah loc_perpustakaan", "pindah loc_paviliun",
        "talk npc_penatua", "1", "lanjut", "lanjut",
        "pindah loc_perpustakaan",
        "talk npc_moyun", "lanjut", "lanjut",
        # pasca arc: CLI tetap hidup — istirahat, pasang senjata, side quest, berburu
        "pindah loc_paviliun", "pindah loc_aula_ujian", "pindah loc_asrama", "istirahat 8",
        "pindah loc_aula_ujian", "pindah loc_gerbang_akademi",
        "pasang pedang_angin",
        "bicara npc_pemburu", "1", "lanjut",      # ambil side quest berburu
        "pindah loc_wilayah_berburu", "berburu",
        "teknik", "bertahan", "item", "kabur", "foo", "teknik tek_elemen_bola_api", "serang",
        "ingatan", "ingatan mem_999",
        "simpan cli_arc_end",
        "keluar",
    ]
    inputs = iter(script)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    from src.cli import main

    main()
    out = capsys.readouterr().out
    assert "AKHIR ARC 1: AKADEMI CHANGFENG" in out, "arc tidak selesai di CLI"
    assert "Belum ada ingatan" in out, "ingatan kosong tidak ditampilkan"
    assert "NPC di sini" in out, "daftar NPC tanpa arg tidak ditampilkan"
    assert "Tujuan:" in out, "daftar tujuan tanpa arg tidak ditampilkan"
    assert "Senjata di inventori" in out, "daftar senjata tanpa arg tidak ditampilkan"
    assert "Pedang Angin" in out, "senjata terpasang tidak tampil di header"
    assert "Tugas Berburu" in out, "side quest tidak tampil di header"
    assert "tek_elemen" in out, "daftar teknik battle tidak tampil"


def test_cli_load_missing_save(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("src.engine.session.SAVES_DIR", tmp_path)
    monkeypatch.setattr("sys.argv", ["src/cli.py", "-l", "save_cli_hantu"])
    monkeypatch.setattr("builtins.input", lambda prompt="": (_ for _ in ()).throw(EOFError))

    from src.cli import main

    main()
    out = capsys.readouterr().out
    assert "Save 'save_cli_hantu' tidak ditemukan" in out


def test_cli_load_corrupt_save(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("src.engine.session.SAVES_DIR", tmp_path)
    (tmp_path / "save_rusak.json").write_text("{bukan json", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["src/cli.py", "-l", "save_rusak"])

    from src.cli import main

    main()
    out = capsys.readouterr().out
    assert "Gagal memuat save 'save_rusak'" in out
