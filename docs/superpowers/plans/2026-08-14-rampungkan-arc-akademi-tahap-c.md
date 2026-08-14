# Rampungkan Tahap C FULL — Matangkan Fitur GDD yang Masih Kosong — Implementation Plan

> **Untuk agentic workers:** REQUIRED SUB-SKILL: Gunakan `superpowers:subagent-driven-development` (disarankan) atau `superpowers:executing-plans` untuk implementasi task-by-task. Steps pakai checkbox (`- [ ]`).
>
> **Sumber**: audit status Arc Akademi & kesiapan engine adaptif (2026-08-14) — keputusan user: **sebelum arc berikutnya, Arc Akademi harus rampung penuh, fitur GDD dibangun hingga lengkap & dimatangkan, dan engine harus adaptif (arc baru = data saja, tanpa ubah script engine).** Tahap A (DoD §11.2 + playtest §17) ✅ `b2388c7`/`4907c7b`/`1c593f4`. Tahap B (engine adaptif — 0 hardcode arc-1) ✅ `7ef1050`/`4991ea3`. Tahap ini = Tahap C: 3 fitur GDD yang masih kosong (rekomendasi P2 #4/#5/#6 + P3 #7 dari audit fitur).
>
> **STATUS EKSEKUSI (2026-08-14 lanjutan)**: ✅ **SELESAI — C1, C2, C3 + C3-fix** (commit `b0abbc3` C1, `77188eb` C2, `ab23534` C3, `06c8919` C3-fix). Verifikasi akhir: validate exit 0 + **251 passed**; playthrough CLI 3 akademi hijau (non-breaking). Deviasi C1: (1) batas level upgrade = **`order` ranah + 1**, bukan `technique_slots` — slots ranah awal = 1 tak memberi ruang upgrade (fitur mati); (2) test power scaling memakai **keanggotaan** daftar panggilan `_calc_damage`. Deviasi C2: formula month = **`(day−1)//mld+1`** (plan `day//mld+1` off-by-one di kelipatan persis). Deviasi C3: blok `return` `view()` sempat tersangkut di `_pick_ending` (unreachable) saat implementasi awal — dikoreksi sebelum commit (test menangkap); `_good()` test validator ditambah `arcs` valid. **C3-fix (temuan evaluasi)**: `_eval_condition` sempat *early-return* pada `flag` — kombinasi `flag` + kondisi lain (skema ending) mengabaikan kondisi lain; kini flag = cek AND biasa (data dialog existing flag tunggal → tanpa regresi).

**Goal:** Membangun & mematangkan 3 fitur yang GDD janjikan tapi masih kosong di kode, semuanya **data-driven & non-breaking** (arc Akademi sekarang tetap identik; arc berikutnya tinggal isi data):
- **C1 (GDD §7)**: Teknik **dipelajari & ditingkatkan** — reward teknik dari quest/dialog (efek `technique`), upgrade tingkat teknik (biaya + batas ranah), power scaling per level. Sekarang: teknik statis dari `skill_pool`; `technique_slots` di `realms.csv` ada tapi **tidak dipakai engine**.
- **C2 (GDD §7)**: **Siklus waktu lebih dalam** — bulan (derived dari hari), kondisi dialog berbasis bulan, event dunia terjadwal (data). Sekarang: hanya day/hour; GDD §7: *"hari/bulan berjalan; beberapa peristiwa hanya muncul pada waktu tertentu"*.
- **C3 (GDD §3.4/§9)**: **Moralitas → penentu ending** — scaffold sistem ending data-driven (`config.arcs[].endings` dengan kondisi moral+flags), `arc_summary` menampilkan ending; 3 ending tematik (Reformer/Destroyer/Ascetic) siap diisi konten arc final. Sekarang: moralitas hanya membuka/menutup pilihan dialog, bukan penentu ending.

**Architecture:** Semua perubahan mengikuti pola data-driven yang sudah mapan: (C1) efek `technique` di `effects.py` + `state.player.techniques` (list, diserialisasi) + `state.technique_levels` (dict, diserialisasi) + aksi `upgrade_technique` (pola `is_safe` seperti grounding) + `_use_technique` baca level; (C2) `time.month_length_days` di config + `state.month` derived (kompatibel save lama — tidak diserialisasi, dihitung dari `day`) + kondisi dialog `month_min/max` + `config.world.events` opsional; (C3) `config.arcs[].endings` opsional (arc akademi tanpa endings → `arc_summary.ending = None`, kontrak view tidak berubah) + `_eval_ending` memakai pola `_eval_condition` yang sudah ada. Setiap perubahan skema data disertai pembaruan validator (aturan 7 config, aturan efek quest/dialog, aturan 13 teknik).

**Tech Stack:** Python 3.12, stdlib-only, pytest. Tidak ada lint/typecheck.

## Global Constraints

- Semua komentar, dokumen, dan teks test **Bahasa Indonesia**; istilah teknis ber-pinyin/hanzi.
- Wajib lolos setelah setiap task: `python3 tools/validate_data.py` (exit 0) **dan** `python3 -m pytest -q`. Urutan baku CI: validate → pytest.
- Run dari root repo. Tidak menambah dependency.
- Konvensi commit repo: `feat:`, `test:`, `docs:`, `fix+test:`.
- Pola TDD untuk perubahan perilaku: tulis failing test dulu → verifikasi gagal → implementasi → hijau.
- Setiap perubahan skema data (kolom CSV baru, key config baru, tipe efek baru) WAJIB disertai pembaruan validator (`EFFECT_TYPES`/`_check_effect`, aturan 7, aturan 13).
- **Non-breaking**: kontrak `view()` lama tidak berubah (field baru opsional); save lama tetap dimuat (`from_dict` default).
- Prasyarat verifikasi per task: playthrough CLI 3 akademi (`tests/test_cli.py`) tetap hijau — bukti arc Akademi tidak berubah.

---

### Task C1: Teknik dipelajari & ditingkatkan (GDD §7)

> Kondisi sekarang: `loader.py::player_techniques(academy, realm, completed_quests)` hanya dari `skill_pool` akademi (+`unlock_arc` B4). Tidak ada cara memberi teknik baru dari quest/dialog, tidak ada upgrade. `realms.csv` punya kolom `technique_slots` (1..9) yang **tidak pernah dibaca engine** — jadikan batas level upgrade.

**Files:**
- Modify: `src/engine/state.py` — `PlayerState.techniques` (list[str], default []) + `technique_levels` (dict[str,int], default {}); to_dict/from_dict
- Modify: `src/engine/effects.py` — efek baru `technique` (id: str | list[str]) → tambah ke `player.techniques`
- Modify: `src/loader.py` — `player_techniques(academy, realm, completed_quests, owned=())` → union skill_pool + unlock_arc + owned (non-breaking: default `()`)
- Modify: `src/engine/session.py` — aksi `upgrade_technique {technique}` (hanya titik aman, pola `is_safe`; biaya `config.cultivation.technique_upgrade_cost_base` × level; batas level = `technique_slots` ranah saat ini); register di handler-map `apply_action`; tambah ke teks bantuan CLI (`cli.py` daftar perintah) + tombol web
- Modify: `src/engine/battle.py` — `_use_technique` power × (1 + (level−1) × `technique_power_growth_per_level`) ; `allowed` juga terima `owned` dari state
- Modify: `src/cli.py` / `web/app.py` / `web/static/app.js` — teruskan `owned` (state.player.techniques); tampilkan level teknik (CLI daftar teknik `Nama (Lv.X)`, web panel teknik + tombol Upgrade bila teknik belum max)
- Modify: `tools/validate_data.py` — `EFFECT_TYPES` + `technique`; `_check_effect` referensi teknik valid (aturan 13); config upgrade valid (aturan 7)
- Modify: `data/config.json` — `cultivation.technique_upgrade_cost_base` (mis. 20) + `technique_power_growth_per_level` (mis. 0.15)
- Modify: `tests/test_effects.py` / `tests/test_battle.py` / `tests/test_session.py` — test baru
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §5.4 (CSV teknik + teknik_slots), §9.1 (progresi), §5.2 (efek `technique`)

**Interfaces:**
- Consumes: `realms.csv::technique_slots`, `config.cultivation.technique_upgrade_cost_base`, `config.cultivation.technique_power_growth_per_level`, efek `technique`.
- Produces: pemain punya daftar teknik sendiri (dari akademi + reward) & level per teknik; battle memakai power bertingkat; validator menolak efek `technique` tak dikenal & config upgrade tak valid.

**Desain:**
- Efek: `{ "type": "technique", "id": "tek_x" }` atau `"id": ["tek_x", "tek_y"]` — quest/dialog memberi teknik baru (data-driven; arc berikutnya reward teknik tanpa ubah engine).
- `player_techniques` urutan hasil: skill_pool akademi → unlock_arc (B4) → owned (teknik reward) — dedup.
- `upgrade_technique`: di titik aman; `biaya = base × level_sekarang`; `level_baru = level+1`; batas `level <= technique_slots(ranah)` (dari realms.csv, order ranah → slots). Log sistem jelas ("teknik naik ke Lv.X" / "ranah belum cukup").
- Battle `_use_technique`: `power_efektif = int(power * (1 + (level-1) * growth))` — level default 1 (teknik reward mulai Lv.1).

- [ ] **Step 1: Tulis failing test** — `tests/test_effects.py`: efek `technique` menambah `player.techniques` (single & list); `tests/test_session.py`: `upgrade_technique` di titik aman menaikkan level & memotong gold; ditolak di luar titik aman; batas `technique_slots` ranah (level tidak naik melewati slots); `tests/test_battle.py`: power teknik naik sesuai level (monkeypatch `_calc_damage` atau cek argumen power)
- [ ] **Step 2: Run** — verifikasi gagal
- [ ] **Step 3: Implementasi state + effects** — `PlayerState.techniques`/`technique_levels` + efek `technique` + to_dict/from_dict
- [ ] **Step 4: Implementasi loader** — `player_techniques(..., owned=())` union + dedup (test existing `test_player_techniques_filter_ranah` & `test_player_techniques_unlock_arc_lintas_akademi` tetap hijau)
- [ ] **Step 5: Implementasi session** — aksi `upgrade_technique` + handler-map + log; helper `_technique_max_level(ranah)` baca `realms.csv::technique_slots`; `upgrade_technique` hanya untuk teknik yang `∈ player.techniques ∪ skill_pool` (teknik yang dimiliki)
- [ ] **Step 6: Implementasi battle** — `_use_technique` power scaling; `allowed` teruskan owned
- [ ] **Step 7: Caller** — `cli.py` daftar teknik tampil `Nama (Lv.X)`; `web/app.py` sertakan `level` per teknik
- [ ] **Step 8: Validator** — `EFFECT_TYPES` + `_check_effect` teknik valid; config upgrade (base > 0, growth ≥ 0) aturan 7
- [ ] **Step 9: Config** — tambah `technique_upgrade_cost_base` & `technique_power_growth_per_level`
- [ ] **Step 10: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau (+playthrough CLI)
- [ ] **Step 11: Docs** — ENGINE §5.2/§5.4/§9.1

---

### Task C2: Siklus waktu lebih dalam — bulan & peristiwa (GDD §7)

> Kondisi sekarang: `config.time` = `{day_length_hours: 24, start_day: 1, start_hour: 8}`; `state.day`/`state.hour`; `_pass_time` menaikkan jam→hari. GDD §7: *"hari/bulan berjalan; beberapa peristiwa hanya muncul pada waktu tertentu"* — jam sudah dipakai (jadwal NPC, window quest, night hunt); **bulan belum ada**.

**Files:**
- Modify: `data/config.json` — `time.month_length_days` (mis. 30) + opsional `time.month_names` (12 nama, Bahasa Indonesia)
- Modify: `src/engine/state.py` — property `month` (1-based: `day // month_length_days + 1`) + `month_name(registry)` helper (fallback `f"Bulan {month}"` bila `config.time.month_names` tidak ada); `absolute_hours` tetap
- Modify: `src/engine/dialog.py` — kondisi `month_min`/`month_max` di `_eval_condition` (berbasis `state.month`)
- Modify: `src/engine/session.py` — `view()` sertakan `month` (+`month_name`); `_pass_time` tidak berubah (month derived)
- Modify: `src/cli.py` — header tampil `Bulan X — Hari Y, jam Z`
- Modify: `web/app.py` + `web/static/app.js` — header web tampilkan bulan (opsional, minor)
- Modify: `tools/validate_data.py` — aturan 7: `month_length_days` int > 0; `month_names` (bila ada) = 12 item string; kondisi dialog `month_min/max` valid (int 1..12) di `_check_dialog_condition`
- Modify: `tests/test_session.py` / `tests/test_dialog.py` / `tests/test_validator.py` — test baru
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §5.6 (config time), §7 (kondisi dialog), §12.4 (view)

**Interfaces:**
- Consumes: `config.time.month_length_days`, `config.time.month_names` (opsional).
- Produces: `view().month` + `view().month_name`; kondisi dialog `month_min/max` (data arc berikutnya: peristiwa bulan tertentu tanpa ubah engine); validator menolak month_length ≤ 0 / month_names ≠ 12 / kondisi bulan tak valid.

**Desain:**
- `month` **derived**, bukan field tersimpan — save lama otomatis kompatibel (tidak perlu migrasi). `month = day // month_length_days + 1` (day 1 = Bulan 1).
- Kondisi dialog `month_min`/`month_max` dipakai AND dengan kondisi lain (pola `_eval_condition` multi-kunci). Contoh data masa depan: *"hanya muncul Bulan 3–5"*.
- Event dunia terjadwal (`config.world.events`) **opsional & ditunda** — C2 fokus bulan + kondisi; event peristiwa dunia bisa jadi task tersendiri bila konten arc berikutnya butuh (dicatat sebagai follow-up, bukan blocker).

- [ ] **Step 1: Tulis failing test** — `tests/test_session.py`: `view().month` benar untuk day 1 / day 31 / day 61 (month_length 30); `tests/test_dialog.py`: kondisi `month_min/max` menyaring choice; `tests/test_validator.py`: month_length ≤ 0 ditolak, month_names ≠ 12 ditolak, kondisi month_min/max di luar 1..12 ditolak
- [ ] **Step 2: Run** — verifikasi gagal
- [ ] **Step 3: Implementasi state** — property `month` + helper `month_name`
- [ ] **Step 4: Implementasi dialog** — `month_min`/`month_max` di `_eval_condition`
- [ ] **Step 5: Implementasi view + CLI + web** — sertakan bulan di view & header
- [ ] **Step 6: Validator** — aturan 7 (config time) + `_check_dialog_condition` (month range)
- [ ] **Step 7: Config** — tambah `month_length_days` (+`month_names`)
- [ ] **Step 8: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau (+playthrough CLI)
- [ ] **Step 9: Docs** — ENGINE §5.6/§7/§12.4

---

### Task C3: Moralitas → penentu ending (scaffold GDD §3.4/§9)

> Kondisi sekarang: moralitas [-100, 100] dipakai kondisi dialog (`morality_min/max` — `dialog.py::_eval_condition`), efek quest/dialog, dan ditampilkan di `arc_summary`. GDD §3.4: *"Skala moralitas dipakai untuk membuka/menutup pilihan dialog **& ending**"*; §9: penentu ending = pilihan kunci + moralitas akhir; 3 ending tematik (Reformer/Destroyer/Ascetic) disahkan. Scaffold **data-driven**: `config.arcs[].endings` — arc Akademi tanpa endings (non-breaking), arc final tinggal isi data.

**Files:**
- Modify: `data/config.json` — struktur arcs: field opsional `endings` (tidak diisi untuk arc akademi — bukti non-breaking; contoh skema di docs)
- Modify: `src/engine/session.py` — `view()`: saat arc selesai (`arc_summary` terbentuk), hitung `ending` dari `config.arcs[].endings` pertama yang kondisinya cocok (pola `_eval_condition`); `arc_summary["ending"] = {id, title, desc} | None`
- Modify: `src/cli.py` — banner arc tampilkan ending bila ada
- Modify: `web/static/app.js` — modal arc tampilkan ending bila ada (opsional, minor)
- Modify: `tools/validate_data.py` — aturan 7: tiap ending punya `id` unik, `title`/`desc` string, `condition` dict (moral/flags); referensi flag bebas (string); validator kondisi ending memakai pola `_check_dialog_condition` (subset: morality_min/max, flags)
- Modify: `tests/test_session.py` — test ending: arc dengan endings (inject dummy ke config) memilih sesuai moralitas; arc tanpa endings → `ending = None`
- Modify: `docs/ENGINE_ARCHITECTURE.md` — §5.6 (skema endings), §9.2/§17 (penentu ending data-driven)

**Interfaces:**
- Consumes: `config.arcs[].endings` (opsional), `state.player.morality`, `state.flags`, `state.completed_quests`.
- Produces: `arc_summary.ending` (None untuk arc akademi — kontrak view lama tidak berubah); validator menolak ending tanpa id/title/desc atau kondisi tak valid.

**Skema (dicontohkan di docs, tidak diisi arc akademi) — PENTING: `condition` harus mengikuti skema kondisi dialog existing (`_eval_condition`): kunci `morality_min`/`morality_max` TOP-LEVEL dan `flag` SINGULAR (bukan `flags` plural/nested):**
```json
"endings": [
  { "id": "reformer", "title": "Pembangun Ulang (Reformer)",
    "desc": "Membangun ulang sistem yang lebih baik.",
    "condition": { "morality_min": 30, "flag": { "key": "kunci_reformasi", "value": true } } },
  { "id": "destroyer", "title": "Penghancur (Destroyer)",
    "desc": "Membakar habis sistem lama.",
    "condition": { "morality_max": -30, "flag": { "key": "kunci_kehancuran", "value": true } } },
  { "id": "ascetic", "title": "Pertapa (Ascetic)",
    "desc": "Menerima dan berdamai dengannya.",
    "condition": {} }
]
```
Semua condition = AND (pola `_eval_condition` — dipakai ulang apa adanya, bukan parser baru); ending pertama yang cocok menang; fallback: bila `condition` kosong → selalu cocok (ending "default"). Validator `_check_dialog_condition` dipakai ulang untuk ending (subset kunci yang didukung: `morality_min/max`, `flag`, `has_item`, `academy`, dll. sesuai kondisi dialog).

- [ ] **Step 1: Tulis failing test** — `tests/test_session.py`: (a) inject endings dummy ke `config.arcs[0]` + set moralitas & flags → `arc_summary.ending.id` benar; (b) moralitas berbeda → ending berbeda; (c) tanpa `endings` → `arc_summary["ending"] is None` (kontrak lama); (d) validator: ending tanpa title ditolak, condition tak dikenal (mis. `mood_min`) ditolak
- [ ] **Step 2: Run** — verifikasi gagal
- [ ] **Step 3: Implementasi session** — helper `_pick_ending(arc)` (iterate endings, `_eval_condition`-style) + `arc_summary["ending"]`
- [ ] **Step 4: CLI + web** — tampilkan ending bila ada (opsional field — tidak memecah render lama)
- [ ] **Step 5: Validator** — aturan 7 endings (id unik, title/desc, condition valid: hanya kunci morality_min/max/flags)
- [ ] **Step 6: Run** `python3 tools/validate_data.py && python3 -m pytest -q` — hijau (+playthrough CLI)
- [ ] **Step 7: Docs** — ENGINE §5.6/§9.2/§17: skema endings + peta ke 3 ending tematik GDD §9 (konten arc final = data)

---

## Kriteria Selesai (Tahap C FULL)

- [ ] `python3 tools/validate_data.py` exit 0 + `python3 -m pytest -q` hijau setelah setiap task (aturan 7 & 13 diperluas; jumlah aturan tetap 16)
- [ ] **Non-breaking**: playthrough CLI 3 akademi (`tests/test_cli.py`) hijau setelah tiap task — arc Akademi tidak berubah perilaku
- [ ] C1: efek `technique` memberi teknik dari quest/dialog (data-driven); `upgrade_technique` di titik aman naikkan level (biaya gold, batas `technique_slots` ranah); battle memakai power bertingkat; save round-trip `player.techniques`/`technique_levels`; validator menolak efek tak dikenal
- [ ] C2: `view().month` benar (derived, kompatibel save lama); kondisi dialog `month_min/max` menyaring; validator config time & kondisi bulan; header CLI/web menampilkan bulan
- [ ] C3: `config.arcs[].endings` opsional; `arc_summary.ending` = None untuk arc akademi (kontrak lama utuh); dengan endings dummy → pilih sesuai moralitas+flags (first-match, AND); validator ending
- [ ] Docs sinkron: ENGINE §5.2/§5.4/§5.6/§7/§9.1/§9.2/§12.4/§17, CHANGELOG, PROJECT (bila baris baru), README (angka test)
- [ ] Commit per task bila file disjoint; bila tumpang-tindih (session.py/validator/config dipakai >1 fitur) → 1 commit tema dengan pesan jujur (preseden Tahap A/B)
