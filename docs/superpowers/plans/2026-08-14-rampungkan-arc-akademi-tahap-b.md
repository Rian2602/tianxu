# Rampungkan Tahap B FULL — Engine Adaptif (Arc Baru = Data Saja) — Implementation Plan

> **Untuk agentic workers:** REQUIRED SUB-SKILL: Gunakan `superpowers:subagent-driven-development` (disarankan) atau `superpowers:executing-plans` untuk implementasi task-by-task. Steps pakai checkbox (`- [ ]`).
>
> **Sumber**: audit status Arc Akademi & kesiapan engine adaptif (2026-08-14) — keputusan user: **sebelum arc berikutnya, Arc Akademi harus rampung penuh dan engine harus memuat fitur adaptif sehingga arc baru = data saja, tanpa mengubah script engine.** Tahap A (DoD §11.2 #1 + 4 keputusan playtest §17) selesai (`b2388c7`, `4907c7b`, `1c593f4`). Tahap ini = Tahap B: menghilangkan sisa hardcode arc-1 dari engine.
>
> **STATUS EKSEKUSI (2026-08-14)**: ✅ **SELESAI** — Task B1 (arc_summary data-driven), B2 (fallback safe-location), B3 (banner CLI generik), B4 (teknik lintas akademi). Verifikasi: validate exit 0 + **238 passed** (+7 test); prasyarat grep 0 hardcode arc-1 di `src/` ✓. Deviasi: validator `_load_all` memuat `config.json` paling awal (aturan 13 butuh `config.arcs`).

**Goal:** Menghilangkan seluruh hardcode arc-1 dari engine (`src/`) sehingga penambahan arc berikutnya (Sekte/Kekaisaran/Final) cukup lewat data:
- **B1**: `arc_summary` (layar penutup arc) data-driven via `config.json → arcs` — hapus `"q_akademi_07"`, label cabang (`branch_3aa`…), title, teaser, dan angka ingatan hardcode dari `session.py::view()`.
- **B2**: fallback lokasi aman saat KO data-driven — hapus `"loc_asrama"` dari `battle.py::_ko`.
- **B3**: banner penutup arc di CLI generik — hapus flag literal `"arc_akademi_selesai"` dari `cli.py` (trigger via `arc_summary`).
- **B4**: scaffolding teknik lintas akademi (GDD §5.2 — skill akademi lain terbuka di arc berikutnya) — kolom opsional `unlock_arc` di `techniques.csv` + `player_techniques` menerima quest selesai; tanpa data baru, perilaku sekarang identik (non-breaking).

**Architecture:** Semua perubahan = engine membaca dari data (config/CSV), tidak ada literal arc-1 yang tersisa di `src/` maupun `web/`. `arcs` ditaruh di `config.json` (konsisten dengan `academies`/`world` yang juga konten di config, bukan file terpisah) → validator cukup **memperluas aturan 7** (config.json), jumlah aturan §14 tetap 16 (menghindari sinkronisasi jumlah aturan di AGENTS.md/PROJECT). Skema `unlock_arc` opsional → validator aturan 13 diperluas. Web tidak berubah (app.js sudah render `arc_summary` generik; `arc-seen` localStorage per-save tetap).

**Tech Stack:** Python 3.12, stdlib-only, pytest. Tidak ada lint/typecheck.

## Global Constraints

- Semua komentar, dokumen, dan teks test **Bahasa Indonesia**; istilah teknis ber-pinyin/hanzi.
- Wajib lolos setelah setiap task: `python3 tools/validate_data.py` (exit 0) **dan** `python3 -m pytest -q`. Urutan baku CI: validate → pytest.
- Run dari root repo. Tidak menambah dependency.
- Konvensi commit repo: `feat:`, `test:`, `docs:`, `fix+test:`.
- Pola TDD untuk perubahan perilaku: tulis failing test dulu → verifikasi gagal → implementasi → hijau.
- Setiap perubahan skema data (kolom CSV baru, key config baru) WAJIB disertai pembaruan validator.
- **Prasyarat verifikasi**: setelah B1–B3, jalankan `grep -rn "q_akademi\|AKHIR ARC\|loc_asrama\|arc_akademi_selesai" src/ web/ --include=*.py --include=*.js` → **0 hasil** (hardcode arc-1 hilang dari kode).

---

### Task B1: `arc_summary` data-driven (`config.arcs`)

> Kondisi sekarang: `session.py:529-554` hardcode `"q_akademi_07" in s.completed_quests`, 4 label cabang (`branch_3aa/3ab/3b/3c`), title `"AKHIR ARC 1: AKADEMI CHANGFENG"`, teaser arc-1, dan `f"{len(s.memories)}/4"` (angka 4 hardcode). Quest data sudah punya `arc: "akademi"` per quest (terverifikasi) — metadata arc (title/teaser/branches) yang belum data-driven.

**Files:**
- Modify: `data/config.json` — tambah key `arcs` (list)
- Modify: `src/engine/session.py` — `view()` baca config arcs
- Modify: `tools/validate_data.py` — `_check_config` perluas aturan 7
- Modify: `tests/test_session.py` — adaptasi + test baru
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §5.6/§9.2/§17 (arc_summary dari config arcs)

**Interfaces:**
- Consumes: `registry.config["arcs"]` (baru), `state.completed_quests`, `state.flags`, `len(state.memories)`.
- Produces: `view()["arc_summary"]` dengan struktur yang **sama persis** seperti sekarang (kontrak view tak berubah — web/CLI tidak disentuh).

**Skema `config.arcs` (default, data arc akademi):**
```json
"arcs": [
  {
    "id": "akademi",
    "final_quest": "q_akademi_07",
    "title": "AKHIR ARC 1: AKADEMI CHANGFENG",
    "teaser": "Kebenaran di balik Penatua An telah terkuak. Namun bayang-bayang masa lalu Long Tianxu dan intrik Sekte Regional baru saja dimulai...",
    "memories_total": 4,
    "branches": {
      "branch_3aa": "Cabang 3AA — Konfrontasi Terbuka Penatua An",
      "branch_3ab": "Cabang 3AB — Penyelidikan Diam-Diam Mo Yun",
      "branch_3b": "Cabang 3B — Memeras Zhou Yan & Mengambil Keuntungan",
      "branch_3c": "Cabang 3C — Berdiam Diri & Menjaga Diri"
    }
  }
]
```

**Logika `view()` baru (generik):** iterasi `config.arcs` **dari akhir** (urutan config = kronologis arc: akademi → sekte → …) — ambil arc **terakhir** yang `final_quest ∈ completed_quests` (arc paling baru selesai; setelah arc 2 selesai, summary menampilkan arc 2, bukan arc 1). Branch label = kunci `branches` pertama yang flag-nya ada di `state.flags` (fallback `"Tidak Diketahui"`); `memories_unlocked = f"{len(s.memories)}/{arc.memories_total}"`. Bila tidak ada arc selesai → `arc_summary = None` (perilaku sama).

- [ ] **Step 1: Tulis failing test** — `tests/test_session.py::test_view_arc_summaries` diadaptasi agar memakai data nyata + test baru: (a) arc_summary tetap terisi dengan label yang sama saat `q_akademi_07` selesai (guard: kontrak view tidak berubah); (b) arc_summary **None** saat quest asing (mis. `"q_sekte_final"` dummy) di-completed tanpa arc di config → tidak crash dan None; (c) `memories_unlocked` sesuai `arc.memories_total` dari config (bukan hardcode 4); (d) **arc terakhir** di config yang selesai yang menang (simulasi 2 arc selesai → summary arc kedua)
- [ ] **Step 2: Run** test — verifikasi gagal (view masih hardcode)
- [ ] **Step 3: Implementasi config** — tambah `arcs` di `data/config.json` (skema di atas, konten persis sama dengan literal lama)
- [ ] **Step 4: Implementasi `session.py::view()`** — loop `config.arcs`; bangun summary generik; hapus semua literal arc-1
- [ ] **Step 5: Validator aturan 7** — `_check_config`: tiap arc punya `id` unik, `final_quest` ada di quest, `title`/`teaser` string non-kosong, `memories_total` int > 0, `branches` dict non-kosong
- [ ] **Step 6: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 7: Prasyarat verifikasi** — `grep -rn "q_akademi_07\|AKHIR ARC" src/ --include=*.py` → hanya comment/referensi valid; tidak ada literal di logika
- [ ] **Step 8: Docs** — ENGINE §5.6/§9.2/§17: arc_summary dibaca dari `config.arcs` (arc id `akademi`), skema dicontohkan; §14 aturan 7 diperluas (arcs)

---

### Task B2: Fallback lokasi aman data-driven

> Kondisi sekarang: `battle.py:354` — `safe = self.state.last_safe_location or "loc_asrama"`. Bila save arc-2 tak punya `loc_asrama`, KO akan crash/respawn di lokasi tak valid.

**Files:**
- Modify: `data/config.json` — `world.safe_fallback_location`
- Modify: `src/engine/battle.py` — `_ko` baca config lalu data lokasi
- Modify: `tools/validate_data.py` — aturan 7 (referensi lokasi valid + `is_safe`)
- Modify: `tests/test_battle.py` — test baru
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §8.1 catatan KO respawn

**Interfaces:**
- Consumes: `registry.config["world"]["safe_fallback_location"]` (baru, opsional), `registry.locations` (fallback: lokasi `is_safe` pertama dari data).
- Produces: `_ko` memilih lokasi respawn: `last_safe_location` → `config.world.safe_fallback_location` → lokasi `is_safe` pertama di data → error validator (tidak mungkin, karena validator memastikan ≥1 safe location + fallback valid).

- [ ] **Step 1: Tulis failing test** — `tests/test_battle.py`: (a) KO tanpa `last_safe_location` → respawn di `config.world.safe_fallback_location` (set ke `loc_asrama` di data nyata); (b) hapus key `safe_fallback_location` → fallback ke lokasi `is_safe` pertama dari data (bukan hardcode string)
- [ ] **Step 2: Run** — verifikasi gagal (masih `or "loc_asrama"`)
- [ ] **Step 3: Implementasi config** — `world.safe_fallback_location: "loc_asrama"`
- [ ] **Step 4: Implementasi `battle.py::_ko`** — prioritas: `last_safe_location` → config → lokasi safe pertama data (guard: lokasi hasil selalu ada di registry)
- [ ] **Step 5: Validator aturan 7** — `safe_fallback_location` (bila ada) harus merujuk lokasi yang ada dan `is_safe: true`
- [ ] **Step 6: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 7: Prasyarat verifikasi** — `grep -rn "loc_asrama" src/ --include=*.py` → 0 hasil
- [ ] **Step 8: Docs** — ENGINE §8.1: prioritas lokasi respawn KO

---

### Task B3: Banner penutup arc CLI generik

> Kondisi sekarang: `cli.py:312` — `if not arc_ended and "arc_akademi_selesai" in session.state.flags:`. Flag ini di-set data quest (on_complete q07) — tapi engine CLI tak boleh bergantung nama flag arc-1; trigger yang benar = `view().arc_summary` (sudah data-driven dari B1).

**Files:**
- Modify: `src/cli.py` — kondisi banner
- Modify: `tests/test_cli.py` — test tambahan (opsional; playthrough existing sudah assert banner)
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §9.2 catatan CLI

**Interfaces:**
- Consumes: `session.view()["arc_summary"]` (bukan flag).
- Produces: banner ANSI emas sama persis; `arc_ended` tetap mencegah tampil berulang.

- [ ] **Step 1: Refactor `cli.py`** — ganti kondisi dengan `if not arc_ended:` lalu `v_after = session.view()` dan `if v_after.get("arc_summary"): arc_ended = True; ...` (hapus literal flag; `arc_ended = True` dipindah **setelah** cek arc_summary agar arc tanpa summary tidak terkunci selamanya). view() murni baca state — dobel panggilan aman
- [ ] **Step 2: Run** `python3 -m pytest tests/test_cli.py -q` — playthrough 3 akademi + full-commands tetap hijau (banner masih tampil)
- [ ] **Step 3: Prasyarat verifikasi** — `grep -rn "arc_akademi_selesai" src/ --include=*.py` → 0 hasil (flag tetap boleh ada di data/dialogs & data/quests — itu data arc akademi, bukan engine)
- [ ] **Step 4: Docs** — ENGINE §9.2: banner CLI dipicu `arc_summary` dari config arcs

---

### Task B4: Scaffolding teknik lintas akademi (`unlock_arc`)

> GDD §5.2: skill akademi lain dibuka di arc berikutnya. Kondisi sekarang: `loader.py::player_techniques(academy, realm)` hanya dari `skill_pool` akademi pilihan — tidak ada mekanik teknik lintas akademi. **Scaffolding data-driven, non-breaking**: kolom opsional `unlock_arc` di `techniques.csv`; teknik dengan `unlock_arc` terisi ikut tampil untuk pemain akademi mana pun bila quest final arc itu sudah selesai. Tanpa data baru, perilaku identik (kolom kosong untuk semua teknik sekarang). **Catatan scope**: B4 hanya *lintas-akademi* (arc 2 bisa pakai); *upgrade tingkat teknik* (P2 #4, GDD §7) **tetap di luar** Tahap B → Tahap C. Karena belum ada data yang memakainya, test memakai teknik dummy — scaffolding tanpa bukti produksi, disahkan karena prasyarat "arc baru = data saja".

**Files:**
- Modify: `data/techniques.csv` — tambah header kolom `unlock_arc` (semua baris kosong)
- Modify: `src/loader.py` — `player_techniques` terima `completed_quests` (set, default kosong); filter teknik `unlock_arc` yang final_quest-nya selesai
- Modify: `src/engine/battle.py` (`allowed`), `src/cli.py` (daftar teknik), `web/app.py` (daftar teknik) — teruskan `set(state.completed_quests)`; param default → caller lama tetap jalan tanpa perubahan wajib
- Modify: `tools/validate_data.py` — aturan 13: `unlock_arc` (bila ada) merujuk `config.arcs[].id`
- Modify: `tests/test_loader.py` (atau `test_battle.py`) — test baru
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §5.2 (teknik lintas akademi via `unlock_arc`)

**Interfaces:**
- Consumes: `config.arcs[].final_quest`, `techniques.csv::unlock_arc`, `state.completed_quests`.
- Produces: `player_techniques(academy, realm, completed_quests)` — teknik akademi sendiri (skill_pool) selalu; teknik lain dengan `unlock_arc ∈ arcs selesai` ikut; sisanya tidak.

- [ ] **Step 1: Tulis failing test** — `tests/test_loader.py`: (a) teknik dengan `unlock_arc: "akademi"` (dummy) tampil untuk akademi lain hanya bila `completed_quests` memuat `q_akademi_07`; (b) tanpa `completed_quests` → tidak tampil; (c) teknik tanpa `unlock_arc` tidak terpengaruh
- [ ] **Step 2: Run** — verifikasi gagal
- [ ] **Step 3: Implementasi CSV** — tambah kolom `unlock_arc` (kosong semua baris — non-breaking)
- [ ] **Step 4: Implementasi `loader.py::player_techniques`** — signature `(academy, realm=None, completed_quests=frozenset())`; helper internal `_arc_done(arc_id)` = `final_quest ∈ completed_quests`
- [ ] **Step 5: Caller** — `battle.py:199`, `cli.py:215`, `web/app.py:50` teruskan `set(session.state.completed_quests)` (web via `session.state`)
- [ ] **Step 6: Validator aturan 13** — teknik `unlock_arc` harus ∈ `config.arcs[].id`
- [ ] **Step 7: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau
- [ ] **Step 8: Docs** — ENGINE §5.2: teknik lintas akademi via `unlock_arc` (opsional, arc 2 siap pakai)

---

## Kriteria Selesai (Tahap B FULL)

- [ ] `python3 tools/validate_data.py` exit 0 + `python3 -m pytest -q` hijau setelah setiap task (aturan 7 & 13 diperluas; jumlah aturan tetap 16)
- [ ] `grep -rn "q_akademi_07\|AKHIR ARC\|loc_asrama\|arc_akademi_selesai" src/ --include=*.py` → **0 hasil** (web sudah generik; flag di data/dialogs & data/quests = data arc akademi, sah)
- [ ] Kontrak `view().arc_summary` tidak berubah (web `app.js` & CLI banner tanpa modifikasi wajib; `test_view_arc_summaries` & playthrough CLI tetap hijau)
- [ ] B1: `config.arcs` berisi arc akademi lengkap (title/teaser/branches/memories_total); validator menolak arc dengan `final_quest` tak dikenal / `memories_total` ≤ 0 / branches kosong
- [ ] B2: KO tanpa `last_safe_location` respawn di `config.world.safe_fallback_location`, lalu fallback lokasi safe pertama data; validator menolak fallback yang bukan lokasi `is_safe`
- [ ] B3: CLI banner tampil sekali via `arc_summary` (bukan flag literal); playthrough existing hijau
- [ ] B4: `techniques.csv` punya kolom `unlock_arc` (kosong); `player_techniques` non-breaking (semua caller lama jalan); validator menolak `unlock_arc` tak dikenal; test lintas-akademi hijau
- [ ] Docs sinkron: ENGINE §5.2/§5.6/§8.1/§9.2/§14/§17, CHANGELOG, PROJECT (bila baris baru), README (angka test)
- [ ] Commit: B1–B3 satu commit tema "engine adaptif arc" (file tumpang-tindih: config/validator/docs), B4 commit terpisah — pesan jujur mencatat overlap
