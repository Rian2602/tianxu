# Rampungkan Arc Akademi (Tahap A FULL) — Implementation Plan

> **Untuk agentic workers:** REQUIRED SUB-SKILL: Gunakan `superpowers:subagent-driven-development` (disarankan) atau `superpowers:executing-plans` untuk implementasi task-by-task. Steps pakai checkbox (`- [ ]`).
>
> **Sumber**: audit status Arc Akademi & kesiapan engine adaptif (2026-08-14) — keputusan user: Arc Akademi harus **rampung penuh** (konten + DoD + matangkan) sebelum arc berikutnya; engine baru boleh dibangun bila mekanik baru diperlukan, dengan aturan arc baru = data.
>
> **STATUS EKSEKUSI (2026-08-14)**: ✅ **SELESAI** — Task A1 (playthrough 3 akademi, tutup DoD §11.2 #1, commit `b2388c7`) & Task A2 (keputusan §17).
>
> **Keputusan A2 (ask_user 2026-08-14)**: (1) Han Xiu → **`turn_order: "speed"`** (engine, bukan naikkan stat); (2) reward q3 → **turunkan exp 8→4**; (3) side quest defeat → **tambah lapor (`report_to`)**; (4) over-leveling → **cap exp grind harian** (`daily_grind_exp_cap` 60). Deviasi kecil saat eksekusi: god_mode test diubah menjadi **no-op `_enemy_turn`** (ed-aware gagal untuk musuh custom tanpa elemen) — aman, test damage-musuh tidak pakai god_mode. Verifikasi: validate exit 0 + **230 passed**; guardrail arc-end Lv 4–6 hijau untuk 3 akademi.

**Goal:** Menutup seluruh gap konten Arc Akademi: (A1) DoD §11.2 #1 — playthrough end-to-end untuk **3 akademi** (elemen/senjata/summoning), dan (A2) memutuskan + menerapkan 4 temuan playtest §17 yang masih terbuka (balance Han Xiu, reward ganda spar q3, side quest "defeat" tanpa lapor, over-leveling). **Tidak** termasuk generalisasi engine (Tahap B — plan terpisah); pengecualian: bila keputusan A2 memilih dukungan `turn_order: "speed"`, itu menjadi satu-satunya perubahan engine di plan ini (dengan validator + docs).

**Architecture:** A1 = 100% test baru (tanpa ubah kode produksi — buktikan 3 akademi playable sampai q07). A2 = satu sesi `ask_user` untuk 4 keputusan (masing-masing punya default), lalu implementasi keputusan: mayoritas data (`npcs.json`, `quests_akademi.json`), maksimal 1 perubahan engine kecil (turn-order). Commit: A1 (test) terpisah dari A2 (data/engine) — file disjoint (`tests/test_cli.py` vs data + `battle.py`).

**Tech Stack:** Python 3.12, stdlib-only, pytest. Tidak ada lint/typecheck.

## Global Constraints

- Semua komentar, dokumen, dan teks test **Bahasa Indonesia**; istilah teknis ber-pinyin/hanzi.
- Wajib lolos setelah setiap task: `python3 tools/validate_data.py` (exit 0) **dan** `python3 -m pytest -q`. Urutan baku CI: validate → pytest.
- Run dari root repo. Tidak menambah dependency.
- Konvensi commit repo: `feat:`, `test:`, `docs:`, `fix+test:`.
- Pola TDD untuk perubahan perilaku (A2): tulis failing test dulu → verifikasi gagal → implementasi → hijau.
- Setiap perubahan skema data (mis. field objective baru) WAJIB disertai pembaruan validator.

---

### Task A1: Playthrough end-to-end 3 akademi (tutup DoD §11.2 #1)

> Kondisi sekarang: `test_cli_playthrough_3aa` & `test_cli_full_playthrough_commands` keduanya jalur 3aa + akademi_elemen. akademi_senjata & akademi_summoning hanya punya test fragmen (battle/companion/dialog). DoD §11.2 #1 ("3 playthrough minimal") belum tertutup.

**Files:**
- Modify: `tests/test_cli.py` — **parametrize** `test_cli_playthrough_3aa` (satu body, 3 varian: elemen/senjata/summoning) — bukan duplikasi script

**Interfaces:**
- Produces: 2 test playthrough baru (senjata, summoning) yang menuntaskan q01–q07 jalur 3aa, memakai teknik khas akademi, dan meng-assert:
  - banner "AKHIR ARC 1: AKADEMI CHANGFENG" + "Konfrontasi Terbuka Penatua An" (capsys)
  - teknik akademi terpakai di battle (senjata: `tek_senjata_tebasan_angin`; summoning: `tek_summoning_roh_api`) — script CLI menyisipkan perintah `teknik <id>` sebelum `serang`
  - summoning: teks kompanion muncul di battle view (assert output CLI mengandung nama roh / stat bar roh)
- Data acuan (terverifikasi): teknik per akademi di `techniques.csv` (senjata: tebasan_angin qi 8; summoning: roh_api qi 8 — muat di qi awal); `play_to_incident` menerima `akademi_senjata`/`akademi_summoning`; kompanion `komp_roh_awan` otomatis menyerang di battle.

> **Catatan**: jalankan playthrough terlebih dahulu sebagai *verifikasi manual* (skrip ad-hoc) untuk akademi senjata & summoning — pastikan tidak ada asumsi tersembunyi (mis. perintah CLI "teknik" membutuhkan qi cukup, kompanion tidak mengubah jumlah langkah "serang"). Baru tulis test permanen dari skrip yang terbukti jalan.

- [ ] **Step 1: Verifikasi manual playthrough senjata & summoning** — skrip ad-hoc (god mode) sampai q07; catat skrip CLI yang berhasil (teknik id + jumlah langkah "serang" per battle)
- [ ] **Step 2: Parametrize `test_cli_playthrough_3aa`** — `@pytest.mark.parametrize("akademi, teknik_id, pakai_roh", [...])` — satu body test, script `pilih {akademi}` + sisipkan `teknik {teknik_id}` (bila ada) sebelum `serang`; varian: elemen (None, False), senjata (tek_senjata_tebasan_angin, False), summoning (tek_summoning_roh_api, True)
- [ ] **Step 3: Assert per varian** — banner "AKHIR ARC 1" + "Konfrontasi Terbuka Penatua An"; `pakai_roh=True` → teks "Roh" muncul di output (terverifikasi: CLI render header `cli.py:61-63` & battle `:138-140`); semua varian assert `realm_level` akhir di Lv 4–6 (**baseline pacing** — jadi guardrail A2)
- [ ] **Step 4: Run** `python3 -m pytest tests/test_cli.py -q` — playthrough (3aa × 3 varian + full-commands) hijau
- [ ] **Step 5: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau (total test +2 via parametrize)
- [ ] **Step 6: Docs** — `docs/ENGINE_ARCHITECTURE.md` §11.2/DoD: tandai butir 1 "3 playthrough" ✅ (catat 3 akademi di-cover); `docs/list_bug.md`/`CHANGELOG.md` catat penutupan DoD
- [ ] **Step 7: Commit** `test: playthrough end-to-end 3 akademi — tutup DoD §11.2 #1`

### Task A2: Keputusan & implementasi temuan playtest §17

> Empat temuan terbuka di ENGINE §17: (1) Han Xiu undertuned — gate ujian q3 terlalu mudah, pemain selalu duluan (`turn_order: fixed_alternate`, `speed` hanya dipakai flee); (2) reward ganda spar q3 — `spar_win_exp` 8 + reward quest q3 `{exp 8, gold 10}` = 16 exp sekali menang (terverifikasi); (3) side quest `q_side_berburu` (kind `defeat`) auto-complete saat battle menang tanpa lapor `npc_pemburu`; (4) over-leveling via grind Lv1→Lv8 (disengaja, side quest = grinding).

**Files (tergantung keputusan — mayoritas data):**
- Modify: `data/npcs.json` (stat Han Xiu bila naik)
- Modify: `data/quests/quests_akademi.json` (reward q3 bila diturunkan)
- Modify: `src/engine/battle.py` (hanya bila memilih `turn_order: "speed"`)
- Modify: `data/config.json` (hanya bila turn-order speed: `battle.turn_order`)
- Modify: `tests/test_battle.py` / `tests/test_session.py` (test sesuai keputusan)
- Modify: `docs/ENGINE_ARCHITECTURE.md` §17 (tandai tiap temuan: keputusan + status)

**Interfaces:**
- Consumes: `battle.py` (urutan giliran, reward spar), `quest.py::notify_battle_won` (side quest defeat), `data/npcs.json` Han Xiu combat, `data/quests/quests_akademi.json` q3 on_complete.
- Produces: keputusan tertulis di §17 + data/test sesuai pilihan.

> **Keputusan default (diajukan, dikonfirmasi 1 sesi ask_user):**
> 1. **Han Xiu q3** — default: **naikkan stat** tanpa ubah `turn_order` — angka final **ditentukan setelah simulasi deterministik** (bukan asumsi): target kemenangan pemain ~60–70% di Lv1 (strategi wajar), nyaris pasti di Lv2; jalur kalah tetap non-blocking (G4a: `spar_kalah` = quest selesai + dialog beda — aman). Opsi lain: dukung `turn_order: "speed"` (engine), atau terima by-design.
> 2. **Reward ganda q3** — default: **turunkan reward quest q3** `exp 8 → 4` (total spar ujian = 12 exp + 10 koin, tetap terasa, tidak dobel penuh). Opsi lain: terima overlap.
> 3. **Side quest defeat tanpa lapor** — default: **terima + dokumentasikan** (auto-complete konsisten dengan objektif `defeat` quest utama; lapor menambah kompleksitas tanpa nilai naratif besar). Opsi lain: tambah langkah lapor (objektif `report` baru di engine — skala lebih besar, masuk Tahap B).
> 4. **Over-leveling** — default: **dokumentasikan sebagai desain** (grinding = tujuan side quest; jalur utama target Lv 4–6 sudah sesuai). Tanpa perubahan.

- [ ] **Step 1: ask_user** — konfirmasi 4 keputusan (default di atas); catat jawaban ke plan
- [ ] **Step 2: Simulasi balance Han Xiu** (bila keputusan #1 = naikkan stat) — test deterministik RNG (`test_battle.py`): simulasikan duel Lv1 & Lv2 terhadap kandidat stat; pilih angka yang memenuhi target menang 60–70% / ~100%
- [ ] **Step 3: Tulis failing test sesuai keputusan** (keputusan #1: `test_battle.py` outcome Han Xiu baru; #2: test reward q3 = 4 exp; #3: test auto-complete tetap)
- [ ] **Step 4: Run** test — verifikasi gagal
- [ ] **Step 5: Implementasi** — data (`npcs.json`, `quests_akademi.json`) dan/atau engine (`battle.py` turn-order) sesuai keputusan; validator bila skema berubah
- [ ] **Step 6: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 7: Guardrail pacing** — jalankan playthrough parametrize (A1): arc-end `realm_level` tetap Lv 4–6 setelah reward q3 diturunkan; sesuaikan data bila meleset
- [ ] **Step 8: Docs** — ENGINE §17: 4 temuan ditandai `(KEPUTUSAN + status, 2026-08-14)`; `CHANGELOG.md`; `PROJECT.md` (bila ada baris baru)
- [ ] **Step 9: Commit** `fix+test: keputusan playtest §17 — balance Han Xiu, reward q3, dokumentasi side-quest/grinding`

---

## Kriteria Selesai (Tahap A FULL)

- [ ] `python3 tools/validate_data.py` exit 0 + `python3 -m pytest -q` hijau setelah setiap task (total test +2 dari A1; A2 sesuai keputusan)
- [ ] DoD §11.2 #1 tertutup: 3 akademi (elemen/senjata/summoning) punya playthrough end-to-end otomatis sampai q07 (**1 body parametrize**) — banner arc + cabang + teknik khas akademi (+ teks "Roh" untuk summoning) ter-assert; arc-end `realm_level` Lv 4–6 tercatat sebagai baseline
- [ ] Angka stat Han Xiu final **berasal dari simulasi deterministik** (bukan asumsi) dan memenuhi target menang; guardrail pacing arc-end (Lv 4–6) tetap hijau setelah A2
- [ ] Keempat temuan §17 punya status tertulis: keputusan + implementasi/terima + tanggal (bukan lagi "open")
- [ ] Bila turn-order speed dipilih: `turn_order` tetap data-driven (config), validator menolak nilai tak dikenal, docs §8.1 sinkron
- [ ] Docs sinkron: ENGINE §11.2/§17, CHANGELOG, PROJECT (bila perlu)
- [ ] Commit A1 (test) & A2 (keputusan) terpisah — file disjoint
