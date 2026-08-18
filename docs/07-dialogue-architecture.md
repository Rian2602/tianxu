# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 07. Dialogue Architecture

**Status:** DRAFT — Phase 8 of 18
**Depends on:** seluruh file sebelumnya — fase ini secara khusus menepati janji "state-aware dialogue" dan "diformalkan Phase 8" yang tersebar di enam titik sepanjang Quest Graph, Character Bible, dan Faction Bible.
**Prinsip wajib:** ini adalah SPESIFIKASI PRODUKSI, bukan naskah lengkap. Setiap dialogue entry mencantumkan kondisi dan struktur, BUKAN kalimat penuh — kecuali di bagian akhir dokumen (§ Verbatim Dialogue Selection) yang secara sengaja memilih sejumlah kecil dialog untuk ditulis penuh, sesuai instruksi "pilih dialogue penting yang memang perlu ditulis verbatim."

---

## Kategori Versi Dialog Wajib

Setiap dialogue_id yang kompleks harus ditandai memiliki versi mana saja dari enam kategori berikut:

1. **Normal version** — tanpa kondisi khusus terpenuhi
2. **High relationship version** — `state_rel_X` di atas threshold
3. **Low relationship version** — `state_rel_X` di bawah threshold
4. **Memory-aware version** — merujuk pengetahuan dari memory tertentu (`flag_memory_*_seen`)
5. **Faction-aware version** — merujuk `state_rep_*` atau `state_final_principle`
6. **Previous-choice-aware version** — merujuk keputusan spesifik (`state_identity_stance`, branch Chapter 2.3, dll)

Tidak semua dialogue_id memerlukan keenamnya — dialogue sederhana (transisi, tutorial) dapat memiliki normal version saja tanpa kehilangan fungsi.

---

## `dialog_a02_d014` — Forbidden Archive Access (mengisi commitment Quest Graph)

| Field | Value |
|---|---|
| `dialogue_id` | `dialog_a02_d014` |
| `speaker` | Guru pembimbing / Mei Ruo / NPC simpatisan (bervariasi per versi) |
| `listener` | Protagonis |
| `context` | Akses pertama ke Forbidden Archive, `quest_a04_c01_001` |
| `trigger` | Memasuki `loc_forbidden_archive` untuk pertama kali |
| `prerequisites` | `flag_memory_gate_a03_seen == true` |
| `state_conditions` | Bercabang tiga berdasarkan branch Chapter 2.3 (lihat versi di bawah) |
| `relationship_conditions` | `state_rel_master` (untuk versi Obey) |
| `faction_conditions` | `state_rep_tianxu` (untuk versi Confront) |
| `memory_conditions` | Tidak ada |
| `dialogue_purpose` | Consequence, Gameplay Progression (menentukan cara akses) |
| `emotional_state` | Bervariasi — percaya diri (Obey), tegang-hati-hati (Investigate), defensif (Confront) |
| `information_revealed` | Sama secara substansi (Version I/II ada di sana) — cara MENDAPATKAN akses yang berbeda, bukan informasi yang berbeda |
| `player_choices` | Tidak ada choice baru di titik ini — ini murni state-aware framing dari choice yang sudah dibuat di Chapter 2.3 |
| `choice_consequences` | N/A |
| `followup_dialogue` | Mengarah ke `dialog_a04_d001` (Version I/II comparison, generik) |
| `alternate_versions` | Wajib punya: Previous-choice-aware version (tiga varian) |

**Versi Previous-choice-aware (tiga varian):**

- **Jika Obey (`state_rel_master` tinggi):** Guru sendiri yang membukakan akses, dengan nada percaya — "Karena kau jujur waktu itu, aku akan menunjukkan apa yang aku tahu." Guru turut hadir di ruangan, memberi konteks institusional tambahan yang tidak tersedia di dua versi lain
- **Jika Investigate (`flag_archive_suspicious == true`):** Akses mandiri, tanpa pendamping — Mei Ruo satu-satunya yang hadir, framing lebih seperti "menyelinap" meski secara teknis diizinkan. Nada lebih tegang, dipercepat
- **Jika Confront (`state_rep_tianxu` rendah):** Akses via NPC simpatisan (bukan jalur resmi), dengan risiko lebih tinggi — dialog mencantumkan kekhawatiran eksplisit dari NPC simpatisan tentang konsekuensi jika ketahuan

**Catatan produksi:** ketiga versi TIDAK mengubah informasi yang ditemukan (Version I/II/III tetap sama), hanya CARA dan TONE mendapatkannya — konsisten dengan prinsip convergence bahwa story event dapat sama sementara konteks berbeda.

---

## `dialog_a02_d020` — Hidden Cave Group Discussion (mengisi commitment Chapter 2.4)

| Field | Value |
|---|---|
| `dialogue_id` | `dialog_a02_d020` |
| `speaker` | Found family (grup) |
| `listener` | Protagonis / satu sama lain |
| `context` | `quest_a02_c04_007`, memasuki Hidden Cave |
| `trigger` | Convergence dari tiga branch Chapter 2.3 |
| `prerequisites` | `flag_hidden_cave_explored` sedang di-set |
| `state_conditions` | Bercabang berdasarkan branch mana yang diambil |
| `relationship_conditions` | Tidak ada |
| `faction_conditions` | Tidak ada |
| `memory_conditions` | Tidak ada |
| `dialogue_purpose` | Consequence, Relationship (menunjukkan bahwa found family membawa "ingatan" tentang keputusan sebelumnya, bukan reset) |
| `emotional_state` | Bervariasi per versi |
| `information_revealed` | Tidak ada informasi baru — ini murni texture/consequence dialogue |
| `player_choices` | Tidak ada |
| `choice_consequences` | N/A |
| `followup_dialogue` | Mengarah ke `dialog_a02_d021` (artifact discovery, generik) |
| `alternate_versions` | Previous-choice-aware version (tiga varian, lebih ringkas dari `dialog_a02_d014`) |

**Versi ringkas:**
- **Obey:** Anggota kelompok yang skeptis terhadap institusi (kemungkinan Gu Han) berkomentar singkat tentang bagaimana melapor "berhasil," dengan nada yang tidak sepenuhnya meyakinkan
- **Investigate:** Kelompok berbagi rasa lega campur waspada — keputusan diam-diam ini membuahkan hasil, tapi belum tentu tanpa konsekuensi
- **Confront:** Ketegangan sosial yang ditimbulkan konfrontasi terbuka masih terasa — mungkin ada anggota found family yang menyatakan kekhawatiran implisit tentang reputasi kelompok

---

## `dialog_a04_d033` — Grandmaster Optional High-Relationship Dialogue

| Field | Value |
|---|---|
| `dialogue_id` | `dialog_a04_d033` |
| `speaker` | `npc_grandmaster` |
| `listener` | Protagonis |
| `context` | Dialog opsional setelah `quest_a04_c03_003`, jika relationship cukup tinggi |
| `trigger` | Memilih opsi dialog tambahan setelah percakapan utama Chapter 4.3 |
| `prerequisites` | `flag_grandmaster_met == true` |
| `state_conditions` | Tidak ada tambahan |
| `relationship_conditions` | `state_rel_grandmaster >= threshold_tinggi` **[DESIGN GAP — nilai numerik exact]** |
| `faction_conditions` | Tidak ada |
| `memory_conditions` | Tidak ada |
| `dialogue_purpose` | Character Development, Foreshadowing (untuk payoff Chapter 6.4) |
| `emotional_state` | Reflektif, jujur, tanpa pertahanan diri — kontras dengan tone otoritatif Grandmaster di dialog utama |
| `information_revealed` | Konfirmasi bahwa Grandmaster PERNAH menginginkan hal yang sama seperti protagonis (menghancurkan/mengubah sistem), sebelum melihat konsekuensinya |
| `player_choices` | Tidak ada choice bercabang — ini adalah dialog yang didengarkan, bukan diarahkan |
| `choice_consequences` | N/A |
| `followup_dialogue` | Tidak ada langsung — payoff-nya di `dialog_a06_d041` (Mentor, Chapter 6.4) |
| `alternate_versions` | High relationship version SAJA — dialog ini secara definisi tidak ada versi low-relationship karena ia hanya muncul jika threshold terpenuhi |

**Catatan verbatim (dipilih untuk ditulis penuh — lihat § Verbatim Dialogue Selection):** baris "Aku juga pernah menginginkannya. Lalu aku melihat apa yang terjadi setelahnya" sudah dikutip MSB secara eksplisit dan menjadi jangkar emosional Chapter 4.3.

---

## `dialog_a06_d041` — Mentor's Cross-Reference to Grandmaster

| Field | Value |
|---|---|
| `dialogue_id` | `dialog_a06_d041` |
| `speaker` | `npc_mentor` |
| `listener` | Protagonis |
| `context` | Bagian dari `quest_a06_c04_004`, sebelum revelation utama |
| `trigger` | Memasuki dialog Chapter 6.4 |
| `prerequisites` | `flag_second_life_meaning_known == true` |
| `state_conditions` | Modifier tambahan jika `dialog_a04_d033` sudah didengar |
| `relationship_conditions` | Tidak gating, tapi memengaruhi kedalaman versi |
| `faction_conditions` | Tidak ada |
| `memory_conditions` | Tidak ada |
| `dialogue_purpose` | Character Development, Foreshadowing→Payoff (pola "antagonist yang dapat dipahami" lintas-karakter) |
| `emotional_state` | Tenang, sedikit melankolis |
| `information_revealed` | Mentor mengaitkan keraguannya sendiri dengan yang pernah ia lihat pada Grandmaster — jika pemain sudah mendengar `dialog_a04_d033`, baris ini terasa sebagai callback yang diakui, bukan informasi baru |
| `player_choices` | Tidak ada |
| `choice_consequences` | N/A |
| `followup_dialogue` | Mengarah langsung ke revelation utama Chapter 6.4 ("Cara kau memegang pedang...") |
| `alternate_versions` | Memory-aware version (jika `dialog_a04_d033` didengar) vs Normal version (jika tidak) |

**Versi Memory-aware:** Mentor menyebut Grandmaster secara eksplisit — "Bahkan Grandmaster pernah bercerita padaku, ia juga pernah ragu seperti ini. Mungkin lebih banyak dari kita yang meragukan sistem ini daripada yang terlihat." (draft, bukan final — lihat § Verbatim)

**Versi Normal:** Mentor tidak menyebut Grandmaster secara spesifik, hanya berbicara tentang keraguan secara umum sebelum masuk ke revelation personalnya.

---

## `dialog_a07_d001` — The Last Night (Hub Dialogue, mengisi commitment "paling kompleks")

**Catatan struktural khusus:** ini bukan satu dialogue_id tunggal, melainkan SET dialogue yang dikelompokkan di bawah satu payung produksi, karena kompleksitasnya. Setiap anggota cast punya entry terpisah, tapi berbagi kerangka kondisi yang sama.

| Field | Value |
|---|---|
| `dialogue_id` | `dialog_a07_d001` (payung) — sub-entries: `dialog_a07_d001_linyue`, `dialog_a07_d001_shenluo`, `dialog_a07_d001_meiruo`, `dialog_a07_d001_guhan`, `dialog_a07_d001_mentor`, `dialog_a07_d001_grandmaster` |
| `speaker` | Bervariasi per sub-entry |
| `listener` | Protagonis |
| `context` | `quest_a07_c01_001`, hub sebelum Final Confrontation |
| `trigger` | Mendekati tiap NPC di lokasi The Last Night |
| `prerequisites` | `state_final_principle != null` |
| `state_conditions` | **SELURUH akumulasi state campaign** — ini adalah dialogue paling kondisional dalam dokumen |
| `relationship_conditions` | `state_rel_*` masing-masing karakter |
| `faction_conditions` | `state_final_principle`, `state_rep_*` |
| `memory_conditions` | Tidak langsung, tapi tone dipengaruhi apakah `belief_protagonist_may_be_cause` sempat true lalu dikoreksi |
| `dialogue_purpose` | Consequence (payoff terbesar dalam dokumen — eksplisit dicatat di Quest Graph) |
| `emotional_state` | Urgen tapi tidak panik — MSB: "Tidak ada lagi quest yang terasa seperti side activity" |
| `information_revealed` | Tidak ada informasi baru — murni emosional/relational |
| `player_choices` | Tidak ada branch baru — dialog ini adalah OBSERVASI, bukan decision point |
| `choice_consequences` | N/A |
| `followup_dialogue` | Mengarah ke `quest_a07_c02_002` |
| `alternate_versions` | Setiap sub-entry memerlukan MINIMAL matrix 2x2: `state_lin_yue_status` (atau setara) × `state_final_principle` |

**Struktur matrix per sub-entry (contoh Lin Yue, pola sama untuk Shen Luo/Mei Ruo/Gu Han):**

| `state_lin_yue_status` \ `state_final_principle` | Preserve | Destroy | Transform | Sacrifice |
|---|---|---|---|---|
| Loyal Companion | Dukungan penuh, tenang | Dukungan dengan kekhawatiran eksplisit | Dukungan antusias | Penolakan emosional keras — mencoba mencegah |
| Separated | Hadir tapi berjarak, harapan hati-hati | Tidak hadir (sudah berpisah sebelumnya) atau hadir dengan tensi | Keterbukaan hati-hati untuk rekonsiliasi | Kesedihan, penyesalan tidak sempat rekonsiliasi |
| Disillusioned | Skeptis terbuka, mempertanyakan motif protagonis | Ironi pahit ("akhirnya kau setuju denganku") | Skeptis tapi sedikit lega | Shock, kemungkinan momen rekonsiliasi mendadak karena taruhannya nyawa |

**Catatan produksi kritis:** matrix ini BUKAN kombinasi acak — 4 prinsip × 3 status × 4 karakter (Lin Yue, Shen Luo, Mei Ruo, Gu Han) = potensi 48 kombinasi hanya untuk found family, belum termasuk Mentor/Grandmaster. Ini adalah **[ENGINE RISK]** yang akan dicatat di Phase 18 (Implementation Readiness) — jumlah variant dialogue di titik ini berisiko meledak jika tidak dikelola dengan pendekatan modular (mis. dialog tersusun dari blok-blok kondisional yang digabung dinamis, bukan 48 naskah penuh terpisah).

**Rekomendasi mitigasi (bukan spesifikasi final):** setiap sub-entry dipecah menjadi DUA lapis — (1) baris pembuka yang ditentukan `state_final_principle` (4 varian tetap), (2) baris penutup yang ditentukan status relationship karakter (3 varian per karakter). Kombinasi dirakit dari dua lapis ini, bukan 48 naskah independen — mengurangi beban produksi aktual menjadi ~4+3×4=16 blok teks yang dirangkai, bukan 48.

---

## `dialog_a07_d015` — I Am Not You (Final Confrontation)

| Field | Value |
|---|---|
| `dialogue_id` | `dialog_a07_d015` |
| `speaker` | Jiang Yan imprint / Protagonis |
| `listener` | Satu sama lain |
| `context` | `quest_a07_c02_002`, klimaks emosional utama campaign |
| `trigger` | Memasuki ruang terdalam setelah `flag_last_night_complete` |
| `prerequisites` | `flag_last_night_complete == true` |
| `state_conditions` | Dimodifikasi `state_identity_stance` dari Arc III (sudah dicatat di Quest Graph) |
| `relationship_conditions` | Tidak ada — ini adalah konfrontasi dengan diri sendiri, bukan NPC relasional |
| `faction_conditions` | Tidak ada langsung |
| `memory_conditions` | Seluruh memory chain (implisit — protagonis membawa semua yang sudah dipelajari) |
| `dialogue_purpose` | Revelation (puncak), Character Development (puncak) — MSB: "titik paling penting dari seluruh campaign" |
| `emotional_state` | Jiang Yan: harapan yang lelah. Protagonis: tegas, bukan marah |
| `information_revealed` | Tidak ada informasi baru — payoff murni karakter |
| `player_choices` | **[DESIGN GAP]** — apakah "Aku bukan kau" adalah baris tetap (fixed line) atau ada variasi tekstual berdasarkan `state_identity_stance`. Direkomendasikan: BARIS INTI tetap sama ("Aku bukan kau") sebagai jangkar naratif yang tidak boleh diubah, tapi kalimat SEBELUM dan SESUDAHnya bervariasi (lihat tiga versi di bawah) |
| `choice_consequences` | N/A — ini adalah revelation wajib, bukan choice |
| `followup_dialogue` | Mengarah ke Entity's Truth, lalu `quest_a07_c03_003` |
| `alternate_versions` | Previous-choice-aware version (tiga varian berdasarkan `state_identity_stance`) |

**Tiga versi (draft, bukan final — dipilih sebagai salah satu verbatim di bawah):**

- **Jika `deny` (Arc III):** Baris pembuka protagonis lebih panjang — pengakuan bahwa penolakan yang dulu ia pertahankan sekarang menjadi sesuatu yang ia PILIH secara sadar, bukan sekadar pertahanan diri
- **Jika `accept_cautious`:** Baris paling ringkas — "Aku bukan kau" terasa sebagai kesimpulan logis dari sikap hati-hati yang konsisten sejak awal
- **Jika `seek_truth`:** Protagonis dapat merujuk detail spesifik yang ia temukan lewat investigasi ekstra (Mei Ruo relationship tinggi) sebagai bukti bahwa penolakannya berbasis pemahaman penuh, bukan penolakan buta

---

## Dialogue-NPC Coverage Verification

Tabel berikut memverifikasi bahwa setiap karakter dengan `character_arc_id` di Phase 5 memiliki minimal satu dialogue_id state-conditional yang diformalkan di fase ini — jika ada yang kosong, itu adalah gap yang harus dicatat, bukan diabaikan:

| Karakter | dialogue_id Terformalkan | Status |
|---|---|---|
| Lin Yue | `dialog_a07_d001_linyue` | ✅ Terformalkan (via matrix hub) |
| Shen Luo | `dialog_a07_d001_shenluo` | ✅ Terformalkan (via matrix hub) |
| Mei Ruo | `dialog_a07_d001_meiruo` | ✅ Terformalkan (via matrix hub) |
| Gu Han | `dialog_a07_d001_guhan` | ✅ Terformalkan (via matrix hub) |
| Mentor | `dialog_a06_d041`, `dialog_a07_d001_mentor` | ✅ Terformalkan |
| Grandmaster | `dialog_a04_d033`, `dialog_a07_d001_grandmaster` | ✅ Terformalkan |
| Mo Chen | **Tidak ada dialogue_id terformalkan di fase ini** | ⚠️ GAP — konsisten dengan gap besar yang sudah dicatat di Phase 5-6; dialog Mo Chen bergantung penuh pada resolusi arahnya terlebih dulu |
| Jiang Yan | `dialog_a07_d015` | ✅ Terformalkan |
| Entity | **Tidak ada dialogue_id terpisah diformalkan** — dialog Entity (Chapter 5.4, 7.2) dicatat di Quest Graph sebagai fixed revelation lines, tidak memerlukan versi kondisional kompleks karena sifatnya sebagai revelation tunggal, bukan relationship-driven | ✅ Cukup (by design, bukan gap) |

**Hasil verifikasi:** satu gap terbuka (Mo Chen), konsisten dan sudah diketahui — bukan temuan baru. Tidak ada karakter yang TERLEWAT tanpa penjelasan.

---

## Verbatim Dialogue Selection

Sesuai instruksi "pilih dialogue penting yang memang perlu ditulis verbatim," berikut daftar final dengan justifikasi — bukan seluruh dialogue_id di atas, hanya yang benar-benar memerlukan naskah tetap karena signifikansi tematik atau karena MSB sendiri sudah mengutipnya secara eksplisit:

| dialogue_id | Alasan dipilih verbatim | Baris MSB (jika ada) |
|---|---|---|
| `dialog_a04_d033` | Sudah dikutip MSB §39 secara eksplisit sebagai satu baris tetap | "Aku juga pernah menginginkannya. Lalu aku melihat apa yang terjadi setelahnya." |
| `dialog_a06_d041` (bagian revelation utama, bukan cross-reference Grandmaster) | Sudah dikutip MSB §38 secara eksplisit | "Cara kau memegang pedang... Aku pernah melihatnya." |
| `dialog_a07_d015` (baris inti "Aku bukan kau") | MSB secara eksplisit menyebut ini "titik paling penting dari seluruh campaign" — baris ini TIDAK BOLEH bervariasi bentuknya meski konteks di sekitarnya bervariasi | "Aku membuatmu untuk menyelesaikan apa yang gagal kuselesaikan." / "Tidak." / "Aku bukan kau." |
| Memory `memory_a03_m01` (baris "Kalau dunia harus membenciku, biarkan") | Sudah dikutip MSB secara eksplisit, dan reliability/ambiguitasnya (dicatat Phase 7) membuatnya SANGAT SENSITIF terhadap perubahan delivery — harus verbatim untuk menjaga ambiguitas yang sudah dirancang | "Kalau dunia harus membenciku, biarkan." |
| Entity, Chapter 5.4 (dua baris) | Sudah dikutip MSB secara eksplisit, fixed revelation | "Kau membunuhku sekali." / "Aku adalah alasan kalian menyebut dunia ini sebagai anugerah." |
| Hidden Resolution epilogue, Lin Yue's question | Sudah dikutip MSB §36 penuh sebagai closing scene | "Kalau kau bisa mengulang hidupmu, apakah kau akan memilih hal yang sama?" / "Tidak." |

**Prinsip seleksi:** enam entri di atas dipilih karena SEMUANYA sudah dikutip MSB secara eksplisit sebagai baris tetap — bukan karena saya menciptakan baris baru yang "terasa penting." Ini menjaga agar Verbatim Dialogue Selection tetap setia pada Critical Constraint (tidak mengarang dialog baru yang mengklaim status "wajib" tanpa dasar MSB). Dialog LAIN yang saya tulis sebagai draft di badan dokumen ini (mis. "Bahkan Grandmaster pernah bercerita...") secara eksplisit ditandai draft/bukan final, dan TIDAK masuk daftar verbatim — itu tetap tanggung jawab tim dialogue writer untuk finalisasi.

---

## Design Gap & Recommendation Ringkasan Fase Ini

1. **Nilai numerik threshold** (`state_rel_grandmaster >= threshold_tinggi`, dan berbagai threshold relationship lain) — belum dispesifikasikan sebagai angka konkret di seluruh dokumen manapun. **Direkomendasikan menjadi item prioritas Phase 15 (Story State Catalog)** karena ini memengaruhi implementasi across-the-board, bukan cuma dialogue
2. **[ENGINE RISK] eksplisit dicatat:** kompleksitas matrix `dialog_a07_d001` (potensi 48 kombinasi found family saja) — mitigasi direkomendasikan (blok modular 2-lapis), tapi keputusan arsitektur akhir ada di tim engineering, bukan dokumen naratif ini
3. **Mo Chen dialogue** — tidak dapat diformalkan hingga arah karakternya diputuskan (gap yang sudah diketahui sejak Phase 5)

---

**File berikutnya:** `08-npc-location-catalog.md` — NPC dan Location Bible, akan menyelesaikan sebagian besar `[DESIGN GAP]` lokasi spesifik yang tersebar di seluruh dokumen sebelumnya, dan memformalkan roster pavilion Arc I yang masih terbuka sejak Phase 2.
