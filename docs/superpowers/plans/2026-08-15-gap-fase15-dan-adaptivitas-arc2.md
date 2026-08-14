# Gap Fase 1.5 + Adaptivitas Arc 2 — Implementation Plan (Revisi Prioritas)

> **Untuk agentic workers:** REQUIRED SUB-SKILL: Gunakan `superpowers:subagent-driven-development` (disarankan) atau `superpowers:executing-plans` untuk implementasi task-by-task. Steps pakai checkbox (`- [ ]`).
>
> **Sumber**: Evaluasi status Fase 1.5 (2026-08-15, verifikasi langsung vs kode) + audit adaptivitas (grep hardcode arc-1 di `src/`) + **evaluasi plan (2026-08-15, skala prioritas urgensi)**. Keputusan user: **sebelum menulis story arc berikutnya, selesaikan sisa gap Fase 1.5 DAN pastikan engine adaptif — arc baru = data saja, tanpa mengubah arsitektur/codebase.** Commit dasar: `9ef0a94` (Fase 1.5 foundation freeze) · `3f08c32` (kompresi aset) — ter-push.
>
> **Revisi v2 (2026-08-15) — hasil evaluasi urgensi/efisiensi:**
> - Urutan dikerjakan ulang jadi **3 gelombang prioritas**: G1 = prasyarat arc 2 (playtest → transisi → bukti → freeze), G2 = micro-task adaptivitas (B1+A1 digabung), G3 = task spekulatif **ditunda ke pipeline desain cerita** (A2 quest-failure menunggu outline arc 2; A3 onboarding = audit).
> - **A2 (quest failure) TIDAK dikerjakan sekarang** — membangun mekanik tanpa konsumen = risiko salah desain yang justru memaksa ubah engine saat arc 2. Dipindah: *outline cerita arc 2 → identifikasi mekanik yang dibutuhkan → bangun & validasi → isi konten*.
> - Keputusan desain terbuka yang HARUS diselesaikan di G1-T2 (sebelum menulis konten arc 2): hunt multi-lokasi, gating quest by relation, scoping memory per arc.
>
> **STATUS EKSEKUSI (2026-08-15)**: 🔲 belum dimulai.

**Goal:** Menutup gap Fase 1.5 + menutup lubang adaptivitas dengan **urutan yang mengutamakan dampak dan menghindari kerja spekulatif**, sehingga arc berikutnya cukup menulis data:

- **G1 (P0 — prasyarat arc 2)**: playtest 4 cabang → kontrak transisi arc → bukti adaptif → freeze.
- **G2 (P1 — micro-task)**: hilangkan hardcode `loc_wilayah_berburu` + auto-equip starter kit (satu batch).
- **G3 (P2 — tergantung desain cerita)**: quest failure/deadline (menunggu outline arc 2) + onboarding audit.

**Architecture:** Semua perubahan mengikuti pola data-driven yang sudah mapan — engine hanya menambah **mekanik umum** (arc-summary generik, auto-equip), konten tetap data. Setiap perubahan skema data disertai pembaruan validator. Non-breaking: kontrak `view()` lama utuh, save lama tetap dimuat, playthrough arc 1 identik.

**Tech Stack:** Python 3.12, stdlib-only, pytest. Tidak ada lint/typecheck.

## Global Constraints

- Semua komentar, dokumen, dan teks test **Bahasa Indonesia**; istilah teknis ber-pinyin/hanzi.
- Wajib lolos setelah setiap task: `python3 tools/validate_data.py` (exit 0) **dan** `python3 -m pytest -q`. Urutan baku CI: validate → pytest.
- Run dari root repo. Tidak menambah dependency runtime.
- Konvensi commit repo: `feat:`, `test:`, `docs:`, `fix+test:`.
- Pola TDD untuk perubahan perilaku: tulis failing test dulu → verifikasi gagal → implementasi → hijau.
- Setiap perubahan skema data WAJIB disertai pembaruan validator.
- **Non-breaking**: playthrough CLI 3 akademi (`tests/test_cli.py`) tetap hijau.

---

# GELOMBANG 1 — P0: Prasyarat Arc 2 (wajib sebelum menulis konten arc 2)

Urutan kerja G1 sengaja: **playtest dulu** (temukan & perbaiki bug alur pada fondasi yang ada) → **kontrak transisi** (pintu masuk arc 2 + keputusan desain) → **bukti adaptif** (regression guard) → **freeze** (deklarasi resmi).

### G1-T1: Playtest 4 cabang moral + perbaikan (jaring kualitas)

> Kondisi sekarang: playthrough CLI otomatis (15) mencakup jalur utama, belum per-cabang dengan verifikasi world-state akhir. Playtest SEBELUM membangun apa pun — kalau ada bug alur, diperbaiki dulu di atas fondasi yang bersih.

**Files:**
- Add: `tests/test_playthrough_branches.py` — untuk tiap cabang (3aa, 3ab, 3b, 3c): playthrough dari awal (helper `play_to_incident`) → pilih cabang → selesaikan sampai `q_akademi_07` → assertion world-state akhir: `arc_akademi_selesai`, `bell_status=kembali`, flag cabang, relations (Zhou Yan/Su Qing/Mo Yun/Penatua sesuai cabang), morality akhir sesuai jalur, memory ter-unlock, `arc_summary` benar.
- Bila assertion mengungkap bug alur → task perbaikan terpisah (`fix+test:`) dalam gelombang ini, SEBELUM lanjut G1-T2.

**Interfaces:**
- Consumes: `tests/conftest.py` helper (`play_to_incident`, `finish_dialog`, `god_mode`).
- Produces: bukti terdokumentasi 4 jalur moral tuntas & deterministik.

- [ ] **Step 1: Tulis test playthrough per cabang** (deterministik via god_mode)
- [ ] **Step 2: Run** — semua cabang hijau; bug yang terungkap → fix terpisah + re-run
- [ ] **Step 3: Commit** — `test: playthrough 4 cabang moral + verifikasi world-state akhir`

### G1-T2: Kontrak transisi arc + arc_summary generik + keputusan desain arc 2

> Kondisi sekarang: `q_akademi_07` (`final_quest` arc 1) punya `next: []` → setelah selesai game masuk sandbox; tidak ada konvensi bagaimana arc 2 dimulai; `arc_summary` perlu diverifikasi untuk multi-arc.

**Files:**
- Modify: `src/engine/session.py` — `_arc_summary`/`_pick_ending`: pilih arc berdasarkan **quest yang baru selesai == `arc.final_quest`** (generik N arc; arc tanpa `endings` → `ending: None`, kontrak lama utuh).
- Modify: `tools/validate_data.py` — perkuat: `arcs[].final_quest` harus quest kind=main yang ada (aturan 7).
- Modify: `docs/ENGINE_ARCHITECTURE.md` — **§ "Menambah Arc Baru (checklist)"** + **keputusan desain arc 2** (di bawah).
- Modify: `tests/test_session.py` / `test_saveload.py` — arc kedua sintetis (config arcs + quest mini): selesaikan final quest arc 1 → quest arc 2 aktif via `next`; `arc_summary` menunjuk arc yang benar.

**Keputusan desain yang WAJIB diselesaikan di task ini (sebelum menulis konten arc 2):**
1. **`world.hunt` multi-lokasi?** — schema sekarang global tunggal (`world.hunt.location`). Bila arc 2 punya wilayah berburu baru → perluas schema: `world.hunt` → `hunt_zones: [{id, location, pool, night_pool, mini_boss, search_item}]` (per-lokasi) ATAU `world.hunt` per-arc (`arcs[].hunt`). **Keputusan**: default sederhana — arc 2 memakai `world.hunt` yang sama (wilayah berburu 1 tetap); perluasan schema HANYA bila outline cerita arc 2 benar-benar menuntut wilayah baru. Dicatat sebagai keputusan, bukan dibangun spekulatif.
2. **Gating quest by relation/reputation?** — dialog sudah punya `relation_min`; quest `available_from` belum mendukung relation. Bila arc 2 butuh "quest hanya muncul jika relation ≥ X" → tambah key `relation_min` di `available_from` (validator + engine, pola kondisi dialog). **Keputusan**: ditunda ke outline cerita (G3 pipeline), dicatat di checklist.
3. **Scoping memory per arc** — `memory_unlock` quest pakai id global (`mem_01`..); `arcs[].memories_total` ada. Konvensi penamaan ingatan arc 2 (`mem_2_01` dst.) dicatat di checklist + validator cek prefiks arc bila perlu.

**Interfaces:**
- Consumes: `config.arcs[]` (multi-arc), quest `next` lintas-arc.
- Produces: transisi arc = **data murni** (`next` quest final arc sebelumnya — sudah didukung `_advance_main`); arc_summary benar per arc; keputusan desain terdokumentasi.

- [ ] **Step 1: Tulis failing test** — arc kedua sintetis → transisi + arc_summary benar
- [ ] **Step 2: Run** — verifikasi gagal
- [ ] **Step 3: Implementasi** — generalisasi `_arc_summary` + validator `final_quest`
- [ ] **Step 4: Putuskan & dokumentasikan 3 keputusan desain** (hunt/relation-gating/memory-scoping) di ENGINE_ARCHITECTURE checklist
- [ ] **Step 5: Run** — validate + pytest + playthrough arc 1 hijau
- [ ] **Step 6: Commit** — `feat+test: arc_summary generik + kontrak transisi arc + checklist docs`

### G1-T3: Test adaptivitas — fixture arc sintetis (bukti "arc baru = data saja")

> Kondisi sekarang: tidak ada test yang membuktikan klaim adaptif. Fixture = data arc mini (`q_arc2_*`) dijalankan lewat `GameSession` tanpa sentuhan kode — bukti otomatis + template data arc 2 asli.

**Files:**
- Add: `tests/test_adaptivity.py` — fixture arc sintetis: quest `q_arc2_01` (talk), `q_arc2_02` (reach + time_window), `q_arc2_03` (defeat + report_to), `q_side_arc2` (gather + report_to), NPC `npc_arc2`, dialog `dlg_arc2` (2 node + choice bersyarat), lokasi `loc_arc2_a/b`, item `item_arc2`. Alur lengkap: talk → reach → defeat+lapor → gather+lapor; assertion quest selesai benar.
- Add (opsional): `tests/test_adaptivity_hardcode.py` — grep `src/engine/*.py` (kecuali loader) & `src/cli.py` untuk id konten arc-1 literal (`loc_|npc_|q_|dlg_|eno_|akademi_|tek_`) dengan whitelist eksplisit (komentar/docstring). Bila terlalu brittle (false positive) → andalkan fixture G1-T3 saja, catat di dokumen.
- Modify: `tests/conftest.py` — helper fixture `arc2_registry` bila perlu.

**Interfaces:**
- Consumes: mekanik quest existing (talk/reach/defeat/gather + report_to + node wajib).
- Produces: regression guard — arc 2 yang butuh mekanik baru akan membuat fixture perlu diperluas (sinyal sadar, bukan hardcode diam-diam).

- [ ] **Step 1: Tulis test fixture** (alur lengkap)
- [ ] **Step 2: Run** — hijau pada engine existing (membuktikan adaptif sudah jalan)
- [ ] **Step 3: (opsional) test hardcode grep** — whitelist match existing
- [ ] **Step 4: Commit** — `test: fixture arc sintetis — bukti engine adaptif (arc baru = data saja)`

### G1-T4: Deklarasi freeze (penutup G1)

**Files:**
- Modify: `docs/PROJECT.md` — Feature Inventory: Fase 1.5 items + "Playtest Arc 1 — 4 cabang" DONE (Verified).
- Modify: `docs/DESIGN_SUMMARY.md` — keputusan: **Gameplay & Narrative Foundation Fase 1 = FROZEN** (tanggal; bukti: test count, validator, playtest 4 cabang, 0 hardcode arc-1 di engine). Catatan: mekanik tambahan (quest failure dll.) dibangun per kebutuhan outline arc 2 — freeze adalah fondasi inti, bukan larangan menambah mekanik.
- Modify: `README.md` — jumlah test bila berubah.

- [ ] **Step 1: Update PROJECT.md + DESIGN_SUMMARY.md + README**
- [ ] **Step 2: Commit** — `docs: deklarasi Gameplay Foundation Fase 1 FROZEN (playtest 4 cabang, 0 hardcode)`

---

# GELOMBANG 2 — P1: Micro-task adaptivitas (satu batch, eksekusi cepat)

### G2-T1: Hilangkan hardcode `loc_wilayah_berburu` + auto-equip starter kit

> Dua task kecil digabung jadi satu batch untuk mengurangi context-switch (satu sesi kerja, dua commit kecil). B1: `cli.py:96` satu-satunya id konten arc-1 tersisa di luar data. A1: gap rekomendasi ChatGPT — senjata starter hanya masuk inventori, tidak ter-equip.

**Files:**
- Modify: `src/engine/session.py` — helper `can_hunt()` baca `config.world.hunt.location` (konsisten `_hunt` A8).
- Modify: `src/cli.py` — ganti `if v["location"]["id"] == "loc_wilayah_berburu":` → `if session.can_hunt():`. Cek `web/app.py`/`app.js` tidak menyebut id itu (bila ada, ganti sama).
- Modify: `src/engine/quest.py` — `_grant_starter_kit`: item `type == "weapon"` + `equipment["weapon"] is None` → auto-equip + log naratif; item tetap di inventori (konsisten `_equip`); non-weapon → inventori biasa; slot terisi → tidak menimpa.
- Modify: `tests/test_session.py` / `tests/test_learning.py` — `can_hunt` data-driven; auto-equip (pilih paviliun → weapon terpasang; weapon kedua tidak menimpa; non-weapon tidak ter-equip).
- Modify: `docs/ENGINE_ARCHITECTURE.md` — `can_hunt` (bila § menyebut perilaku hunt CLI).

**Interfaces:**
- Consumes: `config.world.hunt.location`, `items.csv::type`, `player.equipment.weapon`.
- Produces: 0 hardcode id arc-1 di `src/`/`web/`; pemain langsung punya senjata terpasang.

- [ ] **Step 1: Tulis failing test** (can_hunt + auto-equip)
- [ ] **Step 2: Run** — verifikasi gagal
- [ ] **Step 3: Implementasi** — `can_hunt` + cli.py + `_grant_starter_kit` auto-equip
- [ ] **Step 4: Run** — validate + pytest + playthrough 3 akademi hijau
- [ ] **Step 5: Commit** — dua commit: `fix+test: can_hunt data-driven (hilangkan hardcode lokasi berburu)` · `feat: starter kit auto-equip senjata`

---

# GELOMBANG 3 — P2: Ditunda ke pipeline desain cerita arc 2

### G3-T1: Quest failure/deadline — DITUNDA (menunggu outline cerita arc 2)

> **Keputusan evaluasi**: tidak dikerjakan sekarang. Blueprint #11 sendiri: *"Tidak harus semua digunakan di Fase 2."* Tanpa outline cerita arc 2 kita tidak tahu bentuk deadline (hari absolut vs jam relatif vs kondisi), dan membangun skema spekulatif berisiko **memaksa ubah engine saat arc 2** — kebalikan tujuan.
>
> **Kapan dikerjakan**: setelah outline cerita arc 2 disetujui (pipeline: outline → identifikasi mekanik yang dibutuhkan → bangun & validasi → isi konten). Spesifikasi yang sudah dirancang (siap eksekusi saat dibutuhkan):
> - Schema: quest opsional `timeout: {hours}` (relatif sejak quest mulai, pola `advance_time.day_offset`), `fail_effects` (divalidasi seperti `on_complete.effects`), `fail_next` (quest pengganti — **wajib untuk main quest ber-timeout**, validator).
> - Engine: `quest.check_timeouts()` dipanggil `session._pass_time` (konsisten H1); side quest gagal → efek + hapus + `failed_quests`; main quest gagal → efek + `fail_next` aktif + `failed_quests`.
> - State: `failed_quests: list[str]` (diserialisasi, default `[]` — save lama tetap dimuat).
> - UI: `objective_text` menampilkan sisa jam untuk quest ber-timeout.
> - Validator: aturan baru (timeout valid; main ber-timeout wajib `fail_next`; `fail_next` quest kind=main valid; `fail_effects` dikenal).
> - Test: side gagal, main gagal → fail_next, tanpa timeout tidak terpengaruh, save/load.

### G3-T2: Onboarding loop — AUDIT dulu (kemungkinan tanpa perubahan)

> Blueprint #9 — pemain baru paham 8 sistem inti dalam 15 menit pertama. Arc 2 = lanjutan (bukan new game), onboarding tetap relevan untuk pemain baru arc 1. Prinsip: **konten data, target nol perubahan engine**.
>
> **Langkah**: (1) audit playthrough q1→q4b — sistem inti tersentuh: movement/dialog/quest/paviliun/learning/combat ✅; inventory ⚠️ (pil_qi tersedia tapi belum dituntun pemakaiannya); cultivation ⚠️ (grounding belum disebut quest pemandu). (2) Bila gap → tutup via hint dialog/quest (data), bukan aksi baru. (3) Commit `feat(data): ...` atau `docs:` bila tanpa perubahan.
>
> **Bila audit menunjukkan butuh perubahan engine** (di luar dugaan) → hentikan, laporkan ke user untuk keputusan (jangan perluas scope diam-diam).

---

## Definition of Done (DoD)

1. `python3 tools/validate_data.py` exit 0; `python3 -m pytest -q` hijau (test baru: playthrough 4 cabang, transisi arc, fixture adaptivitas, can_hunt, auto-equip).
2. **0 hardcode id konten arc-1 di `src/`/`web/`** (grep `loc_|npc_|q_|dlg_|eno_|akademi_|tek_` di luar data/loader — hanya whitelist komentar).
3. Arc 1 (Akademi) **identik**: playthrough CLI 3 akademi + 4 cabang hijau (non-breaking).
4. Keputusan desain arc 2 (hunt multi-lokasi, relation-gating quest, scoping memory per arc) **terdokumentasi** di ENGINE_ARCHITECTURE checklist — keputusan final menunggu outline cerita arc 2.
5. Freeze resmi di DESIGN_SUMMARY; PROJECT.md/README sinkron.
6. Quest failure (G3-T1) **tidak** dikerjakan di gelombang ini — spesifikasi siap, eksekusi menunggu outline cerita arc 2.
7. Semua commit G1+G2 ter-push ke `origin/main`.

## Pasca-plan (di luar scope dokumen ini, urutan berikutnya)

1. Tulis **outline cerita arc 2** (quest DAG, cabang, deadline, gating) — basis keputusan G3-T1 + keputusan desain G1-T2.
2. Eksekusi G3 sesuai kebutuhan outline (quest failure bila dibutuhkan; onboarding bila audit menuntut).
3. Isi konten arc 2 = data (quests_arc2.json, NPC, lokasi, dialog, config.arcs) — tanpa ubah engine, diverifikasi via fixture G1-T3.
