# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 01. Arc Overview — 7 Arc

**Status:** DRAFT — Phase 2 of 18
**Depends on:** `00-narrative-architecture.md`
**Konvensi:** setiap field yang bernilai langsung dari MSB dicatat tanpa anotasi. Field yang merupakan turunan/interpretasi (bukan kutipan langsung) ditandai `(derived)`. Field yang murni gap ditandai `[DESIGN GAP]`.

---

## ARC I — A NEW LIFE

| Field | Value |
|---|---|
| `arc_id` | `arc_01` |
| `title` | A New Life |
| `theme` | Belonging |
| `narrative_role` | Membangun fondasi identitas kedua protagonis sebagai murid biasa, sambil menanam foreshadowing minimal-visible (symbol, phrase, dream) tanpa mengganggu tone "kehidupan baru" |
| `gameplay_role` | Tutorial diegetic: aptitude test, pavilion selection, first training, first trial — mengajarkan sistem inti (cultivation, relationship, quest) melalui narasi, bukan UI terpisah |
| `starting_state` | Protagonis tiba di Tian Xu tanpa reputasi, tanpa hubungan, tanpa skill. Semua state relational = 0/neutral. `flag_memory_awareness = false` |
| `ending_state` | Protagonis memiliki: pavilion terpilih, kelompok found family terbentuk (4 anggota), 1 rival relationship dimulai, `flag_memory_awareness = true` (menyadari ia "pernah menjadi seseorang"), symbol kuno di tangan (physical proof, bukan sekadar dream) |
| `core_conflict` | Internal: menyesuaikan diri dengan kehidupan baru vs kejanggalan kecil yang terus muncul. Belum ada external antagonist |
| `mystery_question` | "Siapa aku sebelumnya?" (bibit dari Mystery #1) |
| `mystery_revelation` | Tidak ada revelation besar di Arc ini — hanya konfirmasi bahwa "sesuatu" ada (symbol, memory fragmen tanpa wajah/nama) |
| `emotional_turning_point` | Malam setelah First Trial: mimpi kedua ("Kalau kau kembali, jangan percaya sejarah") + menemukan symbol di meja kamar — pergeseran dari "kejanggalan yang bisa diabaikan" ke "aku harus mencari tahu" |
| `major_choice` | Pavilion Selection — bukan cosmetic, memengaruhi curriculum/NPC/beberapa dialogue/kemungkinan ending (MSB eksplisit menyatakan ini) |
| `convergence_point` | `convergence_a01_c_end_01` — apa pun pavilion yang dipilih, Arc I tetap berakhir di titik naratif yang sama (symbol muncul, found family terbentuk), tapi *state pavilion* dibawa terus sebagai modifier permanen ke seluruh Arc berikutnya (curriculum, guru, beberapa dialogue) |
| `next_arc_setup` | `flag_memory_awareness = true` menjadi prerequisite pembuka Arc II; kelompok found family (4 NPC) menjadi cast tetap; symbol menjadi item/clue yang akan direferensikan di Arc III (Mo Chen recognition) |

**Catatan constraint:** MSB tidak menyatakan pavilion-pavilion apa saja yang tersedia secara konkret (hanya "setiap paviliun menawarkan filosofi berbeda"). Ini `[DESIGN GAP]` — akan didaftar di Phase 3/9 dengan rekomendasi terpisah, bukan diasumsikan di sini.

---

## ARC II — THE FIRST TRIAL

| Field | Value |
|---|---|
| `arc_id` | `arc_02` |
| `title` | The First Trial |
| `theme` | Trust |
| `narrative_role` | Dunia (akademi, faction, guru) mulai bereaksi terhadap kelompok sebagai entitas sosial. Mystery masih subplot — fokus utama tetap trust antar-manusia (guru, sesama murid, institusi) |
| `gameplay_role` | Team-based trial mechanics, first major branching choice dengan konsekuensi relationship/reputation yang bertahan jangka panjang |
| `starting_state` | Kelompok 4 orang solid, pavilion terpilih, `flag_memory_awareness = true` tapi belum ada arah investigasi jelas |
| `ending_state` | `flag_archive_suspicious` (atau setara, tergantung pilihan first major choice) ter-set; artefak kehidupan pertama pertama kali ditemukan; memory pertama yang melibatkan NPC bernama (Lin Yue versi tua) muncul; protagonis punya *pertanyaan spesifik* bukan sekadar rasa janggal |
| `core_conflict` | External mulai muncul: murid senior hilang, institusi menutup-nutupi. Internal: kelompok harus memilih cara merespons ketidakpercayaan terhadap otoritas |
| `mystery_question` | "Apa yang sebenarnya terjadi pada murid yang hilang? Apa itu 'siklus dimulai lagi'?" (bibit Mystery #10) |
| `mystery_revelation` | Memory: protagonis (kehidupan pertama) berbicara dengan Lin Yue versi tua, kalimat "Kalau kau melakukan ini, kau tidak akan kembali" — revelation *parsial*, tidak dijelaskan, sengaja membingungkan (reliability rendah, sesuai prinsip memory MSB §11) |
| `emotional_turning_point` | Menemukan catatan "Siklus dimulai lagi" di tempat persembunyian murid hilang — titik di mana mystery personal (Arc I) mulai bersinggungan dengan sesuatu yang lebih besar dari diri protagonis |
| `major_choice` | First Major Choice: Obey / Investigate / Confront (MSB §9) — payoff eksplisit dinyatakan MSB baru muncul di Arc IV (`flag_archive_suspicious` membuka dialogue berbeda, MSB §43) |
| `convergence_point` | `convergence_a02_c_end_01` — ketiga branch bertemu di penemuan artefak yang sama, tapi *state* (relationship guru, reputation akademi, akses informasi) berbeda secara permanen |
| `next_arc_setup` | Artefak menjadi trigger untuk memory system yang lebih sistematis di Arc III; `flag_archive_suspicious`-type state menjadi modifier untuk dialogue Arc IV |

---

## ARC III — ECHOES OF ANOTHER SELF

| Field | Value |
|---|---|
| `arc_id` | `arc_03` |
| `title` | Echoes of Another Self |
| `theme` | Identity |
| `narrative_role` | Pergeseran genre dari academy adventure ke mystery RPG (eksplisit di MSB §11). Memory menjadi sistem inti, bukan lagi peristiwa langka |
| `gameplay_role` | Memory Investigation System diperkenalkan penuh (fragment/trigger/reliability/related NPC-location-event sebagai data terstruktur) |
| `starting_state` | Protagonis punya artefak + pertanyaan spesifik dari Arc II, belum tahu nama "Jiang Yan" |
| `ending_state` | Protagonis mendapat memory *lengkap* pertama kali (gerbang, kalimat "Kalau dunia harus membenciku, biarkan"), tahu namanya sendiri di kehidupan pertama, tahu status "Deceased", curiga dirinya adalah *penyebab* tragedi (kesimpulan yang nanti akan dikoreksi/direkontekstualisasi di Arc VI) |
| `core_conflict` | Internal murni: identitas. "Apakah aku orang yang menyebabkan tragedi ini?" — tidak ada external antagonist baru; Mo Chen adalah pembawa informasi, bukan antagonist |
| `mystery_question` | "Siapa aku sebelumnya?" (Mystery #1 — jawaban parsial: nama, bukan makna) dan "Siapa Jiang Yan?" (Mystery #2 dibuka, belum dijawab) |
| `mystery_revelation` | Nama "Jiang Yan" (dari Mo Chen), dokumen dengan tanggal + status Deceased, memory gerbang lengkap tapi tanpa konteks ("Kalau dunia harus membenciku, biarkan" — ambigu, bisa dibaca sebagai villain atau sebagai self-sacrifice, sengaja dibiarkan terbuka) |
| `emotional_turning_point` | Konfirmasi status "Deceased" pada dokumen — protagonis untuk pertama kali menghadapi fakta literal kematiannya sendiri, bukan sekadar mimpi/rasa janggal |
| `major_choice` | `[DESIGN GAP]` — MSB tidak menyebutkan major choice eksplisit untuk Arc III selain menemukan mural dan bertemu Mo Chen (peristiwa, bukan pilihan). Perlu dirancang di Phase 4 dengan tetap konsisten pada tema Identity |
| `convergence_point` | `[DESIGN GAP]` — mengikuti gap di atas |
| `next_arc_setup` | Kesimpulan "protagonis mungkin penyebab tragedi" menjadi *false/incomplete interpretation* yang akan dikontraskan langsung oleh Forbidden Archive di Arc IV (§17 MSB: "Yang kami segel bukan musuh. Kami menyegel akibat dari kesalahan kami sendiri.") |

**Catatan penting:** kesimpulan Arc III ("protagonis mungkin penyebab tragedi") harus diperlakukan sebagai *interpretasi pemain yang belum lengkap*, bukan revelation final — ini konsisten dengan sistem memory MSB §11 (`misleading_elements`, `later_contradiction`). Ditandai eksplisit di sini supaya Phase 7 (Memory Architecture) tidak menuliskannya sebagai fakta selesai.

---

## ARC IV — THE FALSE HISTORY

| Field | Value |
|---|---|
| `arc_id` | `arc_04` |
| `title` | The False History |
| `theme` | Truth |
| `narrative_role` | Sejarah *institusional* (bukan personal) mulai runtuh. Pergeseran fokus dari "siapa aku" ke "apa yang sebenarnya dijaga Tian Xu" |
| `gameplay_role` | Investigation quest berat (Forbidden Archive, tiga versi sejarah), pengenalan Grandmaster sebagai figur ideologis kompleks |
| `starting_state` | Nama Jiang Yan diketahui, status Deceased diketahui, `flag_archive_suspicious`-type state dari Arc II aktif sebagai modifier |
| `ending_state` | Tiga versi sejarah ditemukan; origin of cultivation diketahui (sumber purba → entitas lahir dari penggunaannya); Tian Xu diketahui sebagai *feeding mechanism*, bukan sekadar penjaga segel; Grandmaster relationship established (bukan musuh sederhana) |
| `core_conflict` | External institusional: Grandmaster vs kebenaran yang mulai terbongkar. Ideologis, bukan fisik — Grandmaster tidak menjadi combat antagonist di Arc ini |
| `mystery_question` | "Mengapa Tian Xu menyembunyikan sejarahnya?" (Mystery #4), "Apa asal-usul cultivation?" (Mystery #6) |
| `mystery_revelation` | Version III catatan pendiri ("Yang kami segel bukan musuh. Kami menyegel akibat dari kesalahan kami sendiri."); origin cultivation penuh; ruang terdalam dengan formation raksasa yang menyerap energi seluruh akademi |
| `emotional_turning_point` | Menemukan bahwa curriculum, murid, dan guru semuanya adalah *bahan bakar* sistem — pergeseran dari "Tian Xu punya rahasia" ke "aku bagian dari sistem yang mengeksploitasi orang-orang di sekitarku" |
| `major_choice` | `[DESIGN GAP]` — MSB tidak menyebutkan choice eksplisit di Arc IV selain penemuan bertahap. Kandidat kuat (rekomendasi, bukan canon): apakah menyebarkan kebenaran Forbidden Archive ke murid lain, sesuai prinsip Section 45 MSB ("pemain harus menentukan apakah menyebarkan kebenaran") |
| `convergence_point` | `[DESIGN GAP]` — bergantung pada resolusi major_choice di atas |
| `next_arc_setup` | Pengetahuan "Tian Xu memberi makan segel" menjadi prasyarat untuk memahami Spiritual Collapse di Arc V; relationship dengan Grandmaster (ideologis, bukan hostile) dibawa terus hingga Arc VI/VII |

---

## ARC V — THE WORLD THAT REMEMBERS

| Field | Value |
|---|---|
| `arc_id` | `arc_05` |
| `title` | The World That Remembers |
| `theme` | Consequence |
| `narrative_role` | Masalah menjadi global (eksplisit MSB §21). Repeating events menghubungkan langsung kehidupan pertama dengan kehidupan kedua secara mekanis, bukan cuma naratif |
| `gameplay_role` | World Event system diperkenalkan penuh (Spiritual Collapse sebagai multi-region state); Found Family Crisis — kelompok dapat pecah berdasarkan pilihan pemain kumulatif dari Arc I-IV |
| `starting_state` | Sistem Tian Xu diketahui eksploitatif; relationship dengan 4 anggota found family sudah punya trajectory berbeda tergantung pilihan sebelumnya |
| `ending_state` | Repeating event (`Mountain Gate Incident`) terjadi/dicegah tergantung player action; kelompok found family berpotensi terpecah (tidak semua bertahan sebagai sahabat — eksplisit MSB §23); Entity berbicara langsung untuk pertama kali; memory besar: Jiang Yan **mencoba membunuh** Entity (bukan membebaskannya) dan gagal, lalu menciptakan Cycle Formation |
| `core_conflict` | External skala dunia (spiritual anomaly, monster mutation) + internal kelompok (found family retak berdasarkan ideologi masing-masing anggota) |
| `mystery_question` | "Apa itu Entity?" (Mystery #7 dibuka penuh), "Apa yang terjadi di kehidupan pertama?" (Mystery #8 — revelation besar) |
| `mystery_revelation` | Entity: "Kau membunuhku sekali" + "Aku adalah alasan kalian menyebut dunia ini sebagai anugerah." Memory: Jiang Yan mencoba membunuh Entity, gagal karena entitas tidak bisa dibunuh tanpa menghancurkan sumber cultivation, lalu menciptakan Cycle Formation sebagai solusi darurat |
| `emotional_turning_point` | Found Family Crisis mencapai puncak — momen di mana pemain menyadari bahwa hubungan yang dibangun sejak Arc I bisa hancur akibat pilihan ideologis, bukan akibat aksi antagonist eksternal |
| `major_choice` | Bagaimana merespons Repeating Event (`Mountain Gate Incident`) — MSB eksplisit: "Jika berhasil, sejarah berubah. Jika gagal, tragedi terulang." Ini choice dengan gameplay stake nyata (bukan dialog pilihan semata) |
| `convergence_point` | `convergence_a05_c_end_01` — apa pun hasil Mountain Gate Incident dan konfigurasi found family yang tersisa, Arc V tetap berakhir di revelation yang sama (Jiang Yan's failed attempt + Cycle Formation), tapi *siapa yang masih ada di kelompok* dan *bagaimana dunia bereaksi* berbeda permanen |
| `next_arc_setup` | Konfigurasi found family final (siapa loyal, siapa disillusioned, siapa terpisah) menjadi starting state Arc VI; pengetahuan tentang Cycle Formation menjadi prasyarat memahami The Truth of Jiang Yan |

---

## ARC VI — THE LAST CYCLE

| Field | Value |
|---|---|
| `arc_id` | `arc_06` |
| `title` | The Last Cycle |
| `theme` | Forgiveness |
| `narrative_role` | Semua mystery utama diselesaikan (eksplisit MSB §25 "Semua misteri utama mulai diselesaikan"). Ini adalah Arc penutup mystery, bukan Arc penutup cerita — Arc VII adalah final act terpisah |
| `gameplay_role` | Full disclosure Jiang Yan's history sebagai playable/witnessed memory sequence; Mentor emotional revelation; Final Choice Before Endgame (4 prinsip: Preserve/Destroy/Transform/Sacrifice) |
| `starting_state` | Konfigurasi found family dari Arc V; pengetahuan Cycle Formation; belum tahu detail penuh First Betrayal atau The Gate |
| `ending_state` | Full history Jiang Yan diketahui (First Life, First Betrayal, The Gate, Cycle Formation detail); makna sebenarnya Second Life diketahui ("kesempatan eksperimental," bukan hadiah/takdir); Mentor revelation ("Cara kau memegang pedang... aku pernah melihatnya"); prinsip final (Preserve/Destroy/Transform/Sacrifice) dipilih sebagai jalur menuju Arc VII |
| `core_conflict` | Internal: menerima bahwa dirinya *adalah* Jiang Yan tanpa menjadi Jiang Yan (persiapan untuk momen penolakan di Arc VII §33). Tema Forgiveness bekerja dua arah: memaafkan Jiang Yan (diri sendiri) dan dimaafkan/tidak dimaafkan oleh found family yang mengetahui kebenaran |
| `mystery_question` | Mystery #2, #3, #9, #11 dijawab penuh: siapa Jiang Yan, mengapa memory kembali, apa itu Cycle Formation, apa yang sebenarnya dilakukan Jiang Yan |
| `mystery_revelation` | The First Betrayal (pengkhianatan yang sebenarnya adalah upaya mencegah, bukan sekadar pengkhianatan sederhana — MSB §28); The Gate (Jiang Yan mencoba memisahkan Entity dari sumber, bukan membebaskannya — kontras dengan asumsi Arc III); real meaning of Second Life |
| `emotional_turning_point` | Mentor revelation — pengakuan personal, bukan exposition informational, tentang koneksi ke Jiang Yan |
| `major_choice` | Final Choice Before Endgame: Preserve / Destroy / Transform / Sacrifice (MSB §31) — eksplisit dinyatakan "tidak langsung menentukan ending. Ia menentukan jalur final" |
| `convergence_point` | `convergence_a06_c_end_01` — keempat prinsip menuju Arc VII yang sama (The Last Night), tapi dengan starting condition final act yang berbeda signifikan |
| `next_arc_setup` | Prinsip yang dipilih menjadi *jalur dominan* Arc VII tapi TIDAK mengunci ending — MSB eksplisit menyatakan ending ditentukan gabungan seluruh state permainan, bukan satu flag ini saja (relevan untuk Phase 13 Ending Matrix) |

---

## ARC VII — SECOND LIFE

| Field | Value |
|---|---|
| `arc_id` | `arc_07` |
| `title` | Second Life |
| `theme` | Choice |
| `narrative_role` | Final act. Semua hubungan yang dibangun "mulai membayar hasilnya" (MSB §32, kutip langsung prinsip). Tidak ada lagi quest yang terasa seperti side activity |
| `gameplay_role` | Convergence penuh dari seluruh state permainan (relationship, faction, memory, world state) menjadi kondisi ending; Final Confrontation dengan Jiang Yan imprint sebagai emotional/thematic climax, bukan combat climax |
| `starting_state` | Prinsip dari Arc VI (Preserve/Destroy/Transform/Sacrifice) sebagai jalur dominan; found family final configuration; seluruh relationship/faction state dari Arc I-VI |
| `ending_state` | Salah satu dari 5 ending tercapai; character end states untuk 4 anggota found family + Mentor + Grandmaster + Shen Luo ditentukan |
| `core_conflict` | Puncak dari conflict Internal (Identity — "Aku bukan kau") vs conflict External (Tian Xu di ambang kehancuran, Entity keluar, faksi bergerak) |
| `mystery_question` | Mystery #12: "Apa arti sebenarnya Second Life?" — dijawab penuh hanya jika Hidden Resolution tercapai; ending lain menjawabnya secara parsial/berbeda |
| `mystery_revelation` | Entity's Truth lengkap (§34 — "manusialah yang menyerang lebih dahulu" tapi Entity juga tidak innocent); momen penolakan protagonis terhadap Jiang Yan ("Aku bukan kau" — MSB menyebut ini "titik paling penting dari seluruh campaign") |
| `emotional_turning_point` | "Aku bukan kau" — protagonis menolak dikendalikan oleh kehidupan pertamanya. Ini bukan revelation informasi, tapi revelation karakter |
| `major_choice` | FINAL DECISION — empat ending path utama (Unbroken Heaven / Mortal Dawn / New Heaven / Nameless Guardian), dengan Hidden Resolution (Second Life) sebagai kondisi kombinasi tersembunyi (MSB §36) |
| `convergence_point` | Tidak ada convergence setelah ending — ini adalah titik akhir cerita. Namun secara struktural, seluruh convergence dari Arc I-VI bermuara di sini sebagai *satu titik keputusan besar*, bukan lima jalur independen yang tiba-tiba muncul di Arc VII |
| `next_arc_setup` | N/A — akhir campaign. Epilogue state per ending dispesifikasikan di Phase 13 (Ending Matrix) |

---

### Continuity Check (Manual Verification)

Sebelum lanjut ke Phase 3, verifikasi bahwa `ending_state` setiap Arc secara konsisten menjadi (atau superset dari) `starting_state` Arc berikutnya:

| Transisi | Verified? | Catatan |
|---|---|---|
| Arc I → II | ✅ | `flag_memory_awareness=true` dan found family (4 NPC) konsisten |
| Arc II → III | ✅ | Artefak + pertanyaan spesifik konsisten sebagai starting point Memory Investigation System |
| Arc III → IV | ✅ | Nama Jiang Yan + status Deceased + `flag_archive_suspicious`-type state konsisten |
| Arc IV → V | ✅ | Pengetahuan sistem eksploitatif Tian Xu konsisten sebagai prasyarat memahami Spiritual Collapse |
| Arc V → VI | ✅ | Konfigurasi found family final + pengetahuan Cycle Formation konsisten |
| Arc VI → VII | ✅ | Prinsip final (4 pilihan) + found family configuration + seluruh relationship/faction state konsisten sebagai starting Arc VII |

Tidak ditemukan contradiction pada level Arc Overview. Verifikasi lebih detail (state-level, bukan Arc-level) akan diulang di Phase 21 (Narrative QA Audit) setelah seluruh fase produksi selesai.

---

### Ringkasan DESIGN GAP dari Fase Ini

1. **Pavilion roster** (Arc I) — MSB menyatakan sistem ada, tidak menyatakan pavilion konkret apa saja
2. **Major Choice Arc III** — MSB tidak eksplisit menyatakan choice terstruktur, hanya peristiwa (mural, Mo Chen)
3. **Major Choice Arc IV** — MSB tidak eksplisit menyatakan choice terstruktur; kandidat kuat direkomendasikan (menyebarkan kebenaran atau tidak) berdasarkan Section 45 MSB, tapi belum canon

Ketiga gap ini akan diberi rekomendasi konkret di Phase 3 (Chapter Breakdown) dan Phase 4 (Quest Graph), tetap dengan anotasi `[DESIGN GAP]` dan rekomendasi terpisah dari spesifikasi.

---

**File berikutnya:** `02-chapter-breakdown.md` — memecah masing-masing 7 Arc menjadi Chapter dengan pacing Setup→Development→Complication→Escalation→Revelation→Consequence→Transition.
