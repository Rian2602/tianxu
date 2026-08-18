# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 05. Faction Production Bible

**Status:** DRAFT — Phase 6 of 18
**Depends on:** `00-narrative-architecture.md` §0.9, `03-quest-graph-arc1-2.md`, `03b-quest-graph-arc3-7.md`, `04-character-arcs.md`
**Prinsip wajib:** tidak ada faksi yang sepenuhnya good/evil. Setiap faksi punya `public_position` dan `hidden_position` yang berbeda — perbedaan ini bukan kebohongan sinis, tapi kompleksitas ideologis yang genuine.

---

## FACTION TIAN XU ORTHODOX

| Field | Value |
|---|---|
| `faction_id` | `faction_tianxu_orthodox` |
| `ideology` | Sistem cultivation, meski tidak sempurna, harus dipertahankan karena konsekuensi penghentiannya (keruntuhan teknik, kerajaan, keseimbangan dunia) lebih buruk daripada mempertahankan status quo yang bermasalah |
| `public_position` | Tian Xu adalah pelindung dunia dari Ancient Calamity — narasi resmi MSB §16, dipertahankan secara terbuka |
| `hidden_position` | Mengetahui (setidaknya di level kepemimpinan — Grandmaster) bahwa "yang disegel bukan musuh" dan bahwa Tian Xu sendiri adalah mekanisme yang memberi makan segel, bukan sekadar menjaganya. Kebenaran ini disembunyikan bukan demi kekuasaan semata, tapi karena keyakinan jujur bahwa kepanikan publik akan mempercepat keruntuhan yang mereka takutkan |
| `leader` | `npc_grandmaster` |
| `internal_conflict` | Ketegangan antara anggota yang benar-benar percaya narasi resmi (mayoritas murid dan guru biasa) vs segelintir yang mengetahui kebenaran (Grandmaster, kemungkinan sebagian Hidden Guardians yang berafiliasi ganda) — ini menciptakan faksi yang secara internal tidak monolitik meski tampak seragam dari luar |
| `relationship_with_Tian_Xu` | Faksi INI adalah Tian Xu — tidak ada jarak struktural, hanya jarak informasi antara level kepemimpinan dan anggota biasa |
| `relationship_with_protagonist` | Dimulai netral-institusional (protagonis adalah murid biasa) → menjadi kompleks pasca-Arc IV saat protagonis mengetahui kebenaran yang faksi ini sembunyikan → dapat menjadi ally bersyarat jika `state_rel_grandmaster` tinggi dan `state_final_principle=preserve` atau `transform` |
| `questline` | `quest_a04_c03_003` (pengenalan penuh lewat Grandmaster), dialog opsional Arc V-VI, posisi final di `quest_a07_c01_001` |
| `major_choices` | Bagaimana Grandmaster (dan secara meluas, faksi ini) merespons `state_truth_spread_level` tinggi — apakah bereaksi represif atau mulai bertransisi menuju transparansi bertahap |
| `faction_state` | Modifier: `state_rep_tianxu` (dari branch Chapter 2.3), `state_rel_grandmaster` (dari Chapter 4.3+), `state_truth_spread_level` (reaksi negatif proporsional terhadap nilai tinggi) |
| `faction_reactions` | `state_rep_tianxu` rendah → pengawasan lebih ketat terhadap found family (autonomous trigger Grandmaster, lihat Character Bible); `state_truth_spread_level` tinggi → tekanan internal meningkat, kemungkinan perpecahan internal faksi sendiri (`[DESIGN GAP]` — apakah ada sempalan Orthodox yang berubah pikiran, belum diformalkan) |
| `possible_outcomes` | Reformed (jika Grandmaster relationship tinggi + Transform principle) / Last Stand (mempertahankan posisi hingga konflik terbuka di Chapter 7.1 jika relationship rendah + Destroy principle) / Status Quo (ending Unbroken Heaven — faksi ini "menang" secara struktural tapi pertanyaan moral tetap terbuka) |
| `ending_impact` | Faksi paling menentukan identitas ending Unbroken Heaven — apakah dicapai dengan faksi ini "diperbaiki" (Shen Luo sebagai New Grandmaster) atau "dipertahankan apa adanya" (Grandmaster asli tetap memimpin) adalah perbedaan kualitas ending yang signifikan, bukan cuma akses (lihat prinsip ENDING ACCESS vs ENDING QUALITY di Phase 13 nanti) |

---

## FACTION REFORMISTS

| Field | Value |
|---|---|
| `faction_id` | `faction_reformists` |
| `ideology` | Sistem harus diubah, bukan dipertahankan apa adanya, tapi juga bukan dihancurkan total — perubahan bertahap dan terkelola lebih baik daripada revolusi yang tidak terkendali atau status quo yang korup |
| `public_position` | Tian Xu perlu direformasi dari dalam — kritik terhadap institusi yang disampaikan melalui jalur yang sah, bukan pemberontakan terbuka |
| `hidden_position` | Sebagian anggota faksi ini sudah mencurigai (tapi belum tentu mengetahui detail penuh) bahwa masalah sistemik lebih dalam dari sekadar "kebijakan yang perlu diperbaiki" — mereka curiga ada kebenaran yang disembunyikan, tapi kekurangan bukti konkret hingga protagonis menemukannya |
| `leader` | `[DESIGN GAP]` — MSB tidak menyebut nama pemimpin Reformists. Direkomendasikan: karakter baru minor (Ambient/Quest NPC tingkat menengah) daripada memaksakan salah satu dari sembilan karakter utama untuk menghindari over-determinasi peran |
| `internal_conflict` | Ketegangan antara sayap moderat (percaya reformasi bertahap cukup) dan sayap yang semakin tidak sabar (mulai condong ke arah posisi Liberation seiring `state_truth_spread_level` meningkat) |
| `relationship_with_Tian_Xu` | Berada di dalam struktur Tian Xu tapi sebagai suara kritis — bukan pemberontak, tapi bukan pula loyalis tanpa syarat |
| `relationship_with_protagonist` | Berpotensi menjadi ally paling natural jika `state_final_principle=transform` — Reformists secara ideologis paling dekat dengan filosofi "ubah hubungan, jangan hancurkan atau pertahankan buta" |
| `questline` | Tidak ada quest terpusat MSB eksplisit — faksi ini berfungsi sebagai *destination* natural untuk `state_truth_spread_level` sedang-tinggi, bukan questline linear tersendiri. `[DESIGN GAP]` — apakah faksi ini butuh questline dedicated akan direkomendasikan di bagian akhir dokumen |
| `major_choices` | Seberapa jauh faksi ini didorong menuju radikalisasi tergantung kombinasi `state_truth_spread_level` dan hasil Mountain Gate Incident (`flag_mountain_gate_repeated` mendorong sayap tidak sabar semakin vokal) |
| `faction_state` | `state_rep_reformists` (baru, ditulis terutama lewat `state_truth_spread_level` dan hasil branch Chapter 2.3 Confront) |
| `faction_reactions` | Truth spread tinggi → dukungan terbuka terhadap protagonis; Mountain Gate gagal → sayap radikal faksi ini condong bergabung wacana dengan Liberation |
| `possible_outcomes` | Menjadi basis kekuatan utama ending New Heaven jika `state_final_principle=transform` tercapai dengan dukungan faksi ini kuat |
| `ending_impact` | Faksi paling relevan untuk ending New Heaven — representasi bahwa perubahan dapat dicapai tanpa kehancuran total |

---

## FACTION LIBERATION

| Field | Value |
|---|---|
| `faction_id` | `faction_liberation` |
| `ideology` | Cultivation harus dihentikan — sumber masalah bukan sekadar penyalahgunaan sistem, tapi keberadaan sistem itu sendiri |
| `public_position` | Terang-terangan menentang cultivation sebagai institusi, menganjurkan penghentian total, kadang dipandang ekstremis oleh mayoritas masyarakat cultivation |
| `hidden_position` | **Ini bagian krusial untuk menghindari faksi jadi sepenuhnya "benar":** sebagian anggota Liberation tidak sepenuhnya memahami skala kerugian manusiawi jika cultivation dihentikan mendadak (keruntuhan kerajaan, hilangnya mata pencaharian jutaan cultivator, monster spiritual yang berubah tanpa kendali) — idealisme mereka genuine, tapi belum tentu bertanggung jawab penuh terhadap konsekuensinya. Ini paralel dengan MSB §19 (taruhan yang dijelaskan Grandmaster), memberi faksi ini kompleksitas yang sama dengan Orthodox, hanya dari arah berlawanan |
| `leader` | `[DESIGN GAP]` — direkomendasikan: `npc_gu_han` berpotensi menjadi Faction Leader di sini sebagai salah satu end_state-nya (MSB §37 mencantumkan "Faction Leader" sebagai possible state Gu Han) — ini BUKAN klaim bahwa Gu Han adalah pemimpin SEJAK AWAL cerita, melainkan potensi perkembangan jika relationship dan pilihan pemain mengarah ke sana |
| `internal_conflict` | Antara anggota yang menginginkan penghentian gradual-tapi-pasti vs yang menginginkan aksi langsung/radikal (berpotensi termasuk sabotase terhadap formation, meski MSB tidak eksplisit menyebut aksi kekerasan faksi ini) |
| `relationship_with_Tian_Xu` | Oposisi terbuka |
| `relationship_with_protagonist` | Berpotensi ally kuat jika `state_final_principle=destroy`; berpotensi menjadi kritikus keras jika protagonis memilih Preserve atau bahkan Transform (faksi ini mungkin memandang Transform sebagai "setengah-setengah" yang tidak cukup) |
| `questline` | Terhubung erat dengan `branch_a05_c03_b04` (Gu Han's position di Found Family Crisis) dan `autonomous_trigger_condition` Gu Han (membangun jaringan dengan Liberation secara independen jika kondisi terpenuhi — sudah dicatat di Character Bible) |
| `major_choices` | Apakah faksi ini mendukung Mountain Gate intervention atau melihatnya sebagai upaya sia-sia mempertahankan sistem yang seharusnya dihentikan — posisi ini dapat memecah faksi secara internal |
| `faction_state` | `state_rep_liberation` (ditulis terutama lewat branch Chapter 2.3 Confront, `flag_mountain_gate_repeated`, dan posisi Gu Han di Chapter 5.3) |
| `faction_reactions` | Truth spread tinggi + Mountain Gate gagal → faksi ini mendapat momentum wacana signifikan; jika protagonis secara konsisten memilih jalur institusional (Obey), faksi ini memandang protagonis dengan skeptis |
| `possible_outcomes` | Basis kekuatan utama ending Mortal Dawn |
| `ending_impact` | Faksi paling relevan untuk ending Mortal Dawn — "sebagian berterima kasih" (MSB, deskripsi ending ini) kemungkinan besar merujuk pada anggota faksi ini |

---

## FACTION HIDDEN GUARDIANS

| Field | Value |
|---|---|
| `faction_id` | `faction_hidden_guardians` |
| `ideology` | Tidak ada solusi sempurna — baik mempertahankan, menghancurkan, maupun mengubah sistem punya konsekuensi yang tidak dapat sepenuhnya dihindari. Peran mereka adalah menjaga keseimbangan informasi dan mencegah keputusan gegabah dari pihak manapun, termasuk dari Tian Xu Orthodox sendiri |
| `public_position` | Nyaris tidak memiliki "posisi publik" — faksi ini beroperasi dalam bayang-bayang, tidak dikenal luas oleh masyarakat cultivation umum |
| `hidden_position` | Menyimpan pengetahuan historis yang bahkan lebih lengkap dari Forbidden Archive Tian Xu sendiri — kemungkinan termasuk detail tentang Cycle Formation dan Second Life yang bahkan Grandmaster tidak sepenuhnya ketahui |
| `leader` | `[DESIGN GAP]` — kandidat kuat: `npc_mo_chen` (mengikuti rekomendasi di Character Bible), tapi ini belum final |
| `internal_conflict` | Antara anggota yang percaya "tidak ikut campur" adalah cara terbaik menjaga keseimbangan vs yang percaya intervensi terbatas (seperti kemunculan Mo Chen kepada protagonis) kadang diperlukan |
| `relationship_with_Tian_Xu` | Paralel, bukan bagian dari struktur formal — mengawasi dari luar, kadang bersinggungan (Mo Chen jelas memiliki akses informasi yang seharusnya tidak dimiliki murid biasa) |
| `relationship_with_protagonist` | Awalnya observasional (Mo Chen mengamati, memberi sedikit info, menghilang) → berpotensi menjadi sumber informasi krusial di Arc IV-VI jika rekomendasi kemunculan berulang Mo Chen diterima |
| `questline` | `quest_a03_c02_002` (kontak pertama), dan potensi kemunculan lanjutan yang direkomendasikan di Character Bible (Chapter 4.2, 5.4, 6.3) — **belum final, tergantung resolusi gap Mo Chen** |
| `major_choices` | `[DESIGN GAP]` — bergantung pada seberapa jauh peran Hidden Guardians diperluas melalui Mo Chen |
| `faction_state` | Tidak ada state numerik konvensional (reputasi) karena faksi ini tidak berinteraksi dengan publik — lebih tepat diukur lewat `flag_mo_chen_met` dan progres pengungkapan informasi yang mereka berikan |
| `faction_reactions` | Cenderung reaktif terhadap titik-titik krusial cerita (revelation besar), bukan terhadap aksi rutin pemain — konsisten dengan sifat "menjaga keseimbangan" faksi ini |
| `possible_outcomes` | Faksi ini kemungkinan besar tidak memiliki "outcome menang/kalah" konvensional — perannya lebih sebagai fasilitator informasi daripada pihak yang bertarung untuk hasil tertentu |
| `ending_impact` | Paling relevan untuk ending Second Life (Hidden Resolution) — faksi yang "tidak percaya solusi sempurna" secara tematis paling dekat dengan penemuan protagonis bahwa pilihan keempat (bukan Preserve/Destroy/Sacrifice) mungkin ada |

---

## PRIMORDIAL ENTITY (5th Force)

| Field | Value |
|---|---|
| `faction_id` | N/A secara formal — diperlakukan sebagai 5th force struktural, bukan faction dengan anggota konvensional |
| `ideology` | Bertahan hidup dan, seiring waktu, keinginan untuk tidak lagi dieksploitasi — bukan ideologi politik dalam pengertian faksi manusia, tapi memiliki koherensi internal yang setara |
| `public_position` | Tidak memiliki "posisi publik" dalam pengertian konvensional — bagi mayoritas dunia, ia adalah "Calamity," sebuah ancaman abstrak, bukan pihak dengan sudut pandang |
| `hidden_position` | MSB §34: "manusialah yang menyerang lebih dahulu" — perspektif yang sepenuhnya tersembunyi dari narasi manapun (baik resmi maupun Forbidden Archive) hingga Chapter 5.4 |
| `leader` | N/A — Entity adalah entitas tunggal, bukan organisasi |
| `internal_conflict` | N/A dalam pengertian faksi, tapi memiliki konflik internal personal: keinginan dipahami sebagai korban vs kesadaran bahwa balasannya sendiri (menghancurkan manusia) tidak sepenuhnya dapat dibenarkan — detail lengkap di Character Bible `chararc_entity` |
| `relationship_with_Tian_Xu` | Entity ADALAH yang dijaga/diberi-makan oleh Tian Xu — hubungan paling fundamental dan paling eksploitatif dalam seluruh cerita |
| `relationship_with_protagonist` | Personal dan langsung sejak Chapter 5.4 — "Kau membunuhku sekali" menciptakan hubungan yang secara harfiah lintas-kehidupan |
| `questline` | Lihat Character Bible `chararc_entity` — dicatat di sini untuk memastikan Entity terpetakan dalam kerangka faction meski secara struktural adalah character arc |
| `major_choices` | N/A — Entity tidak "memilih" dalam pengertian branching quest, tapi eksistensinya adalah pusat gravitasi FINAL DECISION Arc VII |
| `faction_state` | Tidak ada state faction konvensional — state relevan adalah `flag_entity_first_contact`, `flag_entity_truth_known` (dari Quest Graph) |
| `faction_reactions` | Entity bereaksi terhadap skala eksploitasi (`world_event_a05_spiritual_collapse`) lebih dari terhadap aksi spesifik pemain — konsisten dengan `autonomous_trigger_condition` yang sudah dicatat di Character Bible |
| `possible_outcomes` | Lima outcome berbeda sesuai lima ending — lihat Character Bible `chararc_entity` field `end_state` |
| `ending_impact` | MENENTUKAN identitas tiap ending secara literal (dicatat lengkap di Character Bible) |

---

## Faction Alignment Verification (Cross-Check dengan Character Bible)

Tabel berikut memverifikasi ulang (bukan menyalin mentah) draft cross-reference dari akhir Phase 5, dengan detail faksi yang baru selesai di atas:

| Karakter | Draft Awal (Phase 5) | Verifikasi Setelah Faction Bible | Perubahan? |
|---|---|---|---|
| Lin Yue | Reformists atau netral | **Dikonfirmasi netral/independen** — Lin Yue's core belief (melindungi murid, MSB §23) tidak sepenuhnya sejalan dengan ideologi Reformists yang lebih berorientasi struktur politik; ia lebih tepat sebagai figur yang faksi manapun HORMATI tapi tidak KLAIM | Sedikit direvisi dari draft awal |
| Shen Luo | Reformists → potensi Liberation | **Dikonfirmasi** — trajectory retak-keyakinan Shen Luo (Chapter 4.4) paling konsisten dengan Reformists di awal, dengan potensi radikalisasi jika `state_truth_spread_level` sangat tinggi | Tidak berubah |
| Mei Ruo | Tidak terikat faksi | **Dikonfirmasi** — Mei Ruo secara eksplisit adalah figur "kebenaran di atas ideologi", tidak terikat faksi manapun secara formal | Tidak berubah |
| Gu Han | Liberation Faction | **Dikonfirmasi dan diperkuat** — potensi menjadi Faction Leader Liberation adalah salah satu end_state paling kuat yang didukung baik Character Bible maupun Faction Bible | Tidak berubah, diperkuat |
| Mentor | Tian Xu Orthodox (posisi formal) | **Dikonfirmasi dengan catatan** — posisi formal Orthodox, tapi hidden_position personalnya (rekomendasi "pengkhianat" Jiang Yan) menciptakan kompleksitas yang sejalan dengan internal_conflict Orthodox yang baru diformalkan di atas | Diperkuat dengan detail baru |
| Grandmaster | Tian Xu Orthodox (pemimpin) | **Dikonfirmasi** sebagai leader eksplisit `faction_tianxu_orthodox` | Tidak berubah |
| Mo Chen | Hidden Guardians | **Dikonfirmasi sebagai rekomendasi leader** — tapi tetap ditandai sebagai gap paling belum-matang, konsisten dengan catatan Character Bible | Tidak berubah, tapi peran diperkuat (leader, bukan cuma anggota) |
| Jiang Yan | N/A | **Dikonfirmasi N/A** — tapi dicatat bahwa tindakannya (The Gate) paling dekat secara filosofis dengan Reformists/Transform, relevan untuk memahami mengapa `state_final_principle=transform` terasa sebagai "menyelesaikan apa yang gagal diselesaikan Jiang Yan" tanpa mengulang metodenya | Tidak berubah |
| Entity | 5th force | **Dikonfirmasi** sebagai 5th force struktural, bukan faction konvensional | Tidak berubah |

**Hasil verifikasi:** tidak ditemukan kontradiksi antara draft Character Bible dan detail Faction Bible yang baru ditulis. Satu revisi kecil (Lin Yue dari "Reformists" menjadi "netral/independen") dilakukan karena detail ideologi Reformists yang baru diformalkan (fokus pada reformasi struktural-politik) ternyata kurang pas dengan motivasi Lin Yue yang lebih personal/protektif — dicatat di sini sebagai audit terbuka, bukan disembunyikan.

---

## Design Gap & Recommendation Ringkasan Fase Ini

1. **Pemimpin Reformists** — direkomendasikan karakter baru minor, bukan salah satu dari sembilan karakter utama, untuk menghindari over-determinasi peran
2. **Apakah Reformists butuh questline dedicated** — dicatat sebagai gap terbuka; saat ini faksi berfungsi sebagai "destination" dari state lain, bukan sumber quest sendiri. **Rekomendasi:** ini sebenarnya sudah cukup untuk premium RPG quality (MSB §25: fewer+stronger+connected lebih baik dari filler) — menambah questline dedicated berisiko menjadi padding tanpa fungsi naratif baru. Direkomendasikan TIDAK menambah, kecuali Phase 4 (Quest Graph) direvisi untuk kebutuhan spesifik
3. **Apakah ada sempalan internal Orthodox yang berubah pikiran** — dicatat sebagai gap, tidak diformalkan karena tidak ada dukungan MSB eksplisit
4. **Detail lebih jauh peran Hidden Guardians** — bergantung penuh pada resolusi gap Mo Chen dari Phase 5

---

**File berikutnya:** `06-memory-architecture.md` — Memory Bible lengkap mengikuti struktur Fragment → Interpretation → Contradiction → Investigation → Revelation → Recontextualization, merujuk silang seluruh memory_trigger yang sudah tercatat di Quest Graph (Phase 4) dan belief_state tracking yang sudah dimulai (`belief_protagonist_may_be_cause`).
