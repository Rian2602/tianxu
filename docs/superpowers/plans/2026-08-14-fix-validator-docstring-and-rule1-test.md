# Perbaikan — Docstring Validator & Test Aturan 1

> **Untuk agentic workers:** REQUIRED SUB-SKILL: `superpowers:executing-plans`. Steps pakai checkbox (`- [ ]`).

**Goal:** Menutup dua kelemahan hasil evaluasi — sinkronkan docstring validator dengan enforcement aturan 8, dan perkuat test aturan 1 agar menguji jalur parsing JSON asli.

**Architecture:** (1) edit satu baris docstring; (2) ganti body `test_aturan1_json_rusak` — salin `data/` nyata ke `tmp_path`, rusak `npcs.json`, lalu jalankan `Validator.validate()` lewat `read_json` sungguhan (monkeypatch `vd.DATA` ke tmp), sekaligus hapus `import json`, `import pytest`, dan blok `__main__` (satu-satunya file test yang memakainya).

**Tech Stack:** Python 3.12, stdlib-only (shutil, pathlib), pytest.

## Global Constraints

- Komentar/dokumen **Bahasa Indonesia**.
- Verifikasi tiap task: `python3 tools/validate_data.py` (exit 0) **dan** `python3 -m pytest -q`.
- Run dari root repo. Konvensi commit repo (`docs:`, `test:`).

---

### Task 1: Sinkronkan docstring validator dengan aturan 8

**Files:**
- Modify: `tools/validate_data.py:12`

- [x] **Step 1: Edit line 12** — dari `8. Side quest: repeatable/requires/available_from konsisten` menjadi `8. Side quest butuh available_from {day, hour}; cooldown valid jika ada`
- [ ] **Step 2: Verify** — `python3 tools/validate_data.py && python3 -m pytest -q` → hijau
- [ ] **Step 3: Commit** — `docs: sinkronkan docstring validator dengan aturan 8`

### Task 2: Perkuat `test_aturan1_json_rusak` — jalur parsing asli

**Files:**
- Modify: `tests/test_validator.py`

**Interfaces:**
- Consumes: `import tools.validate_data as vd` (`vd.ROOT`, `vd.DATA`, `vd.Validator`); fixture `tmp_path`, `monkeypatch`.

- [ ] **Step 1: Replace test** — ganti body `test_aturan1_json_rusak` dengan versi copytree; hapus `import json`, `import pytest`, dan blok `__main__` (pytest.main) — tak terpakai lagi dan tidak ada file test lain yang memakainya
- [ ] **Step 2: Run** — `python3 -m pytest tests/test_validator.py -q` → 19 pass
- [ ] **Step 3: Full verify** — `python3 tools/validate_data.py && python3 -m pytest -q` → hijau
- [ ] **Step 4: Commit** — `test: aturan 1 menguji file JSON rusak nyata`
