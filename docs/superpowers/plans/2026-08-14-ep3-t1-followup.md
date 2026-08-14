# EP3-T1 Follow-up — Tutup Sisa Coverage & Hygiene Git

**Goal:** Menutup 18 baris uncovered yang tersisa (16 di `src/cli.py` + 2 di `src/engine/battle.py`) sehingga coverage `src/` 100%, menormalkan `.coverage` yang tertrack secara tak sengaja, tanpa mengubah perilaku game.

**Architecture:** Semua baris cli tersisa adalah jalur display/bootstrap — dicover via (a) direct-call renderer test tanpa RNG, (b) satu run terskrip pendek sampai quest `q_akademi_04` (satu-satunya objektif `choose`), (c) satu subprocess boot. Satu baris battle adalah kode mati terbukti → dihapus (keputusan user), satu lagi guard defensif → ditest langsung.

**Tech Stack:** Python 3.12 stdlib-only, pytest (dari root: `python3 -m pytest -q`), coverage (`--cov=src --cov-report=term-missing`).

## Global Constraints
- Semua teks/kode test berbahasa Indonesia; jalankan dari root repo `/home/dienk/tian-xu-second-life`.
- Determinisme: patch semua RNG; direct-call test tidak memakai RNG.
- `python3 tools/validate_data.py` wajib exit 0 setelah sentuh `data/` — plan ini TIDAK menyentuh `data/`.
- Tidak ada config lint; satu-satunya dev-dependency pytest.
- Perubahan `src/` hanya di Task 2 (hapus 2 baris kode mati). Seluruh sisanya test-only.
- Diterima sebagai risiko (bukan tugas): test playthrough rapuh terhadap edit urutan dialog (StopIteration), dan `test_teknik_defend` mem-pin `== 71` (pembulatan `round`). Keduanya perilaku yang sah saat ini.
- Commit per task. Verifikasi tiap task: `pytest -q` hijau + laporan coverage.

---

### Task 1: Normalisasi `.coverage` (git hygiene)

**Files:** `.gitignore`, index git (bukan kode).

- [ ] **Step 1:** Hapus `.coverage` dari tracking tanpa menghapus file lokal:
```bash
git rm --cached .coverage
```
- [ ] **Step 2:** Tambah `.coverage` ke `.gitignore` (setelah baris `saves/*.json`).
- [ ] **Step 3:** Verifikasi: `git status --short` → tidak ada `.coverage`; `git check-ignore .coverage` → keluar 0.
- [ ] **Step 4:** Commit:
```bash
git add .gitignore
git commit -m "chore: untrack .coverage, tambah ke .gitignore"
```

---

### Task 2: Hapus kode mati battle.py:164-165 + test guard companion_turn (battle.py:263)

**Files:**
- Modify: `src/engine/battle.py:163-166` (hapus cek 164-165)
- Test: `tests/test_battle.py` (append)

**Rasional (sudah diverifikasi):** `_all_dead` diperiksa di baris 159 *sebelum* `_enemy_turn`; `_enemy_turn` (232-254) hanya merusak player/companion; `_regen_foes` (272-275) hanya memulihkan qi musuh → cek `_all_dead` setelahnya (164-165) selalu False, unreachable.

- [ ] **Step 1: Tulis test dulu (RED untuk baris 263)**
```python
def test_companion_turn_no_alive_foe_is_noop(session):
    """Guard: tidak ada musuh hidup → _companion_turn tidak melakukan apa-apa."""
    session.state.companion = {"id": "komp_roh_awan", "hp": 10, "active": True}
    session.battle.start([{"id": "eno_test", "name": "Musuh", "hp": 0, "qi": 0, "qi_max": 0,
                           "attack": 1, "defense": 0, "speed": 1, "element": None,
                           "exp_reward": 0, "drop_item": None, "drop_chance": 0}], "hunt")
    session.battle._companion_turn(session.state.pending_battle)
    assert session.state.pending_battle["foes"][0]["hp"] == 0
```
- [ ] **Step 2:** Jalankan untuk lihat baris 263 tercover: `python3 -m pytest --cov=src --cov-report=term-missing tests/test_battle.py -q` → 263 tidak lagi di Missing.
- [ ] **Step 3: Hapus cek mati.** Edit `src/engine/battle.py:163-166` (baris 164-165 dihapus).
- [ ] **Step 4:** `python3 -m pytest -q` → semua hijau. `--cov=src` → battle.py 100%.
- [ ] **Step 5:** Commit:
```bash
git add src/engine/battle.py tests/test_battle.py
git commit -m "test+battle: hapus cek _all_dead redundan, test guard _companion_turn tanpa musuh"
```

---

### Task 3: Direct-call renderer test `src/cli.py` (baris 114, 149, 121-124, 63-64, 103, 141)

**Files:** `tests/test_cli.py` (append; pakai fixture `session` dari `conftest.py`)

- [ ] **Step 1: Tulis 6 test direct-call** (import tambahan: `from src.cli import print_header, dialog_view, battle_view, choose_view, explore_menu`):
```python
def test_dialog_view_without_dialog(session, capsys):
    dialog_view(session)
    assert capsys.readouterr().out == ""          # 114: tidak ada dialog → return

def test_choose_view_without_choose(session, capsys):
    choose_view(session)
    assert capsys.readouterr().out == ""          # 149: tidak ada choose → return

def test_dialog_view_speaker_variants(session, monkeypatch, capsys):
    monkeypatch.setattr(session, "view",
                        lambda: {"dialog": {"speaker": "system", "text": "pesan sistem", "choices": []}})
    dialog_view(session)                          # 121-122: speaker system
    monkeypatch.setattr(session, "view",
                        lambda: {"dialog": {"speaker": "player", "text": "kata pemain", "choices": []}})
    dialog_view(session)                          # 123-124: speaker lain → teks polos
    out = capsys.readouterr().out
    assert "pesan sistem" in out and "kata pemain" in out

def test_print_header_companion_ko(session, capsys):
    session.state.companion = {"id": "komp_roh_awan", "hp": 0, "active": True}
    print_header(session)                         # 63-64: status KO
    assert "KO — pulih di titik aman" in capsys.readouterr().out

def test_explore_menu_racik_option(session, capsys):
    session.state.location = "loc_asrama"
    session.state.player.inventory["material_herba"] = 2
    explore_menu(session)                         # 103: opsi racik muncul
    assert "[racik]" in capsys.readouterr().out

def test_battle_view_with_companion(session, capsys):
    session.state.companion = {"id": "komp_roh_awan", "hp": 10, "active": True}
    session.battle.start([{"id": "eno_test", "name": "Musuh", "hp": 5, "qi": 0, "qi_max": 0,
                           "attack": 1, "defense": 0, "speed": 1, "element": None,
                           "exp_reward": 0, "drop_item": None, "drop_chance": 0}], "hunt")
    battle_view(session)                          # 141: baris companion battle
    assert "otomatis" in capsys.readouterr().out
```
- [ ] **Step 2 (RED):** `python3 -m pytest --cov=src --cov-report=term-missing tests/test_cli.py -q` → baris 63-64, 103, 114, 121-124, 141, 149 hilang dari Missing cli.py.
- [ ] **Step 3 (GREEN):** `python3 -m pytest -q` hijau.
- [ ] **Step 4:** Commit:
```bash
git add tests/test_cli.py
git commit -m "test: direct-call renderer cli (header KO, racik, dialog/battle/choose view)"
```

---

### Task 4: `main()` `-l` dengan save valid (baris 163) + subprocess boot (baris 17 & 330)

**Files:** `tests/test_cli.py` (append; import tambahan `import subprocess, sys`)

- [ ] **Step 1: Tulis 2 test:**
```python
def test_cli_load_valid_save(monkeypatch, capsys, tmp_path, registry):
    monkeypatch.setattr("src.engine.session.SAVES_DIR", tmp_path)
    s = GameSession.new(registry)
    s.state.location = "loc_asrama"               # titik aman agar _save diizinkan
    s._save({"save_name": "valid"})
    assert (tmp_path / "valid.json").exists()
    monkeypatch.setattr("sys.argv", ["src/cli.py", "-l", "valid"])
    monkeypatch.setattr("builtins.input", lambda prompt="": (_ for _ in ()).throw(EOFError))
    from src.cli import main
    main()                                        # 163: "Memuat save 'valid'..."
    assert "Memuat save 'valid'..." in capsys.readouterr().out

def test_cli_boots_as_script():
    proc = subprocess.run([sys.executable, "src/cli.py"], input="",
                          capture_output=True, text=True, timeout=60, cwd=ROOT)
    assert proc.returncode == 0                   # 330: main() via __main__
    assert "TIAN XU: SECOND LIFE" in proc.stdout  # 17: bootstrap sys.path berjalan
```
- [ ] **Step 2 (RED):** laporan coverage cli.py → baris 17, 163, 330 tidak lagi di Missing.
- [ ] **Step 3 (GREEN):** `python3 -m pytest -q` hijau (test subprocess deterministik tanpa RNG).
- [ ] **Step 4:** Commit:
```bash
git add tests/test_cli.py
git commit -m "test: main -l save valid + boot subprocess python3 src/cli.py"
```

---

### Task 5: Run terskrip pendek — choose digit (233-235) & spar dengan argumen (279)

**Files:** `tests/test_cli.py` (append)

**Rasional:** `q_akademi_04` (quests_akademi.json:52) adalah satu-satunya objektif `kind: choose`. Run singkat sampai titik itu lalu jawab `"1"` (digit path); lalu `spar hanxiu` saat mode explore untuk baris 279.

- [ ] **Step 1: Tulis test:**
```python
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
        "1",                         # choose digit path → pilih akademi_elemen (233-235)
        "spar hanxiu",               # spar dengan argumen NPC (279)
        "serang",
        "keluar",
    ]
    inputs = iter(script)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    from src.cli import main
    main()
    out = capsys.readouterr().out
    assert "Akademi Elemen" in out   # choose_view merender opsi
    assert out.count("Aksi:") >= 2   # dua battle: spar ujian + spar hanxiu
```
- [ ] **Step 2 (RED):** coverage → baris 233-235 & 279 hilang dari Missing cli.py.
- [ ] **Step 3 (GREEN):** `python3 -m pytest -q` hijau.
- [ ] **Step 4:** Commit:
```bash
git add tests/test_cli.py
git commit -m "test: jalur digit choose (q_akademi_04) dan spar dengan argumen"
```

---

### Task 6: Verifikasi akhir

- [x] **Step 1:** `python3 -m pytest -q` → **192 passed**.
- [x] **Step 2:** `python3 -m pytest --cov=src --cov-report=term-missing -q` → cli.py & battle.py sisa **2 missed (cli.py 17, 329)** — keduanya hanya terjangkau via subprocess yang tak terukur coverage in-process; boot test subprocess tetap dipertahankan sebagai regresi.
- [x] **Step 3:** `python3 tools/validate_data.py` → exit 0.
- [x] **Step 4:** `git status --short` bersih (`.coverage` ignored).

---

## Catatan eksekusi (deviasi dari plan)

1. **Task 3 — status KO kompanion di `print_header` ternyata dead code**: `companion_stats` (battle.py) menjepit `hp 0 → hp_max` (`min(c.get("hp") or hp_max, hp_max)`), dan kompanion KO langsung di-revive di `session.py:366-373` → `print_header` tak pernah melihat `hp <= 0`. Cabang KO dihapus (konsisten dgn keputusan hapus-dead-code user). Test berubah jadi verifikasi baris "Roh:" aktif.
2. **Task 3 — atribut inventory**: ada di `GameState.inventory` (state.py:77), bukan `PlayerState`.
3. **Task 5 — bug produksi ditemukan**: help CLI (cli.py) mengiklankan `spar hanxiu`, tapi `_spar` lookup `reg.npc("hanxiu")` selalu gagal (id asli `npc_hanxiu`) → perintah manual `spar <id-pendek>` tak pernah jalan. Fix 1 baris: `reg.npc(nid) or reg.npc(f"npc_{nid}")`.
4. **Task 4 — subprocess tak terukur coverage**: `python3 src/cli.py` child berjalan tanpa instrumentasi pytest-cov; baris 17 & 329 tetap "uncovered" di laporan walau test hijau. Diterima (2/1532 = 99,9%).

