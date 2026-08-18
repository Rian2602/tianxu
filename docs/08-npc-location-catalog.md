# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 08. NPC & Location Catalog

**Status:** DRAFT — Phase 9 of 18
**Depends on:** seluruh file sebelumnya — fase ini menutup mayoritas `[DESIGN GAP]` lokasi dan NPC pendukung yang sengaja ditunda sejak Phase 3
**Prinsip wajib:** NPC dibedakan enam kategori (Main/Supporting/Recurring/Quest/Faction/Ambient). Lokasi wajib punya fungsi naratif atau gameplay — tidak ada lokasi kosong sekadar dekorasi.

---

## Bagian A — Pavilion Roster (Mengisi Gap Paling Mendasar)

**Catatan produksi:** roster berikut adalah REKOMENDASI DESAIN untuk mengisi gap yang sudah dicatat sejak Phase 2 — MSB menyatakan sistem pavilion ada ("filosofi berbeda mengenai cultivation") tapi tidak menyebut pavilion konkret. Empat pavilion di bawah dirancang untuk mencerminkan empat pendekatan berbeda terhadap tema sentral MSB (Identity, Trust, Truth, Choice), BUKAN empat elemen generik (api/air/tanah/udara) yang tidak terhubung tematis dengan cerita.

| Pavilion | Filosofi Cultivation | Resonansi Tematik |
|---|---|---|
| **Pavilion Wuxin (Empty Heart)** | Cultivation melalui pelepasan ego — kekuatan datang dari melepaskan keterikatan, bukan mengumpulkannya | Resonan dengan tema Identity (Arc III) — murid pavilion ini punya kerangka filosofis siap pakai untuk memahami krisis identitas protagonis, baik mendukung maupun menantang |
| **Pavilion Jianxin (Sword Heart)** | Cultivation melalui disiplin dan ketepatan — kekuatan sebagai hasil kerja keras yang dapat diukur, resonan dengan worldview awal Shen Luo | Resonan dengan tema Trust (Arc II) — filosofi merit-based menciptakan pertanyaan alami tentang siapa yang "layak" dipercaya |
| **Pavilion Yanzhi (Inkstone Heart)** | Cultivation melalui pengetahuan dan pencatatan — kekuatan berasal dari memahami prinsip di baliknya, bukan sekadar praktik | Resonan dengan tema Truth (Arc IV) dan minat Mei Ruo — murid pavilion ini secara alami condong ke investigasi historis |
| **Pavilion Liuguang (Flowing Light)** | Cultivation melalui adaptasi — tidak ada satu jalan tetap, kekuatan datang dari kemampuan berubah sesuai keadaan | Resonan dengan tema Choice (Arc VII) — filosofi paling terbuka terhadap gagasan bahwa jalan hidup dapat dipilih ulang |

**Guru tiap pavilion** (Ambient/Recurring NPC, detail penuh di Bagian C):
- Pavilion Wuxin: `npc_teacher_wuxin`
- Pavilion Jianxin: `npc_teacher_jianxin`
- Pavilion Yanzhi: `npc_teacher_yanzhi`
- Pavilion Liuguang: `npc_teacher_liuguang`

**Implikasi untuk state_pavilion (mengisi gap Quest Graph `branch_a01_c03_b01`):** `state_pavilion` sekarang punya empat nilai enum konkret: `wuxin`, `jianxin`, `yanzhi`, `liuguang`. Efek permanen tiap pilihan terhadap curriculum/dialogue tetap **[DESIGN GAP]** di level detail granular (dialog spesifik mana yang berubah), tapi kerangka filosofisnya sudah cukup untuk tim dialogue writer mulai bekerja tanpa menebak dari nol.

**Rekomendasi afiliasi ideologis found family terhadap pavilion** (opsional, bukan wajib — pemain tetap bebas memilih pavilion manapun terlepas dari NPC found family):
- Shen Luo → kemungkinan besar Jianxin (merit-based, sesuai worldview awalnya di Character Bible)
- Mei Ruo → kemungkinan besar Yanzhi (minat pada sejarah/catatan, sesuai Character Bible)
- Lin Yue dan Gu Han → tidak direkomendasikan terikat satu pavilion spesifik, untuk menjaga fleksibilitas found family bonding terlepas dari pilihan pemain

---

## Bagian B — Location Bible

### `loc_tianxu_approach_road`
| Field | Value |
|---|---|
| `location_id` | `loc_tianxu_approach_road` |
| `name` | Jalan Pendakian Tian Xu |
| `purpose` | Membangun skala dan misteri Tian Xu sebelum protagonis memasukinya — first impression |
| `first_appearance` | `quest_a01_c01_001` |
| `arc_usage` | Arc I saja |
| `chapter_usage` | Chapter 1.1 |
| `connected_locations` | `loc_tianxu_gate` |
| `important_npcs` | Tidak ada — lokasi transisi murni |
| `available_quests` | `quest_a01_c01_001` |
| `hidden_area` | Tidak ada |
| `secrets` | Tidak ada |
| `memory_triggers` | `memory_a01_m01` (dream sequence terjadi "dalam perjalanan," bukan di lokasi fisik — dicatat di sini untuk kelengkapan referensi) |
| `world_events` | Tidak ada |
| `faction_control` | Netral/tidak berlaku |
| `state_variations` | Tidak ada — lokasi ini hanya dikunjungi sekali |
| `future_payoffs` | Tidak ada |

### `loc_tianxu_gate`
| Field | Value |
|---|---|
| `location_id` | `loc_tianxu_gate` |
| `name` | Gerbang Utama Tian Xu |
| `purpose` | Titik masuk resmi, lokasi aptitude test dan registrasi |
| `first_appearance` | `quest_a01_c01_001` |
| `arc_usage` | Arc I (utama), kemungkinan muncul kembali sebagai lokasi transisi Arc VII |
| `chapter_usage` | Chapter 1.1 |
| `connected_locations` | `loc_tianxu_approach_road`, area umum akademi (tidak diberi ID terpisah — generik) |
| `important_npcs` | Pemeriksa aptitude (lihat Bagian C, `npc_aptitude_examiner`) |
| `available_quests` | `quest_a01_c01_001`, `quest_a01_c01_002` |
| `hidden_area` | Tidak ada |
| `secrets` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `world_events` | Berpotensi menunjukkan `world_event_a05_spiritual_collapse` secara visual di Arc VII (gerbang yang dulu megah kini menunjukkan tanda keretakan) |
| `faction_control` | Tian Xu Orthodox (implisit, ini adalah wilayah inti institusi) |
| `state_variations` | Kondisi visual berubah di Chapter 7.1 (crisis state) |
| `future_payoffs` | Kontras visual Arc I vs Arc VII (megah vs krisis) sebagai world-building non-verbal |

### `loc_hidden_cave`
| Field | Value |
|---|---|
| `location_id` | `loc_hidden_cave` |
| `name` | Gua Tersembunyi (Outer Region) |
| `purpose` | Lokasi convergence Arc II, tempat artefak pertama ditemukan |
| `first_appearance` | `quest_a02_c04_007` |
| `arc_usage` | Arc II saja |
| `chapter_usage` | Chapter 2.4 |
| `connected_locations` | `loc_outer_region` |
| `important_npcs` | Tidak ada NPC hadir — found family saja |
| `available_quests` | `quest_a02_c04_007`, `quest_a02_c04_008` |
| `hidden_area` | Ruang dalam gua tempat artefak berada — tersembunyi dari akses umum |
| `secrets` | `item_artifact_01` |
| `memory_triggers` | `memory_a02_m01` |
| `world_events` | Tidak ada |
| `faction_control` | Tidak dikuasai faksi manapun — di luar wilayah kontrol formal |
| `state_variations` | Tidak ada — dikunjungi sekali di titik naratif tetap |
| `future_payoffs` | Tidak ada langsung — fungsinya selesai setelah Arc II |

### `loc_outer_region`
| Field | Value |
|---|---|
| `location_id` | `loc_outer_region` |
| `name` | Wilayah Luar (nama generik — direkomendasikan diperhalus dengan nama lebih spesifik oleh tim world-building jika diperlukan, mis. "Dataran Reyan" atau serupa; `[DESIGN GAP — nama puitis akhir]`) |
| `purpose` | Area eksplorasi pertama di luar akademi, tempat kelompok mendapat misi lapangan pertama |
| `first_appearance` | `quest_a02_c02_003` |
| `arc_usage` | Arc II (utama), berpotensi muncul kembali Arc V sebagai salah satu wilayah terdampak Spiritual Collapse |
| `chapter_usage` | Chapter 2.2 |
| `connected_locations` | `loc_hidden_cave`, area akademi |
| `important_npcs` | Murid senior hilang (lihat Bagian C, `npc_missing_disciple`) |
| `available_quests` | `quest_a02_c02_003`, `quest_a02_c02_004`, `quest_a02_c02_005` |
| `hidden_area` | Tempat persembunyian murid hilang |
| `secrets` | `item_note_cycle_begins_again` |
| `memory_triggers` | Tidak ada langsung |
| `world_events` | Kandidat kuat untuk salah satu wilayah terdampak `world_event_a05_spiritual_collapse` (memberi kontinuitas — pemain mengenali wilayah ini kembali dalam kondisi rusak, memperkuat resonansi emosional dibanding wilayah baru yang tidak dikenal) |
| `faction_control` | Tidak dikuasai penuh oleh Tian Xu — wilayah abu-abu, berpotensi jadi tempat aktivitas Liberation Faction |
| `state_variations` | Normal (Arc II) vs Terdampak Spiritual Collapse (Arc V, jika direkomendasikan di atas diterima) |
| `future_payoffs` | Kontinuitas visual/emosional Arc II→V jika direkomendasikan digunakan kembali |

### `loc_hidden_room_mural`
| Field | Value |
|---|---|
| `location_id` | `loc_hidden_room_mural` |
| `name` | Ruang Mural Tersembunyi |
| `purpose` | Titik masuk Memory Investigation System penuh, pengenalan genre shift Arc III |
| `first_appearance` | `quest_a03_c01_001` |
| `arc_usage` | Arc III saja |
| `chapter_usage` | Chapter 3.1 |
| `connected_locations` | Area akademi (tidak tercatat di peta resmi — bagian dari signifikansinya) |
| `important_npcs` | `npc_mei_ruo` |
| `available_quests` | `quest_a03_c01_001` |
| `hidden_area` | Ruang ini SENDIRI adalah hidden area relatif terhadap peta akademi resmi |
| `secrets` | Mural dengan bagian yang sengaja dihancurkan |
| `memory_triggers` | Tidak ada memory_id langsung, tapi memicu analisis naratif signifikan |
| `world_events` | Tidak ada |
| `faction_control` | Ambigu — jika ruang ini tidak tercatat resmi, kemungkinan berada di luar kontrol faksi manapun secara formal, meski secara fisik berada dalam wilayah Tian Xu Orthodox |
| `state_variations` | Tidak ada |
| `future_payoffs` | Foreshadowing untuk Forbidden Archive Arc IV (skala lebih besar dari kebenaran yang disembunyikan) |

### `loc_forbidden_archive`
| Field | Value |
|---|---|
| `location_id` | `loc_forbidden_archive` |
| `name` | Arsip Terlarang |
| `purpose` | Lokasi revelation institusional terbesar Arc IV — tiga versi sejarah |
| `first_appearance` | `quest_a04_c01_001` |
| `arc_usage` | Arc IV (utama) |
| `chapter_usage` | Chapter 4.1, 4.2 |
| `connected_locations` | `loc_tianxu_deepest_chamber` (secara tematis terhubung — kedua lokasi adalah lapisan berbeda dari kebenaran tersembunyi Tian Xu, meski tidak harus terhubung secara fisik/geografis) |
| `important_npcs` | `npc_mei_ruo` |
| `available_quests` | `quest_a04_c01_001`, `quest_a04_c02_002` |
| `hidden_area` | Bagian terdalam tempat Version III ditemukan — akses berlapis (Version I/II di area luar, Version III di area dalam) |
| `secrets` | Tiga versi sejarah, dengan Version III sebagai puncak |
| `memory_triggers` | Tidak ada memory_id langsung — ini adalah investigation quest, bukan memory quest (konsisten dengan catatan Phase 7) |
| `world_events` | Tidak ada |
| `faction_control` | Tian Xu Orthodox, tapi dengan akses dibatasi — bahkan di dalam faksi ini, akses berlapis (biasa vs level kepemimpinan) |
| `state_variations` | Akses dimodifikasi berdasarkan branch Chapter 2.3 (dicatat di Dialogue Bible `dialog_a02_d014`) |
| `future_payoffs` | Menjadi rujukan penting untuk memahami `flag_tianxu_feeds_segel_known` di Chapter 4.4 |

### `loc_grandmaster_chamber`
| Field | Value |
|---|---|
| `location_id` | `loc_grandmaster_chamber` |
| `name` | Ruang Grandmaster |
| `purpose` | Lokasi konfrontasi ideologis Chapter 4.3 |
| `first_appearance` | `quest_a04_c03_003` |
| `arc_usage` | Arc IV (utama), kemungkinan Arc VII (The Last Night) |
| `chapter_usage` | Chapter 4.3 |
| `connected_locations` | Area inti kepemimpinan Tian Xu (tidak diberi ID terpisah) |
| `important_npcs` | `npc_grandmaster` |
| `available_quests` | `quest_a04_c03_003` |
| `hidden_area` | Tidak ada |
| `secrets` | Tidak ada objek rahasia — "rahasia" di ruang ini bersifat verbal (pengakuan Grandmaster), bukan objek tersembunyi |
| `memory_triggers` | Tidak ada |
| `world_events` | Tidak ada |
| `faction_control` | Tian Xu Orthodox (pusat kepemimpinan) |
| `state_variations` | Tidak ada di Arc IV; berpotensi berubah drastis (crisis state) jika muncul kembali Arc VII |
| `future_payoffs` | Jika muncul kembali Arc VII, kontras formal (Arc IV) vs personal/krisis (Arc VII) memperkuat arc Grandmaster |

### `loc_tianxu_deepest_chamber`
| Field | Value |
|---|---|
| `location_id` | `loc_tianxu_deepest_chamber` |
| `name` | Ruang Terdalam Tian Xu |
| `purpose` | Lokasi revelation terbesar Arc IV (formation raksasa) DAN lokasi The Gate historis (Arc VI) DAN lokasi Final Confrontation (Arc VII) — satu lokasi dengan signifikansi berlapis di tiga Arc berbeda |
| `first_appearance` | `quest_a04_c04_004` |
| `arc_usage` | Arc IV, VI (sebagai `loc_the_gate` — lihat catatan konsolidasi di bawah), VII |
| `chapter_usage` | Chapter 4.4, 6.3, 7.2 |
| `connected_locations` | `loc_forbidden_archive` (tematis) |
| `important_npcs` | Tidak ada di Arc IV (discovery murni); Jiang Yan imprint di Arc VII |
| `available_quests` | `quest_a04_c04_004`, `quest_a06_c03_003` (via memory), `quest_a07_c02_002` |
| `hidden_area` | Ruang di BAWAH ruang ini sendiri — tempat Final Confrontation Arc VII terjadi, secara eksplisit dicatat Quest Graph sebagai "di bawah `loc_tianxu_deepest_chamber`" |
| `secrets` | Formation raksasa; identitas penuh sebagai The Gate |
| `memory_triggers` | `memory_a06_m01` (via lokasi yang sama secara historis) |
| `world_events` | Pusat dari `flag_tianxu_feeds_segel_known`; berubah signifikan di Chapter 7.1 ("formation mulai gagal") |
| `faction_control` | Tian Xu Orthodox secara formal, tapi maknanya melampaui kontrol faksi manapun — ini adalah pusat gravitasi seluruh cerita |
| `state_variations` | Normal-tersembunyi (Arc IV) → Historis via memory (Arc VI) → Crisis/klimaks (Arc VII) |
| `future_payoffs` | Lokasi dengan future_payoffs TERBESAR dalam seluruh Location Bible — menyatukan tiga Arc berbeda di satu tempat fisik yang sama |

**Catatan konsolidasi penting:** `loc_the_gate` yang dirujuk di beberapa file sebelumnya (Quest Graph, Memory Bible) DIKONSOLIDASIKAN menjadi identik secara lokasi dengan `loc_tianxu_deepest_chamber` — ini BUKAN dua lokasi berbeda, melainkan nama yang sama merujuk konteks temporal berbeda (Arc IV mengenalnya sebagai "ruang terdalam Tian Xu" tanpa tahu sejarahnya; Arc VI mengungkap bahwa tempat yang sama adalah The Gate historis). Keputusan ini SENGAJA dibuat di fase ini untuk menghindari duplikasi lokasi yang tidak perlu — direkomendasikan sebagai keputusan final, bukan gap terbuka, karena memperkuat tema "kebenaran yang sudah ada di depan mata sejak awal."

### `loc_the_gate` — DEPRECATED, lihat `loc_tianxu_deepest_chamber`
Dicatat di sini hanya untuk keperluan cross-reference — semua penggunaan `loc_the_gate` di file-file sebelumnya harus dibaca sebagai `loc_tianxu_deepest_chamber` dalam konteks historis (Arc VI).

### `loc_mountain_gate`
| Field | Value |
|---|---|
| `location_id` | `loc_mountain_gate` |
| `name` | Gerbang Gunung |
| `purpose` | Lokasi Repeating Event terbesar — Mountain Gate Incident |
| `first_appearance` | `quest_a05_c02_002` |
| `arc_usage` | Arc V saja (secara langsung); dirujuk sebagai memori/sejarah di Arc VI-VII |
| `chapter_usage` | Chapter 5.2 |
| `connected_locations` | Salah satu wilayah terdampak `world_event_a05_spiritual_collapse` |
| `important_npcs` | NPC yang terancam (lihat Bagian C, `npc_mountain_gate_villager` — rekomendasi) |
| `available_quests` | `quest_a05_c02_002` |
| `hidden_area` | Tidak ada |
| `secrets` | Tidak ada objek — signifikansinya adalah PERISTIWA, bukan penemuan |
| `memory_triggers` | Tidak ada langsung, tapi merupakan pengulangan dari peristiwa kehidupan pertama yang sama |
| `world_events` | Pusat dari `flag_mountain_gate_changed` / `flag_mountain_gate_repeated` |
| `faction_control` | Di luar kontrol Tian Xu — kemungkinan wilayah pemukiman biasa, memberi stake manusiawi yang berbeda dari lokasi-lokasi institusional lain |
| `state_variations` | Sebelum insiden (normal) → Selama insiden (krisis real-time) → Setelah insiden (berubah/selamat vs hancur, tergantung outcome) |
| `future_payoffs` | Hasil di lokasi ini menjadi salah satu world_state_conditions Ending Matrix (Phase 13) |

### `loc_tianxu_main_hall`
| Field | Value |
|---|---|
| `location_id` | `loc_tianxu_main_hall` |
| `name` | Balairung Utama Tian Xu |
| `purpose` | Hub sentral Arc VII (The Last Night) — tempat found family dan cast lain berkumpul sebelum Final Confrontation |
| `first_appearance` | Kemungkinan sudah muncul sejak Arc I sebagai lokasi generik (upacara, pengumuman), TAPI signifikansi naratif eksplisit baru di Arc VII |
| `arc_usage` | Arc I (ambient, generik), Arc VII (signifikan) |
| `chapter_usage` | Chapter 7.1 |
| `connected_locations` | `loc_tianxu_gate`, `loc_tianxu_deepest_chamber` |
| `important_npcs` | Found family lengkap, Mentor, Grandmaster, Shen Luo, perwakilan faksi — hub NPC terpadat dalam seluruh dokumen |
| `available_quests` | `quest_a07_c01_001` |
| `hidden_area` | Tidak ada |
| `secrets` | Tidak ada |
| `memory_triggers` | Tidak ada |
| `world_events` | Crisis state penuh (formation gagal, Entity mulai keluar) |
| `faction_control` | Tian Xu Orthodox secara formal, tapi di titik ini kontrol faksi sudah mulai runtuh — representasi visual bahwa sistem lama sedang berakhir |
| `state_variations` | Megah/normal (Arc I, jika muncul) vs Krisis total (Arc VII) — paralel visual dengan `loc_tianxu_gate` |
| `future_payoffs` | Titik konvergensi seluruh relationship-building campaign — dicatat Quest Graph sebagai "payoff relationship terbesar dalam dokumen" |

### Lokasi Tambahan yang Direkomendasikan (Mengisi Gap Tersisa)

| location_id | Nama | Mengisi Gap Dari | Catatan |
|---|---|---|---|
| `loc_mo_chen_meeting` | Koridor Sunyi (nama sementara) | Chapter 3.2 pertemuan Mo Chen | Direkomendasikan: lokasi liminal — bukan ruang formal, bukan area publik, mencerminkan sifat Mo Chen yang berada "di antara" struktur formal Tian Xu. Jika rekomendasi Hidden Guardians diterima, lokasi ini dapat muncul kembali di titik kemunculan Mo Chen selanjutnya (Chapter 4.2, 5.4, 6.3) sebagai motif visual berulang, bukan lokasi fisik tetap — Mo Chen "muncul" di berbagai tempat tanpa penjelasan bagaimana ia sampai di sana, konsisten dengan sifat misteriusnya |
| `loc_jiang_yan_records` | Arsip Personal (bagian dari `loc_forbidden_archive` yang diperluas) | Chapter 6.1, rekaman sejarah personal Jiang Yan | **Rekomendasi konsolidasi:** BUKAN lokasi terpisah, melainkan bagian LEBIH DALAM dari `loc_forbidden_archive` yang belum diakses di Arc IV (dicatat sebagai `flag_version_iii_read` sudah true tapi arsip personal spesifik Jiang Yan memerlukan trigger terpisah `flag_jiang_yan_origin_known`) — pendekatan ini menghindari penciptaan lokasi baru yang tidak perlu, konsisten dengan filosofi "fewer + stronger" |
| `loc_entity_manifestation` | Titik Manifestasi Entity | Chapter 5.4, lokasi kemunculan Entity | **Rekomendasi konsolidasi:** BUKAN lokasi baru — direkomendasikan terjadi DI `loc_tianxu_deepest_chamber` atau di salah satu wilayah `world_event_a05_spiritual_collapse` terparah (kemungkinan `loc_outer_region` yang sudah terdampak). Memberi Entity kemunculan pertama di tempat yang sudah dikenal pemain memperkuat kontinuitas dibanding memperkenalkan lokasi benar-benar baru di titik penting cerita |

---

## Bagian C — NPC Catalog

### Main Characters (sudah terformalkan penuh di Phase 5, dicatat di sini untuk kelengkapan indeks)
`npc_lin_yue`, `npc_shen_luo`, `npc_mei_ruo`, `npc_gu_han`, `npc_mentor`, `npc_grandmaster`, `npc_mo_chen` — lihat `04-character-arcs.md` untuk detail penuh.

### Supporting Characters

*(Tidak ada kandidat kuat dari MSB untuk kategori ini secara terpisah dari Main Characters — MSB tidak menyediakan karakter tingkat-kedua yang cukup detail untuk kategori Supporting yang berbeda dari sembilan karakter utama. Dicatat sebagai observasi struktural, bukan gap yang perlu ditambal secara paksa.)*

### Recurring NPC

#### `npc_teacher_wuxin`, `npc_teacher_jianxin`, `npc_teacher_yanzhi`, `npc_teacher_liuguang`
| Field | Value |
|---|---|
| `role` | Guru pavilion — recurring sepanjang Arc I-IV, ambient setelahnya |
| `faction` | Tian Xu Orthodox (secara formal, semua guru berafiliasi institusional) |
| `first_appearance` | `quest_a01_c03_004` (pengenalan filosofi pavilion) |
| `last_appearance` | `[DESIGN GAP]` — direkomendasikan tetap relevan hingga Arc IV sebagai figur curriculum, memudar signifikansinya di Arc V-VII kecuali guru pavilion terpilih pemain (yang dapat muncul di `loc_tianxu_main_hall` Chapter 7.1 sebagai salah satu NPC ambient tambahan) |
| `personality` | Bervariasi sesuai filosofi pavilion masing-masing (lihat Bagian A) |
| `quest_involvement` | `quest_a01_c03_004`, dan konten curriculum-spesifik di Arc II-IV (belum diformalkan detail per-quest) |
| `possible_end_states` | Tidak signifikan secara individual — guru pavilion bukan karakter dengan arc pribadi, fungsinya struktural (curriculum gate) |

### Quest NPC

#### `npc_missing_disciple`
| Field | Value |
|---|---|
| `role` | Murid senior yang hilang, pemicu mystery Arc II |
| `faction` | Tidak diketahui — inilah misterinya (kemungkinan berafiliasi dengan salah satu faksi radikal, ditemukan implisit lewat catatan "Siklus dimulai lagi") |
| `first_appearance` | Tidak pernah hadir secara fisik — hanya via bukti (`quest_a02_c02_005`) |
| `last_appearance` | **[DESIGN GAP]** — apakah murid ini pernah ditemukan (hidup/mati) secara eksplisit di kemudian hari. MSB tidak menyatakan. Direkomendasikan: TIDAK PERNAH ditemukan secara eksplisit, tetap menjadi mystery terbuka — bukan setiap thread cerita harus ditutup rapi, dan ambiguitas ini konsisten dengan skala Cycle Formation (kemungkinan murid ini "menghilang" dalam pengertian yang lebih kompleks daripada sekadar kabur, terkait fenomena spiritual yang baru dipahami penuh di Arc V) |
| `personality` | Tidak diketahui — hanya diketahui lewat jejak (catatan yang ditinggalkan) |
| `quest_involvement` | `quest_a02_c02_005` |
| `possible_end_states` | N/A — karakter ini secara sengaja tetap sebagai mystery, bukan resolved subplot |

#### `npc_aptitude_examiner`
| Field | Value |
|---|---|
| `role` | Pemeriksa aptitude test Arc I |
| `faction` | Tian Xu Orthodox (fungsi administratif) |
| `first_appearance` | `quest_a01_c01_001` |
| `last_appearance` | `quest_a01_c01_002` |
| `personality` | Netral-profesional, tidak signifikan secara naratif — fungsinya murni tutorial/tekstural |
| `quest_involvement` | `quest_a01_c01_001`, `quest_a01_c01_002` |
| `possible_end_states` | N/A — Ambient-tier meski dicatat sebagai Quest NPC karena namanya terlibat langsung di quest_id tertentu |

### Faction NPC

*(Selain Grandmaster yang sudah Main Character, faksi lain — Reformists, Liberation, Hidden Guardians — belum memiliki NPC representasi bernama selain kandidat yang sudah dicatat di Faction Bible: pemimpin Reformists sebagai `[DESIGN GAP]`, Gu Han sebagai potensi Liberation leader, Mo Chen sebagai potensi Hidden Guardians leader. Tidak ada Faction NPC tambahan diciptakan di fase ini untuk menghindari proliferasi karakter tanpa fungsi jelas — konsisten dengan prinsip MSB §25.)*

### Ambient NPC

| npc_id | Peran | Catatan |
|---|---|---|
| `npc_archive_clerk` | Arsiparis di arsip publik akademi | Muncul `quest_a03_c03_003`, murni fungsional |
| `npc_academy_teacher_generic` | Guru pengawas ujian/trial (Arc II) | Fungsi generik, tidak memerlukan nama/kepribadian individual |
| `npc_mountain_gate_villager` | **[Rekomendasi mengisi gap "NPC yang terancam"]** — penduduk/murid yang berisiko dalam Mountain Gate Incident | **Catatan produksi penting:** direkomendasikan BUKAN NPC generik tanpa nama, melainkan salah satu NPC yang SUDAH dikenal pemain sejak Arc sebelumnya (mis. NPC dari `loc_outer_region` yang sempat berinteraksi dengan found family di Arc II) — memberi stake emosional nyata, sesuai catatan `[DESIGN GAP]` di Character Bible tentang pentingnya ini bukan NPC generik. Ini memerlukan sedikit revisi retroaktif ke Chapter 2.2 untuk menyisipkan NPC ambient bernama yang dapat "dipanen" kembali signifikansinya di Arc V — direkomendasikan sebagai penyempurnaan opsional, bukan wajib |

---

## Design Gap & Recommendation Ringkasan Fase Ini

**Gap yang BERHASIL ditutup fase ini:**
1. Roster pavilion (empat pavilion dengan filosofi terhubung tema)
2. Lokasi formation tua Arc I → tetap generik tapi cukup untuk produksi (`loc_outer_region` terhubung)
3. Sebelas lokasi terformalkan penuh dengan seluruh field wajib
4. Nama pemeriksa aptitude, murid hilang, arsiparis — sebagai identifier formal meski kepribadian mereka sengaja minim (fungsi struktural, bukan karakter development)

**Gap yang TETAP terbuka (dengan alasan eksplisit):**
1. **Lokasi pertemuan Mo Chen** — direkomendasikan sebagai motif liminal berulang, bukan lokasi fisik tetap, tapi ini bergantung pada resolusi arah Mo Chen yang belum final
2. **Last appearance `npc_missing_disciple`** — direkomendasikan SENGAJA tetap terbuka sebagai mystery, bukan gap yang perlu ditutup
3. **NPC terancam Mountain Gate Incident** — direkomendasikan revisi retroaktif kecil ke Chapter 2.2 untuk stake emosional lebih kuat; opsional

**Keputusan konsolidasi penting yang dibuat fase ini:**
- `loc_the_gate` DIKONSOLIDASIKAN dengan `loc_tianxu_deepest_chamber` — satu lokasi, signifikansi berlapis tiga Arc
- Arsip personal Jiang Yan (Arc VI) direkomendasikan sebagai perluasan `loc_forbidden_archive`, bukan lokasi baru
- Titik manifestasi Entity direkomendasikan menggunakan lokasi yang sudah ada, bukan lokasi baru

---

**File berikutnya:** `09-world-events.md` — World Event Bible, akan memformalkan `world_event_a05_spiritual_collapse` secara detail (yang sudah dirujuk di banyak lokasi pada fase ini) dan event-event lain yang disebutkan MSB §11 (Mountain Gate Incident, Spiritual Collapse, Tian Xu Formation Failure, Entity Awakening, Faction Conflict, Academy Lockdown).
