# Evaluasi Komprehensif Test Suite Pytest & Bugfix Engine

**Dokumen**: `docs/superpowers/reviews/2026-08-14-test-suite-evaluation.md`  
**Tanggal**: 14 Agustus 2026  
**Proyek**: *Tian Xu: Second Life* (Arc Akademi - Fase 1)  
**Evaluator**: SWE QA & Architecture Evaluator  
**Status Eksekusi Test**: **93 passed in 1.40s** (100% pass rate, 0 failure, 0 skipped, 0 warning)  
**Validasi Data**: **Exit Code 0** (`tools/validate_data.py` — 16/16 aturan §14 lolos)  
**Total Line Coverage**: **84%** (1248/1479 baris engine & CLI ter-cover)  

---

## 1. Ringkasan Eksekutif & Metrik Kualitas

Evaluasi ini menyajikan audit independen dan komprehensif terhadap kualitas kode (*code quality*), pola arsitektur (*architectural design*), dan cakupan pengujian (*test coverage*) dari test suite `pytest` yang baru diimplementasikan beserta serangkaian perbaikan bug engine (*recent engine bugfixes*) terkini pada repositori *Tian Xu: Second Life*.

### 1.1 Metrik Pengujian & Cakupan Kode (Coverage Breakdown)

Berdasarkan eksekusi `python3 -m pytest --cov=src --cov-report=term-missing`, rincian cakupan per modul adalah sebagai berikut:

| Modul / Komponen | Baris Total (Stmts) | Baris Terlewat (Miss) | Cakupan (Cover) | Baris Belum Ter-cover (Missing Lines) | Ringkasan Status & Evaluasi Kualitas |
|---|---|---|---|---|---|
| `src/loader.py` | 64 | 0 | **100%** | — | Pemuatan & pengindeksan data JSON/CSV berstatus sempurna. |
| `src/engine/cultivation.py` | 40 | 0 | **100%** | — | Multiplier akar spiritual, level up, dan breakthrough ranah teruji eksak. |
| `src/engine/morality.py` | 11 | 0 | **100%** | — | Skala moralitas & pembatasan batas (*clamping*) teruji penuh. |
| `src/engine/quest.py` | 212 | 18 | **92%** | 60, 92, 99, 127, 136, 157, 171-172, 180, 220, 227, 234, 236, 238, 242, 244, 249, 257 | Graf DAG main quest, single active invariant, dan konvergensi 4 cabang teruji kokoh. |
| `src/engine/state.py` | 103 | 9 | **91%** | 41, 54-56, 63-64, 95, 104, 112 | Dataclass state, serialisasi `to_dict`/`from_dict`, dan `UIState` proxy berjalan aman. |
| `src/engine/memory.py` | 16 | 2 | **88%** | 20, 23 | Pembukaan ingatan naratif Tianyuan Ling teruji via alur quest. |
| `src/engine/battle.py` | 237 | 34 | **86%** | 32, 137, 145, 156, 165, 181-182, 190-191, 199-205, 208-222, 236, 263, 330 | Formula damage, wuxing, regen Qi, kompanion, flee, spar, dan hunt teruji deterministik. |
| `src/engine/effects.py` | 33 | 5 | **85%** | 25-26, 35, 39, 43 | Efek moralitas, relasi, item, gold, dan flag terintegrasi dengan dialog/quest. |
| `src/engine/session.py` | 380 | 59 | **84%** | 32-33, 35, 79, 89, 133-136, 152, 156-157, 163, 198-199, 244-245, 248-249, 252, 286-297, 301-302, 309-310, 315-324, 358-359, 364-365, 380-381, 386-387, 389-390, 393, 411-412, 432 | Orkestrasi aksi, action gating, proteksi lokasi aman, dan save/load security terverifikasi. |
| `src/engine/dialog.py` | 117 | 23 | **80%** | 34, 44, 48, 61, 66, 69, 90, 94, 129-130, 132-133, 135-140, 142-143, 145-147 | Evaluasi kondisi entri/opsi dialog, traversal node, dan efek percabangan. |
| `src/engine/events.py` | 9 | 2 | **78%** | 15, 21 | Pencatatan event log & log delta. |
| `src/cli.py` | 257 | 79 | **69%** | 17, 58-60, 63-64, 70, 96, 103, 114, 121-124, 141, 149, 159-169, 196-198, 200, 212-229, 233-235, 251-253, 258, 262, 264, 268, 270, 272-275, 278-281, 283-284, 286-287, 289-290, 292, 294-302, 304, 322 | Interface terminal CLI, REPL loop, formatter tampilan, dan playthrough E2E. |
| **TOTAL** | **1479** | **231** | **84%** | — | **Cakupan Pengujian Keseluruhan Sangat Solid** |

---

## 2. Analisis & Verifikasi Bugfix Engine Terkini

Audit terhadap commit-commit perbaikan engine terbaru menunjukkan refactoring yang terarah dan peningkatan keamanan yang signifikan:

### 2.1 Commit `1c4c827`: Transisi Mode UI dan Inisialisasi Proxy State
- **Berkas & Baris**: `src/engine/state.py:46-51, 87-96`
- **Substansi Perubahan**:
  1. Pada `UIState.mode.setter` (`state.py:46-51`), ditambahkan kondisi pembersihan `self._state.pending_battle = None` saat `state.ui.mode` diset ke nilai selain `"battle"` ketika `pending_battle` sedang aktif.
  2. Deklarasi field `_ui_proxy: UIState | None = field(default=None, init=False, repr=False)` dan inisialisasi di `GameState.__post_init__` (`state.py:87-91`), menggantikan pemeriksaan runtime `hasattr(self, "_ui_proxy")`.
- **Verifikasi Test**: `tests/test_session.py::test_ui_mode_transition_clears_pending_battle` memvalidasi bahwa transisi mode dari `"battle"` ke `"explore"` membersihkan `pending_battle`.
- **Penilaian Kualitas**: ⭐⭐⭐⭐⭐ (Sangat Baik). Mencegah desinkronisasi state battle saat mode UI diubah secara programatik.

### 2.2 Commit `523aa93`: Refactoring Dialog Condition Evaluation & Keamanan Save Null-Byte
- **Berkas & Baris**: `src/engine/dialog.py:118-156`, `src/engine/session.py:26-36, 442-450`
- **Substansi Perubahan**:
  1. Metode evaluasi kondisi dialog di-refactor menjadi static method `@staticmethod _eval_condition(state, cond, registry=None)` (`dialog.py:118-153`), memungkinkan pengujian unit kondisi secara langsung tanpa menginstansiasi keseluruhan dependensi engine.
  2. `_safe_save_path` (`session.py:26-36`) diperkuat dengan pengecekan karakter null-byte (`"\x00"`), serta penanganan `(ValueError, OSError)` pada resolusi path `.resolve()`.
  3. `GameSession._save` (`session.py:442-450`) menangkap `(SaveError, ValueError, OSError)` dan mengembalikan respon error JSON yang terformat.
- **Verifikasi Test**:
  - `tests/test_dialog.py::test_dialog_condition_morality` (evaluasi kondisi moralitas via static method).
  - `tests/test_saveload.py::test_save_null_byte_rejected` (penolakan injeksi null-byte pada nama save).
- **Penilaian Kualitas**: ⭐⭐⭐⭐⭐ (Sangat Baik). Modularitas tinggi dan proteksi injeksi null-byte pada filesystem level.

### 2.3 Commit `93ff50e`: Validasi Skema Serialisasi GameState & Proteksi Path Traversal
- **Berkas & Baris**: `src/engine/state.py:130-197`, `src/engine/session.py:26-36, 83-96`, `tests/test_saveload.py:1-116`
- **Substansi Perubahan**:
  1. `GameState.to_dict()` dan `GameState.from_dict()` (`state.py:130-197`) menerapkan `copy.deepcopy()` pada seluruh struktur data mutable (`inventory`, `equipment`, `flags`, `relations`, `memories`, `active_side_quests`, `pending_battle`, `companion`).
  2. Fungsi `_safe_save_path` menegakkan batas direktori melalui `path.parent == SAVES_DIR.resolve()`, menolak nama file traversal (`../`, `..\\`, `/`, `\`).
  3. `GameSession.load()` membungkus semua kegagalan deserialisasi menjadi exception terspesialisasi `SaveError`.
- **Verifikasi Test**: `tests/test_saveload.py` (5 skenario uji: roundtrip serialization immutability, format file save nyata, penolakan path traversal save & load, penolakan null-byte).
- **Penilaian Kualitas**: ⭐⭐⭐⭐⭐ (Sangat Baik). Menjamin isolasi mutasi memori pasca deserialisasi dan mencegah eksfiltrasi/penulisan file arbitrer di luar direktori `saves/`.

### 2.4 Commit `694d242`: Sinkronisasi View Sesi Pasca Percabangan Quest
- **Berkas & Baris**: `src/engine/session.py:137-141`
- **Substansi Perubahan**:
  - Pada `GameSession.apply_action()` (`session.py:137-141`), evaluasi `self._maybe_start_branch_dialog()` dipanggil sebelum penyusunan view (`out = self.view()`), memastikan dialog pilihan cabang langsung hadir pada return payload aksi penentu.
- **Verifikasi Test**: `tests/test_session.py::test_branch_dialog_included_in_apply_action_view` (memverifikasi bahwa aksi `move` ke `loc_ruang_lonceng` yang menyelesaikan `q_akademi_02` langsung menghasilkan respon bermode `"dialog"` dengan `pending_dialog` aktif).
- **Penilaian Kualitas**: ⭐⭐⭐⭐⭐ (Sangat Baik). Mengeliminasi jeda aksi (*action lag*) 1 giliran pada CLI dan frontend Web.

### 2.5 Commit `2a5ae38`: Pengawalan Aksi Sesi (Session Action Gating)
- **Berkas & Baris**: `src/engine/session.py:101-108, 261-268, 326-333, 401-408, 434-441`
- **Substansi Perubahan**:
  1. Penolakan aksi di luar zona aman (`is_safe == False`) untuk aksi: `grounding` (meditasi), `rest` (istirahat), `craft` (meracik), dan `save` (simpan permainan).
  2. Penolakan semua aksi selain `battle_action` ketika `pending_battle` aktif.
- **Verifikasi Test**: `tests/test_session.py` (`test_action_blocked_in_battle`, `test_crafting_blocked_in_unsafe_zone`, `test_resting_blocked_in_unsafe_zone`, `test_saving_blocked_in_unsafe_zone`, `test_grounding_blocked_in_unsafe_zone`, `test_gate_battle_blok_aksi_lain`).
- **Penilaian Kualitas**: ⭐⭐⭐⭐⭐ (Sangat Baik). Menegakkan aturan integritas game loop sesuai GDD §9.3 & ENGINE_ARCHITECTURE §12.3.

---

## 3. Tinjauan Arsitektural dan Kualitas Kode

### 3.1 Pola Desain Inti (Core Design Patterns)

1. **Data-Driven Architecture**:
   - Seluruh konten permainan (14 quest, 10 dialog, 9 NPC, 9 lokasi, 6 item, 3 musuh, 4 ingatan, resep, kompanion, teknik, ranah) disimpan dalam format JSON & CSV di `data/`.
   - `src/loader.py::DataRegistry` memuat dan mengindeks seluruh data menjadi kamus read-only pada saat startup.
2. **Dataclass GameState sebagai Single Source of Truth**:
   - Status runtime terpusat pada instance `GameState`. Seluruh engine (`DialogEngine`, `QuestEngine`, `BattleEngine`) beroperasi langsung terhadap instance state bersama ini.
3. **Session Orchestrator & Action Dispatcher**:
   - `GameSession.apply_action(action: dict) -> dict` menjadi satu-satunya gerbang mutasi state bagi CLI (`src/cli.py`) maupun Web REST HTTP (`web/app.py`).

### 3.2 Temuan & Evaluasi Kritis per Modul

#### A. `src/engine/state.py` (Kualitas: Baik | Kritik: Dualitas Abstraksi UIState Proxy)
- **Kelebihan**:
  - Implementasi dataclass bersih dengan `to_dict` dan `from_dict` yang menerapkan deepcopy menyeluruh.
  - Perhitungan stat (`max_hp`, `max_qi`, `exp_next`, `exp_multiplier`) terintegrasi langsung dengan konfigurasi registri.
- **Kritik & Catatan Arsitektural**:
  - Kelas `UIState` (`state.py:28-65`) bertindak sebagai helper proxy untuk kompatibilitas pengujian lama yang mengakses `state.ui.mode` dan `state.ui.battle`. Properti setter `mode` hanya dapat mengaktifkan mode `"battle"` (`self._state.pending_battle = {"active": True}`), sementara jika diset ke `"dialog"`, tidak ada keterkaitan dengan `pending_dialog`. Dualitas ini menciptakan dua jalur mutasi state UI (`state.pending_battle` vs `state.ui.mode`). Disarankan di Fase 2 untuk menyederhanakan akses state langsung ke field `GameState` tanpa proxy wrapper.

#### B. `src/engine/session.py` (Kualitas: Sangat Baik | Kritik: Rekonstruksi Out-Dict pada Action Dispatcher)
- **Kelebihan**:
  - Gating aksi zona aman dan battle konsisten menuliskan log sistem dan mengembalikan pesan error informatif.
  - Penanganan file save aman dari path traversal dan kerusakan format UTF-8 / JSON.
- **Kritik & Catatan Arsitektural**:
  - Pada `apply_action` (`session.py:137-141`):
    ```python
    self._maybe_start_branch_dialog()
    out = self.view()
    if isinstance(res, dict) and "error" in res:
        out["error"] = res["error"]
    return out
    ```
    Struktur ini membangun ulang `out` dari `self.view()`. Jika di masa mendatang terdapat handler aksi yang mengembalikan metadata kustom di `res` selain field `"error"`, metadata tersebut akan tereliminasi. Saat ini seluruh handler internal mengembalikan `self.view()`, namun pola yang lebih defensif adalah menggabungkan seluruh kunci non-view dari `res` ke dalam `out`.

#### C. `src/engine/quest.py` (Kualitas: Sangat Baik | Kritik: Naming Misnomer pada Storage Progres Quest Utama)
- **Kelebihan**:
  - Penegakan graf DAG dan invariansi satu quest utama aktif (`single_active_main_quest`) bekerja presisi.
  - Mendukung 7 jenis objektif (`talk`, `defeat`, `gather`, `reach`, `choose`, `spar`, `advance_time`) dengan tracking offset waktu (`day_offset`).
- **Kritik & Catatan Arsitektural**:
  - Kamus `state.active_side_quests` (`quest.py:36-39, 72, 170, 211`) digunakan untuk mencatat progres sementara quest utama (seperti hitungan bicara `talk` dan metadata `start_day`/`start_hour` untuk `advance_time`).
  - Meskipun metode `active_side()` (`quest.py:35-39`) menyaring entri dengan `(self.reg.quest(qid) or {}).get("kind") == "side"`, penggunaan kamus bernama `active_side_quests` untuk progres quest utama merupakan *naming misnomer*. Di Fase 2, disarankan memisahkan kamus ini menjadi `state.quest_progress: dict[str, dict]` untuk tracking objektif dan `state.active_side_quests: dict[str, dict]` murni untuk side quest aktif.

#### D. `src/engine/battle.py` (Kualitas: Sangat Baik | Kritik: Cakupan Cabang Teknik Defend/Heal & Item)
- **Kelebihan**:
  - Formula damage `attack * (100 / (100 + defense)) * multiplier` teruji matematis.
  - Multiplier wuxing 1.5× dan 0.67× terisolasi dengan determinisme sempurna.
  - Mekanik kompanion Summoning (§9.4) bertindak otomatis dan memiliki persentase target 50% yang teruji via mocking RNG.
- **Kritik & Catatan Arsitektural**:
  - Cabang teknik bertipe `"defend"` (`battle.py:200`) dan `"heal"` (`battle.py:203`) serta penggunaan item dalam battle (`battle.py:208-222`) belum memiliki test method tersendiri di `test_battle.py`, meskipun logika kodenya valid.

#### E. `tools/validate_data.py` (Kualitas: Luar Biasa)
- **Kelebihan**:
  - Menegakkan 16 aturan integritas statis data sesuai `ENGINE_ARCHITECTURE.md §14`.
  - Menguji topologi DAG tanpa siklus (DFS cycle detection), koneksi dua arah lokasi, keunikan ID, konsistensi formula CSV, integritas resep, dan isolasi NPC side quest vs main quest.
  - Teruji secara menyeluruh oleh `tests/test_validator.py` dengan 19 skenario korupsi data buatan.

---

## 4. Evaluasi Cakupan Test Suite (Test Suite Breakdown)

Suite pengujian terdiri dari **11 berkas pengujian** dengan total **93 skenario uji**:

| Berkas Pengujian | Jumlah Test | Fokus Pengujian & Cakupan Kasus | Strategi Determinisme |
|---|---|---|---|
| `tests/test_battle.py` | 12 | Formula damage, wuxing element advantage/disadvantage, batas variasi & kritikal, damage min 1, drop reward, KO respawn & penalti exp, pembatasan teknik akademi, regen Qi. | `mock_god_mode` & monkeypatching `random.uniform`/`random.random`. |
| `tests/test_cli.py` | 1 | E2E playthrough dari awal hingga akhir Arc Akademi (cabang 3aa) + validasi persistensi penyimpanan pasca-arc. | Mocking `builtins.input` dan `BattleEngine._calc_damage`. |
| `tests/test_companion.py` | 6 | Pemberian binatang roh jalur Summoning, eksklusivitas akademi, auto-action kompanion, targeting musuh, KO & revival saat rest, scaling stat per tingkat. | Mocking RNG targeting dan fixture `god_mode`. |
| `tests/test_conftest.py` | 2 | Verifikasi integritas fixture bersama (`dummy_session`, `mock_god_mode`). | Eksak. |
| `tests/test_cultivation.py` | 3 | Multiplier exp akar spiritual (0.8× low, 1.25× high), breakthrough level 10, batas cap ranah tertinggi. | Perhitungan matematis deterministik. |
| `tests/test_dialog.py` | 8 | Evaluasi kondisi moralitas via static method, traversal dialog penjaga, entri kondisional NPC Su Qing, efek pilihan dialog, percabangan, isolasi penawaran side quest. | Navigasi dialog terstruktur. |
| `tests/test_quest_dag.py` | 10 | 4 cabang konvergensi (3aa, 3ab, 3b, 3c), pengawal balancing level akhir Lv.4–6, invariansi 1 quest aktif, penegakan `day_offset`, penyelesaian side quest berburu. | Helper `play_to_incident` dan `move_path`. |
| `tests/test_saveload.py` | 5 | Roundtrip serialisasi `to_dict`/`from_dict`, format json file nyata, penolakan path traversal save & load, penolakan null-byte injection. | Fixture `tmp_path` dan monkeypatching `SAVES_DIR`. |
| `tests/test_session.py` | 19 | Pergerakan lokasi valid/invalid, kuota grounding harian, transaksi toko beli/jual, gating lokasi aman (save/craft/rest/grounding), pembatasan aksi saat battle, validasi save corrupt/non-utf8, branch dialog view sync. | Isolasi direktori save & aksi sesi. |
| `tests/test_validator.py` | 19 | Verifikasi dataset valid vs 16 variasi data korup (JSON rusak, NPC hilang, siklus DAG, choice_id hilang, konflik side vs main, ID duplikat, elemen invalid, formula rusak, dll). | In-memory mocking & temporary file trees. |
| `tests/test_web.py` | 8 | Server HTTP nyata (`ThreadingHTTPServer` pada port ephemeral dinamis), endpoint index, new game, talk action, save/load API, panel Tianyuan, error handling 400 bad request, penolakan aksi tanpa sesi. | Multi-threaded HTTP server & urllib client. |

---

## 5. Analisis Celah Pengujian yang Teridentifikasi (Detailed Gap Analysis)

Meskipun suite test mencapai tingkat kelulusan 100% dan coverage 84%, analisis mendalam mengidentifikasi baris dan cabang logika yang belum dieksekusi secara langsung:

### 5.1 Rincian Baris Belum Ter-cover per Modul

1. **`src/engine/dialog.py` (23 baris Miss | 80% Cover)**:
   - `line 34`: Return `None` saat dialog ID tidak terdaftar di `reg.dialog()`.
   - `line 44`: Return `None` pada `choose()` saat `self.current` atau `self.node_id` belum aktif.
   - `line 48`: Return `self.view()` pada `choose()` saat `choice_index` berada di luar rentang.
   - `line 61`: Pemanggilan `self._end()` pada opsi tanpa properti `next`.
   - `line 66`: Return `None` pada `advance()` saat dialog tidak aktif.
   - `line 69`: Return `self.view()` pada `advance()` saat node memiliki pilihan (mencegah skip pilihan).
   - `line 90`: Pengecualian opsi dialog dalam `_visible_choices` saat evaluasi kondisi bernilai `False`.
   - `line 94`: Pengecualian opsi dialog dengan efek `start_quest` saat quest tidak lagi memenuhi syarat penawaran (`is_offerable == False`).
   - `line 129-130`: Evaluasi kondisi `morality_max` saat moralitas pemain melebihi batas maksimum.
   - `line 132-133`: Evaluasi kondisi `has_item` saat jumlah item dalam inventori `< 1`.
   - `line 135-140`: Evaluasi kondisi `realm_min` saat `registry is None` atau tingkatan ranah pemain belum mencukupi.
   - `line 142-143`: Evaluasi kondisi `academy` saat akademi pemain tidak cocok dengan syarat dialog.
   - `line 145-147`: Evaluasi kondisi `quest_active` saat quest target tidak sedang aktif.

2. **`src/engine/battle.py` (34 baris Miss | 86% Cover)**:
   - `line 32`: Return `None` pada `companion_stats` saat ID kompanion tidak ditemukan di data registri.
   - `line 137`: Return awal `self.view()` pada `player_action` saat pertarungan telah selesai (`over == True`).
   - `line 145`: Pemanggilan `_use_item` dari dispatcher `player_action`.
   - `line 156`: Pencatatan log kegagalan kabur saat `_try_flee(pc, b) == False`.
   - `line 165`: Skenario kemenangan ketika seluruh musuh tereliminasi setelah giliran musuh.
   - `line 181-182`: Penolakan teknik pertarungan yang tidak terdaftar di data registri.
   - `line 190-191`: Penolakan eksekusi teknik saat Qi pemain tidak mencukupi `qi_cost`.
   - `line 199-205`: Eksekusi teknik bertahan bertipe `"defend"` dan teknik penyembuhan bertipe `"heal"`.
   - `line 208-222`: Alur penggunaan item konsumsi (`_use_item`) dalam pertarungan.
   - `line 236`: Loop giliran musuh melewati entri musuh yang sudah KO (`hp <= 0`).
   - `line 263`: Return awal pada giliran kompanion jika tidak ada musuh yang hidup.
   - `line 330`: Pemberian exp kekalahan latihan tanding (`spar_loss_exp`) saat pemain KO dalam mode spar.

3. **`src/engine/session.py` (59 baris Miss | 84% Cover)**:
   - `line 32-33, 35`: Penanganan `(ValueError, OSError)` dan exception `SaveError` pada `_safe_save_path`.
   - `line 79`: Pengesetan `last_safe_location` di `GameSession.new()` jika lokasi awal tergolong zona aman.
   - `line 89`: Penanganan eksplisit `FileNotFoundError` pada `GameSession.load()`.
   - `line 133-136`: Penanganan aksi tak dikenal (*unknown action type*) di `apply_action`.
   - `line 152, 156-157, 163`: Penanganan NPC tidak valid atau tidak berada di lokasi pemain pada `_talk`.
   - `line 198-199`: Penolakan perpindahan ke lokasi yang tidak terdaftar di registri pada `_move`.
   - `line 244-245, 248-249, 252`: Penolakan pemakaian item yang tidak dimiliki / bukan konsumsi / pembersihan kunci inventori saat count mencapai 0 pada `_use_item`.
   - `line 286-297`: Inisiasi latihan tanding bebas (`_spar`) melalui menu explore.
   - `line 301-302, 309-310`: Penolakan berburu di luar Wilayah Berburu / ketiadaan musuh pada `_hunt`.
   - `line 315-324`: Eksekusi pencarian herba (`_search`) pada skenario sukses (`RNG < 0.6`) dan gagal (`RNG >= 0.6`).
   - `line 358-359, 364-365, 380-381, 386-387, 389-390, 393`: Penanganan error transaksi toko (pedagang tidak ada, item tidak dijual/dibeli, stok pemain kurang, dan pembersihan slot inventori saat habis terjual).
   - `line 411-412`: Penolakan resep racik yang tidak terdaftar pada `_craft`.
   - `line 432`: Return `None` saat tidak ada pedagang di lokasi saat ini pada `_merchant_here`.

4. **`src/engine/effects.py` (5 baris Miss | 85% Cover)**:
   - `line 25-26`: Penerapan efek penyesuaian reputasi faksi (`reputation`).
   - `line 35`: Penghapusan item dari inventori saat count berkurang menjadi `<= 0` akibat efek dialog.
   - `line 39`: Clamping nilai gold agar tidak bernilai negatif saat dikurangi melebihi saldo.
   - `line 43`: Pencatatan log sistem saat menerima tipe efek yang tidak dikenali.

5. **`src/engine/quest.py` (18 baris Miss | 92% Cover)**:
   - `line 60, 92, 99, 127, 136, 157, 171-172, 180, 220, 227, 234, 236, 238, 242, 244, 249, 257`: Fallback return pada pemeriksaan notifikasi objektif dan penanganan metode side quest sekunder.

6. **`src/engine/state.py` (9 baris Miss | 91% Cover)**:
   - `line 41`: UIState `mode` mengembalikan `"dialog"` saat `pending_dialog` aktif.
   - `line 54-56, 63-64`: UIState `battle` getter dan setter fallback branches.
   - `line 95`: Fallback inisialisasi lazy `_ui_proxy` pada properti `ui`.
   - `line 104, 112`: Fallback `max_hp` dan `max_qi` saat ID ranah pemain tidak ditemukan di registri.

7. **`src/cli.py` (79 baris Miss | 69% Cover)**:
   - `line 17, 58-60, 63-64, 70, 96, 103, 114, 121-124, 141, 149, 159-169, 196-198, 200, 212-229, 233-235, 251-253, 258, 262, 264, 268, 270, 272-275, 278-281, 283-284, 286-287, 289-290, 292, 294-302, 304, 322`: Penanganan format banner teks, menu bantuan interaktif, rendering tabel toko/resep/inventori, dan prompt konfirmasi keluar.

---

## 6. Rekomendasi & Rencana Tindak Lanjut

### 6.1 Rekomendasi Jangka Pendek (Penyempurnaan Suite Test)

Untuk meningkatkan coverage engine dari 84% menuju >95%, disarankan menambahkan skenario uji berikut:

1. **Unit Test Evaluasi Kondisi Dialog (`tests/test_dialog.py`)**:
   - Tambahkan test parametrik untuk `DialogEngine._eval_condition` yang menguji secara langsung kondisi: `morality_max`, `has_item`, `realm_min`, `academy`, dan `quest_active`.
2. **Unit Test Aksi Battle Non-Serangan (`tests/test_battle.py`)**:
   - Uji teknik bertipe `"defend"` (memverifikasi mitigasi damage 50% atau sesuai power).
   - Uji teknik bertipe `"heal"` (memverifikasi pemulihan HP pemain).
   - Uji pemakaian item pemulihan di tengah giliran battle (`action: "item"`).
   - Uji kegagalan kabur pemain (`_try_flee == False`) dan konfirmasi giliran musuh tetap berjalan.
   - Uji skenario kalah spar yang memicu perolehan `spar_loss_exp`.
3. **Unit Test Transaksi Toko & Racik Edge Cases (`tests/test_session.py`)**:
   - Uji penolakan pembelian saat pedagang tidak menjual item yang diminta.
   - Uji penolakan penjualan saat pemain tidak memiliki item tersebut.
   - Uji penolakan peracikan saat resep tidak terdaftar di registri.
   - Uji aksi `search` herba di Wilayah Berburu untuk skenario roll gagal dan sukses.

### 6.2 Rekomendasi Jangka Panjang (Arsitektur Fase 2 - Arc Sekte)

1. **Pemisahan Kamus State Tracking Quest**:
   - Gantikan penggunaan ganda `state.active_side_quests` untuk progres quest utama dengan memisahkannya menjadi dua field eksplisit:
     ```python
     quest_progress: dict[str, dict] = field(default_factory=dict)  # qid -> {talk: int, start_day: int, ...}
     active_side_quests: dict[str, dict] = field(default_factory=dict)  # qid -> side_quest_data
     ```
2. **Penyederhanaan State UI Proxy**:
   - Hilangkan dualitas `UIState` proxy pada `GameState`. Jadikan `state.mode` atau `view()` sebagai penentu mode tunggal yang sepenuhnya berbasis state riil (`pending_battle`, `pending_dialog`, atau `explore`).
3. **Penambahan Static Type Checking (CI Pipeline)**:
   - Integrasikan `mypy` atau `pyright` pada alur CI untuk memverifikasi tipe dataclass dan dictionary return types tanpa menambah dependensi runtime aplikasi.

---

## 7. Kesimpulan & Penilaian Akhir

Berdasarkan evaluasi menyeluruh, implementasi test suite `pytest` dan rangkaian bugfix engine terkini pada *Tian Xu: Second Life* berada dalam **kondisi sangat matang, kokoh, dan siap rilis**.

- **Reliabilitas**: Seluruh 93 skenario uji berjalan 100% deterministik (<1.5 detik) berkat mocking RNG yang terisolasi.
- **Keamanan**: Serialisasi state terlindungi dari kebocoran mutasi referensi (*deepcopy*) dan filesystem terlindungi dari kerentanan *path traversal* maupun *null-byte injection*.
- **Integritas Aturan**: Validator data statis menegakkan seluruh 16 aturan arsitektur data §14 tanpa celah.

Repositori ini telah memenuhi seluruh kriteria kualitas kode, arsitektur data-driven, dan keandalan pengujian yang dipersyaratkan.
