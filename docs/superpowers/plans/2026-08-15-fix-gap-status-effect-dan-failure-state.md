# Fix Gap Fase 1.5 — Status Effect + Quest Failure State (+2 minor) — Implementation Plan

> **Untuk agentic workers:** REQUIRED SUB-SKILL: Gunakan `superpowers:subagent-driven-development` (disarankan) atau `superpowers:executing-plans` untuk implementasi task-by-task. Steps pakai checkbox (`- [ ]`).
>
> **Sumber**: Evaluasi hasil kerja vs rekomendasi ChatGPT (2026-08-15, diverifikasi langsung di kode) menemukan 2 gap jujur + 2 minor:
> 1. **Status effect TIDAK ADA di battle** (blueprint #10 "freeze combat API" mencantumkannya) — bila arc 2 butuh burn/stun/poison, `battle.py` harus berubah → melanggar "arc baru = data saja".
> 2. **Quest failure state BELUM ADA** (blueprint #11) — schema tidak bisa membedakan success/failure/expired; spesifikasi lengkap sudah siap di plan `2026-08-15-gap-fase15-dan-adaptivitas-arc2.md` §G3-T1.
> 3. **Minor: gating quest by relation** — quest `available_from` belum dukung `relation_min` (dialog sudah).
> 4. **Minor: tier relationship web 3 vs 5** — rekomendasi hostile/distrustful/neutral/friendly/close; web hanya 3.
>
> **STATUS EKSEKUSI (2026-08-15)**: 🔲 belum dimulai. Baseline terverifikasi: **341 passed**, validate exit 0, playthrough 4 cabang hijau, 0 hardcode arc-1 di `src/web`.

**Goal:** Menutup 2 gap + 2 minor secara **general & data-driven** (arc 2 tetap = data saja), dengan **3 pertanyaan verifikasi sebagai struktur wajib** untuk SETIAP task:

> **Q1 — Sesuai plan secara ketat?** Setiap task punya langkah plan bernomor; akhir task WAJIB mencatat "SESUAI PLAN: ya / deviasi: …" (konvensi repo: deviasi dicatat eksplisit, tidak disembunyikan).
>
> **Q2 — Benar-benar memperbaiki bug?** TDD: test reproduksi yang GAGAL dulu (bukti bug nyata) → implementasi → HIJAU pada skenario bug yang sama (bukan test baru yang kebetulan lolos).
>
> **Q3 — Menimbulkan bug baru?** Setiap task wajib lolos: (a) save/load round-trip dengan field baru; (b) kasus batas (batas waktu/health/stacking/expiry); (c) data lama tetap valid (from_dict default); (d) full suite + validator + playthrough 3 akademi + 4 cabang; (e) fixture adaptivitas (canary) tetap hijau.

**Architecture:** Semua perubahan general & non-breaking — arc Akademi identik (playthrough 4 cabang + 3 akademi tetap hijau); save lama tetap dimuat. Setiap skema baru divalidasi validator. Status effect & failure state dibangun dari **prinsip umum** (bukan spesifik arc 2) supaya tidak terkunci pada cerita tertentu.

**Tech Stack:** Python 3.12, stdlib-only, pytest. Tidak ada lint/typecheck.

## Global Constraints

- Komentar/dokumen/test **Bahasa Indonesia**; istilah teknis ber-pinyin.
- Setiap task: `python3 tools/validate_data.py` exit 0 **dan** `python3 -m pytest -q` hijau.
- Run dari root repo; tidak menambah dependency.
- Konvensi commit: `feat:`, `test:`, `docs:`, `fix+test:`.
- TDD untuk semua perubahan perilaku; skema data baru wajib disertai validator.
- **Q3 selalu**: setelah implementasi, jalankan `tests/test_playthrough_branches.py` + `tests/test_adaptivity.py` + `tests/test_saveload.py` (jaring Q3).

---

### Task 1: Status effect di battle (blueprint #10) — engine + data + validator

> Kondisi sekarang: battle tanpa status effect sama sekali (grep `status|burn|stun|poison` di `battle.py` = kosong). Arc 2 yang butuh "pertarungan vs X yang membakar/melumpuhkan" akan memaksa ubah battle → kontrak belum beku.

**Files:**
- Modify: `data/config.json` — `battle.statuses`: dict id → `{name, kind, power, duration}`. Kind minimal: `dot` (damage per turn) & `stun` (skip turn). Contoh data: `burn` (dot, power 3, duration 3), `stun` (stun, duration 1). Arc 1 TIDAK memakai (non-breaking).
- Modify: `data/enemies.csv` — kolom opsional `status` + `status_chance` (0-1) pada musuh; arc 1 dibiarkan kosong.
- Modify: `src/engine/battle.py` —
  - `start()`: inisialisasi `statuses: {}` per combatant (pemain & tiap foe).
  - Saat serangan musuh kena: bila musuh punya `status` + `status_chance` → terapkan ke pemain (dengan `random.random() < chance`).
  - Awal tiap giliran pemain: proses `dot` (damage) & `stun` (lewati giliran); kurangi `duration`; status habis → hapus.
  - `view()` battle: tampilkan status aktif tiap combatant (opsional, non-breaking).
- Modify: `src/engine/session.py` — serialisasi battle sudah via `pending_battle` deepcopy → status ikut tersimpan (verifikasi round-trip).
- Modify: `tools/validate_data.py` — aturan 16 (battle): `statuses` valid (id unik, kind ∈ {dot, stun}, power/duration int ≥ 0, duration > 0); `enemies.csv` `status` harus ada di `battle.statuses` & `status_chance` 0-1.
- Modify: `tests/test_battle.py` — test baru (Q2).
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §8 kontrak battle + skema status.

**Interfaces:**
- Consumes: `config.battle.statuses`, `enemies.csv::status/status_chance`.
- Produces: musuh arc 2 bisa membakar/melumpuhkan via data; battle API tidak berubah bentuk untuk arc 1.

**Desain:**
- **Q2 (bukti bug)**: test reproduksi — musuh dengan `status: burn, status_chance: 1.0` → setelah serang, pemain punya status `burn`; giliran berikutnya pemain kehilangan `power` HP; setelah `duration` giliran status hilang. `stun` → pemain tidak bisa aksi 1 giliran. Tanpa fitur, test GAGAL (AttributeError/status tak pernah ada).
- **Q3 (no new bug)**: (a) battle tanpa status → perilaku identik (random tidak dipanggil, guard `if not status`); (b) status tidak menumpuk ganda (timpa/replace, keputusan: **replace** — sederhana); (c) expiry tepat di `duration`; (d) save/load di tengah battle → status tetap; (e) KO dengan status aktif → bersih; (f) full suite + playthrough + fixture.

- [ ] **Step 1 (Q2): Tulis failing test reproduksi** — `tests/test_battle.py::test_status_burn_dot_dan_expiry` + `test_status_stun_lewati_giliran` + `test_status_chance_0_tidak_mempan`
- [ ] **Step 2: Run** — verifikasi GAGAL (fitur belum ada)
- [ ] **Step 3: Implementasi config + enemies.csv + battle.py + view**
- [ ] **Step 4: Implementasi validator** (aturan 16 + referensi enemies)
- [ ] **Step 5 (Q3): Test edge + save/load + non-breaking** — battle tanpa status identik; stack replace; expiry; save/load tengah battle
- [ ] **Step 6: Run lengkap** — validate + pytest + playthrough 3 akademi + 4 cabang + fixture adaptivitas
- [ ] **Step 7 (Q1): Catat SESUAI PLAN / deviasi** di status plan ini + commit — `feat+test: status effect data-driven (dot/stun) di battle + validator`

---

> **STATUS EKSEKUSI (2026-08-15)**: Task 1 ✅ commit `45558c2` (350 passed).
> Task 2 ✅ commit `(lihat log)` — SESUAI PLAN: ya. Catatan:
> - Test Q2 (side/main gagal, tanpa timeout, batas >=, selesai sebelum deadline,
>   save lama tanpa start, save/load failed_quests) merah → hijau.
> - Validator: timeout.hours int>0; main ber-timeout WAJIB fail_next; fail_next
>   tanpa timeout / kind side / quest tak ada → ditolak; data arc-1 tanpa timeout
>   tetap lolos.
> - Docs §6.4b + skema §5.1; web memakai `objective_text` (sisa jam otomatis tampil,
>   tanpa ubah web/app).

### Task 2: Quest failure/deadline (blueprint #11) — spesifikasi G3-T1 dieksekusi

> Kondisi sekarang: quest hanya sukses; `failed_quests` tidak ada. Spesifikasi sudah final di plan `2026-08-15-gap-fase15-dan-adaptivitas-arc2.md` §G3-T1 — task ini mengeksekusinya VERBATIM (Q1).

**Files:**
- Modify: `src/engine/state.py` — `failed_quests: list[str]` (to_dict/from_dict, default `[]` — save lama tetap dimuat).
- Modify: `src/engine/quest.py` —
  - `_note_main_start` & `start_side`: catat `start_abs = day*24+hour` (side quest belum mencatat start — perlu).
  - `check_timeouts()`: untuk tiap quest aktif (main + side) dengan `timeout: {hours}` → `now_abs - start_abs >= hours` → gagal: side → `fail_effects` + hapus + `failed_quests`; main → `fail_effects` + `fail_next` (wajib ada, divalidasi) aktif + `failed_quests`.
  - `objective_text`: quest ber-timeout tampil "Sisa: X jam".
- Modify: `src/engine/session.py` — `_pass_time` panggil `quest.check_timeouts()` setelah `advance_time_target_met()` (konsisten H1).
- Modify: `tools/validate_data.py` — aturan baru: `timeout.hours` int > 0; **main quest ber-timeout WAJIB** `fail_next` valid (quest kind=main yang ada); `fail_effects` divalidasi seperti `on_complete.effects`; main quest normal dilarang `fail_next`.
- Modify: `web/app.py`/`app.js` — quest panel tampilkan sisa waktu (opsional, non-breaking).
- Modify: `tests/test_quest_dag.py` / `tests/test_saveload.py` — test (Q2).
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §6 lifecycle quest (timeout/fail_next/fail_effects/failed_quests).

**Interfaces:**
- Consumes: quest `timeout`/`fail_next`/`fail_effects` (semua opsional).
- Produces: quest bisa gagal → efek + cabang gagal; state gagal tersimpan; UI sisa waktu.

**Desain:**
- **Q2 (bukti bug)**: test reproduksi — side quest `timeout: {hours: 5}` → lewat 6 jam (advance_time) → quest hilang dari aktif + masuk `failed_quests` + `fail_effects` diterapkan. Main quest ber-timeout → `fail_next` aktif + `current_quest` berpindah + `failed_quests` tercatat. Quest TANPA timeout → tidak terpengaruh. Sebelum implementasi: GAGAL (tidak ada check_timeouts/failed_quests).
- **Q3 (no new bug)**: (a) timeout di batas persis (`>=` vs `>` — keputusan: **`>=`**); (b) main quest gagal tanpa `fail_next` → validator MENOLAK sejak data (engine tidak pernah macet); (c) save/load membawa `failed_quests`; (d) quest selesai tepat sebelum deadline → tidak gagal (urutan: cek timeout setelah advance_time, quest selesai sudah pop dari aktif); (e) data arc-1 tanpa timeout → tidak berubah; (f) full suite + playthrough + fixture.

- [ ] **Step 1 (Q2): Tulis failing test** — side gagal, main gagal → fail_next, tanpa timeout tak terpengaruh, save/load `failed_quests`
- [ ] **Step 2: Run** — verifikasi GAGAL
- [ ] **Step 3: Implementasi state + quest engine + session**
- [ ] **Step 4: Implementasi validator** + verifikasi data arc-1 lolos (tidak ada quest ber-timeout → non-breaking)
- [ ] **Step 5 (Q3): Test edge** — batas `>=`, selesai tepat sebelum deadline, save/load, main tanpa fail_next ditolak validator
- [ ] **Step 6: Run lengkap** — validate + pytest + playthrough + 4 cabang + fixture
- [ ] **Step 7 (Q1): Catat SESUAI PLAN / deviasi** + commit — `feat+test: quest failure/deadline (timeout, fail_next, failed_quests) + validator`

---

### Task 3 (minor): Gating quest by relation (available_from.relation_min)

> Kondisi sekarang: dialog punya `relation_min`; quest `available_from` belum. Arc 2: "quest hanya muncul bila relation ≥ X".

**Files:**
- Modify: `src/engine/quest.py` — `is_offerable`: bila `available_from.relation_min = {npc, value}` → `state.relations.get(npc, 0) >= value` (gagal → tidak ditawarkan).
- Modify: `tools/validate_data.py` — aturan 8: `available_from.relation_min` valid (npc ada, value int).
- Modify: `tests/test_quest_dag.py` — test: relation rendah → tidak ditawarkan; cukup → ditawarkan.
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §6.4/§6.5.
- **Q2**: test reproduksi gagal dulu (quest ditawarkan padahal relation 0) → hijau setelah implementasi.
- **Q3**: data arc-1 tanpa `relation_min` → `available_from` lama tetap jalan; save/load tidak terpengaruh (tidak ada field state baru); full suite.
- Commit: `feat+test: gating side quest by relation (available_from.relation_min)`

---

### Task 4 (minor): Tier relationship web 5 tingkat

> Kondisi sekarang: `getRelationTier` 3 tier; rekomendasi 5 (hostile/distrustful/neutral/friendly/close).

**Files:**
- Modify: `web/static/app.js` — `getRelationTier`: skor ≤ -20 hostile, -19..-1 distrustful, 0 neutral, 1..19 friendly, ≥ 20 close; label Indonesia (Bermusuhan/Kurang Akrab/Netral/Bersahabat/Akrab).
- Modify: `web/static/style.css` — kelas badge `distrustful`/`close` (bila perlu).
- **Q2**: verifikasi fungsi tier (unit check via node atau assertion manual) untuk 5 ambang.
- **Q3**: perubahan murni tampilan — tidak menyentuh engine; cek `node --check` + test web tetap hijau.
- Commit: `feat(web): tier relationship 5 tingkat (hostile/distrustful/neutral/friendly/close)`

---

## Definition of Done (DoD)

1. **Q1 — SESUAI PLAN KETAT**: setiap task selesai dengan catatan "SESUAI PLAN: ya / deviasi: …" di status plan; deviasi (bila ada) dievaluasi eksplisit, bukan disembunyikan.
2. **Q2 — BENAR-BENAR MEMPERBAIKI**: tiap bug punya test reproduksi yang terbukti GAGAL sebelum fix & HIJAU setelah fix (bukan test baru yang kebetulan lolos).
3. **Q3 — TIDAK ADA BUG BARU**:
   - Full suite hijau + validator exit 0 + playthrough CLI 3 akademi + `tests/test_playthrough_branches.py` (4 cabang) + `tests/test_adaptivity.py` (fixture canary).
   - Save/load round-trip dengan field baru (`failed_quests`, status battle) + save lama (from_dict default) tetap dimuat.
   - Kasus batas tiap fitur diuji (expiry/stacking/`>=` boundary/chance 0-1/data tanpa field).
   - Validator menolak data korup baru (status tak dikenal, main ber-timeout tanpa fail_next, relation_min npc tak ada).
4. Arc 1 (Akademi) **identik secara konten & perilaku** (non-breaking).
5. Dokumentasi sinkron: ENGINE_ARCHITECTURE (§8 status, §6 lifecycle quest, §6.5 checklist diperbarui), DESIGN_SUMMARY catatan gap tertutup, PROJECT.md/README test count bila berubah.
6. Semua commit ter-push ke `origin/main`.

## Pasca-plan

- Update plan `2026-08-15-gap-fase15-dan-adaptivitas-arc2.md`: tandai G3-T1 selesai (failure state) & §6.5 catatan status effect tertutup.
- Setelah 2 gap + 2 minor tertutup → **freeze penuh** (termasuk mekanik battle & failure): arc 2 = data saja, satu-satunya jalur perubahan engine = mekanik baru yang diidentifikasi outline cerita (dengan fixture sebagai canary).
