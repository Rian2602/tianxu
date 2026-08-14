# STORY — Arc Akademi (Fase 1)

> **Status**: Disetujui via wawancara penulis (keputusan cerita)
> **Merujuk**: GDD.md §3 (struktur naratif), §4 (quest DAG), §11 (cakupan Fase 1)
> **Input teknis**: ENGINE_ARCHITECTURE.md §5–§7 (skema quest/dialog/NPC/ingatan)
> **Durasi target**: 1–2 jam per playthrough · **3 playthrough** (3 cabang sikap)

---

## 1. Keputusan Cerita (Ringkasan Disahkan)

| # | Aspek | Keputusan |
|---|---|---|
| 1 | Alur Arc Akademi | **Ujian & adaptasi dulu, lalu insiden** memicu penyelidikan (dua babak berurutan) |
| 2 | Makna 3 cabang quest | **3 sikap terhadap ketidakadilan**: membongkar / mengambil keuntungan / berdiam diri — menggerakkan skala moralitas |
| 3 | Benih ending | **Tidak** — cabang Fase 1 murni variasi konten; arah ending ditentukan pilihan moral arc selanjutnya |
| 4 | Tokoh kunci | **Semua hadir**: mentor, rival, sahabat, figur mencurigakan + kenangan cinta masa lalu (lewat ingatan saja) |
| 5 | Tianyuan Ling | **Jarang bicara, misterius** — hanya di momen penting, kalimat singkat penuh teka-teki |
| 6 | Tone | **Terang** — kehidupan akademi ceria & hangat; firasat tragis tersirat **halus** di akhir |
| 7 | Ingatan pertama | **Istana yang Sunyi** — masa kecil Long Tianxu di istana sebelum diracun |
| 8 | Insiden Act 2 | **Artefak pusaka hilang** (Lonceng Angin Panjang), tuduhan jatuh pada murid baru |
| 9 | Korban | **Murid seangkatan lain** (tidak dikenal dekat) — menguji moralitas tanpa ikatan personal |
| 10 | Nama tokoh | Set B: Gu Canghai, Han Xiu, Su Qing, Mo Yun (lihat §3) |
| 11 | Kota akademi | **Changfeng Cheng (长风城, "Kota Angin Panjang")** |
| 12 | Karakter Chen Xu | Sikap **berubah bertahap** sesuai jumlah ingatan yang pulih — mulai polos, makin dewasa/melankolis seiring ingatan (lihat §3.1) |
| 13 | Ujian masuk | Tes akar spiritual + **sparing vs Han Xiu (pertarungan wajib)** + berburu binatang liar (opsional/sampingan) |
| 14 | Bukti Act 2 | Chen Xu **melihat Mo Yun** diam-diam membawa benda terbungkus dari ruang lonceng |
| 15 | Nasib Zhou Yan | **3a: bebas** · **3b: diusir** · **3c: diusir** (tak ada yang membela — lebih gelap) |
| 16 | Tianyuan Ling | **Pasif murni** — hanya mengumumkan (ingatan terbuka, notifikasi); tidak menjawab pertanyaan di Fase 1 |
| 17 | Penutup q5 | **Konfrontasi langsung dengan Penatua di 3aa**; cabang lain: kebenaran lewat Mo Yun tanpa konfrontasi |
| 18 | Struktur akademi | **Satu kompleks akademi, 3 paviliun** (五行阁/兵锋院/御灵宗) — terpusat, mudah dinavigasi |
| 19 | Hasil sparing | **Pemain bisa menang/kalah** — menang = pengakuan & reputasi naik; kalah = motivasi & dialog berbeda *(diimplementasikan 2026-08-14, G4a: kalah tetap menyelesaikan quest spar + flag `spar_kalah` + dialog Gu Canghai berbeda; penalti KO tetap berlaku)* |
| 20 | Progresi ranah | **Tiap ranah = 10 tingkat**; progresi via aktivitas (berkultivasi/grounding, berburu monster, menang sparing) yang menghasilkan qi/exp — rajin beraktivitas = makin cepat naik (detail teknis: ENGINE_ARCHITECTURE §9.1) |
| 21 | Side quest | **Berburu, bantu Su Qing, tugas Mo Yun** — data terpisah, **bisa diulang** setelah selesai untuk menaikkan ranah, dilarang bertabrakan dengan main quest |
| 22 | Benih romansa Su Qing | **Benih halus** — isyarat sangat halus (kontras dengan kenangan cinta masa lalu Long Tianxu); jalinan dibuka di arc berikutnya |
| 23 | Han Xiu pasca-3a | **Mulai menghormati** Chen Xu (rival → semi-sekutu) — persaingan tetap tapi hangat |
| 24 | Motif Mo Yun | **Hutang budi** pada Penatua — membayarnya dengan diam |
| 25 | Tangga ranah | **9 ranah penuh didefinisikan sekarang** (Pengumpul Qi → … → Penantang Surga); Fase 1 hanya memakai 1–2 ranah |

---

## 2. Sinopsis — Tiga Babak

### Act 1 — Ujian & Adaptasi *(tone terang)*

Chen Xu tiba di **Changfeng Cheng** dari **Yunxi Cun** untuk mengikuti ujian masuk akademi. Di gerbang ia bertemu **Gu Canghai**, guru senior yang menyambut murid baru. Di awal, Chen Xu tampil sebagai **pemuda desa yang polos & ingin tahu** — ia baru menyimpan sedikit ingatan (kurva karakter §3.1). Ujian masuk: **tes akar spiritual** (perkenalan mekanik kultivasi), lalu **sparing persahabatan vs Han Xiu** — pertarungan wajib utama Fase 1 yang membangun dinamika rival. **Berburu binatang liar** di area berburu tersedia sebagai aktivitas opsional/sampingan. Ia berkenalan dengan **Su Qing** (sahabat, ceria) dan **Han Xiu** (rival, berbakat & kompetitif). Pemain **memilih 1 dari 3 akademi** (Elemen/Senjata/Summoning) — lapisan setup, tidak mengubah alur cerita, hanya membuka pool skill (GDD §5.2).

**Puncak Act 1**: saat menatap arsitektur aula akademi (atau aroma dupa tua di perpustakaan), sesuatu dalam diri Chen Xu bergetar — **Tianyuan Ling menyala** dan ingatan pertama terbuka: **"Istana yang Sunyi"** (mem_01). Chen Xu tahu ia membawa masa lalu yang tak boleh diketahui siapa pun. *(Firasat halus pertama.)*

### Act 2 — Insiden: Lonceng Angin Panjang *(transisi)*

Beberapa hari kemudian, **Lonceng Angin Panjang (长风钟)** — pusaka akademi sejak kota berdiri — **hilang** dari ruang penyimpanan. Tuduhan jatuh pada murid baru: **Zhou Yan (周炎)**, murid pendiam seangkatan yang kebetulan terlihat di dekat ruang lonceng malam sebelumnya.

Chen Xu kebetulan **melihat Mo Yun** — pustakawan misterius — diam-diam membawa **benda terbungkus** keluar dari ruang lonceng pada malam kejadian. Ini membuktikan Zhou Yan tidak bersalah sekaligus menjelaskan kelakuan aneh Mo Yun sejak kejadian. Kini Chen Xu memegang informasi yang bisa menyelamatkan — atau memanfaatkan — orang lain. *(Momen ini memicu quest bercabang.)*

### Act 3 — Tiga Sikap (3a/3b/3c) → Menyatu di q5

| Cabang | Sikap | Isi | Efek moralitas |
|---|---|---|---|
| **3a** | **Membongkar** | Bantu Zhou Yan: cari bukti pembebasan, hadapi pihak akademi, pertaruhkan nama baik sendiri | Naik (+), reputasi Su Qing & sebagian murid naik; berani menantang struktur |
| ├─ **3aa** | Konfrontasi langsung | Hadapi Penatua/pihak akademi secara terbuka dengan bukti yang ada | Naik (+), lebih berani, risiko reputasi sebagian |
| └─ **3ab** | Kumpulkan bukti diam-diam | Selidiki pelan-pelan (termasuk memancing info Mo Yun), baru mengungkap saat pasti | Naik (+ lebih kecil), lebih aman, hubungan Mo Yun naik |
| **3b** | **Mengambil keuntungan** | Manfaatkan situasi: tawar "bantuan" dengan imbalan, atau pakai rumor untuk menjatuhkan pesaing (Han Xiu) & naik posisi | Turun (−), reputasi sebagian naik (yang diuntungkan), hubungan Su Qing turun |
| **3c** | **Berdiam diri** | Tidak terlibat, fokus latihan; biarkan kasus berjalan apa adanya | Netral (0/sedikit), Su Qing kecewa (hubungan turun) |

Setiap cabang membuka **ingatan berbeda** (naratif murni — tidak memberi kekuatan, GDD §2.1). Semua cabang **menyatu kembali di q5**.

### Penutup — q5 (kebenaran) & Firasat

Di q5, kebenaran terungkap: **Lonceng Angin Panjang diambil oleh Penatua akademi** — bukan dicuri — untuk keperluan rahasia yang "tak boleh dibocorkan". Zhou Yan dijadikan **kambing hitam** demi ketenangan akademi. **Mo Yun** ternyata tahu dari awal dan memilih diam *(itu sebabnya ia tampak mencurigakan)*.

Di cabang **3aa**, Chen Xu **berhadapan langsung dengan Penatua** — ia menuntut jawaban, dan Penatua menyingkirkannya dengan dingin: kekuatan Chen Xu belum cukup untuk melawan sistem. *(Penutup paling dramatis; tone sedikit lebih tegang.)* Di cabang lain, kebenaran datang **lewat Mo Yun** tanpa konfrontasi.

Chen Xu — dengan ingatan pertama yang masih segar — menyadari **pola lama yang sama**: *yang lemah dikorbankan untuk yang kuat*. Ini benih tema besar (GDD §1.2) — disampaikan **halus**, tanpa kekerasan: hanya ketidaknyamanan, pertanyaan, dan tekad kecil. Tone tetap terang hingga akhir babak; layar penutup arc mengarahkan ke Arc berikutnya (Sekte).

---

## 3. Tokoh Fase 1

| ID | Nama | Hanzi | Makna | Peran | Catatan cerita |
|---|---|---|---|---|---|
| `npc_gucanghai` | Gu Canghai | 古沧海 | "Laut Tua" | **Mentor** — guru senior penyambut murid baru | Bijak, tenang, sedikit bicara, banyak tahu. Menjadi pembimbing Chen Xu. Reaksinya di q5 bergantung pilihan pemain. |
| `npc_hanxiu` | Han Xiu | 韩修 | "Terampil" | **Rival** — murid berbakat seangkatan | Kompetitif, sedikit sombong, tidak jahat. Persaingan sehat; pasca-3a **mulai menghormati** Chen Xu (rival → semi-sekutu). |
| `npc_suqing` | Su Qing | 苏清 | "Jernih" | **Sahabat** — murid baru seangkatan | Ramah, jujur, ceria. Pendukung Chen Xu. Kecewa di cabang 3b/3c — menggerakkan hubungan NPC. **Benih romansa halus** (kontras dengan kenangan cinta masa lalu Long Tianxu); jalinan di arc berikutnya. |
| `npc_moyun` | Mo Yun | 墨云 | "Awan Tinta" | **Figur mencurigakan** — pustakawan/penjaga gudang artefak | Red herring: tampak mencurigakan, tahu kebenaran Lonceng sejak awal, memilih diam karena **hutang budi pada Penatua**. Kunci info di q5. |
| `npc_zhouyan` | Zhou Yan | 周炎 | — | **Korban** — murid pendiam yang dituduh | Murid seangkatan yang tidak dikenal dekat; nasibnya ditentukan pilihan pemain di cabang (3a bebas, 3b/3c diusir). |
| `npc_penatua` | Penatua An (*usulan*) | 安长老 | "Damai" (ironis) | **Antagonis kecil** — Penatua akademi | Mengambil Lonceng untuk keperluan rahasia; menjadikan Zhou Yan kambing hitam demi ketenangan. Dikonfrontasi Chen Xu di cabang 3aa. |
| `npc_penjaga` | Penjaga Gerbang | — | — | NPC pengantar Act 1 | Quest pengenalan "Bicaralah dengan Penjaga Gerbang" (contoh quest `talk` pertama). |
| *(ingatan)* | Eks-kekasih Long Tianxu | — | — | **Hanya lewat ingatan**, bukan NPC hadir | Isyarat paling halus: bayangan sosok di mem_01 ("Istana yang Sunyi"). Jalinan dibuka di arc selanjutnya. |

### 3.1 Kurva Karakter Chen Xu (berbasis ingatan yang pulih)

> Keputusan penulis: **sikap Chen Xu berubah bertahap** — bergantung berapa banyak ingatan yang sudah dipulihkan. Fase 1 = pengumpulan ingatan awal.

| Ingatan terpulih | Sikap Chen Xu | Dampak pada dialog/quest |
|---|---|---|
| 0 (awal Act 1) | Polos, ingin tahu, sedikit canggung — anak desa berbakat; sesekali "perasaan aneh" tanpa sebab | Opsi dialog netral/ceria |
| `mem_01` (akhir Act 1) | Gelisah; rasa kehilangan tanpa sebab; bicara mulai hati-hati | Opsi dialog "hati-hati/melankolis" mulai muncul |
| `mem_02/03/04` (Act 3, sesuai cabang) | Sikap berubah signifikan sesuai isi ingatan — hangat menolong / curiga & sinis / tertutup & menghindar | Opsi dialog tertentu **hanya muncul setelah ingatan terkait pulih** (gating ingatan — pola sama seperti gating moralitas GDD §3.4) |

**Aturan ketat**: ingatan memengaruhi **sikap & pilihan dialog** — tetapi tetap **tidak pernah** memberi kekuatan mekanik (GDD §2.1). Kekuatan hanya lewat jalur kultivasi konvensional.

---

> Nama korban (Zhou Yan) & Penatua (usulan: An, 安长老) adalah **usulan** — silakan diganti saat penulisan konten.

---

## 4. Ingatan (Memories) Fase 1

> Aturan kunci (GDD §2.1): ingatan **naratif murni**, tidak membuka skill/power. Tampil di panel Tianyuan Ling; terkunci tampil "???". Ingatan yang pulih **mengubah sikap & membuka opsi dialog** Chen Xu (§3.1) — tetapi tetap tanpa kekuatan mekanik.

| ID | Judul | Isi singkat | Terbuka via |
|---|---|---|---|
| `mem_01` | **Istana yang Sunyi** | Masa kecil Long Tianxu di istana sebelum diracun; kehangatan singkat, bayangan sosok (calon eks-kekasih), dan kesunyian aula | Act 1 — quest pengenalan selesai |
| `mem_02` | **Kebaikan yang Terlupakan** | Tianxu muda menolong orang asing yang ternyata **dewa tersesat** — asal-usul Tianyuan Ling | Cabang **3a** (membongkar) |
| `mem_03` | **Racun di Balik Senyum** | Momen diracuni selir ayahnya — pengkhianatan diam-diam dari orang terdekat | Cabang **3b** (ambil keuntungan) |
| `mem_04` | **Pengasingan** | Saat diusir dari istana, sendirian di jalan — kesunyian yang memilih diam | Cabang **3c** (berdiam diri) |

Total 4 ingatan di Fase 1 (panel menampilkan "Ingatan (x/4)"). Setiap playthrough hanya membuka 2 (mem_01 + satu cabang) — mendorong replayability.

---

## 5. Suara Tianyuan Ling (Gaya)

**Jarang, misterius, dan pasif murni** (disahkan). Hanya muncul di momen penting; kalimat singkat, penuh teka-teki, sedikit dingin tapi tidak jahat. Tidak pernah memberi jawaban langsung — **tidak menjawab pertanyaan pemain** di Fase 1 (dialog interaktif dengan Sistem ditunda ke arc berikutnya).

Contoh gaya (untuk penulisan konten):
- Saat ingatan pertama terbuka: *"[Sistem] ...Sepotong masa lalu telah kembali."*
- Saat quest besar selesai: *"[Sistem] Jalanmu baru dimulai."*
- Saat pemain memilih cabang 3a: *"[Sistem] Kau memilih untuk menolong. Ingat: kebaikan pun punya harga."*
- Cabang 3b: *"[Sistem] Mengambil. Seperti yang lain."* *(nada samar — bukan penghakiman eksplisit)*
- Cabang 3c: *"[Sistem] Diam juga sebuah pilihan."*
- Saat q5: *"[Sistem] Pola yang sama. Kau melihatnya, bukan?"*

Tampil di **log utama** dengan prefiks `[Sistem]` + warna khusus, dan masuk ke **Log Sistem** panel Tianyuan Ling.

---

## 6. Tone, Bahasa & Durasi

- **Tone**: terang & hangat (kehidupan akademi, persahabatan, persaingan sehat). Firasat tragis hanya **tersirat halus** — via ingatan, perasaan "sudah pernah terjadi", dan kebenaran q5 yang tidak nyaman — tanpa kekerasan/kejelasan gelap.
- **Bahasa**: Bahasa Indonesia; istilah teknis (ranah, teknik, item, akademi) disertai Pinyin (disahkan §13-5).
- **Durasi**: 1–2 jam per playthrough; 3 playthrough untuk melihat semua cabang.

---

## 7. Catatan Implementasi (Pemetaan Quest ID)

Pemetaan beat cerita ke skema quest (ENGINE_ARCHITECTURE §5.1–§5.2):

| Quest ID | Beat cerita | Objektif | Cabang |
|---|---|---|---|
| `q_akademi_01` | Tiba di gerbang akademi | `talk` Penjaga Gerbang | – |
| `q_akademi_02` | Ujian masuk: tes akar spiritual | `talk` Gu Canghai | – |
| `q_akademi_03` | Ujian masuk: **sparing vs Han Xiu** (battle wajib) | `spar` Han Xiu | – |
| `q_akademi_04` | Pilih 1 dari 3 akademi | `choose` akademi | – |
| `q_akademi_05` | Hari-hari pertama; puncak = ingatan pertama | `talk` Su Qing → `memory_unlock` mem_01 | – |
| `q_akademi_06` (= **q3**) | Insiden Lonceng hilang; Chen Xu melihat Mo Yun membawa benda terbungkus (malam) | `reach` Ruang Lonceng + `time_window` malam; berakhir dialog pilih sikap | **4 cabang** (3aa/3ab/3b/3c) |
| `q_akademi_3aa` | **3aa** — konfrontasi langsung Penatua | `talk` Penatua | mem_02 |
| `q_akademi_3ab` | **3ab** — kumpulkan bukti diam-diam (info Mo Yun) | `talk` Mo Yun | mem_02 |
| `q_akademi_3b` | Ambil keuntungan | `talk` Zhou Yan | mem_03 |
| `q_akademi_3c` | Berdiam diri | `advance_time` (1 hari) | mem_04 |
| `q_akademi_07` (= **q5**) | Kebenaran Penatua + kambing hitam + firasat | `talk` Mo Yun (reaksi beda per cabang) | **menyatu** dari 3aa/3ab/3b/3c |
| `q_side_berburu` | **Berburu binatang liar** di area berburu — **repeatable** (grinding) | `defeat` musuh liar | paralel |
| `q_side_suqing` | **Bantu Su Qing** (belanja ramuan) — **repeatable** | `gather` | paralel |
| `q_side_moyun` | **Tugas perpustakaan Mo Yun** — **repeatable** | `gather` | paralel |

**Side quest (disahkan)**: data terpisah (`quests_side.json`), bisa diulang setelah selesai untuk **grinding ranah** (ENGINE_ARCHITECTURE §6.4/§9), dan dilarang bertabrakan dengan main quest (validator §14-10).

**World-state Arc 2 (G4b/#10, 2026-08-14)** — world-facts resmi tersimpan sebagai `flags` (diset di on_complete cabang, siap ditanyakan konten Arc 2):

| World-fact | 3aa | 3ab | 3b | 3c |
|---|---|---|---|---|
| `zhouyan_status` | `bebas` | `bebas` | `diusir` | `diusir` |
| `elder_exposed` | `true` | `false` | `false` | `false` |
| `academy_knows_truth` | `true` | `false` | `false` | `false` |
| `bell_status` (q07) | `kembali` | `kembali` | `kembali` | `kembali` |

**Catatan teknis (disetujui)**: cabang 3a dipecah menjadi **3aa** (konfrontasi langsung) / **3ab** (kumpulkan bukti diam-diam) lewat **percabangan bertingkat di dalam dialog** pilihan sikap — keduanya **menyatu kembali** di q5 (`q_akademi_07`). Ini membuktikan **percabangan bertingkat** pada konten nyata (DoD GDD §11.2) tanpa menambah beban naratif berarti.
