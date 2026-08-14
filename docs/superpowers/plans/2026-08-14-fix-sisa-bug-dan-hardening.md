# Fix Sisa Bug & Hardening — Implementation Plan

> **Untuk agentic workers:** REQUIRED SUB-SKILL: Gunakan `superpowers:subagent-driven-development` (disarankan) atau `superpowers:executing-plans` untuk implementasi task-by-task. Steps pakai checkbox (`- [ ]`).
>
> **Sumber temuan**: `docs/list_bug.md` (audit 1–9, diverifikasi 2026-08-14). Status verifikasi ulang: 9 fix terdokumentasi + batch tambahan (H1/H2/H3/G4e/K1–K5/G4d) sudah di working tree (201 test pass); daftar di bawah = **sisa yang belum diperbaiki** + **kelemahan minor fix yang sudah diterapkan**.
>
> **STATUS EKSEKUSI (2026-08-14 lanjutan)**: ✅ **SELESAI** — Fase A (Task 1–5), Fase B (Task 6–10, semua keputusan default disahkan via ask_user), Fase D (Task 12–14). Task 11 (B3/#13) sengaja tidak dikerjakan (defer). Verifikasi akhir: `tools/validate_data.py` exit 0 + `pytest` **209 passed**. Keputusan desain Fase B yang disahkan: 4 world-facts flags · 3 node reaksi 3ab · q07 3aa jadi konfirmasi · `node_penutup_3b` versi gelap · spar kalah = selesai + dialog berbeda.

**Goal:** Menutup seluruh bug aktif/latent yang tersisa (A1, A2, B2, B3/#13, G4a, G4b/#10, G4c, G4f, H4, J3#6, #9) dan memperbaiki kelemahan minor pada fix yang sudah diterapkan (K4 lock server, G3d lintas perangkat, docs tertinggal) — tanpa mengubah arsitektur.

**Architecture:** Fase A = fix teknis aman (tanpa keputusan desain: H4, A1, J3#6, #9, A2). Fase B = perbaikan konten naratif yang butuh keputusan desain (G4b/#10, G4c, G4f, B2, G4a) — setiap task dimulai dengan keputusan default yang diusulkan, konfirmasi via ask_user bila dijalankan. Fase C = fitur baru skala besar (B3/#13) — defer, dikerjakan terpisah. Fase D = hardening web opsional + sinkronisasi dokumentasi.

**Tech Stack:** Python 3.12, stdlib-only, pytest. Tidak ada lint/typecheck.

## Global Constraints

- Semua komentar, dokumen, dan teks test **Bahasa Indonesia**; istilah teknis ber-pinyin/hanzi.
- Wajib lolos setelah setiap task: `python3 tools/validate_data.py` (exit 0) **dan** `python3 -m pytest -q`. Urutan baku CI: validate → pytest.
- Run dari root repo. Tidak menambah dependency.
- Mengubah skema data wajib disertai pembaruan validator `tools/validate_data.py` + `docs/ENGINE_ARCHITECTURE.md` (aturan emas §1).
- Konvensi commit repo: `fix:`, `test:`, `docs:`, `feat:`, `chore:`.

---

## Fase A — Fix teknis aman (tanpa keputusan desain)

### Task 1: H4 — tegakkan `realm_required` pada teknik

> Temuan: `battle.py::_technique` cek teknik dikenal → skill_pool → Qi, **tanpa** cek ranah; `loader.player_techniques` hanya filter prefix. Latent di Arc 1 (semua teknik `realm_pengumpul_qi`), menyala di Arc 2.

**Files:**
- Modify: `src/engine/battle.py::_technique` — cek ranah sebelum izin pakai
- Modify: `src/engine/loader.py::player_techniques` — filter `realm_required` ≤ ranah pemain (pola sama `dialog.py:137` bandingkan `order`)
- Modify: `tests/test_battle.py` — test teknik ranah lebih tinggi ditolak
- Modify: `docs/ENGINE_ARCHITECTURE.md` §9.2 — catatan enforcement

**Interfaces:**
- Consumes: `registry.realms[realm]["order"]`, `state.player.realm`; `BattleEngine._technique(pc, b, tid)`.

- [ ] **Step 1: Tulis failing test** — teknik dummy `realm_required` ranah lebih tinggi → log "ranah belum cukup", teknik tidak memberi damage, dan **giliran tetap berlanjut seperti aksi invalid lain** (musuh tetap menyerang — perilaku existing `battle.py`, konsisten dengan keputusan desain §G P2)
- [ ] **Step 2: Run** `python3 -m pytest tests/test_battle.py -q` — verifikasi gagal
- [ ] **Step 3: Fix** `_technique` (cek `order` ranah) + `loader.player_techniques` (filter ranah)
- [ ] **Step 4: Run** `python3 -m pytest -q` — hijau (201 + test baru)
- [ ] **Step 5: Update docs** §9.2
- [ ] **Step 6: Commit** `fix+battle: tegakkan realm_required teknik (H4)`

### Task 2: A1 — jadwal NPC dukung lintas tengah malam

> Temuan: `_is_npc_available` (`session.py:159`) `h_start <= hour <= h_end` tak menangani `19 → 06`; inkonsisten dengan `quest.py::_in_window` (`start <= h < end`). Latent (data belum ada jadwal lintas tengah malam) — fix menyeragamkan perilaku.

**Files:**
- Modify: `src/engine/session.py::_is_npc_available` — pola `start <= h < end`, lintas tengah malam `h >= start or h < end`
- Modify: `tests/test_session.py` — test NPC jadwal `19–06` tersedia jam 20 & 05, tidak jam 12
- Modify: `docs/ENGINE_ARCHITECTURE.md` §17 (jadwal NPC) — catatan batas inklusif/eksklusif diseragamkan

**Interfaces:**
- Consumes: `npc["schedule"]` (`hour_start`/`hour_end`); `state.hour`.

- [ ] **Step 1: Tulis failing test** — jadwal sintetis `19→06`: jam 20 & 5 = tersedia; jam 12 = tidak
- [ ] **Step 2: Run** `python3 -m pytest tests/test_session.py -q` — verifikasi gagal
- [ ] **Step 3: Fix** `_is_npc_available` dengan pola `_in_window` (lintas tengah malam)
- [ ] **Step 4: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 5: Update docs** §17
- [ ] **Step 6: Commit** `fix: jadwal NPC lintas tengah malam (A1)`

### Task 3: J3#6 — choice illusion pada `node_konfrontasi`

> Temuan: `dialogs_akademi.json:309-310` dua opsi `node_konfrontasi` sama-sama → `node_konfrontasi2` tanpa efek beda.

**Keputusan default**: opsi pertama (menuntut) diberi efek `morality +1` (konsisten jalur 3aa yang menaikkan moralitas); opsi kedua (menahan amarah) tetap tanpa efek. Ini mempertahankan kedua pilihan tanpa mengubah alur.

**Files:**
- Modify: `data/dialogs/dialogs_akademi.json` — efek pada opsi pertama
- Modify: `tests/test_dialog.py` — verifikasi efek berbeda per opsi

- [ ] **Step 1: Edit data** — tambah `"effects": [{ "type": "morality", "value": 1 }]` pada opsi pertama
- [ ] **Step 2: Tulis test** — pilih opsi 1 → morality naik; opsi 2 → tidak
- [ ] **Step 3: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 4: Commit** `fix: hilangkan choice illusion node_konfrontasi (J3#6)`

### Task 4: #9 — responsif minimal (desktop dulu, breakpoint dasar)

> Temuan: grid `260px 1fr 300px` (`style.css:126`) tanpa `@media`. Keputusan GDD §12.5: "desktop dulu, HP ditunda" — jadi fix = jaga grid 3 kolom di ≥1024px, tumpuk di bawahnya (bukan optimasi HP penuh).

**Files:**
- Modify: `web/static/style.css` — satu `@media (max-width: 1023px)` menumpuk kolom (grid 1 kolom, panel statistik di atas log)
- Verifikasi manual: `python3 web/app.py` + resize browser (tidak ada test otomatis JS/CSS)

- [ ] **Step 1: Tambah @media** di `style.css`
- [ ] **Step 2: Verifikasi manual** — buka `http://localhost:8000`, resize <1024px, pastikan tidak overflow horizontal
- [ ] **Step 3: Commit** `fix: breakpoint responsif dasar web (I1#9)`

### Task 5: A2 — data-drive aktivitas berburu (debt teknis)

> Temuan: pool musuh `_hunt` (`session.py:327-328`) + `loc_wilayah_berburu`/`material_herba` (`:343-345`) hardcoded. Konflik prinsip §2 (data-driven total).

**Keputusan default**: tambah `world.hunt` di `config.json` — `{ "pool": ["eno_serigala_qi", "eno_babi_hutan"], "mini_boss": "eno_raja_serigala", "mini_boss_chance": 0.1, "location": "loc_wilayah_berburu", "search_item": "material_herba" }`; engine baca dari config. Validator aturan 7 diperluas (referensi musuh/lokasi/item valid).

**Files:**
- Modify: `data/config.json` — blok `world.hunt`
- Modify: `src/engine/session.py::_hunt`/`_search` — baca dari `config.world.hunt`
- Modify: `tools/validate_data.py` — aturan 7: validasi referensi pool/mini_boss/location/search_item
- Modify: `tests/test_validator.py` — test data korup (pool musuh tak ada)
- Modify: `tests/test_session.py` — berburu tetap jalan (regresi)
- Modify: `docs/ENGINE_ARCHITECTURE.md` §5.6/§9.2

- [ ] **Step 1: Edit config + validator** (aturan 7 diperluas)
- [ ] **Step 2: Tulis failing test** validator — pool musuh invalid ditolak
- [ ] **Step 3: Refactor** `_hunt`/`_search` baca config (fallback ke nilai lama bila field absen)
- [ ] **Step 4: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 5: Update docs** §5.6/§9.2
- [ ] **Step 6: Commit** `refactor: aktivitas berburu data-driven (A2)`

---

## Fase B — Perbaikan konten naratif (butuh keputusan desain; konfirmasi saat eksekusi)

> Tiap task di fase ini dimulai dengan **ask_user** untuk mengesahkan keputusan default di bawah.

### Task 6: G4b/#10 — world-state resmi untuk kontinuitas Arc 2 (P1)

> Temuan: setelah branch hanya tersimpan `branch_*`, morality, relation, memory — bukan `zhouyan_status`/`bell_status`/`elder_exposed`/`academy_knows_truth`/`chenxu_reputation`. Arc 2 tak bisa menanyakan "apakah Zhou Yan bebas?".

**Keputusan default**: definisikan world-facts sebagai `flags` eksplisit (tanpa field baru):
- `zhouyan_status`: `"bebas"` (3aa/3ab) | `"diusir"` (3b/3c)
- `bell_status`: `"kembali"` (set semua cabang di q07)
- `elder_exposed`: `true` hanya di 3aa
- `academy_knows_truth`: `false` di 3b/3c (tidak ada yang tahu), `true` di 3aa/3ab

Set di `on_complete` quest cabang + q07. Dokumentasikan di `docs/STORY_FASE1.md` (tabel world-state per cabang) dan `docs/ENGINE_ARCHITECTURE.md` §10.

**Files:**
- Modify: `data/quests/quests_akademi.json` — `effects.flag` pada 4 cabang + q07
- Modify: `docs/STORY_FASE1.md` — tabel world-state
- Modify: `docs/ENGINE_ARCHITECTURE.md` §10
- Modify: `tests/test_quest_dag.py` — test flag world-state benar per cabang
- Modify: `tools/validate_data.py` — (opsional) aturan flag kontrak? **Tidak** — flag bebas oleh desain; cukup dokumentasi.

- [ ] **Step 1: Konfirmasi daftar world-facts via ask_user**
- [ ] **Step 2: Edit data** — set flags per cabang
- [ ] **Step 3: Tulis test** — playthrough 3aa → `zhouyan_status=bebas`, `elder_exposed=true`; 3b → `diusir`
- [ ] **Step 4: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 5: Update docs** STORY + ENGINE
- [ ] **Step 6: Commit** `fix+story: world-state cabang untuk Arc 2 (G4b/#10)`

### Task 7: G4c — reaksi positif untuk cabang 3ab

> Temuan: `node_hangat_3a`/`node_bersyukur`/`node_respect` hanya cond `branch_3aa`; tak ada padanan 3ab.

**Keputusan default**: tambah entri kondisional `branch_3ab` untuk ketiga dialog dengan teks lebih tenang (sukses tanpa konfrontasi: "kau melakukan ini dengan kepala dingin" — Su Qing bangga tapi lebih pelan; Zhou Yan bersyukur; Han Xiu diam-diam mengakui, tanpa "berdiri di depan Penatua").

**Files:**
- Modify: `data/dialogs/dialogs_akademi.json` — 3 node padanan 3ab (Su Qing, Zhou Yan, Han Xiu)
- Modify: `tests/test_dialog.py` — entri kondisional 3ab terpilih saat `branch_3ab`

- [ ] **Step 1: Konfirmasi arah teks 3ab via ask_user**
- [ ] **Step 2: Edit data** — node padanan + urutan entri kondisional (pertama yang cocok)
- [ ] **Step 3: Tulis test** — cond `branch_3ab` memilih node 3ab
- [ ] **Step 4: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 5: Commit** `fix+story: reaksi NPC untuk cabang 3ab (G4c)`

### Task 8: G4f — q07 tidak redundan setelah 3aa

> Temuan: `q_akademi_07` objective `talk npc_moyun` untuk semua cabang; setelah 3aa kebenaran sudah terungkap di konfrontasi.

**Keputusan default**: biarkan objective tetap (dokumen mendesain q07 = "talk Mo Yun reaksi beda per cabang"), tapi ubah `node_truth_3aa` → reaksi **pasca-konfrontasi** (Mo Yun mengonfirmasi yang sudah diketahui, bukan reveal pertama; tambah `node_penutup` tetap). Tidak mengubah alur engine — murni teks.

**Files:**
- Modify: `data/dialogs/dialogs_akademi.json` — teks `node_truth_3aa` (konfirmasi, bukan reveal)
- Modify: `tests/test_dialog.py` — (regresi) alur 3aa → q07 tetap selesai

- [ ] **Step 1: Konfirmasi arah teks via ask_user**
- [ ] **Step 2: Edit data** — `node_truth_3aa` versi pasca-konfrontasi
- [ ] **Step 3: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 4: Commit** `fix+story: q07 pasca-3aa tidak ulangi reveal (G4f)`

### Task 9: B2 — payoff tematik cabang 3b

> Temuan: `node_truth_3b` ber-`end: true` — jalur gelap melewatkan `node_penutup` ("yang lemah dikorbankan untuk yang kuat").

**Keputusan default**: tambahkan `node_penutup_3b` — versi gelap dari penutup (narasi "Kau tahu polanya. Kau hanya memilih berada di sisi yang salah kali ini.") → `end: true`. Menjaga 3b tetap berbeda tanpa kehilangan beat tematik.

**Files:**
- Modify: `data/dialogs/dialogs_akademi.json` — `node_truth_3b` → `node_penutup_3b` → end
- Modify: `tests/test_dialog.py` — alur 3b mencapai penutup 3b

- [ ] **Step 1: Konfirmasi via ask_user** (mau payoff gelap atau biarkan tanpa penutup = keputusan desain)
- [ ] **Step 2: Edit data**
- [ ] **Step 3: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 4: Commit** `fix+story: payoff tematik cabang 3b (B2)`

### Task 10: G4a — spar "boleh kalah" (jalur loss)

> Temuan: `STORY_FASE1.md` "pemain bisa menang/kalah; kalah = dialog berbeda" vs implementasi hanya menang (`quest.py:77-81`); KO → respawn tanpa jalur loss.

**Keputusan default (minimal)**: kalah sparring ujian (q_akademi_03) **tetap** menyelesaikan quest dengan dialog berbeda (Gu Canghai menenangkan: "kalah pertama bukan kekalahan terakhir") — konsisten premis "tidak ada game over permanen", tanpa mengubah penalti KO (tetap berlaku). Implementasi: `notify_spar_loss(npc_id)` yang menyelesaikan objective `spar` dengan flag `spar_kalah=true`; dialog Gu Canghai entri kondisional flag itu.

**Files:**
- Modify: `src/engine/quest.py` — `notify_spar_loss`
- Modify: `src/engine/battle.py` — panggil `notify_spar_loss` saat KO dalam konteks spar
- Modify: `data/dialogs/dialogs_akademi.json` — entri kondisional pasca-kalah
- Modify: `data/quests/quests_akademi.json` — (opsional) reward lebih kecil saat kalah? **Default: sama** (sederhana)
- Modify: `tests/test_quest_dag.py` — kalah spar → quest selesai + flag
- Modify: `docs/ENGINE_ARCHITECTURE.md` §9.1 + `docs/STORY_FASE1.md` §1 (baris 19)

- [ ] **Step 1: Konfirmasi keputusan via ask_user** (kalah tetap selesai + dialog beda, vs retry wajib)
- [ ] **Step 2: Tulis failing test** — kalah spar → `q_akademi_03` selesai + `spar_kalah`
- [ ] **Step 3: Implementasi** quest + battle + dialog
- [ ] **Step 4: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 5: Update docs** STORY + ENGINE
- [ ] **Step 6: Commit** `feat: spar boleh kalah dengan dialog berbeda (G4a)`

---

## Fase C — Fitur baru (defer, dikerjakan terpisah)

### Task 11: B3/#13 — gating ingatan → opsi dialog (fitur baru)

> Temuan: `STORY_FASE1.md §3.1` "opsi dialog tertentu hanya muncul setelah ingatan terkait pulih" — engine tak punya tipe kondisi `memory`; nol dialog memakainya.

**Keputusan default**: tipe kondisi `memory_unlocked` di `dialog.py::_eval_condition` (cek `mem_id in state.memories`) — skala lebih besar, gabung dengan Task 7 (entri kondisional baru) bila mau. **Defer ke sprint terpisah** (sesuai prioritas list_bug).

- [ ] *(tidak dikerjakan dalam plan ini — buat plan terpisah bila disetujui)*

---

## Fase D — Hardening web opsional + sinkronisasi docs

### Task 12: K4 — lock server (defense-in-depth, opsional)

> Temuan: `web/app.py` `ThreadingHTTPServer` tanpa `threading.Lock`; busy flag frontend sudah menutup kasus satu-klien, lock server melindungi multi-request ter-skrip.

**Keputusan default**: tambah `threading.Lock` di `web/app.py` — `do_POST` aksi (new/load/action/save) ambil lock per request.

**Files:**
- Modify: `web/app.py` — lock di sekitar mutasi sesi; endpoint yang dimutasi saat ini: `POST /api/new|load|action` (catatan: `/api/save` sudah dihapus). `GET /api/tianyuan` juga membaca sesi — ikut ambil lock agar konsisten.
- Modify: `tests/test_web.py` — (opsional) dua request berurutan aman (regresi)

- [ ] **Step 1: Tambah lock** di handler POST
- [ ] **Step 2: Run** `python3 -m pytest tests/test_web.py -q` — hijau
- [ ] **Step 3: Commit** `fix: lock server web (K4 defense-in-depth)`

### Task 13: G3d — batasan lintas perangkat (dokumentasi)

> Temuan: `localStorage "arc-seen:<save>"` tidak ikut antar perangkat (konsekuensi keputusan K2). Fase 1 = lokal single-player → batasan diterima.

**Keputusan default**: tanpa perubahan kode — tulis catatan batasan di `docs/ENGINE_ARCHITECTURE.md` §12.5 dan `docs/DESIGN_SUMMARY.md` §8. Opsi backend (flag di save) ditunda.

- [ ] **Step 1: Update docs** (catatan batasan localStorage)
- [ ] **Step 2: Commit** `docs: catat batasan arc-summary per perangkat (G3d)`

### Task 14: Sinkronisasi dokumen dengan working tree

> Temuan: `list_bug.md` menulis "197 passed (192 + 5)" & tabel 9 fix — working tree sudah 201 test + batch H1/H2/H3/G4e/K1–K5/G4d yang tidak terdokumentasi.

**Files:**
- Modify: `docs/list_bug.md` — tabel status: tambah batch fix terlewat (H1/H2/H3/G4e/K1–K5/G4d), koreksi 197 → **201**, tandai G4d/K5 selesai, perbarui "Prioritas perbaikan" (coret B1/G4d/K5)
- Modify: `docs/ENGINE_ARCHITECTURE.md` §17 — status fitur + catatan batasan baru (H4, A1)
- Modify: `docs/DESIGN_SUMMARY.md` §8 — 197 → 201

- [ ] **Step 1: Update** `list_bug.md` (tabel status + prioritas)
- [ ] **Step 2: Update** `docs/ENGINE_ARCHITECTURE.md` + `docs/DESIGN_SUMMARY.md` (angka test)
- [ ] **Step 3: Verifikasi akhir** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 4: Commit** `docs: sinkronkan status bug & jumlah test (201)`

---

## Urutan eksekusi yang disarankan

1. **Fase A** (Task 1–5) — aman, bisa dikerjakan langsung tanpa konfirmasi; tiap task satu commit + validate + pytest.
2. **Fase B** (Task 6–10) — mulai dengan satu sesi ask_user untuk 5 keputusan desain sekaligus (world-facts, teks 3ab, q07 3aa, payoff 3b, spar kalah), lalu eksekusi berurutan.
3. **Fase D** (Task 12–14) — Task 14 (sinkronisasi docs) boleh dikerjakan kapan pun, idealnya sebelum Fase B agar status dokumen akurat saat konten berubah.
4. **Fase C** (Task 11) — tidak termasuk; buat plan terpisah bila disetujui.

**Kriteria selesai:** semua task Fase A/B/D selesai → `validate_data.py` exit 0, `pytest` hijau (jumlah test naik sesuai task), docs mencerminkan kode, tidak ada bug aktif tersisa selain yang sengaja di-defer (B3/#13, A2 optional, #9 manual).
