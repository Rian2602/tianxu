# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 10. Consequence Matrix & Convergence Matrix

**Status:** DRAFT — Phase 11-12 of 18 (digabung karena saling merujuk erat)
**Depends on:** seluruh Quest Graph, Character Bible, Faction Bible, Memory Bible, World Event Bible
**Koreksi struktural sebelum fase ini dimulai:** audit menemukan `convergence_a05_c03_01` dipakai untuk DUA titik berbeda (convergence Mountain Gate Outcome di `quest_a05_c02_002`, dan klaim "tidak ada convergence" di Found Family Crisis `quest_a05_c03_003`). Diperbaiki di `03b-quest-graph-arc3-7.md`: ID Mountain Gate diganti `convergence_a05_c02_01`. Ditandai terbuka di sini, bukan disembunyikan.

---

## BAGIAN A — CONSEQUENCE MATRIX

**Prinsip wajib:** setiap major choice memiliki Immediate → Short-term → Mid-term → Long-term → Ending consequence. Consequence TIDAK boleh berupa reward semata (instruksi eksplisit).

### Consequence Matrix: Pavilion Selection (Arc I)

| Tahap | Konsekuensi |
|---|---|
| **Immediate** | `state_pavilion` di-set permanen; guru pavilion terpilih menjadi recurring NPC |
| **Short-term** | Curriculum Arc I-II dimodifikasi; found family bonding sedikit dipengaruhi kedekatan pavilion |
| **Mid-term** | Akses ke beberapa clue/dialogue Arc III-IV termodifikasi (`[DESIGN GAP]` detail spesifik clue mana) |
| **Long-term** | Modifier faction relationship tidak langsung Arc IV+ (dicatat Quest Graph, belum granular) |
| **Ending** | Salah satu major_choice_conditions untuk Ending Matrix (Phase 13) — MSB eksplisit menyatakan pavilion memengaruhi "beberapa kemungkinan pada ending" |

### Consequence Matrix: First Major Choice — Obey/Investigate/Confront (Arc II, Chapter 2.3)

| Tahap | Obey | Investigate | Confront |
|---|---|---|---|
| **Immediate** | `state_rel_master +` | `flag_archive_suspicious = true` | `state_rep_tianxu -` |
| **Short-term** | Guru lebih percaya kelompok | Akses investigasi mandiri tambahan | Sebagian murid mulai bersimpati; guru waspada |
| **Mid-term** | Akses Forbidden Archive dibantu guru (`dialog_a02_d014` versi Obey) | Akses Forbidden Archive mandiri, lebih cepat | Akses via NPC simpatisan, berisiko lebih tinggi |
| **Long-term** | Modifier positif `state_rep_tianxu`; sedikit lebih lambat mendapat kebenaran penuh karena bergantung jalur institusional | Jalur paling efisien menuju kebenaran, tapi tanpa dukungan institusional formal | Modifier negatif `state_rep_tianxu`; bibit relationship dengan Reformists/Liberation |
| **Ending** | Berkontribusi pada kualitas ending Unbroken Heaven (jalur institusional konsisten) | Netral terhadap ending manapun — jalur paling "murni investigatif" | Berkontribusi pada kemungkinan ending Mortal Dawn (jalur anti-institusional sejak awal) |

**Catatan kepatuhan instruksi:** matrix ini secara sengaja TIDAK menunjukkan reward murni pada salah satu opsi — ketiganya punya trade-off nyata (Obey = percaya tapi lambat; Investigate = efisien tapi tanpa dukungan; Confront = cepat tapi berisiko dan mengorbankan reputasi).

### Consequence Matrix: Major Choice Arc III — Deny/Accept Cautious/Seek Truth (Chapter 3.4)

| Tahap | Deny | Accept Cautious | Seek Truth |
|---|---|---|---|
| **Immediate** | `state_identity_stance = deny` | `state_identity_stance = accept_cautious` | `state_identity_stance = seek_truth`, `state_rel_mei_ruo +` (lebih besar) |
| **Short-term** | Found family reaksi campuran (dukungan vs kekhawatiran Mei Ruo) | Reaksi paling netral | Mei Ruo relationship menguat signifikan |
| **Mid-term** | Dialogue investigatif Arc IV-V lebih defensif/tertutup | Akses seimbang ke dialogue investigatif | Optional investigation quest tambahan Arc IV-V terbuka |
| **Long-term** | Modifier tone Final Confrontation — "Aku bukan kau" terasa sebagai penegasan yang diperjuangkan | Modifier netral — kesimpulan logis dari sikap konsisten | Akses informasi paling lengkap sebelum Final Confrontation |
| **Ending** | Tidak secara langsung menggerbang ending manapun, tapi memengaruhi TONE Chapter 7.2 | Sama — memengaruhi tone, bukan akses | Berkontribusi pada prasyarat Hidden Resolution (investigasi kehidupan pertama lebih mudah terpenuhi) |

### Consequence Matrix: Mountain Gate Incident Outcome (Arc V, Chapter 5.2)

| Tahap | Berhasil (`flag_mountain_gate_changed`) | Gagal (`flag_mountain_gate_repeated`) |
|---|---|---|
| **Immediate** | Dunia bereaksi dengan harapan hati-hati | Dunia bereaksi dengan duka/ketakutan |
| **Short-term** | Found family sedikit lebih stabil menghadapi Chapter 5.3 | Urgensi Found Family Crisis diperkuat — kemungkinan lebih banyak anggota memilih posisi radikal |
| **Mid-term** | Momentum wacana Liberation Faction lebih lemah | Liberation Faction mendapat momentum wacana signifikan ("cultivation menyebabkan ini") |
| **Long-term** | Tone dunia Arc VI-VII sedikit lebih optimis | Tone dunia Arc VI-VII sedikit lebih berat/waspada |
| **Ending** | World_state_condition yang berkontribusi pada epilogue lebih "terselamatkan" di ending manapun | World_state_condition yang berkontribusi pada epilogue lebih "menanggung kehilangan" di ending manapun |

**Catatan kepatuhan instruksi:** MSB eksplisit menyatakan hasil ini BUKAN gate ending (ending ditentukan `quest_a07_c03_003` terpisah) — matrix ini mengonfirmasi bahwa outcome Mountain Gate memengaruhi KUALITAS epilogue, bukan AKSES ke ending tertentu, konsisten dengan prinsip ENDING ACCESS vs ENDING QUALITY yang akan diformalkan penuh Phase 13.

### Consequence Matrix: Found Family Crisis (Arc V, Chapter 5.3)

| Tahap | Konsekuensi |
|---|---|
| **Immediate** | `state_lin_yue_status`, `state_shen_luo_status`, `state_mei_ruo_status`, `state_gu_han_status` masing-masing ditentukan berdasarkan akumulasi relationship |
| **Short-term** | Konfigurasi found family final memengaruhi siapa yang hadir/tidak hadir di quest-quest Arc VI |
| **Mid-term** | Anggota yang berpisah berpotensi bergabung faksi tertentu (Gu Han → Liberation paling kuat; lainnya `[DESIGN GAP]`) |
| **Long-term** | Menentukan siapa yang hadir di Chapter 7.1 (The Last Night) dan dengan tone seperti apa (matrix dialog sudah diformalkan Phase 8) |
| **Ending** | Character end state final tiap anggota found family (detail penuh Phase 13) |

**Catatan kepatuhan instruksi paling penting di seluruh matrix ini:** Found Family Crisis adalah SATU-SATUNYA major choice dalam dokumen yang consequence-nya TIDAK memiliki "opsi aman" — MSB eksplisit menyatakan "Tidak semua karakter harus tetap menjadi sahabat," dan matrix ini tidak menyembunyikan bahwa kehilangan permanen adalah outcome valid, bukan failure state yang harus dihindari.

### Consequence Matrix: Final Choice Before Endgame — Preserve/Destroy/Transform/Sacrifice (Arc VI, Chapter 6.4)

| Tahap | Preserve | Destroy | Transform | Sacrifice |
|---|---|---|---|---|
| **Immediate** | `state_final_principle = preserve` | `= destroy` | `= transform` | `= sacrifice` |
| **Short-term** | Found family yang selaras Orthodox mendukung kuat | Found family yang selaras Liberation mendukung kuat | Found family yang selaras Reformists mendukung kuat | Reaksi paling emosional — MSB Chapter 5.3 branch Lin Yue eksplisit mencatat "Penolakan emosional keras" untuk prinsip ini |
| **Mid-term** | Tone Chapter 7.1 condong institusional-defensif | Tone Chapter 7.1 condong konfrontatif | Tone Chapter 7.1 condong diplomatis-mencari-jalan-tengah | Tone Chapter 7.1 condong elegis/berat |
| **Long-term** | Dominant path menuju ending Unbroken Heaven (bukan gate mutlak) | Dominant path menuju ending Mortal Dawn | Dominant path menuju ending New Heaven | Dominant path menuju ending Nameless Guardian |
| **Ending** | **PENTING (ditegaskan ulang dari Quest Graph):** ini adalah WEIGHT/MODIFIER, bukan hard gate — kombinasi dengan seluruh state lain yang menentukan ending final, sesuai MSB eksplisit "tidak langsung menentukan ending" | Sama | Sama | Sama |

---

## BAGIAN B — CONVERGENCE MATRIX

**Prinsip wajib:** convergence TIDAK berarti branch menjadi identik. Story event dapat sama, tapi konteks/relationship/faction state/memory/knowledge pemain tetap berbeda. Discarded_information harus dicatat eksplisit — bukan berarti "dihapus," melainkan informasi yang TIDAK lagi relevan untuk gating konten berikutnya meski tetap ada di riwayat pemain.

### `convergence_a01_c_end_01`

| Field | Value |
|---|---|
| `convergence_id` | `convergence_a01_c_end_01` |
| `incoming_branches` | `branch_a01_c03_b01` (empat pilihan pavilion) |
| `shared_story_event` | Arc I berakhir di titik naratif yang sama — symbol muncul, found family terbentuk, `flag_memory_awareness = true` |
| `preserved_state` | `state_pavilion` (permanen, dibawa terus sebagai modifier — TIDAK pernah "hilang" meski convergence terjadi) |
| `discarded_information` | Tidak ada — ini adalah convergence paling "ringan," karena pavilion bukan choice yang menyembunyikan informasi dari jalur lain, hanya memodifikasi akses/curriculum |
| `retained_relationship_effect` | Modifier kecil found family berdasarkan kedekatan pavilion (dicatat Quest Graph) |
| `retained_faction_effect` | Tidak ada langsung di titik ini — baru muncul Arc IV+ |
| `retained_world_effect` | Tidak ada |
| `future_payoff` | Kemungkinan ending tertentu (Phase 13) |

### `convergence_a02_c04_01`

| Field | Value |
|---|---|
| `convergence_id` | `convergence_a02_c04_01` |
| `incoming_branches` | `branch_a02_c03_b01` (Obey), `branch_a02_c03_b02` (Investigate), `branch_a02_c03_b03` (Confront) |
| `shared_story_event` | Ketiga branch bertemu di penemuan Hidden Cave dan First Artifact (`quest_a02_c04_007`, `quest_a02_c04_008`) |
| `preserved_state` | `state_rel_master`, `flag_archive_suspicious`, `state_rep_tianxu` — SALAH SATU dari ketiganya aktif tergantung branch yang diambil, dan TETAP aktif melewati convergence ini |
| `discarded_information` | Cara SPESIFIK found family membicarakan keputusan Chapter 2.3 (dialog `dialog_a02_d020`) tidak lagi menjadi prerequisite konten berikutnya setelah convergence ini — tapi TETAP tercatat sebagai bagian riwayat, bukan dihapus dari memori naratif pemain |
| `retained_relationship_effect` | `state_rel_master` (jika Obey) dibawa terus sebagai modifier Arc IV dialogue |
| `retained_faction_effect` | `state_rep_tianxu` (jika Confront) dibawa terus, memengaruhi Faction Bible reactions |
| `retained_world_effect` | `flag_archive_suspicious` (jika Investigate) dibawa terus sebagai akses Arc IV |
| `future_payoff` | Dialogue Arc IV bervariasi (`dialog_a02_d014`, sudah diformalkan Phase 8) |

### `convergence_a05_c02_01` (Sebelumnya Salah Diberi Label — Dikoreksi Fase Ini)

| Field | Value |
|---|---|
| `convergence_id` | `convergence_a05_c02_01` |
| `incoming_branches` | `branch_a05_c02_b01` (Mountain Gate Outcome — berhasil/gagal) |
| `shared_story_event` | Kedua outcome bertemu di quest yang sama berikutnya (`quest_a05_c03_003`, Found Family Crisis) — insiden Mountain Gate, apa pun hasilnya, mengarah ke krisis kelompok yang sama |
| `preserved_state` | `flag_mountain_gate_changed` ATAU `flag_mountain_gate_repeated` — permanen, memengaruhi tone Found Family Crisis tapi tidak menentukan hasilnya secara langsung |
| `discarded_information` | Detail MEKANIS spesifik bagaimana insiden ditangani (build/strategi pemain) tidak lagi relevan sebagai prerequisite — hanya OUTCOME biner yang dibawa terus |
| `retained_relationship_effect` | Kemungkinan penurunan `state_rel_*` jika gagal (dicatat Quest Graph sebagai gap detail) |
| `retained_faction_effect` | Momentum Liberation jika gagal |
| `retained_world_effect` | Tone dunia Arc VI-VII (dicatat Consequence Matrix di atas) |
| `future_payoff` | World_state_condition Ending Matrix (Phase 13) |

### `convergence_a03_c05_01`

| Field | Value |
|---|---|
| `convergence_id` | `convergence_a03_c05_01` |
| `incoming_branches` | `branch_a03_c04_b01` (Deny), `branch_a03_c04_b02` (Accept Cautious), `branch_a03_c04_b03` (Seek Truth) |
| `shared_story_event` | Ketiganya bertemu di memory gerbang lengkap (`quest_a03_c05_005`) — memory ini muncul TERLEPAS dari sikap yang dipilih |
| `preserved_state` | `state_identity_stance` — permanen, salah satu dari tiga nilai tetap aktif melewati convergence |
| `discarded_information` | Detail SPESIFIK percakapan individual dengan tiap anggota found family (jika pemain memilih opsional) tidak menjadi prerequisite konten berikutnya — tapi relationship value yang terbentuk dari percakapan itu TETAP dibawa |
| `retained_relationship_effect` | Cara found family memperlakukan protagonis sejak titik ini berbeda permanen tergantung stance (dicatat eksplisit di Quest Graph sebagai "PENTING") |
| `retained_faction_effect` | Tidak ada langsung |
| `retained_world_effect` | Tidak ada |
| `future_payoff` | Modifier dialog Chapter 7.2 (`dialog_a07_d015`, tiga versi sudah diformalkan Phase 8) — payoff PALING JAUH dari seluruh convergence dalam dokumen (Arc III → Arc VII) |

### `convergence_a06_c04_01`

| Field | Value |
|---|---|
| `convergence_id` | `convergence_a06_c04_01` |
| `incoming_branches` | `branch_a06_c04_b01` (Preserve), `b02` (Destroy), `b03` (Transform), `b04` (Sacrifice) |
| `shared_story_event` | Keempat prinsip menuju Chapter 7.1 (The Last Night) yang sama |
| `preserved_state` | `state_final_principle` — permanen, salah satu dari empat nilai dibawa sebagai WEIGHT (bukan hard gate, ditegaskan berulang) menuju Ending Matrix |
| `discarded_information` | Detail spesifik BAGAIMANA percakapan dengan Mentor berjalan (jika ada variasi dialog opsional) tidak menjadi prerequisite — tapi `state_rel_mentor` yang terbentuk tetap dibawa |
| `retained_relationship_effect` | Found family yang selaras/tidak selaras secara ideologis dengan prinsip terpilih (dicatat Consequence Matrix di atas) |
| `retained_faction_effect` | Signifikan — tiap prinsip selaras faksi berbeda (dicatat Faction Bible) |
| `retained_world_effect` | Tone Chapter 7.1 (dicatat Consequence Matrix) |
| `future_payoff` | Modifier terbesar untuk Ending Matrix Phase 13 — TAPI bukan satu-satunya faktor, ditegaskan berulang di seluruh dokumen untuk menghindari kesalahan implementasi sebagai simple 4-way branch ending |

### Convergence yang SENGAJA Tidak Ada: Found Family Crisis (`quest_a05_c03_003`)

**Dicatat eksplisit sebagai bagian dari Convergence Matrix, meski TIDAK memiliki convergence_id** — konsisten dengan prinsip bahwa tidak semua branch harus (atau boleh) convergence. MSB eksplisit: "Tidak semua karakter harus tetap menjadi sahabat." Memaksakan convergence formal di titik ini (mis. "found family selalu bertemu lagi di titik X, hanya beda dialog") akan MENGKHIANATI prinsip ini — konfigurasi found family yang berbeda benar-benar membawa konsekuensi permanen berbeda hingga ending, bukan sekadar variasi kosmetik yang "convergence" tersembunyi di baliknya.

---

## Convergence Coverage Verification

| convergence_id | Terformalkan Fase Ini | Catatan |
|---|---|---|
| `convergence_a01_c_end_01` | ✅ | |
| `convergence_a02_c04_01` | ✅ | |
| `convergence_a05_c02_01` | ✅ | Dikoreksi dari `convergence_a05_c03_01` yang salah label sebelum fase ini dimulai |
| `convergence_a03_c05_01` | ✅ | |
| `convergence_a06_c04_01` | ✅ | |
| Found Family Crisis | ✅ (dicatat sebagai "sengaja tidak ada") | Bukan gap — keputusan desain eksplisit |

**Hasil verifikasi:** enam dari enam titik dalam Quest Graph yang memerlukan keputusan convergence (baik formal maupun "sengaja tidak formal") sudah tercakup. Tidak ada convergence_id yang disebut di Quest Graph tapi tidak terformalkan di sini.

---

## Design Gap & Recommendation Ringkasan Fase Ini

1. **Koreksi struktural:** `convergence_a05_c03_01` yang salah dipakai untuk dua titik berbeda diperbaiki menjadi `convergence_a05_c02_01` di file Quest Graph — dicatat terbuka di awal dokumen ini
2. **Detail granular clue/dialogue yang dimodifikasi pavilion** (Consequence Matrix Pavilion Selection) — masih `[DESIGN GAP]`, memerlukan pass tambahan saat dialogue production penuh dimulai
3. **Detail anggota found family mana yang bergabung faksi apa jika berpisah** (selain Gu Han→Liberation yang sudah kuat) — masih `[DESIGN GAP]`, direkomendasikan diselesaikan bersamaan dengan Phase 13 (Ending Matrix) karena kedua hal saling terkait erat

---

**File berikutnya:** `11-ending-matrix.md` — Ending Matrix untuk kelima ending, akan secara eksplisit menggunakan seluruh Consequence Matrix dan Convergence Matrix di atas sebagai input kondisi, dan memformalkan pembedaan ENDING ACCESS vs ENDING QUALITY vs CHARACTER OUTCOME yang sudah berulang kali dirujuk sepanjang dokumen.
