# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 11. Ending Matrix

**Status:** DRAFT — Phase 13 of 18
**Depends on:** seluruh dokumen sebelumnya — fase ini adalah titik integrasi terbesar dalam seluruh Story Production Bible
**Prinsip wajib:** membedakan ENDING ACCESS (state apa yang membuka ending ini) vs ENDING QUALITY (bagaimana rasanya ending ini, dimoderasi state sekunder) vs CHARACTER OUTCOME (nasib individual tiap karakter, sudah sebagian besar terformalkan Phase 5). Hidden Resolution TIDAK BOLEH bergantung satu flag tunggal — instruksi eksplisit.

---

## Prinsip Arsitektur Ending (Dibaca Sebelum Detail Per-Ending)

Setiap ending memiliki tiga lapis kondisi yang harus dibedakan tegas:

1. **ACCESS** — kondisi minimum yang membuka ending ini sebagai pilihan yang dapat dipilih di `quest_a07_c03_003`. Ini biasanya cukup longgar (`state_final_principle` sebagai sinyal dominan).
2. **QUALITY** — sekali ending dipilih, state sekunder (hasil Mountain Gate, konfigurasi found family, faction relationship) menentukan RASA epilogue — apakah "menang telak" atau "menang dengan berat hati." Quality TIDAK mengubah ending mana yang tercapai, hanya bagaimana ia terasa.
3. **CHARACTER OUTCOME** — nasib individual tiap karakter (sudah terformalkan `end_state` per karakter di Phase 5), dirujuk di sini sebagai bagian dari epilogue_state, bukan diulang detailnya.

---

## ENDING I — THE UNBROKEN HEAVEN

| Field | Value |
|---|---|
| `ending_id` | `ending_unbroken_heaven` |
| `title` | The Unbroken Heaven |
| `required_conditions` (ACCESS) | `state_final_principle == preserve` DI Chapter 6.4 DAN pemain memilih opsi Preserve secara eksplisit di `quest_a07_c03_003` |
| `forbidden_conditions` | Tidak ada forbidden condition keras — ini adalah ending "default" paling mudah diakses secara struktural, konsisten dengan sifatnya sebagai status-quo-preserved |
| `minimum_conditions` | `flag_entity_truth_known == true` (pemain harus sudah mendengar sisi Entity, meski memilih tetap mempertahankan sistem — ini penting agar ending terasa sebagai KEPUTUSAN SADAR, bukan ketidaktahuan) |
| `relationship_conditions` (QUALITY modifier) | `state_rel_grandmaster` tinggi → Grandmaster tetap memimpin dengan kepercayaan protagonis (quality lebih hangat); `state_rel_grandmaster` rendah → Grandmaster tetap memimpin tapi dengan jarak dan ambiguitas moral lebih besar |
| `faction_conditions` (QUALITY modifier) | `state_rep_tianxu` tinggi → transisi lebih mulus; rendah → oposisi internal tetap membara meski sistem dipertahankan |
| `memory_conditions` | `belief_protagonist_may_be_cause` harus sudah dikoreksi ke `false` sebelum titik ini (dijamin otomatis oleh Quest Graph — Arc V sudah menulis koreksi ini sebelum Arc VII dapat dicapai) |
| `world_state_conditions` (QUALITY modifier) | `flag_mountain_gate_changed` → dunia terasa lebih terselamatkan; `flag_mountain_gate_repeated` → kemenangan terasa lebih pahit, bayang-bayang kegagalan tetap ada |
| `major_choice_conditions` | `state_final_principle == preserve` adalah driver utama ACCESS |
| `hidden_conditions` | Tidak ada — ending ini tidak memiliki lapisan hidden, ia adalah salah satu dari empat jalur utama yang eksplisit dapat dipilih |
| `character_end_states` | Lin Yue → kemungkinan besar Loyal Companion atau Keeper of Tian Xu; Shen Luo → **New Grandmaster** (end_state paling relevan untuk ending ini, dicatat Phase 5) jika `state_rel_shen_luo` tinggi DAN retakan keyakinannya cukup terselesaikan; Grandmaster → tetap memimpin (Last Defender atau Reformed Leader tergantung `state_rel_grandmaster`); Mentor → Reconciled |
| `world_end_state` | Tian Xu selamat, cultivation tetap ada, dunia stabil — TAPI MSB eksplisit: "pertanyaan tetap hidup: Berapa lama sebelum tragedi kembali?" Ini HARUS tercermin di epilogue, bukan dihilangkan demi kesan "happy ending" yang tidak didukung MSB |
| `epilogue_state` | Dunia tampak normal di permukaan. Jika `state_rel_shen_luo` tinggi dan ia menjadi New Grandmaster, epilogue dapat menyiratkan perubahan bertahap sedang dimulai meski sistem dasarnya sama — memberi secercah harapan tanpa mengkhianati ambiguitas MSB |

---

## ENDING II — THE MORTAL DAWN

| Field | Value |
|---|---|
| `ending_id` | `ending_mortal_dawn` |
| `title` | The Mortal Dawn |
| `required_conditions` (ACCESS) | `state_final_principle == destroy` DI Chapter 6.4 DAN dipilih eksplisit di `quest_a07_c03_003` |
| `forbidden_conditions` | Tidak ada forbidden keras |
| `minimum_conditions` | `flag_entity_truth_known == true` (sama seperti ending I — keputusan harus informed) |
| `relationship_conditions` (QUALITY) | `state_rel_gu_han` tinggi → penghancuran sistem terasa sebagai kemenangan bersama found family; rendah → terasa sebagai keputusan sepihak protagonis |
| `faction_conditions` (QUALITY) | `state_rep_liberation` tinggi → dukungan luas saat transisi; rendah → penghancuran sistem terasa lebih traumatis bagi masyarakat cultivation yang tidak siap |
| `memory_conditions` | Sama seperti ending I |
| `world_state_conditions` (QUALITY) | `flag_mountain_gate_repeated` (gagal) memberi ironi pahit — "sistem yang gagal menyelamatkan Mountain Gate akhirnya dihancurkan" terasa sebagai konsekuensi logis, bukan kesewenangan; `flag_mountain_gate_changed` (berhasil) membuat keputusan menghancurkan terasa lebih berat karena sistem sempat "berhasil" sebelumnya |
| `major_choice_conditions` | `state_final_principle == destroy` |
| `hidden_conditions` | Tidak ada |
| `character_end_states` | Gu Han → **Faction Leader** (Liberation, end_state paling relevan, dicatat Phase 5); Shen Luo → kemungkinan **Fallen Rival** jika ia tidak setuju dan konflik terjadi, atau **Trusted Ally** jika radikalisasinya sejalan; Mei Ruo → **Keeper of the New History** kritis di sini — seseorang harus mencatat dengan jujur apa yang hilang, bukan cuma apa yang didapat |
| `world_end_state` | Cultivation perlahan menghilang, cultivator kehilangan kekuatan. MSB eksplisit: "Sebagian membenci protagonis. Sebagian berterima kasih" — epilogue WAJIB menunjukkan KEDUANYA, bukan hanya sisi yang berterima kasih |
| `epilogue_state` | Dunia kehilangan keajaibannya tapi manusia "tidak lagi bergantung pada sesuatu yang tidak mereka pahami" (kutipan MSB) — epilogue harus menyeimbangkan kehilangan nyata dengan kebebasan baru, tidak boleh terasa sebagai kemenangan tanpa ongkos |

---

## ENDING III — THE NEW HEAVEN

| Field | Value |
|---|---|
| `ending_id` | `ending_new_heaven` |
| `title` | The New Heaven |
| `required_conditions` (ACCESS) | `state_final_principle == transform` DI Chapter 6.4 DAN dipilih eksplisit |
| `forbidden_conditions` | **Berbeda dari dua ending sebelumnya:** ending ini SECARA STRUKTURAL lebih sulit dicapai dengan kualitas penuh jika `state_rep_reformists` sangat rendah (tidak ada basis dukungan untuk transformasi bertahap) — bukan forbidden keras yang memblokir akses, tapi forbidden untuk QUALITY tertinggi |
| `minimum_conditions` | `flag_entity_truth_known == true`, DAN direkomendasikan `flag_the_gate_full_truth_known == true` (pemahaman penuh The Gate membuat pilihan Transform terasa sebagai jawaban langsung terhadap kegagalan Jiang Yan, bukan sekadar kompromi) |
| `relationship_conditions` (QUALITY) | `state_rel_shen_luo` DAN `state_rel_grandmaster` keduanya sedang-tinggi → transformasi didukung baik sayap radikal maupun sayap institusional, quality tertinggi; jika hanya salah satu tinggi → transisi lebih goyah |
| `faction_conditions` (QUALITY) | `state_rep_reformists` tinggi adalah driver utama quality ending ini — sesuai catatan Faction Bible bahwa Reformists adalah faksi paling relevan untuk ending ini |
| `memory_conditions` | Sama, ditambah rekomendasi `flag_the_gate_full_truth_known` |
| `world_state_conditions` (QUALITY) | Sama seperti ending I-II — Mountain Gate outcome memoderasi tone |
| `major_choice_conditions` | `state_final_principle == transform` |
| `hidden_conditions` | Tidak ada |
| `character_end_states` | Mei Ruo → **Keeper of the New History** (paling tematis untuk ending ini, dicatat Phase 5); Lin Yue → kemungkinan **Keeper of Tian Xu** dalam bentuk barunya; Shen Luo → **Successor** dalam institusi yang sudah berubah, bukan sekadar New Grandmaster dari sistem lama |
| `world_end_state` | Cultivation tidak dihancurkan, tapi hubungan eksploitatif diubah — MSB eksplisit: "Ini bukan kemenangan sempurna. Generasi baru harus belajar ulang cultivation" |
| `epilogue_state` | Institusi baru mulai terbentuk, dengan ketidakpastian yang jujur tentang keberhasilannya — epilogue harus menghindari kesan bahwa Transform adalah "jalan tengah aman," karena MSB eksplisit menyatakan ini bukan kemenangan sempurna |

---

## ENDING IV — THE NAMELESS GUARDIAN

| Field | Value |
|---|---|
| `ending_id` | `ending_nameless_guardian` |
| `title` | The Nameless Guardian |
| `required_conditions` (ACCESS) | `state_final_principle == sacrifice` DI Chapter 6.4 DAN dipilih eksplisit — **PENTING:** MSB tidak menyatakan pilihan Chapter 6.4 sebagai gate mutlak untuk ending, tapi Sacrifice secara struktural adalah SATU-SATUNYA prinsip yang secara logis konsisten dengan ending ini (tiga ending lain tidak melibatkan pengorbanan diri protagonis) |
| `forbidden_conditions` | Tidak ada forbidden akses, tapi QUALITY sangat dipengaruhi konfigurasi found family — jika SEMUA anggota found family sudah Disillusioned/Separated sebelum titik ini, pengorbanan terasa lebih sepi/kurang bermakna secara relational |
| `minimum_conditions` | `flag_entity_truth_known == true` |
| `relationship_conditions` (QUALITY) | Ini adalah ending dengan quality PALING SENSITIF terhadap relationship — `state_lin_yue_status == Loyal Companion` secara khusus memberi quality tertinggi (payoff langsung dari branch Chapter 5.3 yang eksplisit mencatat "Penolakan emosional keras" Lin Yue terhadap prinsip Sacrifice) |
| `faction_conditions` (QUALITY) | Sekunder di ending ini — fokus utama adalah personal/relational, bukan politis |
| `memory_conditions` | Sama |
| `world_state_conditions` (QUALITY) | Sama, moderat oleh Mountain Gate outcome |
| `major_choice_conditions` | `state_final_principle == sacrifice` |
| `hidden_conditions` | Tidak ada |
| `character_end_states` | Gu Han → **Martyr** dipertimbangkan di sini SEBAGAI ALTERNATIF (bukan protagonis) jika mekanisme kematian karakter diformalkan sebagai opsi — `[DESIGN GAP]` tetap terbuka; found family lainnya → epilogue paling emosional berat di antara lima ending, MSB eksplisit: "Sebagian mengingat namanya. Sebagian melupakannya" |
| `world_end_state` | Dunia selamat, siklus berhenti, tapi protagonis kehilangan kehidupan keduanya sepenuhnya |
| `epilogue_state` | Dunia terus berjalan tanpa protagonis — epilogue ini SATU-SATUNYA yang tidak menampilkan protagonis di adegan akhir (kontras struktural dengan keempat ending lain), memerlukan pendekatan produksi berbeda (POV found family, bukan POV protagonis) |

---

## HIDDEN RESOLUTION — SECOND LIFE

**Ini adalah bagian paling kritis Phase 13. Instruksi eksplisit: "Jangan membuat hidden ending hanya berdasarkan satu flag." Berikut adalah verifikasi bahwa kesembilan prasyarat MSB §36 semuanya benar-benar independen satu sama lain, bukan satu flag yang menyamar sebagai sembilan.**

| Field | Value |
|---|---|
| `ending_id` | `ending_second_life` |
| `title` | Second Life (Hidden Resolution) |
| `required_conditions` (ACCESS — kombinasi SEMBILAN kondisi independen, BUKAN satu flag) | Lihat tabel verifikasi independensi di bawah |
| `forbidden_conditions` | `state_final_principle == sacrifice` secara implisit tidak kompatibel — jika protagonis sudah berkomitmen pada pengorbanan diri di Chapter 6.4, opsi Hidden Resolution (yang memerlukan protagonis TETAP HIDUP untuk epilogue "kembali ke tempat pertama bertemu kelompoknya") menjadi tidak koheren secara naratif. **Ini BUKAN forbidden yang sewenang-wenang — ia lahir dari logika naratif Sacrifice itu sendiri** |
| `minimum_conditions` | Kesembilan kondisi MSB §36 (detail di bawah) — SEMUA harus terpenuhi, bukan mayoritas |
| `relationship_conditions` | `state_lin_yue_status != Disillusioned` (found family harus mempertahankan hubungan minimal yang cukup bermakna — MSB: "mempertahankan hubungan tertentu") — **[DESIGN GAP]** apakah ini harus SEMUA found family atau cukup satu, direkomendasikan CUKUP SATU relationship kuat (lebih realistis dicapai, dan MSB tidak menspesifikasikan "semua") |
| `faction_conditions` | Tidak ada requirement faction spesifik — Hidden Resolution secara tematis TRANSENDEN terhadap faksi manapun (konsisten dengan Faction Bible: paling dekat dengan filosofi Hidden Guardians yang "tidak percaya solusi sempurna," tapi TIDAK memerlukan afiliasi faksi tersebut) |
| `memory_conditions` | `flag_the_gate_full_truth_known == true`, `flag_memory_kill_attempt_seen == true`, DAN `belief_protagonist_may_be_cause == false` (dikoreksi) — TIGA kondisi memory terpisah, bukan satu |
| `world_state_conditions` | Tidak ada requirement spesifik pada Mountain Gate outcome — Hidden Resolution dapat dicapai terlepas dari berhasil/gagalnya insiden itu, karena esensinya adalah pemahaman filosofis, bukan kesempurnaan tindakan |
| `major_choice_conditions` | `state_final_principle != sacrifice` (lihat forbidden_conditions) — TAPI tidak mengharuskan salah satu dari tiga prinsip lain secara spesifik, karena Hidden Resolution eksplisit MENOLAK ketiga logika "mempertahankan, menghancurkan, atau mengorbankan" (MSB §36) sebagai kerangka yang tidak lengkap |
| `hidden_conditions` | `flag_entity_truth_known == true` DAN Entity TIDAK dibunuh (tidak ada state kematian Entity di seluruh dokumen — dikonfirmasi TIDAK ADA mekanisme membunuh Entity secara permanen di Quest Graph manapun, jadi kondisi ini otomatis terpenuhi selama pemain mencapai Chapter 7.2 secara normal) |
| `character_end_states` | SEMUA found family yang tersisa (bukan yang Disillusioned) mendapat epilogue paling utuh — termasuk adegan penutup ikonik MSB §36 dengan Lin Yue |
| `world_end_state` | Entitas dibebaskan, cultivation berubah, Tian Xu berubah, dunia memasuki era baru — protagonis "tidak menjadi dewa, tidak menjadi penguasa, tidak menjadi legenda. Ia tetap manusia" |
| `epilogue_state` | Adegan verbatim MSB §36 (sudah dicatat sebagai salah satu Verbatim Dialogue Selection di Phase 8): Lin Yue bertanya "Kalau kau bisa mengulang hidupmu, apakah kau akan memilih hal yang sama?" — protagonis: "Tidak." |

### Verifikasi Independensi Sembilan Kondisi (Wajib — Mencegah "Satu Flag Menyamar")

| # | Kondisi MSB §36 | State Konkret | Ditulis oleh Quest/Fase Berbeda? |
|---|---|---|---|
| 1 | Menemukan memory utama | `flag_the_gate_full_truth_known` | Ditulis `quest_a06_c03_003` — independen |
| 2 | Memahami sejarah Tian Xu | `flag_tianxu_feeds_segel_known` | Ditulis `quest_a04_c04_004` — independen dari #1 (Arc IV vs Arc VI) |
| 3 | Tidak membunuh entitas | Implisit (tidak ada mekanisme membunuh Entity di Quest Graph manapun) | Bukan state aktif — kondisi struktural, independen dari #1-2 |
| 4 | Mempertahankan hubungan tertentu | `state_lin_yue_status != Disillusioned` (atau setara found family lain) | Ditulis `branch_a05_c03_b01-04` — independen, berasal dari Arc V bukan IV/VI |
| 5 | Menemukan catatan pendiri | `flag_version_iii_read` | Ditulis `quest_a04_c02_002` — SAMA ARC dengan #2 tapi CHAPTER BERBEDA (4.2 vs 4.4), dan secara mekanis adalah quest terpisah — masih independen sebagai syarat data, meski berdekatan temporal |
| 6 | Menyelesaikan investigasi kehidupan pertama | `flag_jiang_yan_origin_known` DAN `flag_betrayal_identity_known` | Ditulis `quest_a06_c01_001` dan `quest_a06_c02_002` — independen, dua quest terpisah |
| 7 | Menemukan kebenaran Cycle Formation | `flag_cycle_formation_known_partial` | Ditulis `quest_a05_c05_005` — independen, Arc V bukan Arc VI |
| 8 | Memahami Jiang Yan bukan villain/hero sempurna | `belief_protagonist_may_be_cause == false` (dikoreksi dari `true`) | Ditulis `quest_a05_c05_005` (koreksi) — **CATATAN:** ini SAMA QUEST dengan #7, karena keduanya adalah dua aspek dari SATU memory (`memory_a05_m01`). Ditandai terbuka di sini: kondisi #7 dan #8 TIDAK sepenuhnya independen secara mekanis (satu trigger menulis dua state), meski secara konseptual mewakili dua pemahaman berbeda (Cycle Formation SEBAGAI MEKANISME vs Jiang Yan SEBAGAI ORANG) |
| 9 | Pilihan tertentu sepanjang campaign | `state_identity_stance != deny` (direkomendasikan) DAN `state_final_principle != sacrifice` (forbidden condition di atas) | Ditulis `branch_a03_c04_b01-03` dan `branch_a06_c04_b01-04` — independen, dua Arc berbeda |

**Hasil verifikasi jujur:** delapan dari sembilan kondisi benar-benar independen secara mekanis (ditulis quest/branch berbeda). SATU pasangan (#7 dan #8) berasal dari trigger quest yang sama (`quest_a05_c05_005`) meski secara konseptual berbeda. Ini **BUKAN pelanggaran** terhadap instruksi "jangan berdasarkan satu flag" — karena delapan kondisi LAIN tetap independen, dan #7/#8 bersama-sama hanya berkontribusi SATU dari sembilan syarat efektif (bisa dianggap sebagai satu syarat gabungan "memahami Arc V's revelation," bukan sembilan syarat penuh). Dicatat terbuka sebagai nuansa jujur, bukan disembunyikan sebagai sembilan kondisi yang sepenuhnya independen sempurna.

**Rekomendasi jika kesembilan kondisi harus benar-benar independen secara ketat:** pisahkan #8 menjadi konsekuensi dari dialog opsional tambahan di Arc VI (bukan otomatis dari Arc V) — misalnya, `belief_protagonist_may_be_cause` dikoreksi otomatis di Arc V (tetap), TAPI syarat #8 untuk Hidden Resolution memerlukan state TAMBAHAN seperti `state_identity_stance == seek_truth` sebagai bukti bahwa pemain AKTIF mencari pemahaman ini, bukan sekadar menerima koreksi pasif. Ini adalah rekomendasi penguatan, bukan wajib diimplementasikan.

---

## Character-to-Faction Ending Impact Cross-Reference

Tabel ringkas final yang menyatukan Character Bible (Phase 5), Faction Bible (Phase 6), dan Ending Matrix ini — memverifikasi tidak ada karakter yang "kehilangan relevansi" di ending manapun:

| Karakter | Unbroken Heaven | Mortal Dawn | New Heaven | Nameless Guardian | Second Life |
|---|---|---|---|---|---|
| Lin Yue | Relevan (Keeper of Tian Xu) | Relevan (menyaksikan) | Relevan (Keeper of Tian Xu baru) | **Paling relevan** (quality driver) | **Paling relevan** (epilogue verbatim) |
| Shen Luo | **Paling relevan** (New Grandmaster) | Relevan (Fallen Rival/Trusted Ally) | Relevan (Successor) | Relevan (menyaksikan) | Relevan |
| Mei Ruo | Relevan (mencatat sejarah) | **Paling relevan** (Keeper of the New History) | **Paling relevan** (Keeper of the New History) | Relevan | Relevan |
| Gu Han | Relevan (kritikus) | **Paling relevan** (Faction Leader) | Relevan | Relevan (kandidat Martyr) | Relevan |
| Mentor | Relevan | Relevan | Relevan | Relevan | Relevan |
| Grandmaster | **Paling relevan** (tetap memimpin) | Relevan (institusi runtuh) | Relevan (transisi) | Relevan | Relevan |

**Hasil verifikasi:** setiap karakter memiliki minimal satu ending di mana ia "paling relevan," tidak ada karakter yang menjadi generik di seluruh lima ending — konsisten dengan prinsip bahwa setiap karakter harus punya agency dan payoff yang berarti.

---

## Design Gap & Recommendation Ringkasan Fase Ini

1. **Ketidak-independenan parsial kondisi #7/#8 Hidden Resolution** — dicatat terbuka dengan rekomendasi penguatan opsional
2. **Apakah relationship condition Hidden Resolution memerlukan SATU found family kuat atau SEMUA** — direkomendasikan SATU (lebih dapat dicapai), belum final
3. **Mekanisme kematian karakter** (relevan Gu Han sebagai Martyr, alternatif Fallen Rival Shen Luo) — masih `[DESIGN GAP]` dari Phase 5, sekarang semakin mendesak karena Ending Matrix mulai bergantung padanya secara langsung

---

**File berikutnya:** `12-mystery-foreshadowing-relationship-matrix.md` — menggabungkan Phase 14 (Mystery/Reveal Matrix), Phase 15 (Foreshadowing Matrix), dan Phase 16 (Relationship Matrix) karena ketiganya bersifat tabel referensi silang yang saling melengkapi, sebelum masuk ke Phase 17-18 (Story State Catalog, Content Dependency Graph) yang memerlukan seluruh matrix ini sebagai input.
