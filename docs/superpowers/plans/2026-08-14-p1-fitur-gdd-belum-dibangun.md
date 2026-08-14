# Fitur GDD Belum Dibangun — Implementation Plan (P1)

> **Untuk agentic workers:** REQUIRED SUB-SKILL: Gunakan `superpowers:subagent-driven-development` (disarankan) atau `superpowers:executing-plans` untuk implementasi task-by-task. Steps pakai checkbox (`- [ ]`).
>
> **Sumber**: rekomendasi fitur belum dibangun per GDD.md (2026-08-14) — P1 = melengkapi cakupan Fase 1.
>
> **STATUS EKSEKUSI (2026-08-14)**: ✅ **SELESAI** — P1-2 (relations berdampak), P1-1 (gating ingatan = B3/#13), P1-3 (musuh malam). Verifikasi akhir: `validate_data.py` exit 0 + `pytest` **222 passed**. Commit: lihat riwayat git (3 commit per task).
>
> **Deviasi konten (tercatat saat eksekusi)**: P1-2 semula merencanakan node gated Su Qing/Zhou Yan — saat eksekusi terverifikasi bahwa `relations` Su Qing/Zhou Yan **tak punya sumber yang bisa tumbuh** (hanya on_complete ±5; tak bisa di-spar), sehingga node gated mereka tak akan terjangkau atau menaungi node lama. Diganti 2 node gated dari mekanik yang baru ditambahkan: **Han Xiu** `node_tip_spar` (rel ≥ 20) & **Gu Canghai** `node_akui_latihan` (rel ≥ 20) — keduanya tercapai lewat sparring berulang (`spar_win_relation` 5). P1-1 & P1-3 sesuai rencana; `night_window` memakai skema `hour_start`/`hour_end` (konsisten `quest._in_window`).

**Goal:** Menutup 3 gap GDD dalam cakupan Fase 1 (Arc Akademi): (P1-1) gating ingatan → opsi dialog (B3/#13, satu-satunya defer resmi), (P1-2) hubungan NPC (`relations`) benar-benar memengaruhi dialog, (P1-3) tipe musuh beragam (pembelot malam + pool malam data-driven). Tanpa mengubah arsitektur — pola engine yang sudah ada diperluas.

**Architecture:** Ketiga task menyentuh titik yang sama (`dialog.py::_eval_condition` + validator `_check_dialogs`), jadi dikerjakan **berurutan**, satu commit per task (file disjoint antar task). Urutan: P1-2 (paling kecil, murni konsumsi data yang sudah ada) → P1-1 (kondisi baru + konten naratif) → P1-3 (data musuh + config + session). Setiap perubahan skema data disertai pembaruan validator (aturan AGENTS.md).

**Tech Stack:** Python 3.12, stdlib-only, pytest. Tidak ada lint/typecheck.

## Global Constraints

- Semua komentar, dokumen, dan teks test **Bahasa Indonesia**; istilah teknis ber-pinyin/hanzi.
- Wajib lolos setelah setiap task: `python3 tools/validate_data.py` (exit 0) **dan** `python3 -m pytest -q`. Urutan baku CI: validate → pytest.
- Run dari root repo. Tidak menambah dependency.
- Konvensi commit repo: `feat:`, `fix:`, `test:`, `docs:`.
- Pola TDD: tulis failing test → verifikasi gagal → implementasi → hijau.
- Skema kondisi dialog baru WAJIB divalidasi validator (`_check_dialogs`) — aturan AGENTS.md (ubah skema = ubah validator).

---

### Task P1-2: Hubungan NPC berdampak pada dialog (GDD §7, §4.4)

> Kondisi sekarang: `state.relations` diisi efek (`effects.py:23`, tipe efek `relation`) tapi **tidak pernah dibaca** — tidak ada satu pun kondisi dialog berbasis relation. "Konsekuensi nyata" (GDD §4.4) belum terasa di layer hubungan.

**Files:**
- Modify: `src/engine/dialog.py::_eval_condition` — tambah tipe kondisi `relation_min` / `relation_max`
- Modify: `tools/validate_data.py::_check_dialogs` — validasi referensi npc pada kondisi relation
- Modify: `data/dialogs/dialogs_akademi.json` — 2–3 node gated relation (default di bawah)
- Modify: `src/engine/battle.py::_victory` (cabang spar) — tambah efek `relation` saat spar menang (belum ada; hanya `spar_win_exp`)
- Modify: `data/config.json` — `cultivation.spar_win_relation` (default 5, sejajar `spar_win_exp`)
- Modify: `tests/test_dialog.py` — test kondisi relation (TDD)
- Modify: `docs/ENGINE_ARCHITECTURE.md` (daftar tipe kondisi dialog) + `docs/list_bug.md` (catatan fitur) + `PROJECT.md` (baris matriks baru)

**Interfaces:**
- Schema kondisi (konsisten pola `morality_min` + butuh 2 nilai): `{ "relation_min": { "npc": "npc_suqing", "value": 15 } }` — true bila `state.relations.get(npc, 0) >= value`. `relation_max` kebalikannya. Nilai default relations = 0.
- Produces: kondisi baru dipakai node dialog; efek `relation` sudah ada di `effects.py` (tidak diubah).

> **Keputusan default konten** (bisa diganti saat eksekusi): efek hubungan datang dari (a) spar menang — `cultivation.spar_win_relation` (default 5, disuntikkan di `_victory` cabang spar setelah `notify_spar_won`), dan (b) on_complete quest yang **sudah ada** (terverifikasi 5 entri: `npc_hanxiu`/`npc_suqing` +5, `npc_moyun` +5, `npc_suqing` −5/−3) — **jangan duplikasi**. Node gated dibuat **baru** (jangan re-gate node lama agar konten existing tidak hilang): `dlg_hanxiu` `node_tip_spar` syarat `relation >= 20` (Han Xiu berbagi tip sparring), `dlg_suqing` `node_hangat_kuat` syarat `relation >= 15`, `dlg_zhouyan` `node_bersyukur_kuat` syarat `relation >= 10`.

> **Catatan evaluasi (2026-08-14)**: kondisi boleh dipasang di **choice** (`_visible_choices` menyaring `ch.condition`) — bukan hanya node. Untuk gating opsi (P1-1 & P1-2), taruh `condition` di pilihan; kombinasi beberapa kunci dalam satu dict = AND (pola `_eval_condition`).

- [ ] **Step 0: Verifikasi mekanik relation saat ini** — sudah terverifikasi saat evaluasi plan: on_complete quest memuat 5 efek relation (jangan duplikasi); spar menang **belum** memberi relation (hanya exp). Titik suntik: `battle.py::_victory` cabang `context == "spar"` setelah `notify_spar_won`
- [ ] **Step 1: Tulis failing test** — `test_dialog.py`: choice dengan kondisi `relation_min` tersembunyi saat `relations` kosong / di bawah ambang; tampil setelah `state.relations[npc]` di-set (simulasi spar menang / on_complete quest)
- [ ] **Step 2: Run** `python3 -m pytest tests/test_dialog.py -q -k "relation"` — verifikasi gagal
- [ ] **Step 3: Implementasi engine** — `dialog.py::_eval_condition` (relation_min/relation_max) + verifikasi/tambah efek relation spar menang
- [ ] **Step 4: Update validator** — `_check_dialogs`: `relation_min/max.npc` harus ada di npcs
- [ ] **Step 5: Data** — config `cultivation.spar_win_relation` + `battle.py::_victory` (efek relation spar menang) + 3 node gated BARU di dialog (default di atas; jangan sentuh on_complete yang sudah ada)
- [ ] **Step 6: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 7: Docs** — ENGINE_ARCHITECTURE (tipe kondisi), PROJECT.md (baris fitur), CHANGELOG
- [x] **Step 8: Commit** `feat: hubungan NPC memengaruhi dialog (relation_min/max) — GDD §7`

### Task P1-1: Gating ingatan → opsi dialog (GDD §3.1, B3/#13)

> Kondisi sekarang: 4 ingatan murni naratif (`memory.py` + `data/memories.json`); tidak ada dialog yang membaca `state.memories`. Arc 1 = "arc pengumpulan ingatan" tapi ingatan tak membuka opsi apa pun. Ini B3/#13 — defer resmi di `list_bug.md`.

**Files:**
- Modify: `src/engine/dialog.py::_eval_condition` — tambah tipe kondisi `memory`
- Modify: `tools/validate_data.py::_check_dialogs` — validasi referensi id ingatan pada kondisi `memory` (cek di **node maupun choice**; saat ini kondisi tidak divalidasi sama sekali — cukup tipe baru, jangan rombak validasi kondisi lama)
- Modify: `data/dialogs/dialogs_akademi.json` — 2 pilihan dialog gated ingatan (default di bawah)
- Modify: `tests/test_dialog.py` — test kondisi memory (TDD)
- Modify: `docs/STORY_FASE1.md` §3.1 (tandai terimplementasi) + `docs/ENGINE_ARCHITECTURE.md` + `docs/list_bug.md` (B3/#13 ✅) + `PROJECT.md`

**Interfaces:**
- Schema: `{ "memory": "mem_02" }` (flat, konsisten mayoritas kondisi) — true bila `"mem_02" in state.memories`.
- Produces: opsi dialog muncul hanya setelah ingatan terkait pulih (STORY_FASE1 §3.1).

> **Keputusan default konten**: (a) `dlg_moyun` q07 — pilihan gated `mem_02` ("Kebaikan yang Terlupakan", asal Tianyuan Ling): Chen Xu menyadari kemiripan benda hangat → Mo Yun merespons lebih dalam; (b) `dlg_gucanghai` node_umum — pilihan gated `mem_01` ("Istana yang Sunyi"): Gu Canghai membaca duka tua di mata murid baru. Dua titik cukup untuk membuktikan mekanik + bisa diuji.

- [ ] **Step 1: Tulis failing test** — `test_dialog.py`: opsi dengan kondisi `memory: mem_02` tidak tampil sebelum unlock; tampil setelah `state.memories` berisi `mem_02`
- [ ] **Step 2: Run** `python3 -m pytest tests/test_dialog.py -q -k "memory"` — verifikasi gagal
- [ ] **Step 3: Implementasi engine** — `dialog.py::_eval_condition` (tipe `memory`)
- [ ] **Step 4: Update validator** — `_check_dialogs`: `condition.memory` harus ada di memories.json
- [ ] **Step 5: Data** — 2 pilihan gated di `dlg_moyun` & `dlg_gucanghai` (default di atas)
- [ ] **Step 6: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 7: Docs** — STORY_FASE1 §3.1 "diimplementasikan 2026-08-14", ENGINE_ARCHITECTURE (daftar tipe kondisi + catatan B3), list_bug B3/#13 → ✅ (hapus dari defer), PROJECT.md baris matriks
- [x] **Step 8: Commit** `feat: ingatan membuka opsi dialog (kondisi memory) — GDD §3.1, B3/#13`

### Task P1-3: Tipe musuh beragam + pool malam (GDD §8)

> Kondisi sekarang: hanya 3 musuh (`eno_serigala_qi`, `eno_babi_hutan`, mini-boss `eno_raja_serigala`), semua di pool siang `world.hunt.pool`. GDD §8 menyebut "liar, pembelot, penjaga, boss naratif".

**Files:**
- Modify: `data/enemies.csv` — +2 musuh (default: `eno_pembelot_malam` = Pembelot Malam 夜叛, realm lebih tinggi dari pool siang, drop `material_tulang`/`material_herba`; `eno_ular_hutan` = Ular Bayangan 影蛇, cepat, drop herba)
- Modify: `data/config.json` — `world.hunt` + field `night_pool` (daftar id musuh) + `night_window` (`{"start": 19, "end": 6}` — pola quest `_in_window` lintas tengah malam)
- Modify: `src/engine/session.py::_hunt` — pilih pool berdasarkan jam (siang/malam) dengan pola `_in_window`, **sebelum** logika swap mini-boss
- Modify: `tools/validate_data.py` aturan 7 — validasi `night_pool` referensi musuh + `night_window` sanitasinya
- Modify: `tests/test_validator.py` (aturan 7 night_pool) + `tests/test_session.py` (berburu malam memakai pool malam)
- Modify: `docs/ENGINE_ARCHITECTURE.md` §5.6/§17 + `docs/list_bug.md` + `PROJECT.md`

**Interfaces:**
- Produces: `_hunt` membaca `world.hunt.night_pool` saat jam dalam `night_window`; `world.hunt` lama tetap berfungsi bila field baru absen (fallback = pool siang — non-breaking, konsisten A2).

- [ ] **Step 1: Tulis failing test** — `test_session.py`: jam 21 (malam) → `_hunt` memilih musuh dari `night_pool` (mock `random`); jam 10 → pool siang. `test_validator.py`: `night_pool` referensi tak ada → error
- [ ] **Step 2: Run** `python3 -m pytest tests/test_session.py tests/test_validator.py -q -k "malam or night"` — verifikasi gagal
- [ ] **Step 3: Data** — 2 musuh baru di enemies.csv (validasi aturan referensi item drop lulus) + `  night_pool`/`night_window` di config
- [ ] **Step 4: Implementasi engine** — `_hunt`: ganti `pool = list(hunt.get("pool", ...))` dengan seleksi per jam (jam dalam `night_window` → `night_pool`, fallback pool siang), lalu lanjut logika mini-boss & `random.choice` seperti sekarang
- [ ] **Step 5: Update validator** — aturan 7: `night_pool` tiap id ada di enemies.csv; `night_window.start/end` int 0–23 (start boleh > end = lintas tengah malam)
- [ ] **Step 6: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 7: Docs** — ENGINE_ARCHITECTURE §5.6 (skema world.hunt), §17; list_bug (A2-sisa tertutup); PROJECT.md baris matriks
- [x] **Step 8: Commit** `feat: tipe musuh beragam + pool berburu malam (GDD §8)`

---

## Kriteria Selesai

- [ ] `python3 tools/validate_data.py` exit 0 + `python3 -m pytest -q` hijau setelah setiap task (total test bertambah ≥ 3: relation, memory, night-pool)
- [ ] P1-2: spar menang menaikkan relation; minimal 3 node dialog gated relation teruji (hidden → tampil)
- [ ] P1-1: opsi gated `mem_02` di `dlg_moyun` & `mem_01` di `dlg_gucanghai` teruji (tersembunyi sebelum unlock); `list_bug.md` B3/#13 → ✅, tak ada lagi defer tersisa
- [ ] P1-3: berburu malam (jam 19–6) memakai pool malam; validator menolak `night_pool` referensi rusak
- [ ] Docs sinkron: ENGINE_ARCHITECTURE (tipe kondisi dialog + skema world.hunt), STORY_FASE1 §3.1, list_bug, PROJECT.md (3 baris fitur baru), CHANGELOG
- [ ] Verifikasi manual singkat: playthrough CLI/web — berburu malam bertemu pembelot, dialog Mo Yun/Gu Canghai berubah setelah ingatan pulih, spar berulang mengubah reaksi Han Xiu
