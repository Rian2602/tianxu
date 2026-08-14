# Perbaikan Temuan Evaluasi Diri — Implementation Plan

> **Untuk agentic workers:** REQUIRED SUB-SKILL: Gunakan `superpowers:subagent-driven-development` (disarankan) atau `superpowers:executing-plans` untuk implementasi task-by-task. Steps pakai checkbox (`- [ ]`).
>
> **Sumber temuan**: evaluasi diri atas eksekusi `docs/superpowers/plans/2026-08-14-fix-sisa-bug-dan-hardening.md` (indikator 3: bug baru yang diperkenalkan sendiri). Dua temuan nyata + satu verifikasi latent.

**Goal:** Memperbaiki 2 temuan yang diperkenalkan batch sebelumnya (regresi konten `node_kalah`; dok drift angka test 207 vs 209) dan memverifikasi batas eksklusif jadwal NPC (A1) tidak menyentuh data nyata.

**Architecture:** Task A = ubah `node_kalah` dari `end: true` menjadi `next: "node_umum"` (dialog nasihat Gu Canghai tetap terjangkau setelah konsolasi kalah) + perkuat test spar_kalah. Task B = koreksi angka test di docs (207 → **209**) + grep verifikasi konsistensi. Task C = verifikasi statis data jadwal NPC (tidak ada `hour_start == hour_end` / jadwal yang tersentuh batas) — tanpa perubahan kode.

**Tech Stack:** Python 3.12, stdlib-only, pytest. Tidak ada lint/typecheck.

## Global Constraints

- Semua komentar, dokumen, dan teks test **Bahasa Indonesia**; istilah teknis ber-pinyin/hanzi.
- Wajib lolos setelah setiap task: `python3 tools/validate_data.py` (exit 0) **dan** `python3 -m pytest -q`. Urutan baku CI: validate → pytest.
- Run dari root repo. Tidak menambah dependency.
- Konvensi commit repo: `fix:`, `test:`, `docs:`.
- Kali ini commit **per task** benar-benar bisa (file tiap task tidak tumpang-tindih: Task A = dialog+test_quest_dag, Task B = docs, Task C = tanpa file).

---

### Task A: Perbaiki regresi konten `node_kalah` (temuan b)

> Temuan: `node_kalah` di `dlg_gucanghai_ujian` ber-`end: true` — setelah kalah sparring ujian, flag `spar_kalah` menang permanen di `_resolve_entry` → dialog normal Gu Canghai (`node_umum` nasihat) tidak pernah tampil lagi untuk playthrough itu.

**Files:**
- Modify: `data/dialogs/dialogs_akademi.json` — `node_kalah`: `"end": true` → `"next": "node_umum"` (konsolasi dulu, lalu dialog biasa tetap tersedia)
- Modify: `tests/test_quest_dag.py` — perkuat `test_spar_kalah_tetap_selesai_dan_dialog_beda`: setelah melihat teks `node_kalah`, `finish_dialog(s, [])` → bicara Gu Canghai lagi → dialog `node_umum` (nasihat) tampil

**Interfaces:**
- Consumes: `dlg_gucanghai_ujian` nodes `node_kalah`/`node_umum`; alur `test_spar_kalah_tetap_selesai_dan_dialog_beda` (sudah ada).

> **Catatan koreksi (evaluasi plan)**: jangan bicara Gu Canghai *lagi* — `_resolve_entry` selalu memilih `node_kalah` (flag `spar_kalah` menetap), jadi bicara kedua tetap membuka node_kalah. Assert `node_umum` dilakukan **dalam sesi dialog yang sama**, setelah satu langkah lanjut dari node_kalah.

- [ ] **Step 1: Tulis failing test** — lanjut dari test spar_kalah: setelah teks `node_kalah` tampil, `s.apply_action({"type": "dialog_choice", "choice_index": -1})` (lanjut satu node) → teks view berisi "Kultivasi itu seperti laut" (node_umum, dengan pilihan nasihat). Saat ini (node_kalah `end: true`) advance justru menutup dialog → view mode explore → assert gagal
- [ ] **Step 2: Run** `python3 -m pytest tests/test_quest_dag.py -q -k "spar_kalah"` — verifikasi gagal
- [ ] **Step 3: Edit data** — `node_kalah` → `next: "node_umum"`
- [ ] **Step 4: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 5: Commit** `fix+story: dialog Gu Canghai tetap terbuka setelah konsolasi kalah (regresi G4a)`

### Task B: Koreksi angka test di docs (temuan a)

> Temuan: `docs/list_bug.md:19,45` dan `docs/DESIGN_SUMMARY.md:114` menulis **207 passed**, aktual **209** (ditulis sebelum Fase B selesai, tidak direvisi). Plan file sudah benar (209).

**Files:**
- Modify: `docs/list_bug.md` — "**207 passed**" → "**209 passed**" (baris 19); "— 207 test total:" → "— 209 test total:" (baris 45)
- Modify: `docs/DESIGN_SUMMARY.md` — "→ **207 test**" → "→ **209 test**" (baris 114)

- [ ] **Step 1: Grep verifikasi** — `rg -n "207|209" docs/` → pastikan hanya 207 yang tersisa adalah yang tidak relevan (mis. nomor baris di kutipan)
- [ ] **Step 2: Edit docs** — 207 → 209 di kedua file
- [ ] **Step 3: Verifikasi angka aktual** — `python3 -m pytest -q 2>&1 | tail -1` → konfirmasi 209
- [ ] **Step 4: Commit** `docs: koreksi jumlah test (209) di list_bug & DESIGN_SUMMARY`

### Task C: Verifikasi batas jadwal NPC (A1, latent) — tanpa perubahan kode

> Konteks: fix A1 mengubah batas `hour_end` menjadi eksklusif (`start <= h < end`, pola `quest._in_window`). Perlu dipastikan tidak ada jadwal di data yang menyentuh batas (mis. NPC aktif sampai jam `hour_end` itu sendiri diandalkan alur mana pun).

**Files:**
- Baca saja: `data/npcs.json` (semua `schedule`), `tests/test_session.py::test_jadwal_npc_lintas_tengah_malam`

- [ ] **Step 1: Audit data** — untuk tiap schedule NPC: `hour_start < hour_end`? tidak ada `hour_end == 24` yang diandalkan? tidak ada alur quest/NPC yang bergantung pada bicara tepat di jam `hour_end`?
- [ ] **Step 2: Dokumentasikan hasil** — tambah satu baris di `docs/ENGINE_ARCHITECTURE.md` §17 catatan A1: "diverifikasi 2026-08-14: tidak ada schedule data yang menyentuh batas hour_end — perubahan eksklusif tak berdampak playthrough saat ini"
- [ ] **Step 3: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 4: Commit** `docs: verifikasi batas eksklusif jadwal NPC (A1)`

---

## Urutan eksekusi

1. **Task A** (fix konten + test) → 2. **Task B** (koreksi docs) → 3. **Task C** (verifikasi + catatan docs).
Tidak ada dependensi antar task; urutan bebas, tapi Task A paling penting (dampak gameplay).

**Kriteria selesai:** `validate_data.py` exit 0 + `pytest` 209 passed; `node_kalah` tidak menyembunyikan dialog normal Gu Canghai; tidak ada sisa "207" yang keliru di docs; catatan verifikasi A1 tercatat.
