# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 03. Quest Graph — Main Quest & Branching Quest

**Status:** DRAFT — Phase 4 of 18
**Depends on:** `00-narrative-architecture.md`, `01-arc-overview.md`, `02-chapter-breakdown.md`
**Struktur wajib per quest:** setiap Main Quest mencantumkan state yang **dibaca** (prerequisite) dan state yang **ditulis** (world_state_changes) secara eksplisit — bukan sekadar quest_id pendahulu. Ini menegakkan model `EVENT → STATE CHANGE → CONSEQUENCE → NEW POSSIBILITY → PLAYER CHOICE → BRANCH → CONSEQUENCE → CONVERGENCE → FUTURE PAYOFF` dari Narrative Architecture §0.2.

**Cakupan file ini:** Arc I dan Arc II (density lebih rendah, dijadikan pola rujukan konsisten untuk Arc III-VII di file lanjutan `03b-quest-graph-arc3-7.md`).

---

## Legenda Branch Classification

Setiap branch diklasifikasikan salah satu dari tiga tingkat (sesuai instruksi wajib):

- **COSMETIC** — mengubah dialog/flavor text, tidak mengubah state naratif signifikan
- **MEANINGFUL** — mengubah relationship/reputation/akses konten dalam Arc yang sama
- **MAJOR** — payoff eksplisit beberapa Chapter atau Arc kemudian (wajib untuk minimal satu branch di tiap Arc)

---

# ARC I — A NEW LIFE

## `quest_a01_c01_001` — Arrival

| Field | Value |
|---|---|
| `quest_id` | `quest_a01_c01_001` |
| `title` | Arrival |
| `arc` | `arc_01` |
| `chapter` | `chapter_01_01` |
| `quest_type` | Main Quest |
| `narrative_function` | World Building, Foreshadowing |
| `gameplay_function` | Tutorial diegetic — pergerakan dasar, pengenalan UI dialog |
| `prerequisites` | Tidak ada — quest pembuka campaign |
| `objectives` | Tiba di Tian Xu; menjalani aptitude test |
| `success_conditions` | Aptitude test selesai (hasil tidak memengaruhi gate — MSB eksplisit "hasilnya tidak luar biasa") |
| `failure_conditions` | Tidak ada failure state — ini adalah onboarding wajib |
| `involved_npcs` | Pemeriksa aptitude (Ambient NPC, `[DESIGN GAP]` nama — Phase 9) |
| `locations` | `loc_tianxu_approach_road`, `loc_tianxu_gate` |
| `required_items` | Tidak ada |
| `required_skills` | Tidak ada |
| `dialogue_events` | Mimpi koridor terbakar ("Jangan buka gerbang itu!") — dipicu otomatis, bukan dialog choice |
| `branching_points` | Tidak ada di quest ini |
| `consequences` | Menetapkan `flag_dream_a01_01_seen = true` |
| `world_state_changes` | **Writes:** `flag_dream_a01_01_seen = true` |
| `relationship_changes` | Tidak ada |
| `faction_changes` | Tidak ada |
| `memory_triggers` | `memory_a01_m01` (dream fragment, lihat Phase 7) |
| `next_quests` | `quest_a01_c01_002` |
| `convergence_id` | N/A |

---

## `quest_a01_c01_002` — Registration

| Field | Value |
|---|---|
| `quest_id` | `quest_a01_c01_002` |
| `title` | Registration |
| `arc` / `chapter` | `arc_01` / `chapter_01_01` |
| `quest_type` | Main Quest |
| `narrative_function` | World Building |
| `gameplay_function` | Pengenalan sistem progression dasar |
| `prerequisites` | **Reads:** `flag_dream_a01_01_seen == true` |
| `objectives` | Diterima resmi sebagai murid Tian Xu |
| `success_conditions` | Registrasi selesai |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Pemeriksa aptitude (lanjutan) |
| `locations` | `loc_tianxu_gate` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Dialog administratif standar |
| `branching_points` | Tidak ada |
| `consequences` | `state_murid_status = "registered"` |
| `world_state_changes` | **Writes:** `state_murid_status = "registered"` |
| `relationship_changes` / `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a01_c02_003` |
| `convergence_id` | N/A |

---

## `quest_a01_c02_003` — First Lesson

| Field | Value |
|---|---|
| `quest_id` | `quest_a01_c02_003` |
| `title` | First Lesson |
| `arc` / `chapter` | `arc_01` / `chapter_01_02` |
| `quest_type` | Main Quest |
| `narrative_function` | Character Development (introduces 4 found family candidates), Foreshadowing (familiar technique) |
| `gameplay_function` | Pengenalan mekanik cultivation dasar |
| `prerequisites` | **Reads:** `state_murid_status == "registered"` |
| `objectives` | Mengikuti pelajaran pertama; berinteraksi dengan calon anggota kelompok |
| `success_conditions` | Pelajaran selesai |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | `npc_lin_yue`, `npc_shen_luo`, `npc_mei_ruo`, `npc_gu_han` (semua first_appearance) |
| `locations` | Ruang latihan umum |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Interaksi individual opsional dengan tiap calon anggota — memengaruhi starting relationship value sebelum kelompok resmi terbentuk |
| `branching_points` | `branch_a01_c02_b01` (lihat di bawah) — COSMETIC, urutan/intensitas interaksi dengan tiap NPC tidak mengubah state signifikan, hanya starting relationship offset kecil |
| `consequences` | Teknik "terasa familiar" saat mencoba gerakan dasar |
| `world_state_changes` | **Writes:** `state_rel_lin_yue`, `state_rel_shen_luo`, `state_rel_mei_ruo`, `state_rel_gu_han` (masing-masing mulai dari 0, disesuaikan kecil berdasarkan interaksi opsional) |
| `relationship_changes` | Baseline dibentuk untuk keempat NPC |
| `faction_changes` | Tidak ada |
| `memory_triggers` | `memory_a01_m02` (technique familiarity, reliability rendah) |
| `next_quests` | `quest_a01_c03_004` |
| `convergence_id` | N/A |

### `branch_a01_c02_b01` — Urutan Interaksi Found Family
| Field | Value |
|---|---|
| `branch_id` | `branch_a01_c02_b01` |
| `parent_quest` | `quest_a01_c02_003` |
| `classification` | COSMETIC |
| `trigger` | Pemain memilih NPC mana yang diajak bicara lebih dulu |
| `player_choice` | Urutan interaksi (tidak eksklusif — pemain dapat bicara ke semua) |
| `choice_meaning` | Menunjukkan preferensi sosial awal pemain, tidak mengunci apa pun |
| `immediate_result` | Dialog flavor berbeda |
| `state_changes` | Offset kecil pada `state_rel_*` NPC yang diajak bicara lebih dulu (+1 relative ke lainnya) |
| `NPC_reactions` | Tidak signifikan |
| `relationship_changes` | Minor, dalam batas noise — tidak memengaruhi gating konten manapun |
| `faction_changes` | Tidak ada |
| `quest_changes` | Tidak ada |
| `future_effects` | Tidak ada — ditegaskan COSMETIC agar tidak disalahartikan sebagai major choice |
| `convergence_point` | N/A — tidak perlu convergence formal untuk cosmetic branch |

---

## `quest_a01_c03_004` — Pavilion Selection

| Field | Value |
|---|---|
| `quest_id` | `quest_a01_c03_004` |
| `title` | Pavilion Selection |
| `arc` / `chapter` | `arc_01` / `chapter_01_03` |
| `quest_type` | Main Quest |
| `narrative_function` | Character Development, Gameplay Progression, Setup untuk future payoff |
| `gameplay_function` | Menentukan curriculum/build path jangka panjang |
| `prerequisites` | **Reads:** `state_rel_lin_yue`, `state_rel_shen_luo`, `state_rel_mei_ruo`, `state_rel_gu_han` (baseline dari quest sebelumnya, tidak gating — hanya referensi dialog) |
| `objectives` | Mempelajari filosofi tiap pavilion; memilih satu |
| `success_conditions` | Pavilion dipilih |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Guru tiap pavilion (`[DESIGN GAP]` — roster Phase 9) |
| `locations` | `[DESIGN GAP]` — lokasi tiap pavilion, Phase 9 |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Eksplorasi filosofi tiap pavilion sebelum memilih (opsional tapi direkomendasikan) |
| `branching_points` | `branch_a01_c03_b01` — **MAJOR** |
| `consequences` | Curriculum permanen, guru permanen, beberapa dialogue Arc II-VII dimodifikasi |
| `world_state_changes` | **Writes:** `state_pavilion = <chosen>` (permanen, tidak dapat diubah — sesuai prinsip choice yang punya bobot nyata) |
| `relationship_changes` | Kelompok found family mulai solid berdasarkan kedekatan pavilion (NPC yang berada di pavilion sama/berdekatan dengan pilihan pemain mendapat modifier relationship kecil positif) |
| `faction_changes` | Tidak ada langsung, tapi `state_pavilion` akan menjadi modifier untuk faction relationship di Arc IV+ (`[DESIGN GAP]` — detail pemetaan pavilion↔faction akan diformalkan Phase 6) |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a01_c04_005` |
| `convergence_id` | N/A — pavilion TIDAK punya convergence karena ia adalah permanent state modifier, bukan branch yang "selesai" |

### `branch_a01_c03_b01` — Pilihan Pavilion
| Field | Value |
|---|---|
| `branch_id` | `branch_a01_c03_b01` |
| `parent_quest` | `quest_a01_c03_004` |
| `classification` | **MAJOR** |
| `trigger` | Pemain memilih satu dari roster pavilion (`[DESIGN GAP]` — jumlah dan nama pavilion) |
| `player_choice` | Filosofi cultivation mana yang dianut |
| `choice_meaning` | Cara hidup, bukan sekadar class — eksplisit MSB |
| `immediate_result` | `state_pavilion` di-set permanen |
| `state_changes` | Curriculum, guru, dan akses ke beberapa clue/dialogue termodifikasi sepanjang sisa campaign |
| `NPC_reactions` | Guru pavilion terpilih menjadi recurring NPC; guru pavilion lain menjadi occasional/ambient |
| `relationship_changes` | Modifier kecil terhadap found family berdasarkan kedekatan pavilion |
| `faction_changes` | Modifier tidak langsung ke faction relationship Arc IV+ |
| `quest_changes` | Beberapa optional quest di Arc II-IV hanya tersedia untuk pavilion tertentu (`[DESIGN GAP]` — akan diformalkan saat pavilion roster final) |
| `future_effects` | **MAJOR payoff:** kemungkinan tertentu pada ending (MSB eksplisit menyatakan pavilion memengaruhi "beberapa kemungkinan pada ending") — detail exact akan diformalkan di Phase 13 (Ending Matrix) |
| `convergence_point` | N/A |

**Catatan produksi:** branch ini adalah kandidat kuat untuk MAJOR choice pertama campaign yang payoff-nya bertahan hingga Phase 13. Karena roster pavilion sendiri adalah `[DESIGN GAP]`, detail *spesifik* future_effects (pavilion mana membuka apa) belum dapat difinalisasi — tapi *mekanisme* bahwa pavilion adalah permanent state modifier sudah ditetapkan di sini dan tidak akan berubah di fase berikutnya.

---

## `quest_a01_c04_005` — First Training & First Trial

| Field | Value |
|---|---|
| `quest_id` | `quest_a01_c04_005` |
| `title` | First Training & First Trial |
| `arc` / `chapter` | `arc_01` / `chapter_01_04` |
| `quest_type` | Main Quest |
| `narrative_function` | World Building, Mystery, Foreshadowing |
| `gameplay_function` | Combat/cooperation tutorial dengan kelompok penuh |
| `prerequisites` | **Reads:** `state_pavilion != null` |
| `objectives` | Mengumpulkan material; menyelidiki gangguan spiritual; menghadapi monster penjaga formation |
| `success_conditions` | Monster dihadapi (tidak harus dikalahkan secara konvensional — MSB menyiratkan monster "menjaga sesuatu", bukan musuh biasa; `[DESIGN GAP]` — mekanisme resolusi encounter, direkomendasikan non-lethal/investigative resolution agar konsisten dengan monster sebagai guardian bukan threat) |
| `failure_conditions` | `[DESIGN GAP]` — MSB tidak menyebut failure state eksplisit |
| `involved_npcs` | Keempat anggota found family (misi pertama sebagai kelompok penuh) |
| `locations` | Wilayah sekitar akademi dengan formation tua |
| `required_items` / `required_skills` | Skill dasar dari `quest_a01_c02_003` |
| `dialogue_events` | Diskusi kelompok saat menemukan monster tidak normal |
| `branching_points` | Tidak ada branch besar di sini — MSB menyiratkan ini linear |
| `consequences` | Menyentuh formation tua → memory muncul |
| `world_state_changes` | **Writes:** `flag_formation_touched = true` |
| `relationship_changes` | Found family bond meningkat (misi bersama pertama) |
| `faction_changes` | Tidak ada |
| `memory_triggers` | `memory_a01_m03` (formation hancur, fragment tanpa konteks penuh) |
| `next_quests` | `quest_a01_c04_006` |
| `convergence_id` | N/A |

---

## `quest_a01_c04_006` — Night Incident (Arc I Ending)

| Field | Value |
|---|---|
| `quest_id` | `quest_a01_c04_006` |
| `title` | Night Incident |
| `arc` / `chapter` | `arc_01` / `chapter_01_04` |
| `quest_type` | Main Quest |
| `narrative_function` | Mystery, Foreshadowing, Setup untuk future payoff |
| `gameplay_function` | Menutup Arc I, transisi ke Arc II |
| `prerequisites` | **Reads:** `flag_formation_touched == true` |
| `objectives` | Mengalami mimpi kedua; menemukan symbol di kamar |
| `success_conditions` | Symbol ditemukan (otomatis, bukan skill check) |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Tidak ada — momen soliter |
| `locations` | Kamar/asrama protagonis |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Mimpi: "Kalau kau kembali, jangan percaya sejarah." |
| `branching_points` | Tidak ada |
| `consequences` | `flag_memory_awareness = true`; item symbol diperoleh |
| `world_state_changes` | **Writes:** `flag_memory_awareness = true`, `item_ancient_symbol = acquired` |
| `relationship_changes` / `faction_changes` | Tidak ada |
| `memory_triggers` | `memory_a01_m04` (dream #2 + symbol) |
| `next_quests` | `quest_a02_c01_001` (Arc II dimulai) |
| `convergence_id` | `convergence_a01_c_end_01` |

---

# ARC II — THE FIRST TRIAL

## `quest_a02_c01_001` — Midterm

| Field | Value |
|---|---|
| `quest_id` | `quest_a02_c01_001` |
| `title` | Midterm |
| `arc` / `chapter` | `arc_02` / `chapter_02_01` |
| `quest_type` | Main Quest |
| `narrative_function` | Gameplay Progression, World Building (rivalitas antar-pavilion) |
| `gameplay_function` | Ujian solo/kelompok pertama pasca-onboarding |
| `prerequisites` | **Reads:** `flag_memory_awareness == true` |
| `objectives` | Mengikuti ujian midterm |
| `success_conditions` | Ujian selesai (tidak ada fail-state permanen — MSB tidak menyiratkan kegagalan akademik sebagai game over) |
| `failure_conditions` | `[DESIGN GAP]` |
| `involved_npcs` | Guru pengawas (`[DESIGN GAP]` nama) |
| `locations` | Arena ujian akademi |
| `required_items` / `required_skills` | Skill dari Arc I |
| `dialogue_events` | Standar |
| `branching_points` | Tidak ada |
| `consequences` | `state_reputation_academic` mulai terbentuk |
| `world_state_changes` | **Writes:** `state_reputation_academic = <initial value>` |
| `relationship_changes` / `faction_changes` | Tidak ada langsung |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a02_c01_002` |
| `convergence_id` | N/A |

---

## `quest_a02_c01_002` — Team Trial

| Field | Value |
|---|---|
| `quest_id` | `quest_a02_c01_002` |
| `title` | Team Trial |
| `arc` / `chapter` | `arc_02` / `chapter_02_01` |
| `quest_type` | Main Quest |
| `narrative_function` | Relationship, Gameplay Progression |
| `gameplay_function` | Kooperasi kelompok di bawah tekanan institusional |
| `prerequisites` | **Reads:** `state_reputation_academic >= <threshold>` **[DESIGN GAP — nilai threshold]** |
| `objectives` | Lulus ujian kelompok |
| `success_conditions` | Kelompok lulus |
| `failure_conditions` | `[DESIGN GAP]` |
| `involved_npcs` | Keempat found family, guru pengawas |
| `locations` | Arena ujian |
| `required_items` / `required_skills` | Tidak ada tambahan |
| `dialogue_events` | Interaksi rivalitas antar-pavilion opsional |
| `branching_points` | Tidak ada |
| `consequences` | Kelompok resmi diakui sebagai unit fungsional oleh institusi |
| `world_state_changes` | **Writes:** `flag_team_recognized = true` |
| `relationship_changes` | Found family bond meningkat signifikan |
| `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a02_c02_003` |
| `convergence_id` | N/A |

---

## `quest_a02_c02_003` — Outer Region

| Field | Value |
|---|---|
| `quest_id` | `quest_a02_c02_003` |
| `title` | Outer Region |
| `arc` / `chapter` | `arc_02` / `chapter_02_02` |
| `quest_type` | Main Quest |
| `narrative_function` | World Building, Setup |
| `gameplay_function` | Eksplorasi area baru, misi lapangan pertama |
| `prerequisites` | **Reads:** `flag_team_recognized == true` |
| `objectives` | Penugasan rutin ke outer region |
| `success_conditions` | Tiba di outer region |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Found family |
| `locations` | `loc_outer_region` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Standar |
| `branching_points` | Tidak ada |
| `consequences` | Membuka akses area baru |
| `world_state_changes` | **Writes:** `flag_outer_region_unlocked = true` |
| `relationship_changes` / `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a02_c02_004` |
| `convergence_id` | N/A |

---

## `quest_a02_c02_004` — Spiritual Disturbance

| Field | Value |
|---|---|
| `quest_id` | `quest_a02_c02_004` |
| `title` | Spiritual Disturbance |
| `arc` / `chapter` | `arc_02` / `chapter_02_02` |
| `quest_type` | Investigation Quest |
| `narrative_function` | Mystery, Foreshadowing (bibit Spiritual Collapse Arc V) |
| `gameplay_function` | Investigasi lingkungan |
| `prerequisites` | **Reads:** `flag_outer_region_unlocked == true` |
| `objectives` | Menyelidiki sumber gangguan spiritual |
| `success_conditions` | Sumber gangguan teridentifikasi sebagai terkait murid hilang |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Found family |
| `locations` | `loc_outer_region` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Diskusi kelompok tentang keanehan gangguan |
| `branching_points` | Tidak ada |
| `consequences` | Mengarah ke penemuan murid hilang |
| `world_state_changes` | **Writes:** `flag_disturbance_investigated = true` |
| `relationship_changes` / `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a02_c02_005` |
| `convergence_id` | N/A |

---

## `quest_a02_c02_005` — Missing Disciple

| Field | Value |
|---|---|
| `quest_id` | `quest_a02_c02_005` |
| `title` | Missing Disciple |
| `arc` / `chapter` | `arc_02` / `chapter_02_02` |
| `quest_type` | Investigation Quest |
| `narrative_function` | Mystery, Foreshadowing (Cycle Formation) |
| `gameplay_function` | Penemuan bukti kontradiktif terhadap narasi resmi |
| `prerequisites` | **Reads:** `flag_disturbance_investigated == true` |
| `objectives` | Menemukan tempat persembunyian murid hilang; menemukan catatan "Siklus dimulai lagi" |
| `success_conditions` | Catatan ditemukan |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Murid senior hilang (Quest NPC, `[DESIGN GAP]` nama) |
| `locations` | Tempat persembunyian tersembunyi di outer region |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Tidak ada dialog langsung (murid tidak ditemukan secara fisik di titik ini — hanya bukti) |
| `branching_points` | Tidak ada di quest ini — branch besar ada di quest berikutnya |
| `consequences` | Bukti kontradiktif terhadap pernyataan resmi institusi ("kemungkinan kabur") |
| `world_state_changes` | **Writes:** `flag_evidence_missing_disciple = true`, `item_note_cycle_begins_again = acquired` |
| `relationship_changes` / `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a02_c03_006` |
| `convergence_id` | N/A |

---

## `quest_a02_c03_006` — Accusation (First Major Choice)

| Field | Value |
|---|---|
| `quest_id` | `quest_a02_c03_006` |
| `title` | Accusation |
| `arc` / `chapter` | `arc_02` / `chapter_02_03` |
| `quest_type` | Branching Quest (decision point) |
| `narrative_function` | Relationship, Faction Conflict, Consequence, Setup untuk future payoff |
| `gameplay_function` | Major branching choice — menentukan jalur relationship/reputation jangka panjang |
| `prerequisites` | **Reads:** `flag_evidence_missing_disciple == true` |
| `objectives` | Memutuskan bagaimana merespons bukti yang ditemukan |
| `success_conditions` | Salah satu dari tiga pilihan diambil (tidak ada fail-state — semua pilihan valid) |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Guru (Obey path), tidak ada NPC baru (Investigate), pihak akademi/forum (Confront path) |
| `locations` | Bervariasi per branch |
| `required_items` / `required_skills` | `item_note_cycle_begins_again` |
| `dialogue_events` | Tiga jalur dialog berbeda tergantung pilihan |
| `branching_points` | `branch_a02_c03_b01` (Obey), `branch_a02_c03_b02` (Investigate), `branch_a02_c03_b03` (Confront) — ketiganya **MAJOR** |
| `consequences` | Lihat detail branch di bawah |
| `world_state_changes` | Lihat detail branch |
| `relationship_changes` | Lihat detail branch |
| `faction_changes` | Lihat detail branch |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a02_c04_007` (ketiga branch convergent) |
| `convergence_id` | `convergence_a02_c04_01` |

### `branch_a02_c03_b01` — Obey
| Field | Value |
|---|---|
| `branch_id` | `branch_a02_c03_b01` |
| `parent_quest` | `quest_a02_c03_006` |
| `classification` | **MAJOR** |
| `trigger` | Pemain memilih menyerahkan bukti kepada guru |
| `player_choice` | Obey |
| `choice_meaning` | Percaya pada sistem institusional untuk menangani kebenaran |
| `immediate_result` | Guru menerima laporan, memuji kejujuran kelompok |
| `state_changes` | `state_rel_master += <value>` |
| `NPC_reactions` | Guru menjadi lebih percaya terhadap kelompok |
| `relationship_changes` | `state_rel_master` naik signifikan |
| `faction_changes` | `state_rep_tianxu += <value>` (implisit — kepercayaan pada institusi; dibaca ulang sebagai input faction relationship Orthodox di Phase 6, konsisten dengan penggunaan `state_rep_tianxu` di branch Confront) |
| `quest_changes` | Akses investigasi mandiri berkurang (institusi mengambil alih); akses ke jalur resmi Forbidden Archive di Arc IV lebih mudah karena kepercayaan guru |
| `future_effects` | **MAJOR payoff Arc IV:** `state_rel_master` tinggi membuka dialogue khusus saat Forbidden Archive ditemukan — guru lebih terbuka berbagi informasi karena kepercayaan yang sudah terbangun |
| `convergence_point` | `convergence_a02_c04_01` |

### `branch_a02_c03_b02` — Investigate
| Field | Value |
|---|---|
| `branch_id` | `branch_a02_c03_b02` |
| `parent_quest` | `quest_a02_c03_006` |
| `classification` | **MAJOR** |
| `trigger` | Pemain memilih menyembunyikan sebagian bukti dan menyelidiki sendiri |
| `player_choice` | Investigate |
| `choice_meaning` | Tidak sepenuhnya percaya institusi, tapi belum siap konfrontasi terbuka |
| `immediate_result` | Tidak ada reaksi NPC langsung (tindakan tersembunyi) |
| `state_changes` | `flag_archive_suspicious = true` (mengikuti MSB §43 secara literal) |
| `NPC_reactions` | Tidak ada reaksi langsung — efeknya laten |
| `relationship_changes` | Tidak ada perubahan signifikan jangka pendek |
| `faction_changes` | Tidak ada langsung |
| `quest_changes` | Membuka jalur investigasi mandiri tambahan (optional quest tersedia untuk menelusuri lebih jauh sebelum Arc IV) |
| `future_effects` | **MAJOR payoff Arc IV:** `flag_archive_suspicious == true` membuka dialogue berbeda saat Forbidden Archive ditemukan (MSB eksplisit menyatakan ini di §43) — akses lebih cepat ke Version II tanpa perlu melalui jalur resmi |
| `convergence_point` | `convergence_a02_c04_01` |

### `branch_a02_c03_b03` — Confront
| Field | Value |
|---|---|
| `branch_id` | `branch_a02_c03_b03` |
| `parent_quest` | `quest_a02_c03_006` |
| `classification` | **MAJOR** |
| `trigger` | Pemain memilih menuduh pihak akademi menyembunyikan sesuatu secara terbuka |
| `player_choice` | Confront |
| `choice_meaning` | Konfrontasi langsung, menerima risiko sosial demi kebenaran cepat |
| `immediate_result` | Reaksi negatif dari sebagian pihak akademi; sebagian murid lain mulai memperhatikan kelompok |
| `state_changes` | `state_rep_tianxu -= <value>` (mengikuti MSB §43 secara literal) |
| `NPC_reactions` | Guru menjadi waspada; sebagian murid mulai bersimpati (potensi bibit relationship dengan faction Liberation/Reformists di Arc IV+) |
| `relationship_changes` | `state_rel_master` turun; kemungkinan relationship baru dengan NPC yang bersimpati (`[DESIGN GAP]` detail) |
| `faction_changes` | `state_rep_tianxu` (turun, sama dengan world_state_changes di atas — reputasi umum institusi, dibaca ulang sebagai modifier faction Orthodox di Phase 6); `state_rep_liberation` atau `state_rep_reformists` mendapat modifier positif kecil (bibit awal — akan diformalkan penuh Phase 6) |
| `quest_changes` | Beberapa optional quest "jalur resmi" tertutup; jalur alternatif via simpatisan terbuka |
| `future_effects` | **MAJOR payoff Arc IV-V:** reputasi rendah dengan Orthodox membuat akses Forbidden Archive lebih sulit tapi membuka jalur alternatif lewat faction yang lebih simpatik terhadap kebenaran |
| `convergence_point` | `convergence_a02_c04_01` |

---

## `quest_a02_c04_007` — Hidden Cave

| Field | Value |
|---|---|
| `quest_id` | `quest_a02_c04_007` |
| `title` | Hidden Cave |
| `arc` / `chapter` | `arc_02` / `chapter_02_04` |
| `quest_type` | Main Quest (Convergence) |
| `narrative_function` | Mystery, Convergence |
| `gameplay_function` | Titik temu ketiga branch — dungeon/exploration segment |
| `prerequisites` | **Reads:** salah satu dari `state_rel_master`, `flag_archive_suspicious`, atau `state_rep_tianxu` sudah ter-set (menandakan branch sebelumnya sudah diselesaikan — bukan gating eksklusif, ketiganya menuju quest yang sama) |
| `objectives` | Menemukan gua tersembunyi yang mengarah ke artefak |
| `success_conditions` | Gua ditemukan dan dieksplorasi |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Found family |
| `locations` | `loc_hidden_cave` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Dialog kelompok bervariasi tergantung branch mana yang diambil (state-aware dialogue — diformalkan Phase 8) |
| `branching_points` | Tidak ada branch baru — ini adalah convergence execution |
| `consequences` | Membuka akses ke artefak |
| `world_state_changes` | **Writes:** `flag_hidden_cave_explored = true` |
| `relationship_changes` / `faction_changes` | Tidak ada baru — state dari branch sebelumnya tetap dipertahankan (prinsip convergence wajib) |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a02_c04_008` |
| `convergence_id` | `convergence_a02_c04_01` |

---

## `quest_a02_c04_008` — First Artifact

| Field | Value |
|---|---|
| `quest_id` | `quest_a02_c04_008` |
| `title` | First Artifact |
| `arc` / `chapter` | `arc_02` / `chapter_02_04` |
| `quest_type` | Memory Quest |
| `narrative_function` | Mystery, Revelation (parsial), Foreshadowing |
| `gameplay_function` | Trigger memory system pertama kali secara naratif signifikan |
| `prerequisites` | **Reads:** `flag_hidden_cave_explored == true` |
| `objectives` | Menyentuh artefak; mengalami memory Lin Yue versi tua |
| `success_conditions` | Memory selesai dialami |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | `npc_lin_yue` (dalam memory, bukan dunia nyata) |
| `locations` | `loc_hidden_cave` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Memory: "Kalau kau melakukan ini, kau tidak akan kembali." |
| `branching_points` | Tidak ada |
| `consequences` | `item_artifact_01 = acquired`; memory tersimpan |
| `world_state_changes` | **Writes:** `item_artifact_01 = acquired`, `flag_memory_lin_yue_elder_seen = true` |
| `relationship_changes` | Tidak langsung — tapi ini mulai membangun *dramatic irony* untuk `npc_lin_yue` di dunia nyata (pemain tahu sesuatu tentang masa depan Lin Yue yang Lin Yue sendiri di masa kini belum tentu tahu) |
| `faction_changes` | Tidak ada |
| `memory_triggers` | `memory_a02_m01` (Lin Yue elder, reliability sedang — jelas tapi tanpa konteks) |
| `next_quests` | `quest_a02_c04_009` |
| `convergence_id` | N/A |

---

## `quest_a02_c04_009` — Return & Trial Conclusion (Arc II Ending)

| Field | Value |
|---|---|
| `quest_id` | `quest_a02_c04_009` |
| `title` | Return & Trial Conclusion |
| `arc` / `chapter` | `arc_02` / `chapter_02_04` |
| `quest_type` | Main Quest |
| `narrative_function` | Consequence, Setup untuk future payoff |
| `gameplay_function` | Menutup Arc II, transisi ke Memory Investigation System penuh (Arc III) |
| `prerequisites` | **Reads:** `flag_memory_lin_yue_elder_seen == true` |
| `objectives` | Kembali ke akademi; laporan trial selesai |
| `success_conditions` | Arc II ditutup |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Found family, guru (reaksi bervariasi tergantung branch Chapter 2.3) |
| `locations` | Akademi utama |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Dialog penutup, state-aware terhadap branch sebelumnya |
| `branching_points` | Tidak ada |
| `consequences` | Artefak menjadi trigger sistematis untuk Arc III |
| `world_state_changes` | **Writes:** `flag_arc2_complete = true` |
| `relationship_changes` / `faction_changes` | Tidak ada baru |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a03_c01_001` (Arc III dimulai) |
| `convergence_id` | N/A |

---

## Ringkasan State Baru yang Diperkenalkan Arc I-II

Katalog lengkap akan diformalkan di Phase 15 (Story State Catalog). Daftar berikut adalah working list untuk memastikan konsistensi penamaan di file Quest Graph lanjutan (Arc III-VII):

| State | Tipe | Ditulis oleh | Dibaca oleh |
|---|---|---|---|
| `flag_dream_a01_01_seen` | boolean | `quest_a01_c01_001` | `quest_a01_c01_002` |
| `state_murid_status` | enum | `quest_a01_c01_002` | `quest_a01_c02_003` |
| `state_rel_lin_yue/shen_luo/mei_ruo/gu_han` | integer | `quest_a01_c02_003`, banyak quest lanjutan | Banyak quest & dialogue lanjutan |
| `state_pavilion` | enum (permanen) | `quest_a01_c03_004` | Banyak quest, dialogue, ending Phase 13 |
| `flag_formation_touched` | boolean | `quest_a01_c04_005` | `quest_a01_c04_006` |
| `flag_memory_awareness` | boolean | `quest_a01_c04_006` | `quest_a02_c01_001`, banyak dialogue |
| `item_ancient_symbol` | item state | `quest_a01_c04_006` | Arc III (Mo Chen recognition) |
| `state_reputation_academic` | integer | `quest_a02_c01_001` | `quest_a02_c01_002` |
| `flag_team_recognized` | boolean | `quest_a02_c01_002` | `quest_a02_c02_003` |
| `flag_outer_region_unlocked` | boolean | `quest_a02_c02_003` | `quest_a02_c02_004` |
| `flag_disturbance_investigated` | boolean | `quest_a02_c02_004` | `quest_a02_c02_005` |
| `flag_evidence_missing_disciple` | boolean | `quest_a02_c02_005` | `quest_a02_c03_006` |
| `item_note_cycle_begins_again` | item state | `quest_a02_c02_005` | `quest_a02_c03_006`, foreshadowing Arc VI |
| `state_rel_master` | integer | `branch_a02_c03_b01` | Arc IV dialogue |
| `flag_archive_suspicious` | boolean | `branch_a02_c03_b02` | Arc IV dialogue (eksplisit MSB §43) |
| `state_rep_tianxu` | integer | `branch_a02_c03_b03` | Arc IV+ dialogue, faction relationship |
| `flag_memory_lin_yue_elder_seen` | boolean | `quest_a02_c04_008` | `quest_a02_c04_009` |
| `flag_arc2_complete` | boolean | `quest_a02_c04_009` | `quest_a03_c01_001` |

**Catatan konsistensi:** `state_rel_master` dan `state_rep_tianxu` adalah dua state berbeda (relationship personal dengan satu guru vs reputasi dengan institusi secara umum) — dipisahkan sengaja karena MSB §43 menyebutkan keduanya sebagai efek independen dari branch berbeda (Obey → `relationship_master +`; Confront → `rep_tianxu -`).

**Koreksi konsistensi (self-audit):** draft awal fase ini sempat menulis `state_rep_tianxu_orthodox` sebagai state terpisah dari `state_rep_tianxu` di branch Confront — ini digabungkan menjadi satu state (`state_rep_tianxu`) karena keduanya merujuk konsep yang sama (reputasi umum dengan institusi Tian Xu). `state_rep_tianxu` akan dibaca ulang sebagai salah satu input untuk faction relationship Orthodox secara spesifik di Phase 6 (Faction Bible), bukan diduplikasi sebagai state baru.

---

**File berikutnya:** `03b-quest-graph-arc3-7.md` — melanjutkan Quest Graph untuk Arc III-VII, termasuk mengisi dua `[DESIGN GAP]` Major Choice yang tercatat di Phase 3 (Chapter 3.4, dan ongoing-state Arc IV).
