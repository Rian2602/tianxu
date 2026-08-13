# Fix — Save Rusak Ditolak dengan Pesan Jelas

> **Untuk agentic workers:** REQUIRED SUB-SKILL: `superpowers:executing-plans`. Steps pakai checkbox (`- [ ]`).

**Goal:** Save JSON korup/format salah → `SaveError` dengan pesan jelas, bukan crash — menutup gap kontrak §13 ENGINE_ARCHITECTURE ("reject save rusak → pesan jelas, bukan crash") yang belum diimplementasi.

**Architecture:** Root-cause di fungsi bersama `GameSession.load` (`src/engine/session.py:64-68`) — saat ini `open` + `json.load` + `GameState.from_dict` tanpa guard; caller `cli.py:164` & `web/app.py:145` hanya tangkap `FileNotFoundError`. Fix: definisikan `SaveError`, bungkus `json.load` dan `from_dict`, caller tangkap. `FileNotFoundError` tetap propagasi (caller bergantung padanya).

**Tech Stack:** Python 3.12, stdlib-only, pytest.

## Global Constraints

- Komentar/dokumen **Bahasa Indonesia**.
- Verifikasi tiap task: `python3 tools/validate_data.py` (exit 0) **dan** `python3 -m pytest -q`.
- Run dari root repo. Konvensi commit repo (`test:`, `fix:`). Commit per task.

---

### Task 1: Test penolakan save rusak (TDD)

**Files:**
- Modify: `tests/test_session.py`

**Interfaces:**
- Consumes: fixtures `tmp_path`, `monkeypatch`, `registry`; `import src.engine.session as m`; `pytest.raises`.

- [x] **Step 1: Tulis test** (TDD — harus GAGAL sebelum fix):
  - `test_load_save_rusak_menolak`: `monkeypatch.setattr(m, "SAVES_DIR", tmp_path)`; tulis `save1.json` = `{rusak`; `with pytest.raises(m.SaveError)` di `m.GameSession.load(registry, "save1")`
  - `test_load_save_format_salah_menolak`: tulis `'{"player": 1}'`; `with pytest.raises(m.SaveError)`
- [ ] **Step 2: Verify merah** — `python3 -m pytest tests/test_session.py -q` → 2 gagal (SaveError belum ada)
- [ ] **Step 3: Commit** — `test: load menolak save rusak tanpa crash`

### Task 2: Fix root-cause + caller

**Files:**
- Modify: `src/engine/session.py`, `src/cli.py`, `web/app.py`

**Interfaces:**
- New: `class SaveError(Exception)` di `src/engine/session.py`; `except SaveError` di `cli.py` & `web/app.py`.

- [ ] **Step 1: `session.py`** — tambah `SaveError`; di `GameSession.load`:
  - `try: open+json.load` → `except (OSError, json.JSONDecodeError)` → `raise SaveError(f"save '{save_name}' rusak: {e}") from e`; `except FileNotFoundError: raise`
  - `try: from_dict` → `except (KeyError, TypeError, ValueError)` → `raise SaveError(f"save '{save_name}' format tidak dikenal") from e`
- [ ] **Step 2: `cli.py`** — setelah `except FileNotFoundError`: `except SaveError as e: print(f"Gagal memuat save '{save_name}': {e}"); return` (JANGAN fallback ke game baru — risiko data loss)
- [ ] **Step 3: `web/app.py`** — import `SaveError` (satu baris import yang sudah ada); tambah `except SaveError as e: self._send_json({"ok": False, "error": f"Save '{name}' rusak: {e}"}, 400)` di `/api/load`
- [ ] **Step 4: Verify hijau** — `python3 -m pytest tests/test_session.py -q` → 17 pass; `python3 tools/validate_data.py && python3 -m pytest -q` → semua hijau
- [ ] **Step 5: Commit** — `fix: save rusak ditolak dengan pesan jelas (bukan crash)`

### Catatan keputusan
- Test web `/api/load` korup **dilewati** (ponytail) — engine test adalah jaring utama; perubahan handler hanya 2 baris.
- CHANGELOG dilewati — tidak ada section "Unreleased".
