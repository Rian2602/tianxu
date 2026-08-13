# Ringkasan Desain — Fase 1 (untuk Review)

> **Tujuan dokumen**: merangkum SEMUA keputusan yang sudah disahkan lewat wawancara, dalam satu halaman bahasa sederhana — agar Anda bisa review cepat sebelum pembangunan dimulai.
> **Dokumen resmi (detail teknis)**: `GDD.md` · `STORY_FASE1.md` · `ENGINE_ARCHITECTURE.md`

---

## 1. Cerita — Arc Akademi (3 babak)

**Act 1 — Ujian & Adaptasi** *(hangat, tone terang)*
Chen Xu dari **Yunxi Cun** tiba di **Changfeng Cheng (长风城)**. Ujian masuk: tes akar spiritual + **sparing vs Han Xiu**. Kenalan: mentor **Gu Canghai**, rival **Han Xiu**, sahabat **Su Qing**, pustakawan misterius **Mo Yun**. Pilih 1 dari 3 akademi (Elemen 五行阁 / Senjata 兵锋院 / Summoning 御灵宗). Puncak: ingatan pertama **"Istana yang Sunyi"** terbuka — Tianyuan Ling menyala.

**Act 2 — Insiden**
Pusaka **Lonceng Angin Panjang** hilang. Murid pendiam **Zhou Yan** dituduh. Chen Xu **melihat Mo Yun** membawa benda terbungkus dari ruang lonceng malam itu — bukti Zhou Yan tak bersalah (hanya muncul **malam hari**).

**Act 3 — Tiga Sikap** *(menggerakkan moralitas)*
| Cabang | Sikap | Akibat |
|---|---|---|
| **3aa** | Konfrontasi langsung dengan Penatua | Zhou Yan bebas · moralitas naik · Han Xiu mulai menghormati |
| **3ab** | Kumpulkan bukti diam-diam (via Mo Yun) | Zhou Yan bebas · lebih aman |
| **3b** | Ambil keuntungan | Zhou Yan **diusir** · moralitas turun · Su Qing kecewa |
| **3c** | Berdiam diri | Zhou Yan **diusir** · moralitas netral · Su Qing kecewa |

**Penutup (q5 — semua jalur menyatu)**
Kebenaran: Lonceng diambil **Penatua** untuk keperluan rahasia; Zhou Yan kambing hitam. Mo Yun diam karena **hutang budi** pada Penatua. Chen Xu melihat pola lama: *yang lemah dikorbankan untuk yang kuat* — firasat halus tema besar. (Konfrontasi langsung Penatua hanya di 3aa.)

**Tokoh**: Chen Xu (sikap berubah seiring ingatan pulih: polos → gelisah → dewasa) · Gu Canghai · Han Xiu · Su Qing (benih romansa halus) · Mo Yun · Zhou Yan · Penatua (usulan nama: **An**) · kenangan cinta masa lalu (lewat ingatan saja).

**Ingatan (4)**: Istana yang Sunyi · Kebaikan yang Terlupakan (3a) · Racun di Balik Senyum (3b) · Pengasingan (3c). *Murni naratif — tidak memberi kekuatan.*

---

## 2. Alur Quest Utama

```
q1 (gerbang) → q2 (ujian + sparing + pilih akademi) → q3 (insiden)
   → [ 3aa / 3ab ]  → q5 (kebenaran)
   →   3b           → q5
   →   3c           → q5
```
Satu quest utama aktif; percabangan lewat pilihan dialog; cabang yang tak dipilih jadi konten replay. **Side quest (3, bisa diulang)**: berburu binatang liar · bantu Su Qing · tugas perpustakaan Mo Yun — data terpisah, tidak bertabrakan dengan main quest.

---

## 3. Fitur Game

| Fitur | Keputusan |
|---|---|
| Kultivasi | **9 ranah × 10 tingkat**; progresi via **aktivitas** (grounding/berburu/sparing) |
| Battle | Giliran menu: Serang / Teknik / Item / Bertahan / Kabur |
| Toko | 1 pedagang: jual material, beli Pil Qi + material + 1 senjata |
| Alkimia | 2 resep (Pil Qi, Pil Pemulihan) dari material buruan |
| Senjata | Slot senjata (+attack) — reward quest / beli |
| Akar spiritual | Tier bakat × kecepatan exp (usulan Chen Xu = 中品) |
| Kompanion | Jalur Summoning: 1 binatang roh, ikut battle otomatis |
| Mini-boss | 1 di area berburu (opsional, reward besar) |
| Waktu | Event terjadwal (bukti malam) · respawn monster 5 jam · grounding maks 8 jam/hari |
| Save | Hanya di titik aman · menu utama Mulai Baru / Lanjut |
| Tianyuan Ling | Panel (Status Misi / Ingatan / Log Sistem) — suara jarang, misterius, pasif |

---

## 4. Mekanik Inti

- **Damage**: `serangan × 100/(100+pertahanan)`, min 1, variasi ±10–20% · **kritikal** 8% ×1.5
- **Elemen 五行**: 克制 1.5× / 被克 0.67× (logam→kayu→tanah→air→api→logam)
- **Giliran**: tetap pemain → musuh · **Regen Qi** 5%/giliran
- **KO**: respawn titik aman + hilang 10% exp (sparing juga)
- **Exp**: kurva `10 × 1.2^(tingkat-1)` · level 10 → breakthrough otomatis
- **HP/Qi**: `dasar + (tingkat−1) × per_level` (Pengumpul Qi lvl 5 = HP 100, Qi 52)
- **Target**: pemain rajin mencapai **Pengumpul Qi tingkat 5–6** di akhir arc

---

## 5. Visual (Web, v1 = teks)

- Layout **3 kolom**: cerita tengah · statistik kiri · inventori/quest kanan
- **Teks polos** (tanpa emoji) · HP/Qi **angka saja** · **statis** (tanpa animasi)
- Lokasi: nama + deskripsi + tombol daftar tujuan (tanpa mini-peta)
- **Desktop dulu** (HP ditunda)
- Tema: **gelap + emas**, font serif untuk narasi
- Bahasa: **Bahasa Indonesia** + istilah teknis ber-Pinyin (mis. 五行阁 Wǔxíng Gé)

---

## 6. Yang MASIH BISA Diubah (usulan, bukan keputusan final)

| Item | Status sekarang | Bisa diganti saat review konten |
|---|---|---|
| Nama Penatua | "An (安长老)" | Ya |
| Nama Zhou Yan (korban) | "Zhou Yan (周炎)" | Ya |
| Akar spiritual Chen Xu | 中品 (Akar Menengah) | Ya (atas/bawah) |
| Angka balancing | exp, harga toko, stat musuh | Ya |
| Detail dialog & teks ingatan | sudah ditulis (`data/dialogs`, `data/memories.json`) | Ya |

---

## 7. Konfirmasi

Jika semua di atas sudah benar → **kita mulai membangun** (data → engine → UI).
Jika ada yang kurang/kurang pas → **tunjukkan bagiannya**, saya perbaiki dulu.
