# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 02. Chapter Breakdown — 7 Arc

**Status:** DRAFT — Phase 3 of 18
**Depends on:** `00-narrative-architecture.md`, `01-arc-overview.md`
**Prinsip pacing wajib per chapter-sequence dalam satu Arc:** Setup → Development → Complication → Escalation → Revelation → Consequence → Transition. Tidak setiap chapter individual harus melalui ketujuh tahap ini sendirian — tahapan ini didistribusikan across chapter dalam satu Arc.

**Metodologi penentuan jumlah chapter:** jumlah chapter per Arc ditentukan oleh (a) jumlah quest eksplisit di MSB untuk Arc tersebut, (b) jumlah revelation/turning point yang butuh ruang bernapas agar tidak jadi lore-dump, dan (c) posisi Arc dalam eskalasi keseluruhan (Arc VII sengaja lebih padat/singkat sesuai prinsip MSB §32). Ini dicatat eksplisit di awal tiap Arc supaya keputusan jumlah chapter bisa diaudit, bukan sekadar diterima.

---

## ARC I — A NEW LIFE (4 Chapter)

**Rasional jumlah:** MSB memberi 10 quest eksplisit dalam satu chain linear (`arc1_arrival` → `arc1_end`) tanpa branching berarti — ini pengenalan sistem, bukan mystery kompleks. Dipadatkan jadi 4 chapter yang masing-masing menggabungkan 2-3 quest MSB, cukup untuk pacing penuh tanpa menyeret tutorial.

### Chapter 1.1 — Arrival
| Field | Value |
|---|---|
| `chapter_id` | `chapter_01_01` |
| `title` | Arrival |
| `narrative_purpose` | Membangun tone "kehidupan baru", memperkenalkan dunia Tian Xu dari mata murid biasa |
| `emotional_purpose` | Disorientasi netral → rasa ingin tahu (bukan takut) |
| `main_conflict` | Tidak ada konflik eksternal — internal: menyesuaikan ekspektasi ("aku bukan murid istimewa") |
| `opening_state` | Protagonis dalam perjalanan menuju akademi |
| `closing_state` | Diterima sebagai murid baru, hasil aptitude test biasa-biasa saja |
| `key_characters` | Tidak ada NPC nama besar — pemeriksa aptitude sebagai ambient/quest NPC |
| `key_locations` | `loc_tianxu_approach_road` [DESIGN GAP — nama lokasi belum di MSB, akan diformalkan Phase 9], `loc_tianxu_gate` |
| `main_quests` | `quest_a01_c01_001` (`arc1_arrival`), `quest_a01_c01_002` (`arc1_registration`) |
| `optional_content` | Eksplorasi awal gerbang/pekarangan akademi (world-building, tidak wajib) |
| `mystery_progress` | Mimpi koridor terbakar + "Jangan buka gerbang itu!" — first hint Mystery #1, TANPA konteks (sesuai prinsip: jangan langsung menjelaskan) |
| `foreshadowing` | Dream sequence pertama (koridor terbakar, suara tanpa wajah) |
| `payoff` | N/A di chapter ini — payoff dream ini baru di Chapter 1.4 |
| `chapter_climax` | Kalimat "Jangan buka gerbang itu!" dalam mimpi, terpotong sebelum protagonis tahu siapa yang bicara |
| `transition_to_next_chapter` | Aptitude test selesai → chapter berikutnya dimulai dengan pelajaran pertama |

### Chapter 1.2 — First Lesson, First Bonds
| Field | Value |
|---|---|
| `chapter_id` | `chapter_01_02` |
| `title` | First Lesson, First Bonds |
| `narrative_purpose` | Memperkenalkan mekanisme cultivation dasar dan keempat calon anggota found family sebagai individu (belum sebagai kelompok solid) |
| `emotional_purpose` | Belonging mulai terbentuk — pengenalan personal, bukan sekadar exposition sistem |
| `main_conflict` | Rivalitas ringan dengan Shen Luo (belum hostile, sesuai MSB §5 "awalnya menganggap protagonis biasa saja") |
| `opening_state` | Murid baru tanpa hubungan |
| `closing_state` | Empat karakter (Lin Yue, Shen Luo, Mei Ruo, Gu Han) sudah dikenal secara individual sebagai NPC dengan first_appearance masing-masing |
| `key_characters` | `npc_lin_yue`, `npc_shen_luo`, `npc_mei_ruo`, `npc_gu_han` — semua first appearance di chapter ini |
| `key_locations` | Ruang latihan umum, area umum akademi |
| `main_quests` | `quest_a01_c02_003` (`arc1_first_lesson`) |
| `optional_content` | Interaksi opsional dengan tiap calon anggota kelompok — tidak wajib untuk progress tapi memengaruhi relationship starting value sebelum Chapter 1.3 |
| `mystery_progress` | Tidak ada progress mystery langsung — chapter ini murni character-building |
| `foreshadowing` | Teknik yang "terasa familiar" saat protagonis mencoba gerakan dasar pertama (foreshadowing element "Technique" dari MSB §44) |
| `payoff` | N/A |
| `chapter_climax` | Momen kecil di mana keempat calon anggota kelompok berada di ruang yang sama untuk pertama kali (tanpa harus jadi kelompok resmi) |
| `transition_to_next_chapter` | Pengumuman pavilion selection |

### Chapter 1.3 — The Path Chosen
| Field | Value |
|---|---|
| `chapter_id` | `chapter_01_03` |
| `title` | The Path Chosen |
| `narrative_purpose` | Major Choice pertama permainan: Pavilion Selection. Menegaskan bahwa pilihan sejak awal punya bobot jangka panjang, bukan sekadar class-picking |
| `emotional_purpose` | Agency — pemain merasa keputusannya "membentuk cara hidup", sesuai penekanan MSB |
| `main_conflict` | Internal: filosofi cultivation mana yang paling sesuai dengan cara pemain ingin bermain |
| `opening_state` | Belum memilih pavilion |
| `closing_state` | Pavilion terpilih; kelompok found family mulai solid berdasarkan siapa yang berada di pavilion yang sama/berdekatan |
| `key_characters` | Guru pavilion (`[DESIGN GAP]` — nama/detail belum ada di MSB, akan diformalkan Phase 9) |
| `key_locations` | `[DESIGN GAP]` — lokasi tiap pavilion, tergantung roster pavilion final |
| `main_quests` | `quest_a01_c03_004` (`arc1_pavilion_selection`) |
| `optional_content` | Dialog eksplorasi filosofi tiap pavilion sebelum memilih (memastikan pilihan informed, bukan blind) |
| `mystery_progress` | Tidak langsung — tapi pavilion terpilih akan memengaruhi *akses* ke beberapa clue di Arc-Arc berikutnya (dicatat sebagai permanent modifier, bukan gate absolut) |
| `foreshadowing` | Tidak ada foreshadowing baru — chapter fokus pada payoff sistem, bukan mystery |
| `payoff` | Payoff dari sistem cultivation yang diperkenalkan Chapter 1.2 |
| `chapter_climax` | Momen memilih pavilion |
| `transition_to_next_chapter` | Training pertama di pavilion terpilih |

**`[DESIGN GAP]` eksplisit:** roster pavilion konkret (nama, filosofi, guru) belum ada di MSB. Rekomendasi pengisian gap ini diberikan terpisah di bagian akhir dokumen ini (§ Design Gap Recommendations), bukan diasumsikan di sini.

### Chapter 1.4 — What the Formation Remembers
| Field | Value |
|---|---|
| `chapter_id` | `chapter_01_04` |
| `title` | What the Formation Remembers |
| `narrative_purpose` | First Trial + Arc I ending — memory pertama yang cukup konkret untuk mengubah "rasa janggal" menjadi "aku harus mencari tahu" |
| `emotional_purpose` | Dari netral/ingin-tahu (Ch 1.1) menuju urgensi personal |
| `main_conflict` | External baru: monster yang menjaga formation tua berperilaku tidak normal (bukan sekadar hostile) |
| `opening_state` | Kelompok found family solid dengan pavilion masing-masing |
| `closing_state` | `flag_memory_awareness = true`; symbol kuno di tangan; found family terikat lewat pengalaman berbagi first trial |
| `key_characters` | Keempat anggota found family (kelompok penuh untuk pertama kali dalam misi nyata) |
| `key_locations` | Wilayah sekitar akademi dengan formation tua (`[DESIGN GAP]` — nama lokasi spesifik) |
| `main_quests` | `quest_a01_c04_005` (`arc1_first_training` + `arc1_first_trial` digabung), `quest_a01_c04_006` (`arc1_night_incident` + `arc1_end`) |
| `optional_content` | Eksplorasi tambahan area sekitar formation tua sebelum/sesudah trial |
| `mystery_progress` | Memory pertama (formation hancur) + mimpi kedua ("jangan percaya sejarah") + penemuan symbol — payoff langsung dari foreshadowing Chapter 1.1 |
| `foreshadowing` | Symbol kuno ditanam sebagai foreshadowing untuk Arc III (Mo Chen recognition) |
| `payoff` | Payoff dream Chapter 1.1 (koridor terbakar terhubung tematis dengan formation hancur, walau belum secara eksplisit sama) |
| `chapter_climax` | Menemukan symbol di meja kamar setelah mimpi kedua — protagonis sadar ini bukan sekadar mimpi |
| `transition_to_next_chapter` | **Arc I → Arc II.** `flag_memory_awareness=true` menjadi prasyarat pembuka Arc II |

---

## ARC II — THE FIRST TRIAL (4 Chapter)

**Rasional jumlah:** 10 quest eksplisit MSB (`arc2_midterm` → `arc2_trial_conclusion`) dengan satu branching choice signifikan (Obey/Investigate/Confront) di tengah. 4 chapter memberi ruang: (1) build-up ke insiden, (2) insiden + discovery, (3) choice + immediate branch consequence, (4) convergence + revelation penutup Arc.

### Chapter 2.1 — Team Trial
| Field | Value |
|---|---|
| `chapter_id` | `chapter_02_01` |
| `title` | Team Trial |
| `narrative_purpose` | Menunjukkan kelompok sebagai unit fungsional di bawah tekanan institusional (midterm, team trial) — trust antar-anggota kelompok, bukan trust terhadap institusi (itu baru muncul chapter berikutnya) |
| `emotional_purpose` | Solidaritas kelompok diuji tekanan eksternal netral (ujian, bukan konspirasi) |
| `main_conflict` | Rivalitas antar-pavilion mulai muncul sebagai tekanan sosial |
| `opening_state` | Kelompok solid pasca-Arc I |
| `closing_state` | Kelompok lulus team trial, reputasi awal terbentuk di mata guru |
| `key_characters` | Keempat anggota found family; guru pengawas (`[DESIGN GAP]` — nama) |
| `key_locations` | Arena ujian akademi |
| `main_quests` | `quest_a02_c01_001` (`arc2_midterm`), `quest_a02_c01_002` (`arc2_team_trial`) |
| `optional_content` | Interaksi dengan murid pavilion lain (rivalitas antar-pavilion sebagai world-building, bukan quest wajib) |
| `mystery_progress` | Tidak ada progress langsung |
| `foreshadowing` | Tidak ada foreshadowing baru |
| `payoff` | Payoff pavilion selection Arc I (curriculum berbeda terlihat konkret dalam cara kelompok menghadapi trial) |
| `chapter_climax` | Kelulusan team trial sebagai kelompok resmi |
| `transition_to_next_chapter` | Penugasan misi lapangan pertama ke outer region |

### Chapter 2.2 — What the Cave Hides
| Field | Value |
|---|---|
| `chapter_id` | `chapter_02_02` |
| `title` | What the Cave Hides |
| `narrative_purpose` | Setup mystery utama Arc II: murid senior hilang, gangguan spiritual, penemuan tempat persembunyian dengan catatan "Siklus dimulai lagi" |
| `emotional_purpose` | Dari kepercayaan diri (pasca team trial) menuju kecurigaan pertama terhadap institusi |
| `main_conflict` | Institusi (lewat guru/pengumuman resmi) menyatakan murid hilang "kemungkinan kabur" — kelompok menemukan bukti bertentangan |
| `opening_state` | Kelompok baru lulus team trial, dikirim ke outer region untuk tugas rutin |
| `closing_state` | Bukti kontradiktif ditemukan; catatan "Siklus dimulai lagi" di tangan kelompok, tanpa penjelasan |
| `key_characters` | Keempat anggota found family; murid senior yang hilang (nama `[DESIGN GAP]`, statusnya sebagai Quest NPC akan diformalkan Phase 9) |
| `key_locations` | `loc_outer_region` [DESIGN GAP nama spesifik], gua tersembunyi |
| `main_quests` | `quest_a02_c02_003` (`arc2_outer_region`), `quest_a02_c02_004` (`arc2_spiritual_disturbance`), `quest_a02_c02_005` (`arc2_missing_disciple`) |
| `optional_content` | Eksplorasi outer region tambahan, interaksi dengan penduduk lokal (jika ada — `[DESIGN GAP]` apakah outer region punya populasi non-akademi) |
| `mystery_progress` | First hint Mystery #10 ("Mengapa sejarah berulang?") lewat catatan "Siklus dimulai lagi" — sengaja tanpa konteks |
| `foreshadowing` | Catatan itu sendiri adalah foreshadowing besar untuk Cycle Formation (Arc VI) |
| `payoff` | Tidak ada payoff di chapter ini — murni setup |
| `chapter_climax` | Menemukan catatan "Siklus dimulai lagi" |
| `transition_to_next_chapter` | Kelompok harus memutuskan apa yang dilakukan dengan bukti ini |

### Chapter 2.3 — What You Choose to Trust
| Field | Value |
|---|---|
| `chapter_id` | `chapter_02_03` |
| `title` | What You Choose to Trust |
| `narrative_purpose` | First Major Choice: Obey / Investigate / Confront. Payoff tematik penuh dari tema Trust Arc II |
| `emotional_purpose` | Ketegangan moral — tidak ada opsi yang terasa "benar secara jelas" (sesuai instruksi eksplisit: tidak ada pilihan langsung benar) |
| `main_conflict` | Kelompok vs institusi (implisit); atau kelompok vs kelompok jika anggota tidak sepakat pada pilihan (`[DESIGN GAP]` — apakah found family bisa berbeda pendapat di titik ini adalah desain opsional yang direkomendasikan, dibahas di bagian gap) |
| `opening_state` | Bukti + catatan misterius di tangan kelompok |
| `closing_state` | Salah satu dari tiga state-branch aktif: `flag_archive_suspicious=true` (Investigate) ATAU `state_rel_master +` (Obey) ATAU `state_rep_tianxu -` (Confront) — sesuai MSB §43 |
| `key_characters` | Guru yang menerima laporan (Obey path) ATAU tidak muncul (Investigate path) ATAU pihak akademi yang dituduh (Confront path) |
| `key_locations` | Bervariasi tergantung branch — kantor guru (Obey), lanjutan investigasi tersembunyi (Investigate), forum/pertemuan terbuka (Confront) |
| `main_quests` | `quest_a02_c03_006` (`arc2_accusation` — nama MSB, mencakup ketiga branch sebagai satu decision point dengan tiga outcome) |
| `optional_content` | Tidak ada — ini adalah keputusan wajib untuk melanjutkan cerita |
| `mystery_progress` | Tergantung branch: Investigate memberi progress mystery paling langsung; Obey/Confront memberi progress relationship/reputation dengan mystery progress lebih lambat |
| `foreshadowing` | Tidak ada foreshadowing baru |
| `payoff` | Payoff langsung dari Chapter 2.2 (catatan misterius) |
| `chapter_climax` | Momen pengambilan keputusan itu sendiri |
| `transition_to_next_chapter` | Ketiga branch menuju penemuan yang sama: `arc2_hidden_cave` |

### Chapter 2.4 — First Artifact
| Field | Value |
|---|---|
| `chapter_id` | `chapter_02_04` |
| `title` | First Artifact |
| `narrative_purpose` | Convergence Point Arc II — ketiga branch bertemu di penemuan artefak yang sama, tapi state relationship/reputation/informasi berbeda dibawa terus |
| `emotional_purpose` | Dari ketegangan moral (Ch 2.3) menuju kebingungan personal (memory pertama yang melibatkan Lin Yue versi tua) |
| `main_conflict` | Internal: memory yang tidak dipahami ("Kalau kau melakukan ini, kau tidak akan kembali" — dari siapa? tentang apa?) |
| `opening_state` | Salah satu dari tiga state branch Chapter 2.3 aktif |
| `closing_state` | Artefak ditemukan dan sudah bereaksi terhadap protagonis; memory pertama yang melibatkan NPC bernama (Lin Yue versi tua) muncul; Arc II selesai |
| `key_characters` | `npc_lin_yue` (muncul dalam memory, versi tua — bukan NPC hadir di dunia nyata saat ini) |
| `key_locations` | `loc_hidden_cave` (mengikuti nama MSB `arc2_hidden_cave`) |
| `main_quests` | `quest_a02_c04_007` (`arc2_hidden_cave`), `quest_a02_c04_008` (`arc2_first_artifact`), `quest_a02_c04_009` (`arc2_return` + `arc2_trial_conclusion` digabung) |
| `optional_content` | Tidak ada — ini adalah climax Arc, semua konten wajib |
| `mystery_progress` | Revelation parsial Mystery #1/#2 — memory dengan Lin Yue versi tua, tanpa konteks penuh (reliability rendah, sesuai prinsip memory) |
| `foreshadowing` | "Kalau kau melakukan ini, kau tidak akan kembali" — foreshadowing besar untuk The Gate (Arc VI) |
| `payoff` | Payoff dari catatan "Siklus dimulai lagi" (Chapter 2.2) — walau belum dijelaskan penuh, mulai terasa terhubung dengan memory personal protagonis |
| `chapter_climax` | Memory Lin Yue versi tua |
| `transition_to_next_chapter` | **Arc II → Arc III.** Artefak menjadi trigger sistematis untuk Memory Investigation System |

---

## ARC III — ECHOES OF ANOTHER SELF (5 Chapter)

**Rasional jumlah:** Arc ini adalah genre shift eksplisit (academy adventure → mystery RPG, MSB §11). Butuh lebih banyak chapter dibanding Arc I/II karena pacing harus sengaja lebih investigatif/lambat, dan ada dua design gap (major choice, convergence) yang perlu ruang untuk diisi dengan hati-hati tanpa terasa dipaksakan.

### Chapter 3.1 — The Room That Isn't on the Map
| Field | Value |
|---|---|
| `chapter_id` | `chapter_03_01` |
| `title` | The Room That Isn't on the Map |
| `narrative_purpose` | Pengenalan penuh Memory Investigation System sebagai mekanik; penemuan ruangan tersembunyi dengan mural |
| `emotional_purpose` | Rasa ingin tahu berubah jadi kewaspadaan — "seseorang sengaja menyembunyikan ini" |
| `main_conflict` | Tidak ada antagonist langsung — misteri institusional pasif |
| `opening_state` | Artefak dari Arc II sebagai trigger aktif |
| `closing_state` | Ruangan tersembunyi + mural ditemukan; Mei Ruo mengidentifikasi bahwa kerusakan mural disengaja |
| `key_characters` | `npc_mei_ruo` (peran menonjol — pintu masuk mystery sesuai MSB §5) |
| `key_locations` | `loc_hidden_room_mural` [DESIGN GAP nama formal] |
| `main_quests` | `quest_a03_c01_001` [DESIGN GAP — MSB tidak beri quest_id eksplisit untuk Arc III, ID dibuat mengikuti convention] |
| `optional_content` | Analisis tambahan mural bersama Mei Ruo (deepening relationship + world-building sejarah Tian Xu) |
| `mystery_progress` | Mystery #4 ("Mengapa Tian Xu menyembunyikan sejarah?") dibuka pertama kali secara konkret (bukan lagi sekadar rasa janggal personal) |
| `foreshadowing` | Bagian mural yang dihancurkan — foreshadowing untuk Forbidden Archive Arc IV |
| `payoff` | N/A |
| `chapter_climax` | Mei Ruo: "Seseorang sengaja menghapusnya" |
| `transition_to_next_chapter` | Kemunculan Mo Chen |

### Chapter 3.2 — The Stranger Who Knows My Name
| Field | Value |
|---|---|
| `chapter_id` | `chapter_03_02` |
| `title` | The Stranger Who Knows My Name |
| `narrative_purpose` | Pertemuan Mo Chen; pengenalan nama "Jiang Yan" — titik mystery paling personal sejauh ini |
| `emotional_purpose` | Dari kewaspadaan (Ch 3.1) menuju disorientasi identitas yang tajam |
| `main_conflict` | Internal murni — Mo Chen bukan antagonist, ia pembawa informasi yang tidak lengkap lalu menghilang |
| `opening_state` | Kecurigaan terhadap sejarah resmi Tian Xu |
| `closing_state` | Nama "Jiang Yan" diketahui; Mo Chen menghilang tanpa penjelasan lanjutan |
| `key_characters` | `npc_mo_chen` (first_appearance) |
| `key_locations` | `[DESIGN GAP]` — lokasi pertemuan Mo Chen belum ditentukan MSB |
| `main_quests` | `quest_a03_c02_002` |
| `optional_content` | Tidak ada — pertemuan ini wajib dan singkat (MSB: "Mo Chen kemudian menghilang" — momen deliberately terpotong) |
| `mystery_progress` | Mystery #1/#2 — nama diketahui, makna belum |
| `foreshadowing` | Mo Chen sebagai NPC recurring — kemunculan berikutnya harus dijustifikasi (akan diformalkan di Phase 9 NPC Bible) |
| `payoff` | Payoff parsial dari symbol Arc I (kemungkinan Mo Chen mengenali symbol tersebut — direkomendasikan sebagai detail produksi, bukan diklaim sebagai fakta MSB) |
| `chapter_climax` | Mo Chen memanggil protagonis "Jiang Yan" |
| `transition_to_next_chapter` | Pencarian dokumen untuk memverifikasi nama tersebut |

### Chapter 3.3 — Deceased
| Field | Value |
|---|---|
| `chapter_id` | `chapter_03_03` |
| `title` | Deceased |
| `narrative_purpose` | Penemuan dokumen dengan nama Jiang Yan, tanggal, dan status Deceased — konfirmasi literal, bukan lagi spekulatif |
| `emotional_purpose` | Titik paling personal & berat sejauh cerita — menghadapi bukti kematian diri sendiri |
| `main_conflict` | Internal murni |
| `opening_state` | Nama diketahui tanpa verifikasi |
| `closing_state` | Dokumen dengan status Deceased ditemukan dan diverifikasi |
| `key_characters` | Arsip/pencatat dokumen (Ambient NPC, `[DESIGN GAP]` detail) |
| `key_locations` | Arsip akademi (bagian yang dapat diakses publik, berbeda dari Forbidden Archive Arc IV) |
| `main_quests` | `quest_a03_c03_003` |
| `optional_content` | Riset tambahan tentang periode waktu dokumen tersebut (world-building) |
| `mystery_progress` | Mystery #1 hampir terjawab penuh — hanya makna "mengapa" yang masih tertutup |
| `foreshadowing` | Tanggal dokumen ("lebih dari dua puluh tahun sebelum protagonis lahir") — detail yang akan relevan untuk memahami timeline Cycle Formation di Arc VI |
| `payoff` | Payoff langsung dari Chapter 3.2 |
| `chapter_climax` | Melihat kata "Deceased" tertulis dengan namanya sendiri |
| `transition_to_next_chapter` | Emosi mentah ini butuh outlet — Major Choice chapter berikutnya |

### Chapter 3.4 — What I Choose to Believe
| Field | Value |
|---|---|
| `chapter_id` | `chapter_03_04` |
| `title` | What I Choose to Believe |
| `narrative_purpose` | Mengisi `[DESIGN GAP]` Major Choice Arc III yang dicatat di Phase 2. Tema Identity dibayar penuh di sini: bagaimana protagonis memilih menafsirkan dirinya sebelum bukti lengkap tersedia |
| `emotional_purpose` | Agency personal — pemain menentukan *sikap*, bukan sekadar fakta |
| `main_conflict` | Internal, dimediasi lewat reaksi found family terhadap identitas protagonis yang terungkap |
| `opening_state` | Status Deceased diketahui, found family mulai tahu (atau tidak, tergantung pilihan pemain apakah memberi tahu mereka) |
| `closing_state` | Salah satu dari sikap berikut aktif sebagai state: `state_identity_stance = "deny"` (menolak bahwa ia adalah Jiang Yan) / `"accept_cautious"` (menerima tapi berjarak) / `"seek_truth"` (aktif mencari, netral secara emosional) |
| `key_characters` | Keempat anggota found family — reaksi mereka terhadap pengungkapan ini adalah konten chapter, bukan sekadar dialog kosmetik |
| `key_locations` | Ruang privat kelompok (asrama/tempat berkumpul found family) |
| `main_quests` | `quest_a03_c04_004` **[DESIGN GAP — quest dan branch ini baru, bukan dari MSB langsung]** |
| `optional_content` | Percakapan individual dengan tiap anggota found family tentang bagaimana mereka masing-masing merespons (memberi variasi relationship state) |
| `mystery_progress` | Tidak menambah fakta baru — chapter ini murni tentang sikap terhadap fakta yang sudah ada |
| `foreshadowing` | `state_identity_stance` akan memengaruhi dialogue availability di seluruh Arc IV-VII (terutama percakapan dengan Mentor Arc VI dan Final Confrontation Arc VII) |
| `payoff` | Payoff dari seluruh relationship yang dibangun sejak Arc I — momen di mana found family diuji bukan oleh external threat, tapi oleh kejujuran |
| `chapter_climax` | Reaksi found family, khususnya Lin Yue (emotional anchor) dan Gu Han (skeptis institusi — mungkin justru paling menerima karena sudah skeptis pada narasi resmi) |
| `transition_to_next_chapter` | Memory gerbang penuh muncul sebagai closing Arc |

### Chapter 3.5 — The Gate I Opened
| Field | Value |
|---|---|
| `chapter_id` | `chapter_03_05` |
| `title` | The Gate I Opened |
| `narrative_purpose` | Arc III ending — memory gerbang lengkap, kesimpulan (belum-final) bahwa protagonis mungkin penyebab tragedi |
| `emotional_purpose` | Puncak ambiguitas Arc — ditutup dengan ketidakpastian yang disengaja, bukan resolusi |
| `main_conflict` | Internal — klimaks tema Identity |
| `opening_state` | `state_identity_stance` aktif dari Chapter 3.4 |
| `closing_state` | Memory gerbang lengkap tersimpan; kesimpulan sementara "aku mungkin penyebab tragedi" aktif sebagai *player belief state*, bukan fakta tercatat (penting untuk Phase 7 Memory Architecture — ini harus bisa dikontraskan nanti tanpa terasa retcon) |
| `key_characters` | Tidak ada NPC baru — momen soliter protagonis |
| `key_locations` | Tempat memory dipicu (`[DESIGN GAP]` spesifik) |
| `main_quests` | `quest_a03_c05_005` (convergence dari Chapter 3.4, terlepas dari `state_identity_stance` mana yang aktif) |
| `optional_content` | Tidak ada |
| `mystery_progress` | Mystery #8 dibuka parsial (memory gerbang) — TIDAK final, akan dikontraskan Arc VI |
| `foreshadowing` | Kalimat "Kalau dunia harus membenciku, biarkan" — foreshadowing ambigu yang baru dipahami penuh di Arc VI (The Gate, First Betrayal) |
| `payoff` | Payoff dari seluruh Arc III sebagai satu kesatuan investigasi |
| `chapter_climax` | Memory gerbang lengkap, cut sebelum protagonis melihat hasil setelah membuka gerbang |
| `transition_to_next_chapter` | **Arc III → Arc IV.** `state_identity_stance` dan kesimpulan sementara dibawa sebagai modifier dialogue Arc IV, khususnya saat Forbidden Archive mengontraskannya |

**Convergence Point Arc III (mengisi gap dari Phase 2):** `convergence_a03_c04_01` — ketiga `state_identity_stance` bertemu di Chapter 3.5 (memory gerbang muncul terlepas dari sikap yang dipilih), tapi *cara found family memperlakukan protagonis* sejak titik ini berbeda permanen tergantung stance yang dipilih.

---

## ARC IV — THE FALSE HISTORY (4 Chapter)

**Rasional jumlah:** tiga versi sejarah (MSB §17) secara natural memberi struktur tiga-lapis-revelation, ditambah satu chapter penutup untuk origin of cultivation + Grandmaster + ruang terdalam formation. Tidak dipadatkan lebih sedikit karena tiap versi sejarah butuh reaksi/refleksi terpisah supaya tidak jadi lore-dump berturutan.

### Chapter 4.1 — The Archive Beneath
| Field | Value |
|---|---|
| `chapter_id` | `chapter_04_01` |
| `title` | The Archive Beneath |
| `narrative_purpose` | Penemuan Forbidden Archive; Version I (resmi) dan Version II (disembunyikan) dibandingkan langsung |
| `emotional_purpose` | Dari ambiguitas personal (penutup Arc III) menuju fokus institusional — kelegaan sementara bahwa masalah ini lebih besar dari sekadar dirinya, sebelum kembali menyempit personal di Chapter 4.3 |
| `main_conflict` | Institusi vs kebenaran — versi resmi mulai runtuh |
| `opening_state` | `flag_archive_suspicious`-type state dari Arc II sebagai prasyarat akses (jika Investigate dipilih, akses lebih mudah; jika Obey/Confront, jalur alternatif tersedia — `[DESIGN GAP]` detail gating akan diformalkan Phase 4 Quest Graph) |
| `closing_state` | Version I dan II dibandingkan; kontradiksi nyata terdokumentasi |
| `key_characters` | Mei Ruo (analisis dokumen, peran menonjol berlanjut dari Arc III) |
| `key_locations` | `loc_forbidden_archive` |
| `main_quests` | `quest_a04_c01_001` |
| `optional_content` | Membaca detail tambahan Version I/II untuk world-building sejarah Tian Xu |
| `mystery_progress` | Mystery #4 mendapat progress signifikan |
| `foreshadowing` | Petunjuk keberadaan Version III (catatan pribadi pendiri) |
| `payoff` | Payoff dari kecurigaan sejak Chapter 2.2/3.1 |
| `chapter_climax` | Menyadari Version I dan II saling bertentangan secara fundamental, bukan sekadar detail kecil |
| `transition_to_next_chapter` | Pencarian Version III |

### Chapter 4.2 — What We Sealed
| Field | Value |
|---|---|
| `chapter_id` | `chapter_04_02` |
| `title` | What We Sealed |
| `narrative_purpose` | Penemuan Version III — revelation langsung dari kata-kata pendiri sendiri: "Yang kami segel bukan musuh. Kami menyegel akibat dari kesalahan kami sendiri." |
| `emotional_purpose` | Titik balik terbesar Arc — dari "sejarah dipalsukan" menjadi "kesalahan foundational yang disembunyikan" |
| `main_conflict` | Tidak ada konfrontasi langsung — ini adalah revelation chapter |
| `opening_state` | Kontradiksi Version I/II diketahui |
| `closing_state` | Version III diketahui penuh; origin of cultivation mulai terbuka (sumber purba, entitas lahir dari penggunaan) |
| `key_characters` | Mei Ruo |
| `key_locations` | `loc_forbidden_archive` (bagian terdalam) |
| `main_quests` | `quest_a04_c02_002` |
| `optional_content` | Tidak ada — revelation inti wajib dialami penuh |
| `mystery_progress` | Mystery #4 terjawab penuh; Mystery #6 (origin cultivation) dibuka signifikan |
| `foreshadowing` | Detail tentang "akibat dari kesalahan kami sendiri" — foreshadowing untuk pemahaman penuh The Gate (Arc VI) |
| `payoff` | Payoff besar dari seluruh kecurigaan institusional sejak Arc II |
| `chapter_climax` | Membaca kutipan Version III secara langsung |
| `transition_to_next_chapter` | Konfrontasi (ideologis) dengan Grandmaster |

### Chapter 4.3 — The Man Who Chose Fear
| Field | Value |
|---|---|
| `chapter_id` | `chapter_04_03` |
| `title` | The Man Who Chose Fear |
| `narrative_purpose` | Pengenalan Grandmaster sebagai figur ideologis kompleks — bukan villain, tapi seseorang yang mempertahankan sistem karena takut kehilangan orang lain lagi |
| `emotional_purpose` | Kompleksitas moral — pemain tidak bisa membencinya secara sederhana |
| `main_conflict` | Ideologis: "dunia membutuhkan cultivation" (Grandmaster) vs kebenaran yang baru ditemukan (protagonis) |
| `opening_state` | Origin of cultivation diketahui parsial |
| `closing_state` | Grandmaster relationship established sebagai kompleks (bukan hostile default); pemain memahami taruhan konkret jika sumber dihentikan (teknik runtuh, kerajaan runtuh, dst — MSB §19) |
| `key_characters` | `npc_grandmaster` (first meaningful appearance sebagai karakter, bukan sekadar figur otoritas jauh) |
| `key_locations` | `loc_grandmaster_chamber` [DESIGN GAP nama formal] |
| `main_quests` | `quest_a04_c03_003` |
| `optional_content` | Dialog tambahan dengan Grandmaster untuk relationship tinggi — MSB menyebutkan dialog khusus tersedia jika relationship/reputation cukup tinggi (baru payoff penuh di Arc VI, tapi dasar relationship dibangun di sini) |
| `mystery_progress` | Konteks untuk Mystery #4 — *mengapa* disembunyikan (bukan cuma *apa* yang disembunyikan) |
| `foreshadowing` | "Aku juga pernah menginginkannya. Lalu aku melihat apa yang terjadi setelahnya." — baris ini di-plant sebagai potential high-relationship dialogue, full payoff di Arc VI |
| `payoff` | Payoff dari Version III (memahami *mengapa* seseorang memilih menyembunyikan kebenaran alih-alih menghadapinya) |
| `chapter_climax` | Grandmaster mengakui sistem tidak sempurna, tanpa meminta maaf atau berjanji berubah |
| `transition_to_next_chapter` | Turun ke ruang terdalam Tian Xu |

### Chapter 4.4 — What Tian Xu Feeds On
| Field | Value |
|---|---|
| `chapter_id` | `chapter_04_04` |
| `title` | What Tian Xu Feeds On |
| `narrative_purpose` | Arc IV ending — penemuan formation raksasa yang menyerap energi seluruh akademi. Revelation institusional terbesar: Tian Xu bukan hanya menjaga segel, tapi memberi makan segel |
| `emotional_purpose` | Horor sistemik — protagonis sadar dirinya bagian dari sistem yang mengeksploitasi orang di sekitarnya |
| `main_conflict` | Puncak konflik institusional Arc IV — bukan combat, tapi realisasi moral |
| `opening_state` | Grandmaster relationship established; origin cultivation diketahui parsial |
| `closing_state` | Formation raksasa ditemukan; pemahaman penuh bahwa murid/guru/curriculum adalah bagian dari sistem; Arc IV selesai |
| `key_characters` | Tidak ada NPC baru — ini adalah discovery chapter |
| `key_locations` | `loc_tianxu_deepest_chamber` |
| `main_quests` | `quest_a04_c04_004` |
| `optional_content` | Tidak ada — climax Arc, wajib |
| `mystery_progress` | Mystery #5 ("Apa yang ada di bawah Tian Xu?") terjawab penuh |
| `foreshadowing` | Skala formation — foreshadowing untuk Spiritual Collapse (Arc V) |
| `payoff` | Payoff dari seluruh Arc IV, dan payoff tidak langsung dari "koridor bawah tanah" (foreshadowing element MSB §44 sejak Arc I) |
| `chapter_climax` | Melihat formation raksasa yang menggunakan energi seluruh akademi sebagai sumber daya |
| `transition_to_next_chapter` | **Arc IV → Arc V.** Pengetahuan sistemik ini menjadi prasyarat memahami skala Spiritual Collapse |

**`[DESIGN GAP]` Major Choice Arc IV (dari Phase 2):** setelah menganalisis density Arc IV, saya **tidak** menyisipkan choice besar terpisah di sini — MSB Section 45 menyatakan prinsip "pemain harus menentukan apakah menyebarkan kebenaran" secara umum, bukan spesifik untuk Arc IV. Rekomendasi: choice ini lebih tepat ditempatkan sebagai *ongoing state* yang bisa diaktifkan kapan saja sejak Chapter 4.2 hingga Arc V (menyebarkan sebagian dari Version I/II/III ke murid lain), bukan satu keputusan tunggal di satu chapter. Ini dicatat sebagai rekomendasi desain di bagian akhir dokumen, bukan diklaim sebagai keputusan final MSB.

---

## ARC V — THE WORLD THAT REMEMBERS (5 Chapter)

**Rasional jumlah:** Arc ini punya bobot terbesar dalam MSB — Spiritual Collapse (skala dunia), Repeating Events (mekanik unik), Found Family Crisis (emosional), Entity Speaks (revelation besar), dan Arc ending (revelation terbesar sejauh cerita: Jiang Yan mencoba membunuh Entity). Lima elemen besar ini masing-masing butuh chapter sendiri agar tidak saling menenggelamkan.

### Chapter 5.1 — The World Remembers Too
| Field | Value |
|---|---|
| `chapter_id` | `chapter_05_01` |
| `title` | The World Remembers Too |
| `narrative_purpose` | Pengenalan Spiritual Collapse sebagai world event skala besar (cultivation deviation, monster mutation, dead zones, spiritual storms, corrupted formations) |
| `emotional_purpose` | Dari horor sistemik personal (penutup Arc IV) menuju horor skala dunia |
| `main_conflict` | External murni — dunia mulai rusak, tidak ada single antagonist untuk disalahkan langsung |
| `opening_state` | Pengetahuan sistemik dari Arc IV |
| `closing_state` | Beberapa wilayah terkonfirmasi terdampak Spiritual Collapse; `world_event_a05_spiritual_collapse` aktif sebagai state |
| `key_characters` | Keempat anggota found family (bereaksi berbeda terhadap skala krisis — awal dari divergence yang akan pecah penuh di Chapter 5.3) |
| `key_locations` | Multiple affected regions (`[DESIGN GAP]` nama spesifik) |
| `main_quests` | `quest_a05_c01_001` |
| `optional_content` | Membantu wilayah terdampak secara lokal (world-building, menunjukkan skala manusiawi krisis) |
| `mystery_progress` | Konteks awal untuk Mystery #10 (mengapa sejarah berulang) — pemain mulai melihat pola, belum memahami mekanismenya |
| `foreshadowing` | Pola kejadian yang terasa familiar — foreshadowing Repeating Events |
| `payoff` | Payoff skala dari formation raksasa Arc IV |
| `chapter_climax` | Melihat wilayah pertama yang benar-benar rusak akibat Spiritual Collapse |
| `transition_to_next_chapter` | Menyadari salah satu event terasa seperti déjà vu yang sangat spesifik |

### Chapter 5.2 — Mountain Gate, Again
| Field | Value |
|---|---|
| `chapter_id` | `chapter_05_02` |
| `title` | Mountain Gate, Again |
| `narrative_purpose` | Repeating Event utama: `Mountain Gate Incident` — mekanik unik di mana protagonis menyadari peristiwa ini identik dengan catatan kehidupan pertama, dengan satu perbedaan: kali ini ia hadir |
| `emotional_purpose` | Urgensi tertinggi sejauh cerita — ini bukan lagi investigasi masa lalu, tapi kesempatan mengubah masa depan secara langsung |
| `main_conflict` | External konkret dengan stake nyata — gameplay choice yang menentukan apakah sejarah berubah atau terulang |
| `opening_state` | Pola Repeating Events mulai dikenali |
| `closing_state` | Salah satu dari dua outcome: `flag_mountain_gate_changed = true` (berhasil mengubah sejarah) atau `flag_mountain_gate_repeated = true` (tragedi terulang) — MSB eksplisit menyatakan dua outcome ini |
| `key_characters` | Bergantung pada outcome — bisa melibatkan NPC yang terancam di lokasi kejadian (`[DESIGN GAP]` detail siapa yang berisiko) |
| `key_locations` | `loc_mountain_gate` |
| `main_quests` | `quest_a05_c02_002` |
| `optional_content` | Tidak ada — ini adalah major gameplay choice dengan stake nyata, bukan opsional |
| `mystery_progress` | Mystery #10 mendapat bukti konkret pertama (bukan lagi pola abstrak) |
| `foreshadowing` | Hasil event ini (berubah/berulang) menjadi permanent world state yang direferensikan di ending (Phase 13) |
| `payoff` | Payoff dari "Siklus dimulai lagi" (Chapter 2.2) |
| `chapter_climax` | Momen keputusan/aksi Mountain Gate Incident itu sendiri |
| `transition_to_next_chapter` | Konsekuensi emosional dari hasil event ini terhadap found family |

### Chapter 5.3 — Cracks in the Family
| Field | Value |
|---|---|
| `chapter_id` | `chapter_05_03` |
| `title` | Cracks in the Family |
| `narrative_purpose` | Found Family Crisis — divergensi ideologis empat anggota kelompok (Lin Yue: lindungi murid; Shen Luo: hancurkan sistem; Mei Ruo: cari kebenaran penuh; Gu Han: Tian Xu tidak dapat diperbaiki) |
| `emotional_purpose` | Titik paling emosional sejauh cerita — kehilangan berpotensi terjadi bukan dari antagonist eksternal, tapi dari perbedaan nilai antar-sahabat |
| `main_conflict` | Internal kelompok — empat ideologi yang sama validnya, tidak ada yang "benar" secara objektif |
| `opening_state` | Hasil Mountain Gate Incident sebagai katalis; relationship state tiap anggota dari akumulasi pilihan Arc I-IV |
| `closing_state` | Konfigurasi found family final ditentukan — kemungkinan hasil bervariasi dari "tetap solid" hingga "satu atau lebih anggota berpisah/menjadi disillusioned" (sesuai possible_states tiap karakter di MSB §37) |
| `key_characters` | Keempat anggota found family — chapter ini adalah puncak character arc mereka masing-masing |
| `key_locations` | Tempat berkumpul kelompok (lokasi personal, kontras dengan skala dunia di chapter sebelumnya) |
| `main_quests` | `quest_a05_c03_003` — MSB catatan: "Pilihan pemain menentukan hubungan mereka. Tidak semua karakter harus tetap menjadi sahabat" |
| `optional_content` | Percakapan individual dengan tiap anggota sebelum keputusan akhir — memberi pemain kesempatan memahami perspektif masing-masing sebelum crisis memuncak |
| `mystery_progress` | Tidak ada progress mystery — chapter ini murni character-driven |
| `foreshadowing` | Konfigurasi final di sini menjadi prasyarat untuk seluruh character end state di Phase 13 (Ending Matrix) |
| `payoff` | Payoff dari seluruh relationship-building sejak Arc I Chapter 1.2 |
| `chapter_climax` | Momen di mana perpecahan (jika terjadi) menjadi eksplisit dan tidak dapat dibatalkan |
| `transition_to_next_chapter` | Entity muncul di tengah krisis emosional ini — timing yang disengaja, bukan kebetulan |

### Chapter 5.4 — The Voice Beneath Everything
| Field | Value |
|---|---|
| `chapter_id` | `chapter_05_04` |
| `title` | The Voice Beneath Everything |
| `narrative_purpose` | Entity berbicara langsung untuk pertama kali — "Kau membunuhku sekali" dan "Aku adalah alasan kalian menyebut dunia ini sebagai anugerah" |
| `emotional_purpose` | Dari kehancuran personal (Ch 5.3) menuju kengerian eksistensial skala kosmik |
| `main_conflict` | Konfrontasi langsung pertama dengan Entity — bukan combat, tapi dialog yang mengguncang pemahaman pemain tentang siapa villain sebenarnya |
| `opening_state` | Konfigurasi found family final; pemahaman origin cultivation dari Arc IV |
| `closing_state` | Entity dikonfirmasi sebagai entitas yang pernah "dibunuh" oleh protagonis di kehidupan pertama; pertanyaan besar terbuka tentang siapa sebenarnya villain dalam cerita ini |
| `key_characters` | Entity (first direct communication) |
| `key_locations` | `[DESIGN GAP]` — lokasi kemunculan Entity, kemungkinan terhubung dengan formation raksasa Arc IV atau lokasi Spiritual Collapse terparah |
| `main_quests` | `quest_a05_c04_004` |
| `optional_content` | Tidak ada — revelation inti wajib |
| `mystery_progress` | Mystery #7 (Apa itu Entity?) dibuka signifikan; Mystery #8 (Apa yang terjadi di kehidupan pertama?) mendapat clue besar pertama ("kau membunuhku sekali") |
| `foreshadowing` | "Aku adalah alasan kalian menyebut dunia ini sebagai anugerah" — foreshadowing untuk Entity's Truth penuh di Arc VII |
| `payoff` | Payoff dari seluruh buildup Entity sejak disebutkan pertama kali di Arc IV (origin cultivation) |
| `chapter_climax` | Kalimat "Kau membunuhku sekali" |
| `transition_to_next_chapter` | Memory besar tentang percobaan membunuh Entity |

### Chapter 5.5 — What I Tried to Kill
| Field | Value |
|---|---|
| `chapter_id` | `chapter_05_05` |
| `title` | What I Tried to Kill |
| `narrative_purpose` | Arc V ending — memory besar: Jiang Yan mencoba membunuh Entity (bukan membebaskannya, mengoreksi kesimpulan Arc III), gagal, lalu menciptakan Cycle Formation sebagai solusi darurat |
| `emotional_purpose` | Rekontekstualisasi besar — apa yang dikira pemain sebagai "villain origin story" ternyata adalah kegagalan seseorang yang mencoba melakukan hal benar dengan cara yang salah |
| `main_conflict` | Internal — klimaks tema Consequence: setiap tindakan Jiang Yan (dan sekarang protagonis) punya konsekuensi berantai |
| `opening_state` | Entity's partial truth dari Chapter 5.4 |
| `closing_state` | Memory percobaan membunuh Entity lengkap; Cycle Formation diketahui sebagai *hasil dari kegagalan*, bukan rencana besar yang berhasil; Arc V selesai |
| `key_characters` | Tidak ada NPC baru — momen memory soliter |
| `key_locations` | Terhubung dengan lokasi memory sebelumnya |
| `main_quests` | `quest_a05_c05_005` |
| `optional_content` | Tidak ada — climax Arc |
| `mystery_progress` | Mystery #8 terjawab signifikan (walau detail penuh First Betrayal dan The Gate masih tertutup untuk Arc VI); Mystery #9 (Cycle Formation) dibuka |
| `foreshadowing` | Detail "solusi darurat" — foreshadowing untuk pemahaman penuh The Gate dan First Betrayal (Arc VI) |
| `payoff` | Payoff besar: mengoreksi kesimpulan Arc III ("aku mungkin penyebab tragedi") — sekarang jelas lebih kompleks: mencoba mencegah tragedi, gagal, lalu tragedi baru muncul dari kegagalan itu |
| `chapter_climax` | Melihat momen kegagalan itu sendiri — Entity tidak bisa dibunuh tanpa menghancurkan sumber cultivation |
| `transition_to_next_chapter` | **Arc V → Arc VI.** Konfigurasi found family final + pengetahuan Cycle Formation menjadi starting state Arc VI |

---

## ARC VI — THE LAST CYCLE (4 Chapter)

**Rasional jumlah:** MSB §26-31 memberi empat blok revelation berurutan dengan bobot setara (Truth of Jiang Yan, First Betrayal, The Gate, Final Choice) — masing-masing layak satu chapter agar forgiveness (tema Arc) terasa sebagai proses bertahap, bukan satu ledakan informasi.

### Chapter 6.1 — Someone Like Me
| Field | Value |
|---|---|
| `chapter_id` | `chapter_06_01` |
| `title` | Someone Like Me |
| `narrative_purpose` | The Truth of Jiang Yan — pengungkapan bahwa Jiang Yan bukan chosen one, memulai dari nol persis seperti protagonis, dengan found family serupa |
| `emotional_purpose` | Empati alih-alih horor — untuk pertama kalinya protagonis (dan pemain) melihat Jiang Yan sebagai manusia biasa, bukan figur misterius yang menakutkan |
| `main_conflict` | Internal — mulai bergesernya sikap dari takut/menolak identitas menuju memahami |
| `opening_state` | `state_identity_stance` dari Arc III sebagai modifier; pengetahuan Cycle Formation dari Arc V |
| `closing_state` | Paralel penuh antara perjalanan Jiang Yan dan perjalanan protagonis diketahui |
| `key_characters` | Jiang Yan (sebagai figur historis, belum sebagai imprint langsung — itu Arc VII) |
| `key_locations` | Rekaman/catatan sejarah personal Jiang Yan (`[DESIGN GAP]` lokasi spesifik) |
| `main_quests` | `quest_a06_c01_001` |
| `optional_content` | Membandingkan detail spesifik found family Jiang Yan dengan found family protagonis (world-building yang memperkuat tema paralel) |
| `mystery_progress` | Mystery #2 terjawab signifikan |
| `foreshadowing` | Paralel found family — foreshadowing untuk momen "Aku bukan kau" di Arc VII (kontras, bukan kesamaan, yang akhirnya jadi kunci) |
| `payoff` | Payoff dari "Someone Like Me" — mengoreksi seluruh asumsi awal bahwa Jiang Yan adalah figur besar/istimewa |
| `chapter_climax` | Menyadari kesamaan struktural antara kedua kehidupan |
| `transition_to_next_chapter` | Pengungkapan bahwa Jiang Yan meminta bantuan seseorang — dan dikhianati |

### Chapter 6.2 — The Betrayal That Wasn't
| Field | Value |
|---|---|
| `chapter_id` | `chapter_06_02` |
| `title` | The Betrayal That Wasn't |
| `narrative_purpose` | The First Betrayal — pengkhianatan yang ternyata adalah upaya mencegah Jiang Yan karena takut terhadap rencananya, bukan pengkhianatan sederhana demi keuntungan |
| `emotional_purpose` | Kompleksitas moral lanjutan — mengajarkan pemain (lewat parallel Jiang Yan) bahwa "pengkhianatan" bisa lahir dari kepedulian, bukan hanya self-interest |
| `main_conflict` | Historis/naratif — bukan konflik langsung protagonis, tapi konflik yang dialami lewat memory/investigasi |
| `opening_state` | Paralel found family diketahui |
| `closing_state` | Identitas dan motivasi si "pengkhianat" diketahui penuh (`[DESIGN GAP]` — MSB tidak menyebut nama spesifik orang ini, hanya "seseorang") |
| `key_characters` | `[DESIGN GAP]` — NPC historis yang berperan sebagai "pengkhianat" Jiang Yan; kemungkinan kuat terhubung dengan salah satu karakter yang sudah ada (Mentor adalah kandidat terkuat mengingat MSB §38 eksplisit menyatakan Mentor "pernah mengenal Jiang Yan") |
| `key_locations` | `[DESIGN GAP]` |
| `main_quests` | `quest_a06_c02_002` |
| `optional_content` | Investigasi tambahan untuk memverifikasi identitas si "pengkhianat" sebelum reveal penuh |
| `mystery_progress` | Detail baru untuk Mystery #8 |
| `foreshadowing` | Ini adalah pembuka langsung untuk Mentor Arc revelation ("Cara kau memegang pedang... aku pernah melihatnya") jika direkomendasikan bahwa si pengkhianat = Mentor |
| `payoff` | Payoff dari kompleksitas moral yang sudah dibangun sejak Grandmaster arc (Arc IV) — pola berulang bahwa "antagonist" dalam cerita ini selalu punya alasan yang dapat dipahami |
| `chapter_climax` | Reveal identitas dan motivasi si pengkhianat |
| `transition_to_next_chapter` | Terlepas dari pengkhianatan, Jiang Yan melanjutkan rencananya — menuju The Gate |

**Rekomendasi desain (bukan canon):** mengidentifikasi si "pengkhianat" sebagai Mentor akan memberi payoff ganda — baik untuk Mystery #8 maupun untuk Mentor Arc revelation yang sudah eksplisit di MSB §38. Ini konsisten secara struktural (MSB menyatakan Mentor "pernah mengenal Jiang Yan" tapi "tidak mengetahui bahwa protagonis sekarang adalah Jiang Yan") namun **MSB tidak secara eksplisit menyatakan Mentor adalah si pengkhianat** — ini murni inferensi desain yang ditandai terpisah di sini, bukan diklaim sebagai fakta MSB.

### Chapter 6.3 — The Gate, The Formation, The Cost
| Field | Value |
|---|---|
| `chapter_id` | `chapter_06_03` |
| `title` | The Gate, The Formation, The Cost |
| `narrative_purpose` | The Gate — Jiang Yan membuka gerbang menuju sumber asli cultivation (bukan membebaskan Entity), mencoba memisahkan Entity dari sumber, eksperimen gagal, Cycle Formation tercipta sebagai tindakan darurat terakhir |
| `emotional_purpose` | Klimaks revelation Arc — kalimat "Kalau dunia harus membenciku, biarkan" (Arc III) akhirnya dipahami penuh: bukan ancaman, tapi kesediaan menanggung kesalahpahaman demi mencoba menyelamatkan dunia |
| `main_conflict` | Historis — puncak dari seluruh mystery chain sejak Arc III |
| `opening_state` | Identitas pengkhianat diketahui; found family paralel dipahami |
| `closing_state` | Detail penuh The Gate diketahui; real meaning of Second Life terbuka penuh ("kesempatan eksperimental," bukan hadiah/takdir) |
| `key_characters` | Jiang Yan (via memory) |
| `key_locations` | `loc_the_gate` (lokasi historis, kemungkinan sama dengan `loc_tianxu_deepest_chamber` Arc IV) |
| `main_quests` | `quest_a06_c03_003` |
| `optional_content` | Tidak ada — revelation inti terbesar cerita, wajib dialami penuh |
| `mystery_progress` | Mystery #9 (Cycle Formation) terjawab penuh; Mystery #11 (apa yang sebenarnya dilakukan Jiang Yan) terjawab penuh; Mystery #12 (makna Second Life) terjawab penuh |
| `foreshadowing` | N/A — ini adalah payoff chapter untuk hampir semua foreshadowing sejak Arc I-V |
| `payoff` | Payoff terbesar dalam dokumen ini: kalimat Arc III, catatan "Siklus dimulai lagi" Arc II, formation Arc IV, Entity's partial truth Arc V — semua bertemu di sini |
| `chapter_climax` | Memahami bahwa Second Life bukan rencana yang berhasil, tapi solusi darurat dari kegagalan |
| `transition_to_next_chapter` | Mentor's personal revelation |

### Chapter 6.4 — What the Sword Remembers
| Field | Value |
|---|---|
| `chapter_id` | `chapter_06_04` |
| `title` | What the Sword Remembers |
| `narrative_purpose` | Mentor Arc revelation ("Cara kau memegang pedang... aku pernah melihatnya") + Final Choice Before Endgame (Preserve/Destroy/Transform/Sacrifice) — Arc VI ending |
| `emotional_purpose` | Dari revelation informasional (Ch 6.3) kembali ke personal — forgiveness tema dibayar penuh lewat momen intim dengan Mentor, sebelum pemain harus membuat keputusan terbesar sejauh ini |
| `main_conflict` | Internal — menentukan prinsip yang akan dibawa ke final act |
| `opening_state` | Real meaning of Second Life diketahui penuh |
| `closing_state` | Mentor relationship mendapat emotional payoff besar; salah satu dari empat prinsip (Preserve/Destroy/Transform/Sacrifice) dipilih sebagai `state_final_principle`; Arc VI selesai |
| `key_characters` | `npc_mentor` (revelation terbesar karakter ini) |
| `key_locations` | Tempat latihan personal dengan Mentor (kontras intim dengan skala The Gate) |
| `main_quests` | `quest_a06_c04_004` |
| `optional_content` | Percakapan mendalam dengan Mentor sebelum Final Choice (opsional tapi sangat direkomendasikan untuk emotional payoff penuh) |
| `mystery_progress` | Tidak ada mystery baru — chapter ini adalah emotional payoff murni |
| `foreshadowing` | `state_final_principle` menjadi jalur dominan (bukan pengunci mutlak) untuk Arc VII, sesuai catatan eksplisit MSB §31 |
| `payoff` | Payoff dari seluruh Mentor Arc sejak first_appearance (kemungkinan Arc I, `[DESIGN GAP]` — MSB tidak eksplisit menyebut kapan Mentor pertama muncul, akan diformalkan Phase 9) |
| `chapter_climax` | Momen Mentor mengucapkan "Cara kau memegang pedang... Aku pernah melihatnya" |
| `transition_to_next_chapter` | **Arc VI → Arc VII.** `state_final_principle` + seluruh state akumulasi menjadi starting condition final act |

---

## ARC VII — SECOND LIFE (3 Chapter)

**Rasional jumlah:** MSB eksplisit menyatakan prinsip pacing untuk Arc ini — "Tidak ada lagi quest yang terasa seperti side activity" (§32). Ini adalah sinyal desain kuat untuk *memadatkan*, bukan memperbanyak chapter. Tiga chapter (The Last Night → Final Confrontation → Final Decision) memberi struktur climax tiga-babak klasik tanpa mengulur momentum.

### Chapter 7.1 — The Last Night
| Field | Value |
|---|---|
| `chapter_id` | `chapter_07_01` |
| `title` | The Last Night |
| `narrative_purpose` | Tian Xu di ambang kehancuran; formation gagal; Entity mulai keluar; faksi bergerak; setiap karakter mengambil posisi berdasarkan seluruh perjalanan pemain |
| `emotional_purpose` | Urgensi puncak — semua yang dibangun sejak Arc I sekarang aktif secara bersamaan |
| `main_conflict` | Puncak konflik eksternal skala dunia + puncak posisi seluruh faksi |
| `opening_state` | `state_final_principle` dan seluruh state akumulasi Arc I-VI |
| `closing_state` | Posisi final tiap karakter/faksi terkonfirmasi; jalan menuju bawah Tian Xu terbuka |
| `key_characters` | Seluruh cast — found family (konfigurasi final dari Arc V), Mentor, Grandmaster, Shen Luo, perwakilan tiap faksi |
| `key_locations` | Seluruh Tian Xu dalam kondisi krisis (`loc_tianxu_main_hall`, dan lokasi-lokasi Arc sebelumnya kini dalam state "crisis") |
| `main_quests` | `quest_a07_c01_001` |
| `optional_content` | Percakapan singkat dengan tiap karakter sebelum turun (MSB: "semua hubungan yang dibangun mulai membayar hasilnya" — momen terakhir untuk melihat payoff relationship secara eksplisit sebelum climax) |
| `mystery_progress` | Tidak ada mystery baru — murni konvergensi state |
| `foreshadowing` | N/A |
| `payoff` | Payoff relationship terbesar dalam dokumen — setiap pilihan sejak Arc I terlihat hasilnya di sini secara simultan |
| `chapter_climax` | Momen protagonis memutuskan turun ke bawah Tian Xu |
| `transition_to_next_chapter` | Final Confrontation |

### Chapter 7.2 — I Am Not You
| Field | Value |
|---|---|
| `chapter_id` | `chapter_07_02` |
| `title` | I Am Not You |
| `narrative_purpose` | Final Confrontation dengan Jiang Yan imprint + Entity's Truth lengkap — titik paling penting seluruh campaign (MSB eksplisit menyebutnya demikian) |
| `emotional_purpose` | Klimaks tema Identity dan Choice sekaligus — momen penolakan protagonis terhadap kendali kehidupan pertamanya |
| `main_conflict` | Puncak konflik internal (Identity) beririsan dengan puncak konflik eksternal (Entity, Tian Xu runtuh) |
| `opening_state` | Posisi final seluruh cast dari Chapter 7.1 |
| `closing_state` | "Aku bukan kau" diucapkan; Entity's Truth lengkap diketahui; kondisi Hidden Resolution (jika terpenuhi) menjadi dapat diakses di chapter berikutnya |
| `key_characters` | Jiang Yan imprint (bukan tubuh/hantu — "imprint kesadaran"), Entity |
| `key_locations` | Ruang terdalam Tian Xu (di bawah `loc_tianxu_deepest_chamber`) |
| `main_quests` | `quest_a07_c02_002` |
| `optional_content` | Tidak ada — ini adalah klimaks wajib tanpa jalur opsional |
| `mystery_progress` | Seluruh mystery yang belum terjawab (jika ada) dituntaskan di sini; Entity's Truth (§34 MSB) diungkapkan penuh |
| `foreshadowing` | N/A — payoff murni |
| `payoff` | Payoff terbesar: "Aku bukan kau" sebagai jawaban naratif terhadap seluruh perjalanan identitas sejak Arc III |
| `chapter_climax` | "Aku bukan kau." |
| `transition_to_next_chapter` | Final Decision |

### Chapter 7.3 — Second Life
| Field | Value |
|---|---|
| `chapter_id` | `chapter_07_03` |
| `title` | Second Life |
| `narrative_purpose` | FINAL DECISION — pemain memilih di antara empat ending path utama, dengan Hidden Resolution tersedia jika kombinasi kondisi terpenuhi |
| `emotional_purpose` | Resolusi — beragam tergantung ending yang dicapai, dari kelegaan pahit hingga harapan penuh |
| `main_conflict` | Resolusi dari seluruh konflik campaign |
| `opening_state` | "Aku bukan kau" diucapkan; Entity's Truth diketahui; kondisi Hidden Resolution dicek terhadap seluruh state permainan |
| `closing_state` | Salah satu dari 5 ending tercapai; epilogue state ditampilkan |
| `key_characters` | Bergantung pada ending — akan diformalkan penuh di Phase 13 (Ending Matrix) |
| `key_locations` | Bervariasi per ending |
| `main_quests` | `quest_a07_c03_003` (FINAL DECISION sebagai satu quest dengan lima kemungkinan resolusi) |
| `optional_content` | Tidak ada |
| `mystery_progress` | Mystery #12 (makna Second Life) mendapat jawaban final — berbeda kedalamannya tergantung ending yang dicapai |
| `foreshadowing` | N/A |
| `payoff` | Payoff dari seluruh 7 Arc sebagai satu kesatuan |
| `chapter_climax` | Momen keputusan final itu sendiri |
| `transition_to_next_chapter` | N/A — akhir campaign. Epilogue per ending di Phase 13 |

---

## Ringkasan Jumlah Chapter per Arc

| Arc | Jumlah Chapter | Total (Running) |
|---|---|---|
| I — A New Life | 4 | 4 |
| II — The First Trial | 4 | 8 |
| III — Echoes of Another Self | 5 | 13 |
| IV — The False History | 4 | 17 |
| V — The World That Remembers | 5 | 22 |
| VI — The Last Cycle | 4 | 26 |
| VII — Second Life | 3 | 29 |

**29 Chapter total.** Distribusi tidak rata secara sengaja — Arc III dan V (5 chapter masing-masing) adalah titik-titik dengan bobot revelation/emosional terbesar di paruh pertama dan kedua campaign; Arc VII (3 chapter) sengaja paling padat sesuai prinsip MSB eksplisit.

---

## Design Gap Recommendations (Ringkasan Fase Ini)

Berikut seluruh `[DESIGN GAP]` yang muncul di fase ini, dengan rekomendasi terpisah dari spesifikasi:

1. **Pavilion roster (Arc I)** — belum direkomendasikan konkret di fase ini; akan diformalkan di Phase 9 (NPC/Location Bible) karena butuh nama guru + filosofi + lokasi sekaligus untuk konsisten.
2. **Nama-nama lokasi spesifik** (banyak `[DESIGN GAP]` tersebar) — akan diformalkan penuh di Phase 9 (Location Bible), sengaja tidak diisi di sini untuk menghindari penamaan tergesa yang tidak konsisten dengan katalog NPC/Location final.
3. **Identitas "pengkhianat" Jiang Yan (Chapter 6.2)** — rekomendasi: Mentor, dengan alasan struktural (payoff ganda untuk Mystery #8 + Mentor Arc revelation §38). **Ditandai eksplisit sebagai inferensi, bukan fakta MSB.**
4. **Major Choice Arc IV** — direkomendasikan sebagai *ongoing state* (menyebarkan kebenaran secara bertahap) alih-alih satu keputusan tunggal, berdasarkan prinsip umum MSB §45. **Bukan keputusan final MSB.**
5. **Apakah found family bisa berbeda pendapat di First Major Choice Arc II (Chapter 2.3)** — dicatat sebagai opsi desain, belum diputuskan. Direkomendasikan: TIDAK — MSB menyatakan found family baru benar-benar terpecah di Arc V (Chapter 5.3), sehingga perbedaan pendapat eksplisit di Arc II berisiko mendahului payoff emosional Found Family Crisis yang seharusnya jadi momen unik Arc V.

Kelima gap ini akan direview ulang saat Phase 4 (Quest Graph) dan Phase 9 (NPC/Location Bible) — tidak ada yang dianggap final di sini.

---

**File berikutnya:** `03-quest-graph.md` — Main Quest dan Branching Quest lengkap dengan causal chain (state read/write), mengikuti template Phase 3-4 dari brief asli.
