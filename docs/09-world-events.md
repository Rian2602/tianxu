# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 09. World Event Bible

**Status:** DRAFT — Phase 10 of 18
**Depends on:** `01-arc-overview.md`, `02-chapter-breakdown.md`, `03-quest-graph-arc1-2.md`, `03b-quest-graph-arc3-7.md`, `08-npc-location-catalog.md`
**Konteks:** MSB §11 memberi enam CONTOH event ("Contoh:" — bukan daftar wajib lengkap): Mountain Gate Incident, Spiritual Collapse, Tian Xu Formation Failure, Entity Awakening, Faction Conflict, Academy Lockdown. Audit terhadap seluruh dokumen sebelumnya menemukan: Mountain Gate Incident sudah terformalkan penuh (Quest Graph); Spiritual Collapse dirujuk luas sebagai state tapi belum sebagai event object formal; Formation Failure, Entity Awakening, dan Faction Conflict SUDAH ada secara implisit — ketiganya adalah aspek simultan dari satu kalimat narasi Chapter 7.1 yang sudah dirancang di Phase 3; Academy Lockdown TIDAK memiliki jejak apa pun di dokumen manapun.

---

## `event_a05_spiritual_collapse`

| Field | Value |
|---|---|
| `event_id` | `event_a05_spiritual_collapse` |
| `trigger` | Otomatis di awal Arc V — bukan dipicu pilihan pemain, melainkan konsekuensi kumulatif dari eksploitasi sistem cultivation yang sudah berjalan ribuan tahun (dijelaskan Arc IV) |
| `prerequisites` | `flag_arc4_complete == true` |
| `affected_locations` | `loc_outer_region` (dikonfirmasi Phase 9 sebagai kandidat kuat), berpotensi meluas ke wilayah tambahan yang belum diberi ID spesifik — `[DESIGN GAP]` apakah perlu 2-3 wilayah terdampak tambahan untuk skala "global" yang MSB janjikan ("masalah menjadi global," Arc Overview §Arc V), atau cukup 1 wilayah dikenal (`loc_outer_region`) plus deskripsi naratif tentang wilayah lain yang tidak perlu location_id formal. **Direkomendasikan: opsi kedua** — menambah lokasi baru hanya untuk "skala" berisiko jadi world-building tanpa fungsi gameplay (fetch-quest generator), bertentangan dengan MSB §25 |
| `affected_npcs` | Found family (reaksi bervariasi, memicu divergensi Chapter 5.3); NPC di `loc_outer_region` termasuk kandidat `npc_mountain_gate_villager` |
| `affected_factions` | Liberation Faction mendapat momentum wacana (dicatat Faction Bible); Tian Xu Orthodox menghadapi tekanan legitimasi |
| `state_changes` | **Writes:** `world_event_a05_spiritual_collapse = active` (sudah tercatat Quest Graph) |
| `available_quests` | `quest_a05_c01_001` hingga `quest_a05_c05_005` — event ini adalah PAYUNG untuk seluruh Arc V, bukan quest tunggal |
| `unavailable_quests` | Konten optional Arc I-IV yang bersifat "normal academy life" (mis. dialog opsional santai dengan guru pavilion) menjadi tonally tidak sesuai — direkomendasikan tetap DAPAT diakses secara teknis tapi dengan framing berbeda (guru yang biasanya santai kini disibukkan penanganan krisis), bukan benar-benar diblokir |
| `dialogue_changes` | Seluruh dialogue Arc V-VII memiliki potensi modifier "krisis" — sudah terformalkan sebagian di Dialogue Bible (`dialog_a07_d001`), berlaku juga untuk dialog ambient/generik yang tidak dispesifikasikan detail di sini |
| `visual_implications` | `[DESIGN GAP — bukan tanggung jawab dokumen naratif]` — dead zones, monster mutation, spiritual storms, corrupted formations (istilah MSB langsung) memerlukan spesifikasi visual dari tim art, bukan tim narasi |
| `future_consequences` | Menjadi prasyarat langsung `world_event_a07_the_last_night` (lihat di bawah) — Spiritual Collapse yang tidak/belum terselesaikan penuh adalah kondisi awal Chapter 7.1 |
| `ending_implications` | Skala kerusakan Spiritual Collapse (dimoderasi hasil Mountain Gate Incident) memengaruhi tone epilogue di SEMUA 5 ending — dunia yang "lebih rusak" vs "lebih terselamatkan" mengubah rasa kemenangan/kehilangan tiap ending tanpa mengubah ending mana yang dicapai |

---

## `event_a05_mountain_gate_incident` (Formalisasi Ulang — Cross-Reference)

**Catatan:** event ini SUDAH terformalkan penuh sebagai quest+branch di Quest Graph (`quest_a05_c02_002`, `branch_a05_c02_b01`). Entry ini HANYA melengkapi field-field khusus World Event yang tidak tercakup format Quest Graph (affected_locations, dialogue_changes secara eksplisit), untuk konsistensi katalog — bukan mendefinisikan ulang mekanismenya.

| Field | Value |
|---|---|
| `event_id` | `event_a05_mountain_gate_incident` |
| `trigger` | Sub-event dari `event_a05_spiritual_collapse`, dipicu di Chapter 5.2 |
| `prerequisites` | `world_event_a05_spiritual_collapse == active` |
| `affected_locations` | `loc_mountain_gate` |
| `affected_npcs` | `npc_mountain_gate_villager` (rekomendasi Phase 9) |
| `affected_factions` | Tidak langsung, tapi hasil (`flag_mountain_gate_changed`/`repeated`) memengaruhi momentum Liberation/Reformists (dicatat Faction Bible) |
| `state_changes` | Lihat `branch_a05_c02_b01` di Quest Graph — tidak diduplikasi di sini |
| `available_quests` / `unavailable_quests` | Lihat Quest Graph |
| `dialogue_changes` | Chapter 5.3 (Found Family Crisis) dialog dimodifikasi berdasarkan outcome — sudah dicatat implisit di Quest Graph, dikonfirmasi eksplisit di sini sebagai world_event dialogue_changes field |
| `visual_implications` | `[DESIGN GAP — tim art]` |
| `future_consequences` | Salah satu world_state_conditions Ending Matrix (dicatat Quest Graph) |
| `ending_implications` | Sudah dicatat Quest Graph — dikonfirmasi di sini untuk kelengkapan katalog |

---

## `event_a07_the_last_night` (Konsolidasi Formation Failure + Entity Awakening + Faction Conflict)

**Keputusan produksi kunci fase ini:** ketiga event MSB §11 — Tian Xu Formation Failure, Entity Awakening, Faction Conflict — DIKONSOLIDASIKAN menjadi SATU world_event dengan tiga aspek simultan, bukan tiga event terpisah. Dasar keputusan ini adalah audit yang menemukan ketiganya sudah tertanam dalam satu kalimat narasi Chapter 7.1 sejak Phase 3 ("formation mulai gagal; Entity mulai keluar; faksi bergerak") — memisahkannya menjadi tiga event_id berbeda akan menciptakan tiga entri yang secara mekanis identik (trigger sama, lokasi sama, konsekuensi sama: Chapter 7.1) hanya berbeda label, yang bertentangan dengan prinsip "fewer + stronger" MSB §25.

| Field | Value |
|---|---|
| `event_id` | `event_a07_the_last_night` |
| `trigger` | Otomatis di awal Arc VII — kulminasi dari seluruh Spiritual Collapse yang tidak (atau belum sepenuhnya) terselesaikan sejak Arc V |
| `prerequisites` | `state_final_principle != null` (dari Chapter 6.4) |
| `affected_locations` | `loc_tianxu_main_hall` (hub utama), `loc_tianxu_gate` (kontras visual dengan Arc I), `loc_tianxu_deepest_chamber` (tujuan akhir) |
| `affected_npcs` | SELURUH cast — found family, Mentor, Grandmaster, Shen Luo, perwakilan faksi (dicatat Quest Graph sebagai hub NPC terpadat) |
| `affected_factions` | Keempat faksi ditambah Entity sekaligus — titik konvergensi seluruh Faction Bible |
| `state_changes` | **Writes:** `flag_last_night_complete = true` (sudah tercatat Quest Graph) |
| `available_quests` | `quest_a07_c01_001` |
| `unavailable_quests` | Seluruh optional content dari Arc I-VI yang belum diselesaikan menjadi TIDAK LAGI dapat diakses setelah titik ini — Chapter 7.1 secara struktural adalah "titik tanpa jalan kembali" terakhir sebelum final act. **`[ENGINE RISK]`** dicatat: perlu memastikan UI/UX memberi peringatan jelas kepada pemain sebelum melewati titik ini, karena banyak optional content (dialog opsional Grandmaster, investigasi tambahan Mei Ruo, dll) menjadi permanen tidak dapat diakses |
| `dialogue_changes` | SELURUH matrix `dialog_a07_d001` yang sudah diformalkan Phase 8 |
| `visual_implications` | Tiga aspek simultan: (1) formation gagal — representasi visual keretakan/instabilitas di `loc_tianxu_deepest_chamber` dan area sekitarnya; (2) Entity mulai keluar — manifestasi parsial, BUKAN kemunculan penuh (kemunculan penuh baru di Chapter 7.2); (3) faksi bergerak — representasi visual posisi berbeda tiap faksi di sekitar `loc_tianxu_main_hall`. `[DESIGN GAP — tim art]` untuk detail spesifik |
| `future_consequences` | Langsung mengarah ke `quest_a07_c02_002` (Final Confrontation) |
| `ending_implications` | Bagaimana ketiga aspek ini terjadi (skala kerusakan formation, seberapa jauh Entity "keluar," bagaimana faksi memposisikan diri) menjadi bagian dari world_state_conditions Ending Matrix — TIDAK menentukan ending mana yang dicapai (itu ranah `quest_a07_c03_003`), tapi memengaruhi KUALITAS/TONE epilogue |

**Catatan MSB compliance:** konsolidasi ini TIDAK mengubah lore atau menghapus elemen MSB — ketiga nama event (Formation Failure, Entity Awakening, Faction Conflict) tetap ada secara konseptual sebagai ASPEK dari `event_a07_the_last_night`, direkomendasikan tetap dirujuk dengan nama individualnya dalam dokumentasi produksi lanjutan (mis. "aspek Formation Failure dari The Last Night") untuk menjaga keterlacakan ke MSB, meski secara data-driven mereka satu event_id.

---

## Academy Lockdown — Evaluasi Design Gap

**Status:** TIDAK DIFORMALKAN sebagai event terpisah di fase ini. Berikut penjelasan keputusan, bukan gap yang diam-diam diabaikan:

MSB §11 menyebut "Academy Lockdown" sebagai salah satu dari enam CONTOH event (kata MSB: "Contoh:" mendahului daftar, menandakan ini adalah ilustrasi jenis event yang mungkin, bukan daftar wajib lengkap yang harus semuanya terpakai). Audit menyeluruh terhadap sembilan file sebelumnya tidak menemukan satu pun jejak naratif — baik eksplisit maupun implisit — yang mengarah ke skenario penguncian akademi.

**Tiga opsi dipertimbangkan:**
1. **Memaksakan Academy Lockdown sebagai event baru** — ditolak, karena akan memerlukan menciptakan quest/chapter baru yang belum ada dasarnya di Phase 3-4, berisiko melanggar Critical Constraint (tidak diam-diam menganggap gap sebagai canon) jika saya memutuskan sendiri KAPAN dan MENGAPA lockdown terjadi tanpa basis MSB
2. **Memetakan Academy Lockdown ke event yang sudah ada** — dipertimbangkan (mis. sebagai bagian dari reaksi Grandmaster terhadap `state_truth_spread_level` tinggi, yang sudah dicatat Faction Bible sebagai "faction_reactions... pengawasan lebih ketat"), tapi ini sudah tercakup istilah lain (`autonomous_trigger_condition` Grandmaster, Character Bible) — menciptakan event_id terpisah untuk sesuatu yang sudah punya mekanisme akan redundan
3. **Mencatatnya sebagai contoh MSB yang sengaja tidak diambil** — **DIPILIH**. Konsisten dengan prinsip bahwa tidak semua elemen "contoh" dalam instruksi produksi wajib direalisasikan sebagai konten — realisasi paksa berisiko menghasilkan konten filler yang MSB sendiri eksplisit larang

**Rekomendasi jika tim produksi tetap menginginkan Academy Lockdown:** cara paling konsisten mengintegrasikannya adalah sebagai VARIAN dari reaksi Grandmaster yang sudah tercatat (`autonomous_trigger_condition`, Character Bible) — bukan event baru, melainkan salah satu BENTUK KONKRET dari "tindakan pengamanan institusional" yang sudah dijanjikan. Ini akan memerlukan revisi kecil ke Character Bible (menspesifikasikan bahwa salah satu bentuk tindakan pengamanan adalah lockdown parsial), bukan penambahan world_event baru — direkomendasikan sebagai catatan untuk fase revisi, bukan dieksekusi sekarang tanpa konfirmasi.

---

## World Event Coverage Verification

| Event MSB §11 | Status | event_id (jika ada) |
|---|---|---|
| Mountain Gate Incident | ✅ Terformalkan (Quest Graph + cross-reference di sini) | `event_a05_mountain_gate_incident` |
| Spiritual Collapse | ✅ Terformalkan penuh fase ini | `event_a05_spiritual_collapse` |
| Tian Xu Formation Failure | ✅ Terformalkan sebagai aspek `event_a07_the_last_night` | (konsolidasi) |
| Entity Awakening | ✅ Terformalkan sebagai aspek `event_a07_the_last_night` | (konsolidasi) |
| Faction Conflict | ✅ Terformalkan sebagai aspek `event_a07_the_last_night` | (konsolidasi) |
| Academy Lockdown | ⚠️ Sengaja tidak diformalkan — dijelaskan di atas, bukan gap yang terlewat | N/A |

---

## Design Gap & Recommendation Ringkasan Fase Ini

1. **Jumlah wilayah terdampak Spiritual Collapse** — direkomendasikan TIDAK menambah location_id baru murni untuk kesan skala; deskripsi naratif tanpa ID formal dianggap cukup
2. **Academy Lockdown** — keputusan eksplisit untuk TIDAK diformalkan, dengan tiga opsi dipertimbangkan dan alasan pemilihan dicatat terbuka; rekomendasi jalur integrasi diberikan jika tim produksi menginginkannya di kemudian hari
3. **[ENGINE RISK]** dicatat eksplisit: titik tanpa-jalan-kembali di awal `event_a07_the_last_night` memerlukan UI/UX warning yang jelas — ini adalah risiko implementasi, bukan risiko naratif, tapi dicatat di sini karena munculnya justru dari struktur naratif (konvergensi total sebelum final act)

---

**File berikutnya:** `10-consequence-convergence-matrix.md` — Consequence Matrix dan Convergence Matrix (Phase 11-12 digabung dalam satu file karena keduanya saling merujuk erat), memformalkan struktur Immediate→Short-term→Mid-term→Long-term→Ending untuk setiap major choice yang sudah tercatat, dan detail penuh setiap convergence_id yang sudah muncul di Quest Graph.
