# Laporan Spesifikasi & Penambangan Fitur (Spec Mining Report) — Fase 1 Arc Akademi

**Dokumen**: `/home/dienk/tian-xu-second-life/.agents/teamwork_preview_spec_miner_survey_2/handoff.md`  
**Tanggal**: 14 Agustus 2026  
**Proyek**: *Tian Xu: Second Life* (RPG Xianxia Berbasis Teks)  
**Peran**: Specification Miner (Teamwork Specialist)  
**Tujuan**: Analisis komprehensif seluruh dokumen desain (`docs/GDD.md`, `docs/DESIGN_SUMMARY.md`, `docs/STORY_FASE1.md`, `docs/ENGINE_ARCHITECTURE.md`, `AGENTS.md`) dan data spesifikasi game untuk menyediakan katalog spesifikasi otoritatif, aturan validasi, alur cerita, batasan fase, dan kasus tepi.

---

## 1. Observation

Berdasarkan pembacaan langsung terhadap berkas dokumentasi otoritatif dan kontrak data sistem:

1. **Dokumen Desain & Arsitektur Utama**:
   - `AGENTS.md`: Menetapkan aturan game berbasis Python 3.12 stdlib-only, dev pytest, data-driven di `data/`, alur aksi lewat `session.py::apply_action`, graf quest DAG, save di `saves/*.json` (hanya di titik aman), 五行 (wuxing multiplier 1.5× / 0.67×), validator 16 aturan §14.
   - `docs/GDD.md` (v2.1 Final): Menetapkan premis Long Tianxu/Chen Xu, Tianyuan Ling sebagai Sistem naratif murni (pemisahan tegas ingatan vs kekuatan mekanik), 9 ranah kultivasi × 10 tingkat, pertempuran giliran menu bergantian (pemain → musuh), ekonomi 1 toko, 2 resep alkimia, 3 pilihan akademi (五行阁 / 兵锋院 / 御灵宗), kompanion binatang roh khusus Summoning, 3 ending tematik (Reformer / Destroyer / Ascetic), target durasi 1–2 jam per playthrough.
   - `docs/DESIGN_SUMMARY.md`: Merangkum seluruh keputusan yang telah disahkan: 3 babak Arc Akademi (Ujian & Adaptasi → Insiden Lonceng → 3 Sikap), formula damage `serangan × 100/(100+pertahanan)` (variasi ±10–20%, crit 8% × 1.5), exp `10 × 1.2^(tingkat-1)`, target level akhir arc di Pengumpul Qi tingkat 5–6.
   - `docs/STORY_FASE1.md`: Detail pemetaan cerita: 4 cabang sikap (`3aa` konfrontasi Penatua An, `3ab` bukti diam-diam via Mo Yun, `3b` ambil keuntungan peras Zhou Yan, `3c` berdiam diri), 4 ingatan naratif (`mem_01` Istana yang Sunyi, `mem_02` Kebaikan yang Terlupakan, `mem_03` Racun di Balik Senyum, `mem_04` Pengasingan), kurva karakter Chen Xu (0 ingatan = polos; mem_01 = gelisah; mem_02/03/04 = berubah sesuai cabang), side quest 3 jenis repeatable (berburu, Su Qing, Mo Yun).
   - `docs/ENGINE_ARCHITECTURE.md`: Kontrak teknis detail skema JSON/CSV, 17 handler aksi `GameSession`, 16 aturan validasi startup (`tools/validate_data.py`), arsitektur web stdlib (`web/app.py`), status UI Tianyuan Ling, save/load security, dan roadmap teknis.
   - `docs/PLAYTEST_PROMPT.md` & `docs/superpowers/reviews/2026-08-14-test-suite-evaluation.md`: Verifikasi status test suite (93 passed, 100% pass rate, 84% coverage, validator 16/16 rules pass).

2. **Data Game Aktual (`data/`)**:
   - `data/config.json`: Konfigurasi starting state, 3 akademi, siklus 5 elemen, batasan moralitas [-100, +100], kultivasi (levels 10, exp base 10, growth 1.2, grounding 2 exp/jam maks 8 jam/hari, spar win 8 / loss 3, hunt 6), roots tier (low 0.8x, mid 1.0x, high 1.25x, peak 1.5x), penalti KO (10% exp), stat kompanion scale, monster respawn (5 jam), battle (crit 0.08, crit mult 1.5, qi regen 5%).
   - `data/realms.csv`: 9 ranah lengkap (Pengumpul Qi s.d. Penantang Surga), masing-masing 10 tingkat, formula HP/Qi per level.
   - `data/techniques.csv`: 9 teknik (3 per akademi: attack/defend/heal).
   - `data/items.csv`: 6 item (pil_qi [+30 Qi], pil_pemulihan [+50 HP], material_herba, material_tulang, pedang_bambu [+3 atk], pedang_angin [+5 atk]).
   - `data/enemies.csv`: 3 musuh (Serigala Qi, Babi Hutan Liar, Raja Serigala Qi [mini-boss]).
   - `data/recipes.json`: 2 resep (rc_pil_qi, rc_pil_pemulihan).
   - `data/companions.json`: 1 kompanion (komp_roh_awan, elemen kayu).
   - `data/locations.json`: 9 lokasi (titik aman: `loc_asrama`, `loc_pasar`).
   - `data/npcs.json`: 9 NPC (`npc_penjaga`, `npc_gucanghai`, `npc_hanxiu`, `npc_suqing`, `npc_moyun`, `npc_zhouyan`, `npc_penatua`, `npc_pedagang`, `npc_pemburu`).
   - `data/memories.json`: 4 ingatan naratif (`mem_01` s.d. `mem_04`).
   - `data/quests/quests_akademi.json`: 11 node quest utama DAG (`q_akademi_01` s.d. `q_akademi_07` via cabang `3aa`, `3ab`, `3b`, `3c`).
   - `data/quests/quests_side.json`: 3 side quest repeatable (`q_side_berburu`, `q_side_suqing`, `q_side_moyun`).
   - `data/dialogs/dialogs_akademi.json`: 10 dialog terstruktur dengan percabangan eksplisit.

---

## 2. Features Discovered

Berikut adalah tabel seluruh fitur yang dispesifikasikan dalam dokumen otoritatif untuk Fase 1 dan arsitektur engine:

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Cultivation | 9 Ranah Kultivasi | Sistem 9 tingkatan besar kekuatan kultivasi (Pengumpul Qi hingga Penantang Surga). | Order ranah dari `realms.csv` | Multiplier stat HP/Qi dasar, slot teknik | Ranah tidak ditemukan → fallback stat default | `GDD.md §7`, `ENGINE_ARCHITECTURE.md §5.4` |
| 2 | Cultivation | 10 Tingkat per Ranah | Setiap ranah dibagi menjadi 10 sub-tingkat (`realm_level` 1..10). | Exp aktivitas | `realm_level` naik, stat HP/Qi bertambah | Exp melebihi ambang → akumulasi dan naik tingkat beruntun | `GDD.md §7`, `ENGINE_ARCHITECTURE.md §9.1` |
| 3 | Cultivation | Kurva Kebutuhan Exp | Ambang batas exp per level dihitung dengan kurva eksponensial: `round(base × growth^(level-1))`. | Base 10, Growth 1.2, level saat ini | `exp_next` integer | Ambang minimal 1 | `DESIGN_SUMMARY.md §4`, `ENGINE_ARCHITECTURE.md §9.1` |
| 4 | Cultivation | Multiplier Akar Spiritual | Bakat bawaan melipatgandakan perolehan exp dari seluruh aktivitas (Bawah 0.8×, Menengah 1.0×, Atas 1.25×, Puncak 1.5×). Default Chen Xu = Menengah (中品). | Tier akar pemain (`roots.tiers`) | Pengali exp (float) | Tier tidak valid ditolak validator startup | `GDD.md §7, §11.1`, `ENGINE_ARCHITECTURE.md §5.6, §9.1` |
| 5 | Cultivation | Meditasi / Grounding | Aksi menghabiskan waktu di titik aman untuk mendapatkan exp kultivasi (`2 exp/jam`) + pemulihan Qi lambat. Kuota maks 8 jam per hari. | Aksi `grounding` `{hours: N}` di lokasi aman | Exp bertambah, waktu in-game maju | Ditolak di luar titik aman atau melebihi kuota 8 jam/hari | `DESIGN_SUMMARY.md §3`, `ENGINE_ARCHITECTURE.md §9.1, §12.3` |
| 6 | Cultivation | Terobosan Otomatis (Breakthrough) | Saat `realm_level` mencapai level 10 dan exp penuh, pemain otomatis terobos ke ranah berikutnya (`order + 1`), mereset level ke 1. | Cap level tercapai | Ranah baru, pesan sistem terobosan | Jika mencapai puncak ranah tertinggi (Penantang Surga), tetap di level 10 tanpa crash | `ENGINE_ARCHITECTURE.md §9.1`, `src/engine/cultivation.py` |
| 7 | Combat | Turn-Based Bergantian | Giliran pertarungan bergantian tetap: Pemain → Musuh. | Menu aksi: `attack`, `technique`, `item`, `guard`, `flee` | Mutasi HP/Qi pemain & musuh | Non-battle action ditolak saat battle aktif | `DESIGN_SUMMARY.md §4`, `ENGINE_ARCHITECTURE.md §8.1` |
| 8 | Combat | Formula Damage & Variasi | Damage dihitung: `attack × 100 / (100 + defense) × elemen × RNG(0.8..1.2)`. Minimal damage 1. | Atk penyerang, Def bertahan, elemen | Damage integer, flag crit | Nilai damage < 1 di-clamp ke 1 | `DESIGN_SUMMARY.md §4`, `ENGINE_ARCHITECTURE.md §8.1` |
| 9 | Combat | Siklus Elemen 五行 (Wuxing) | 5 Elemen (Logam → Kayu → Tanah → Air → Api → Logam). 克制 (menang) = 1.5×, 被克 (kalah) = 0.67×, netral = 1.0×. | Elemen skill/penyerang vs elemen target | Pengali damage | Elemen None/netral = 1.0× | `DESIGN_SUMMARY.md §4`, `ENGINE_ARCHITECTURE.md §5.6, §8.2` |
| 10 | Combat | Serangan Kritikal | Peluang acak `crit_chance` (8%) melipatgandakan total damage sebesar `crit_multiplier` (1.5×). | RNG < crit_chance | Multiplier 1.5×, log kritikal | - | `DESIGN_SUMMARY.md §4`, `ENGINE_ARCHITECTURE.md §5.6, §8.1` |
| 11 | Combat | Regenerasi Qi Per Giliran | Pemain & musuh memulihkan 5% Qi maks pada awal setiap gilirannya. | Qi maks karakter | Pemulihan Qi integer | Di-clamp agar tidak melebihi Qi maks | `DESIGN_SUMMARY.md §4`, `ENGINE_ARCHITECTURE.md §8.1` |
| 12 | Combat | Bertahan (Guard) | Aksi `guard` mengurangi damage yang diterima sebesar 50% (atau sesuai power teknik defend) pada giliran tersebut. | Aksi `guard` | Mitigasi damage 50% | - | `ENGINE_ARCHITECTURE.md §8.1` |
| 13 | Combat | Kabur (Flee) | Peluang melarikan diri dari pertarungan berdasarkan perbandingan kecepatan (`speed`). Jika gagal, giliran beralih ke musuh. | Aksi `flee` | Pertarungan berakhir atau giliran musuh | Gagal kabur mencatat log sistem | `ENGINE_ARCHITECTURE.md §8.1` |
| 14 | Combat | Kompanion Summoning di Battle | Khusus akademi Summoning: Roh Awan bertindak otomatis tiap ronde (menyerang musuh). Musuh memiliki peluang 50% menarget kompanion jika aktif. | Kehadiran kompanion aktif | Serangan kompanion, mitigasi target pemain | HP kompanion 0 = status KO (tidak bertarung sampai istirahat) | `GDD.md §5.1, §11.1`, `ENGINE_ARCHITECTURE.md §9.4` |
| 15 | Combat | Penalti KO & Respawn | Pemain KO dalam battle biasa maupun sparing → respawn di titik aman terakhir, HP/Qi pulih, kehilangan 10% exp progres level saat ini. Tidak ada permadeath pada main path. | HP pemain ≤ 0 | Pindah ke `last_safe_location`, exp terpotong 10% | Exp tidak berkurang di bawah 0 | `GDD.md §8, §11.1`, `ENGINE_ARCHITECTURE.md §8.3, §9.3` |
| 16 | Combat | Sparing NPC Bebas | Tantang NPC ber-`can_spar: true` (Han Xiu, Gu Canghai) tanpa batas frekuensi. Menang = exp penuh (`spar_win_exp`); kalah = exp kecil (`spar_loss_exp`) + penalti KO. | Aksi `spar` `{npc: id}` | Memulai battle sparing | NPC tanpa `can_spar` ditolak | `STORY_FASE1.md §1`, `ENGINE_ARCHITECTURE.md §5.3, §9.1` |
| 17 | Combat | Pembatasan Teknik per Akademi | Pemain hanya dapat memakai teknik yang termasuk dalam `skill_pool` akademi yang telah dipilihnya. | Aksi `technique` `{technique: id}` | Eksekusi teknik sesuai jenis (atk/def/heal) | Teknik di luar akademi atau Qi tidak cukup ditolak | `GDD.md §5.2`, `ENGINE_ARCHITECTURE.md §9.4` |
| 18 | Morality | Skala Moralitas [-100, +100] | Tracking nilai moral pemain (mulai 0 netral) yang dimutasi oleh pilihan dialog dan penyelesaian quest. | `effects.morality` | Mutasi skor integer moralitas | Nilai di-clamp antara -100 dan +100 | `GDD.md §3.4`, `ENGINE_ARCHITECTURE.md §5.6, §10` |
| 19 | Morality | Gating Pilihan & Entri Dialog | Kondisi `morality_min` / `morality_max` menyembunyikan atau membuka opsi dialog dan entri dialog tertentu. | State moralitas pemain | Filter pilihan yang terlihat di UI | Pilihan tidak memenuhi syarat disembunyikan | `GDD.md §3.4`, `ENGINE_ARCHITECTURE.md §5.2, §7` |
| 20 | Quest | Main Quest DAG (Satu-Aktif) | Quest utama berupa Directed Acyclic Graph dengan invariant tepat 1 quest utama aktif dalam satu waktu. | Selesai objektif quest | Transisi otomatis atau pembukaan dialog cabang | Dilarang memiliki siklus (diverifikasi validator §14-3) | `GDD.md §4`, `ENGINE_ARCHITECTURE.md §6.1` |
| 21 | Quest | Percabangan Dialog Eksplisit | Percabangan quest hanya dipicu oleh opsi dialog eksplisit (`choice_id` + `option`), bukan trigger tersembunyi. | Pilihan dialog pemain | Pemilihan cabang penerus (`next_quest`) | Sisi > 1 tanpa dialog valid ditolak validator §14-4 | `GDD.md §4.2`, `ENGINE_ARCHITECTURE.md §5.1, §6.2` |
| 22 | Quest | Konvergensi Graf | Seluruh 4 cabang sikap (`3aa`, `3ab`, `3b`, `3c`) menyatu kembali ke quest penutup `q_akademi_07` (q5 Kebenaran). | Selesai quest cabang | Aktivasi `q_akademi_07` | - | `GDD.md §4.3`, `STORY_FASE1.md §2`, `ENGINE_ARCHITECTURE.md §6.2` |
| 23 | Quest | 7 Jenis Objektif Quest | Mendukung jenis objektif: `talk`, `defeat`, `gather`, `reach` (dengan `time_window`), `choose`, `spar`, `advance_time`. | Parameter objektif quest | Pengecekan penyelesaian otomatis/manual | Input data tidak sesuai ditolak validator | `ENGINE_ARCHITECTURE.md §5.1` |
| 24 | Quest | Side Quest Repeatable | Quest sampingan data terpisah (`quests_side.json`), boleh aktif bersamaan, dan dapat diulang untuk grinding exp ranah. | Aksi dialog giver (`start_quest`) | Reward exp/item/reputasi, reset objektif | Dilarang bertabrakan target dengan main quest (§14-10) | `GDD.md §4.4`, `ENGINE_ARCHITECTURE.md §6.4` |
| 25 | Quest | Replayability Tracking | Cabang yang tidak dipilih pemain dicatat dalam state sebagai konten yang belum dijelajahi untuk playthrough berikutnya. | Pemilihan cabang | Pencatatan `available_branches` | - | `GDD.md §4.3`, `ENGINE_ARCHITECTURE.md §6.3` |
| 26 | Story | 3 Pilihan Akademi (Fase 1) | Pemain memilih 1 dari 3 paviliun di Act 1: Elemen (五行阁), Senjata (兵锋院), Summoning (御灵宗). Menentukan pool skill & kompanion tanpa mengubah alur cerita utama. | Quest `q_akademi_04` (choose) | Pool skill terkunci, bonus kompanion | - | `GDD.md §5.1`, `ENGINE_ARCHITECTURE.md §5.6` |
| 27 | Story | Kurva Karakter Chen Xu | Sikap dan pilihan dialog Chen Xu berubah bertahap dari polos (awal) → gelisah (`mem_01`) → dewasa/sinis (`mem_02..04`). | Jumlah & ID ingatan terpulih | Pembukaan opsi dialog naratif tertentu | Ingatan murni naratif, tanpa penambahan power mekanik | `STORY_FASE1.md §3.1` |
| 28 | Story | Insiden & 3 Sikap Moral | Insiden pencurian Lonceng Angin Panjang membuka 4 jalur sikap moral: `3aa` (Konfrontasi), `3ab` (Bukti Diam), `3b` (Ambil Untung), `3c` (Berdiam Diri). | Dialog pilihan sikap di Ruang Lonceng malam hari | Cabang quest spesifik, perubahan relasi NPC, ingatan berbeda | - | `DESIGN_SUMMARY.md §1`, `STORY_FASE1.md §2` |
| 29 | Memory | 4 Ingatan Naratif Tianyuan Ling | Pemulihan memori masa lalu Long Tianxu: `mem_01` (Istana), `mem_02` (Kebaikan), `mem_03` (Racun), `mem_04` (Pengasingan). | `on_complete.memory_unlock` pada quest | Teks memori dapat dibaca di UI Tianyuan Ling | Terkunci tampil `???` | `GDD.md §2.1`, `STORY_FASE1.md §4`, `ENGINE_ARCHITECTURE.md §5.5` |
| 30 | UI | Panel UI Tianyuan Ling | Panel khusus (toggle) berisi 3 bagian: Status Misi, Ingatan (x/4), dan Log Sistem bersuara misterius. | Aksi `open_tianyuan`/`close_tianyuan` | Tampilan status & narasi terisolasi | Sistem pasif murni di Fase 1 (tidak menjawab tanya) | `GDD.md §2.1, §13-6`, `ENGINE_ARCHITECTURE.md §11` |
| 31 | World | Graf Lokasi & Titik Aman | Peta pergerakan 9 lokasi terkoneksi via `connections`. Lokasi aman (`is_safe: true`) mengizinkan save, rest, grounding, dan craft. | Aksi `move` `{to: id}` | Pindah lokasi pemain | Pindah ke lokasi tidak terhubung ditolak | `ENGINE_ARCHITECTURE.md §5.8, §12.3` |
| 32 | World | Simulasi Waktu In-Game | Siklus hari dan jam (24 jam/hari). Waktu maju lewat pergerakan, battle, aksi `advance_time`, `grounding`, dan `rest`. | Aksi in-game | Waktu bertambah, trigger event jadwal | - | `ENGINE_ARCHITECTURE.md §5.6, §9.2` |
| 33 | World | Event Terjadwal (Time Window) | Kondisi kemunculan quest/NPC pada jam tertentu (misal melihat Mo Yun di Ruang Lonceng pada jam 19:00–06:00). | `objective.time_window` / NPC schedule | Ketersediaan aksi dan trigger objektif | Mencapai lokasi di luar jendela waktu tidak memicu progres | `STORY_FASE1.md §1`, `ENGINE_ARCHITECTURE.md §5.1, §9.2` |
| 34 | World | Mini-Boss Wilayah Berburu | Musuh kuat opsional (Raja Serigala Qi) di Wilayah Berburu dengan HP 120, attack 14, reward 60 exp, drop 100% material. | Aksi `hunt` di Wilayah Berburu | Pertarungan mini-boss | Respawn setelah 5 jam in-game | `GDD.md §3, §11.1`, `ENGINE_ARCHITECTURE.md §9.2` |
| 35 | World | Respawn Monster (5 Jam) | Monster liar di area berburu muncul kembali setelah 5 jam in-game berlalu. | Waktu berlalu ≥ 5 jam | Musuh tersedia untuk diburu | Berburu sebelum respawn ditolak | `DESIGN_SUMMARY.md §3`, `ENGINE_ARCHITECTURE.md §9.2` |
| 36 | Economy | Toko Kios Pedagang | 1 NPC pedagang di Pasar Changfeng dengan harga beli/jual tetap. Beli: Pil Qi, Pil Pemulihan, Herba, Pedang Bambu. Jual: Herba, Tulang Serigala. | Aksi `shop_buy`, `shop_sell` | Mutasi inventori & saldo koin emas | Pembelian saat emas kurang atau penjualan item tanpa stok ditolak | `DESIGN_SUMMARY.md §3`, `ENGINE_ARCHITECTURE.md §5.3, §9.3` |
| 37 | Alchemy | Alkimia Dasar (2 Resep) | Meracik pil di titik aman: `rc_pil_qi` (2 Herba → 1 Pil Qi) & `rc_pil_pemulihan` (2 Tulang → 1 Pil Pemulihan). | Aksi `craft` `{recipe: id}` di titik aman | Mengonsumsi material, menghasilkan pil | Ditolak di luar titik aman atau bahan tidak cukup | `DESIGN_SUMMARY.md §3`, `ENGINE_ARCHITECTURE.md §5.7, §9.3` |
| 38 | Equipment | Slot Senjata (Equipment) | Pemain memiliki 1 slot senjata (`equipment.weapon`). Senjata menambah stat attack pemain secara langsung dalam pertempuran. | Aksi `equip` `{item: id}` | Senjata terpasang, attack battle meningkat | Item bukan weapon ditolak | `DESIGN_SUMMARY.md §3`, `ENGINE_ARCHITECTURE.md §5.4, §9.3` |
| 39 | Save/Load | Simpan di Titik Aman Saja | Fitur save dibatasi hanya di lokasi aman (`is_safe: true`). Serialisasi penuh `GameState` ke format JSON di `saves/`. | Aksi `save` `{save_name: str}` | Berkas save JSON tersimpan di disk | Save di luar titik aman ditolak dengan pesan jelas | `DESIGN_SUMMARY.md §3`, `ENGINE_ARCHITECTURE.md §13` |
| 40 | Save/Load | Proteksi Integritas & Path Traversal | Pengamanan sistem save/load terhadap path traversal (`../`), null-byte injection (`\x00`), dan file corrupt format JSON. | Aksi `save` / `load` | Pemuatan state aman atau `SaveError` | Save rusak ditolak dengan `SaveError` tanpa membuat game crash | `ENGINE_ARCHITECTURE.md §13`, `docs/superpowers/plans/2026-08-14-fix-save-rusak.md` |
| 41 | System | Validasi Data Startup (16 Aturan) | Validasi menyeluruh 16 aturan arsitektur data pada startup sebelum server atau CLI dijalankan. | Dataset `data/` | Status validasi sukses / daftar error | Error validasi menghasilkan exit non-zero | `ENGINE_ARCHITECTURE.md §14`, `tools/validate_data.py` |
| 42 | Interface | Web UI 3-Kolom & Tema Dark-Gold | UI browser stdlib-only: narasi di tengah, statistik di kiri, inventori/quest di kanan, tema xianxia gelap + emas, rendering teks polos statis. | HTTP API JSON dari `web/app.py` | Tampilan browser terstruktur | Error HTTP 400 untuk aksi invalid | `DESIGN_SUMMARY.md §5`, `ENGINE_ARCHITECTURE.md §12` |
| 43 | Interface | CLI Playthrough Mode | Antarmuka CLI interaktif stdlib-only untuk menjalankan seluruh playthrough dari terminal. | Perintah teks terminal (`src/cli.py`) | Output teks terminal berformat | Perintah salah menampilkan pesan bantuan | `AGENTS.md`, `ENGINE_ARCHITECTURE.md §4` |

---

## 3. Edge Cases

Berikut adalah tabel kasus-kasus tepi (*edge cases*) dan perilaku yang teramati / disyaratkan oleh spesifikasi:

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Cultivation Breakthrough | Pemain mencapai level 10 pada ranah tertinggi (Penantang Surga / `order: 9`) dan exp penuh. | Tidak terjadi crash; pemain tetap berada di ranah tertinggi level 10 dengan log `[Sistem] Kau mencapai puncak ranah ini.` |
| 2 | Cultivation Grounding Limit | Pemain mencoba melakukan `grounding` 9 jam dalam satu hari (melebihi batas 8 jam/hari). | Aksi ditolak dengan pesan error kuota harian tercapai; sisa jam tidak terpakai dan waktu tidak dimajukan berlebih. |
| 3 | Cultivation Safe Zone Gating | Pemain menjalankan aksi `grounding`, `rest`, `craft`, atau `save` di lokasi dengan `is_safe: false` (misal di Gerbang atau Arena). | Seluruh aksi tersebut ditolak dengan pesan sistem yang menginstruksikan pemain kembali ke titik aman (Asrama atau Pasar). |
| 4 | Battle Action Lockout | Klien mengirimkan aksi non-battle (seperti `move`, `talk`, `grounding`) saat `pending_battle` sedang aktif. | Aksi non-battle ditolak seketika oleh `GameSession.apply_action` dengan pesan `Kau sedang bertarung — selesaikan atau kabur dulu.` |
| 5 | Battle Skill Pool Constraint | Pemain mencoba mengeksekusi teknik milik akademi lain (misal teknik pedang saat terdaftar di Akademi Elemen) atau sebelum memilih akademi. | Aksi `technique` ditolak karena ID teknik tidak ada dalam `skill_pool` akademi yang aktif. |
| 6 | Battle Qi Depletion | Pemain mengeksekusi teknik bertarung dengan `qi_cost` lebih besar dari sisa Qi saat ini. | Aksi ditolak dengan pesan kekurangan Qi, giliran tidak terbuang, pemain diminta memilih aksi lain. |
| 7 | Battle Escape Failure | Pemain memilih aksi `flee` namun roll RNG kecepatan menghasilkan kegagalan. | Pemain gagal kabur, mencatat log sistem kegagalan, dan giliran langsung beralih ke giliran musuh untuk menyerang. |
| 8 | Battle Companion KO | Kompanion menerima damage fatal (HP mencapai 0) dalam pertarungan. | Kompanion menjadi tidak aktif (`active: false`), tidak lagi menyerang atau ditarget, dan hanya dapat dipulihkan dengan aksi `rest` di titik aman. |
| 9 | Battle Minimum Damage | Serangan pemain dengan attack rendah melawan musuh dengan defense sangat tinggi dan elemen yang dirugikan (0.67×). | Formula kalkulasi damage tetap memberikan nilai minimal `1` (tidak pernah 0 atau negatif). |
| 10 | Battle KO & Exp Reduction | Pemain kalah dalam battle liar atau sparring saat progres exp tingkat saat ini bernilai 5. | Pemain kehilangan 10% exp progres (`round(5 * 0.1) = 0` atau `1`), respawn di titik aman, dan exp tidak pernah menjadi negatif. |
| 11 | Quest Single Active Invariant | Pemain menyelesaikan quest yang memiliki percabangan (`q_akademi_06`). | State langsung bertransisi ke mode dialog pemilihan cabang; engine menjamin tepat satu quest utama yang aktif setelah pilihan dibuat. |
| 12 | Quest DAG Cycle Prevention | Dataset quest sengaja dibuat memiliki siklus (misal `q5 -> q7 -> q5`). | `tools/validate_data.py` (aturan §14-3) mendeteksi siklus melalui traversal DFS dan menggagalkan startup dengan exit non-zero. |
| 13 | Quest Objective Time Window | Pemain memasuki `loc_ruang_lonceng` pada siang hari (pukul 12:00) saat menjalankan `q_akademi_06`. | Objektif `reach` tidak terpenuhi karena berada di luar jendela waktu (19:00–06:00); pemain harus menunggu malam hari. |
| 14 | Side Quest Conflict Prevention | Side quest baru dibuat menuntut NPC atau lokasi yang sedang digunakan oleh main quest yang aktif. | Validator data aturan §14-5 dan §14-10 menolak dataset saat startup untuk mencegah benturan alur. |
| 15 | Economy Insufficient Gold | Pemain mencoba membeli item di toko pedagang dengan saldo emas kurang dari harga beli. | Aksi `shop_buy` ditolak dengan pesan error emas tidak mencukupi, state emas dan inventori tetap utuh. |
| 16 | Economy Inventory Zero Item | Pemain menjual seluruh item yang dimilikinya hingga count mencapai 0. | Slot item tersebut dihapus bersih dari kamus/list inventori pemain (tidak meninggalkan entri count 0). |
| 17 | Save Path Traversal Attack | Klien mengirimkan aksi `save` atau `load` dengan parameter nama `../../etc/passwd` atau `..\\malicious`. | `_safe_save_path` mendeteksi bahwa path berada di luar folder `saves/` dan melempar `SaveError` / pesan penolakan. |
| 18 | Save Corrupted JSON Format | File save di disk mengalami korupsi bit atau format JSON tidak lengkap (`{rusak`). | `GameSession.load` menangkap `json.JSONDecodeError` dan membungkusnya menjadi `SaveError` dengan pesan jelas tanpa memicu unhandled exception. |

---

## 4. Rincian Spesifikasi Teknis per Subsistem

### 4.1 Subsistem Kultivasi (Cultivation System)
- **Struktur Tangga Ranah**:
  1. Pengumpul Qi (炼气 Liànqì) — Ranah aktif Fase 1
  2. Pembangun Fondasi (筑基 Zhùjī) — Ranah lanjutan
  3. Pembentuk Inti (金丹 Jīndān)
  4. Jiwa Baru Lahir (元婴 Yuányīng)
  5. Transformasi Roh (化神 Huàshén)
  6. Pemurni Kehampaan (炼虚 Liànxū)
  7. Penyatu (合体 Hétǐ)
  8. Mahayana (大乘 Dàchéng)
  9. Penantang Surga (渡劫 Dùjié)
- **Tingkat per Ranah**: 10 tingkat (`realm_level` 1 s.d. 10).
- **Formula Stat**:
  $$\text{HP}_{\text{max}} = \text{base\_hp} + (\text{realm\_level} - 1) \times \text{hp\_per\_level}$$
  $$\text{Qi}_{\text{max}} = \text{base\_qi} + (\text{realm\_level} - 1) \times \text{qi\_per\_level}$$
- **Formula Kebutuhan Exp**:
  $$\text{exp\_needed}(\text{level}) = \text{round}(10 \times 1.2^{\text{level} - 1})$$
- **Aktivitas Perolehan Exp (Base)**:
  - Meditasi (Grounding): 2 exp / jam (maks 8 jam/hari)
  - Berburu Liar: 6 exp / kill
  - Menang Sparing: 8 exp / win
  - Kalah Sparing: 3 exp / loss
  - Quest Rewards: 3 s.d. 18 exp
- **Multiplier Akar Spiritual**: Semua exp aktivitas dikalikan tier akar (`akar_low` 0.8×, `akar_mid` 1.0×, `akar_high` 1.25×, `akar_peak` 1.5×).
- **Target Balancing Fase 1**: Pemain menyelesaikan Arc Akademi pada **Pengumpul Qi Tingkat 5–6** (jalur quest murni ≈ Lv.5, rajin grinding ≈ Lv.6).

### 4.2 Subsistem Pertarungan (Battle Engine)
- **Urutan Giliran**: Fixed alternate (Pemain → Musuh ronde bergantian).
- **Regenerasi Qi**: $5\%$ dari $\text{Qi}_{\text{max}}$ di awal giliran setiap karakter.
- **Formula Damage**:
  $$\text{Base Damage} = \text{Attack} \times \left(\frac{100}{100 + \text{Defense}}\right) \times \text{Multiplier}_{\text{elemen}} \times \text{RNG}(0.8, 1.2)$$
  $$\text{Final Damage} = \max(1, \text{round}(\text{Base Damage} \times (\text{Multiplier}_{\text{crit}} \text{ jika crit else } 1.0)))$$
- **Matriks Keunggulan Elemen 五行**:
  - Logam $\rightarrow$ Kayu $\rightarrow$ Tanah $\rightarrow$ Air $\rightarrow$ Api $\rightarrow$ Logam
  - Keunggulan (克制): $1.5\times$
  - Kelemahan (被克): $0.67\times$
  - Netral: $1.0\times$
- **Parameter Kritikal**: Peluang 8% (`0.08`), Pengali 1.5× (`1.5`).
- **Mekanik Kompanion (Akademi Summoning)**:
  - Diberikan saat memilih `akademi_summoning` (`komp_roh_awan`).
  - Stat scaling: $\text{Base} + \text{Level} \times \text{Scale}$ ($\text{HP} +12/\text{lvl}, \text{Atk} +2/\text{lvl}, \text{Def} +1/\text{lvl}, \text{Spd} +0.5/\text{lvl}$).
  - Aksi otomatis tiap ronde setelah aksi pemain.
  - Musuh memiliki probabilitas 50% menarget kompanion saat aktif.
  - HP kompanion persisten, pulih hanya lewat `rest` di titik aman.

### 4.3 Subsistem Moralitas & Dao (Morality Engine)
- **Rentang Skor**: Integer $[-100, +100]$, default `0`.
- **Dampak Pilihan 3 Sikap**:
  - `3aa` (Konfrontasi Langsung Penatua An): Moralitas $+8$, Relasi Han Xiu $+5$, Relasi Su Qing $+5$, Reward Pedang Angin.
  - `3ab` (Kumpulkan Bukti Diam-Diam via Mo Yun): Moralitas $+5$, Relasi Mo Yun $+5$.
  - `3b` (Ambil Keuntungan / Peras Zhou Yan): Moralitas $-8$, Relasi Su Qing $-5$, Reward Gold $+30$.
  - `3c` (Berdiam Diri): Moralitas $-2$, Relasi Su Qing $-3$.
- **Koneksi Ending Jangka Panjang**: 3 Ending tematik (Reformer, Destroyer, Ascetic) ditentukan oleh kombinasi pilihan cabang moralitas dan akumulasi skor Dao pada akhir arc lanjutan.

### 4.4 Subsistem Dialog & Memori Tianyuan Ling
- **Node Dialog**: Struktur berbasis graf dengan speaker (`npc`, `player`, `narration`, `system`), evaluasi kondisi (`condition`), dan efek mutasi state (`effects`).
- **Gating Memori**:
  - `mem_01` (Istana yang Sunyi): Terbuka di akhir Act 1 (`q_akademi_05`). Mengubah sikap Chen Xu menjadi lebih berhati-hati.
  - `mem_02` (Kebaikan yang Terlupakan): Terbuka pada cabang `3aa` & `3ab`. Menjelaskan asal-usul pemberian Tianyuan Ling oleh dewa tersesat.
  - `mem_03` (Racun di Balik Senyum): Terbuka pada cabang `3b`. Menjelaskan memori peracunan oleh selir kaisar.
  - `mem_04` (Pengasingan): Terbuka pada cabang `3c`. Menjelaskan memori terusir dari istana.
- **Prinsip Isolasi Naratif**: Memori berstatus *murni naratif* dan tidak memberikan bonus stat/kekuatan tempur mekanik.

### 4.5 Graf Quest Utama (DAG) & Side Quests
- **Topologi Graf Utama**:
  ```
  q_akademi_01 (Gerbang - Penjaga)
       ↓
  q_akademi_02 (Ujian Akar - Gu Canghai)
       ↓
  q_akademi_03 (Sparing Wajib - Han Xiu)
       ↓
  q_akademi_04 (Pilih Akademi - 3 Paviliun)
       ↓
  q_akademi_05 (Hari Pertama & mem_01 - Su Qing)
       ↓
  q_akademi_06 (Insiden Ruang Lonceng Malam Hari)
       ├─► q_akademi_3aa (Konfrontasi Langsung) ──┐
       ├─► q_akademi_3ab (Bukti Diam-Diam)      ──┤
       ├─► q_akademi_3b  (Ambil Keuntungan)     ──┼─► q_akademi_07 (Kebenaran Penatua / Akhir Arc)
       └─► q_akademi_3c  (Berdiam Diri)         ──┘
  ```
- **Side Quests (Repeatable)**:
  - `q_side_berburu`: Mengalahkan 2 musuh liar di Wilayah Berburu (Giver: Pemburu Tua, Reward: 20 exp, 15 gold, 1 material tulang).
  - `q_side_suqing`: Mengumpulkan 3 Herba Awan (Giver: Su Qing, Reward: 15 exp, 10 gold, relasi +2).
  - `q_side_moyun`: Mengumpulkan 2 Herba Awan untuk perpustakaan (Giver: Mo Yun, Reward: 12 exp, 8 gold, relasi +2).

### 4.6 Graf Dunia & Lokasi
- **9 Lokasi Terdefinisi**:
  1. `loc_gerbang_akademi` (Gerbang utama, koneksi: Aula Ujian, Pasar, Wilayah Berburu)
  2. `loc_aula_ujian` (Aula tes, koneksi: Gerbang, Paviliun, Asrama, Arena)
  3. `loc_paviliun` (Lapangan 3 Paviliun, koneksi: Aula Ujian, Perpustakaan)
  4. `loc_perpustakaan` (Perpustakaan Mo Yun, koneksi: Paviliun, Ruang Lonceng)
  5. `loc_ruang_lonceng` (Ruang pusaka insiden, koneksi: Perpustakaan)
  6. `loc_asrama` (**Titik Aman**, koneksi: Aula Ujian, Pasar, Arena)
  7. `loc_pasar` (**Titik Aman**, kios pedagang, koneksi: Gerbang, Asrama)
  8. `loc_arena` (Tempat sparring Han Xiu, koneksi: Asrama, Aula Ujian)
  9. `loc_wilayah_berburu` (Hutan monster & herba, koneksi: Gerbang)

---

## 5. Aturan Validasi Data (16 Aturan ENGINE_ARCHITECTURE §14)

1. **Aturan 1 (Format Dokumen)**: Seluruh file JSON wajib dapat di-parse dengan benar dan file CSV memiliki header baris lengkap serta tipe numerik valid.
2. **Aturan 2 (Integritas Referensi)**: Seluruh referensi lintas berkas (quest, dialog, NPC, item, musuh, lokasi, teknik, ingatan) wajib merujuk pada entitas yang terdaftar.
3. **Aturan 3 (Topologi DAG Quest)**: Graf quest utama wajib asiklik (bebas dari siklus/loop) yang dibuktikan melalui traversal deteksi siklus DFS.
4. **Aturan 4 (Mapping Pilihan Cabang)**: Setiap node quest dengan sisi keluar $> 1$ wajib memiliki atribut `choice_id` dan seluruh nilai `option` pada `next` wajib terpetakan pada opsi dialog terkait.
5. **Aturan 5 (Isolasi Konflik Quest)**: Tidak boleh ada dua quest yang dapat aktif bersamaan yang menuntut NPC, lokasi, atau target objektif yang sama.
6. **Aturan 6 (Keunikan ID Global)**: Seluruh ID (quest, dialog, NPC, item, musuh, lokasi, teknik, ingatan) wajib unik secara global dalam domainnya.
7. **Aturan 7 (Validitas Konfigurasi Starting)**: Berkas `config.json` wajib memiliki `starting.current_quest` yang valid, daftar akademi terdaftar, dan siklus `element_advantage` yang lengkap.
8. **Aturan 8 (Spesifikasi Side Quest)**: Setiap quest sampingan wajib memiliki atribut `available_from {day, hour}`, dan jika memiliki `cooldown`, nilainya harus $> 0$.
9. **Aturan 9 (Restriksi Repeatability)**: Atribut `repeatable: true` hanya diizinkan untuk quest bertipe `kind: "side"`.
10. **Aturan 10 (Isolasi Target Repeatable vs Main)**: Quest sampingan yang dapat diulang dilarang keras menuntut NPC, lokasi, atau objek yang dipakai oleh quest utama.
11. **Aturan 11 (Integritas Resep Alkimia)**: Resep pada `recipes.json` wajib menghasilkan item yang terdaftar di `items.csv`, bahan-bahan terdaftar, dan bahan tidak boleh sama dengan hasil racikan.
12. **Aturan 12 (Integritas Toko NPC)**: Seluruh item dalam daftar `buy` dan `sell` pada toko NPC wajib terdaftar di `items.csv`.
13. **Aturan 13 (Integritas Senjata & Akar)**: Seluruh item bertipe `weapon` wajib memiliki nilai `power > 0`; konfigurasi `roots.tiers` wajib terdefinisi dan `default` terdaftar.
14. **Aturan 14 (Konsistensi Graf Lokasi)**: Atribut `is_safe` berupa boolean; daftar `connections` antar lokasi wajib simetris dan merujuk pada ID lokasi yang ada.
15. **Aturan 15 (Integritas Kompanion)**: Data pada `companions.json` memiliki ID unik, nilai base stat valid, dan referensi elemen terdaftar pada siklus lima elemen.
16. **Aturan 16 (Parameter Pertarungan Battle)**: Konfigurasi `config.battle` memiliki nilai `crit_chance` di rentang $[0, 1]$, `turn_order` terdaftar, dan `damage_formula` terdaftar.

---

## 6. Batasan Cakupan Fase (Scope Boundaries)

| Subsistem / Dimensi | Fase 1 (Arc Akademi — Bukti Konsep) | Fase 2 (Arc Sekte & Kekaisaran) | Fase 3 (Arc Final & Dunia Penuh) |
|---|---|---|---|
| **Alur Narasi** | Arc Akademi saja (Changfeng Cheng, Gerbang s.d. Kebenaran Lonceng). | Naik ke tingkat Sekte regional & intrik Kekaisaran asal Long Tianxu. | Perang sistemik skala benua kultivasi & konfrontasi struktur kekuasaan. |
| **Ranah Kultivasi** | Pengumpul Qi (Tingkat 1–10) aktif; Pembangun Fondasi sebagai target lanjutan. | Pembangun Fondasi, Pembentuk Inti, Jiwa Baru Lahir. | Transformasi Roh hingga Penantang Surga (9 Ranah Penuh). |
| **Teknik & Jurus** | 9 Teknik dasar (3 per akademi: Serangan, Perisai, Pemulihan). | Puluhan teknik lanjutan, teknik gabungan, dan pembukaan lintas akademi. | Seni bela diri tingkat tinggi, teknik warisan surga, manipulasi hukum dunia. |
| **Sistem Kompanion** | 1 Binatang roh dasar (Roh Awan) untuk jalur Summoning dengan auto-attack. | Evolusi binatang roh, penjinakan hewan buas baru di alam liar. | Kompanion legendaris, sinergi taktik tempur penuh. |
| **Ekonomi & Pasar** | 1 Toko Kios pedagang dengan harga statis di Pasar Changfeng. | Pasar dinamis, fluktuasi harga antar wilayah sekte/kota. | Rumah lelang, ekonomi global, monopoli material langka. |
| **Alkimia & Crafting** | 2 Resep dasar (Pil Qi & Pil Pemulihan) dari bahan buruan. | Tungku alkimia, resep pil tingkat menengah (penembus ranah), risiko kegagalan. | Alkimia tingkat dewa, penciptaan artefak spiritual. |
| **Tianyuan Ling** | Pasif murni: panel UI penampil memori (4 entri) & notifikasi log sistem. | Dialog interaktif terbatas dengan Sistem, pembukaan memori hidup pertama lebih dalam. | Sistem aktif penuh, pengungkapan takdir reinkarnasi dan kehendak dewa. |
| **Ending Permainan** | Akhir Arc Akademi (q5/q7), layar penutup mengarahkan ke Arc Sekte. | Percabangan faksi besar Sekte & Kekaisaran. | 3 Ending tematik final: Reformer, Destroyer, Ascetic. |
| **Antarmuka (UI)** | Web UI 3-kolom berbasis teks statis & terminal CLI stdlib-only. | Peningkatan UI web responsif & visual layout lanjutan. | Antarmuka grafis kaya / visual novel hybrid. |

---

## 7. Logic Chain

1. **Premis Dasar**: Dokumen `GDD.md` dan `DESIGN_SUMMARY.md` menetapkan arsitektur data-driven di mana seluruh aturan, statistik, dan dialog disimpan di `data/`, sementara mesin `src/engine/` bertindak sebagai evaluator logika murni.
2. **Karakteristik Naratif**: Alur cerita dirancang sebagai DAG yang menjamin tidak adanya tumpang tindih quest utama (satu quest aktif pada satu waktu). Pilihan sikap pada insiden Lonceng menggerakkan skor moralitas dan relasi NPC tanpa memutus konvergensi ke quest akhir `q_akademi_07`.
3. **Pemisahan Narasi vs Mekanik**: Memori masa lalu (`mem_01` s.d. `mem_04`) dipisahkan secara ketat dari peningkatan stat/power pemain untuk mencegah bottleneck antara progres cerita dan progresi kultivasi.
4. **Keamanan & Konsistensi**: Aturan validasi startup (§14) dan gating aksi sesi (`is_safe`, `pending_battle`) menjamin bahwa integritas state permainan selalu terjaga, baik saat dimainkan melalui CLI maupun antarmuka Web HTTP.

---

## 8. Caveats

- **Cooldown Side Quest**: Field `repeat_cooldown` pada side quest telah divalidasi oleh validator (§14-8), namun sesuai catatan `ENGINE_ARCHITECTURE.md §17`, mekanisme delay cooldown berbasis jam belum diimplementasikan di engine (quest saat ini langsung tersedia kembali setelah selesai).
- **Balance Sparing Han Xiu & Double Reward**: Pada playtest putaran 2 tercatat bahwa menang sparing pada `q_akademi_03` memberikan reward dobel (exp spar + reward quest). Dokumen mencatat ini sebagai *by-design overlap* yang telah disahkan untuk memastikan pemain mencapai level 2 dengan mulus.
- **Eksklusivitas Akademi**: Pada Fase 1, teknik dari akademi lain terkunci permanen untuk playthrough tersebut.

---

## 9. Conclusion

Spesifikasi *Tian Xu: Second Life* Fase 1 (Arc Akademi) telah **terdefinisi secara lengkap, terstruktur, dan tervalidasi penuh**. Dokumen desain (`docs/GDD.md`, `docs/DESIGN_SUMMARY.md`, `docs/STORY_FASE1.md`, `docs/ENGINE_ARCHITECTURE.md`) dan implementasi saat ini memiliki sinkronisasi yang sangat tinggi:
- Seluruh 43 fitur Fase 1 telah dikatalogkan dengan input, output, dan batas error.
- Alur quest DAG 4-cabang konvergen telah terpetakan secara presisi ke data dan dialog.
- 16 aturan validasi data (§14) telah ditegakkan oleh validator dan diverifikasi oleh suite pengujian otomatis.
- Batasan antara Fase 1 dan fase-fase berikutnya telah didefinisikan secara tegas untuk memandu peta jalan (*roadmap*) pengembangan selanjutnya.

---

## 10. Verification Method

Spesifikasi dan integritas data/kode dapat diverifikasi secara independen melalui perintah berikut dari root repositori:

1. **Validasi Data Statis (16 Aturan §14)**:
   ```bash
   python3 tools/validate_data.py
   ```
   *Ekspektasi*: Output `VALIDASI LULUS — quest: 14, dialog: 10, npc: 9, lokasi: 9, item: 6, musuh: 3, ingatan: 4` dengan exit code 0.

2. **Eksekusi Pengujian Otomatis (Pytest Suite)**:
   ```bash
   python3 -m pytest -q
   ```
   *Ekspektasi*: Seluruh 93 skenario uji lulus (100% pass rate).

3. **Verifikasi Cakupan Logika Engine**:
   ```bash
   python3 -m pytest --cov=src --cov-report=term-missing
   ```
   *Ekspektasi*: Total line coverage $\ge 84\%$.

4. **Verifikasi Berkas Spesifikasi**:
   - Periksa keberadaan berkas ini di: `/home/dienk/tian-xu-second-life/.agents/teamwork_preview_spec_miner_survey_2/handoff.md`.
