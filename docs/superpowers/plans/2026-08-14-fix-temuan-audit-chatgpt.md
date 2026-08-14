# Fix Temuan Audit ChatGPT — Bug Engine + Polish Web — Implementation Plan

> **Untuk agentic workers:** REQUIRED SUB-SKILL: Gunakan `superpowers:executing-plans` untuk implementasi task-by-task. Steps pakai checkbox (`- [ ]`).
>
> **Sumber**: Verifikasi 3 analisis ChatGPT terhadap kode nyata (2026-08-14) — 12 klaim engine terkonfirmasi (2 kritis masih valid di kode sekarang), 13 klaim estetika web terkonfirmasi, rekomendasi aset eksternal terverifikasi. Laporan lengkap & evaluasinya disepakati; keputusan user: **(1) lingkup = Engine + Web sekaligus; (2) ikuti GDD — tanpa animasi/audio** (DESIGN_SUMMARY §5 "statis, tanpa animasi" tetap dijunjung).
>
> **STATUS EKSEKUSI**: ⬜ belum dimulai. Baseline: `251 passed` · validate exit 0 · working tree bersih (`ccafebe`).
>
> **Goal**: (1) Menuntaskan 8 temuan engine terverifikasi — termasuk 2 kritis: hang EXP ranah tertinggi (A1) & sinkronisasi quest-dialog cabang 3aa (A2/A3); (2) Menghidupkan visual web dalam batas GDD — hierarchy, semantic color, hero stat, log/dialog treatment, responsive, aksesibilitas — **semua inline (CSS/SVG), tanpa dependency, tanpa animasi/audio**.

## Global Constraints

- Semua komentar, dokumen, dan teks test **Bahasa Indonesia**; istilah teknis ber-pinyin/hanzi.
- Wajib lolos setelah setiap task: `python3 tools/validate_data.py` (exit 0) **dan** `python3 -m pytest -q`. Urutan baku CI: validate → pytest.
- Run dari root repo. **Tidak menambah dependency** (stdlib-only; web tetap vanilla, tanpa CDN/framework).
- Konvensi commit repo: `feat:`, `test:`, `docs:`, `fix+test:`.
- Pola TDD untuk perubahan perilaku: tulis failing test dulu → verifikasi gagal → implementasi → hijau.
- Setiap perubahan skema data WAJIB disertai pembaruan validator (`tools/validate_data.py`) + `docs/ENGINE_ARCHITECTURE.md` (aturan emas: skema = kontrak).
- **Non-breaking**: kontrak `view()` lama tidak berubah (field baru opsional); save lama tetap dimuat; data quest/dialog existing tetap valid (validasi exit 0 tanpa edit data lama, kecuali task yang memang mengubah data).
- Prasyarat verifikasi per task: playthrough CLI 3 akademi (`tests/test_cli.py`) tetap hijau.
- **Keputusan desain baru wajib konfirmasi user** (pola fix-sisa-bug Fase B) — task yang butuh konfirmasi ditandai ⚠️.

---

## FASE 1 — ENGINE (A1–A8)

### Task A1: Hang EXP di ranah tertinggi (CRITICAL — P0)

> Kondisi sekarang: `cultivation.py::gain_exp` — `while state.player.exp >= exp_next`: kurangi exp, panggil `_level_up`. Di ranah tertinggi, `_breakthrough` (line 57-67) tidak menemukan ranah berikutnya → level di-reset ke maks → loop terus (bukan infinite matematis, tapi **hang praktis**: exp 1e9 ≈ 19 juta iterasi × log append). Terverifikasi: `timeout 10` → exit 124.

**Files:**
- Modify: `src/engine/cultivation.py` — `gain_exp` berhenti saat puncak ranah; `_breakthrough` memberi sinyal "max"
- Modify: `tests/test_cultivation.py` — test baru (TDD)
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §9.1 catatan puncak ranah

**Desain:**
- `_breakthrough` mengembalikan `bool` (True = ranah naik, False = sudah puncak).
- `gain_exp`: dalam `while`, jika `_level_up` tidak menaikkan level (puncak), **hentikan loop dan cap** `exp = min(exp, exp_next - 1)` + log `[Sistem] Kau di puncak ranah — exp tertahan.` → exp tidak hilang sia-sia, tidak hang, tidak loop.
- Alternatif yang dipertimbangkan & ditolak: buang exp berlebih (rugi pemain) / raise error (crash) — cap + log adalah yang paling adil & aman.

- [ ] Step 1: Tulis failing test — `test_cultivation.py`: `gain_exp` besar (mis. 10_000_000) di ranah tertinggi & level maks → selesai cepat (< 0.5 detik), level tidak berubah, exp di-cap, ada log puncak
- [ ] Step 2: Run — verifikasi gagal (hang/test timeout)
- [ ] Step 3: Implementasi `_breakthrough` → bool + `gain_exp` cap
- [ ] Step 4: Run test + suite penuh + playthrough CLI
- [ ] Step 5: Docs §9.1 + commit `fix+test:`

**Kriteria selesai:** test baru hijau cepat; suite penuh hijau; playthrough CLI hijau; validate exit 0.

---

### Task A2+A3: Sinkronisasi quest-dialog — objective `talk` + lapisan "required node" (HIGH — P0)

> Kondisi sekarang: `quest.py::notify_dialog_ended` (line 75-83) hanya cek `kind == "talk"` + `npc_id` — tidak peduli node/outcome. Akibat (terverifikasi): saat quest `q_akademi_3aa` aktif, bicara ke Penatua → `dlg_penatua.start = node_umum` (generik) → quest selesai → `branch_3aa` baru diset → konfrontasi baru tersedia **setelah** quest selesai. Naratif 3aa salah urutan. Test `test_dialog.py:26` **mengunci perilaku bug** sebagai expected (A4 — diperbaiki di task ini juga).
>
> Kabar baik (temuan verifikasi): `dialog.py::_resolve_entry` (line 79-84) **sudah** memilih node kondisional pertama di level atas dialog. Lapisan baru tinggal: quest tahu node mana yang wajib dimainkan & dialog bisa dipaksa mulai dari node tertentu.

**Files:**
- Modify: `src/engine/quest.py` — `notify_dialog_ended(npc_id, node_id)` cek objective `talk` field baru `node`/`nodes` (node wajib); `notify_dialog_ended` juga menerima `node_id` terakhir yang dimainkan
- Modify: `src/engine/dialog.py` — `start(dialog_id, forced_node=None)` → `_resolve_entry` pakai `forced_node` bila ada; simpan `self.node_id` untuk dilaporkan
- Modify: `src/engine/session.py` — `_talk` baca objective quest aktif (`talk` + `start_node`) → teruskan ke `dialog.start`; `_dialog_choice` saat dialog berakhir teruskan `dialog.node_id` ke `quest.notify_dialog_ended(npc_id, node_id)`
- Modify: `tools/validate_data.py` — aturan 4 (`_check_quests`): objective `talk` dengan `node`/`nodes`/`start_node` wajib merujuk node yang **ada di dialog NPC tsb** (cek `dialog(id).nodes`)
- Modify: `data/quests/quests_akademi.json` — `q_akademi_3aa.objective` → `{"kind":"talk","npc":"npc_penatua","node":"node_konfrontasi","start_node":"node_konfrontasi","target":1}`
- Modify: `data/dialogs/dialogs_akademi.json` — `dlg_penatua` tambah node kondisi baru: `node_konfrontasi` condition = `quest_active q_akademi_3aa` **atau** flag `branch_3aa` (sehingga konfrontasi muncul saat quest berjalan **dan** sesudahnya); pastikan `node_konfrontasi` pertama dalam urutan JSON yang kondisinya bisa benar
- Modify: `tests/test_quest_dag.py` / `tests/test_dialog.py` — **tulis ulang** `test_konfrontasi_pilihan_efek_beda` (bug-lock → perilaku benar) + test baru: saat quest 3aa aktif, dialog = `node_konfrontasi`, quest selesai setelah node itu dimainkan; quest talk tanpa `node` tetap perilaku lama (non-breaking)
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §5.1/§5.2 (skema objective `talk` + node), §7 (dialog forced node)

**Interfaces:**
- Consumes: objective `talk` field opsional `node` (str) / `nodes` (list[str]) / `start_node` (str); kondisi dialog `quest_active`.
- Produces: quest `talk` selesai hanya bila node wajib dimainkan; dialog bisa dipaksa mulai dari node; validator menolak node yang tidak ada di dialog target.

**Desain:**
- Skema (non-breaking, opsional): `objective.talk` → `"node": "node_x"` atau `"nodes": ["a","b"]` = node yang wajib dimainkan agar quest selesai; `"start_node": "node_x"` = dialog dipaksa mulai dari node ini saat quest aktif (mengalahkan `start` & kondisi entry).
- Semantik selesai: `notify_dialog_ended(npc_id, node_id)` → jika objective punya `node`/`nodes`, quest selesai hanya jika `node_id in (node/nodes)`; jika tidak punya, perilaku lama (target talk).
- `dialog.start(dialog_id, forced_node)`: `forced_node` dipakai langsung bila ada di `nodes` (jika tidak ada → fallback `_resolve_entry` + log error tidak crash).
- Data 3aa: `start_node` membuat dialog Penatua terbuka langsung di `node_konfrontasi` saat quest aktif; condition entry `quest_active q_akademi_3aa` membuat konfrontasi juga terpilih via `_resolve_entry` untuk kunjungan berikutnya (flag `branch_3aa` diset saat quest selesai → tetap terpilih sesudahnya).
- **A4 ikut terselesaikan**: test lama yang mengunci bug ditulis ulang menjadi test yang menegakkan naratif benar.

- [ ] Step 1: Tulis failing test — quest `talk` dengan `node`: selesai hanya bila node benar; `start_node` memaksa dialog mulai dari node itu; test 3aa baru: saat quest aktif → dialog = `node_konfrontasi` (bukan `node_umum`)
- [ ] Step 2: Run — verifikasi gagal (quest selesai lewat node salah / dialog mulai node_umum)
- [ ] Step 3: Implementasi `quest.py` + `dialog.py` + `session.py`
- [ ] Step 4: Validator aturan baru + data quest/dialog 3aa
- [ ] Step 5: Tulis ulang test bug-lock + playthrough CLI 3 akademi hijau
- [ ] Step 6: Docs §5.1/§5.2/§7 + commit `feat+test:` (perubahan skema data = satu commit dengan validator)

**Kriteria selesai:** reproduksi bug lama → perilaku benar (saat quest 3aa aktif, dialog = konfrontasi; quest selesai setelah node konfrontasi); quest talk existing tanpa `node` tidak berubah; validator tolak `node` tak ada di dialog; suite + playthrough hijau.

---

### Task A5: `advance_time` overshoot (MEDIUM — P1)

> Kondisi sekarang: `quest.py:206` — `elapsed_hours >= required_hours AND state.hour >= target_hour`. Overshoot (tunggu 30 jam → Hari 3 01:00) → `hour >= 20` gagal → quest molor hampir 1 hari. Terverifikasi.

**Files:**
- Modify: `src/engine/quest.py` — `advance_time_target_met`: hitung target absolut `(start_day + day_offset) * 24 + target_hour`, selesai jika `day*24 + hour >= target_abs` (overshoot otomatis memenuhi)
- Modify: `tests/test_quest_dag.py` — test baru: overshoot (lewati target) → selesai (TDD)
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §5.1 objective advance_time

- [ ] Step 1: Failing test — advance_time: start Hari 1 19:00, target day_offset 1 hour 20 → tunggu 30 jam (Hari 3 01:00) → quest selesai
- [ ] Step 2: Run — gagal (belum selesai)
- [ ] Step 3: Implementasi rumus target absolut
- [ ] Step 4: Suite + playthrough hijau + docs + commit `fix+test:`

**Kriteria selesai:** overshoot menyelesaikan quest; kasus dalam window tetap selesai; non-breaking.

---

### Task A6: `skill_pool` hanya elemen pertama (LATENT — P2)

> Kondisi sekarang: `loader.py:110` — `pool = a.get("skill_pool", [""])[0]` → pool kedua tak pernah dibaca. Terverifikasi.

**Files:**
- Modify: `src/loader.py` — `player_techniques`: loop semua prefix di `skill_pool` (list), union + dedup
- Modify: `tests/` (test loader/teknik) — test baru: `skill_pool` 2 elemen → teknik dari kedua pool (TDD)
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §5.4

- [ ] Step 1: Failing test — akademi dengan `skill_pool: ["tek_elemen_*","tek_universal_*"]` → dapat teknik dari keduanya
- [ ] Step 2: Implementasi + hijau
- [ ] Step 3: Docs + commit `fix+test:`

**Kriteria selesai:** semua elemen pool diproses; pool 1 elemen (data existing) tidak berubah.

---

### Task A7: Objective `defeat` main quest tanpa filter (LATENT — P2)

> Kondisi sekarang: `quest.py:124-126` — main quest `defeat` selesai atas musuh apa pun; side quest sudah benar (filter `enemies` + `target`). Terverifikasi. Fase 1 tidak memakai main `defeat` → murni hardening untuk arc berikutnya.

**Files:**
- Modify: `src/engine/quest.py` — `notify_battle_won(defeated_enemy_ids)`: main quest `defeat` ikuti pola side quest — filter `enemies` (bila ada) + `target` count
- Modify: `tests/test_quest_dag.py` — test baru (TDD)
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §5.1

- [ ] Step 1: Failing test — main `defeat` dengan `enemies:["boss_x"]`: kalahkan musuh lain → tidak selesai; kalahkan boss_x → selesai
- [ ] Step 2: Implementasi + hijau
- [ ] Step 3: Docs + commit `fix+test:`

**Kriteria selesai:** main `defeat` memverifikasi target; tanpa `enemies` → perilaku lama (non-breaking).

---

### Task A8: Hilangkan fallback hardcode hunt (DEBT — P2)

> Kondisi sekarang: `session.py:335,348,353,374,380` — fallback literal `"loc_wilayah_berburu"`, `["eno_serigala_qi","eno_babi_hutan"]`, `"eno_raja_serigala"`, `"material_herba"` padahal `config.world.hunt` sudah lengkap. Terverifikasi.

**Files:**
- Modify: `src/engine/session.py` — `_hunt`/`_search`: ambil dari `config.world.hunt` **tanpa fallback literal**; jika config tidak punya `hunt` → log sistem "Berburu belum tersedia" (data-driven murni)
- Modify: `tests/test_session.py` — test baru: config hunt tanpa field → perilaku aman; config hunt lengkap → berburu normal (TDD)
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §5.6 (catatan: tanpa fallback arc-1)

- [ ] Step 1: Failing test — hapus sementara key dari config → tidak crash, ada log penolakan
- [ ] Step 2: Implementasi (hapus literal, baca config) + hijau
- [ ] Step 3: Docs + commit `fix+test:`

**Kriteria selesai:** 0 literal id konten arc-1 di engine hunt; data existing (config lengkap) tidak berubah perilakunya.

---

## FASE 2 — WEB POLISH (B1–B9, C1–C4) — tanpa animasi/audio, tanpa dependency

> Prinsip (keputusan user): semua efek **inline** (CSS gradient, border, glyph, SVG inline) — **tidak ada file aset eksternal, tidak ada CDN, tidak ada animasi/audio** (GDD §12.5 + DESIGN_SUMMARY §5). File yang tersentuh: `web/static/style.css`, `web/static/app.js`, `web/static/index.html`; `web/app.py` hanya bila view/context berubah (dicek per task).

### Task B8: Aksesibilitas keyboard — `:focus` (P1)

> Kondisi sekarang: grep `:focus` di `style.css` = **0 hasil** — keyboard accessibility tidak ada. Terverifikasi.

**Files:**
- Modify: `web/static/style.css` — `:focus-visible`/`:focus` outline emas konsisten untuk tombol, choice, link, input, modal (ganti `outline: none` bila ada); focus trap ringan untuk modal (JS: simpan focus sebelum buka, kembalikan saat tutup)
- Modify: `web/static/app.js` — `showModal`/`closeModal`: simpan/restore focus + fokus elemen pertama modal
- Modify: `tests/test_web.py` — test: markup modal punya `tabindex`/fokus awal (bila feasible; unit sederhana)

- [ ] Step 1: Audit `outline: none` / elemen interaktif di CSS
- [ ] Step 2: Implementasi focus styles + focus management modal
- [ ] Step 3: Test web + suite hijau + commit `feat+test:`

**Kriteria selesai:** navigasi keyboard terlihat jelas (outline emas); modal fokus ke elemen pertama & restore focus saat tutup.

---

### Task B9: Feedback loading (P1)

> Kondisi sekarang: `app.js` — `busy` mencegah double-click tapi **tanpa indikator visual** → tombol terasa rusak saat koneksi lambat. Terverifikasi.

**Files:**
- Modify: `web/static/app.js` — `act`/`actShop`: saat `busy`, tombol sumber di-disable + teks `Memproses…` (set `disabled` attr + class `is-loading`); sembunyikan setelah selesai
- Modify: `web/static/style.css` — `.is-loading` (opacity/pointer-events, **tanpa animasi** — sesuai GDD)
- Modify: `tests/test_web.py` — test ringan bila feasible

- [ ] Step 1: Implementasi `busy` → disabled + label
- [ ] Step 2: Test + commit `feat:`

**Kriteria selesai:** saat aksi berjalan, tombol terlihat non-aktif dengan teks "Memproses…"; tanpa animasi.

---

### Task B1+B2: Visual hierarchy + semantic color (P2)

> Kondisi sekarang: 3 kolom memakai 1 bahasa visual (bg-panel + heading gold `stat-title`); gold dipakai untuk heading/tombol/log system/quest/border sekaligus (B1/B2 terverifikasi).

**Files:**
- Modify: `web/static/style.css` — split semantic color: gold = kultivasi/utama (realm, teknik, judul), blue = pemain/roh/pengetahuan, red = bahaya/musuh, green = sukses/healing, cream = narasi, gray = sekunder; panel samping diberi treatment lebih redup (border lebih tipis, heading lebih kecil), kolom tengah (story) paling menonjol (bg sedikit berbeda / border emas halus)
- Modify: `web/static/app.js` — kelas warna per jenis nilai (sudah ada `stat-value.gold/red/blue` — perluas + konsisten)
- Modify: `tests/test_web.py` — cek konteks tidak berubah (non-breaking)

- [ ] Step 1: Definisikan semantic color mapping di `:root` (komentar per warna)
- [ ] Step 2: Terapkan ke panel kiri/tengah/kanan + log + tombol
- [ ] Step 3: Verifikasi visual manual (jalankan web) + suite hijau + commit `feat:`

**Kriteria selesai:** hierarki visual jelas (story > keputusan > state > quest/inventory > sekunder); gold tidak lagi jadi satu-satunya "special"; kontrak view/context tidak berubah.

---

### Task B3: Realm jadi hero stat + progress (P2)

> Kondisi sekarang: `app.js:114` — `statRow("Ranah", Lv.X)` = 1 row kecil; tidak ada progress bar. Terverifikasi.

**Files:**
- Modify: `web/static/app.js` — panel kiri: blok hero Ranah (nama ranah + level, besar) + progress exp (`exp/exp_next`) sebagai **bar CSS statis** (div lebar %, tanpa animasi)
- Modify: `web/static/style.css` — `.realm-hero`, `.progress-track`/`.progress-fill` (statis)

- [ ] Step 1: Implementasi hero realm + progress statis
- [ ] Step 2: Verifikasi + commit `feat:`

**Kriteria selesai:** ranah tampil sebagai info terbesar panel kiri dengan bar progress exp; tanpa animasi.

---

### Task B4: Log — perlakuan speaker & separator scene (P2)

> Kondisi sekarang: `app.js:177-178` — log = div polos per entry (`log-entry log-${type}`); 5 warna sudah ada tapi tanpa struktur. Terverifikasi.

**Files:**
- Modify: `web/static/app.js` — render log: tipe `narration` = paragraf dengan `text-indent`/jarak antar-scene (separator `scene-gap`); entry ber-speaker (dialog) ditampilkan `**Nama:** teks` dengan nama diberi kelas `log-speaker`
- Modify: `web/static/style.css` — `.log-speaker` (gold/blue per tipe), `.scene-gap` (margin + divider tipis)

- [ ] Step 1: Implementasi render log + CSS
- [ ] Step 2: Verifikasi + commit `feat:`

**Kriteria selesai:** log terlihat seperti narasi interaktif (speaker menonjol, scene terpisah) — tanpa mengubah isi view.

---

### Task B5: Dialog jadi "story card" (P2)

> Kondisi sekarang: `.interact-box` (border 1px + radius 6 + padding) generik; speaker header sudah ada (`app.js:308`) tapi tidak menonjol. Terverifikasi (klaim ChatGPT "tidak ada indikasi" berlebihan — speaker sudah ada).

**Files:**
- Modify: `web/static/style.css` — `.interact-box` treatment story card: bg sedikit berbeda dari panel lain, border kiri emas (accent 3px), radius lebih besar, `.dialog-speaker` lebih tegas (huruf kapital, letter-spacing, warna per tipe)
- Modify: `web/static/app.js` — kelas speaker per tipe (narration/NPC/pemain)

- [ ] Step 1: Implementasi story card + speaker tegas
- [ ] Step 2: Verifikasi + commit `feat:`

**Kriteria selesai:** dialog terasa pusat pengalaman (berbeda dari panel statistik), tetap teks murni.

---

### Task B6: Responsive mobile naratif (P2)

> Kondisi sekarang: `style.css:324-328` — mobile hanya stack 3 kolom → halaman sangat panjang. Terverifikasi.

**Files:**
- Modify: `web/static/style.css` — breakpoint: mobile = story pertama, lalu pilihan, quest, lalu drawer untuk inventory/memory (panel kanan jadi tombol "Inventori/Quest" yang membuka panel overlay — **tanpa animasi**, toggle class)
- Modify: `web/static/app.js` — toggle drawer mobile (show/hide class)

- [ ] Step 1: Implementasi layout mobile naratif
- [ ] Step 2: Verifikasi (browser responsive) + commit `feat:`

**Kriteria selesai:** mobile menampilkan story → choices → quest terlebih dulu; inventory/memory di drawer; desktop tidak berubah.

---

### Task B7: Title screen + ornamen xianxia (P2)

> Kondisi sekarang: `index.html:12-21` — title 72px + gold sudah elegan tapi kosong (tanpa emblem/ornamen). Terverifikasi.

**Files:**
- Modify: `web/static/index.html` — tambah **SVG inline** (divider 云纹, corner ornament, seal) di title-box — tanpa file eksternal
- Modify: `web/static/style.css` — `.ornament` (opacity rendah, posisi), judul diberi lapisan gradient tipis (tetap teks)

- [ ] Step 1: Buat 2-3 SVG ornament inline sederhana (divider, corner, seal)
- [ ] Step 2: Pasang di title screen + section divider
- [ ] Step 3: Verifikasi + commit `feat:`

**Kriteria selesai:** title screen berornamen xianxia halus; identitas visual menguat tanpa gambar eksternal.

---

### Task C4: Background lokasi data-driven (P2 — perubahan skema ⚠️)

> Kondisi sekarang: `locations.json` hanya `{id, name, description, connections, is_safe}` — tanpa field visual. Usulan ChatGPT: field `background` per lokasi. **Keputusan plan**: gunakan **tipe atmosfer enum** (data-driven, tanpa file gambar): `"ambience": "mist" | "forest" | "academy" | "night" | "market"` → dipetakan ke CSS gradient/pattern statis.

**Files:**
- Modify: `data/locations/locations_akademi.json` (atau `data/locations.json` — cek nama file aktual) — tambah field `ambience` per lokasi (opsional; default `"academy"`)
- Modify: `tools/validate_data.py` — aturan 14: `ambience` bila ada harus ∈ enum yang didefinisikan di config
- Modify: `data/config.json` — `world.ambiences`: daftar enum → deskripsi (mis. `{"academy": "kampus", ...}`) — sumber kebenaran untuk validator
- Modify: `src/engine/session.py` (view) atau `web/app.py` (`_context`) — teruskan `ambience` lokasi saat ini (opsional field baru, non-breaking)
- Modify: `web/static/app.js` — kelas `ambience-<x>` di body/kolom tengah
- Modify: `web/static/style.css` — gradient statis per ambience (tanpa gambar, tanpa animasi)
- Modify: `tests/test_validator.py` / `tests/test_web.py` — test baru (TDD)
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §5.6/§12.4 (kontrak view + skema lokasi)

- [ ] Step 1: Failing test validator — `ambience` tak dikenal → ditolak
- [ ] Step 2: Config enum + validator + data lokasi
- [ ] Step 3: View/context teruskan `ambience` + CSS gradient + test web
- [ ] Step 4: validate + suite + playthrough hijau + docs + commit `feat+test:`

**Kriteria selesai:** tiap lokasi punya atmosfer visual statis (gradient) dari data; validator tolak enum tak dikenal; kontrak view non-breaking (field opsional).

---

### Task C1-C3 (font self-host, icon Lucide, texture aset) — DEFER / OPSIONAL

> Keputusan plan: **tunda** C1 (font self-host) & C3 (texture file) — keduanya butuh **file aset eksternal** (font OFL, webp/png) yang melanggar prinsip "tanpa aset tambahan" untuk batch ini; C2 (icon system) sebagian tercakup di B1-B7 lewat glyph/svg inline. Bila user ingin lanjut setelah Fase 2, buat plan terpisah (butuh keputusan penyimpanan aset + lisensi).

---

## VERIFIKASI AKHIR (setelah semua task)

- [ ] `python3 tools/validate_data.py` exit 0
- [ ] `python3 -m pytest -q` — seluruh suite hijau (baseline 251 → bertambah)
- [ ] `python3 -m pytest tests/test_cli.py -q` — playthrough CLI 3 akademi hijau (non-breaking)
- [ ] Jalankan `python3 web/app.py` + cek visual manual: title screen, panel kiri (hero realm), log, dialog, responsive mobile, fokus keyboard
- [ ] Grep `:focus` > 0 · grep animasi/audio (`transition`, `@keyframes`, `<audio`, `.mp3`) = 0 (keputusan GDD dijaga)
- [ ] Update `README.md`/`PROJECT.md`/`CHANGELOG.md` — angka test baru + entri batch
- [ ] Update `docs/list_bug.md` — Batch 6: A1–A8, B1–B9, C4 (masing-masing ✅ / defer dicatat)
- [ ] Commit penutup `docs:`

---

## RIWAYAT KEPUTUSAN USER (dikonfirmasi via ask_user)

1. **Lingkup**: Engine + Web sekaligus (2 fase dalam 1 plan).
2. **GDD**: Ikuti keputusan terkunci — **tanpa animasi/audio**; polish = font/icon/texture/ornamen/hierarchy dalam batas "text + panel".
3. **Fix 3aa**: Lapisan **"required node" penuh (A3)** — skema quest `talk` + `node`/`start_node`, quest selesai hanya jika node wajib dimainkan.
4. **C1-C3 aset eksternal**: Defer ke plan terpisah (butuh keputusan aset).
