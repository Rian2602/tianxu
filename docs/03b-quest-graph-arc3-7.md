# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 03b. Quest Graph — Arc III-VII (Lanjutan)

**Status:** DRAFT — Phase 4 of 18 (lanjutan)
**Depends on:** `00-narrative-architecture.md`, `01-arc-overview.md`, `02-chapter-breakdown.md`, `03-quest-graph-arc1-2.md`

---

# ARC III — ECHOES OF ANOTHER SELF

## `quest_a03_c01_001` — The Room That Isn't on the Map

| Field | Value |
|---|---|
| `quest_id` | `quest_a03_c01_001` |
| `title` | The Room That Isn't on the Map |
| `arc` / `chapter` | `arc_03` / `chapter_03_01` |
| `quest_type` | Investigation Quest |
| `narrative_function` | Mystery, World Building, Foreshadowing |
| `gameplay_function` | Pengenalan penuh Memory Investigation System sebagai mekanik eksplorasi |
| `prerequisites` | **Reads:** `flag_arc2_complete == true`, `item_artifact_01 == acquired` |
| `objectives` | Menemukan ruangan tersembunyi; menganalisis mural bersama Mei Ruo |
| `success_conditions` | Mural dianalisis, kerusakan disengaja teridentifikasi |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | `npc_mei_ruo` |
| `locations` | `loc_hidden_room_mural` |
| `required_items` / `required_skills` | `item_artifact_01` (sebagai trigger) |
| `dialogue_events` | Mei Ruo: "Seseorang sengaja menghapusnya." |
| `branching_points` | Tidak ada |
| `consequences` | Mystery #4 dibuka konkret |
| `world_state_changes` | **Writes:** `flag_mural_analyzed = true` |
| `relationship_changes` | `state_rel_mei_ruo += <value>` (kolaborasi investigatif) |
| `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada memory langsung — ini adalah investigation quest, bukan memory quest |
| `next_quests` | `quest_a03_c02_002` |
| `convergence_id` | N/A |

---

## `quest_a03_c02_002` — The Stranger Who Knows My Name

| Field | Value |
|---|---|
| `quest_id` | `quest_a03_c02_002` |
| `title` | The Stranger Who Knows My Name |
| `arc` / `chapter` | `arc_03` / `chapter_03_02` |
| `quest_type` | Main Quest |
| `narrative_function` | Mystery, Character Development (Mo Chen intro), Foreshadowing |
| `gameplay_function` | Cutscene-driven encounter, singkat by design |
| `prerequisites` | **Reads:** `flag_mural_analyzed == true` |
| `objectives` | Bertemu Mo Chen |
| `note_item_recognition` | `item_ancient_symbol` (diperoleh Arc I Chapter 1.4) tidak menggerbang quest ini, tapi jika dimiliki, Mo Chen secara eksplisit mengenali symbol tersebut dalam dialog sebagai konfirmasi visual tambahan sebelum ia mengucapkan nama "Jiang Yan" — memberi pemain yang memerhatikan detail sejak Arc I sebuah momen pengenalan yang terasa earned, bukan sekadar exposisi sepihak dari NPC |
| `success_conditions` | Pertemuan terjadi (tidak dapat dihindari — MSB menyiratkan ini peristiwa wajib) |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | `npc_mo_chen` (first_appearance) |
| `locations` | `[DESIGN GAP]` — lokasi pertemuan Mo Chen |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Mo Chen memanggil protagonis "Jiang Yan"; kemudian menghilang |
| `branching_points` | Tidak ada — MSB menyiratkan pertemuan ini di luar kendali pemain (Mo Chen "kemudian menghilang" tanpa transisi dialog normal) |
| `consequences` | Nama "Jiang Yan" diketahui pemain untuk pertama kali |
| `world_state_changes` | **Writes:** `flag_name_jiang_yan_known = true`, `flag_mo_chen_met = true` |
| `relationship_changes` / `faction_changes` | Tidak ada — Mo Chen menghilang sebelum relationship dapat terbentuk |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a03_c03_003` |
| `convergence_id` | N/A |

---

## `quest_a03_c03_003` — Deceased

| Field | Value |
|---|---|
| `quest_id` | `quest_a03_c03_003` |
| `title` | Deceased |
| `arc` / `chapter` | `arc_03` / `chapter_03_03` |
| `quest_type` | Investigation Quest |
| `narrative_function` | Mystery, Revelation |
| `gameplay_function` | Pencarian dokumen di arsip publik akademi |
| `prerequisites` | **Reads:** `flag_name_jiang_yan_known == true` |
| `objectives` | Mencari dan memverifikasi dokumen dengan nama Jiang Yan |
| `success_conditions` | Dokumen ditemukan, status "Deceased" dikonfirmasi |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Arsiparis (Ambient NPC, `[DESIGN GAP]`) |
| `locations` | Arsip publik akademi (berbeda dari Forbidden Archive Arc IV) |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Tidak ada dialog signifikan — momen membaca dokumen |
| `branching_points` | Tidak ada |
| `consequences` | Konfirmasi literal identitas dan kematian Jiang Yan |
| `world_state_changes` | **Writes:** `flag_jiang_yan_deceased_confirmed = true` |
| `relationship_changes` / `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a03_c04_004` |
| `convergence_id` | N/A |

---

## `quest_a03_c04_004` — What I Choose to Believe (Major Choice)

**Catatan produksi:** quest ini mengisi `[DESIGN GAP]` Major Choice Arc III yang dicatat di Phase 2 dan Phase 3. Struktur choice di bawah adalah desain baru yang konsisten dengan tema Identity, **bukan** turunan langsung dari peristiwa spesifik di MSB — ditandai eksplisit.

| Field | Value |
|---|---|
| `quest_id` | `quest_a03_c04_004` |
| `title` | What I Choose to Believe |
| `arc` / `chapter` | `arc_03` / `chapter_03_04` |
| `quest_type` | Branching Quest (decision point) — **`[DESIGN GAP — quest baru, bukan dari MSB langsung]`** |
| `narrative_function` | Character Development, Relationship |
| `gameplay_function` | Major choice kedua campaign, berbasis sikap (bukan aksi fisik) |
| `prerequisites` | **Reads:** `flag_jiang_yan_deceased_confirmed == true` |
| `objectives` | Menentukan sikap terhadap identitas yang terungkap; opsional memberi tahu found family |
| `success_conditions` | Salah satu dari tiga stance dipilih |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Keempat found family (reaksi mereka adalah konten inti quest ini) |
| `locations` | Ruang privat kelompok |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Percakapan individual opsional dengan tiap anggota found family |
| `branching_points` | `branch_a03_c04_b01` (Deny), `branch_a03_c04_b02` (Accept Cautious), `branch_a03_c04_b03` (Seek Truth) — ketiganya **MEANINGFUL**, bukan MAJOR (karena payoff-nya bersifat modifier dialogue berkelanjutan, bukan satu payoff besar di titik tunggal — meski dampak kumulatifnya signifikan hingga Arc VII) |
| `consequences` | Lihat detail branch |
| `world_state_changes` | Lihat detail branch |
| `relationship_changes` | Lihat detail branch |
| `faction_changes` | Tidak ada langsung |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a03_c05_005` |
| `convergence_id` | `convergence_a03_c05_01` |

### `branch_a03_c04_b01` — Deny
| Field | Value |
|---|---|
| `branch_id` | `branch_a03_c04_b01` |
| `parent_quest` | `quest_a03_c04_004` |
| `classification` | MEANINGFUL (cumulative MAJOR melalui Arc VII) |
| `trigger` | Pemain memilih menolak bahwa dirinya adalah Jiang Yan |
| `player_choice` | Deny |
| `choice_meaning` | Menjaga jarak dari kehidupan pertama sebagai mekanisme pertahanan psikologis |
| `immediate_result` | Found family reaksi bervariasi — sebagian mendukung penolakan ini, sebagian (terutama Mei Ruo, sang truth-seeker) sedikit khawatir |
| `state_changes` | `state_identity_stance = "deny"` |
| `NPC_reactions` | Gu Han (skeptis institusi) cenderung netral/mendukung; Mei Ruo (truth seeker) sedikit frustrasi tapi tidak memaksa |
| `relationship_changes` | Minor variasi antar-anggota found family |
| `faction_changes` | Tidak ada |
| `quest_changes` | Beberapa dialogue investigatif opsional di Arc IV-V menjadi lebih defensif/tertutup |
| `future_effects` | **Payoff Arc VII:** state ini menjadi salah satu modifier dialogue di Final Confrontation Chapter 7.2 — momen "Aku bukan kau" mendapat lapisan makna tambahan jika protagonis sebelumnya secara konsisten menolak identitas ini, lalu akhirnya mengucapkannya sebagai penegasan yang telah diperjuangkan, bukan penolakan pertama kali |
| `convergence_point` | `convergence_a03_c05_01` |

### `branch_a03_c04_b02` — Accept Cautious
| Field | Value |
|---|---|
| `branch_id` | `branch_a03_c04_b02` |
| `parent_quest` | `quest_a03_c04_004` |
| `classification` | MEANINGFUL (cumulative MAJOR melalui Arc VII) |
| `trigger` | Pemain memilih menerima identitas tapi menjaga jarak emosional |
| `player_choice` | Accept Cautious |
| `choice_meaning` | Pragmatisme — menerima fakta tanpa langsung mengizinkannya mendefinisikan diri |
| `immediate_result` | Found family reaksi paling netral dari ketiga opsi |
| `state_changes` | `state_identity_stance = "accept_cautious"` |
| `NPC_reactions` | Reaksi seimbang dari semua anggota |
| `relationship_changes` | Perubahan minimal, paling "aman" secara relationship |
| `faction_changes` | Tidak ada |
| `quest_changes` | Akses seimbang ke dialogue investigatif Arc IV-V |
| `future_effects` | **Payoff Arc VII:** modifier paling netral di Final Confrontation — "Aku bukan kau" terasa sebagai kesimpulan logis dari sikap hati-hati yang konsisten, bukan pembalikan dramatis |
| `convergence_point` | `convergence_a03_c05_01` |

### `branch_a03_c04_b03` — Seek Truth
| Field | Value |
|---|---|
| `branch_id` | `branch_a03_c04_b03` |
| `parent_quest` | `quest_a03_c04_004` |
| `classification` | MEANINGFUL (cumulative MAJOR melalui Arc VII) |
| `trigger` | Pemain memilih aktif mencari kebenaran secara netral emosional |
| `player_choice` | Seek Truth |
| `choice_meaning` | Prioritas pada pemahaman, menunda penilaian diri sampai bukti cukup |
| `immediate_result` | Mei Ruo (truth seeker) paling mendukung; hubungan investigatif dengannya menguat |
| `state_changes` | `state_identity_stance = "seek_truth"` |
| `NPC_reactions` | Mei Ruo relationship menguat signifikan; Gu Han netral; Lin Yue mendukung tapi khawatir soal kesehatan emosional protagonis |
| `relationship_changes` | `state_rel_mei_ruo += <value>` (lebih besar dari branch lain) |
| `faction_changes` | Tidak ada |
| `quest_changes` | Membuka optional investigation quest tambahan di Arc IV-V terkait detail historis Jiang Yan |
| `future_effects` | **Payoff Arc VII:** stance ini memberi protagonis akses informasi paling lengkap sebelum Final Confrontation, berpotensi menjadi salah satu jalur menuju kondisi Hidden Resolution (Phase 13) karena prasyarat "menyelesaikan investigasi kehidupan pertama" lebih mudah terpenuhi |
| `convergence_point` | `convergence_a03_c05_01` |

---

## `quest_a03_c05_005` — The Gate I Opened (Arc III Ending)

| Field | Value |
|---|---|
| `quest_id` | `quest_a03_c05_005` |
| `title` | The Gate I Opened |
| `arc` / `chapter` | `arc_03` / `chapter_03_05` |
| `quest_type` | Memory Quest (Convergence) |
| `narrative_function` | Mystery, Revelation (parsial/misleading), Foreshadowing |
| `gameplay_function` | Menutup Arc III dengan memory besar yang sengaja ambigu |
| `prerequisites` | **Reads:** `state_identity_stance != null` |
| `objectives` | Mengalami memory gerbang lengkap |
| `success_conditions` | Memory selesai |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Tidak ada — momen soliter |
| `locations` | `[DESIGN GAP]` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Memory: "Kalau dunia harus membenciku, biarkan." |
| `branching_points` | Tidak ada — ini adalah convergence execution dari `quest_a03_c04_004` |
| `consequences` | **PENTING:** kesimpulan "protagonis mungkin penyebab tragedi" ditulis sebagai `belief_state`, BUKAN sebagai fact-flag — untuk memastikan Phase 7 (Memory Bible) dapat mengontraskannya di Arc IV/VI tanpa terasa retcon |
| `world_state_changes` | **Writes:** `flag_memory_gate_a03_seen = true`, `belief_protagonist_may_be_cause = true` (ditandai eksplisit sebagai player belief, bukan world fact — lihat Memory Reliability di Phase 7) |
| `relationship_changes` | Tidak ada baru — state dari `state_identity_stance` dipertahankan (convergence tidak menghapus) |
| `faction_changes` | Tidak ada |
| `memory_triggers` | `memory_a03_m01` (gate memory, reliability RENDAH, misleading_elements tinggi — akan diformalkan detail Phase 7) |
| `next_quests` | `quest_a04_c01_001` (Arc IV dimulai) |
| `convergence_id` | `convergence_a03_c05_01` |

---

# ARC IV — THE FALSE HISTORY

## `quest_a04_c01_001` — The Archive Beneath

| Field | Value |
|---|---|
| `quest_id` | `quest_a04_c01_001` |
| `title` | The Archive Beneath |
| `arc` / `chapter` | `arc_04` / `chapter_04_01` |
| `quest_type` | Investigation Quest |
| `narrative_function` | Mystery, World Building |
| `gameplay_function` | Akses ke Forbidden Archive — gating berbeda tergantung state dari Arc II |
| `prerequisites` | **Reads:** `flag_memory_gate_a03_seen == true` DAN (`flag_archive_suspicious == true` ATAU `state_rel_master >= <threshold>` ATAU `state_rep_tianxu <= <threshold>`) — tiga jalur akses berbeda sesuai branch Arc II Chapter 2.3, tidak saling eksklusif |
| `objectives` | Mengakses Forbidden Archive; membandingkan Version I dan Version II |
| `success_conditions` | Kontradiksi antara Version I/II terdokumentasi |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | `npc_mei_ruo` |
| `locations` | `loc_forbidden_archive` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Dialog akses bervariasi tergantung jalur (Obey → dibantu guru; Investigate → akses mandiri lebih cepat; Confront → jalur alternatif via simpatisan) |
| `branching_points` | Tidak ada branch baru — jalur akses adalah *state-conditional content availability*, bukan pilihan baru |
| `consequences` | Version I dan II dibandingkan |
| `world_state_changes` | **Writes:** `flag_history_v1_v2_compared = true` |
| `relationship_changes` | `state_rel_mei_ruo += <value>` |
| `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a04_c02_002` |
| `convergence_id` | N/A |

---

## `quest_a04_c02_002` — What We Sealed

| Field | Value |
|---|---|
| `quest_id` | `quest_a04_c02_002` |
| `title` | What We Sealed |
| `arc` / `chapter` | `arc_04` / `chapter_04_02` |
| `quest_type` | Investigation Quest |
| `narrative_function` | Mystery, Revelation |
| `gameplay_function` | Revelation chapter — akses ke bagian terdalam Forbidden Archive |
| `prerequisites` | **Reads:** `flag_history_v1_v2_compared == true` |
| `objectives` | Menemukan Version III (catatan pribadi pendiri) |
| `success_conditions` | Version III dibaca lengkap |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | `npc_mei_ruo` |
| `locations` | `loc_forbidden_archive` (bagian terdalam) |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Kutipan Version III: "Yang kami segel bukan musuh. Kami menyegel akibat dari kesalahan kami sendiri." |
| `branching_points` | Tidak ada |
| `consequences` | **Rekontekstualisasi besar:** kesimpulan `belief_protagonist_may_be_cause` dari Arc III mulai terkontraskan (bukan langsung dibatalkan — dikontraskan secara bertahap, payoff penuh baru di Arc VI) |
| `world_state_changes` | **Writes:** `flag_version_iii_read = true`, `flag_origin_cultivation_known_partial = true` |
| `relationship_changes` | `state_rel_mei_ruo += <value>` |
| `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a04_c03_003` |
| `convergence_id` | N/A |

---

## `quest_a04_c03_003` — The Man Who Chose Fear

| Field | Value |
|---|---|
| `quest_id` | `quest_a04_c03_003` |
| `title` | The Man Who Chose Fear |
| `arc` / `chapter` | `arc_04` / `chapter_04_03` |
| `quest_type` | Character Quest |
| `narrative_function` | Character Development, Faction Conflict (ideologis) |
| `gameplay_function` | Dialog-heavy encounter dengan Grandmaster |
| `prerequisites` | **Reads:** `flag_origin_cultivation_known_partial == true` |
| `objectives` | Konfrontasi ideologis dengan Grandmaster |
| `success_conditions` | Percakapan selesai (tidak ada win/lose state — ini murni dialog) |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | `npc_grandmaster` (first meaningful appearance) |
| `locations` | `loc_grandmaster_chamber` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Grandmaster mengakui sistem tidak sempurna; menjelaskan taruhan jika sumber dihentikan |
| `branching_points` | Tidak ada branch mayor — tapi dialog opsional tambahan tersedia jika `state_rel_grandmaster` (baru, mulai dari 0) cukup tinggi setelah percakapan ini, membuka baris "Aku juga pernah menginginkannya..." — **ditandai sebagai SETUP untuk payoff penuh di Arc VI, bukan payoff itu sendiri** |
| `consequences` | Relationship dasar dengan Grandmaster terbentuk sebagai kompleks, bukan hostile |
| `world_state_changes` | **Writes:** `flag_grandmaster_met = true` (dibaca oleh Phase 9 NPC recurring-appearance logic dan sebagai prerequisite dialog opsional Grandmaster di Arc VI Chapter 6.4), `flag_stakes_of_stopping_source_known = true` |
| `relationship_changes` | `state_rel_grandmaster = <initial value>` (state baru, first introduced di sini) |
| `faction_changes` | Tidak ada langsung — tapi ini menjadi dasar untuk faction Orthodox relationship di Phase 6 |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a04_c04_004` |
| `convergence_id` | N/A |

---

## `quest_a04_c04_004` — What Tian Xu Feeds On (Arc IV Ending)

| Field | Value |
|---|---|
| `quest_id` | `quest_a04_c04_004` |
| `title` | What Tian Xu Feeds On |
| `arc` / `chapter` | `arc_04` / `chapter_04_04` |
| `quest_type` | Main Quest |
| `narrative_function` | Mystery, Revelation, World Building |
| `gameplay_function` | Discovery chapter, menutup Arc IV |
| `prerequisites` | **Reads:** `flag_stakes_of_stopping_source_known == true` |
| `objectives` | Menemukan ruang terdalam Tian Xu; melihat formation raksasa |
| `success_conditions` | Formation ditemukan dan dipahami skalanya |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Tidak ada — discovery chapter soliter/kelompok tanpa dialog NPC baru |
| `locations` | `loc_tianxu_deepest_chamber` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Reaksi kelompok terhadap penemuan (jika found family hadir — `[DESIGN GAP]` apakah found family menemani di titik ini, direkomendasikan YA untuk konsistensi dengan found family sebagai unit eksplorasi utama) |
| `branching_points` | Tidak ada |
| `consequences` | Mystery #5 terjawab penuh; horor sistemik dipahami |
| `world_state_changes` | **Writes:** `flag_tianxu_feeds_segel_known = true`, `flag_arc4_complete = true` |
| `relationship_changes` / `faction_changes` | Tidak ada baru |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a05_c01_001` (Arc V dimulai) |
| `convergence_id` | N/A |

**Ongoing State — Menyebarkan Kebenaran (mengisi `[DESIGN GAP]` Major Choice Arc IV dari Phase 3):**

Alih-alih satu quest keputusan, saya formalkan sebagai state opsional yang dapat diaktifkan pemain kapan saja sejak `flag_version_iii_read == true` hingga akhir Arc V:

| Field | Value |
|---|---|
| `state_id` | `state_truth_spread_level` |
| `type` | Integer (0 = tidak disebarkan sama sekali, meningkat setiap kali pemain memilih opsi dialog untuk membagikan sebagian Version I/II/III ke murid lain) |
| `modified_by` | Dialog opsional tersebar di Arc IV-V (bukan satu quest terpusat) |
| `read_by` | Faction reaction di Phase 6; beberapa dialogue Arc V-VI (reaksi murid lain terhadap kebenaran yang beredar) |
| `purpose` | Memberi pemain agency berkelanjutan atas prinsip "apakah menyebarkan kebenaran" tanpa memaksakan satu titik keputusan tunggal yang tidak didukung MSB secara eksplisit |
| `persistence` | Permanen, akumulatif |
| `affected_content` | Faction reputation drift (Reformists/Liberation bereaksi positif terhadap `state_truth_spread_level` tinggi; Orthodox bereaksi negatif) — detail penuh Phase 6 |

**Ditandai eksplisit:** mekanisme ini adalah rekomendasi desain untuk mengisi gap, bukan spesifikasi MSB langsung.

---

# ARC V — THE WORLD THAT REMEMBERS

## `quest_a05_c01_001` — The World Remembers Too

| Field | Value |
|---|---|
| `quest_id` | `quest_a05_c01_001` |
| `title` | The World Remembers Too |
| `arc` / `chapter` | `arc_05` / `chapter_05_01` |
| `quest_type` | Main Quest / World Event trigger |
| `narrative_function` | World Building, Consequence |
| `gameplay_function` | Pengenalan Spiritual Collapse sebagai world event sistem |
| `prerequisites` | **Reads:** `flag_arc4_complete == true` |
| `objectives` | Menyaksikan/menyelidiki wilayah pertama yang terdampak |
| `success_conditions` | Minimal satu wilayah terkonfirmasi terdampak |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Found family (konfigurasi masih utuh di titik ini — perpecahan baru di Chapter 5.3) |
| `locations` | `[DESIGN GAP]` — multiple affected regions |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Reaksi found family terhadap skala krisis (awal divergensi sikap, belum eksplisit menjadi konflik) |
| `branching_points` | Tidak ada |
| `consequences` | Memicu `world_event_a05_spiritual_collapse` |
| `world_state_changes` | **Writes:** `world_event_a05_spiritual_collapse = active` |
| `relationship_changes` / `faction_changes` | Tidak ada baru |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a05_c02_002` |
| `convergence_id` | N/A |

---

## `quest_a05_c02_002` — Mountain Gate, Again

| Field | Value |
|---|---|
| `quest_id` | `quest_a05_c02_002` |
| `title` | Mountain Gate, Again |
| `arc` / `chapter` | `arc_05` / `chapter_05_02` |
| `quest_type` | Main Quest (Repeating Event) |
| `narrative_function` | Mystery, Consequence, Revelation (mekanik, bukan informasional) |
| `gameplay_function` | Gameplay choice dengan stake nyata (bukan dialog choice) — MSB eksplisit menyatakan hasil bergantung pada aksi pemain ("Jika berhasil... Jika gagal...") |
| `prerequisites` | **Reads:** `world_event_a05_spiritual_collapse == active` |
| `objectives` | Merespons Mountain Gate Incident secara real-time |
| `success_conditions` | `flag_mountain_gate_changed = true` (sejarah berubah) |
| `failure_conditions` | `flag_mountain_gate_repeated = true` (tragedi terulang) — **PENTING:** ini bukan "game over" fail state, melainkan hasil naratif valid yang membawa konsekuensi berbeda, bukan menghentikan progress |
| `involved_npcs` | NPC yang terancam di lokasi (`[DESIGN GAP]` — direkomendasikan salah satu NPC recurring untuk memberi stake emosional, bukan NPC generik; detail final di Phase 9) |
| `locations` | `loc_mountain_gate` |
| `required_items` / `required_skills` | Bergantung pada build/pavilion pemain — `[DESIGN GAP]` mekanisme sukses/gagal konkret, direkomendasikan kombinasi skill check + pilihan strategis, bukan murni RNG, agar terasa sebagai payoff dari build pemain sepanjang campaign |
| `dialogue_events` | Dialog tegang real-time selama insiden |
| `branching_points` | `branch_a05_c02_b01` (outcome berhasil/gagal) — **MAJOR**, bukan player dialogue choice melainkan gameplay outcome |
| `consequences` | Lihat detail branch |
| `world_state_changes` | Lihat detail branch |
| `relationship_changes` | Lihat detail branch |
| `faction_changes` | Tidak ada langsung |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a05_c03_003` |
| `convergence_id` | `convergence_a05_c02_01` |

### `branch_a05_c02_b01` — Mountain Gate Outcome
| Field | Value |
|---|---|
| `branch_id` | `branch_a05_c02_b01` |
| `parent_quest` | `quest_a05_c02_002` |
| `classification` | **MAJOR** |
| `trigger` | Hasil gameplay real-time (bukan dialog pilihan) |
| `player_choice` | Bagaimana pemain menangani insiden secara mekanis (strategi, build, timing) |
| `choice_meaning` | Payoff dari seluruh pembangunan skill/build sejak Arc I, bukan choice naratif murni |
| `immediate_result` | `flag_mountain_gate_changed` ATAU `flag_mountain_gate_repeated` di-set |
| `state_changes` | Kedua outcome menulis world state permanen berbeda |
| `NPC_reactions` | Jika berhasil: found family dan dunia bereaksi dengan harapan hati-hati; jika gagal: found family dan dunia bereaksi dengan duka/ketakutan yang memperkuat urgensi Found Family Crisis di chapter berikutnya |
| `relationship_changes` | Jika gagal, kemungkinan `state_rel_*` turun untuk anggota yang paling terikat dengan NPC yang terancam (`[DESIGN GAP]` detail) |
| `faction_changes` | Jika gagal, faction Liberation dapat memperoleh momentum wacana ("cultivation menyebabkan ini") — detail Phase 6 |
| `quest_changes` | Beberapa optional quest world-building berbeda tersedia tergantung outcome |
| `future_effects` | **MAJOR payoff Phase 13:** hasil Mountain Gate Incident menjadi salah satu world_state_conditions untuk Ending Matrix — dunia yang "berhasil diselamatkan sekali" vs "gagal diselamatkan sekali" memberi tone berbeda pada epilogue ending manapun yang dicapai |
| `convergence_point` | `convergence_a05_c02_01` |

---

## `quest_a05_c03_003` — Cracks in the Family (Found Family Crisis)

| Field | Value |
|---|---|
| `quest_id` | `quest_a05_c03_003` |
| `title` | Cracks in the Family |
| `arc` / `chapter` | `arc_05` / `chapter_05_03` |
| `quest_type` | Character Quest (multi-karakter, konvergen) |
| `narrative_function` | Character Development, Relationship, Consequence |
| `gameplay_function` | Titik keputusan besar berbasis akumulasi relationship dari seluruh Arc I-IV, bukan pilihan dialog tunggal |
| `prerequisites` | **Reads:** `flag_mountain_gate_changed` ATAU `flag_mountain_gate_repeated` (salah satu, sebagai katalis); seluruh `state_rel_lin_yue/shen_luo/mei_ruo/gu_han` akumulatif sebagai input penentu outcome |
| `objectives` | Menghadapi divergensi ideologis found family |
| `success_conditions` | Konfigurasi found family final ditentukan (tidak ada "sukses" tunggal — semua outcome valid secara naratif) |
| `failure_conditions` | N/A — lihat catatan di atas |
| `involved_npcs` | Keempat found family — chapter ini adalah puncak character arc masing-masing |
| `locations` | Tempat berkumpul kelompok |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Percakapan individual dengan tiap anggota sebelum crisis memuncak (opsional tapi sangat direkomendasikan) |
| `branching_points` | `branch_a05_c03_b01` melalui `branch_a05_c03_b04` (satu per anggota found family, masing-masing menentukan apakah anggota tersebut tetap loyal/berpisah/disillusioned berdasarkan akumulasi `state_rel_*` dan `state_truth_spread_level`) — **MAJOR** |
| `consequences` | Lihat detail branch |
| `world_state_changes` | Lihat detail branch |
| `relationship_changes` | Lihat detail branch |
| `faction_changes` | Anggota yang berpisah berpotensi bergabung dengan faction tertentu (`[DESIGN GAP]` detail — Phase 6) |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a05_c04_004` |
| `convergence_id` | N/A — **PENTING:** Found Family Crisis TIDAK memiliki convergence formal karena hasilnya (siapa tetap, siapa pergi) adalah permanent branching state yang dibawa hingga ending, bukan sesuatu yang "bertemu kembali" di titik naratif berikutnya |

### `branch_a05_c03_b01` — Lin Yue's Position
| Field | Value |
|---|---|
| `branch_id` | `branch_a05_c03_b01` |
| `parent_quest` | `quest_a05_c03_003` |
| `classification` | **MAJOR** |
| `trigger` | `state_rel_lin_yue` akumulatif dari Arc I-V |
| `player_choice` | Bagaimana pemain memperlakukan Lin Yue sepanjang campaign (tidak ada single choice di titik ini — ini adalah payoff akumulatif) |
| `choice_meaning` | Lin Yue ingin melindungi murid-murid Tian Xu (posisi tetap dari MSB §23) — bagaimana ia mengekspresikan ini bergantung pada relationship |
| `immediate_result` | Salah satu dari possible_states MSB §37: Loyal Companion / Separated / Disillusioned / (Sacrificed dan lainnya lebih relevan untuk Phase 13 Ending) |
| `state_changes` | `state_lin_yue_status = <determined>` |
| `NPC_reactions` | N/A — ini adalah hasil, bukan reaksi terhadap sesuatu |
| `relationship_changes` | `state_rel_lin_yue` final terkunci sebagai modifier ending |
| `faction_changes` | Tidak langsung |
| `quest_changes` | Ketersediaan Lin Yue di Arc VI-VII bergantung pada status ini |
| `future_effects` | **MAJOR payoff Phase 13:** `state_lin_yue_status` adalah salah satu character_end_state condition |
| `convergence_point` | N/A |

*(Branch serupa berlaku untuk `branch_a05_c03_b02` Shen Luo, `branch_a05_c03_b03` Mei Ruo, `branch_a05_c03_b04` Gu Han — detail lengkap tiap karakter akan diformalkan penuh di Phase 5 Character Arcs, dirujuk silang dari sini untuk menghindari duplikasi konten antara Quest Graph dan Character Bible.)*

---

## `quest_a05_c04_004` — The Voice Beneath Everything

| Field | Value |
|---|---|
| `quest_id` | `quest_a05_c04_004` |
| `title` | The Voice Beneath Everything |
| `arc` / `chapter` | `arc_05` / `chapter_05_04` |
| `quest_type` | Main Quest |
| `narrative_function` | Mystery, Revelation |
| `gameplay_function` | Dialog encounter pertama dengan Entity |
| `prerequisites` | **Reads:** konfigurasi found family final dari `quest_a05_c03_003` (tidak gating — semua konfigurasi valid untuk melanjutkan) |
| `objectives` | Konfrontasi (dialog) pertama dengan Entity |
| `success_conditions` | Dialog selesai |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Entity (first direct communication) |
| `locations` | `[DESIGN GAP]` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | "Kau membunuhku sekali." / "Aku adalah alasan kalian menyebut dunia ini sebagai anugerah." |
| `branching_points` | Tidak ada — ini adalah revelation wajib, bukan choice |
| `consequences` | Mystery #7 dibuka signifikan |
| `world_state_changes` | **Writes:** `flag_entity_first_contact = true` |
| `relationship_changes` / `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada langsung — memory besar ada di quest berikutnya |
| `next_quests` | `quest_a05_c05_005` |
| `convergence_id` | N/A |

---

## `quest_a05_c05_005` — What I Tried to Kill (Arc V Ending)

| Field | Value |
|---|---|
| `quest_id` | `quest_a05_c05_005` |
| `title` | What I Tried to Kill |
| `arc` / `chapter` | `arc_05` / `chapter_05_05` |
| `quest_type` | Memory Quest |
| `narrative_function` | Mystery, Revelation, Consequence |
| `gameplay_function` | Menutup Arc V dengan memory besar |
| `prerequisites` | **Reads:** `flag_entity_first_contact == true` |
| `objectives` | Mengalami memory percobaan membunuh Entity |
| `success_conditions` | Memory selesai |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Tidak ada — momen memory soliter |
| `locations` | Terhubung dengan lokasi memory sebelumnya |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Tidak ada — murni memory sequence |
| `branching_points` | Tidak ada |
| `consequences` | **Rekontekstualisasi besar kedua:** `belief_protagonist_may_be_cause` dari Arc III sekarang jelas TIDAK akurat sebagai "penyebab tragedi" secara sederhana — protagonis (Jiang Yan) *mencoba mencegah*, gagal, dan kegagalan itu yang menyebabkan konsekuensi berantai. Ini bukan pembebasan dari tanggung jawab, tapi rekontekstualisasi yang lebih kompleks (konsisten dengan prinsip: revelation harus mengubah state, bukan sekadar informasi baru) |
| `world_state_changes` | **Writes:** `flag_memory_kill_attempt_seen = true`, `flag_cycle_formation_known_partial = true`, `belief_protagonist_may_be_cause = false` (dikoreksi, bukan dihapus — dicatat sebagai state transition untuk keperluan Phase 7 memory reliability tracking) |
| `relationship_changes` / `faction_changes` | Tidak ada baru |
| `memory_triggers` | `memory_a05_m01` (kill attempt, reliability TINGGI — ini adalah revelation yang mengoreksi memory sebelumnya, bukan memory yang perlu dikoreksi lagi) |
| `next_quests` | `quest_a06_c01_001` (Arc VI dimulai) |
| `convergence_id` | N/A |

---

# ARC VI — THE LAST CYCLE

## `quest_a06_c01_001` — Someone Like Me

| Field | Value |
|---|---|
| `quest_id` | `quest_a06_c01_001` |
| `title` | Someone Like Me |
| `arc` / `chapter` | `arc_06` / `chapter_06_01` |
| `quest_type` | Investigation Quest / Memory Quest |
| `narrative_function` | Character Development, Revelation, Relationship (dengan diri sendiri masa lalu) |
| `gameplay_function` | Investigasi historis mendalam tentang kehidupan Jiang Yan |
| `prerequisites` | **Reads:** `flag_cycle_formation_known_partial == true` |
| `objectives` | Menemukan detail kehidupan awal Jiang Yan; paralel dengan found family protagonis |
| `success_conditions` | Paralel dipahami penuh |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Tidak ada NPC baru — investigasi historis |
| `locations` | `[DESIGN GAP]` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Tidak ada — murni discovery/reading |
| `branching_points` | Tidak ada |
| `consequences` | Mystery #2 terjawab signifikan |
| `world_state_changes` | **Writes:** `flag_jiang_yan_origin_known = true` |
| `relationship_changes` / `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a06_c02_002` |
| `convergence_id` | N/A |

---

## `quest_a06_c02_002` — The Betrayal That Wasn't

**Catatan produksi:** quest ini berisi rekomendasi desain (identitas "pengkhianat" = Mentor) yang ditandai eksplisit sebagai inferensi, bukan fakta MSB — konsisten dengan catatan di Phase 3.

| Field | Value |
|---|---|
| `quest_id` | `quest_a06_c02_002` |
| `title` | The Betrayal That Wasn't |
| `arc` / `chapter` | `arc_06` / `chapter_06_02` |
| `quest_type` | Investigation Quest / Character Quest |
| `narrative_function` | Character Development, Revelation |
| `gameplay_function` | Investigasi untuk mengungkap identitas "pengkhianat" |
| `prerequisites` | **Reads:** `flag_jiang_yan_origin_known == true` |
| `objectives` | Mengidentifikasi dan memahami motivasi si "pengkhianat" |
| `success_conditions` | Identitas terungkap penuh |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | `[DESIGN GAP — REKOMENDASI: npc_mentor]` |
| `locations` | `[DESIGN GAP]` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Reveal bahwa "pengkhianatan" adalah upaya mencegah, bukan self-interest |
| `branching_points` | Tidak ada |
| `consequences` | Mystery #8 mendapat detail baru; kompleksitas moral pola berulang (konsisten dengan Grandmaster) |
| `world_state_changes` | **Writes:** `flag_betrayal_identity_known = true` |
| `relationship_changes` | Jika `[DESIGN GAP]` rekomendasi Mentor diterima: `state_rel_mentor` mendapat lapisan kompleksitas baru (tidak otomatis naik/turun — tergantung reaksi pemain, akan diformalkan Phase 8 Dialogue) |
| `faction_changes` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a06_c03_003` |
| `convergence_id` | N/A |

---

## `quest_a06_c03_003` — The Gate, The Formation, The Cost

| Field | Value |
|---|---|
| `quest_id` | `quest_a06_c03_003` |
| `title` | The Gate, The Formation, The Cost |
| `arc` / `chapter` | `arc_06` / `chapter_06_03` |
| `quest_type` | Memory Quest |
| `narrative_function` | Mystery, Revelation (puncak) |
| `gameplay_function` | Revelation terbesar dalam campaign — payoff hampir seluruh foreshadowing |
| `prerequisites` | **Reads:** `flag_betrayal_identity_known == true` |
| `objectives` | Memahami The Gate secara penuh |
| `success_conditions` | Revelation lengkap dialami |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Jiang Yan (via memory) |
| `locations` | `loc_the_gate` |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Memory sequence lengkap: The Gate, upaya memisahkan Entity dari sumber, kegagalan, Cycle Formation sebagai solusi darurat |
| `branching_points` | Tidak ada — revelation wajib |
| `consequences` | Mystery #9, #11, #12 terjawab penuh |
| `world_state_changes` | **Writes:** `flag_the_gate_full_truth_known = true`, `flag_second_life_meaning_known = true` |
| `relationship_changes` / `faction_changes` | Tidak ada baru |
| `memory_triggers` | `memory_a06_m01` (The Gate, reliability TINGGI — ini adalah ground truth) |
| `next_quests` | `quest_a06_c04_004` |
| `convergence_id` | N/A |

---

## `quest_a06_c04_004` — What the Sword Remembers (Arc VI Ending / Final Choice Before Endgame)

| Field | Value |
|---|---|
| `quest_id` | `quest_a06_c04_004` |
| `title` | What the Sword Remembers |
| `arc` / `chapter` | `arc_06` / `chapter_06_04` |
| `quest_type` | Character Quest / Branching Quest |
| `narrative_function` | Character Development, Relationship, Setup untuk future payoff (ending path) |
| `gameplay_function` | Emotional payoff Mentor + Major Choice terbesar sejauh campaign |
| `prerequisites` | **Reads:** `flag_second_life_meaning_known == true` |
| `objectives` | Momen personal dengan Mentor; memilih prinsip final |
| `success_conditions` | Salah satu dari empat prinsip dipilih |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | `npc_mentor` (revelation terbesar karakter ini) |
| `locations` | Tempat latihan personal dengan Mentor |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | "Cara kau memegang pedang... Aku pernah melihatnya." Versi dialog Mentor di sini dimodifikasi jika `flag_grandmaster_met == true` dan `state_rel_grandmaster` tinggi dari Arc IV — Mentor dapat merujuk balik ke kompleksitas ideologis Grandmaster sebagai cermin bagi keraguannya sendiri, memperkuat pola "antagonist yang dapat dipahami" secara lintas-karakter |
| `branching_points` | `branch_a06_c04_b01` (Preserve), `branch_a06_c04_b02` (Destroy), `branch_a06_c04_b03` (Transform), `branch_a06_c04_b04` (Sacrifice) — keempatnya **MAJOR** |
| `consequences` | Lihat detail branch |
| `world_state_changes` | Lihat detail branch |
| `relationship_changes` | `state_rel_mentor` mendapat payoff emosional besar (nilai eksak tergantung akumulasi relationship sebelumnya) |
| `faction_changes` | Tidak ada langsung dari momen Mentor, tapi prinsip yang dipilih memengaruhi faction alignment secara signifikan (detail Phase 6) |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a07_c01_001` (Arc VII dimulai) |
| `convergence_id` | `convergence_a06_c04_01` |

### `branch_a06_c04_b01` s.d. `b04` — Final Principle
| Field | Value |
|---|---|
| `branch_id` | `branch_a06_c04_b01/b02/b03/b04` |
| `parent_quest` | `quest_a06_c04_004` |
| `classification` | **MAJOR** |
| `trigger` | Pemain memilih satu dari Preserve/Destroy/Transform/Sacrifice |
| `player_choice` | Prinsip filosofis untuk final act |
| `choice_meaning` | MSB eksplisit: "tidak langsung menentukan ending. Ia menentukan jalur final." — **PENTING untuk data engine: ini BUKAN gate ending langsung, melainkan modifier/weight yang dikombinasikan dengan seluruh state lain di Phase 13** |
| `immediate_result` | `state_final_principle = <chosen>` |
| `state_changes` | Menjadi dominant path indicator untuk Arc VII, bukan hard-lock |
| `NPC_reactions` | Found family (konfigurasi final dari Arc V) bereaksi berbeda tergantung prinsip — anggota yang selaras secara ideologis mendukung lebih kuat |
| `relationship_changes` | Variatif tergantung keselarasan ideologi found family individual |
| `faction_changes` | Signifikan — tiap prinsip selaras dengan satu atau lebih faction secara lebih kuat (detail Phase 6) |
| `quest_changes` | Konten Chapter 7.1 (The Last Night) disesuaikan tone-nya berdasarkan prinsip ini |
| `future_effects` | **MAJOR payoff Phase 13:** salah satu dari major_choice_conditions utama Ending Matrix |
| `convergence_point` | `convergence_a06_c04_01` — keempat prinsip menuju Chapter 7.1 yang sama, tapi starting condition berbeda |

---

# ARC VII — SECOND LIFE

## `quest_a07_c01_001` — The Last Night

| Field | Value |
|---|---|
| `quest_id` | `quest_a07_c01_001` |
| `title` | The Last Night |
| `arc` / `chapter` | `arc_07` / `chapter_07_01` |
| `quest_type` | Main Quest (Convergence besar) |
| `narrative_function` | Consequence (payoff relationship terbesar) |
| `gameplay_function` | Hub chapter — bertemu seluruh cast sebelum climax |
| `prerequisites` | **Reads:** `state_final_principle != null` |
| `objectives` | Berinteraksi dengan seluruh cast sebelum turun ke bawah Tian Xu |
| `success_conditions` | Siap untuk Final Confrontation |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Seluruh cast — found family (konfigurasi Arc V), Mentor, Grandmaster, Shen Luo, perwakilan faksi |
| `locations` | Seluruh Tian Xu (crisis state) |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | Percakapan singkat dengan tiap karakter, state-aware terhadap SELURUH akumulasi campaign — ini adalah dialogue paling kompleks secara kondisional dalam seluruh dokumen (akan diformalkan detail Phase 8) |
| `branching_points` | Tidak ada branch baru |
| `consequences` | Posisi final tiap karakter/faksi terkonfirmasi |
| `world_state_changes` | **Writes:** `flag_last_night_complete = true` |
| `relationship_changes` / `faction_changes` | Tidak ada baru — chapter ini adalah *observasi* dari seluruh state yang sudah terbentuk |
| `memory_triggers` | Tidak ada |
| `next_quests` | `quest_a07_c02_002` |
| `convergence_id` | N/A |

---

## `quest_a07_c02_002` — I Am Not You

| Field | Value |
|---|---|
| `quest_id` | `quest_a07_c02_002` |
| `title` | I Am Not You |
| `arc` / `chapter` | `arc_07` / `chapter_07_02` |
| `quest_type` | Main Quest |
| `narrative_function` | Revelation (puncak), Character Development (puncak) |
| `gameplay_function` | Final Confrontation — klimaks emosional utama |
| `prerequisites` | **Reads:** `flag_last_night_complete == true` |
| `objectives` | Konfrontasi dengan Jiang Yan imprint; mendengar Entity's Truth lengkap |
| `success_conditions` | "Aku bukan kau" diucapkan |
| `failure_conditions` | Tidak ada |
| `involved_npcs` | Jiang Yan imprint, Entity |
| `locations` | Ruang terdalam Tian Xu (di bawah `loc_tianxu_deepest_chamber`) |
| `required_items` / `required_skills` | Tidak ada |
| `dialogue_events` | "Aku membuatmu untuk menyelesaikan apa yang gagal kuselesaikan." → "Tidak. Aku bukan kau." Modifier dialog berdasarkan `state_identity_stance` (Arc III) — lihat catatan payoff di branch Arc III |
| `branching_points` | Tidak ada — ini adalah revelation wajib, bukan choice bercabang |
| `consequences` | Entity's Truth lengkap; titik paling penting campaign (MSB eksplisit) |
| `world_state_changes` | **Writes:** `flag_i_am_not_you_said = true`, `flag_entity_truth_known = true` |
| `relationship_changes` / `faction_changes` | Tidak ada baru |
| `memory_triggers` | Tidak ada — ini bukan memory, ini present-moment confrontation |
| `next_quests` | `quest_a07_c03_003` |
| `convergence_id` | N/A |

---

## `quest_a07_c03_003` — Second Life (FINAL DECISION)

| Field | Value |
|---|---|
| `quest_id` | `quest_a07_c03_003` |
| `title` | Second Life |
| `arc` / `chapter` | `arc_07` / `chapter_07_03` |
| `quest_type` | Branching Quest (Ending Decision) |
| `narrative_function` | Seluruh 10 fungsi quest sekaligus — ini adalah payoff terbesar dokumen |
| `gameplay_function` | Menentukan ending final dari 5 kemungkinan |
| `prerequisites` | **Reads:** `flag_entity_truth_known == true` |
| `objectives` | Memilih jalur akhir |
| `success_conditions` | Salah satu dari 5 ending tercapai |
| `failure_conditions` | N/A |
| `involved_npcs` | Bervariasi per ending |
| `locations` | Bervariasi per ending |
| `required_items` / `required_skills` | Tidak ada tambahan |
| `dialogue_events` | Bervariasi per ending — detail penuh Phase 13 |
| `branching_points` | `branch_a07_c03_b01` (Preserve → Unbroken Heaven), `branch_a07_c03_b02` (Destroy → Mortal Dawn), `branch_a07_c03_b03` (Transform → New Heaven), `branch_a07_c03_b04` (Sacrifice → Nameless Guardian), `branch_a07_c03_b05` (Hidden Resolution → Second Life, hanya jika kombinasi kondisi terpenuhi) — kelimanya **MAJOR**, detail kondisi lengkap di Phase 13 |
| `consequences` | Epilogue sesuai ending |
| `world_state_changes` | **Writes:** `state_ending_achieved = <one of 5>` |
| `relationship_changes` | Character end states final (Phase 13) |
| `faction_changes` | Faction end states final (Phase 6/13) |
| `memory_triggers` | Tidak ada |
| `next_quests` | N/A — akhir campaign |
| `convergence_id` | N/A — titik akhir, bukan convergence menuju konten lanjutan |

**Catatan penting:** detail *kondisi* tiap branch (required_conditions, forbidden_conditions, dst) sengaja **tidak** dispesifikasikan penuh di sini untuk menghindari duplikasi — akan dispesifikasikan lengkap di Phase 13 (Ending Matrix) sebagai dokumen otoritatif untuk ending conditions. Quest Graph ini hanya mencatat bahwa titik keputusan ini ADA dan bercabang lima arah.

---

## Ringkasan State Baru Arc III-VII

| State | Tipe | Ditulis oleh | Dibaca oleh |
|---|---|---|---|
| `flag_mural_analyzed` | boolean | `quest_a03_c01_001` | `quest_a03_c02_002` |
| `flag_name_jiang_yan_known` | boolean | `quest_a03_c02_002` | `quest_a03_c03_003` |
| `flag_mo_chen_met` | boolean | `quest_a03_c02_002` | Phase 9 NPC recurring logic |
| `flag_jiang_yan_deceased_confirmed` | boolean | `quest_a03_c03_003` | `quest_a03_c04_004` |
| `state_identity_stance` | enum (deny/accept_cautious/seek_truth) | `branch_a03_c04_b01/02/03` | Arc IV-VII dialogue, Phase 13 ending |
| `flag_memory_gate_a03_seen` | boolean | `quest_a03_c05_005` | `quest_a04_c01_001` |
| `belief_protagonist_may_be_cause` | boolean (mutable — bukan permanent flag) | `quest_a03_c05_005` (true) → `quest_a05_c05_005` (false, dikoreksi) | Phase 7 Memory reliability tracking |
| `flag_history_v1_v2_compared` | boolean | `quest_a04_c01_001` | `quest_a04_c02_002` |
| `flag_version_iii_read` | boolean | `quest_a04_c02_002` | `state_truth_spread_level` availability |
| `flag_origin_cultivation_known_partial` | boolean | `quest_a04_c02_002` | `quest_a04_c03_003` |
| `state_rel_grandmaster` | integer | `quest_a04_c03_003` | Arc VI Grandmaster payoff dialogue |
| `flag_stakes_of_stopping_source_known` | boolean | `quest_a04_c03_003` | `quest_a04_c04_004` |
| `flag_tianxu_feeds_segel_known` | boolean | `quest_a04_c04_004` | `quest_a05_c01_001` |
| `flag_arc4_complete` | boolean | `quest_a04_c04_004` | `quest_a05_c01_001` |
| `state_truth_spread_level` | integer (akumulatif) | Berbagai dialog opsional Arc IV-V | Faction reaction Phase 6 |
| `world_event_a05_spiritual_collapse` | state (active/resolved) | `quest_a05_c01_001` | `quest_a05_c02_002` |
| `flag_mountain_gate_changed` / `flag_mountain_gate_repeated` | boolean (mutually exclusive) | `branch_a05_c02_b01` | Phase 13 ending conditions |
| `state_lin_yue_status` / `state_shen_luo_status` / `state_mei_ruo_status` / `state_gu_han_status` | enum | `branch_a05_c03_b01-04` | Phase 5 Character Arcs, Phase 13 ending |
| `flag_entity_first_contact` | boolean | `quest_a05_c04_004` | `quest_a05_c05_005` |
| `flag_memory_kill_attempt_seen` | boolean | `quest_a05_c05_005` | `quest_a06_c01_001` |
| `flag_cycle_formation_known_partial` | boolean | `quest_a05_c05_005` | `quest_a06_c01_001` |
| `flag_jiang_yan_origin_known` | boolean | `quest_a06_c01_001` | `quest_a06_c02_002` |
| `flag_betrayal_identity_known` | boolean | `quest_a06_c02_002` | `quest_a06_c03_003` |
| `flag_the_gate_full_truth_known` | boolean | `quest_a06_c03_003` | Phase 13 Hidden Resolution prerequisite |
| `flag_second_life_meaning_known` | boolean | `quest_a06_c03_003` | `quest_a06_c04_004`, Phase 13 |
| `state_final_principle` | enum (preserve/destroy/transform/sacrifice) | `branch_a06_c04_b01-04` | Arc VII tone, Phase 13 ending (weight, bukan hard gate) |
| `flag_last_night_complete` | boolean | `quest_a07_c01_001` | `quest_a07_c02_002` |
| `flag_i_am_not_you_said` | boolean | `quest_a07_c02_002` | Phase 13 |
| `flag_entity_truth_known` | boolean | `quest_a07_c02_002` | `quest_a07_c03_003` |
| `state_ending_achieved` | enum (5 values) | `quest_a07_c03_003` | Epilogue rendering, Phase 13 |

---

## Design Gap & Recommendation Ringkasan Fase Ini

1. **Major Choice Arc III** (`quest_a03_c04_004`) — quest baru dirancang penuh (Deny/Accept Cautious/Seek Truth), ditandai eksplisit sebagai desain baru konsisten tema, bukan turunan MSB langsung
2. **Ongoing state Arc IV** (`state_truth_spread_level`) — mekanisme baru menggantikan single-choice yang tidak didukung MSB eksplisit
3. **Identitas "pengkhianat" Jiang Yan** — direkomendasikan Mentor, ditandai `[DESIGN GAP — REKOMENDASI]` di quest terkait
4. **Mekanisme sukses/gagal Mountain Gate Incident** — direkomendasikan skill check + pilihan strategis, bukan RNG murni, belum final
5. **NPC yang terancam di Mountain Gate Incident** — direkomendasikan NPC recurring untuk stake emosional, nama spesifik belum ditentukan
6. Berbagai `[DESIGN GAP]` lokasi spesifik — konsisten dicatat untuk diformalkan Phase 9

Tidak ada gap yang diisi tanpa penanda eksplisit di titik ini.

---

**File berikutnya:** `04-character-arcs.md`, `05-faction-arcs.md`, `06-memory-architecture.md` — tiga dokumen paralel untuk Phase 5, dimulai dengan Character Arcs karena paling banyak dirujuk silang oleh Quest Graph di atas (terutama `branch_a05_c03_b01-04` yang sengaja tidak diperluas penuh di sini untuk menghindari duplikasi).
