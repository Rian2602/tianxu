# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 13. Story State Catalog

**Status:** DRAFT — Phase 17 of 18
**Depends on:** seluruh sebelas file sebelumnya — fase ini adalah katalog MASTER yang mengonsolidasikan setiap state yang tersebar
**Koreksi ditemukan saat membangun fase ini:** audit otomatis menemukan `state_rep_tianxu_orthodox` masih tersisa di branch Obey (`quest_a02_c03_006`, Quest Graph Arc I-II) meski konsolidasi sebelumnya (dicatat di file yang sama) hanya memperbaiki branch Confront. Diperbaiki menjadi `state_rep_tianxu` untuk konsistensi penuh. Dicatat terbuka di sini karena ini adalah audit lanjutan yang menemukan celah dari audit sebelumnya — bukti bahwa proses verifikasi berlapis diperlukan, bukan cukup sekali jalan.

**Prinsip wajib:** tidak ada state redundan. Setiap state_id harus punya `modified_by`, `read_by`, `purpose`, `persistence`, dan `affected_content` yang jelas — state tanpa consumer yang jelas adalah tanda dead-end yang harus dipertanyakan.

---

## GLOBAL FLAGS

State yang berlaku lintas-Arc, tidak terikat satu Arc/Chapter spesifik.

| state_id | type | initial_value | modified_by | read_by | purpose | persistence | affected_content |
|---|---|---|---|---|---|---|---|
| `flag_memory_awareness` | boolean | false | `quest_a01_c04_006` | `quest_a02_c01_001`, banyak dialogue | Menandai protagonis sadar akan koneksi kehidupan pertama | Permanen | Membuka Arc II, memodifikasi tone dialogue selanjutnya |
| `belief_protagonist_may_be_cause` | boolean (mutable) | null | `quest_a03_c05_005` (true) → `quest_a05_c05_005` (false) | Phase 7 Memory reliability tracking, tone dialogue Arc IV-VI | Melacak keyakinan pemain yang BERUBAH, bukan fakta tetap | Mutable — SATU-SATUNYA state di katalog ini yang secara eksplisit bukan permanent flag | Nuansa dialogue tentang tanggung jawab moral protagonis |
| `state_identity_stance` | enum (deny/accept_cautious/seek_truth) | null | `branch_a03_c04_b01/02/03` | Arc IV-VII dialogue, Ending Matrix (tone Chapter 7.2) | Sikap protagonis terhadap identitas Jiang Yan | Permanen | Modifier dialog `dialog_a07_d015`, akses investigasi opsional |
| `state_final_principle` | enum (preserve/destroy/transform/sacrifice) | null | `branch_a06_c04_b01-04` | Tone Arc VII, Ending Matrix (ACCESS driver, bukan hard gate) | Prinsip filosofis final sebelum endgame | Permanen | Dominant path menuju salah satu 4 ending utama |
| `state_ending_achieved` | enum (5 values) | null | `quest_a07_c03_003` | Epilogue rendering | Ending final yang tercapai | Permanen (akhir permainan) | Seluruh epilogue content |

---

## ARC FLAGS

State yang menandai penyelesaian/status satu Arc secara keseluruhan.

| state_id | type | initial_value | modified_by | read_by | purpose | persistence | affected_content |
|---|---|---|---|---|---|---|---|
| `flag_arc2_complete` | boolean | false | `quest_a02_c04_009` | `quest_a03_c01_001` | Gate Arc II→III | Permanen | Membuka seluruh Arc III |
| `flag_arc4_complete` | boolean | false | `quest_a04_c04_004` | `quest_a05_c01_001`, `event_a05_spiritual_collapse` | Gate Arc IV→V | Permanen | Membuka Arc V dan Spiritual Collapse |
| `flag_last_night_complete` | boolean | false | `quest_a07_c01_001` | `quest_a07_c02_002` | Gate Chapter 7.1→7.2 (titik tanpa-jalan-kembali) | Permanen | Membuka Final Confrontation, mengunci optional content sebelumnya |

**Catatan:** Arc I tidak memiliki `flag_arc1_complete` terpisah — transisinya memakai `flag_memory_awareness` (Global Flag) sebagai gate fungsional. Arc III, VI, VII tidak memiliki Arc-completion-flag terpisah karena transisinya memakai state lain yang lebih spesifik (`flag_memory_gate_a03_seen`, `flag_second_life_meaning_known`, `state_ending_achieved`). Ini BUKAN inkonsistensi — bukti bahwa tidak setiap Arc memerlukan flag generik terpisah jika sudah ada state lebih spesifik yang berfungsi sama.

---

## CHAPTER FLAGS

State yang menandai penyelesaian satu Chapter spesifik dan menjadi gate chapter berikutnya.

| state_id | type | modified_by | read_by | purpose |
|---|---|---|---|---|
| `flag_dream_a01_01_seen` | boolean | `quest_a01_c01_001` | `quest_a01_c01_002` | Gate Chapter 1.1 internal |
| `flag_formation_touched` | boolean | `quest_a01_c04_005` | `quest_a01_c04_006` | Gate Chapter 1.4 internal |
| `flag_team_recognized` | boolean | `quest_a02_c01_002` | `quest_a02_c02_003` | Gate Chapter 2.1→2.2 |
| `flag_outer_region_unlocked` | boolean | `quest_a02_c02_003` | `quest_a02_c02_004` | Gate Chapter 2.2 internal |
| `flag_disturbance_investigated` | boolean | `quest_a02_c02_004` | `quest_a02_c02_005` | Gate Chapter 2.2 internal |
| `flag_evidence_missing_disciple` | boolean | `quest_a02_c02_005` | `quest_a02_c03_006` | Gate Chapter 2.2→2.3 |
| `flag_hidden_cave_explored` | boolean | `quest_a02_c04_007` | `quest_a02_c04_008` | Gate Chapter 2.4 internal |
| `flag_mural_analyzed` | boolean | `quest_a03_c01_001` | `quest_a03_c02_002` | Gate Chapter 3.1→3.2 |
| `flag_mo_chen_met` | boolean | `quest_a03_c02_002` | Phase 9 NPC recurring logic | Gate kemunculan Mo Chen berikutnya |
| `flag_name_jiang_yan_known` | boolean | `quest_a03_c02_002` | `quest_a03_c03_003` | Gate Chapter 3.2→3.3 |
| `flag_jiang_yan_deceased_confirmed` | boolean | `quest_a03_c03_003` | `quest_a03_c04_004` | Gate Chapter 3.3→3.4 |
| `flag_memory_gate_a03_seen` | boolean | `quest_a03_c05_005` | `quest_a04_c01_001` | Gate Arc III→IV |
| `flag_history_v1_v2_compared` | boolean | `quest_a04_c01_001` | `quest_a04_c02_002` | Gate Chapter 4.1→4.2 |
| `flag_version_iii_read` | boolean | `quest_a04_c02_002` | `quest_a04_c03_003`, `state_truth_spread_level` availability | Gate Chapter 4.2→4.3 |
| `flag_grandmaster_met` | boolean | `quest_a04_c03_003` | Phase 9 NPC logic, prerequisite dialog opsional Arc VI | Gate + recurring appearance |
| `flag_stakes_of_stopping_source_known` | boolean | `quest_a04_c03_003` | `quest_a04_c04_004` | Gate Chapter 4.3→4.4 |
| `flag_tianxu_feeds_segel_known` | boolean | `quest_a04_c04_004` | `quest_a05_c01_001` | Gate Arc IV→V |
| `flag_entity_first_contact` | boolean | `quest_a05_c04_004` | `quest_a05_c05_005` | Gate Chapter 5.4→5.5 |
| `flag_memory_kill_attempt_seen` | boolean | `quest_a05_c05_005` | `quest_a06_c01_001` | Gate Arc V→VI |
| `flag_cycle_formation_known_partial` | boolean | `quest_a05_c05_005` | `quest_a06_c01_001` | Gate Arc V→VI (paralel dengan di atas) |
| `flag_jiang_yan_origin_known` | boolean | `quest_a06_c01_001` | `quest_a06_c02_002` | Gate Chapter 6.1→6.2 |
| `flag_betrayal_identity_known` | boolean | `quest_a06_c02_002` | `quest_a06_c03_003` | Gate Chapter 6.2→6.3 |
| `flag_the_gate_full_truth_known` | boolean | `quest_a06_c03_003` | `quest_a06_c04_004`, Ending Matrix (Hidden Resolution) | Gate Chapter 6.3→6.4 |
| `flag_second_life_meaning_known` | boolean | `quest_a06_c03_003` | `quest_a06_c04_004` | Gate Chapter 6.3→6.4 (paralel) |
| `flag_i_am_not_you_said` | boolean | `quest_a07_c02_002` | Ending Matrix | Gate internal Chapter 7.2 |
| `flag_entity_truth_known` | boolean | `quest_a07_c02_002` | `quest_a07_c03_003`, seluruh Ending Matrix minimum_conditions | Gate Chapter 7.2→7.3 |

---

## QUEST FLAGS

State yang secara spesifik menandai hasil satu quest/branch tunggal (di luar yang sudah masuk kategori Chapter Flags karena fungsi gating-nya).

| state_id | type | modified_by | read_by | purpose |
|---|---|---|---|---|
| `state_murid_status` | enum | `quest_a01_c01_002` | `quest_a01_c02_003` | Status administratif awal |
| `state_reputation_academic` | integer | `quest_a02_c01_001` | `quest_a02_c01_002` | Reputasi akademik lokal, bukan reputasi faksi |
| `flag_archive_suspicious` | boolean | `branch_a02_c03_b02` (Investigate) | `dialog_a02_d014`, Ending Matrix (Hidden Resolution catatan pendiri) | Hasil First Major Choice — jalur Investigate |
| `flag_mountain_gate_changed` / `flag_mountain_gate_repeated` | boolean (mutually exclusive) | `branch_a05_c02_b01` | Consequence Matrix, Ending Matrix (QUALITY modifier di semua ending) | Hasil Repeating Event |

---

## MEMORY FLAGS

| state_id | type | modified_by | read_by | purpose |
|---|---|---|---|---|
| `flag_memory_lin_yue_elder_seen` | boolean | `quest_a02_c04_008` | `quest_a02_c04_009` | Menandai memory_a02_m01 dialami |
| `item_ancient_symbol` | item state | `quest_a01_c04_006` | `quest_a03_c02_002` (soft-recognition, bukan hard gate) | Bukti fisik lintas-memory |
| `item_artifact_01` | item state | `quest_a02_c04_008` | `quest_a03_c01_001` | Trigger sistematis Memory Investigation System |
| `item_note_cycle_begins_again` | item state | `quest_a02_c02_005` | `quest_a02_c03_006` (required_items) | Bukti fisik pemicu First Major Choice |

**Catatan:** delapan `memory_id` (`memory_a01_m01` dst.) BUKAN state — mereka adalah content object (Memory Bible), bukan game state yang dibaca/ditulis quest lain. Dicatat di sini untuk klarifikasi supaya tidak disalahartikan sebagai state yang hilang dari katalog ini.

---

## RELATIONSHIP STATES

| state_id | type | modified_by | read_by | purpose |
|---|---|---|---|---|
| `state_rel_lin_yue` | integer | `quest_a01_c02_003` dan seterusnya (akumulatif) | Dialogue matrix, `branch_a05_c03_b01`, Ending Matrix | Relationship dengan Lin Yue |
| `state_rel_shen_luo` | integer | Sama pola | `branch_a05_c03_b02`, Ending Matrix, `autonomous_trigger_condition` Shen Luo | Relationship dengan Shen Luo |
| `state_rel_mei_ruo` | integer | Sama pola, ditambah `branch_a03_c04_b03` (Seek Truth, boost lebih besar) | `branch_a05_c03_b03`, Ending Matrix | Relationship dengan Mei Ruo |
| `state_rel_gu_han` | integer | Sama pola | `branch_a05_c03_b04`, Ending Matrix, `autonomous_trigger_condition` Gu Han | Relationship dengan Gu Han |
| `state_rel_master` | integer | `branch_a02_c03_b01` (Obey) | `dialog_a02_d014` versi Obey | Relationship dengan guru pembimbing Arc II (BUKAN Mentor karakter utama — dicatat terpisah, entitas berbeda) |
| `state_rel_mentor` | integer | Akumulatif sejak Arc I (first_appearance direkomendasikan) | Chapter 6.4 emotional payoff | Relationship dengan `npc_mentor` |
| `state_rel_grandmaster` | integer | `quest_a04_c03_003` dan seterusnya | `dialog_a04_d033`, Ending Matrix (QUALITY modifier Unbroken Heaven) | Relationship dengan Grandmaster |
| `state_lin_yue_status` / `state_shen_luo_status` / `state_mei_ruo_status` / `state_gu_han_status` | enum (per-karakter possible_states dari Phase 5) | `branch_a05_c03_b01-04` | Character Bible end_state, Ending Matrix character_end_states | Hasil FINAL Found Family Crisis — berbeda dari `state_rel_*` yang kontinu, ini adalah snapshot kategorikal permanen |

**Klarifikasi penting yang ditemukan saat audit fase ini:** `state_rel_master` (Arc II, guru pembimbing generik) dan `state_rel_mentor` (karakter utama `npc_mentor`) adalah DUA STATE BERBEDA merujuk DUA ENTITAS BERBEDA — bukan duplikasi. Ini perlu ditegaskan eksplisit karena penamaannya mirip dan berpotensi disalahpahami sebagai bug oleh developer yang membaca katalog ini tanpa konteks penuh. Direkomendasikan penamaan lebih jelas jika memungkinkan di tahap implementasi (mis. `state_rel_arc2_teacher` vs `state_rel_mentor`), tapi TIDAK diubah di sini untuk menghindari breaking change terhadap seluruh referensi yang sudah ditulis di sepuluh file sebelumnya.

---

## FACTION STATES

| state_id | type | modified_by | read_by | purpose |
|---|---|---|---|---|
| `state_rep_tianxu` | integer | `branch_a02_c03_b01` (Obey, positif), `branch_a02_c03_b03` (Confront, negatif) | Faction Bible reactions, `dialog_a02_d014`, Ending Matrix | Reputasi umum dengan institusi Tian Xu — **dikoreksi fase ini dari sisa `state_rep_tianxu_orthodox` yang lolos audit sebelumnya** |
| `state_rep_liberation` | integer | Branch Confront (bibit), `flag_mountain_gate_repeated` | Faction Bible, autonomous trigger Gu Han | Reputasi dengan Liberation Faction |
| `state_rep_reformists` | integer | `state_truth_spread_level`, branch Confront (bibit) | Faction Bible, Ending Matrix (QUALITY New Heaven) | Reputasi dengan Reformists |
| `state_truth_spread_level` | integer (akumulatif) | Dialog opsional tersebar Arc IV-V | Faction Bible reactions (multi-faksi) | Mekanisme "menyebarkan kebenaran" pengganti single-choice Arc IV |

---

## WORLD STATES

| state_id | type | modified_by | read_by | purpose |
|---|---|---|---|---|
| `world_event_a05_spiritual_collapse` | state (active/resolved) | `quest_a05_c01_001` | `quest_a05_c02_002`, World Event Bible | Payung krisis skala-dunia Arc V |
| `world_event_a07_the_last_night` | state (triggered) | Otomatis awal Arc VII | `quest_a07_c01_001` | Konsolidasi 3 event MSB (Formation Failure, Entity Awakening, Faction Conflict) |
| `state_pavilion` | enum (wuxin/jianxin/yanzhi/liuguang, permanen) | `branch_a01_c03_b01` | Curriculum, dialogue modifier sepanjang campaign, Ending Matrix | Pilihan filosofi cultivation |

---

## KNOWLEDGE STATES

State yang secara spesifik melacak APA yang diketahui protagonis (berbeda dari Chapter Flags yang lebih fokus gating) — dikelompokkan terpisah karena fungsinya lebih ke arah "pemahaman naratif" daripada "akses konten."

| state_id | type | modified_by | read_by | purpose |
|---|---|---|---|---|
| `flag_origin_cultivation_known_partial` | boolean | `quest_a04_c02_002` | `quest_a04_c03_003` | Pemahaman parsial origin cultivation |

*(Sebagian besar "knowledge states" lain sudah tercakup Chapter Flags karena fungsi gating dan fungsi knowledge-nya menyatu — dicatat di sini untuk menghindari duplikasi entri.)*

---

## ENDING FLAGS

Sudah tercakup penuh di kategori GLOBAL FLAGS (`state_ending_achieved`) — dicatat di sini sebagai cross-reference sesuai struktur sepuluh kategori wajib, bukan duplikasi entri.

---

## Redundancy Audit (Verifikasi Akhir Wajib)

| Kandidat Redundansi Diperiksa | Hasil |
|---|---|
| `flag_cycle_formation_known_partial` vs `flag_the_gate_full_truth_known` | TIDAK redundan — yang pertama parsial (Arc V), yang kedua penuh (Arc VI), keduanya diperlukan sebagai TAHAPAN terpisah untuk Hidden Resolution (dicatat Ending Matrix) |
| `state_rel_master` vs `state_rel_mentor` | TIDAK redundan (diklarifikasi di atas) — dua entitas berbeda meski penamaan mirip |
| `flag_grandmaster_met` vs `state_rel_grandmaster` | TIDAK redundan — satu adalah boolean pertemuan pertama (gating), satu adalah nilai kontinu (kualitas hubungan) |
| `belief_protagonist_may_be_cause` vs `flag_memory_gate_a03_seen` | TIDAK redundan — satu adalah keyakinan mutable, satu adalah penanda peristiwa permanen yang MEMICU keyakinan tersebut |

**Hasil audit redundansi:** tidak ditemukan state benar-benar redundan dalam katalog 70 state (setelah dikurangi false-positive dan koreksi `state_rep_tianxu_orthodox`) yang terkumpul dari sebelas file — total state_id valid: **70** (71 hasil regex awal, dikurangi 1 karena `state_rep_tianxu_orthodox` sekarang sudah dikoreksi menjadi identik dengan `state_rep_tianxu` yang sudah terhitung).

---

## Design Gap & Recommendation Ringkasan Fase Ini

1. **Koreksi `state_rep_tianxu_orthodox`** — ditemukan dan diperbaiki di fase ini, dicatat terbuka di pembuka dokumen
2. **Penamaan `state_rel_master` vs `state_rel_mentor` berpotensi membingungkan** — direkomendasikan penamaan lebih jelas saat implementasi, tidak diubah di dokumen ini untuk menghindari breaking change
3. **Nilai numerik threshold** (masih `[DESIGN GAP]` sejak Phase 8) — katalog ini mengonfirmasi SEMUA state relationship/reputation menggunakan tipe `integer` tanpa rentang atau threshold spesifik didefinisikan di manapun. **Ini adalah gap paling signifikan yang tersisa** untuk implementasi — direkomendasikan menjadi prioritas pertama saat data engine mulai dibangun dari dokumen ini

---

**File berikutnya:** `14-content-dependency-graph.md` — Content Dependency Graph (Phase 18), akan memvisualisasikan Quest→State→Branch→Quest→Convergence→Future Event→Ending sebagai satu graph konseptual utuh, dan secara khusus mencari dead-end, unreachable content, circular dependency, dan gap lain yang mungkin masih lolos dari audit-audit lokal yang sudah dilakukan per-fase.
