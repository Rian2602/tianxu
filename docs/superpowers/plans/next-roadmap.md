# Peta Jalan Subagent-Driven Development (SDD Roadmap)
# Tian Xu: Second Life — Fase 1 (Arc Akademi)

**Dokumen**: `docs/superpowers/plans/next-roadmap.md`  
**Versi**: 1.1.0 (Otoritatif & Terverifikasi Adversarial)  
**Tanggal**: 14 Agustus 2026  
**Status**: Siap Eksekusi Paralel (Ready for Parallel SDD Execution)  
**Arsitektur Target**: Python 3.12 (stdlib-only), Web UI statis stdlib HTTP, CLI ANSI, Data-Driven (`data/`), Pytest Suite.

---

## 1. Ringkasan Eksekutif & Status Terkini Fase 1

### 1.1 Status Baseline Proyek
Berdasarkan hasil investigasi teknis, eksekusi pengujian, dan audit adversarial menyeluruh terhadap repositori *Tian Xu: Second Life*, kondisi kesehatan basis kode berada pada tingkat stabilitas yang sangat tinggi:

- **Pengujian Otomatis (Pytest)**: **93/93 skenario uji lulus (100% pass rate)** dalam tempo ~1.37 detik tanpa kegagalan, peringatan, atau regresi.
- **Validasi Integritas Data (`tools/validate_data.py`)**: **16/16 aturan arsitektur §14 lulus dengan exit code 0** (memvalidasi 14 quest, 10 dialog, 9 NPC, 9 lokasi, 6 item, 3 musuh, dan 4 ingatan).
- **Cakupan Pengujian (Code Coverage)**: Total coverage basis kode mencapai **84%** (1.248 baris tereksekusi dari 1.479 total baris logika aktif pada `src/`).
- **Keamanan Sistem**: Proteksi terhadap *path traversal* (`../`), *null-byte injection* (`\x00`), dan penolakan *save corrupted* telah diuji dan berfungsi secara tangguh.

### 1.2 Ringkasan Capaian vs Kesenjangan Fase 1 (Arc Akademi)

#### Yang Telah Selesai & Terverifikasi (Done & Verified)
1. **Core Loop Kultivasi**: Sistem 9 ranah kultivasi × 10 tingkat, formula eksponensial exp ($10 \times 1.2^{\text{level}-1}$), multiplier akar spiritual (0.8× s.d. 1.5×), meditasi titik aman (maks 8 jam/hari), dan terobosan otomatis (*auto-breakthrough*) di tingkat 10.
2. **Mesin Pertarungan (Battle Engine)**: Sistem *turn-based* bergantian tetap, mitigasi pertahanan, siklus keunggulan elemen 五行 (Wuxing 1.5× / 0.67×), serangan kritikal (8% / 1.5×), regenerasi 5% Qi per ronde, aksi bertahan (*guard*), kabur (*flee*), dan penalti KO (potong 10% exp progres + respawn titik aman).
3. **Sistem Kompanion (Akademi Summoning)**: Integrasi Roh Awan (`komp_roh_awan`) yang bertindak otomatis tiap ronde, pengalihan 50% target musuh, *scaling* stat per level, serta persistensi HP dan pemulihan di titik aman.
4. **Graf Alur Cerita & Quest DAG**: 11 quest utama DAG dengan invariant tepat 1 quest utama aktif, 4 cabang insiden Lonceng Angin Panjang (`3aa` Konfrontasi, `3ab` Bukti Diam, `3b` Ambil Untung, `3c` Berdiam Diri) yang berkonvergensi ke `q_akademi_07`, serta pencatatan *replayability*.
5. **Naratif Tianyuan Ling**: Pemulihan 4 ingatan naratif (`mem_01` s.d. `mem_04`) dengan pemisahan tegas antara narasi dan kekuatan mekanik.
6. **Ekonomi & Alkimia Dasar**: Logika transaksi toko pedagang (`_shop_buy`, `_shop_sell`) dan 2 resep racik pil (`rc_pil_qi`, `rc_pil_pemulihan`) di engine level dan terminal CLI.
7. **Keamanan Save/Load**: Mekanisme simpan eksklusif di titik aman (`is_safe: true`), serialisasi JSON berbasis `copy.deepcopy`, dan penolakan payload berbahaya.

#### Kesenjangan yang Wajib Diselesaikan (Gaps to Address)

> **Status 2026-08-14**: seluruh gap di bawah telah **dieksekusi dan diverifikasi** melalui Epic 1 (Web UI), Epic 2 (Simulasi Engine), dan EP3-T1 (QA hardening) — baseline ini historis. Verifikasi implementasi: `docs/ENGINE_ARCHITECTURE.md` §17 (fitur `SELESAI (Verified)`).

1. **Paritas Web UI (P0 - Blokir Fungsional Frontend)**:
   - Antarmuka Toko Pedagang (Beli/Jual) belum tersedia di Web UI (`app.js`), sehingga pemain di web tidak bisa membeli pil/senjata atau menjual material buruan.
   - Menu peracikan pil di Web UI masih men-hardcode pengecekan Herba saja, mengabaikan resep Pil Pemulihan berbasis Tulang.
   - Modal panel Tianyuan Ling belum menampilkan seksi Status Misi secara modular (memisahkan main quest dan side quests) dan belum menampilkan placeholder slot ingatan terkunci `??? (x/4)` sesuai kontrak §11.1.
2. **Integritas Simulasi Engine & Skema Data (P1)**:
   - Diskrepansi nama field `repeat_cooldown` pada `data/quests/quests_side.json` terhadap spesifikasi `cooldown` di validator & engine; belum ada penegakan waktu jeda cooldown side quest dengan deserialisasi defensif `.get()`.
   - Mekanisme timer respawn monster berburu (5 jam in-game) dan pengecekan jadwal aktif NPC (`schedule`) harian berulang belum diterapkan pada `session.py` (wajib sinkronisasi dengan test suite hunting beruntun).
   - Belum adanya layar/modal ringkasan penutup formal (*Arc Completion Closure*) setelah menyelesaikan quest akhir `q_akademi_07`, dengan pemisahan tegas antara logika backend/CLI dan modal Web UI berkemampuan *single-fire dismissal*.
3. **Hardening Kualitas & Dokumentasi (P2)**:
   - Terdapat 231 baris *edge case* pada `dialog.py`, `battle.py`, `session.py`, dan `effects.py` yang belum diuji secara langsung (target coverage >95%).
   - Sinkronisasi sisa catatan historis pada `docs/ENGINE_ARCHITECTURE.md` dan `docs/DESIGN_SUMMARY.md`.

---

## 2. Matriks Kesenjangan (Gap Analysis Matrix)

Berikut adalah pemetaan silang menyeluruh antara spesifikasi desain resmi (`GDD.md`, `DESIGN_SUMMARY.md`, `STORY_FASE1.md`, `ENGINE_ARCHITECTURE.md`, `AGENTS.md`) terhadap kondisi nyata basis kode saat ini:

| # | Subsistem / Fitur | Referensi Spesifikasi | Lokasi Implementasi Kode | Status & Kondisi Nyata | Prioritas |
|---|---|---|---|---|---|
| 1 | **Quest Utama (DAG)** | GDD §4, STORY §2, ENGINE §5.1, §6 | `src/engine/quest.py:30-228`, `data/quests/quests_akademi.json` | **DONE (Verified)**. 11 quest utama terhubung asiklik, 4 cabang menyatu di `q_akademi_07`. | - |
| 2 | **Side Quests (Repeatable)** | GDD §4.4, STORY §7, ENGINE §6.4 | `src/engine/quest.py:231-269`, `data/quests/quests_side.json` | **PARTIAL**. 3 side quest jalan, tetapi nama field di JSON `repeat_cooldown` (bukan `cooldown`) dan engine belum memblokir pengulangan instan sebelum jeda waktu selesai. | **P1** |
| 3 | **Pertarungan Giliran & Wuxing** | GDD §8, ENGINE §8, DESIGN §4 | `src/engine/battle.py:1-362`, `data/techniques.csv` | **DONE (Verified)**. Turn-based alternate, damage formula, wuxing (1.5× / 0.67×), Qi regen 5%, crit 8%. | - |
| 4 | **Kompanion Roh Awan** | GDD §5.1, ENGINE §9.4 | `src/engine/battle.py:233-267`, `data/companions.json` | **DONE (Verified)**. Bertarung otomatis, 50% target musuh, HP persisten, revive di titik aman. | - |
| 5 | **Kultivasi & Breakthrough** | GDD §7, ENGINE §5.4, §9.1 | `src/engine/cultivation.py`, `data/realms.csv` | **DONE (Verified)**. 9 ranah × 10 level, exp curve, multiplier akar, auto-breakthrough. | - |
| 6 | **Meditasi Grounding** | DESIGN §3, ENGINE §12.3 | `src/engine/session.py:261-283` | **DONE (Verified)**. 2 exp/jam, dibatasi di titik aman, kuota maks 8 jam/hari. | - |
| 7 | **Toko Pedagang (Engine & CLI)** | GDD §7, ENGINE §5.3, §9.3 | `src/engine/session.py:355-399`, `src/cli.py` | **DONE (Verified)**. Handler `_shop_buy` dan `_shop_sell` berfungsi penuh di engine dan CLI. | - |
| 8 | **Toko Pedagang (Web UI)** | GDD §11.1, ENGINE §12.3 | `web/static/app.js:178-185`, `web/app.py` | **GAP (P0)**. Tombol NPC pedagang hanya memicu dialog; tidak ada modal transaksi beli/jual di frontend web. | **P0** |
| 9 | **Alkimia Dinamis (Web UI)** | GDD §7, ENGINE §5.7 | `web/static/app.js:221-226` | **GAP (P0)**. Resep di-hardcode ke Herba saja. Resep Pil Pemulihan (Tulang) terabaikan di web UI. | **P0** |
| 10 | **Panel 3-Seksi Tianyuan Ling** | GDD §2.1, ENGINE §11.1 | `web/static/app.js:324-347`, `web/app.py:72-81` | **GAP (P1)**. Modal web belum memuat Status Misi modular dan belum menampilkan placeholder `???` untuk ingatan terkunci. | **P1** |
| 11 | **Respawn Monster & Jadwal NPC** | GDD §7, ENGINE §9.2 | `src/engine/session.py:299-313, 153-165` | **GAP (P1)**. Berburu belum dibatasi timer respawn 5 jam; aksi `_talk`/`_spar` belum mengecek jam aktif rutin harian NPC. | **P1** |
| 12 | **Layar Ringkasan Akhir Arc 1** | GDD §11.2, DoD | `src/cli.py`, `web/static/app.js` | **GAP (P1)**. Pasca `q_akademi_07`, belum ada layar rekapitulasi pilihan cabang, moralitas, dan ranah (backend, CLI & modal web). | **P1** |
| 13 | **Cakupan Pengujian Edge Cases** | QA Review §5.1 | `tests/` | **GAP (P2)**. 231 baris edge cases (evaluasi kondisi langka, jurus defend/heal, item di battle) belum ter-cover. | **P2** |
| 14 | **Sinkronisasi Dokumen Arsitektur** | ENGINE §12, §16-17 | `docs/ENGINE_ARCHITECTURE.md` | **GAP (P2)**. Perlu sinkronisasi catatan historis dan dokumentasi endpoint payload web terkini. | **P2** |

---

## 3. Peta Jalan & Rencana Prioritas (Prioritized Roadmap Epics)

Peta jalan pengembangan dibagi menjadi 3 Epic utama dengan urutan prioritas yang ketat:

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│ EPIC 1: Web UI Feature Parity & Context API (Prioritas: P0 - Urgent Blocker)      │
│ Mengangkat fungsionalitas Web UI agar setara 100% dengan kapabilitas Engine & CLI  │
├───────────────────────────────────────────────────────────────────────────────────┤
│ • EP1-T1: Antarmuka Toko Pedagang Web UI (Beli/Jual)                              │
│ • EP1-T2: Dinamisasi Menu Alkimia / Peracikan Berbasis Resep                      │
│ • EP1-T3: Penyesuaian Panel 3-Seksi Tianyuan Ling (Status Misi, Slot Terkunci)    │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ EPIC 2: Simulasi Engine & Integritas Data (Prioritas: P1 - Core Enhancements)     │
│ Memperkuat simulasi dunia, konsistensi data schema, dan penutupan formal Arc 1    │
├───────────────────────────────────────────────────────────────────────────────────┤
│ • EP2-T1: Sinkronisasi Skema Side Quest (cooldown) & Penegakan di QuestEngine     │
│ • EP2-T2: Simulasi Waktu: Respawn Monster Berburu (5 Jam) & Jadwal Harian NPC     │
│ • EP2-T3: Rekapitulasi Akhir Arc 1 (Backend/CLI Closure & Frontend UI Modal)     │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ EPIC 3: Hardening QA & Sinkronisasi Dokumen (Prioritas: P2 - Quality & Docs)      │
│ Mengamankan keandalan jangka panjang dan menjaga sinkronisasi dokumentasi resmi  │
├───────────────────────────────────────────────────────────────────────────────────┤
│ • EP3-T1: Penutupan Edge Cases Unit Test Menuju >95% Branch Coverage              │
│ • EP3-T2: Sinkronisasi Dokumen Arsitektur & GDD Terhadap Basis Kode Terkini       │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Spesifikasi Detail Tugas SDD (Actionable SDD Task Specifications)

Setiap tugas di bawah ini telah dirancang secara mandiri (*self-contained*), memiliki kontrak teknis yang presisi, kriteria penerimaan berbasis checklist, dan template prompt subagent yang siap disalin langsung ke dalam loop Subagent-Driven Development.

---

### Task EP1-T1: Antarmuka Toko Pedagang Web UI (Beli / Jual)

#### Informasi Tugas
- **ID Tugas**: `EP1-T1`
- **Judul**: Implementasi Antarmuka Transaksi Toko Pedagang di Web UI
- **Prioritas**: `P0 (Blokir Fungsional Web UI)`
- **Estimasi Kompleksitas**: `M (Medium - 3 Story Points / 1 Jam)`
- **Fase Eksekusi**: 
  - **Fase Backend (Wave 1)**: Modifikasi `web/app.py` & `tests/test_web.py`
  - **Fase Frontend (Wave 2 Jalur A)**: Modifikasi `web/static/app.js`, `web/static/index.html`, `web/static/style.css`

#### Motivasi & User Story
*Sebagai pemain Web UI, saya ingin dapat membuka menu toko saat berbicara atau berinteraksi dengan Pedagang Kios di Pasar Changfeng agar saya dapat membeli pil penyembuh/senjata dan menjual material hasil buruan untuk mendapatkan Koin Emas.*

#### Daftar Berkas Target
1. `web/app.py` (Fase Wave 1: ekspos data katalog toko pedagang aktif di `_context()`)
2. `web/static/index.html` (Fase Wave 2A: tambahkan kontainer modal/panel toko `#modal-shop`)
3. `web/static/app.js` (Fase Wave 2A: fungsi `renderShop()`, `openShop()`, `closeShop()`, dan event handler beli/jual)
4. `web/static/style.css` (Fase Wave 2A: styling panel transaksi toko bertema xianxia dark-gold)
5. `tests/test_web.py` (Fase Wave 1: pengujian endpoint aksi `shop_buy` dan `shop_sell` via REST API)

#### Spesifikasi Teknis & Kontrak Data/API
1. **Backend Context (`web/app.py::_context`)**:
   Sertakan katalog toko pedagang yang berada di lokasi saat ini ke dalam payload context:
   ```python
   merchant_shop = None
   for n in registry.npcs:
       if n.get("shop") and n.get("location") == session.state.location:
           merchant_shop = {
               "merchant_id": n["id"],
               "merchant_name": n["name"],
               "buy": [
                   {"item": s["item"], "name": registry.item(s["item"])["name"],
                    "price": s["price"], "type": registry.item(s["item"]).get("type", "")}
                   for s in n["shop"].get("buy", [])
               ],
               "sell": [
                   {"item": s["item"], "name": registry.item(s["item"])["name"],
                    "price": s["price"], "type": registry.item(s["item"]).get("type", "")}
                   for s in n["shop"].get("sell", [])
               ],
           }
           break
   # Sertakan ke dalam dictionary context:
   # context["merchant_shop"] = merchant_shop
   ```
2. **Frontend UI Interaction (`web/static/app.js`)**:
   - Di `renderExplore()`, jika `c.merchant_shop` ada, tambahkan tombol aksi:
     `<button class="btn btn-gold" onclick="openShop()">Buka Toko Pedagang</button>`.
   - Fungsi `renderShop()` menampilkan 2 tab/seksi:
     - **Tab Beli**: Menampilkan daftar item yang dijual pedagang, harga beli emas, dan tombol `Beli (1×)`. Dinonaktifkan jika `gold < price`.
     - **Tab Jual**: Menampilkan daftar item dalam inventori pemain yang diterima pedagang, harga jual emas, jumlah yang dimiliki pemain, dan tombol `Jual (1×)`.
   - Mengirim aksi ke backend via `act({type: "shop_buy", item: itemId, count: 1})` dan `act({type: "shop_sell", item: itemId, count: 1})`.
   - Setelah aksi berhasil, perbarui tampilan saldo Koin Emas dan inventori secara reaktif.

#### Pra-syarat & Dependensi
- Menggunakan handler `session.py::_shop_buy` dan `_shop_sell` yang sudah teruji di backend.

#### Rencana Pengujian & Validasi
- `python3 -m pytest tests/test_web.py` — Pengujian siklus penuh HTTP POST `shop_buy` dan `shop_sell`.
- `python3 tools/validate_data.py` — Pastikan integritas data tetap exit 0.

#### Kriteria Penerimaan (Acceptance Criteria)
- [ ] Backend `_context()` mengekspos `merchant_shop` saat berada di lokasi pedagang.
- [ ] Tombol `Buka Toko` muncul di Web UI saat pemain berada di `loc_pasar`.
- [ ] Modal/panel toko dapat dibuka dan ditutup dengan mulus.
- [ ] Pemain dapat membeli item (`pil_qi`, `pil_pemulihan`, `material_herba`, `pedang_bambu`) dan saldo emas terpotong dengan benar.
- [ ] Pemain dapat menjual material (`material_herba`, `material_tulang`) dan memperoleh Koin Emas.
- [ ] Tombol beli terdisable atau memberikan notifikasi yang sesuai jika emas tidak mencukupi.
- [ ] Seluruh unit test di `tests/test_web.py` lulus 100%.

#### Template Prompt Subagent (Wave 1 Backend Context)
```markdown
Anda adalah implementer backend subagent untuk Tian Xu: Second Life (Wave 1).
Tugas Anda adalah mengekspos katalog toko pedagang di context web API (Task ID: EP1-T1 Backend).

Target Berkas:
- `web/app.py`
- `tests/test_web.py`

Instruksi:
1. Perbarui `web/app.py::_context()` untuk menyertakan `merchant_shop` (katalog buy/sell dengan nama item & harga) jika ada NPC pedagang di lokasi sesi saat ini.
2. Tambahkan unit test baru di `tests/test_web.py` untuk memverifikasi endpoint `shop_buy` dan `shop_sell` melalui web action handler serta keberadaan `merchant_shop` di context.
3. Jalankan `python3 -m pytest tests/test_web.py` dan `python3 tools/validate_data.py` untuk memastikan kelulusan 100%.
```

---

### Task EP1-T2: Dinamisasi Menu Alkimia / Peracikan Berbasis Resep

#### Informasi Tugas
- **ID Tugas**: `EP1-T2`
- **Judul**: Dinamisasi Menu Alkimia / Peracikan di Web UI Berdasarkan Data Registri Resep
- **Prioritas**: `P0 (Blokir Fungsional Web UI)`
- **Estimasi Kompleksitas**: `S (Small - 1.5 Story Points / 30 Menit)`
- **Fase Eksekusi**: 
  - **Fase Backend (Wave 1)**: Modifikasi `web/app.py` & `tests/test_web.py`
  - **Fase Frontend (Wave 2 Jalur A)**: Modifikasi `web/static/app.js`

#### Motivasi & User Story
*Sebagai pemain Web UI, saya ingin melihat seluruh resep pil yang dapat saya racik secara dinamis di titik aman (termasuk Pil Pemulihan dari Tulang Serigala), sehingga saya dapat memanfaatkan semua hasil buruan untuk bertahan hidup.*

#### Daftar Berkas Target
1. `web/app.py` (Fase Wave 1: ekspos `registry.recipes` ke dalam payload `_context()`)
2. `web/static/app.js` (Fase Wave 2A: refactor blok render racik di `renderExplore()`)
3. `tests/test_web.py` (Fase Wave 1: validasi payload context resep)

#### Spesifikasi Teknis & Kontrak Data/API
1. **Backend Context (`web/app.py::_context`)**:
   Tambahkan metadata seluruh resep alkimia ke dalam dictionary context:
   ```python
   "recipes": [
       {
           "id": r["id"],
           "result": r["result"],
           "result_name": registry.item(r["result"])["name"],
           "count": r.get("count", 1),
           "ingredients": [
               {"item": ing["item"], "name": registry.item(ing["item"])["name"], "count": ing["count"]}
               for ing in r.get("ingredients", [])
           ],
           "description": r.get("description", ""),
       }
       for r in registry.recipes
   ]
   ```
2. **Frontend UI Rendering (`web/static/app.js`)**:
   Gantikan blok statis pengecekan `material_herba` dengan iterasi dinamis:
   ```javascript
   // racik resep (hanya di lokasi aman)
   if (loc.is_safe && c.recipes && c.recipes.length) {
     const invMap = {};
     (v.inventory || []).forEach((i) => { invMap[i.id] = i.count; });

     const availableRecipes = c.recipes.filter((r) => {
       return r.ingredients.every((ing) => (invMap[ing.item] || 0) >= ing.count);
     });

     if (availableRecipes.length) {
       let craftHtml = `<div class="action-row"><span class="action-label">Racik:</span>`;
       availableRecipes.forEach((r) => {
         const ingText = r.ingredients.map((ing) => `${ing.count} ${ing.name}`).join(", ");
         craftHtml += `<button class="btn" onclick='act({type:"craft",recipe:"${r.id}"})'>` +
                      `Racik ${esc(r.result_name)} (${esc(ingText)})</button> `;
       });
       craftHtml += `</div>`;
       html += craftHtml;
     }
   }
   ```

#### Pra-syarat & Dependensi
- Menggunakan `session.py::_craft` yang sudah teruji.

#### Rencana Pengujian & Validasi
- `python3 -m pytest tests/test_web.py` — Verifikasi payload context dan eksekusi aksi craft.
- `python3 tools/validate_data.py` — Verifikasi data resep.

#### Kriteria Penerimaan (Acceptance Criteria)
- [ ] Payload `_context()` pada web server memuat daftar resep lengkap beserta detail bahan.
- [ ] Web UI me-render tombol racik secara dinamis untuk setiap resep yang bahannya mencukupi di inventori pemain.
- [ ] Pemain dengan 2 Material Tulang dapat meracik Pil Pemulihan dari antarmuka Web UI.
- [ ] Tombol racik tidak muncul di luar lokasi aman (`is_safe: false`).

#### Template Prompt Subagent (Wave 1 Backend Context)
```markdown
Anda adalah implementer backend subagent untuk Tian Xu: Second Life (Wave 1).
Tugas Anda adalah mengekspos registri resep pada context API web server (Task ID: EP1-T2 Backend).

Target Berkas:
- `web/app.py`
- `tests/test_web.py`

Instruksi:
1. Perbarui `web/app.py::_context()` untuk menyertakan list `recipes` lengkap dari `registry.recipes` (id, result, result_name, count, ingredients dengan item_name dan count).
2. Tambahkan assertion di `tests/test_web.py` untuk memastikan field `recipes` ada pada payload context state.
3. Jalankan `python3 -m pytest tests/test_web.py` dan laporkan hasil pengujian.
```

---

### Task EP1-T3: Penyesuaian Panel 3-Seksi Tianyuan Ling & Sinkronisasi Payload

#### Informasi Tugas
- **ID Tugas**: `EP1-T3`
- **Judul**: Penyesuaian Panel UI Tianyuan Ling Menjadi 3 Seksi Sesuai Spesifikasi §11.1 & Modular Payload
- **Prioritas**: `P1 (Desain & UI Alignment)`
- **Estimasi Kompleksitas**: `S (Small - 2 Story Points / 45 Menit)`
- **Fase Eksekusi**: 
  - **Fase Backend (Wave 1)**: Modifikasi `web/app.py` & `tests/test_web.py`
  - **Fase Frontend (Wave 2 Jalur A)**: Modifikasi `web/static/app.js`, `web/static/style.css`

#### Motivasi & User Story
*Sebagai pemain, saya ingin membuka artefak Tianyuan Ling dan melihat panel terpadu 3 seksi: Status Misi (memisahkan Main Quest dan Side Quests agar side quest tetap terlihat meski main quest selesai), Daftar 4 Ingatan (dengan penanda slot terkunci ???), dan Log Sistem, agar sesuai dengan atmosfer naratif kultivasi Xianxia yang misterius.*

#### Daftar Berkas Target
1. `web/app.py` (Fase Wave 1: perbarui `_tianyuan_payload()` dengan struktur modular `{"main": ..., "side_quests": [...]}` dan 4 slot ingatan lengkap)
2. `web/static/app.js` (Fase Wave 2A: perbarui fungsi `openTianyuan()` untuk me-render 3 seksi)
3. `web/static/style.css` (Fase Wave 2A: penataan visual slot ingatan terkunci dan seksi panel)
4. `tests/test_web.py` (Fase Wave 1: sinkronisasi pengujian endpoint `/api/tianyuan` terhadap skema 4 slot ingatan dan status misi modular)

#### Spesifikasi Teknis & Kontrak Data/API
1. **Backend Payload (`web/app.py::_tianyuan_payload`)**:
   Formatkan payload `/api/tianyuan` agar memuat 3 seksi lengkap dengan pemisahan modular misi:
   ```python
   def _tianyuan_payload() -> dict:
       if not session:
           return {
               "mission": {"main": None, "side_quests": []},
               "memories": [],
               "unlocked_count": 0,
               "total_count": 4,
               "system_log": [],
           }
       
       # 1. Status Misi (Modular: side_quests tetap persisten walau main quest selesai / None)
       q = session.quest.current_main()
       mission = {
           "main": {
               "id": q["id"],
               "title": q["title"],
               "objective": session.quest.objective_text(q),
           } if q else None,
           "side_quests": [
               {
                   "id": sq["id"],
                   "title": sq["title"],
                   "objective": session.quest.objective_text(sq),
               }
               for sq in session.quest.active_side()
           ],
       }
       
       # 2. 4 Slot Ingatan (Terbuka vs Terkunci)
       all_memories = []
       for mem in registry.memories:
           mid = mem["id"]
           unlocked = mid in session.state.memories
           all_memories.append({
               "id": mid,
               "title": mem["title"] if unlocked else "???",
               "text": mem.get("text", "") if unlocked else None,
               "unlocked": unlocked,
           })
       
       # 3. Log Sistem
       system_log = [e["text"] for e in session.state.log if e["type"] == "system"]
       
       return {
           "mission": mission,
           "memories": all_memories,
           "unlocked_count": len(session.state.memories),
           "total_count": len(registry.memories),
           "system_log": system_log,
       }
   ```
2. **Frontend UI Rendering (`web/static/app.js::openTianyuan`)**:
   Render 3 seksi secara berurutan:
   - **Seksi 1: Status Misi**: 
     - Jika `mission.main`: tampilkan `[Misi Utama] {title}` dan objektif.
     - Jika `mission.main` tidak ada (`None`): tampilkan `[Misi Utama] Belum ada misi utama aktif (Arc 1 Tamat / Eksplorasi Bebas)`.
     - Jika `mission.side_quests` ada: tampilkan daftar `[Misi Sampingan] {title}` dan progres.
   - **Seksi 2: Ingatan Masa Lalu (x/4)**: Tampilkan kotak ingatan terbuka dengan teks lengkap. Untuk ingatan terkunci (`unlocked: false`), tampilkan kotak bergaris putus-putus (*dashed border*) bertuliskan `• ??? (Belum Terbuka)`.
   - **Seksi 3: Log Komunikasi Sistem**: 30 entri log sistem terakhir.
3. **Sinkronisasi Test Suite (`tests/test_web.py::test_tianyuan_panel`)**:
   Perbarui assertion pada test eksisting agar mencocokkan struktur 4 slot:
   ```python
   def test_tianyuan_panel(base_url: str) -> None:
       post(base_url, "/api/new")
       body, status = get(base_url, "/api/tianyuan")
       assert status == 200
       data = json.loads(body)
       assert data["ok"] is True
       assert len(data["tianyuan"]["memories"]) == 4
       assert all(not m["unlocked"] for m in data["tianyuan"]["memories"])
       assert all(m["title"] == "???" for m in data["tianyuan"]["memories"])
       assert data["tianyuan"]["mission"]["main"] is not None
       assert data["tianyuan"]["mission"]["side_quests"] == []
   ```

#### Pra-syarat & Dependensi
- Dapat dikerjakan bersama tugas backend Wave 1 lainnya.

#### Rencana Pengujian & Validasi
- `python3 -m pytest tests/test_web.py` — Verifikasi struktur data respon `/api/tianyuan` dan sinkronisasi assertion 4-slot.

#### Kriteria Penerimaan (Acceptance Criteria)
- [ ] Endpoint `/api/tianyuan` mengembalikan dictionary dengan struktur `mission: {"main": ..., "side_quests": [...]}`, `memories` (4 slot), `unlocked_count`, dan `system_log`.
- [ ] Data `side_quests` tetap terjaga pada payload meski quest utama bernilai `None`.
- [ ] Modal web menampilkan 3 seksi yang jelas: Status Misi, Ingatan (x/4), dan Log Sistem.
- [ ] Slot ingatan yang belum terbuka ditampilkan sebagai `??? (Belum Terbuka)`.
- [ ] Unit test `tests/test_web.py::test_tianyuan_panel` disinkronkan dan lulus 100%.

#### Template Prompt Subagent (Wave 1 Backend Context)
```markdown
Anda adalah implementer backend subagent untuk Tian Xu: Second Life (Wave 1).
Tugas Anda adalah memperbarui payload `/api/tianyuan` dan menyinkronkan test suite web (Task ID: EP1-T3 Backend).

Target Berkas:
- `web/app.py`
- `tests/test_web.py`

Instruksi:
1. Modifikasi fungsi `_tianyuan_payload()` pada `web/app.py` agar mengembalikan `mission: {"main": ..., "side_quests": [...]}` (sehingga side quest tetap ada saat main quest selesai), `memories` (seluruh 4 slot memori dengan flag `unlocked` dan title `"???"` jika terkunci), `unlocked_count`, `total_count`, dan `system_log`.
2. Perbarui assertion `test_tianyuan_panel` pada `tests/test_web.py` untuk memvalidasi `len(memories) == 4`, semua `unlocked == False`, dan `mission["side_quests"] == []`.
3. Jalankan `python3 -m pytest tests/test_web.py` untuk konfirmasi kelulusan.
```

---

### Task EP2-T1: Sinkronisasi Skema Side Quest, Penegakan Cooldown & Deserialisasi Defensif

#### Informasi Tugas
- **ID Tugas**: `EP2-T1`
- **Judul**: Sinkronisasi Skema `cooldown` Side Quest, Penegakan Jeda Waktu di QuestEngine, dan Deserialisasi Defensif
- **Prioritas**: `P1 (Integritas Skema & Simulasi)`
- **Estimasi Kompleksitas**: `M (Medium - 3 Story Points / 1 Jam)`
- **Fase Eksekusi**: `Wave 1 (Fondasi Data & State Backend)`

#### Motivasi & User Story
*Sebagai pengembang dan pemain, saya ingin data side quest menggunakan penamaan skema yang konsisten (`cooldown`), QuestEngine menegakkan jeda waktu cooldown setelah quest selesai, dan deserialisasi save data bersifat defensif agar kompatibel mundur dengan file simpanan lama.*

#### Daftar Berkas Target
1. `data/quests/quests_side.json` (Modifikasi: ganti `repeat_cooldown` menjadi `cooldown` dengan nilai jam positif)
2. `src/engine/state.py` (Modifikasi: tambahkan tracking `side_quest_cooldowns` pada `GameState` dengan deserialisasi defensif `.get()`)
3. `src/engine/quest.py` (Modifikasi: perbarui `is_offerable()` dan `_complete_side()` untuk mencatat dan mengecek cooldown)
4. `tools/validate_data.py` (Verifikasi: pastikan aturan §14-8 dan §14-9 memvalidasi `cooldown > 0`)
5. `tests/test_quest_dag.py` (Modifikasi: tambahkan unit test pengujian jeda cooldown side quest)

#### Spesifikasi Teknis & Kontrak Data/API
1. **Pembaruan Data Skema (`data/quests/quests_side.json`)**:
   Gantikan properti `"repeat_cooldown": 0` pada ketiga side quest menjadi `"cooldown": 2` (atau nilai jam yang dirancang):
   ```json
   {
     "id": "q_side_berburu",
     "repeatable": true,
     "cooldown": 2,
     "available_from": { "day": 1, "hour": 8 }
   }
   ```
2. **State Tracking & Defensive Deserialization (`src/engine/state.py::GameState`)**:
   - Tambahkan field `side_quest_cooldowns: dict[str, int] = field(default_factory=dict)` yang mencatat total jam absolut (`day * 24 + hour`) saat quest diselesaikan.
   - Pada `to_dict()`:
     ```python
     "side_quest_cooldowns": copy.deepcopy(self.side_quest_cooldowns),
     ```
   - Pada `from_dict()` (wajib defensif menggunakan `.get()` dengan fallback `{}`):
     ```python
     side_quest_cooldowns=copy.deepcopy(d.get("side_quest_cooldowns", {})),
     ```
     *Catatan Penting*: Pola `.get()` ini wajib agar save file lama tanpa field `side_quest_cooldowns` tetap dapat dimuat tanpa memicu `KeyError`.
3. **Logika QuestEngine (`src/engine/quest.py`)**:
   - Di `_complete_side(qid)`:
     ```python
     now_abs_hours = self.state.day * 24 + self.state.hour
     self.state.side_quest_cooldowns[qid] = now_abs_hours
     ```
   - Di `is_offerable(qid)`:
     ```python
     cd = sq.get("cooldown", 0)
     if cd > 0 and qid in self.state.side_quest_cooldowns:
         now_abs_hours = self.state.day * 24 + self.state.hour
         last_completed = self.state.side_quest_cooldowns[qid]
         if (now_abs_hours - last_completed) < cd:
             return False
     ```

#### Pra-syarat & Dependensi
- Fondasi utama sebelum ekspansi data side quest berikutnya.

#### Rencana Pengujian & Validasi
- `python3 tools/validate_data.py` — Wajib exit 0 (Aturan 8 memvalidasi bahwa `cooldown` adalah angka $> 0$).
- `python3 -m pytest tests/test_quest_dag.py` — Uji penyelesaian side quest, pastikan quest tidak dapat diambil kembali seketika, dan dapat diambil setelah waktu dimajukan melebihi cooldown.

#### Kriteria Penerimaan (Acceptance Criteria)
- [ ] Tidak ada lagi kunci `repeat_cooldown` pada `data/quests/quests_side.json`.
- [ ] `python3 tools/validate_data.py` lulus 100% tanpa pelanggaran Aturan 8.
- [ ] `GameState.from_dict()` menggunakan pola `.get("side_quest_cooldowns", {})` yang menjamin backward-compatibility terhadap save data lama.
- [ ] `is_offerable()` mengembalikan `False` jika waktu in-game belum melampaui `cooldown` jam pasca selesai.
- [ ] Seluruh unit test DAG dan validator lulus 100%.

#### Template Prompt Subagent (Ready to Copy)
```markdown
Anda adalah implementer subagent untuk Tian Xu: Second Life (Wave 1).
Tugas Anda adalah merapikan skema `cooldown` pada side quest, menegakkan jeda waktu di QuestEngine, dan menerapkan deserialisasi defensif (Task ID: EP2-T1).

Target Berkas:
- `data/quests/quests_side.json`
- `src/engine/state.py`
- `src/engine/quest.py`
- `tests/test_quest_dag.py`

Instruksi:
1. Ganti semua instansi `"repeat_cooldown": 0` pada `data/quests/quests_side.json` menjadi `"cooldown": 2`.
2. Tambahkan `side_quest_cooldowns: dict[str, int] = field(default_factory=dict)` pada dataclass `GameState` di `src/engine/state.py`.
3. Di `GameState.to_dict()`, sertakan `"side_quest_cooldowns": copy.deepcopy(self.side_quest_cooldowns)`.
4. Di `GameState.from_dict()`, gunakan deserialisasi defensif: `side_quest_cooldowns=copy.deepcopy(d.get("side_quest_cooldowns", {}))`.
5. Di `src/engine/quest.py::_complete_side()`, catat waktu selesai absolut (`day * 24 + hour`) ke `state.side_quest_cooldowns[qid]`.
6. Di `src/engine/quest.py::is_offerable()`, periksa jika quest memiliki cooldown dan waktu sekarang belum melewati `last_time + cooldown`, maka return `False`.
7. Tulis unit test di `tests/test_quest_dag.py` yang menguji siklus: ambil quest -> selesaikan -> coba ambil langsung (gagal) -> tunggu jam in-game -> ambil kembali (berhasil).
8. Jalankan `python3 tools/validate_data.py` dan `python3 -m pytest tests/test_quest_dag.py`.
```

---

### Task EP2-T2: Simulasi Waktu: Respawn Monster Berburu (5 Jam) & Jadwal Rutin Harian NPC

#### Informasi Tugas
- **ID Tugas**: `EP2-T2`
- **Judul**: Penegakan Timer Respawn Monster Berburu (5 Jam), Jadwal Rutin Harian NPC, dan Sinkronisasi Test Suite
- **Prioritas**: `P1 (Simulasi Dunia & Balancing)`
- **Estimasi Kompleksitas**: `M (Medium - 3 Story Points / 1 Jam)`
- **Fase Eksekusi**: `Wave 2 Jalur B (Engine & CLI Simulation Track)`

#### Motivasi & User Story
*Sebagai pemain, saya ingin dunia terasa hidup di mana monster liar membutuhkan waktu 5 jam untuk respawn setelah diburu dan NPC memiliki jam kerja rutin harian yang aktif setiap hari tanpa mengalami softlock permanen di Hari ke-2+, serta memberikan respon naratif yang ramah ketika dikunjungi di luar jam aktif.*

#### Daftar Berkas Target
1. `data/npcs.json` (Modifikasi: pastikan skema jadwal NPC konsisten sebagai rutinitas harian berulang)
2. `src/engine/state.py` (Modifikasi: tambahkan tracking `last_hunt_time` pada `GameState` dengan deserialisasi defensif `.get()`)
3. `src/engine/session.py` (Modifikasi: penegakan jeda 5 jam pada `_hunt()`, evaluasi jadwal rutin harian NPC pada `_talk()` & `_spar()`, dan pesan fallback log sistem yang informatif)
4. `tests/test_session.py` (Modifikasi: unit test untuk respawn monster dan ketersediaan NPC terjadwal)
5. `tests/test_quest_dag.py` (Modifikasi: sinkronisasi pengujian berburu beruntun pada `test_side_quest_berburu_selesai_via_kemenangan`)

#### Spesifikasi Teknis & Kontrak Data/API
1. **Respawn Timer Berburu (`src/engine/session.py::_hunt`)**:
   - Baca nilai `respawn_hours = self.reg.config.get("world", {}).get("monster_respawn_hours", 5)`.
   - Hitung total jam absolut saat ini: `now_abs_hours = self.state.day * 24 + self.state.hour`.
   - Jika `self.state.last_hunt_time is not None` dan `(now_abs_hours - self.state.last_hunt_time) < respawn_hours`:
     - Sisa jam: `remaining = respawn_hours - (now_abs_hours - self.state.last_hunt_time)`
     - Tambahkan pesan sistem: `add_log(self.state, "system", f"Wilayah Berburu masih sepi. Monster liar baru muncul kembali dalam {remaining} jam.")`
     - Kembalikan `self.view()` tanpa memulai pertarungan.
   - Jika waktu telah lewat (atau hunt pertama), catat `self.state.last_hunt_time = now_abs_hours` dan mulai battle seperti biasa.
2. **Defensive Deserialization (`src/engine/state.py`)**:
   - Di `GameState`: `last_hunt_time: int | None = None`
   - Di `to_dict()`: `"last_hunt_time": self.last_hunt_time`
   - Di `from_dict()`: `last_hunt_time=d.get("last_hunt_time", None)` (menjaga kompatibilitas mundur dengan save file lama).
3. **Pencegahan Softlock & Rutinitas Harian Jadwal NPC (`src/engine/session.py::_is_npc_available` & `data/npcs.json`)**:
   - **Prinsip Rutinitas Harian**: Di Fase 1 (Arc Akademi), jadwal NPC pada `data/npcs.json` merepresentasikan jam aktif harian (misal Penatua An jam 09:00–17:00, Penjaga Gerbang jam 06:00–22:00) yang **berulang setiap hari**.
   - Helper `_is_npc_available(self, npc: dict) -> bool`:
     ```python
     def _is_npc_available(self, npc: dict) -> bool:
         schedules = npc.get("schedule", [])
         if not schedules:
             return True
         for s in schedules:
             # Jadwal harian berulang: jika day tidak ditentukan atau s.get("day") in (None, self.state.day)
             # Di Fase 1, entri schedule berlaku sebagai rutinitas jam harian
             h_start = s.get("hour_start", 0)
             h_end = s.get("hour_end", 24)
             if h_start <= self.state.hour <= h_end:
                 return True
         return False
     ```
   - **Pesan Fallback Informatif**:
     - Pada `_talk()`: Jika `not self._is_npc_available(npc_data)`:
       `add_log(self.state, "system", f"{npc_data['name']} sedang beristirahat/bertapa dan tidak menerima tamu saat ini.")`
       `return self.view()`
     - Pada `_spar()`: Jika `not self._is_npc_available(npc_data)`:
       `add_log(self.state, "system", f"{npc_data['name']} sedang tidak berada di tempat untuk berlatih tanding.")`
       `return self.view()`
4. **Sinkronisasi Test Suite (`tests/test_quest_dag.py`)**:
   - Pada `tests/test_quest_dag.py::test_side_quest_berburu_selesai_via_kemenangan`, aksi hunt kedua yang dipanggil segera setelah kill pertama harus memajukan waktu 5 jam terlebih dahulu atau me-reset `last_hunt_time`:
     ```python
     session.apply_action({"type": "hunt"})
     session.apply_action({"type": "battle_action", "action": "attack"})
     session.apply_action({"type": "advance_time", "hours": 5})  # jeda respawn monster
     session.apply_action({"type": "hunt"})
     session.apply_action({"type": "battle_action", "action": "attack"})
     ```
     Hal ini memastikan test tidak gagal akibat penolakan cooldown respawn monster yang baru diaktifkan.

#### Pra-syarat & Dependensi
- Bergantung pada ketersediaan data `schedule` di `data/npcs.json`.

#### Rencana Pengujian & Validasi
- `python3 -m pytest tests/test_session.py tests/test_quest_dag.py` — Verifikasi pemblokiran berburu beruntun, ketersediaan NPC lintas hari (Hari 1 dan Hari 2+), serta kelulusan test side quest.
- `python3 tools/validate_data.py` — Validasi data NPC tetap exit 0.

#### Kriteria Penerimaan (Acceptance Criteria)
- [ ] Berburu beruntun dalam jeda < 5 jam in-game ditolak dengan log pesan sisa waktu yang informatif.
- [ ] Memajukan waktu ≥ 5 jam memulihkan ketersediaan monster berburu.
- [ ] `tests/test_quest_dag.py::test_side_quest_berburu_selesai_via_kemenangan` disinkronkan dan lulus 100%.
- [ ] `GameState.from_dict()` memuat `last_hunt_time` secara defensif dengan fallback `None`.
- [ ] NPC yang memiliki jadwal aktif (misal Penatua An jam 09:00–17:00) dapat ditemui di jam kerjanya pada **Hari 1, Hari 2, dan hari-hari berikutnya** tanpa terkunci permanen.
- [ ] Mengunjungi NPC di luar jam kerja memberikan pesan log sistem informatif tanpa memicu error.
- [ ] Seluruh 93+ test lulus 100%.

#### Template Prompt Subagent (Ready to Copy)
```markdown
Anda adalah implementer subagent untuk Tian Xu: Second Life (Wave 2 Jalur B).
Tugas Anda adalah menerapkan timer respawn monster berburu (5 jam), jadwal rutin harian NPC, dan sinkronisasi test suite (Task ID: EP2-T2).

Target Berkas:
- `data/npcs.json`
- `src/engine/state.py`
- `src/engine/session.py`
- `tests/test_session.py`
- `tests/test_quest_dag.py`

Instruksi:
1. Tambahkan `last_hunt_time: int | None = None` pada dataclass `GameState` di `src/engine/state.py`.
2. Di `GameState.to_dict()` sertakan `last_hunt_time`, dan di `GameState.from_dict()` gunakan deserialisasi defensif: `last_hunt_time=d.get("last_hunt_time", None)`.
3. Di `src/engine/session.py::_hunt()`, gunakan `config.world.monster_respawn_hours` (default 5). Jika selisih `(day*24 + hour) - last_hunt_time < 5`, tolak aksi dengan pesan log sistem "Wilayah Berburu masih sepi. Monster liar baru muncul kembali dalam {remaining} jam."
4. Buat helper `_is_npc_available(npc)` di `session.py` yang mengevaluasi jam aktif harian berulang (`hour_start <= self.state.hour <= hour_end`) tanpa mengunci NPC pada Hari 2+. Berikan pesan fallback informatif di `_talk` dan `_spar` saat NPC di luar jam aktif.
5. Di `tests/test_quest_dag.py::test_side_quest_berburu_selesai_via_kemenangan`, tambahkan `session.apply_action({"type": "advance_time", "hours": 5})` di antara hunt pertama dan hunt kedua.
6. Tulis pengujian unit di `tests/test_session.py` yang memverifikasi siklus respawn monster dan jadwal NPC di Hari 1 dan Hari 2+.
7. Jalankan `python3 -m pytest tests/test_session.py tests/test_quest_dag.py` dan `python3 tools/validate_data.py`.
```

---

### Task EP2-T3: Rekapitulasi Akhir Arc 1 (Closure `q_akademi_07`)

#### Informasi Tugas
- **ID Tugas**: `EP2-T3`
- **Judul**: Implementasi Layar Ringkasan dan Rekapitulasi Akhir Arc 1 (Backend/CLI Closure & Frontend UI Modal)
- **Prioritas**: `P1 (Penyelesaian Alur Cerita & DoD)`
- **Estimasi Kompleksitas**: `M (Medium - 2.5 Story Points / 45 Menit)`
- **Pemisahan Jalur Eksekusi (Zero File Collision)**:
  - **Jalur B (Engine & CLI Track - Wave 2)**: Modifikasi `src/engine/session.py`, `src/cli.py`, `tests/test_cli.py`
  - **Jalur A (Frontend UI Track - Wave 2)**: Modifikasi `web/static/app.js`, `web/static/style.css`, `web/static/index.html`

#### Motivasi & User Story
*Sebagai pemain yang telah menyelesaikan seluruh rangkaian cerita Arc Akademi hingga q_akademi_07, saya ingin melihat layar ringkasan pencapaian akhir (cabang sikap yang dipilih, moralitas akhir, ranah kultivasi, dan teaser Arc 2) baik di CLI maupun Web UI dengan mekanisme penutupan modal sekali tayang (*single-fire dismissal*), sehingga eksplorasi bebas pasca-tamat dapat dinikmati tanpa gangguan popup berulang.*

#### Daftar Berkas Target
**Bagian Backend & CLI (Jalur B - Wave 2)**:
1. `src/engine/session.py` (Modifikasi: deteksi penyelesaian `q_akademi_07` dan sertakan metadata `arc_summary` pada `view()`)
2. `src/cli.py` (Modifikasi: render banner rekapitulasi akhir saat `arc_summary` aktif)
3. `tests/test_cli.py` (Modifikasi: verifikasi kemunculan ringkasan akhir arc di CLI)

**Bagian Frontend Web UI (Jalur A - Wave 2)**:
1. `web/static/index.html` (Modifikasi: kontainer `#modal-arc-summary`)
2. `web/static/app.js` (Modifikasi: render modal rekapitulasi akhir dengan flag dismissal `window.arcSummaryDismissed`)
3. `web/static/style.css` (Modifikasi: styling modal penutup emas xianxia)

#### Spesifikasi Teknis & Kontrak Data/API
1. **Metadata Ringkasan di `session.py::view()`**:
   Jika `q_akademi_07` ada di dalam `state.completed_quests`:
   ```python
   # Evaluasi cabang yang ditempuh
   chosen_branch = "Tidak Diketahui"
   if "branch_3aa" in self.state.flags:
       chosen_branch = "Cabang 3AA — Konfrontasi Terbuka Penatua An"
   elif "branch_3ab" in self.state.flags:
       chosen_branch = "Cabang 3AB — Penyelidikan Diam-Diam Mo Yun"
   elif "branch_3b" in self.state.flags:
       chosen_branch = "Cabang 3B — Memeras Zhou Yan & Mengambil Keuntungan"
   elif "branch_3c" in self.state.flags:
       chosen_branch = "Cabang 3C — Berdiam Diri & Menjaga Diri"

   arc_summary = {
       "completed": True,
       "title": "AKHIR ARC 1: AKADEMI CHANGFENG",
       "player_name": self.state.player.name,
       "realm": self.reg.realms[self.state.player.realm]["name_pinyin"],
       "realm_level": self.state.player.realm_level,
       "academy": self.state.player.academy,
       "morality": self.state.player.morality,
       "branch": chosen_branch,
       "memories_unlocked": f"{len(self.state.memories)}/4",
       "gold": self.state.player.gold,
       "day": self.state.day,
       "teaser": "Kebenaran di balik Penatua An telah terkuak. Namun bayang-bayang masa lalu Long Tianxu dan intrik Sekte Regional baru saja dimulai...",
   }
   ```
2. **Tampilan CLI (`src/cli.py`)**:
   Tampilkan bingkai ANSI berwarna emas dengan rekapitulasi stat dan narasi teaser penutup ketika `view.get("arc_summary")` aktif.
3. **Tampilan Web UI & Single-Fire Dismissal (`web/static/app.js`)**:
   - Tambahkan state flag di frontend: `window.arcSummaryDismissed = false`.
   - Di `renderView()`:
     ```javascript
     if (v.arc_summary && !window.arcSummaryDismissed) {
       openArcSummaryModal(v.arc_summary);
     }
     ```
   - Tombol pada modal: `<button class="btn btn-gold" onclick="dismissArcSummary()">Lanjut Eksplorasi Bebas</button>`.
   - Fungsi `dismissArcSummary()`:
     ```javascript
     function dismissArcSummary() {
       window.arcSummaryDismissed = true;
       closeModal("modal-arc-summary");
     }
     ```
   - Hal ini mencegah modal muncul kembali secara berulang-ulang (*infinite modal popup loop*) saat pemain mengambil aksi eksplorasi lanjutan pasca-tamat.

#### Pra-syarat & Dependensi
- Menyelesaikan seluruh alur DAG quest `q_akademi_01` s.d. `q_akademi_07`.

#### Rencana Pengujian & Validasi
- `python3 -m pytest tests/test_cli.py` — Pengujian *end-to-end playthrough* sampai penutup arc di CLI.
- `python3 -m pytest tests/test_web.py` — Pengujian ketersediaan metadata `arc_summary` di view response web.

#### Kriteria Penerimaan (Acceptance Criteria)
- [ ] Menyelesaikan `q_akademi_07` menyertakan `arc_summary` pada payload `session.view()`.
- [ ] CLI menampilkan banner rekapitulasi akhir Arc 1 yang indah dan rapi.
- [ ] Web UI menampilkan modal rekapitulasi akhir yang merangkum cabang pilihan, ranah, dan moralitas.
- [ ] Tombol `Lanjut Eksplorasi Bebas` menandai `window.arcSummaryDismissed = true` sehingga modal tidak muncul kembali pada aksi berikutnya.
- [ ] Tidak terjadi tabrakan berkas antara pengembang Engine (Jalur B) dan pengembang Frontend (Jalur A).

#### Template Prompt Subagent Engine (Wave 2 Jalur B)
```markdown
Anda adalah implementer backend/CLI subagent untuk Tian Xu: Second Life (Wave 2 Jalur B).
Tugas Anda adalah mengimplementasikan backend metadata `arc_summary` dan banner CLI (Task ID: EP2-T3 Engine).

Target Berkas:
- `src/engine/session.py`
- `src/cli.py`
- `tests/test_cli.py`

Instruksi:
1. Di `src/engine/session.py::view()`, jika `q_akademi_07` ada di `state.completed_quests`, tambahkan field `arc_summary` yang merangkum nama, ranah, tingkat, moralitas, cabang pilihan (3AA/3AB/3B/3C), memori terbuka, dan teaser Arc 2.
2. Di `src/cli.py`, render banner ANSI khusus saat `arc_summary` terdeteksi pada view.
3. Di `tests/test_cli.py`, tulis test yang memverifikasi render ringkasan akhir saat quest `q_akademi_07` selesai.
4. Catatan: Jangan menyentuh berkas di `web/static/` karena dikerjakan oleh subagent Frontend di Jalur A.
5. Jalankan `python3 -m pytest tests/test_cli.py` dan konfirmasi kelulusan.
```

---

### Task EP3-T1: Penutupan Edge Cases Unit Test Menuju >95% Coverage

#### Informasi Tugas
- **ID Tugas**: `EP3-T1`
- **Judul**: Penutupan Celah Pengujian Unit Test (*Edge Cases Hardening*) Menuju >95% Code Coverage
- **Prioritas**: `P2 (Kualitas & Hardening QA)`
- **Estimasi Kompleksitas**: `M (Medium - 3 Story Points / 1 Jam)`
- **Fase Eksekusi**: `Wave 3 (Hardening QA)`

#### Motivasi & User Story
*Sebagai tim pengembang, kami ingin menutup 231 baris kode yang belum teruji secara langsung pada subsistem evaluasi dialog, teknik pertarungan bertahan/pemulihan, dan penanganan kesalahan sesi, agar basis kode memiliki tingkat ketahanan dan regresi yang mutlak.*

#### Daftar Berkas Target
1. `tests/test_dialog.py` (Modifikasi: skenario uji kondisi `morality_max`, `has_item`, `realm_min`, `academy`, `quest_active`, `quest_not_active`)
2. `tests/test_battle.py` (Modifikasi: skenario uji teknik jurus `defend`, `heal`, pemakaian item di battle, penalti kekalahan spar `spar_loss_exp`, kegagalan kabur `flee`)
3. `tests/test_session.py` (Modifikasi: penanganan error transaksi toko dan crafting bahan invalid, pencarian herba gagal)
4. `tests/test_effects.py` (Baru: uji langsung pemutasi seluruh jenis effect dispatcher)

#### Spesifikasi Teknis & Kontrak Data/API
1. **Dialog Condition Evaluators (`tests/test_dialog.py`)**:
   - Buat unit test langsung untuk `DialogEngine._eval_condition()`:
     - `morality_max`: lolos jika moral $\le \text{target}$, gagal jika sebaliknya.
     - `has_item`: cek keberadaan item di inventori (`count \ge 1`).
     - `realm_min`: verifikasi ranah kultivasi minimal.
     - `academy`: verifikasi kecocokan akademi pemain.
     - `quest_active` & `quest_not_active`: verifikasi state quest saat ini.
2. **Battle Techniques & Edge Cases (`tests/test_battle.py`)**:
   - Uji jurus teknik bertahan (`kind == "defend"`, misal `tek_elemen_perisai_tanah`) memitigasi damage yang masuk.
   - Uji jurus teknik pemulihan (`kind == "heal"`, misal `tek_elemen_embun_air`) memulihkan HP pemain tanpa melebihi `hp_max`.
   - Uji aksi `item` dalam battle (mengonsumsi `pil_qi` / `pil_pemulihan` di tengah giliran bertarung).
   - Uji kegagalan kabur (`flee`) saat musuh memiliki kecepatan lebih tinggi, memastikan giliran berpindah ke musuh.
   - Uji exp kalah sparing (`spar_loss_exp`) bertambah ke state pemain.
3. **Session Edge Cases (`tests/test_session.py`)**:
   - Uji transaksi beli toko saat emas tidak cukup.
   - Uji transaksi jual toko saat pemain tidak memiliki item tersebut.
   - Uji aksi racik (`craft`) dengan ID resep yang tidak terdaftar di data.
   - Uji aksi `search` di wilayah berburu saat roll RNG herba gagal (menghasilkan log kegagalan).

#### Pra-syarat & Dependensi
- Dieksekusi setelah Wave 1 dan Wave 2 selesai.

#### Rencana Pengujian & Validasi
- `python3 -m pytest --cov=src --cov-report=term-missing` — Target coverage $> 95\%$ untuk seluruh modul dalam `src/engine/`.

#### Kriteria Penerimaan (Acceptance Criteria)
- [ ] Semua cabang evaluasi kondisi di `src/engine/dialog.py` memiliki unit test langsung.
- [ ] Aksi teknik `defend`, `heal`, dan `item` di `src/engine/battle.py` memiliki unit test terisolasi.
- [ ] Total code coverage untuk direktori `src/` meningkat dari 84% menjadi $\ge 95\%$.
- [ ] Seluruh pengujian 100% deterministik tanpa penggunaan random unseeded atau dependency eksternal.

#### Template Prompt Subagent (Ready to Copy)
```markdown
Anda adalah QA implementer subagent untuk Tian Xu: Second Life (Wave 3).
Tugas Anda adalah menutup celah pengujian unit test pada modul dialog, battle, session, dan effects untuk mencapai >95% coverage (Task ID: EP3-T1).

Target Berkas:
- `tests/test_dialog.py`
- `tests/test_battle.py`
- `tests/test_session.py`
- `tests/test_effects.py`

Instruksi:
1. Di `tests/test_dialog.py`, tambahkan skenario uji untuk semua kondisi `_eval_condition`: `morality_max`, `has_item`, `realm_min`, `academy`, `quest_active`, `quest_not_active`.
2. Di `tests/test_battle.py`, tambahkan skenario uji untuk:
   - Penggunaan teknik jenis `defend` (mengurangi damage).
   - Penggunaan teknik jenis `heal` (memulihkan HP di-clamp ke max_hp).
   - Penggunaan aksi `item` dalam battle.
   - Skenario gagal kabur (`flee`) dan exp kalah sparing (`spar_loss_exp`).
3. Di `tests/test_session.py`, tambahkan pengujian untuk penolakan `shop_buy` (uang kurang), `shop_sell` (item tidak ada), `craft` (resep salah / bahan kurang), dan `search` (gagal nemu herba).
4. Buat `tests/test_effects.py` untuk menguji dispatcher effect mutator.
5. Jalankan `python3 -m pytest --cov=src --cov-report=term-missing` dan pastikan line coverage $\ge 95\%$.
```

---

### Task EP3-T2: Sinkronisasi Dokumen Arsitektur & GDD

#### Informasi Tugas
- **ID Tugas**: `EP3-T2`
- **Judul**: Sinkronisasi Dokumen Arsitektur Teknik (`ENGINE_ARCHITECTURE.md`) dan Dokumen Desain Terhadap Kode Nyata
- **Prioritas**: `P2 (Dokumentasi & Konsistensi)`
- **Estimasi Kompleksitas**: `S (Small - 1 Story Point / 30 Menit)`
- **Fase Eksekusi**: `Wave 3 (Dokumentasi)`

#### Motivasi & User Story
*Sebagai pengembang dan pemelihara sistem, saya ingin dokumen arsitektur merefleksikan arsitektur implementasi nyata (seperti struktur endpoint web statis dan status implementasi Fase 1) agar tidak terjadi kebingungan referensi di masa depan.*

#### Daftar Berkas Target
1. `docs/ENGINE_ARCHITECTURE.md` (Modifikasi: perbarui §12 arsitektur Web UI, §16-§17 status implementasi fitur)
2. `docs/DESIGN_SUMMARY.md` (Modifikasi: perbarui catatan sinkronisasi hasil playtest Fase 1)

#### Spesifikasi Teknis & Kontrak Data/API
1. **Pembaruan `docs/ENGINE_ARCHITECTURE.md`**:
   - Di §12.3: Perjelas bahwa aksi Tianyuan Ling adalah panel modal penampil data via endpoint `GET /api/tianyuan` dan `view()`, bukan aksi mutasi sesi terpisah.
   - Di §16 & §17: Tandai seluruh fitur Fase 1 (termasuk Toko Web, Dinamisasi Resep, Cooldown Side Quest, Timer Respawn Monster, Jadwal Harian NPC, dan Layar Penutup Arc 1) sebagai `SELESAI (Verified)`.
2. **Pembaruan `docs/DESIGN_SUMMARY.md`**:
   - Catat penyelesaian seluruh kriteria penerimaan Fase 1 (Arc Akademi).

#### Pra-syarat & Dependensi
- Dieksekusi setelah tugas-tugas pada Epic 1 dan Epic 2 selesai.

#### Rencana Pengujian & Validasi
- Peninjauan teks dokumen secara manual terhadap kesesuaian basis kode.

#### Kriteria Penerimaan (Acceptance Criteria)
- [ ] `docs/ENGINE_ARCHITECTURE.md` selaras 100% dengan kontrak endpoint `web/app.py` dan struktur `src/engine/session.py`.
- [ ] Tidak ada referensi yang saling bertentangan antar dokumen di folder `docs/`.

#### Template Prompt Subagent (Ready to Copy)
```markdown
Anda adalah dokumentator spesialis subagent untuk Tian Xu: Second Life (Wave 3).
Tugas Anda adalah menyinkronkan dokumen teknis terhadap implementasi nyata (Task ID: EP3-T2).

Target Berkas:
- `docs/ENGINE_ARCHITECTURE.md`
- `docs/DESIGN_SUMMARY.md`

Instruksi:
1. Buka dan periksa `docs/ENGINE_ARCHITECTURE.md`. Perbarui bagian §12 (Web API context & endpoint) dan §16-§17 (Status implementasi fitur).
2. Perbarui `docs/DESIGN_SUMMARY.md` untuk mencatat status final dari Fase 1 Arc Akademi.
3. Pastikan seluruh teks berbahasa Indonesia dengan pinyin yang tepat sesuai konvensi AGENTS.md.
```

---

## 5. Graf Dependensi Struktur & Gelombang Eksekusi (Execution Waves)

Untuk mencegah konflik pengeditan berkas (*zero file collision*) dan memastikan setiap tugas dieksekusi setelah fondasi prasyaratnya siap, alur pengerjaan diatur secara bertahap ke dalam **3 Gelombang Eksekusi (Execution Waves)**:

```
========================================================================================
GELOMBANG 1 (WAVE 1) — Fondasi Skema Data & Konteks Web Backend
========================================================================================
Tugas Fondasi Backend & Skema (Serial / Disjoint Backend Tasks):

   ┌────────────────────────────────────────────────────────┐
   │ [EP2-T1] Sinkronisasi Skema Side Quest (cooldown)      │  (Target: data/quests_side.json,
   │          & Penegakan di QuestEngine                    │   src/engine/quest.py, state.py)
   └───────────────────────────┬────────────────────────────┘
                               │
   ┌───────────────────────────┴────────────────────────────┐
   │ [EP1-T1 Backend + EP1-T2 Backend + EP1-T3 Backend]     │  (Target: web/app.py,
   │ Penyediaan context shop, recipes, & tianyuan payload   │   tests/test_web.py)
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
========================================================================================
GELOMBANG 2 (WAVE 2) — Eksekusi Paralel Frontend Web UI & Logika Simulasi Engine
========================================================================================
Dua Jalur Paralel Murni Tanpa Tabrakan Berkas (Zero File Collision Parallelism):

          JALUR A: Frontend Web UI Specialist          JALUR B: Engine & CLI Simulation Track
   ┌─────────────────────────────────────────┐  ┌─────────────────────────────────────────┐
   │ • [EP1-T1 Frontend]: Toko Web (Beli/Jual)│  │ • [EP2-T2]: Respawn Monster (5 Jam) &   │
   │ • [EP1-T2 Frontend]: Racik Resep Dinamis│  │               Jadwal Rutin Harian NPC   │
   │ • [EP1-T3 Frontend]: Panel Tianyuan UI  │  │ • [EP2-T3 Engine/CLI]: Rekapitulasi Arc1 │
   │ • [EP2-T3 Frontend]: Modal Penutup Arc 1│  │   (Session metadata & CLI banner)       │
   │                                         │  │                                         │
   │ (Berkas: web/static/app.js,             │  │ (Berkas: src/engine/state.py,           │
   │          web/static/index.html,         │  │          src/engine/session.py,         │
   │          web/static/style.css)          │  │          src/cli.py, data/npcs.json,    │
   │                                         │  │          tests/test_session.py,         │
   │                                         │  │          tests/test_quest_dag.py,       │
   │                                         │  │          tests/test_cli.py)             │
   └────────────────────┬────────────────────┘  └────────────────────┬────────────────────┘
                        │                                            │
                        └─────────────────────┬──────────────────────┘
                                              │
                                              ▼
========================================================================================
GELOMBANG 3 (WAVE 3) — Hardening QA, Coverage >95% & Sinkronisasi Dokumentasi
========================================================================================
Verifikasi Menyeluruh & Penutupan Rilis:

   ┌────────────────────────────────────────────────────────┐
   │ [EP3-T1] Penutupan Edge Cases Unit Test (>95% Coverage)│  (Target: tests/test_dialog.py,
   │          Battle Defend/Heal, Item, Dialog Conditions   │   test_battle.py, test_session.py,
   │                                                        │   tests/test_effects.py)
   └───────────────────────────┬────────────────────────────┘
                               │
   ┌───────────────────────────┴────────────────────────────┐
   │ [EP3-T2] Sinkronisasi Dokumen Arsitektur & GDD         │  (Target: docs/ENGINE_ARCHITECTURE.md,
   │          Pembaruan status implementasi final Fase 1    │   docs/DESIGN_SUMMARY.md)
   └────────────────────────────────────────────────────────┘
```

### 5.1 Matriks Keamanan Eksekusi Paralel (Parallel Execution Safety Matrix)

Tabel berikut membuktikan bahwa setiap subagent pada setiap gelombang memiliki **lingkup berkas yang terisolasi 100% tanpa tumpang-tindih (Zero File Collision)**:

| Gelombang (Wave) | Jalur / Paket Tugas | Berkas yang Dimodifikasi (Target Files) | Risiko Konflik | Rekomendasi Alokasi Subagent |
|---|---|---|---|---|
| **Wave 1** | **Backend Foundation** (`EP2-T1` + Backend Context `EP1-T1..T3`) | `data/quests/quests_side.json`, `src/engine/quest.py`, `src/engine/state.py`, `web/app.py`, `tests/test_web.py` | Rendah (Serial) | 1 Subagent Backend Foundation |
| **Wave 2** | **Jalur A (Frontend UI)** (`EP1-T1..T3 Frontend` + `EP2-T3 UI Modal`) | `web/static/app.js`, `web/static/index.html`, `web/static/style.css` | **NOL** (Eksklusif di `web/static/`) | 1 Subagent Frontend Specialist |
| **Wave 2** | **Jalur B (Engine & CLI)** (`EP2-T2` + `EP2-T3 Engine/CLI`) | `src/engine/state.py`, `src/engine/session.py`, `src/cli.py`, `data/npcs.json`, `tests/test_session.py`, `tests/test_quest_dag.py`, `tests/test_cli.py` | **NOL** (Eksklusif di `src/engine/`, `src/cli.py`, `data/npcs.json`, `tests/`) | 1 Subagent Engine Specialist |
| **Wave 3** | **QA Hardening** (`EP3-T1`) | `tests/test_dialog.py`, `tests/test_battle.py`, `tests/test_session.py`, `tests/test_effects.py` | **NOL** (Eksklusif di `tests/`) | 1 Subagent QA Auditor |
| **Wave 3** | **Technical Docs** (`EP3-T2`) | `docs/ENGINE_ARCHITECTURE.md`, `docs/DESIGN_SUMMARY.md` | **NOL** (Eksklusif di `docs/`) | 1 Subagent Technical Writer |

### 5.2 Template Prompt Gabungan untuk Eksekusi Subagent

Untuk mempermudah orkestrator menjalankan Wave 2 secara paralel murni, berikut adalah prompt siap-pakai:

#### Prompt Wave 2 Jalur A: Frontend Specialist
```markdown
Anda adalah Frontend Specialist subagent untuk Tian Xu: Second Life (Wave 2 Jalur A).
Tugas Anda adalah menyelesaikan seluruh antarmuka Web UI Fase 1 (Toko Beli/Jual, Racik Resep Dinamis, Panel 3-Seksi Tianyuan Ling, dan Modal Penutup Arc 1).

Kepemilikan Berkas Eksklusif:
- `web/static/app.js`
- `web/static/index.html`
- `web/static/style.css`

Instruksi:
1. Toko Pedagang (EP1-T1 UI): Tambahkan tombol "Buka Toko" di Pasar Changfeng, render modal transaksi beli/jual dengan tab terpisah, dan hubungkan ke aksi `shop_buy` dan `shop_sell`.
2. Alkimia Dinamis (EP1-T2 UI): Ubah `renderExplore()` agar membaca `c.recipes` dinamis dan menampilkan tombol racik untuk semua resep yang bahannya terpenuhi di inventori.
3. Tianyuan Ling Panel (EP1-T3 UI): Ubah `openTianyuan()` agar me-render 3 seksi: Status Misi (Main & Side Quests), 4 Slot Ingatan (tampilkan `??? (Belum Terbuka)` jika `unlocked: false`), dan Log Komunikasi Sistem.
4. Modal Penutup Arc 1 (EP2-T3 UI): Render `#modal-arc-summary` jika `v.arc_summary` ada dan `!window.arcSummaryDismissed`. Tombol "Lanjut Eksplorasi Bebas" wajib men-set `window.arcSummaryDismissed = true` agar modal tidak muncul berulang pada aksi selanjutnya.
5. Periksa styling di `web/static/style.css` agar seluruh modal tampil harmonis bertema xianxia dark-gold.
6. Verifikasi via browser atau visual inspection. Jangan memodifikasi berkas Python di luar `web/static/`.
```

#### Prompt Wave 2 Jalur B: Engine & CLI Specialist
```markdown
Anda adalah Engine & CLI Specialist subagent untuk Tian Xu: Second Life (Wave 2 Jalur B).
Tugas Anda adalah mengimplementasikan timer respawn monster (5 jam), jadwal rutin harian NPC, rekapitulasi penutup Arc 1 di CLI, serta sinkronisasi test suite.

Kepemilikan Berkas Eksklusif:
- `src/engine/state.py`
- `src/engine/session.py`
- `src/cli.py`
- `data/npcs.json`
- `tests/test_session.py`
- `tests/test_quest_dag.py`
- `tests/test_cli.py`

Instruksi:
1. State Defensif: Tambahkan `last_hunt_time` pada `GameState` di `state.py` dengan deserialisasi defensif `d.get("last_hunt_time", None)`.
2. Respawn Berburu (EP2-T2): Di `session.py::_hunt()`, tolak aksi jika `(day*24 + hour) - last_hunt_time < 5` dengan log sistem informatif.
3. Jadwal NPC Harian (EP2-T2): Buat helper `_is_npc_available(npc)` yang mengevaluasi jam aktif harian berulang (`hour_start <= hour <= hour_end`) sehingga NPC aktif setiap hari (Hari 1, 2, dst) tanpa softlock. Berikan log penolakan yang ramah pada `_talk` dan `_spar`.
4. Test Suite Sync: Di `tests/test_quest_dag.py::test_side_quest_berburu_selesai_via_kemenangan`, tambahkan `advance_time` 5 jam di antara hunt 1 dan hunt 2.
5. Arc 1 Closure (EP2-T3): Di `session.py::view()`, sertakan `arc_summary` saat `q_akademi_07` selesai. Di `src/cli.py`, render banner ANSI penutup emas saat `arc_summary` aktif.
6. Tulis pengujian di `tests/test_session.py` dan `tests/test_cli.py`.
7. Jalankan `python3 -m pytest -q` dan `python3 tools/validate_data.py`.
```

---

## 6. Panduan Praktik Terbaik SDD untuk Subagent

Seluruh subagent yang menjalankan paket tugas dari peta jalan ini **WAJIB** mematuhi aturan baku berikut:

1. **Aturan Kepemilikan Berkas (File Ownership Isolation)**:
   - Setiap subagent hanya boleh memodifikasi berkas yang telah ditetapkan dalam daftar target tugasnya.
   - Dilarang keras melakukan refactoring di luar cakupan tugas (*No "While I'm here" refactoring*).
2. **Pola Test-Driven Development (TDD)**:
   - Tulis atau perbarui skenario uji terlebih dahulu sebelum melakukan mutasi logika pada engine atau frontend.
   - Pengujian wajib bersifat **100% deterministik**: dilarang menggunakan `sleep()`, loop polling tanpa batas, atau pemanggilan RNG tanpa seed/mocking pada unit test.
3. **Konvensi Data-Driven & Zero Hardcoding**:
   - Seluruh konten narasi, statistik, harga, dan formula wajib dibaca dari registri `data/`. Dilarang keras men-hardcode ID atau data game langsung di dalam logika Python atau JavaScript.
4. **Aturan Zero Breaking Changes & Kompatibilitas Mundur**:
   - Struktur save data lama (`saves/*.json`) harus tetap kompatibel: setiap field baru di `GameState.from_dict()` **WAJIB** menggunakan pemanggilan defensif `.get(field, default)`.
   - 93 unit test yang sudah ada tidak boleh dirusak. Perubahan assert hanya diperbolehkan jika selaras dengan penyempurnaan spesifikasi resmi.
5. **Kepatuhan Terhadap Aturan Integritas (Integrity Mandate)**:
   - Dilarang membuat implementasi semu/dummy yang hanya mengembalikan nilai statis (*facade pattern*).
   - Seluruh state mutation harus persisten dan diverifikasi secara independen oleh *Forensic Auditor*.

---
*Peta jalan ini disahkan sebagai acuan tunggal pengerjaan Subagent-Driven Development untuk Tian Xu: Second Life Fase 1.*
