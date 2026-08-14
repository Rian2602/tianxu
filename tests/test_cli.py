"""Smoke test CLI — playthrough terskrip lewat input() tiruan (deterministik).

Menjalankan `src.cli.main` dari awal sampai akhir Arc Akademi (cabang 3aa)
dengan battle dipercepat (1 serangan menang). Memastikan loop CLI, alur
quest-dialog-battle-choose, dan deteksi akhir arc bekerja end-to-end.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from src.cli import battle_view, choose_view, dialog_view, explore_menu, print_header
from src.engine.battle import BattleEngine
from src.engine.session import GameSession

ROOT = Path(__file__).resolve().parent.parent


# Tahap A (DoD §11.2 #1): playthrough end-to-end 3 akademi — satu body, 3 varian
PLAYTHROUGH_AKADEMI = [
    pytest.param("akademi_elemen", "Paviliun Elemen", False, id="elemen"),
    pytest.param("akademi_senjata", "Paviliun Senjata", False, id="senjata"),
    pytest.param("akademi_summoning", "Paviliun Summoning", True, id="summoning"),
]


@pytest.mark.parametrize("akademi, nama_akademi, pakai_roh", PLAYTHROUGH_AKADEMI)
def test_cli_playthrough_3aa(monkeypatch, capsys, akademi, nama_akademi, pakai_roh):
    """Playthrough penuh q01–q07 (cabang 3aa) untuk tiap akademi."""
    # battle deterministik: serangan pemain 1-hit menang, giliran musuh dinonaktifkan
    # (aman dengan turn_order "speed")
    monkeypatch.setattr(BattleEngine, "_calc_damage", lambda self, a, d, ea, ed: (99999, False))
    monkeypatch.setattr(BattleEngine, "_enemy_turn", lambda self, pc, b: None)
    monkeypatch.setattr("src.engine.session.GameSession._is_npc_available", lambda self, npc: True)

    script = [
        "talk npc_penjaga", "1", "lanjut", "lanjut",
        "pindah loc_aula_ujian",
        "talk npc_gucanghai", "lanjut", "1", "lanjut", "lanjut", "lanjut",
        "pindah loc_arena",
        "talk npc_hanxiu", "lanjut", "lanjut",
        "serang",                       # menang spar
        "pilih " + akademi,
        "pindah loc_aula_ujian", "pindah loc_paviliun",
        "talk npc_suqing", "1", "lanjut",
        "pindah loc_perpustakaan", "tunggu 12", "pindah loc_ruang_lonceng",
        "lanjut", "1", "1", "lanjut",   # cabang 3aa (node_scene → pilih → cara → aa)
        "pindah loc_perpustakaan", "pindah loc_paviliun",
        "talk npc_penatua", "1", "lanjut", "lanjut",
        "pindah loc_perpustakaan",
        "talk npc_moyun", "lanjut", "1", "lanjut",  # penutup: pilih opsi ingatan mem_02
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
    assert f"Akademi: {nama_akademi}" in out, f"akademi {akademi} tidak tampil di header"
    if pakai_roh:
        assert "Roh" in out, "kompanion summoning tidak tampil di CLI"
    # baseline pacing (guardrail A2): level akhir arc dalam target Lv 4–6
    levels = re.findall(r"Lv\.(\d+)", out)
    assert levels, "tidak ada baris level di output CLI"
    end_lv = int(levels[-1])
    assert 4 <= end_lv <= 6, f"arc-end level {end_lv} di luar target Lv 4–6 (baseline pacing)"
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
        "pakai pil_qi",            # pakai item (dimiliki dari inventori awal)
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
        "talk npc_moyun", "lanjut", "1", "lanjut",  # penutup: pilih opsi ingatan mem_02
        # pasca arc: CLI tetap hidup — istirahat, pasang senjata, side quest, berburu
        "pindah loc_paviliun", "pindah loc_aula_ujian", "pindah loc_asrama", "istirahat 8",
        "pindah loc_aula_ujian", "pindah loc_gerbang_akademi",
        "pasang pedang_angin",
        "bicara npc_pemburu", "1", "lanjut",      # ambil side quest berburu
        "pindah loc_wilayah_berburu", "berburu",
        "teknik", "bertahan", "item", "kabur", "foo", "teknik tek_elemen_bola_api", "serang",
        "ingatan", "ingatan mem_999",
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


def test_dialog_view_without_dialog(session, capsys):
    dialog_view(session)
    assert capsys.readouterr().out == ""          # tidak ada dialog → return


def test_choose_view_without_choose(session, capsys):
    choose_view(session)
    assert capsys.readouterr().out == ""          # tidak ada choose → return


def test_dialog_view_speaker_variants(session, monkeypatch, capsys):
    monkeypatch.setattr(session, "view",
                        lambda: {"dialog": {"speaker": "system", "text": "pesan sistem", "choices": []}})
    dialog_view(session)                          # speaker system
    monkeypatch.setattr(session, "view",
                        lambda: {"dialog": {"speaker": "player", "text": "kata pemain", "choices": []}})
    dialog_view(session)                          # speaker lain → teks polos
    out = capsys.readouterr().out
    assert "pesan sistem" in out and "kata pemain" in out


def test_print_header_companion(session, capsys):
    session.state.companion = {"id": "komp_roh_awan", "hp": 5, "active": True}
    print_header(session)                         # baris roh di header
    out = capsys.readouterr().out
    assert "Roh: Roh Awan" in out


def test_explore_menu_racik_option(session, capsys):
    session.state.location = "loc_asrama"
    session.state.inventory["material_herba"] = 2
    explore_menu(session)                         # opsi racik muncul
    assert "[racik]" in capsys.readouterr().out


def test_battle_view_with_companion(session, capsys):
    session.state.companion = {"id": "komp_roh_awan", "hp": 10, "active": True}
    session.battle.start([{"id": "eno_test", "name": "Musuh", "hp": 5, "qi": 0, "qi_max": 0,
                           "attack": 1, "defense": 0, "speed": 1, "element": None,
                           "exp_reward": 0, "drop_item": None, "drop_chance": 0}], "hunt")
    battle_view(session)                          # baris companion battle
    assert "otomatis" in capsys.readouterr().out


def test_cli_load_valid_save(monkeypatch, capsys, tmp_path, registry):
    monkeypatch.setattr("src.engine.session.SAVES_DIR", tmp_path)
    s = GameSession.new(registry)
    s.state.location = "loc_asrama"               # titik aman agar _save diizinkan
    s._save({"save_name": "valid"})
    assert (tmp_path / "valid.json").exists()
    monkeypatch.setattr("sys.argv", ["src/cli.py", "-l", "valid"])
    monkeypatch.setattr("builtins.input", lambda prompt="": (_ for _ in ()).throw(EOFError))

    from src.cli import main

    main()                                        # jalur memuat save sukses
    assert "Memuat save 'valid'..." in capsys.readouterr().out


def test_cli_boots_as_script():
    proc = subprocess.run([sys.executable, "src/cli.py"], input="",
                          capture_output=True, text=True, timeout=60, cwd=ROOT)
    assert proc.returncode == 0                   # main() via __main__ berjalan
    assert "TIAN XU: SECOND LIFE" in proc.stdout  # bootstrap sys.path (run as script)


def test_cli_choose_digit_and_spar_arg(monkeypatch, capsys):
    monkeypatch.setattr(BattleEngine, "_calc_damage", lambda self, a, d, ea, ed: (99999, False))
    monkeypatch.setattr(BattleEngine, "_enemy_turn", lambda self, pc, b: None)
    monkeypatch.setattr("src.engine.session.GameSession._is_npc_available", lambda self, npc: True)
    script = [
        "talk npc_penjaga", "1", "lanjut", "lanjut",
        "pindah loc_aula_ujian",
        "talk npc_gucanghai", "lanjut", "1", "lanjut", "lanjut", "lanjut",
        "pindah loc_arena",
        "talk npc_hanxiu", "lanjut", "lanjut",
        "serang",                    # menang spar ujian
        "1",                         # choose digit path → pilih akademi_elemen (232-234)
        "spar hanxiu",               # spar dengan argumen NPC (278)
        "serang",
        "keluar",
    ]
    inputs = iter(script)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    from src.cli import main

    main()
    out = capsys.readouterr().out
    assert "Paviliun Elemen" in out   # choose_view merender opsi
    assert out.count("Aksi:") >= 2   # dua battle: spar ujian + spar hanxiu
