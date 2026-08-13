# Tutup Gap Test §14 & Sinkronisasi Docs — Implementation Plan

> **Untuk agentic workers:** REQUIRED SUB-SKILL: Gunakan `superpowers:subagent-driven-development` (disarankan) atau `superpowers:executing-plans` untuk implementasi task-by-task. Steps pakai checkbox (`- [ ]`).

**Goal:** Menutup gap test yang diwajibkan §15 ENGINE_ARCHITECTURE (validator 16 aturan + kultivasi) dan menyinkronkan dokumen dengan kode nyata.

**Architecture:** Test validator memakai monkeypatch metode baca pada `Validator` (inject data rusak per-aturan); test kultivasi memakai fixture `session` yang ada; enforcement aturan 8 ditambahkan ke `_check_quests`; docs §3/§13/§14/§15/§16 dikoreksi.

**Tech Stack:** Python 3.12, stdlib-only, pytest. Tidak ada lint/typecheck.

## Global Constraints

- Semua komentar, dokumen, dan teks test **Bahasa Indonesia**; istilah teknis ber-pinyin/hanzi.
- Wajib lolos setelah setiap task: `python3 tools/validate_data.py` (exit 0) **dan** `python3 -m pytest -q`.
- Run dari root repo.
- Tidak menambah dependency; jangan menyentuh `src/engine/` kecuali validator (`tools/`).
- Konvensi commit repo: `feat:`, `test:`, `fix:`, `docs:`, `ci:`, `chore:`.

---

### Task 1: `tests/test_validator.py` — cakupan 16 aturan §14 (+ enforcement aturan 8)

**Files:**
- Modify: `tools/validate_data.py` (enforce aturan 8 di `_check_quests`)
- Create: `tests/test_validator.py`

**Interfaces:**
- Consumes: `from tools.validate_data import Validator`; `v.validate() -> bool`, `v.errors: list[str]`, `v.read_json(rel)`, `v.read_csv_rows(rel)` (keduanya di-monkeypatch).
- Produces: dataset minimal yang lolos semua aturan + helper `make(data)`.

- [ ] **Step 1: Write failing tests** — `tests/test_validator.py`
- [ ] **Step 2: Run** `python3 -m pytest tests/test_validator.py -q` — verifikasi gagal (aturan 8 belum enforce)
- [ ] **Step 3: Enforce aturan 8** di `tools/validate_data.py::_check_quests`
- [ ] **Step 4: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 5: Commit** `test: cakupan aturan validasi §14 + enforce aturan 8`

### Task 2: `tests/test_cultivation.py` — multiplier akar & breakthrough

**Files:**
- Create: `tests/test_cultivation.py`

**Interfaces:**
- Consumes: `from src.engine.cultivation import gain_exp`; fixture `session` (conftest).

- [ ] **Step 1: Write tests** — multiplier akar, breakthrough level 10, cap ranah tertinggi
- [ ] **Step 2: Run** `python3 -m pytest tests/test_cultivation.py -v` — PASS
- [ ] **Step 3: Commit** `test: progresi kultivasi (multiplier akar, breakthrough)`

### Task 3: Sinkronisasi `docs/ENGINE_ARCHITECTURE.md` dengan kode

**Files:**
- Modify: `docs/ENGINE_ARCHITECTURE.md`

- [ ] **Step 1: §3 diagram** — `(Flask + API)` → `(http.server stdlib + API)`
- [ ] **Step 2: §13** — `src/engine/save.py` → `state.py`/`session.py`
- [ ] **Step 3: §14 rule 8** — perbarui contoh pesan error
- [ ] **Step 4: §15 matrix** — nama file test → yang nyata
- [ ] **Step 5: §16** — `src/validator.py` → `tools/validate_data.py`; tandai step 1–11 selesai
- [ ] **Step 6: Verifikasi** `python3 tools/validate_data.py && python3 -m pytest -q`
- [ ] **Step 7: Commit** `docs: sinkronkan ENGINE_ARCHITECTURE dengan implementasi`
