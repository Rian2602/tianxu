# Laporan Handoff: Gap & Dependency Analysis — Tian Xu: Second Life (Fase 1)

**Dokumen**: `/home/dienk/tian-xu-second-life/.agents/teamwork_preview_explorer_survey_3/handoff.md`  
**Tanggal**: 14 Agustus 2026  
**Peran**: Explorer Subagent (Gap & Dependency Analyst)  
**Status**: Task Selesai (Hard Handoff)

---

## 1. Observation (Hasil Observasi Langsung)

### 1.1 Status Eksekusi dan Verifikasi Basis Kode
- **Pytest**: Menjalankan `python3 -m pytest -q` menghasilkan **93 passed in 1.36s** (100% pass rate, 0 failed).
- **Data Validator**: Menjalankan `python3 tools/validate_data.py` menghasilkan **exit code 0** (`VALIDASI LULUS — quest: 14, dialog: 10, npc: 9, lokasi: 9, item: 6, musuh: 3, ingatan: 4`).
- **Code Coverage**: Berdasarkan evaluasi QA terkini (`docs/superpowers/reviews/2026-08-14-test-suite-evaluation.md`), total coverage mencapai **84%** (1248/1479 baris), dengan 231 baris belum ter-cover pada skenario edge case.

### 1.2 Matriks Fitur Desain (GDD / STORY / ENGINE) vs Implementasi Kode Nyata

| Sistem / Fitur | Spesifikasi Dokumen Desain | Lokasi Implementasi Kode | Status & Temuan Nyata |
|---|---|---|---|
| **Quest Utama (DAG)** | GDD §4, STORY §2, ENGINE §5.1, §6: 1-aktif invariant, 3 babak, 4 cabang (3aa, 3ab, 3b, 3c), konvergensi ke `q_akademi_07`, replayability record. | `src/engine/quest.py:30-228`, `src/engine/dialog.py:31-61`, `data/quests/quests_akademi.json:1-204` | **Selesai & Teruji** (`tests/test_quest_dag.py`). Alur naratif 14 quest utama lengkap dan terhubung secara DAG. |
| **Side Quests (Repeatable)** | GDD §4.4, STORY §7, ENGINE §6.4: 3 side quest (`berburu`, `suqing`, `moyun`), non-conflicting claims, cooldown tracking. | `src/engine/quest.py:231-269`, `data/quests/quests_side.json:1-74` | **Parsial**: Data ada dan alur dasar jalan, tetapi field di data bernama `repeat_cooldown` (`quests_side.json:17,40,63`), sementara validator & ENGINE §5.1 memeriksa `cooldown`. Engine belum menegakkan jeda waktu cooldown antar penyelesaian. |
| **Pertarungan Giliran** | GDD §8, ENGINE §8: Turn-based alternate, serang, 3 teknik per akademi, item, bertahan, kabur, 五行 multiplier (1.5× / 0.67×), regen Qi 5%, kritikal (8% / 1.5×), penalti KO 10% exp. | `src/engine/battle.py:1-362`, `data/techniques.csv:1-11`, `data/enemies.csv:1-5` | **Selesai & Teruji** (`tests/test_battle.py`). Logika formula, wuxing, dan state sync berjalan akurat. |
| **Kompanion Summoning** | GDD §5.1, §7, ENGINE §5.9, §9.4: Roh Awan (`komp_roh_awan`), ikut bertarung otomatis, 50% peluang ditarget musuh, HP persisten, revived di titik aman. | `src/engine/battle.py:22-46, 233-267`, `src/engine/session.py:339-352`, `data/companions.json:1-8` | **Selesai & Teruji** (`tests/test_companion.py`). |
| **Kultivasi & Breakthrough** | GDD §7, STORY §1, ENGINE §5.4, §9.1: 9 ranah, 10 tingkat/ranah, exp aktivitas (meditasi maks 8 jam/hari, berburu, sparing), multiplier akar spiritual, auto-breakthrough di tingkat 10. | `src/engine/cultivation.py:1-59`, `src/engine/session.py:261-283`, `data/realms.csv:1-11` | **Selesai & Teruji** (`tests/test_cultivation.py`). |
| **Ekonomi & Toko Pedagang** | GDD §7, §11.1, ENGINE §5.3, §9.3, §12.3: 1 pedagang (`npc_pedagang`), aksi `shop_buy` dan `shop_sell`, saldo Koin Emas. | `src/engine/session.py:355-399`, `data/npcs.json:26-40`, `src/cli.py:91, 355-399` | **Kesenjangan Kritis pada Web UI**: Handler engine `_shop_buy` dan `_shop_sell` berfungsi, CLI memiliki menu toko lengkap, tetapi `web/static/app.js` sama sekali **tidak memiliki antarmuka modal/tombol toko** untuk membeli item atau menjual material. |
| **Alkimia / Meracik Pil** | GDD §7, §11.1, ENGINE §5.7, §9.3: 2 resep (`rc_pil_qi`, `rc_pil_pemulihan`), dibatasi di lokasi aman. | `src/engine/session.py:400-427`, `data/recipes.json:1-11` | **Kesenjangan UI**: Engine `_craft` berfungsi, tetapi `web/static/app.js:221-226` men-hardcode tombol resep dengan pengecekan `material_herba >= 2`, bukan me-render dinamis dari data `recipes.json`. |
| **Senjata & Peralatan** | GDD §7, §11.1, ENGINE §5.4, §9.3: Slot senjata, `pedang_bambu` (+3), `pedang_angin` (+5), aksi `equip`. | `src/engine/session.py:227-240`, `data/items.csv:6-7` | **Selesai & Teruji** (`tests/test_session.py`). |
| **Panel Tianyuan Ling** | GDD §2.1, §13-6, ENGINE §11.1: Panel UI toggle dengan 3 bagian: Status Misi, Ingatan (x/4 dengan "???" terkunci), dan Log Sistem. | `web/app.py:72-81`, `web/static/app.js:324-347` | **Kesenjangan Desain UI**: Modal web menampilkan daftar ingatan terbuka dan log sistem, namun belum memuat bagian "Status Misi" di dalam modal serta belum menampilkan placeholder slot ingatan terkunci `??? (x/4)`. |
| **Simulasi Waktu & Dunia** | GDD §7, ENGINE §5.6, §9.2: Progresi hari/jam, event malam hari (`loc_ruang_lonceng`), jadwal kehadiran NPC (`npcs.json::schedule`), respawn monster 5 jam (`config.json::world.monster_respawn_hours`). | `src/engine/session.py:210-222, 299-313`, `src/engine/quest.py:122-129` | **Kesenjangan Simulasi Engine**: Event jendela malam dan pergantian hari berfungsi. Namun, `session.py::_hunt` belum menerapkan timer respawn monster (pemain bisa berburu tanpa batas waktu), dan `_talk`/`_spar`/`_shop` belum mengecek ketersediaan jadwal NPC (`schedule`). |
| **Save / Load Sistem** | GDD §11.1, ENGINE §13: Simpan game eksklusif di titik aman (`is_safe`), serialisasi JSON mendalam (`deepcopy`), proteksi path traversal & null-byte. | `src/engine/state.py:130-197`, `src/engine/session.py:26-36, 434-454` | **Selesai & Teruji** (`tests/test_saveload.py`, `tests/test_session.py`). |

---

## 2. Logic Chain (Analisis & Penalaran Kesenjangan)

### 2.1 Kategori Kesenjangan (Gap Classification)

1. **Kesenjangan UI Web (Frontend Gap - P0)**:
   - *Observasi*: Pada `web/static/app.js:178-185`, NPC pedagang hanya diberi tombol `Bicara Pedagang Kios (toko)`. Mengklik tombol ini hanya menjalankan aksi `{type: "talk", npc: "npc_pedagang"}` yang memicu dialog, tanpa pernah membuka antarmuka transaksi beli/jual (`shop_buy`, `shop_sell`).
   - *Implikasi*: Pemain yang memainkan game lewat Web UI tidak bisa membeli `pil_qi`, `pil_pemulihan`, `pedang_bambu`, atau menjual material buruan untuk mendapatkan Koin Emas.
   - *Observasi*: Pada `web/static/app.js:221-226`, logika meracik di-hardcode:
     ```javascript
     const herb = (v.inventory || []).find((i) => i.id === "material_herba");
     if (loc.is_safe && herb && herb.count >= 2) { ... }
     ```
     Ini mengabaikan resep kedua (`rc_pil_pemulihan` yang membutuhkan `material_tulang`) karena UI hanya mengecek herba.

2. **Kesenjangan Sinkronisasi Skema Data & Validator (Data Schema Gap - P1)**:
   - *Observasi*: `data/quests/quests_side.json:17, 40, 63` menggunakan kunci `"repeat_cooldown": 0`. Di sisi lain, `ENGINE_ARCHITECTURE.md §5.1` tabel skema dan `tools/validate_data.py:263` memeriksa `cd = q.get("cooldown")`.
   - *Implikasi*: Terdapat diskrepansi penamaan properti (*naming drift*). Jika `cooldown` diatur di data dengan nama yang salah, validator tidak memvalidasinya, dan engine tidak dapat membaca jeda waktu side quest.

3. **Kesenjangan Logika Simulasi Engine (Engine Simulation Gap - P1)**:
   - *Observasi*: `config.json:52` mendefinisikan `"monster_respawn_hours": 5`. Di `src/engine/session.py:299-313` (`_hunt`), aksi berburu langsung memanggil `self.battle.start([foe], "hunt")` tanpa mencatat waktu terakhir berburu atau memeriksa apakah monster sedang respawn.
   - *Observasi*: `data/npcs.json` mencatat `schedule` harian untuk semua 9 NPC (misal Penatua An jam 09:00–17:00). Pada `src/engine/session.py:158` (`_talk`), engine hanya memvalidasi lokasi statis `npc.get("location") != self.state.location`.
   - *Implikasi*: Sistem simulasi jadwal NPC dan respawn monster yang dirancang di GDD §7 dan ENGINE §9.2 belum aktif di engine level.

4. **Kesenjangan Cakupan Pengujian Unit (QA Edge-Case Gap - P2)**:
   - *Observasi*: Berdasarkan `docs/superpowers/reviews/2026-08-14-test-suite-evaluation.md §5.1`, 231 baris kode pada `dialog.py`, `battle.py`, `session.py`, dan `effects.py` belum diuji secara langsung:
     - Evaluasi kondisi dialog `morality_max`, `has_item`, `realm_min`, `academy`, `quest_active`.
     - Eksekusi teknik pertarungan jenis `"defend"` dan `"heal"` serta pemakaian item di tengah battle.
     - Penanganan kesalahan transaksi toko dan aksi racik invalid.

---

## 3. Structural Dependency Graph (Graf Ketergantungan Struktur)

Berdasarkan analisis ketergantungan komponen, urutan pengerjaan yang tidak melanggar dependensi (*dependency order*) dipetakan sebagai berikut:

```
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 0: Schema Alignment & Backend API Context (Fondasi)               │
│ • Align quests_side.json schema: repeat_cooldown -> cooldown           │
│ • Update web/app.py _context() untuk mengekspos resep & inventori toko │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌──────────────────────────────────────┐   ┌───────────────────────────────────┐
│ TIER 1: Engine Simulation & Logic    │   │ TIER 2: Web UI Feature Parity     │
│ • Implementasi Side Quest Cooldown   │   │ • Antarmuka Toko Web (Beli/Jual)  │
│ • Respawn Timer Monster Berburu (5h) │   │ • Menu Racik Dinamis dari Resep   │
│ • Gating Jadwal NPC pada Aksi        │   │ • Penyempurnaan Tianyuan Panel    │
└──────────────────┬───────────────────┘   └─────────────────┬─────────────────┘
                   │                                         │
                   └───────────────────┬─────────────────────┘
                                       ▼
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 3: Test Hardening & Arc Completion Polish (Integrasi)             │
│ • Tambah Unit Test Evaluasi Kondisi, Teknik Battle Defend/Heal, Item   │
│ • Modal Ringkasan Akhir Arc 1 (q_akademi_07 closure)                   │
│ • Regression E2E Web & CLI Automated Playtest                          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Rekomendasi Roadmap Subagent-Driven Development (SDD)

Berikut adalah paket tugas terstruktur dan terinci (*actionable tasks*), siap dieksekusi oleh tim subagent:

### Epic 1: Web UI Feature Parity & Context API (Prioritas: P0)

#### Task EP1-T1: Implementasi Antarmuka Toko Pedagang di Web UI
- **Prioritas**: `P0 (Blokir Fungsional Web)`
- **Tujuan**: Memungkinkan pemain melakukan transaksi beli/jual item di Web UI sesuai GDD §11.1 & ENGINE §12.3.
- **Berkas yang Dimodifikasi**:
  - `web/app.py` (tambahkan daftar item toko ke dalam `_context()`)
  - `web/static/app.js` (tambahkan render modal/panel toko saat berinteraksi dengan pedagang)
  - `web/static/index.html` & `web/static/style.css` (styling panel transaksi toko)
  - `tests/test_web.py` (tambahkan uji endpoint `shop_buy` dan `shop_sell` via web)
- **Spesifikasi & Batasan**:
  - Saat berada di lokasi berpedagang (`npc_pedagang` di `loc_pasar`), tampilkan tombol `[Toko]`.
  - Panel toko menampilkan tab Beli (Pil Qi 50g, Pil Pemulihan 40g, Herba 8g, Pedang Bambu 100g) dan tab Jual (Herba 6g, Tulang 10g).
  - Mengirim payload `POST /api/action` dengan `{type: "shop_buy", item: "<id>", count: 1}` dan `{type: "shop_sell", item: "<id>", count: 1}`.
  - Memperbarui tampilan Koin Emas dan inventori seketika.

#### Task EP1-T2: Dinamisasi Menu Alkimia / Peracikan di Web UI
- **Prioritas**: `P0 (Blokir Fungsional Web)`
- **Tujuan**: Menghilangkan hardcode herba di `app.js` dan me-render resep racik secara dinamis dari data registri.
- **Berkas yang Dimodifikasi**:
  - `web/app.py` (ekspos `registry.recipes` pada payload `_context()`)
  - `web/static/app.js:221-226` (refactor render menu racik berbasis ketersediaan bahan)
  - `tests/test_web.py`
- **Spesifikasi & Batasan**:
  - Di lokasi aman (`is_safe == true`), iterasi semua resep dari context.
  - Tampilkan tombol aktif jika bahan dalam inventori mencukupi (misal: 2 Herba untuk Pil Qi, 2 Tulang untuk Pil Pemulihan).

#### Task EP1-T3: Penyesuaian Panel Tianyuan Ling Sesuai Spesifikasi §11.1
- **Prioritas**: `P1 (Desain UI)`
- **Tujuan**: Menyelaraskan tampilan modal Tianyuan Ling dengan kontrak teknis `ENGINE_ARCHITECTURE.md §11.1`.
- **Berkas yang Dimodifikasi**:
  - `web/app.py` (sertakan status quest aktif dan total ingatan 4 slot)
  - `web/static/app.js:324-347` & `web/static/style.css`
  - `tests/test_web.py`
- **Spesifikasi & Batasan**:
  - Panel terdiri dari 3 seksi:
    1. **Status Misi**: Menampilkan quest utama aktif, objektif, progres (0/1), dan side quest aktif.
    2. **Ingatan (x/4)**: Menampilkan judul ingatan terbuka (bisa dibaca) dan placeholder `• ??? (terkunci)` untuk slot yang belum terbuka.
    3. **Log Sistem**: 30 notifikasi sistem terakhir.

---

### Epic 2: Engine Simulation & Data Integrity (Prioritas: P1)

#### Task EP2-T1: Sinkronisasi Skema Side Quest & Penegakan Cooldown di QuestEngine
- **Prioritas**: `P1`
- **Tujuan**: Merapikan field `cooldown` pada data side quest dan menegakkan jeda waktu pengulangan quest.
- **Berkas yang Dimodifikasi**:
  - `data/quests/quests_side.json` (ubah `"repeat_cooldown": 0` menjadi `"cooldown": 2` atau nilai jam positif)
  - `src/engine/quest.py:231-246` (`is_offerable` memeriksa `state.quest_completion_time[qid] + cooldown <= current_time`)
  - `src/engine/state.py` (tambahkan tracking waktu selesai side quest pada serialisasi state)
  - `tools/validate_data.py` (verifikasi aturan 8 & 9 tetap exit 0)
  - `tests/test_quest_dag.py`, `tests/test_validator.py`
- **Spesifikasi & Batasan**:
  - Side quest repeatable yang baru saja selesai harus menunggu `cooldown` jam sebelum dapat diambil kembali.

#### Task EP2-T2: Simulasi Waktu: Respawn Monster Berburu & Jadwal NPC
- **Prioritas**: `P1`
- **Tujuan**: Menerapkan mekanisme cooldown berburu dan integrasi jadwal NPC pada aksi sesi sesuai GDD §7 & ENGINE §9.2.
- **Berkas yang Dimodifikasi**:
  - `src/engine/session.py:299-313` (`_hunt` memeriksa `world.monster_respawn_hours` / mencatat waktu perburuan)
  - `src/engine/session.py:153-165` (`_talk` dan `_spar` memeriksa kesesuaian waktu `schedule` NPC)
  - `tests/test_session.py`, `tests/test_cli.py`
- **Spesifikasi & Batasan**:
  - Berburu di `loc_wilayah_berburu` memajukan waktu 1 jam atau memiliki jeda respawn 5 jam in-game.
  - Jika pemain mengajak bicara NPC di luar jadwal aktifnya, berikan dialog/log naratif bahwa NPC sedang beristirahat/tidak di tempat.

#### Task EP2-T3: Layar Ringkasan Akhir Arc 1 (Arc Completion Closure)
- **Prioritas**: `P1`
- **Tujuan**: Memberikan penutup visual/teks yang jelas saat pemain menyelesaikan quest `q_akademi_07` (DoD GDD §11.2).
- **Berkas yang Dimodifikasi**:
  - `src/engine/session.py:458-507` (tambahkan flag `arc_completed: true` pada `view()` pasca `q_akademi_07`)
  - `src/cli.py` & `web/static/app.js` (render banner/modal penutup Arc 1 beserta rekap pilihan cabang, moralitas akhir, dan ranah pencapaian)
  - `tests/test_cli.py`, `tests/test_web.py`

---

### Epic 3: Hardening Test Coverage & Dokumentasi (Prioritas: P2)

#### Task EP3-T1: Penutupan Celah Test Engine Menuju >95% Coverage
- **Prioritas**: `P2`
- **Tujuan**: Menutup 231 baris missing coverage yang diidentifikasi dalam review QA.
- **Berkas yang Dimodifikasi**:
  - `tests/test_dialog.py` (uji langsung kondisi `morality_max`, `has_item`, `realm_min`, `academy`, `quest_active`)
  - `tests/test_battle.py` (uji teknik `defend`, `heal`, aksi `item` dalam battle, penalti kekalahan spar `spar_loss_exp`, kegagalan kabur `flee`)
  - `tests/test_session.py` (uji error edge cases pada transaksi toko, pencarian herba roll gagal, pemakaian item invalid)
- **Spesifikasi & Batasan**:
  - Seluruh pengujian wajib 100% deterministik tanpa flaky tests.

#### Task EP3-T2: Sinkronisasi Dokumen Arsitektur & GDD
- **Prioritas**: `P2`
- **Tujuan**: Memperbarui dokumen resmi untuk mengeliminasi sisa referensi usang.
- **Berkas yang Dimodifikasi**:
  - `docs/ENGINE_ARCHITECTURE.md` (§12.3: perjelas bahwa Tianyuan Ling adalah API GET/view modal, bukan session action mutating; perbarui catatan status implementasi §16-§17).
  - `docs/DESIGN_SUMMARY.md`

---

## 5. Caveats (Batasan & Asumsi Investigasi)

1. **Integritas Read-Only**: Investigasi ini murni audit analitis tanpa melakukan mutasi langsung pada kode sumber `src/`, `data/`, `web/`, atau `tests/`.
2. **Karakteristik Single Player Lokal**: Server web `web/app.py` dirancang untuk single session per proses (`ThreadingHTTPServer`), sehingga evaluasi concurrency multi-user tidak masuk dalam ruang lingkup Fase 1.
3. **Data Fase 1**: Seluruh data yang ada saat ini ditargetkan untuk Arc Akademi (durasi 1–2 jam). Penambahan konten Arc Sekte dan Arc Kekaisaran dijadwalkan untuk Fase 2 sesuai roadmap GDD §12.

---

## 6. Conclusion (Kesimpulan Akhir)

1. **Kondisi Fondasi**: Core game loop (Quest DAG 14 quest dengan 4 cabang sikap, dialog engine ber-condition, pertarungan turn-based Wuxing, progresi kultivasi 10 tingkat & breakthrough, kompanion binatang roh, serta serialisasi save aman) berada dalam **kondisi sangat kokoh, lolos 93/93 tests, dan 16/16 aturan validator data**.
2. **Kesenjangan Utama**: Kesenjangan terbesar saat ini terletak pada **Web UI frontend (`web/static/app.js`) yang belum memiliki antarmuka Toko Pedagang (beli/jual)**, menu racik yang masih hardcoded, dan tampilan panel Tianyuan Ling yang belum lengkap 3 seksi.
3. **Kesiapan Eksekusi**: Rekomendasi roadmap telah dipaketkan ke dalam **3 Epic dan 8 Task SDD mandiri**, terurut secara presisi berdasarkan graf dependensi struktural, dengan prioritas tertinggi (P0) difokuskan pada pemenuhan paritas fitur Web UI.

---

## 7. Verification Method (Metode Verifikasi Independen)

Untuk mereproduksi dan memverifikasi seluruh temuan dalam laporan ini:

```bash
# 1. Verifikasi seluruh rangkaian test otomatis saat ini
python3 -m pytest -q

# 2. Verifikasi 16 aturan integritas data statis
python3 tools/validate_data.py

# 3. Verifikasi ketiadaan fitur Toko pada frontend web
# Periksa bahwa app.js tidak memanggil aksi shop_buy / shop_sell
grep -n "shop_buy" web/static/app.js || echo "KONFIRMASI: shop_buy tidak ada di web/static/app.js"
grep -n "shop_sell" web/static/app.js || echo "KONFIRMASI: shop_sell tidak ada di web/static/app.js"

# 4. Verifikasi diskrepansi penamaan field repeat_cooldown vs cooldown
grep -n "repeat_cooldown" data/quests/quests_side.json
grep -n "cooldown" tools/validate_data.py
```
