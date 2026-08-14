# Ringkasan Desain — Fase 1 (untuk Review)

> **Tujuan dokumen**: merangkum SEMUA keputusan yang sudah disahkan lewat wawancara, dalam satu halaman bahasa sederhana — agar Anda bisa review cepat sebelum pembangunan dimulai.
> **Dokumen resmi (detail teknis)**: `GDD.md` · `STORY_FASE1.md` · `ENGINE_ARCHITECTURE.md`
> **Status**: Fase 1 (Arc Akademi) **SELESAI & tervalidasi** — detail implementasi & status fitur: `ENGINE_ARCHITECTURE.md` §12-§17.
> **Riwayat**: 2026-08-14 — sinkronisasi EP3-T2: catatan penyelesaian kriteria penerimaan Fase 1 (Arc Akademi).

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
q1 (gerbang) → q2 (ujian + sparing + pilih paviliun) → q3 (insiden)
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
| Angka balancing | sudah dikunci lewat rebalancing playtest (v0.1.0-alpha) | Tidak (verifikasi: ENGINE_ARCHITECTURE §9.1) |
| Detail dialog & teks ingatan | sudah ditulis (`data/dialogs`, `data/memories.json`) | Ya |

---

## 8. Status Penyelesaian Fase 1

Seluruh kriteria penerimaan Fase 1 (Arc Akademi) **selesai dan tervalidasi** — lihat `ENGINE_ARCHITECTURE.md` §16 (roadmap implementasi) & §17 (status fitur) untuk detail teknis.

**Fitur yang diverifikasi selesai (SELESAI / Verified):**
- **Toko Web** — modal beli/jual di Pasar Changfeng (dari `context.merchant_shop`).
- **Dinamisasi Resep** — tombol racik dirender dari `context.recipes`.
- **Cooldown Side Quest** — `state.side_quest_cooldowns` + penegakan `quest.py`.
- **Timer Respawn Monster** — berburu ulang dibatasi `world.monster_respawn_hours` (5 jam).
- **Jadwal Harian NPC** — `_is_npc_available` membatasi bicara/spar pada jam aktif NPC.
- **Layar Penutup Arc 1** — `arc_summary` di `view()` + banner CLI + modal web.

**Rebalancing (hasil playtest, disahkan v0.1.0-alpha)**: exp quest diturunkan ~40% & exp aktivitas dikurangi (grounding 2/jam, spar 8, hunt 6) — jalur quest saja ≈ Lv.5, pemain rajin ≈ Lv.6 (target GDD Lv4–6). Detail: ENGINE_ARCHITECTURE §9.1.

**Keadaan teknis saat sinkronisasi (2026-08-14)**: 192 test lolos, coverage `src/` ≈ 99,9%, `tools/validate_data.py` exit 0. **Pembaruan (2026-08-14 lanjutan)**: batch fix audit (G1–G5/H1–H3/K1–K5/G4d/G4e) + batch plan sisa-bug (H4/A1/J3#6/#9/A2) → **209 test**, validator exit 0. Detail: `docs/list_bug.md` §Status perbaikan & plan `docs/superpowers/plans/2026-08-14-fix-sisa-bug-dan-hardening.md`.

**⚜️ FOUNDATION FREEZE (2026-08-15)** — **Gameplay & Narrative Foundation Fase 1 = FROZEN.**

Bukti (semua ter-push ke `origin/main`):
- **Playtest 4 cabang moral** deterministik sampai `q_akademi_07` — world-state akhir diverifikasi per cabang (flags, relations, morality, memories, gold, arc_summary) — `tests/test_playthrough_branches.py`. **338 passed**, validator exit 0.
- **0 hardcode id konten arc-1 di engine** (satu-satunya literal `loc_wilayah_berburu` di `cli.py` dihilangkan G2-T1 plan 2026-08-15).
- **Kontrak transisi arc**: quest akhir arc → quest pertama arc berikutnya via `next` (data); `arc_summary` generik via `final_quest`; checklist §6.5 ENGINE_ARCHITECTURE.
- **Fixture adaptivitas**: arc 2 sintetis dijalankan tanpa ubah kode (`tests/test_adaptivity.py`) — dan berhasil mengungkap 1 bug nyata (main-quest `defeat` mengabaikan `report_to`) yang sudah diperbaiki.
- **Keputusan desain arc 2** (hunt multi-lokasi, gating quest by relation, konvensi id memory per arc) — final menunggu outline cerita.

Arti freeze: **arc berikutnya = konten data saja** (quest/npc/lokasi/dialog/config). Mekanik tambahan (mis. quest failure/deadline) TIDAK dibangun spekulatif — menunggu outline cerita arc 2 (pipeline: outline → identifikasi mekanik → bangun & validasi → isi konten). Lihat plan `docs/superpowers/plans/2026-08-15-gap-fase15-dan-adaptivitas-arc2.md`.

---

## 7. Konfirmasi

Jika semua di atas sudah benar → **kita mulai membangun** (data → engine → UI).
Jika ada yang kurang/kurang pas → **tunjukkan bagiannya**, saya perbaiki dulu.
