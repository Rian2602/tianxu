# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 04. Character Production Bible

**Status:** DRAFT — Phase 5 of 18
**Depends on:** `00-narrative-architecture.md`, `01-arc-overview.md`, `02-chapter-breakdown.md`, `03-quest-graph-arc1-2.md`, `03b-quest-graph-arc3-7.md`
**Cakupan:** sembilan character arc wajib (§0.8 Narrative Architecture). Setiap arc mencantumkan `autonomous_trigger_condition` sesuai agency requirement — kondisi di mana karakter mengambil keputusan tanpa menunggu aksi protagonis.

---

## LIN YUE

| Field | Value |
|---|---|
| `character_arc_id` | `chararc_lin_yue` |
| `character` | `npc_lin_yue` |
| `starting_relationship` | Neutral (0), first_appearance Chapter 1.2 |
| `central_conflict` | Melindungi orang-orang yang ia sayangi vs menerima bahwa protagonis tidak harus mengulang jalan Jiang Yan untuk menjadi berarti |
| `belief` | Kehidupan baru adalah kesempatan sesungguhnya, bukan sekadar pengulangan — MSB §5 eksplisit: "kehidupan baru tidak harus menjadi salinan kehidupan lama" |
| `fear` | Kehilangan protagonis untuk kedua kalinya — baik secara harfiah (kematian/pengorbanan) maupun secara metaforis (protagonis "menjadi" Jiang Yan dan berhenti menjadi dirinya sendiri) |
| `desire` | Melihat murid-murid Tian Xu (bukan cuma protagonis) selamat dari apa pun yang akan terjadi — desire ini yang mendorong posisinya di Found Family Crisis Arc V |
| `secret` | **[DESIGN GAP]** — MSB tidak menyatakan secret eksplisit untuk Lin Yue di kehidupan kedua. Direkomendasikan: Lin Yue-di-kehidupan-kedua mengalami echo memory serupa protagonis, tapi jauh lebih samar, dan ia sengaja tidak memberi tahu siapa pun karena takut dianggap gila atau — lebih buruk — takut jika benar, itu berarti sejarah benar-benar berulang persis seperti sebelumnya. Ini konsisten dengan memory Arc II (Lin Yue versi tua muncul dalam memory protagonis) tanpa mengklaim sebagai fakta MSB |
| `character_question` | Apakah mencintai seseorang berarti melindungi mereka dari kebenaran, atau mempercayai mereka untuk menghadapinya? |
| `progression` | Arc I: teman dekat netral → Arc II-III: pendukung emosional utama saat identitas terungkap (relationship tinggi jika `state_identity_stance = seek_truth` atau `accept_cautious`, sedikit protektif berlebih jika `deny`) → Arc IV: mulai khawatir skala masalah yang ditemukan kelompok → Arc V: puncak konflik nilai di Found Family Crisis, posisi "lindungi murid-murid Tian Xu" dapat bertabrakan dengan arah investigasi protagonis → Arc VI: rekonsiliasi bersyarat tergantung `state_lin_yue_status` → Arc VII: salah satu suara paling berpengaruh di The Last Night |
| `quest_list` | `quest_a01_c02_003` (intro), `quest_a01_c04_005/006` (found family bonding), `quest_a03_c04_004` (reaksi terhadap identity reveal), `quest_a05_c03_003`/`branch_a05_c03_b01` (Found Family Crisis, payoff arc), `quest_a07_c01_001` (final position) |
| `turning_point` | Chapter 5.3 (Cracks in the Family) — momen di mana "melindungi murid-murid Tian Xu" harus dijelaskan secara eksplisit sebagai posisi yang mungkin bertentangan dengan arah protagonis, bukan sekadar dukungan pasif |
| `relationship_branches` | Tinggi + `state_identity_stance=seek_truth` → Loyal Companion; Rendah atau `state_identity_stance=deny` berkepanjangan → Disillusioned; Tinggi tapi dengan divergensi ideologis kuat di Arc V → Separated (berpisah baik-baik, bukan hostile) |
| `failure_state` | Disillusioned — Lin Yue tidak menjadi musuh, tapi kehilangan kepercayaan bahwa protagonis akan memilih jalan berbeda dari Jiang Yan |
| `redemption_state` | Reconciled di Arc VI/VII jika protagonis secara eksplisit menunjukkan (lewat pilihan dialog dan aksi, bukan cuma pernyataan) bahwa Found Family lebih penting dari sekadar menyelesaikan mystery |
| `end_state` | Bergantung `state_lin_yue_status`: Loyal Companion (found family utuh) / Separated (berpisah dengan hormat) / Disillusioned (masih hidup, tapi jarak permanen) / Final Partner (jika relationship romantis diimplementasikan — `[DESIGN GAP]` apakah romance ada di scope, MSB tidak menyebutkan romance eksplisit) / Keeper of Tian Xu (jika Lin Yue memilih tetap di institusi pasca-ending New Heaven/Unbroken Heaven) |
| `Arc payoff` | Payoff terbesar di Chapter 5.3 dan Chapter 7.1 — seluruh relationship-building sejak Chapter 1.2 |
| `final ending impact` | Character end state Lin Yue adalah salah satu epilogue slot di setiap dari 5 ending (detail penuh Phase 13) |
| `autonomous_trigger_condition` | Jika `world_event_a05_spiritual_collapse == active` DAN `state_rel_lin_yue < threshold_rendah` DAN protagonis belum mengambil tindakan protektif terhadap murid lain selama 2+ chapter, Lin Yue dapat bertindak sendiri (off-screen) untuk mengorganisir evakuasi/perlindungan murid, yang kemudian ditemukan protagonis sebagai fait accompli — bukan menunggu protagonis memerintahkannya |

---

## SHEN LUO

| Field | Value |
|---|---|
| `character_arc_id` | `chararc_shen_luo` |
| `character` | `npc_shen_luo` |
| `starting_relationship` | Neutral-rival (0, tapi dengan tensi kompetitif), first_appearance Chapter 1.2 |
| `central_conflict` | Kepercayaan pada merit dan kekuatan individu vs menyaksikan bahwa sistem yang ia percaya (Tian Xu, cultivation) dibangun di atas eksploitasi |
| `belief` | Awalnya: dunia adil terhadap yang berbakat dan bekerja keras (merit-based worldview). Setelah Arc IV: keyakinan ini retak — jika sistem itu sendiri korup, apa arti "merit" di dalamnya? |
| `fear` | Menjadi tidak relevan/lemah — baik secara harfiah (kehilangan kekuatan jika cultivation dihentikan) maupun secara eksistensial (kehilangan identitas sebagai "yang terkuat") |
| `desire` | Membuktikan diri — awalnya terhadap protagonis sebagai rival, kemudian (pasca Arc IV) terhadap sistem itu sendiri: membuktikan bahwa kekuatan dapat dipakai untuk memperbaiki, bukan hanya mempertahankan |
| `secret` | **[DESIGN GAP]** — direkomendasikan: Shen Luo diam-diam iri pada found family protagonis sejak awal, karena latar belakangnya (tersirat kompetitif dan individualis) membuatnya kesulitan membangun ikatan serupa. Ini menjelaskan mengapa MSB §5 menyatakan hubungannya "berkembang dari persaingan menjadi rasa hormat" — bukan cuma soal skill, tapi soal representasi cara hidup yang berbeda |
| `character_question` | Apakah kekuatan yang diperoleh dari sistem korup masih sah dipakai untuk kebaikan, atau harus ditolak sepenuhnya? |
| `progression` | Arc I-II: rival kompetitif standar → Arc III: mulai menghormati protagonis seiring melihat determinasinya menghadapi identitas yang mengguncang → Arc IV: retakan keyakinan besar saat origin of cultivation terungkap → Arc V: mengambil posisi paling radikal di Found Family Crisis ("percaya sistem harus dihancurkan" — MSB §23) → Arc VI: `state_final_principle` pemain sangat memengaruhi apakah Shen Luo menjadi ally atau semakin menjauh secara ideologis → Arc VII: salah satu dari possible_states MSB §37 tercapai |
| `quest_list` | `quest_a01_c02_003` (intro sebagai rival), `quest_a02_c01_001/002` (rivalitas akademik), `quest_a04_c03_003`/`quest_a04_c04_004` (retakan keyakinan, hadir sebagai witness), `branch_a05_c03_b02` (Found Family Crisis — posisi radikal), Arc VI-VII (successor path jika relevan) |
| `turning_point` | Chapter 4.4 (What Tian Xu Feeds On) — menyaksikan bahwa sistem yang membuatnya "terkuat" adalah sistem yang sama yang mengeksploitasi orang lain |
| `relationship_branches` | Tinggi + `state_final_principle=destroy/transform` → Trusted Ally atau Successor; Rendah atau `state_final_principle=preserve` berkepanjangan → Ideological Enemy; Kombinasi ekstrem tertentu → Fallen Rival (mati dalam konflik, kemungkinan di Mountain Gate Incident atau The Last Night — `[DESIGN GAP]` mekanisme kematian karakter belum diformalkan) |
| `failure_state` | Ideological Enemy — bukan musuh personal, tapi menentang pilihan protagonis secara terbuka jika `state_final_principle` bertentangan keras dengan radikalisasinya |
| `redemption_state` | Trusted Ally — jika protagonis menunjukkan bahwa perubahan dapat dicapai tanpa kehancuran total (jalur Transform), Shen Luo dapat menemukan sintesis antara kepercayaannya pada kekuatan dan barunya pada keadilan sistemik |
| `end_state` | Rival (jika relationship tetap rendah-netral) / Trusted Ally / Ideological Enemy / Successor (jika ia menggantikan Grandmaster di ending tertentu) / Fallen Rival / New Grandmaster (khususnya relevan di ending The Unbroken Heaven — MSB §37 eksplisit mencantumkan ini) |
| `Arc payoff` | Payoff besar di Chapter 4.4 dan Chapter 6.4 (final principle choice) |
| `final ending impact` | "New Grandmaster" sebagai end state paling signifikan untuk ending The Unbroken Heaven — representasi bahwa sistem berlanjut tapi dengan pemimpin baru yang sudah melihat kebenarannya |
| `autonomous_trigger_condition` | Jika `flag_tianxu_feeds_segel_known == true` DAN `state_rel_shen_luo` sedang-tinggi DAN protagonis belum mengambil sikap jelas terhadap Grandmaster pada akhir Arc IV, Shen Luo dapat mengonfrontasi Grandmaster sendiri (off-screen), menciptakan ketegangan politik baru yang protagonis temukan di awal Arc V — bukan menunggu protagonis memimpin konfrontasi |

---

## MEI RUO

| Field | Value |
|---|---|
| `character_arc_id` | `chararc_mei_ruo` |
| `character` | `npc_mei_ruo` |
| `starting_relationship` | Neutral-curious (0), first_appearance Chapter 1.2 |
| `central_conflict` | Hasrat mengetahui kebenaran vs tanggung jawab terhadap konsekuensi dari kebenaran yang ditemukan (terutama jika kebenaran itu bisa mengguncang seluruh Tian Xu) |
| `belief` | Kebenaran, betapa pun sulit, selalu lebih baik daripada kebohongan yang nyaman — ini adalah worldview paling konsisten di antara found family |
| `fear` | Menjadi seperti pendiri Tian Xu — menyembunyikan kebenaran "demi kebaikan" dan akhirnya menjadi bagian dari kebohongan itu sendiri |
| `desire` | Menjadi penjaga sejarah yang jujur — bukan sekadar tahu kebenaran, tapi memastikan kebenaran itu tidak hilang lagi (MSB §37: "Ia memastikan bahwa kebenaran yang ditemukan protagonis tidak kembali menjadi sejarah palsu") |
| `secret` | **[DESIGN GAP]** — direkomendasikan: Mei Ruo sudah mencurigai sebagian kebenaran institusional jauh sebelum bertemu protagonis (minatnya pada "sejarah, artefak, dan catatan lama" MSB §5 bukan kebetulan), tapi tidak pernah punya keberanian atau bukti cukup untuk menyelidiki sendirian. Protagonis memberinya alasan dan kesempatan, bukan memperkenalkannya pada ide ini |
| `character_question` | Apakah menyimpan kebenaran yang berbahaya adalah bentuk pengkhianatan terhadap sejarah, atau bentuk tanggung jawab? |
| `progression` | Arc I-II: rasa ingin tahu standar → Arc III: menjadi partner investigatif utama protagonis (pintu masuk mystery, MSB §5) → Arc IV: puncak peran sebagai analis Forbidden Archive → Arc V: salah satu suara "cari kebenaran penuh" di Found Family Crisis, cenderung paling stabil secara ideologis dibanding tiga lainnya → Arc VI-VII: menjadi figur otoritatif tentang bagaimana kebenaran ini akan diceritakan ke generasi berikutnya |
| `quest_list` | `quest_a01_c02_003` (intro), `quest_a03_c01_001` (mural analysis — peran menonjol dimulai), `quest_a04_c01_001/002` (Forbidden Archive, peran puncak), `branch_a05_c03_b03` (Found Family Crisis), `branch_a03_c04_b03` (Seek Truth — relationship terkuat jika pemain memilih stance ini) |
| `turning_point` | Chapter 4.2 (What We Sealed) — menemukan Version III bersama protagonis adalah momen di mana perannya sebagai "penjaga sejarah yang jujur" mengkristal menjadi tujuan hidup, bukan sekadar minat |
| `relationship_branches` | Tinggi + `state_identity_stance=seek_truth` → Historian/Truth Seeker (hubungan paling kuat di antara found family); Rendah → tetap Archivist tapi dengan jarak emosional; Kombinasi khusus → Forbidden Scholar (mengejar kebenaran hingga titik yang membahayakan dirinya sendiri, jika pemain terus mendorong investigasi tanpa mempertimbangkan kesejahteraan Mei Ruo — `[DESIGN GAP]` mekanisme detail) |
| `failure_state` | Forbidden Scholar dalam pengertian negatif — terobsesi hingga terisolasi dari found family lainnya |
| `redemption_state` | Keeper of the New History — jika protagonis menyeimbangkan dorongan investigasi Mei Ruo dengan perhatian terhadap kesejahteraannya, ia menjadi figur yang memastikan kebenaran diceritakan dengan bijak, bukan sekadar diumbar |
| `end_state` | Historian / Archivist / Truth Seeker / Forbidden Scholar / Keeper of the New History (MSB §37, lima possible states) |
| `Arc payoff` | Payoff besar di Chapter 4.2, dan di epilogue New Heaven/Second Life di mana perannya sebagai penjaga sejarah paling relevan |
| `final ending impact` | Keeper of the New History adalah end state paling tematis untuk ending New Heaven dan Second Life — keduanya tentang generasi baru yang harus belajar ulang, dan Mei Ruo adalah orang yang memastikan mereka belajar dengan jujur |
| `autonomous_trigger_condition` | Jika `flag_version_iii_read == true` DAN `state_truth_spread_level == 0` (protagonis belum pernah menyebarkan kebenaran) DAN Arc V dimulai, Mei Ruo dapat mulai menulis/mendokumentasikan kebenaran secara diam-diam terlepas dari keputusan protagonis — sebuah dokumen yang ditemukan pemain kemudian, menunjukkan bahwa agency-nya tidak bergantung pada validasi protagonis |

---

## GU HAN

| Field | Value |
|---|---|
| `character_arc_id` | `chararc_gu_han` |
| `character` | `npc_gu_han` |
| `starting_relationship` | Neutral-guarded (0), first_appearance Chapter 1.2 |
| `central_conflict` | Skeptisisme terhadap institusi (berbasis pengalaman, bukan ideologi abstrak) vs risiko menjadi sinis sepenuhnya dan kehilangan kapasitas untuk percaya pada siapa pun, termasuk found family |
| `belief` | Institusi besar melindungi diri sendiri sebelum melindungi orang-orang di dalamnya — keyakinan ini terbukti benar berulang kali sepanjang cerita, yang justru menjadi tantangan naratif tersendiri (bagaimana membuat karakter yang skeptisismenya "benar" tetap punya arc, bukan cuma jadi oracle yang selalu tepat) |
| `fear` | Menjadi naif lagi — pernah percaya pada sesuatu/seseorang dan dikecewakan (latar belakang "keras" MSB §5 mengisyaratkan ini tanpa detail eksplisit) |
| `desire` | Perlindungan nyata, bukan janji — Gu Han menilai orang dan institusi berdasarkan tindakan, bukan pernyataan |
| `secret` | **[DESIGN GAP]** — direkomendasikan: latar belakang "keras" Gu Han melibatkan pengalaman langsung dengan konsekuensi sosial dari sistem cultivation yang timpang (mis. keluarga/komunitas asalnya dirugikan oleh struktur kekuasaan berbasis cultivation) — ini menjelaskan mengapa ia "paling cepat mencurigai bahwa ada sesuatu yang salah dengan Tian Xu" (MSB §5) tanpa perlu bukti investigatif seperti Mei Ruo; kecurigaannya bersifat experiential, bukan analitis |
| `character_question` | Apakah mungkin melindungi orang lain tanpa akhirnya harus mempercayai sistem yang lebih besar dari diri sendiri? |
| `progression` | Arc I-II: skeptis tapi kooperatif → Arc III-IV: kecurigaannya terbukti benar berkali-kali, memperkuat worldview-nya (berisiko menjadi self-fulfilling cynicism jika tidak diimbangi) → Arc V: mengambil posisi paling ekstrem di antara found family ("Tian Xu tidak dapat diperbaiki" MSB §23) → Arc VI-VII: arc-nya adalah tentang menemukan bahwa "tidak dapat diperbaiki" tidak sama dengan "tidak layak diperjuangkan" |
| `quest_list` | `quest_a01_c02_003` (intro), `quest_a02_c02_005` (Missing Disciple — paling cepat curiga terhadap narasi resmi), `branch_a02_c03_b02/b03` (relationship terkuat jika pemain memilih Investigate/Confront, karena selaras dengan skeptisismenya), `branch_a05_c03_b04` (Found Family Crisis, posisi paling radikal) |
| `turning_point` | Chapter 5.3 — momen di mana "Tian Xu tidak dapat diperbaiki" harus diuji: apakah ini kesimpulan yang ia pertahankan demi konsistensi, atau kesimpulan yang benar-benar ia yakini setelah mempertimbangkan found family yang mungkin terpecah karenanya |
| `relationship_branches` | Tinggi + `state_final_principle=destroy` → Revolutionary/Protector; Rendah → Exile (memilih pergi sendiri, bukan diusir); Ekstrem tertentu → Martyr (MSB §37 mencantumkan ini sebagai possible state — kemungkinan terkait Mountain Gate Incident atau The Last Night, `[DESIGN GAP]` mekanisme spesifik) |
| `failure_state` | Exile — bukan pengkhianatan, tapi Gu Han memilih pergi karena tidak lagi melihat titik temu antara keyakinannya dan arah protagonis |
| `redemption_state` | Protector — jika protagonis menunjukkan (lewat aksi, bukan retorika) bahwa perlindungan nyata terhadap orang-orang rentan adalah prioritas bersama, Gu Han menemukan bahwa idealisme "memperbaiki sistem" dan pragmatismenya "melindungi orang" tidak harus bertentangan |
| `end_state` | Protector / Revolutionary / Exile / Faction Leader (kemungkinan memimpin cabang Liberation Faction) / Martyr (MSB §37) |
| `Arc payoff` | Payoff besar di Chapter 5.3, dengan callback ke Chapter 2.2 (kecurigaan pertamanya terhadap institusi terbukti berakar dalam) |
| `final ending impact` | Faction Leader paling relevan untuk ending Mortal Dawn — representasi bahwa dunia pasca-cultivation membutuhkan orang-orang seperti Gu Han yang sudah lama skeptis terhadap sistem lama |
| `autonomous_trigger_condition` | Jika `state_rep_tianxu` sangat rendah DAN `world_event_a05_spiritual_collapse == active` DAN found family belum secara eksplisit menyepakati arah bersama, Gu Han dapat mulai membangun jaringan dengan Liberation Faction secara independen — protagonis menemukan ini sebagai fakta yang sudah terjadi, bukan sesuatu yang bisa dicegah dengan satu percakapan |

---

## MENTOR

| Field | Value |
|---|---|
| `character_arc_id` | `chararc_mentor` |
| `character` | `npc_mentor` |
| `starting_relationship` | Neutral-authoritative (0), first_appearance **[DESIGN GAP]** — direkomendasikan Arc I (sebagai figur otoritas awal yang membimbing pavilion terpilih atau sebagai guru umum), agar relationship punya cukup waktu berkembang sebelum payoff besar Arc VI |
| `central_conflict` | Kesetiaan pada memori Jiang Yan (yang ia kenal dan, dalam rekomendasi desain fase ini, kemungkinan pernah "mengkhianatinya" demi mencegah bencana) vs kebingungan/ketakutan menyaksikan pola yang sama muncul kembali pada protagonis |
| `belief` | Beberapa kesalahan tidak boleh diulang, bahkan jika itu berarti harus menyakiti orang yang disayangi untuk mencegahnya |
| `fear` | Gagal untuk kedua kalinya — jika Mentor memang adalah "pengkhianat" yang gagal menghentikan Jiang Yan (rekomendasi desain Phase 3-4), ketakutan terbesarnya adalah sejarah berulang persis karena ia tidak cukup tegas atau tidak cukup jujur kali ini |
| `desire` | Melihat protagonis berhasil di tempat Jiang Yan gagal — TANPA harus mengulang kesalahan yang sama, termasuk kesalahannya sendiri (tidak jujur sejak awal) |
| `secret` | **[Terhubung dengan rekomendasi Chapter 6.2]** Mentor pernah mengenal Jiang Yan dan (rekomendasi desain, bukan fakta MSB eksplisit) adalah sosok yang "mengkhianatinya" — mencoba mencegah The Gate karena takut terhadap rencananya. Ia tidak mengetahui protagonis sekarang adalah Jiang Yan hingga Chapter 6.4 |
| `character_question` | Dapatkah seseorang menebus kegagalan masa lalu dengan cara yang berbeda dari sekadar "mencoba lebih keras" kali ini? |
| `progression` | Arc I-III: figur otoritas standar, memberi nasihat yang (tanpa disadari pemain) kadang bertentangan dengan pengalaman kehidupan pertama Jiang Yan → Arc IV-V: mulai menunjukkan tanda-tanda kegelisahan yang tidak dijelaskan saat topik sejarah Tian Xu muncul → Arc VI Chapter 6.2: identitasnya sebagai "pengkhianat" historis terungkap (rekomendasi desain) → Chapter 6.4: revelation personal penuh ("Cara kau memegang pedang... Aku pernah melihatnya") |
| `quest_list` | Quest umum Arc I-III (guru/pembimbing), `quest_a04_c03_003` (dialog opsional yang di-plant untuk payoff nanti — lihat catatan cross-reference dengan Grandmaster), `quest_a06_c02_002` (reveal identitas pengkhianat, jika rekomendasi diterima), `quest_a06_c04_004` (revelation penuh + Final Choice) |
| `turning_point` | Chapter 6.4 — momen pengakuan personal, dirancang MSB sebagai "salah satu emotional revelation" utama campaign |
| `relationship_branches` | Tinggi sebelum Chapter 6.2 → reveal terasa sebagai pengkhianatan berlapis (kekecewaan personal, bukan cuma informasi); Rendah/berjarak sebelum Chapter 6.2 → reveal terasa lebih seperti konfirmasi kecurigaan yang sudah ada |
| `failure_state` | **[DESIGN GAP]** — MSB tidak menyiratkan failure state untuk Mentor secara eksplisit; kemungkinan besar karakter ini dirancang untuk selalu mencapai reconciliation minimal di Chapter 6.4 karena signifikansi naratifnya. Direkomendasikan: TIDAK ada failure state keras, tapi *kedalaman* reconciliation dapat bervariasi berdasarkan relationship kumulatif |
| `redemption_state` | Chapter 6.4 itu sendiri adalah redemption state — pengakuan jujur, terlepas dari bagaimana protagonis meresponsnya |
| `end_state` | **[DESIGN GAP]** — MSB tidak mencantumkan Mentor dalam katalog possible_states seperti empat found family (§37). Direkomendasikan kategori serupa: Reconciled Mentor (default jika Chapter 6.4 dilalui dengan baik) / Guilt-Bound (jika relationship sangat rendah, Mentor tetap membantu tapi dengan jarak emosional permanen) |
| `Arc payoff` | Payoff terbesar Arc VI, dengan setup sejak Arc IV (dialog opsional Grandmaster yang saling merujuk, ditambahkan di Phase 4 audit) |
| `final ending impact` | **[DESIGN GAP]** — peran epilogue Mentor belum dispesifikasikan MSB; akan direkomendasikan konkret di Phase 13 |
| `autonomous_trigger_condition` | Jika `flag_the_gate_full_truth_known == true` (protagonis sudah tahu detail The Gate dari sumber lain) SEBELUM mencapai Chapter 6.2, Mentor dapat mengambil inisiatif mengaku sendiri lebih awal — mempercepat timeline reveal daripada menunggu protagonis "menemukannya" secara investigatif, karena menyembunyikannya lebih lama setelah kebenaran lain sudah terbongkar tidak masuk akal secara karakter |

---

## GRANDMASTER

| Field | Value |
|---|---|
| `character_arc_id` | `chararc_grandmaster` |
| `character` | `npc_grandmaster` |
| `starting_relationship` | Neutral-distant (0), first meaningful appearance Chapter 4.3 (kemungkinan muncul sebagai figur jauh sejak Arc I sebagai World Building, tapi belum sebagai karakter dengan agency) |
| `central_conflict` | Rasa takut kehilangan orang lain (personal, MSB §39) vs tanggung jawab objektif atas skala kerusakan yang ditimbulkan sistem yang ia pertahankan |
| `belief` | "Dunia membutuhkan cultivation" (MSB §19) — bukan karena haus kekuasaan, tapi karena ia benar-benar meyakini konsekuensi penghentian sistem lebih buruk daripada mempertahankannya |
| `fear` | Kehilangan orang lain akibat kegagalan sistem — MSB §39 eksplisit: "ia pernah kehilangan seseorang akibat kegagalan sistem" |
| `desire` | Mencegah tragedi berulang — sama seperti protagonis dan Mentor, tapi melalui jalur berlawanan (mempertahankan alih-alih mengubah) |
| `secret` | **[DESIGN GAP]** — siapa yang hilang. MSB tidak menyebut detail. Direkomendasikan: tidak perlu nama spesifik untuk berfungsi secara naratif — cukup dikonfirmasi sebagai orang dekat (murid, keluarga, atau sesama pemimpin) yang mati dalam insiden terkait ketidakstabilan sistem cultivation, cukup untuk menjustifikasi trauma tanpa memerlukan subplot tambahan yang tidak didukung MSB |
| `character_question` | Apakah mempertahankan sesuatu yang rusak demi mencegah kerusakan lebih besar adalah kebijaksanaan atau pengecutan? |
| `progression` | Arc I-III: figur otoritas jauh, terasa antagonistik dari kejauhan → Arc IV: humanisasi penuh lewat Chapter 4.3 — pengakuan bahwa sistem tidak sempurna → Arc V-VI: posisinya diuji oleh skala Spiritual Collapse; jika `state_rel_grandmaster` tinggi, ia dapat menjadi figur yang membantu (bukan menghalangi) protagonis meski tetap berpegang pada prinsip dasarnya → Arc VII: posisi final di The Last Night bergantung pada `state_final_principle` dan `state_rel_grandmaster` kumulatif |
| `quest_list` | `quest_a04_c03_003` (intro sebagai karakter, revelation utama), dialog opsional lanjutan (payoff Arc VI, ditambahkan di audit Phase 4), `quest_a07_c01_001` (posisi final) |
| `turning_point` | Chapter 4.3 — pengakuan "Aku juga pernah menginginkannya. Lalu aku melihat apa yang terjadi setelahnya" (jika relationship cukup tinggi) |
| `relationship_branches` | Tinggi → dialog khusus tersedia, potensi menjadi ally bersyarat di Arc VII; Rendah → tetap sebagai figur ideologis yang dihormati tapi tidak pernah benar-benar bersekutu |
| `failure_state` | **[DESIGN GAP]** — direkomendasikan: jika `state_final_principle=destroy` dan relationship rendah, Grandmaster dapat menjadi hambatan aktif (bukan villain, tapi seseorang yang secara jujur percaya protagonis salah) di Chapter 7.1, menciptakan konflik institusional terakhir sebelum Final Confrontation |
| `redemption_state` | Jika `state_rel_grandmaster` tinggi DAN `state_final_principle=transform`, Grandmaster dapat menjadi salah satu pendukung kuat jalur New Heaven — sintesis antara ketakutannya (kehilangan orang lain) dan solusi yang tidak memerlukan kehancuran total |
| `end_state` | **[DESIGN GAP]** — MSB tidak mencantumkan possible_states eksplisit untuk Grandmaster seperti found family. Direkomendasikan: Reformed Leader (mendukung transisi) / Last Defender (mempertahankan posisi hingga akhir, tanpa menjadi villain) / Fallen (jika Tian Xu benar-benar runtuh di ending Mortal Dawn dan ia tidak selamat — `[DESIGN GAP]` lebih lanjut) |
| `Arc payoff` | Payoff besar di Chapter 4.3, dengan echo di Chapter 6.4 (Mentor dapat merujuk balik ke kompleksitas Grandmaster, ditambahkan di audit Phase 4) |
| `final ending impact` | Sangat relevan untuk membedakan kualitas ending Unbroken Heaven — apakah dunia "diselamatkan" dengan Grandmaster masih memimpin (status quo bermasalah) atau dengan kepemimpinan yang sudah berubah |
| `autonomous_trigger_condition` | Jika `flag_tianxu_feeds_segel_known == true` (protagonis tahu kebenaran penuh formation) DAN `state_rep_tianxu` sangat rendah, Grandmaster dapat mengambil tindakan pengamanan institusional sendiri (pembatasan akses, pengawasan lebih ketat terhadap found family) sebagai respons defensif — bukan menunggu protagonis melakukan sesuatu yang provokatif secara eksplisit |

---

## MO CHEN

| Field | Value |
|---|---|
| `character_arc_id` | `chararc_mo_chen` |
| `character` | `npc_mo_chen` |
| `starting_relationship` | N/A — Mo Chen bukan karakter dengan relationship value konvensional; ia adalah figur enigmatis yang engagement-nya diukur lewat frekuensi kemunculan dan informasi yang diberikan, bukan relationship score |
| `central_conflict` | **[DESIGN GAP besar]** — MSB memberi sangat sedikit detail tentang Mo Chen di luar first appearance (Chapter 3.2). Ia "tampak mengenal protagonis," memanggilnya "Jiang Yan," lalu menghilang. Tidak ada detail motivasi, afiliasi, atau tujuan |
| `belief` | `[DESIGN GAP]` |
| `fear` | `[DESIGN GAP]` |
| `desire` | `[DESIGN GAP]` |
| `secret` | `[DESIGN GAP]` |
| `character_question` | `[DESIGN GAP]` |
| `progression` | Chapter 3.2 (first appearance, menghilang) → **[DESIGN GAP besar: apakah Mo Chen muncul kembali?]** MSB tidak menyebutkan kemunculan lanjutan. Ini adalah gap paling signifikan di seluruh Character Bible |
| `quest_list` | `quest_a03_c02_002` sejauh ini satu-satunya quest tercatat |
| `turning_point` | `[DESIGN GAP]` |
| `relationship_branches` | N/A hingga gap di atas diisi |
| `failure_state` / `redemption_state` | `[DESIGN GAP]` |
| `end_state` | `[DESIGN GAP]` |
| `Arc payoff` | `[DESIGN GAP]` — MSB §44 mencantumkan "NPC: Mo Chen" sebagai salah satu elemen foreshadowing yang "harus mendapatkan payoff pada Arc III–VII," yang berarti MSB sendiri menyiratkan Mo Chen HARUS muncul kembali dan mendapat payoff, tapi tidak menyatakan bentuknya |
| `final ending impact` | `[DESIGN GAP]` |
| `autonomous_trigger_condition` | `[DESIGN GAP]` |

**REKOMENDASI DESAIN (bagian terpisah, bukan spesifikasi):** mengingat MSB §44 eksplisit menyatakan Mo Chen harus mendapat payoff, dan mengingat kekosongan detail yang sangat besar, saya rekomendasikan Mo Chen diisi sebagai representasi **Hidden Guardians** (salah satu dari lima faksi, MSB §41 — "menjaga rahasia lama dan percaya tidak ada solusi sempurna"). Ini memberi Mo Chen fungsi struktural yang konsisten dengan faksi yang sudah ditetapkan MSB, tanpa perlu menciptakan lore baru yang bertentangan: Mo Chen muncul kembali di titik-titik krusial (kandidat: Chapter 4.2 setelah Version III ditemukan; Chapter 5.4 saat Entity berbicara; Chapter 6.3 saat The Gate terungkap) sebagai figur yang tahu lebih banyak dari yang ia ungkapkan, konsisten dengan ideologi Hidden Guardians. **Ini murni rekomendasi untuk mengisi gap terbesar dalam Character Bible — bukan keputusan final, dan sebaiknya dikonfirmasi ulang sebelum masuk ke Phase 9 (NPC Bible) di mana detail dialogue/appearance Mo Chen akan diformalkan lebih jauh.**

---

## JIANG YAN / PAST SELF

| Field | Value |
|---|---|
| `character_arc_id` | `chararc_jiang_yan` |
| `character` | Jiang Yan (identitas kehidupan pertama protagonis — bukan NPC terpisah dalam pengertian konvensional, tapi entitas naratif yang muncul lewat memory dan, di Arc VII, sebagai imprint kesadaran) |
| `starting_relationship` | N/A — protagonis *adalah* Jiang Yan; "relationship" di sini lebih tepat diukur lewat `state_identity_stance` (Arc III) daripada relationship value konvensional |
| `central_conflict` | Mencoba menyelesaikan masalah dunia sendirian vs kebutuhan akan bantuan orang lain — MSB §46 eksplisit: "Pada kehidupan pertama, Jiang Yan mencoba menyelamatkan dunia sendirian" |
| `belief` | Bahwa beban besar harus dipikul sendiri untuk melindungi orang lain dari risiko/kesalahannya |
| `fear` | Gagal dan menyeret orang lain jatuh bersamanya — inilah yang membuatnya tidak sepenuhnya mempercayai found family-nya sendiri di kehidupan pertama |
| `desire` | Menyelamatkan dunia dari entitas dan sistem yang mengeksploitasinya, dengan caranya sendiri |
| `secret` | The Gate — bahwa ia mencoba memisahkan Entity dari sumber (bukan membebaskannya, seperti yang mungkin disangka), gagal, dan Cycle Formation adalah solusi darurat, bukan rencana besar |
| `character_question` | Dapatkah seseorang menyelesaikan sesuatu yang tidak bisa ia selesaikan sendiri, dengan memberi versi lain dirinya kesempatan yang tidak ia ambil untuknya sendiri — kepercayaan pada orang lain? |
| `progression` | Diceritakan retrospektif lewat memory system: Arc I-II (fragment tanpa konteks) → Arc III (nama, status, gerbang) → Arc V (percobaan membunuh Entity, kegagalan) → Arc VI (full history: origin, betrayal, The Gate, Cycle Formation) → Arc VII (imprint kesadaran, konfrontasi langsung, penolakan protagonis "Aku bukan kau") |
| `quest_list` | Muncul di hampir semua Memory Quest sepanjang campaign — detail penuh di Phase 7 (Memory Bible) |
| `turning_point` | Chapter 7.2 — bukan turning point untuk Jiang Yan sendiri (ia adalah imprint, tidak berkembang lagi), tapi turning point untuk BAGAIMANA protagonis memandangnya: dari ketakutan/kebingungan menjadi pemahaman tanpa peniruan |
| `relationship_branches` | N/A — Jiang Yan bukan karakter dengan branch relationship, tapi `state_identity_stance` dari Arc III memodifikasi TONE Final Confrontation (lihat catatan di Quest Graph `quest_a07_c02_002`) |
| `failure_state` / `redemption_state` | N/A dalam pengertian konvensional — Jiang Yan tidak memiliki failure/redemption state karena ia adalah bagian masa lalu yang sudah selesai; yang bervariasi adalah bagaimana protagonis (dan pemain) memahaminya |
| `end_state` | Selalu sama secara naratif inti (imprint yang dijawab dengan "Aku bukan kau"), tapi *makna* penolakan ini bervariasi tergantung `state_identity_stance` — lihat catatan payoff branch Arc III |
| `Arc payoff` | Payoff terbesar seluruh campaign, terkonsentrasi di Chapter 6.1-6.4 dan 7.2 |
| `final ending impact` | Mendasari makna tematik SEMUA 5 ending — setiap ending adalah jawaban berbeda terhadap pertanyaan yang gagal dijawab Jiang Yan |
| `autonomous_trigger_condition` | N/A — Jiang Yan tidak memiliki agency independen dalam present-tense narasi; ini adalah pengecualian yang disengaja terhadap agency requirement karena sifat karakternya sebagai memory/imprint, bukan NPC hidup |

---

## ENTITY

| Field | Value |
|---|---|
| `character_arc_id` | `chararc_entity` |
| `character` | Entity (primordial, 5th force — bukan faction konvensional, diperlakukan sebagai character arc karena punya agency dan dialog langsung) |
| `starting_relationship` | N/A hingga Chapter 5.4 (first direct communication) — sebelum itu, Entity hadir hanya sebagai implikasi (monster penjaga formation Arc I, formation raksasa Arc IV) |
| `central_conflict` | Ingin dipahami sebagai korban vs tidak dapat mengabaikan bahwa ia juga telah membalas dengan menghancurkan manusia — MSB §34 eksplisit: "Ia tidak innocent. Ia hanya bukan villain sederhana" |
| `belief` | Bahwa manusia menyerang lebih dahulu ("manusialah yang menyerang lebih dahulu" MSB §34) — keyakinan ini valid dari sudut pandangnya, tapi tidak membebaskannya dari tanggung jawab atas balasannya sendiri |
| `fear` | Terus-menerus dieksploitasi tanpa akhir — ribuan tahun manusia mengambil energinya dan menyebutnya "anugerah" |
| `desire` | Bervariasi tergantung interpretasi ending: pembebasan dari eksploitasi (jika Transform/Second Life), penghentian total (implisit jika Destroy), atau — jika Preserve — tidak ada resolusi bagi desirenya sama sekali (relevan untuk memahami mengapa "siklus belum sepenuhnya berakhir" di ending Unbroken Heaven) |
| `secret` | Bahwa ia bukan sekadar "Calamity" pasif — ia adalah entitas dengan perspektif dan sejarah sendiri yang selama ini tidak pernah didengar |
| `character_question` | Dapatkah dua pihak yang saling menyakiti menemukan resolusi yang bukan sekadar salah satu mengalahkan yang lain? |
| `progression` | Arc I (implikasi: monster penjaga formation) → Arc IV (implikasi: formation raksasa yang "diberi makan") → Arc V Chapter 5.4 (kontak langsung pertama, "Kau membunuhku sekali") → Arc VI (dipahami lebih dalam lewat memory The Gate — Jiang Yan mencoba memisahkannya dari sumber, bukan membunuhnya sederhana) → Arc VII (Entity's Truth penuh, resolusi tergantung ending) |
| `quest_list` | `quest_a05_c04_004` (first contact), `quest_a06_c03_003` (dipahami lewat memory), `quest_a07_c02_002` (Entity's Truth penuh) |
| `turning_point` | Chapter 5.4 — momen "Aku adalah alasan kalian menyebut dunia ini sebagai anugerah" mengubah Entity dari ancaman abstrak menjadi karakter dengan suara |
| `relationship_branches` | N/A dalam pengertian relationship value konvensional — tapi `state_final_principle` dan ending yang dicapai menentukan resolusi arc Entity secara mendasar |
| `failure_state` | Ending Preserve (Unbroken Heaven) — dalam pengertian arc Entity, ini adalah "failure state" bagi Entity meski bukan failure state bagi dunia manusia; entitas tetap terperangkap, siklus belum selesai |
| `redemption_state` | Ending Second Life (Hidden Resolution) — "melepaskan kebutuhan manusia untuk mengendalikan sumber tersebut... Entitas dibebaskan" (MSB §36) |
| `end_state` | Bervariasi drastis per ending — akan diformalkan detail penuh di Phase 13, tapi dicatat di sini karena ini adalah character arc, bukan cuma world state |
| `Arc payoff` | Payoff besar di Chapter 5.4 dan 7.2 |
| `final ending impact` | Entity's end state secara literal MENENTUKAN identitas tiap ending (Unbroken Heaven = entitas tetap terkurung; Mortal Dawn = entitas kehilangan bentuk; New Heaven = entitas dibebaskan dari peran penjara; Nameless Guardian = entitas diselamatkan melalui pengorbanan; Second Life = entitas dibebaskan sepenuhnya tanpa exploitasi) |
| `autonomous_trigger_condition` | Jika `world_event_a05_spiritual_collapse == active` untuk durasi lama TANPA intervensi protagonis (mis. Mountain Gate Incident gagal DAN tidak ada investigasi lanjutan), Entity dapat memulai kontak lebih awal dari Chapter 5.4 secara default — manifestasi ketidaksabarannya sendiri, bukan menunggu jadwal naratif tetap |

---

## Character Relationship Cross-Reference (Ringkasan Awal — Detail Penuh Phase 20)

Tabel berikut BUKAN Relationship Matrix lengkap (itu Phase 20) — ini adalah verifikasi cepat bahwa kesembilan character arc di atas saling konsisten sebelum lanjut ke Faction Arcs, yang akan bergantung pada posisi tiap karakter ini.

| Karakter | Posisi Ideologis Dominan (untuk referensi Faction Bahasa) | Kandidat Faction Terdekat |
|---|---|---|
| Lin Yue | Protektif, hati-hati terhadap perubahan drastis | Reformists (perubahan bertahap) atau tetap netral/independen |
| Shen Luo | Awalnya pro-sistem (merit-based), retak menjadi pro-perubahan radikal pasca-Arc IV | Reformists → potensi Liberation jika radikalisasi berlanjut |
| Mei Ruo | Netral-investigatif, prioritas pada kebenaran di atas ideologi politik | Tidak terikat faksi secara ketat — Hidden Guardians secara filosofis (menghargai kompleksitas) tapi tidak secara afiliasi |
| Gu Han | Skeptis institusi, condong radikal | Liberation Faction |
| Mentor | Loyalis dengan keraguan tersembunyi | Tian Xu Orthodox (posisi formal), tapi dengan sejarah personal yang kompleks |
| Grandmaster | Loyalis penuh, tapi bukan karena kekuasaan | Tian Xu Orthodox (pemimpin) |
| Mo Chen | Misterius (rekomendasi: Hidden Guardians) | Hidden Guardians |
| Jiang Yan | N/A (historis) — tapi tindakannya (The Gate) paling dekat dengan filosofi Transform | N/A |
| Entity | 5th force, bukan faction konvensional | N/A |

**Catatan:** tabel ini adalah working draft untuk Phase 6 (Faction Arcs), bukan spesifikasi final — akan diverifikasi ulang saat Faction Bible ditulis.

---

## Design Gap & Recommendation Ringkasan Fase Ini

1. **Secret untuk Lin Yue, Shen Luo, Mei Ruo, Gu Han** — keempatnya diberi rekomendasi desain yang konsisten dengan detail kepribadian MSB, ditandai eksplisit sebagai gap
2. **Mo Chen — gap paling signifikan dalam Character Bible.** Direkomendasikan sebagai representasi Hidden Guardians dengan kemunculan berulang di titik-titik kunci, tapi ini adalah rekomendasi paling belum-matang di seluruh fase ini dan sebaiknya jadi prioritas diskusi sebelum Phase 9
3. **First appearance Mentor** — direkomendasikan Arc I, belum ditentukan MSB
4. **End state Mentor dan Grandmaster** — MSB tidak mencantumkan possible_states eksplisit seperti found family; rekomendasi kategori diberikan tapi belum final
5. **Mekanisme kematian karakter** (relevan untuk Fallen Rival/Martyr sebagai end state) — belum diformalkan sebagai mekanisme gameplay konkret

---

**File berikutnya:** `05-faction-arcs.md` — lima faksi (empat + Entity sebagai 5th force), dibangun di atas cross-reference posisi karakter yang baru selesai di atas.
