# GDD — Tian Xu: Second Life

> **Judul**: Tian Xu: Second Life  
> **Genre**: RPG Kultivasi Xianxia (multi-genre: drama tragis, reinkarnasi, politik, RPG progression)  
> **Platform**: Web (UI) — Python (engine) — JSON (struktur bercabang) + CSV (data tabular/balancing)  
> **Versi GDD**: 2.1  
> **Status**: Final — dasar rancangan (detail teknis di ENGINE_ARCHITECTURE.md)  
> **Pembaruan 2.1**: seluruh asumsi §13 telah disahkan (nama desa, opsi pahlawan, ending, durasi, bahasa, bentuk UI Tianyuan Ling).

---

## 1. Visi & Premis

### 1.1 Premis Inti

**Long Tianxu** (龙天序) adalah pangeran kekaisaran yang meridiannya rusak sejak lahir — diracuni oleh selir ayahnya. Ia diasingkan dan kehilangan tahta. Namun seorang **dewa tersesat** menyembuhkannya, dan Tianxu belajar dari para ahli tersembunyi hingga menjadi **pelindung dunia**.

Ia dikhianati secara kolektif oleh banyak pihak — termasuk mantan kekasihnya dan murid kesayangannya — melalui konvergensi kepentingan. Ia kehilangan istri dan anaknya (dibunuh), kekuatannya direnggut, dan mati dalam kesendirian.

Satu-satunya yang tersisa: **Tianyuan Ling** (天缘灵) — item pemberian dewa atas kebaikan tulus masa mudanya, yang ia simpan hingga kematian. Item itu menyala, dan Long Tianxu terlahir kembali sebagai **Chen Xu** (陈旭) — merasuk ke tubuh bayi kultivator biasa.

### 1.2 Tema

- **Perjalanan hidup yang tragis** — kejatuhan, pengkhianatan kolektif, kematian dalam kesendirian.
- **Kebaikan yang membuahkan keajaiban** — Tianyuan Ling adalah buah dari kebaikan tulus masa muda.
- **Balas dendam terhadap sistem yang korup** — musuh sejati bukan individu, tapi seluruh struktur dunia kultivasi.
- **Tokoh utama adalah antagonis** — premis menegaskan tokoh utama *merupakan* tokoh antagonis yang awalnya baik: di kehidupan pertama kejatuhan ke kegelapan adalah **alur tetap** (pemain menentukan cara & kecepatannya, bukan apakah terjadi); di kehidupan kedua pemain bebas menentukan arah moralnya.
- **Siapa yang bisa dipercaya** — tema besar bukan "balas dendam ke satu musuh", tapi berapa harga dari percaya.

### 1.3 Referensi

| Aspek | Referensi | Elemen yang diadopsi |
|---|---|---|
| Dunia kultivasi | *Against the Gods* (novel) | Struktur kekuatan, sekte, ranah kultivasi, nuansa tragedi |
| Figur tokoh | Yun Che | Kejatuhan → kebangkitan dengan ingatan penuh |
| Sistem game-like | *The Reincarnation of the Strongest Sword God* | Shi Feng — "Sistem" sebagai plot device yang disadari tokoh, pertumbuhan kekuatan terarah |
| Arsitektur/data | Chronicle of the Past (proyek sebelumnya) | Pola data-driven, quest, event, dialog bercabang |
| Simulasi hidup | 4thfever/cultivation-world-simulator (GitHub) | **Pinjam konsep fitur saja**: akar spiritual, sekte, pil, event dunia — bukan arsitektur |

---

## 2. Tokoh Utama — Dua Identitas

| | Kehidupan Pertama | Kehidupan Kedua |
|---|---|---|
| **Nama** | Long Tianxu (龙天序) | Chen Xu (陈旭) |
| **Status** | Pangeran kekaisaran → pelindung dunia | Bayi kultivator biasa yang dirasukinya |
| **Nasib** | Diracun sejak lahir (meridian rusak), diasingkan, disembuhkan dewa, jadi pelindung → dikhianati kolektif, istri & anak dibunuh, mati sendiri | Terlahir kembali dengan ingatan penuh kehidupan pertama |
| **Makna nama** | 天序 "Tatanan/Urutan Langit" — ironis: yang harus menjaga tatanan justru dihancurkan | 陈旭 "Fajar/matahari terbit" — awal baru dari nol, kontras dengan Tatanan Langit yang runtuh |

### 2.1 Tianyuan Ling (天缘灵) — Item/Sistem

- **Bentuk**: item misterius pemberian dewa — hadiah atas kebaikan tulus masa muda Long Tianxu kepada orang asing.
- **Sifat**: item/Sistem yang **disadari penuh** oleh tokoh utama sebagai *plot device* (gaya Yun Che/Shi Feng) — bukan sekadar artefak pasif.
- **Fungsi**: bertahan hingga kematian Tianxu → menjadi pemicu reinkarnasi → di kehidupan kedua, Chen Xu berinteraksi dengannya sebagai Sistem.
- **Asal-usul**: 缘 (yuan) = "ikatan takdir/karma dari perbuatan baik" — sangat sesuai karena item ini didapat dari kebaikan tulus.
- **Catatan desain**: Sistem berjalan **terpisah dari progresi ingatan** — ingatan murni naratif, kekuatan didapat lewat jalur kultivasi konvensional.
- **Bentuk UI (disahkan)**: panel UI terpisah di web (bisa dibuka/ditutup) + log teks notifikasi — detail teknis skema & interaksi dijabarkan di ENGINE_ARCHITECTURE.md.

---

## 3. Struktur Naratif

### 3.1 Titik Mulai Game

- Game **dimulai saat Chen Xu masuk akademi** (bukan dari bayi, bukan prolog kehidupan pertama).
- Ingatan kehidupan pertama (Long Tianxu) didapat **berangsur-angsur lewat penyelesaian quest**.
- **Arc 1 = arc pengumpulan ingatan** — pemain (dan Chen Xu) baru tahu detail pengkhianatan secara bertahap, sama seperti tokohnya.
- Ingatan bersifat **naratif murni** — tidak membuka skill/power secara mekanik (pemisahan sehat: reveal cerita tidak jadi bottleneck kekuatan, dan grinding power tidak jadi bottleneck cerita).
- **Sikap Chen Xu berubah bertahap** seiring ingatan yang pulih — ingatan membuka opsi dialog tertentu (gating ingatan), tetap **tanpa kekuatan mekanik** (detail: docs/STORY_FASE1.md §3.1).

### 3.2 Rahasia Identitas

- Identitas Chen Xu = reinkarnasi Long Tianxu adalah **rahasia mutlak** — tidak ada pihak (termasuk dewa penyembuh) yang tahu sejak awal.
- Chen Xu benar-benar sendirian membangun ulang dari nol.

### 3.3 Motivasi & Akhir Cerita

- **Motivasi akhir**: balas dendam terhadap **sistem dunia yang korup** — skala seluruh dunia kultivasi (benua), bukan individu.
- Tidak ada "big bad" klasik — musuh sejati adalah struktur kekuasaan, sekte, dan kekaisaran yang memungkinkan pengkhianatan terjadi.
- **Tidak ada jalur mencari keluarga** — istri & anak sudah mati, tidak bisa diselamatkan.
- Hierarki musuh berjenjang (bukan satu battle final).

### 3.4 Aturan Moralitas

- **Hidup pertama**: tragis dan terarah — kejatuhan **terjadi** (premis: tokoh utama *adalah* antagonis), pemain hanya menentukan cara & kecepatan.
- **Hidup kedua**: bebas — pemain menentukan arah moral: pembalasan, pengampunan, kehancuran penuh, atau **menjadi pahlawan** *(disahkan — semua arah moral terbuka, tidak ada yang dianggap "salah")*.
- Skala moralitas (baik → jahat) disimpan dan dipakai untuk membuka/menutup pilihan dialog & ending.

---

## 4. Sistem Quest Utama (DAG — Bercabang, Tanpa Tabrakan)

### 4.1 Prinsip Inti

> **Selesaikan satu quest baru muncul satu quest baru.**

Quest utama adalah **graf terarah (DAG — Directed Acyclic Graph)**, bukan pohon murni: cabang boleh **menyatu kembali** di titik tertentu. Skema data tidak berasumsi 1 parent = 1 child — `next_quest` bisa berbeda per-cabang tapi konvergen ke ID yang sama.

### 4.2 Pemicu Percabangan

- Percabangan dipicu oleh **pilihan dialog eksplisit** (choice nodes) — pemain memilih opsi A/B/C saat ngobrol dengan NPC.
- Bukan kondisi tersembunyi (reputasi/item) — transparan untuk pemain, lebih sederhana diimplementasikan.

### 4.3 Model Percabangan

```
quest1 → quest2 → quest3 ─┬─ 3a ─┐
                          ├─ 3b ─┬─ 3ba ─┤
                          │      └─ 3bb ─┤
                          └─ 3c ─────────┘
                                    ↓
                                 quest5 (menyatu kembali)
```

- Setiap quest memiliki **tepat satu quest penerus aktif** pada satu waktu.
- Percabangan terjadi saat quest sebelumnya selesai — pemain **memilih satu jalur**.
- Jalur yang tidak dipilih **tidak hilang**: menjadi konten yang bisa diakses di playthrough berikutnya (replayability).
- Percabangan bisa bertingkat (3b → 3ba/3bb) dan **boleh menyatu** kembali ke quest yang sama.

### 4.4 Aturan Desain Quest

1. **Satu aktif**: sistem memaksa hanya 1 quest utama aktif.
2. **Urutan ketat**: quest N+1 hanya muncul setelah quest N selesai.
3. **Tidak bertabrakan**: tidak ada dua quest yang menuntut lokasi/NPC/objek yang sama secara bersamaan.
4. **Konsekuensi nyata**: pilihan di quest percabangan memengaruhi kondisi dunia (reputasi faksi, hubungan NPC, status moral, ending).
5. **Checkpoint jelas**: setiap quest punya objektif eksplisit (bicara, kalahkan, kumpulkan, pilih).
6. **Quest sampingan** (non-utama) boleh aktif bersamaan — hanya quest utama yang satu-aktif.

### 4.5 Peta Quest Utama (kerangka — detail konten di fase pengembangan)

| Arc | Fokus | Catatan |
|---|---|---|
| **Arc Akademi (Fase 1)** | Chen Xu masuk akademi, pengenalan dunia, **Arc 1 = pengumpulan ingatan** | Bukti-konsep engine — struktur cabang utuh |
| Arc Sekte | Naik ke level sekte, konflik lebih luas | Ditambahkan di fase lanjutan |
| Arc Kekaisaran | Menyentuh struktur kekaisaran tempat Long Tianxu lahir | Ditambahkan di fase lanjutan |
| Arc Final | Balas dendam terhadap sistem korup, skala benua | Ditambahkan di fase lanjutan |

> **Catatan engine**: engine harus mampu beradaptasi dengan data story yang ditambahkan nanti — skema quest mendukung DAG, arc baru, dan mekanik yang belum terpikirkan sekarang.

---

## 5. Sistem Akademi

### 5.1 3 Akademi (Fase 1)

Pemain **memilih 1 dari 3 akademi di dalam cerita**, setelah quest pengenalan awal. **Pilihan tidak mempengaruhi story** — hanya membuka pool skill.

| Akademi | Hanzi | Pinyin | Makna Harfiah | Fokus Skill |
|---|---|---|---|---|
| Paviliun Elemen | 五行阁 | Wǔxíng Gé | "Paviliun Lima Elemen" | Penguasaan 5 elemen (logam-kayu-air-api-tanah) |
| Paviliun Senjata | 兵锋院 | Bīngfēng Yuàn | "Institut Mata Pedang Prajurit" | Senjata & teknik bela diri |
| Paviliun Summoning | 御灵宗 | Yùlíng Zōng | "Mazhab Pengendali Roh" | Roh/binatang roh & pemanggilan |

*Akhiran sengaja divariasikan (阁/院/宗) agar ketiganya terasa institusi berbeda gaya, tapi tetap satu dunia koheren.*

### 5.2 Posisi dalam Struktur Game

- Pemilihan akademi **bukan node di DAG quest utama** — ia lapisan setup/konfigurasi awal yang menentukan pool skill, **sejajar dengan DAG cerita** tapi tidak berpotongan secara naratif.
- **Akses skill terkunci** ke paviliun pilihan selama Arc Akademi (skill paviliun lain terbuka di arc berikutnya / lewat cara lain).

---

## 6. Dunia & Lokasi

### 6.1 Tipe Lokasi (awal)

- **Desa asal — Yunxi Cun (云溪村, "Desa Sungai Awan")** *(disahkan)* — titik awal, pengenalan, kebaikan tulus.
- **Kota akademi** — pusat belajar, toko, quest sampingan.
- **Wilayah kultivasi** — area berburu, musuh liar, material.
- **Wilayah misterius** — terkait Tianyuan Ling & lore dunia (dibuka bertahap).
- **Reruntuhan/rahasia** — konten opsional untuk pemain yang menggali.

---

## 7. Sistem Kultivasi (Dalam — Simulasi Hidup)

Mengikuti kedalaman simulasi (konsep fitur dari 4thfever/cultivation-world-simulator + pola Chronicle of the Past):

- **Ranah kultivasi** — tingkatan kekuatan berjenjang, **9 ranah** *(disahkan)*: Pengumpul Qi (炼气) → Pembangun Fondasi (筑基) → Pembentuk Inti (金丹) → Jiwa Baru Lahir (元婴) → Transformasi Roh (化神) → Pemurni Kehampaan (炼虚) → Penyatu (合体) → Mahayana (大乘) → Penantang Surga (渡劫); **tiap ranah dibagi 10 tingkat** *(disahkan)*.
- **Progresi berbasis aktivitas** *(disahkan)* — pemain mengumpulkan qi/exp lewat **berkultivasi (grounding)**, **berburu monster**, dan **menang sparing**; rajin beraktivitas = makin cepat naik tingkat; side quest sampingan **bisa diulang** untuk grinding (detail: ENGINE_ARCHITECTURE §9.1).
- **Akar spiritual** — bakat bawaan yang menentukan potensi (konsep dari referensi).
- **Teknik** — skill yang dipelajari & ditingkatkan, dibatasi ranah.
- **Item** — pil, ramuan, material, artefak, senjata, alat.
- **Alkimia** — meracik pil/ramuan dari material (opsional pendukung).
- **Senjata & alat** — perlengkapan yang memengaruhi kekuatan.
- **Kompanion** — rekan / binatang roh (terutama jalur Summoning).
- **Ekonomi** — uang, beli/jual, harga bervariasi per lokasi.
- **Hubungan NPC** — reputasi, persahabatan, permusuhan, mentor.
- **Sekte/faksi** — afiliasi & konsekuensi reputasi.
- **Waktu & siklus hidup** — hari/bulan berjalan; beberapa peristiwa hanya muncul pada waktu tertentu.

---

## 8. Sistem Pertarungan (Giliran Berbasis Menu)

- **Pola**: turn-based — pemain memilih aksi dari menu.
- **Aksi dasar**: Serang, Skill/Teknik, Item, Bertahan, Kabur.
- **Elemen**: 5 elemen saling menguatkan/melemahkan (relevan untuk jalur Elemen).
- **Sumber daya**: HP (darah) + Qi/energi (bahan teknik).
- **Musuh**: liar, pembelot, penjaga, boss naratif.
- **Gagal/KO**: pemain pulih di titik aman — tidak ada game over permanen di jalur utama (fokus cerita).
- **Pertarungan wajib** hanya di quest utama; sisanya opsional.

---

## 9. Ending

- **Penentu ending**: pilihan kunci di quest percabangan + skala moralitas akhir — bukan "kalahkan villain X", tapi pilihan filosofis terhadap sistem.
- **Opsi tematik (disahkan — 3 ending, nama final)**:
  - Membangun ulang sesuatu yang lebih baik (reformer)
  - Membakar habis sistem lama (destroyer)
  - Menerima dan berdamai dengannya (ascetic/pelarian)
- Semua ending **valid secara naratif** — tidak ada ending "salah".

---

## 10. Arsitektur Teknis

| Lapisan | Teknologi | Catatan |
|---|---|---|
| Tampilan | **Web** | UI di browser; v1 = text + panel statistik (bukan grafis penuh) |
| Mesin | **Python** | Logika game, state, quest engine (DAG), battle engine |
| Data | **JSON + CSV** | JSON = struktur bercabang (quest, dialog, event); CSV = data tabular/balancing (item, musuh, konfigurasi) |

### 10.1 Prinsip Data-Driven

- Semua konten (quest, dialog, NPC, item, musuh, event) **data JSON/CSV** — bukan hardcode.
- Engine membaca data — menambah konten baru tidak perlu ubah kode.
- **Engine harus adaptif**: mampu menampung arc & mekanik yang belum terpikirkan sekarang (bukan cuma konten baru dalam skema sama).
- Validasi data: file rusak / referensi salah **ditolak saat startup** (bukan crash misterius di tengah main).

### 10.2 Pembagian Dokumen

| Dokumen | Isi |
|---|---|
| **GDD.md** (ini) | Visi, cerita, desain game |
| **ENGINE_ARCHITECTURE.md** | Detail implementasi teknis untuk OpenCode (skema JSON quest DAG, struktur modul, API) |

### 10.3 Struktur Modul (awal)

```
tian-xu-second-life/
├── docs/            # GDD, ENGINE_ARCHITECTURE, kontrak data, workplan
├── data/            # JSON (quest/dialog/event) + CSV (balancing/item/musuh)
├── src/             # Python: engine, quest engine (DAG), battle, save
├── web/             # UI web
├── tests/           # pengujian otomatis
└── tools/           # validator data, dll.
```

---

## 11. Skala Fase 1 — Arc Akademi (Bukti Konsep)

**Tujuan Fase 1**: membuktikan konsep engine — quest DAG bercabang-bercabang-menyatu, dialog eksplisit, satu sistem gameplay konkret.

### 11.1 Cakupan Fase 1

- **Durasi target**: 1–2 jam per playthrough *(disahkan)*.
- **Arc Akademi saja** — dari Chen Xu masuk akademi hingga selesainya arc pengumpulan ingatan awal.
- **Pemilihan akademi**: 3 akademi (Elemen/Senjata/Summoning), dipilih di dalam cerita, memengaruhi pool skill saja.
- **Sistem yang hidup di Fase 1**:
  - Quest utama DAG (satu-aktif-satu-waktu, cabang boleh menyatu) ✓
  - Pilihan dialog eksplisit sebagai pemicu cabang ✓
  - Kultivasi dasar (ranah + teknik awal per akademi) ✓
  - Pertarungan giliran dasar (1-2 area berburu) ✓
  - Item & inventori dasar ✓
  - Dialog bercabang (beberapa NPC kunci) ✓
  - Simulasi hidup ringan (waktu, 1 kota, beberapa NPC) ✓
  - Ekonomi sederhana (uang + 1 toko: jual material, beli Pil Qi) ✓ *(disahkan)*
  - Alkimia dasar (racik 1–2 pil dari material) ✓ *(disahkan)*
  - Senjata dasar (1–2 senjata penambah serangan) ✓ *(disahkan)*
  - Akar spiritual mekanik ringan (bakat memengaruhi kecepatan exp) ✓ *(disahkan)*
  - Penalti KO ringan (kehilangan sebagian kecil exp) ✓ *(disahkan)*
  - Event terjadwal (beberapa momen hanya muncul di waktu tertentu) ✓ *(disahkan)*
  - Kompanion dasar (jalur Summoning: binatang roh ikut bertarung otomatis) ✓ *(disahkan)*
  - Mini-boss opsional (1 di area berburu, reward besar) ✓ *(disahkan)*
  - Simpan game hanya di titik aman ✓ *(disahkan)*
- **Sengaja ditunda**: kehidupan kedua penuh, arc di luar akademi, alkimia penuh, ekonomi penuh (pasar & harga per lokasi), visual grafis.

### 11.2 Kriteria Selesai Fase 1 (DoD)

- [ ] Pemain bisa menyelesaikan Arc Akademi dengan 3 jalur akademi (3 playthrough minimal).
- [ ] Quest utama tidak pernah tumpang tindih (satu-aktif) — diverifikasi otomatis oleh test.
- [ ] Skema quest mendukung DAG: cabang menyatu kembali diverifikasi oleh test.
- [ ] Data quest/items/NPC 100% data-driven; validator lolos.
- [ ] Satu pertarungan giliran nyata melawan musuh dari data.
- [ ] Panel statistik menampilkan HP/Qi/ranah/inventori.

---

## 12. Roadmap (indikatif)

| Tahap | Isi |
|---|---|
| **Fase 1 (bukti konsep)** | Arc Akademi: quest DAG, dialog eksplisit, 3 akademi, pertarungan giliran, kultivasi dasar |
| **Fase 2** | Arc Sekte + Arc Kekaisaran, kehidupan kedua penuh, ending tematik |
| **Fase 3** | Arc Final (balas dendam skala benua), simulasi hidup penuh (ekonomi, alkimia, hubungan mendalam), konten volume penuh |

---

## 13. Asumsi yang Telah Disahkan

| # | Asumsi | Keputusan |
|---|---|---|
| 1 | Nama & lokasi desa asal | **Yunxi Cun (云溪村, "Desa Sungai Awan")** — §6.1 |
| 2 | Opsi "menjadi pahlawan" di hidup kedua | **Ya** — semua arah moral terbuka bagi pemain — §3.4 |
| 3 | Nama & jumlah ending | **3 ending tematik**: Reformer, Destroyer, Ascetic — §9 |
| 4 | Estimasi durasi main Fase 1 | **1–2 jam** per playthrough |
| 5 | Bahasa | **Bahasa Indonesia**; istilah teknis (ranah, teknik, item) disertai Pinyin |
| 6 | Detail sistem Tianyuan Ling | **Panel UI + log teks** (bisa dibuka/ditutup); detail di ENGINE_ARCHITECTURE.md |
