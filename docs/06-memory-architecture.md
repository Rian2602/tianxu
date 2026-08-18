# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 06. Memory Bible

**Status:** DRAFT — Phase 7 of 18
**Depends on:** `03-quest-graph-arc1-2.md`, `03b-quest-graph-arc3-7.md` (sumber seluruh `memory_id`), `04-character-arcs.md`
**Cakupan:** delapan memory_id yang sudah tertanam di Quest Graph. Tidak ada memory baru ditambahkan di fase ini — tujuan fase ini adalah memformalkan struktur internal tiap memory yang sudah punya trigger, bukan menciptakan trigger baru.

**Prinsip wajib:** setiap memory mengikuti alur `Fragment → Interpretation → Contradiction → Investigation → Revelation → Recontextualization`. Tidak ada memory yang langsung menjelaskan dirinya sendiri secara penuh saat pertama muncul.

---

## `memory_a01_m01` — The Burning Corridor

| Field | Value |
|---|---|
| `memory_id` | `memory_a01_m01` |
| `title` | The Burning Corridor |
| `arc` | `arc_01` |
| `trigger_type` | Automatic (cutscene), tidak memerlukan aksi pemain |
| `trigger_condition` | Awal `quest_a01_c01_001`, saat protagonis dalam perjalanan menuju Tian Xu |
| `fragment` | Koridor terbakar. Tidak ada wajah terlihat. Suara berteriak: "Jangan buka gerbang itu!" Protagonis terbangun sebelum mengetahui siapa yang bicara |
| `sensory_detail` | Panas, asap, suara berteriak yang terdistorsi (khas mimpi) — TIDAK ada detail visual wajah/identitas, disengaja |
| `emotional_imprint` | Disorientasi netral, bukan ketakutan eksplisit — ini penting agar tone Arc I tetap "kehidupan baru," bukan horror sejak awal |
| `reliability` | RENDAH — ini adalah fragment paling mentah dalam seluruh campaign, sengaja tanpa konteks apa pun |
| `misleading_elements` | Pemain kemungkinan akan mengasumsikan "gerbang" merujuk pada sesuatu yang literal dan dekat (mis. gerbang Tian Xu itu sendiri) — padahal gerbang yang dimaksud adalah The Gate yang baru terungkap penuh di Arc VI, sebuah objek yang jauh lebih abstrak dan jauh dalam waktu |
| `related_npc` | Tidak ada — suara tidak teridentifikasi hingga jauh kemudian |
| `related_location` | Koridor terbakar — TIDAK pernah dikonfirmasi sebagai lokasi fisik spesifik di dunia nyata; ini kemungkinan representasi simbolis dari The Gate, bukan tempat literal (`[DESIGN GAP]` — apakah ada lokasi fisik yang identik, direkomendasikan TIDAK ada, untuk mempertahankan ambiguitas dream-logic) |
| `related_quest` | `quest_a01_c01_001` |
| `related_item` | Tidak ada |
| `related_event` | Foreshadowing untuk The Gate (Arc VI, Chapter 6.3) |
| `initial_interpretation` | Pemain kemungkinan menganggap ini sekadar mimpi buruk generik pembuka cerita, atau — jika sudah familiar dengan genre — curiga ini pertanda sesuatu yang lebih besar tapi tanpa arah jelas |
| `later_contradiction` | Tidak ada contradiction langsung — memory ini tidak pernah "salah," ia hanya sangat tidak lengkap. Ketidaklengkapannya sendiri adalah bagian dari desain (bandingkan dengan `memory_a03_m01` yang aktif menyesatkan) |
| `true_context` | Ini adalah echo dari momen tepat sebelum Jiang Yan membuka The Gate — suara yang berteriak "Jangan buka gerbang itu!" adalah suara si "pengkhianat" (rekomendasi: Mentor) yang mencoba mencegahnya, sesaat sebelum The Gate dibuka |
| `revelation_arc` | Fragment ini tidak "direvelasikan" secara terpisah — maknanya baru genap dipahami retrospektif setelah Chapter 6.2 (identitas pengkhianat) DAN Chapter 6.3 (The Gate penuh) keduanya diketahui |
| `payoff_arc` | Arc VI (Chapter 6.2-6.3) |
| `state_changes` | **Writes:** `flag_dream_a01_01_seen = true` (sudah tercatat di Quest Graph) |
| `unlocked_content` | Tidak ada konten baru dibuka langsung — fragment ini murni foreshadowing |

---

## `memory_a01_m02` — Hands That Remember

| Field | Value |
|---|---|
| `memory_id` | `memory_a01_m02` |
| `title` | Hands That Remember |
| `arc` | `arc_01` |
| `trigger_type` | Contextual — dipicu saat protagonis mencoba gerakan cultivation dasar pertama kali |
| `trigger_condition` | Selama `quest_a01_c02_003` |
| `fragment` | Bukan visual/naratif seperti memory lain — ini adalah body memory: tangan dan tubuh protagonis "tahu" cara melakukan sebuah teknik dasar sebelum diajarkan penuh, gerakan yang terasa sudah dikuasai |
| `sensory_detail` | Kinestetik murni — sensasi familiaritas otot/gerakan, bukan gambar atau suara |
| `emotional_imprint` | Kejutan ringan, cepat berlalu — protagonis kemungkinan menganggapnya bakat alami di titik ini, bukan sesuatu yang mencurigakan |
| `reliability` | RENDAH-SEDANG — body memory jenis ini secara umum lebih dapat dipercaya sebagai "sesuatu memang terjadi" tapi tidak memberi konteks APA yang terjadi |
| `misleading_elements` | Guru dan NPC lain kemungkinan menginterpretasikan ini sebagai bakat alami protagonis, memperkuat kesan "murid berbakat tersembunyi" — sebuah trope yang MSB secara eksplisit ingin dihindari (protagonis "tidak ada legenda"); penting bagi produksi untuk TIDAK membiarkan interpretasi ini menjadi validasi berlebihan yang bertentangan dengan premis "murid biasa" |
| `related_npc` | Tidak ada |
| `related_location` | Ruang latihan umum |
| `related_quest` | `quest_a01_c02_003` |
| `related_item` | Tidak ada |
| `related_event` | Foreshadowing "Technique" (MSB §44) |
| `initial_interpretation` | Bakat alami / keberuntungan |
| `later_contradiction` | Tidak ada contradiction eksplisit tercatat di MSB — `[DESIGN GAP]` apakah teknik spesifik ini dikonfirmasi sebagai teknik yang pernah dipakai Jiang Yan. Direkomendasikan: YA, teknik dasar yang sama, dikonfirmasi kembali secara implisit saat memory Jiang Yan penuh muncul di Arc VI — memberi momen "oh, itu sebabnya" tanpa memerlukan dialog eksplisit baru |
| `true_context` | Cultivation adalah keterampilan yang sama dipelajari dua kali oleh orang yang sama (dalam dua kehidupan) — body memory adalah residu paling literal dari Cycle Formation |
| `revelation_arc` | Tidak ada revelation quest tersendiri — payoff bersifat implisit/retrospektif |
| `payoff_arc` | Arc VI (retrospektif, tanpa quest dedicated) |
| `state_changes` | Tidak menulis state baru — murni tekstural/atmosferik |
| `unlocked_content` | Tidak ada |

---

## `memory_a01_m03` — What the Formation Remembers

| Field | Value |
|---|---|
| `memory_id` | `memory_a01_m03` |
| `title` | What the Formation Remembers |
| `arc` | `arc_01` |
| `trigger_type` | Contextual — dipicu menyentuh formation tua |
| `trigger_condition` | Selama `quest_a01_c04_005` |
| `fragment` | Formation tua yang sama, tapi dalam kondisi hancur. Tidak ada narasi lengkap, hanya citra visual singkat |
| `sensory_detail` | Visual: keretakan, cahaya formation yang meredup/pecah. Tidak ada suara atau dialog dalam fragment ini |
| `emotional_imprint` | Kengerian samar yang tidak sepenuhnya dipahami protagonis — reaksi tubuh (jantung berdebar) lebih kuat dari pemahaman kognitif |
| `reliability` | SEDANG — visual jelas, tapi tanpa konteks temporal (kapan formation ini hancur? apakah formation yang SAMA dengan yang disentuh sekarang, atau formation yang berbeda?) |
| `misleading_elements` | Pemain berpotensi mengasumsikan formation yang disentuh SEKARANG akan/sudah hancur — padahal fragment ini kemungkinan adalah preview dari kondisi formation SETELAH peristiwa Arc VI (The Gate), bukan kondisinya saat ini atau di masa lalu literal |
| `related_npc` | Tidak ada |
| `related_location` | Formation tua di wilayah sekitar akademi (lokasi sama dengan trigger) |
| `related_quest` | `quest_a01_c04_005` |
| `related_item` | Tidak ada |
| `related_event` | Terhubung dengan The Gate (Arc VI) dan kemungkinan dengan formation raksasa (Arc IV) — `[DESIGN GAP]` apakah ini formation YANG SAMA dengan `loc_tianxu_deepest_chamber`, direkomendasikan TIDAK (untuk menghindari over-koinsidensi), melainkan formation kecil yang terhubung secara jaringan/sistem dengan formation utama, konsisten dengan gagasan bahwa "seluruh akademi" adalah bagian dari sistem (MSB §20) |
| `initial_interpretation` | Firasat buruk generik, atau — bagi pemain yang sudah curiga — indikasi bahwa "sesuatu yang buruk akan/sudah terjadi pada formation ini" |
| `later_contradiction` | Dikontraskan halus oleh Arc IV (`quest_a04_c04_004`) — formation yang ditemukan di sana masih UTUH dan berfungsi (menyerap energi), bukan hancur seperti fragment ini. Ini menciptakan ketegangan produktif: apakah fragment ini masa depan, masa lalu, atau formation yang berbeda? |
| `true_context` | Fragment ini adalah preview dari kondisi formation SETELAH Chapter 7.1 (The Last Night — "formation mulai gagal") — sebuah bentuk foreshadowing non-linear yang genuinely ambigu hingga late-game, bukan sekadar informasi tertunda |
| `revelation_arc` | Dipahami penuh hanya retrospektif setelah pemain mengalami Chapter 7.1 dan menyadari kecocokannya dengan fragment Arc I |
| `payoff_arc` | Arc VII (Chapter 7.1) |
| `state_changes` | **Writes:** kontribusi ke `flag_formation_touched = true` (sudah tercatat di Quest Graph) |
| `unlocked_content` | Tidak ada langsung |

**Catatan produksi penting:** memory ini adalah satu-satunya dalam katalog yang payoff-nya berada di ARC TERAKHIR meski triggernya di ARC PERTAMA — rentang foreshadowing terpanjang dalam seluruh dokumen. Ini secara eksplisit mewujudkan prinsip MSB §26 ("memory sederhana di Arc I yang baru dipahami pada Arc VI lebih bernilai daripada exposition panjang").

---

## `memory_a01_m04` — Don't Trust the History

| Field | Value |
|---|---|
| `memory_id` | `memory_a01_m04` |
| `title` | Don't Trust the History |
| `arc` | `arc_01` |
| `trigger_type` | Automatic (cutscene malam hari) |
| `trigger_condition` | Malam setelah `quest_a01_c04_005`, bagian dari `quest_a01_c04_006` |
| `fragment` | Protagonis melihat dirinya sendiri (wajah masih tidak terlihat). Seseorang berdiri di depannya, berkata: "Kalau kau kembali, jangan percaya sejarah." Terbangun, menemukan symbol kuno di meja kamar yang tangannya "tahu" cara menggambar |
| `sensory_detail` | Visual (dua sosok, tanpa wajah jelas), auditori (kalimat spesifik), lalu transisi ke tactile saat terbangun (symbol fisik di tangan) — memory ini unik karena berakhir dengan bukti FISIK yang persisten ke dunia nyata, bukan cuma sensasi mimpi |
| `emotional_imprint` | Urgensi — ini adalah titik di mana "rasa janggal" beralih menjadi "aku harus mencari tahu," ditandai eksplisit sebagai emotional turning point Arc I di Phase 2 |
| `reliability` | SEDANG-TINGGI — kalimat "jangan percaya sejarah" terbukti akurat sebagai instruksi (sejarah resmi memang tidak dapat dipercaya, dikonfirmasi Arc IV), tapi SIAPA yang mengucapkannya tidak diketahui hingga jauh kemudian |
| `misleading_elements` | Pemain mungkin mengasumsikan sosok yang bicara adalah figur protektif/mentor dari masa lalu — bisa jadi benar (jika direkomendasikan sebagai Mentor) atau bisa disalahartikan sebagai peringatan dari pihak antagonistik |
| `related_npc` | `[DESIGN GAP — REKOMENDASI: sosok yang sama dengan memory_a01_m01, kemungkinan Mentor]` |
| `related_location` | Kamar/asrama protagonis (untuk bagian bangun), lokasi mimpi tidak terverifikasi |
| `related_quest` | `quest_a01_c04_006` |
| `related_item` | `item_ancient_symbol` — item ini LAHIR dari memory ini, bukan sekadar dipicu olehnya |
| `related_event` | Foreshadowing "Symbol" dan "Phrase" (MSB §44, dua elemen foreshadowing terpisah yang bertemu dalam satu memory ini) |
| `initial_interpretation` | Peringatan dari seseorang yang peduli pada protagonis, meski identitasnya belum diketahui |
| `later_contradiction` | Tidak ada contradiction langsung terhadap ISI pesan — "jangan percaya sejarah" tetap valid sepanjang cerita. Yang berkembang adalah pemahaman tentang SIAPA yang mengatakannya dan MENGAPA (jika rekomendasi Mentor-sebagai-pengkhianat diterima, pesan ini adalah gema dari upayanya mencegah Jiang Yan, ditransmisikan entah bagaimana melalui Cycle Formation) |
| `true_context` | Jika direkomendasikan sebagai suara Mentor: ini adalah pesan yang "bocor" melalui mekanisme Cycle Formation — sisa kesadaran/niat dari saat Mentor mencoba memperingatkan Jiang Yan, entah bagaimana terjalin ke dalam proses regenerasi kehidupan kedua. **`[DESIGN GAP]` — mekanisme TEKNIS bagaimana pesan ini bisa "bocor" antar kehidupan tidak dispesifikasikan MSB; direkomendasikan tetap dibiarkan sebagai misteri metafisik yang tidak perlu dijelaskan mekanis, konsisten dengan genre xianxia yang tidak selalu memerlukan hard magic system untuk elemen supranatural semacam ini** |
| `revelation_arc` | Identitas pemberi pesan terungkap di Chapter 6.2 (jika rekomendasi Mentor diterima) |
| `payoff_arc` | Arc VI (Chapter 6.2) |
| `state_changes` | **Writes:** `flag_memory_awareness = true`, `item_ancient_symbol = acquired` (sudah tercatat di Quest Graph) |
| `unlocked_content` | Membuka seluruh Arc II (prerequisite `flag_memory_awareness`) |

---

## `memory_a02_m01` — What You Won't Come Back From

| Field | Value |
|---|---|
| `memory_id` | `memory_a02_m01` |
| `title` | What You Won't Come Back From |
| `arc` | `arc_02` |
| `trigger_type` | Contextual — dipicu menyentuh artefak pertama |
| `trigger_condition` | Selama `quest_a02_c04_008` |
| `fragment` | Protagonis (kehidupan pertama) berbicara dengan seseorang. Wajah orang tersebut adalah Lin Yue — tapi versi jauh lebih tua. Kalimat terakhir: "Kalau kau melakukan ini, kau tidak akan kembali." Memory berakhir sebelum konteks percakapan diketahui |
| `sensory_detail` | Visual jelas (wajah Lin Yue dapat dikenali meski lebih tua), auditori jelas (kalimat lengkap dan spesifik) — ini adalah memory dengan clarity tertinggi sejauh cerita hingga titik ini |
| `emotional_imprint` | Kebingungan yang tajam, bukan sekadar disorientasi — protagonis MENGENALI wajah ini (Lin Yue, temannya di kehidupan sekarang) dalam konteks yang mustahil (versi tua, di masa lalu yang jauh sebelum Lin Yue lahir di kehidupan kedua) |
| `reliability` | TINGGI secara visual/auditori, tapi RENDAH secara interpretatif — pemain TAHU apa yang dikatakan dan siapa yang mengatakannya, tapi TIDAK tahu KONTEKS ("ini" merujuk pada apa?) |
| `misleading_elements` | Sangat mungkin pemain akan mengasumsikan "ini" merujuk pada The Gate secara langsung — yang sebenarnya BENAR secara garis besar, tapi kalimat ini kemungkinan diucapkan pada momen yang berbeda dari peringatan Mentor (`memory_a01_m01`), menciptakan potensi kebingungan produktif: apakah ada DUA orang berbeda yang memperingatkan Jiang Yan? |
| `related_npc` | `npc_lin_yue` (secara tidak langsung — ini adalah versi Lin Yue KEHIDUPAN PERTAMA, entitas naratif berbeda dari `npc_lin_yue` yang hidup sekarang, meski wajah/identitas dasar sama) |
| `related_location` | Tidak dispesifikasikan |
| `related_quest` | `quest_a02_c04_008` |
| `related_item` | `item_artifact_01` |
| `related_event` | Foreshadowing "Relationship" (MSB §44 — "Lin Yue memiliki hubungan dengan kehidupan pertama") |
| `initial_interpretation` | Lin Yue (versi lampau) mengetahui/terlibat dalam rencana besar Jiang Yan dan mencoba mencegahnya — menciptakan dramatic irony langsung terhadap `npc_lin_yue` versi sekarang, yang BELUM tentu memiliki kesadaran akan hal ini (lihat rekomendasi `secret` Lin Yue di Character Bible: echo memory samar) |
| `later_contradiction` | Tidak dikontraskan secara faktual, tapi dikontekstualisasikan ulang signifikan di Arc VI: percakapan ini kemungkinan adalah salah satu dari BEBERAPA upaya orang-orang dekat Jiang Yan mencoba mencegahnya (bukan cuma "pengkhianatan" tunggal dari satu orang) — memperluas skema First Betrayal dari satu peristiwa terisolasi menjadi pola yang lebih luas |
| `true_context` | Lin Yue (kehidupan pertama) adalah salah satu dari found family Jiang Yan yang MSB §26 sebutkan secara eksplisit ("Ia membangun kelompok yang mirip dengan kelompok protagonis sekarang... Ia memiliki sahabat") — memory ini mengonfirmasi bahwa "sahabat" itu, setidaknya salah satunya, memiliki wajah yang sama dengan Lin Yue sekarang |
| `revelation_arc` | Dikontekstualisasikan penuh di Chapter 6.1 (Someone Like Me) saat paralel found family Jiang Yan diungkap |
| `payoff_arc` | Arc VI (Chapter 6.1) |
| `state_changes` | **Writes:** `flag_memory_lin_yue_elder_seen = true` (sudah tercatat di Quest Graph) |
| `unlocked_content` | Membuka Arc III (via `flag_arc2_complete`) |

**Catatan produksi penting — implikasi untuk Character Bible:** memory ini memperkuat rekomendasi `secret` Lin Yue yang sudah dicatat di Phase 5 (echo memory samar). Jika desain akhir mengonfirmasi Lin Yue-kehidupan-kedua memang memiliki kesadaran samar akan koneksi ini, memory ini adalah bukti tekstual yang mendukungnya — TAPI ini tetap direkomendasikan sebagai pilihan desain, bukan dipaksakan sebagai satu-satunya interpretasi valid.

---

## `memory_a03_m01` — The Gate I Opened

| Field | Value |
|---|---|
| `memory_id` | `memory_a03_m01` |
| `title` | The Gate I Opened |
| `arc` | `arc_03` |
| `trigger_type` | Automatic (climax cutscene Arc III) |
| `trigger_condition` | `quest_a03_c05_005`, convergence dari Chapter 3.4 |
| `fragment` | Protagonis (kehidupan pertama) berdiri di depan gerbang. Tian Xu di belakangnya, cahaya hitam di depannya. Berkata: "Kalau dunia harus membenciku, biarkan." Membuka gerbang. Cut — TIDAK menampilkan apa yang terjadi setelahnya |
| `sensory_detail` | Visual dramatis (gerbang, cahaya hitam, siluet Tian Xu), auditori (kalimat final yang diucapkan dengan tenang, bukan panik) |
| `emotional_imprint` | AMBIGU secara sengaja — kalimat "biarkan dunia membenciku" dapat dibaca sebagai villain monologue ATAU sebagai kesediaan self-sacrifice untuk kebaikan yang disalahpahami. MSB sendiri tidak menspesifikasikan tone vokal, yang berarti produksi (voice acting/text delivery) memiliki tanggung jawab besar untuk MEMPERTAHANKAN ambiguitas ini, bukan condong ke salah satu interpretasi secara prematur |
| `reliability` | TINGGI secara visual, tapi RENDAH-SANGAT-RENDAH secara interpretatif — ini adalah memory paling menyesatkan dalam katalog karena ia BENAR secara harfiah (Jiang Yan memang membuka gerbang) tapi SANGAT tidak lengkap secara motivasi |
| `misleading_elements` | Ini adalah memory yang secara sengaja dirancang untuk membuat pemain (dan protagonis) menyimpulkan "aku mungkin penyebab tragedi" (`belief_protagonist_may_be_cause = true`, sudah tercatat di Quest Graph) — kesimpulan yang SECARA TEKNIS tidak salah (Jiang Yan memang membuka gerbang, dan itu memang memicu rangkaian kegagalan) tapi kehilangan konteks krusial: TUJUAN membuka gerbang bukan destruktif, melainkan upaya memisahkan Entity dari sumber |
| `related_npc` | Tidak ada NPC lain hadir dalam fragment ini |
| `related_location` | `loc_the_gate` (dikonfirmasi lokasinya sama dengan Arc VI) |
| `related_quest` | `quest_a03_c05_005` |
| `related_item` | Tidak ada |
| `related_event` | The Gate (peristiwa utama Arc VI) |
| `initial_interpretation` | "Aku (protagonis) mungkin adalah orang yang menyebabkan tragedi Tian Xu" — SESUAI dengan yang sudah dicatat sebagai kesimpulan Arc III di Phase 2 |
| `later_contradiction` | **Dikontraskan dalam DUA tahap terpisah** (bukan sekali) — konsisten dengan prinsip bahwa revelation besar tidak boleh muncul sekaligus di Arc final: (1) Chapter 4.2, Version III catatan pendiri ("Yang kami segel bukan musuh... kami menyegel akibat dari kesalahan kami sendiri") mulai meruntuhkan asumsi villain-sederhana; (2) Chapter 5.5 (`memory_a05_m01`), memory percobaan membunuh Entity, mengoreksi secara eksplisit bahwa Jiang Yan MENCOBA MENCEGAH, bukan menyebabkan secara sengaja |
| `true_context` | Jiang Yan membuka The Gate BUKAN untuk membebaskan Entity (seperti yang mungkin diasumsikan pemain dari nada "biarkan dunia membenciku") — ia membukanya untuk mencoba MEMISAHKAN Entity dari sumber cultivation, sebuah upaya penyelamatan yang gagal, bukan tindakan destruktif yang disengaja. Kalimat "biarkan dunia membenciku" bermakna: ia tahu tindakannya akan disalahpahami, dan bersedia menanggung kesalahpahaman itu demi mencoba menyelesaikan masalah yang tidak bisa diselesaikan siapa pun sebelumnya |
| `revelation_arc` | Rekontekstualisasi bertahap: Chapter 4.2 (parsial) → Chapter 5.5 (signifikan) → Chapter 6.3 (PENUH, The Gate dijelaskan detail lengkap) |
| `payoff_arc` | Arc IV (parsial), Arc V (signifikan), Arc VI (penuh) — memory dengan payoff arc TERPANJANG dan PALING BERTAHAP dalam seluruh katalog |
| `state_changes` | **Writes:** `flag_memory_gate_a03_seen = true`, `belief_protagonist_may_be_cause = true` (sudah tercatat di Quest Graph, dan secara eksplisit dicatat sebagai belief_state bukan fact-flag) |
| `unlocked_content` | Membuka Arc IV |

**Catatan produksi kritis:** memory ini adalah CONTOH UTAMA dari prinsip memory system MSB §11 ("Memory dapat... memberikan false lead") diimplementasikan dengan benar. Penting bagi tim produksi (voice direction, cutscene framing) untuk TIDAK secara visual/auditori mengisyaratkan salah satu interpretasi (villain vs martyr) lebih kuat dari yang lain saat fragment ini pertama kali muncul — ambiguitas adalah fitur, bukan kekurangan penulisan.

---

## `memory_a05_m01` — What I Tried to Kill

| Field | Value |
|---|---|
| `memory_id` | `memory_a05_m01` |
| `title` | What I Tried to Kill |
| `arc` | `arc_05` |
| `trigger_type` | Automatic (climax cutscene Arc V) |
| `trigger_condition` | `quest_a05_c05_005`, setelah `flag_entity_first_contact` |
| `fragment` | Momen kegagalan Jiang Yan mencoba membunuh Entity — ditemukan bahwa Entity tidak dapat dibunuh tanpa menghancurkan sumber cultivation itu sendiri |
| `sensory_detail` | `[DESIGN GAP]` — MSB tidak memberi detail sensorik spesifik untuk momen ini di luar deskripsi naratif umum (MSB §22-25). Direkomendasikan: visual pertarungan/konfrontasi yang berakhir bukan dengan kemenangan atau kekalahan konvensional, melainkan dengan REALISASI (Jiang Yan berhenti, bukan dikalahkan) — penting agar tidak terasa seperti boss fight gagal, melainkan momen pemahaman yang mengubah arah tindakan |
| `emotional_imprint` | Keputusasaan yang berubah menjadi tekad darurat — dari "aku harus membunuhnya" menjadi "aku tidak bisa membunuhnya, aku harus melakukan sesuatu yang lain" |
| `reliability` | TINGGI — ini adalah memory yang secara eksplisit berfungsi MENGOREKSI memory sebelumnya (`memory_a03_m01`), bukan memory yang perlu dikoreksi lagi di kemudian hari. Ditandai eksplisit di Quest Graph sebagai reliability tinggi |
| `misleading_elements` | Tidak ada — memory ini secara sengaja dirancang sebagai titik balik reliability dalam keseluruhan sistem memory, ground truth yang mulai stabil setelah serangkaian fragment ambigu sebelumnya |
| `related_npc` | Entity (versi kehidupan pertama — pertemuan pertama Jiang Yan dengannya, mendahului "Kau membunuhku sekali" yang diucapkan Entity di present-day Chapter 5.4) |
| `related_location` | Kemungkinan sama dengan `loc_the_gate` atau `loc_tianxu_deepest_chamber` — `[DESIGN GAP]` konfirmasi spesifik |
| `related_quest` | `quest_a05_c05_005` |
| `related_item` | Tidak ada |
| `related_event` | Prekursor langsung untuk Cycle Formation |
| `initial_interpretation` | N/A — memory ini SENDIRI berfungsi sebagai koreksi/revelation, bukan sesuatu yang memerlukan interpretasi awal yang keliru |
| `later_contradiction` | Tidak ada — ini adalah salah satu dari dua memory "ground truth" dalam katalog (bersama `memory_a06_m01`) |
| `true_context` | Sama dengan fragment — memory ini SUDAH merupakan true_context, bukan sesuatu yang memerlukan rekontekstualisasi lebih lanjut. Detail TAMBAHAN (bukan koreksi) datang di Arc VI melalui `memory_a06_m01` |
| `revelation_arc` | Berdiri sendiri sebagai revelation Arc V, dengan detail lebih lanjut (bukan koreksi) di Arc VI |
| `payoff_arc` | Arc V (langsung), Arc VI (elaborasi) |
| `state_changes` | **Writes:** `flag_memory_kill_attempt_seen = true`, `flag_cycle_formation_known_partial = true`, `belief_protagonist_may_be_cause = false` (koreksi tercatat, sudah ada di Quest Graph) |
| `unlocked_content` | Membuka Arc VI |

---

## `memory_a06_m01` — The Gate, The Formation, The Cost

| Field | Value |
|---|---|
| `memory_id` | `memory_a06_m01` |
| `title` | The Gate, The Formation, The Cost |
| `arc` | `arc_06` |
| `trigger_type` | Automatic (revelation sequence utama Arc VI) |
| `trigger_condition` | `quest_a06_c03_003`, setelah `flag_betrayal_identity_known` |
| `fragment` | Sequence memory PALING LENGKAP dalam seluruh campaign: Jiang Yan membuka The Gate menuju sumber asli cultivation (bukan untuk membebaskan Entity), mencoba memisahkan Entity dari sumber, eksperimen gagal, sumber menjadi tidak stabil, Tian Xu hampir runtuh, Jiang Yan menggunakan Cycle Formation sebagai tindakan darurat terakhir |
| `sensory_detail` | Multi-sequence: visual The Gate terbuka, sensasi instabilitas (kemungkinan direpresentasikan sebagai distorsi visual/audio), lalu momen tenang saat Cycle Formation diaktifkan (kontras deliberate dengan kekacauan sebelumnya) |
| `emotional_imprint` | Dari tekad (membuka gerbang) → kengerian (eksperimen gagal) → keputusasaan terkendali (Tian Xu hampir runtuh) → ketenangan darurat (mengaktifkan Cycle Formation sebagai solusi terakhir, bukan rencana besar yang direncanakan matang) |
| `reliability` | TINGGI — ini adalah ground truth kedua dan TERLENGKAP dalam katalog, dirancang sebagai payoff untuk hampir seluruh foreshadowing sebelumnya |
| `misleading_elements` | Tidak ada — by design ini adalah titik di mana ambiguitas berhenti, MSB §29 eksplisit menyatakan detail ini sebagai fakta naratif final |
| `related_npc` | Jiang Yan (sebagai pelaku), kemungkinan echo/kehadiran si "pengkhianat" (Mentor, jika direkomendasikan) di titik sebelum The Gate — konsisten dengan `memory_a01_m01` |
| `related_location` | `loc_the_gate` |
| `related_quest` | `quest_a06_c03_003` |
| `related_item` | Tidak ada |
| `related_event` | Cycle Formation (peristiwa yang MELAHIRKAN seluruh premise Second Life) |
| `initial_interpretation` | N/A — ini adalah revelation final, bukan sesuatu yang memerlukan interpretasi awal |
| `later_contradiction` | Tidak ada — ini adalah titik stabilitas naratif tertinggi dalam seluruh Memory Bible |
| `true_context` | Sama dengan fragment — ini ADALAH true_context untuk hampir seluruh mystery besar campaign (Mystery #9, #11, #12 sekaligus, sesuai catatan di Quest Graph) |
| `revelation_arc` | Berdiri sendiri sebagai klimaks revelation Arc VI |
| `payoff_arc` | Arc VI (Chapter 6.3), dengan gema tematis berlanjut ke Arc VII |
| `state_changes` | **Writes:** `flag_the_gate_full_truth_known = true`, `flag_second_life_meaning_known = true` (sudah tercatat di Quest Graph) |
| `unlocked_content` | Membuka Chapter 6.4 (Mentor revelation + Final Choice) |

---

## Memory Reliability Progression (Verifikasi Struktural)

Tabel berikut memverifikasi bahwa reliability memory secara keseluruhan mengikuti kurva yang naratif masuk akal — dari sangat tidak reliable di awal menuju stabil di akhir, BUKAN acak:

| Memory | Arc | Reliability | Fungsi dalam Kurva |
|---|---|---|---|
| `memory_a01_m01` | I | RENDAH | Fragment paling mentah — pembuka |
| `memory_a01_m02` | I | RENDAH-SEDANG | Body memory, minim konteks by design |
| `memory_a01_m03` | I | SEDANG | Visual jelas, temporal ambigu |
| `memory_a01_m04` | I | SEDANG-TINGGI | Pesan jelas, identitas pemberi tidak diketahui |
| `memory_a02_m01` | II | TINGGI (visual/audio) / RENDAH (interpretatif) | Titik paling membingungkan — clarity tinggi tapi makna sangat tidak jelas |
| `memory_a03_m01` | III | TINGGI (visual) / SANGAT RENDAH (interpretatif) | **Puncak misleading** — dirancang aktif menyesatkan |
| `memory_a05_m01` | V | TINGGI | **Titik balik** — mulai mengoreksi, ground truth pertama |
| `memory_a06_m01` | VI | TINGGI | Ground truth final, resolusi penuh |

**Hasil verifikasi:** kurva ini valid secara struktural — reliability interpretatif MEMBURUK dari Arc I ke Arc III (puncak kebingungan di `memory_a03_m01`), lalu membaik tajam mulai Arc V. Ini bukan kurva linear sederhana, melainkan mengikuti prinsip "false lead sebelum revelation" yang diminta MSB §11 secara struktural, bukan cuma di level fragment individual.

---

## Cross-Reference: Belief State Tracking

Sesuai catatan di Quest Graph, `belief_protagonist_may_be_cause` adalah SATU-SATUNYA state yang eksplisit ditandai sebagai *mutable belief*, bukan permanent flag. Fase ini mengonfirmasi bahwa desain tersebut konsisten dengan Memory Bible:

| Titik Waktu | Nilai | Ditulis oleh | Alasan |
|---|---|---|---|
| Setelah `memory_a03_m01` | `true` | `quest_a03_c05_005` | Kesimpulan wajar dari fragment yang aktif menyesatkan |
| Setelah `memory_a05_m01` | `false` | `quest_a05_c05_005` | Koreksi eksplisit — bukan penghapusan tanggung jawab, tapi rekontekstualisasi |

**Catatan desain penting:** koreksi dari `true` ke `false` TIDAK berarti "protagonis sepenuhnya tidak bersalah" — nuansa ini harus dipertahankan dalam dialogue production (Phase 8): Jiang Yan tetap adalah orang yang tindakannya memicu rangkaian kegagalan, tapi motivasinya adalah mencegah, bukan menyebabkan. Sebuah state boolean sederhana (`true`/`false`) berisiko kehilangan nuansa ini jika dialogue tidak dirancang hati-hati — direkomendasikan agar dialogue system (Phase 8) TIDAK memperlakukan `belief_protagonist_may_be_cause = false` sebagai "masalah selesai, protagonis bersih," melainkan sebagai pembukaan pertanyaan yang lebih kompleks (relevan untuk tema Forgiveness Arc VI).

---

## Design Gap & Recommendation Ringkasan Fase Ini

1. **Identitas pemberi pesan di `memory_a01_m01` dan `memory_a01_m04`** — direkomendasikan konsisten sebagai Mentor (mengikuti rekomendasi Phase 3-4), tapi tetap gap terbuka
2. **Mekanisme teknis "kebocoran" pesan lintas-kehidupan (`memory_a01_m04`)** — direkomendasikan TIDAK dijelaskan mekanis, dibiarkan sebagai misteri metafisik genre-appropriate
3. **Detail sensorik `memory_a05_m01`** — MSB tidak spesifik, rekomendasi arah diberikan (realisasi, bukan boss-fight-gagal) tapi bukan storyboard final
4. **Lokasi spesifik beberapa memory** — beberapa `[DESIGN GAP]` lokasi tersisa, konsisten akan diformalkan Phase 9

**Catatan penting untuk fase produksi lanjutan:** Memory Bible ini SENGAJA tidak menciptakan memory_id baru di luar delapan yang sudah tertanam di Quest Graph. Jika tim produksi merasa perlu menambah memory tambahan (misalnya untuk pacing atau texture tambahan), itu harus kembali melalui Phase 4 (Quest Graph) terlebih dahulu untuk menetapkan trigger dan quest_id yang sesuai — Memory Bible tidak boleh menjadi sumber trigger baru yang tidak tercermin di Quest Graph, untuk menjaga single source of truth.

---

**File berikutnya:** `07-dialogue-architecture.md` — Dialogue Production Specification, akan secara khusus memformalkan bagaimana `belief_protagonist_may_be_cause`, `state_identity_stance`, dan variabel-variabel state lain yang sudah terkumpul memodifikasi dialog di berbagai titik (terutama Chapter 7.2, yang sudah dicatat di Quest Graph sebagai dialog paling kompleks secara kondisional dalam seluruh dokumen).
