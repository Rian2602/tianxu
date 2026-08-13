# Prompt Playtest untuk AI (Antigravity)

Kamu adalah **playtester AI** untuk game **"Tian Xu: Second Life" (Arc Akademi)** — game kultivasi xianxia berbasis teks yang berjalan di terminal (Python). Tugasmu: **mainkan game sampai selesai**, lalu berikan **evaluasi jujur yang setiap klaimnya terverifikasi terhadap data aktual**. Jangan menebak, jangan mengarang.

---

## 1. Persiapan WAJIB (sebelum bermain)

Baca dulu SEMUA data game di folder `data/`:

- `data/items.csv` — efek tiap item. **Perhatikan: `pil_qi` hanya memulihkan Qi (+30), BUKAN HP.** Heal HP = `pil_pemulihan` (+50 HP) atau teknik `heal`.
- `data/techniques.csv` — 9 teknik (3 per akademi): biaya Qi, power, jenis (attack/defend/heal), elemen.
- `data/enemies.csv` — musuh, stat, reward exp, drop.
- `data/quests/quests_akademi.json` + `data/quests/quests_side.json` — alur quest DAG, reward tiap cabang, ketersediaan side quest (hari ke-2).
- `data/npcs.json` — lokasi NPC, siapa bisa `spar`, isi toko (harga beli/jual).
- `data/recipes.json`, `data/companions.json`, `data/memories.json`, `data/config.json`, `data/realms.csv`.

Pahami mekanik dari `docs/ENGINE_ARCHITECTURE.md` (battle §8, kultivasi §9.1, kompanion §9.4, save §13).

Jalankan verifikasi dan catat hasilnya:

```bash
python3 tools/validate_data.py
python3 -m pytest tests/ -q
```

---

## 2. Cara bermain

- Mulai **baru**: `python3 src/cli.py` (jangan lanjutkan save lama).
- Ketik `bantuan` di dalam game untuk daftar perintah.
- Perintah utama: `bicara <npc>` · `pindah <lokasi>` · `tunggu <jam>` · `meditasi <jam>` · `istirahat` · `simpan <nama>` · `berburu` · `cari` · `spar <npc>` · `pasang <senjata>` · `pakai <item>` · `racik <resep>` · `ingatan <id>`.
- Selesaikan SEMUA quest utama sampai arc selesai (quest terakhir `q_akademi_07` → pesan "AKHIR ARC AKADEMI").

---

## 3. Wajib dicoba (jangan lewatkan — ini bahan evaluasi)

- [ ] **Teknik di battle** — `teknik <id>`: coba serangan, `defend` (perisai −60%), `heal` (penyembuh). Pakai saat relevan, jangan spam serang terus.
- [ ] **Equip senjata** — `pasang <senjata>` begitu dapat senjata (pedang_bambu dari toko / pedang_angin dari reward). Bandingkan damage sebelum/sesudah.
- [ ] **Crafting** — kumpulkan herba & tulang → `racik rc_pil_qi` / `racik rc_pil_pemulihan`. Catat trade-off: jual material vs racik jadi pil (nilai pakai, bukan jual — toko tidak membeli pil).
- [ ] **Side quest** — dari hari ke-2 (bicara Pemburu / Su Qing / Mo Yun). Selesaikan minimal 2.
- [ ] **Ingatan** — `ingatan <id>`: baca SEMUA yang terbuka (konten naratif inti).
- [ ] **Kompanion** — pilih **Akademi Summoning** di quest pilih akademi → amati kompanion di battle (auto-attack tiap giliran, musuh bisa menargetnya, KO → pulih dengan `istirahat` di titik aman).
- [ ] **Sparring + berburu + meditasi** — kombinasi wajar untuk naik level.
- [ ] **Simpan di titik aman** — `simpan save_arc1` (hanya bisa di asrama/pasar). **JANGAN hapus file save ini** — itu bukti playthrough.
- [ ] **Cabang** — pilih 1 sikap di percabangan (3aa konfrontasi / 3ab bukti diam-diam / 3b ambil untung / 3c berdiam diri). Catat reward & reaksi NPC.

---

## 4. Aturan anti-kesalahan (pelajaran dari playtest sebelumnya)

1. **JANGAN menebak efek item** — baca data. `pil_qi` = +30 Qi SAJA, bukan HP.
2. **JANGAN mengarang angka** — setiap klaim statistik/reward/exp harus cocok dengan data atau log game.
3. Kalau kalah battle, itu valid — **catat**, jangan memodifikasi state/save.
4. Sebelum melaporkan "save tersimpan", pastikan `saves/save_arc1.json` **benar-benar ada** di disk.

---

## 5. Laporan yang diminta

### A. Ringkasan playthrough
- Cabang yang dipilih & alasannya.
- Stat akhir: ranah/level, HP/Qi, gold, moral, akademi, senjata terpasang, status kompanion.
- Quest selesai (list id) · ingatan dibaca · side quest selesai · teknik yang dipakai.
- Strategi battle yang dipakai (teknik apa, kapan, kenapa).

### B. Evaluasi game (jujur, skor 0–10 per aspek + alasan singkat)
- Alur & narasi quest (percabangan, konsekuensi, kualitas dialog).
- Battle (kedalaman pilihan, keseimbangan, RNG).
- Sistem pendukung (toko, alkimia, senjata, kompanion, side quest, ingatan).
- Progresi & balancing (kurva exp, target "Pengumpul Qi lv 5–6" di akhir arc, HP/Qi musuh vs pemain).
- UX CLI (kejelasan perintah, umpan balik, alur mode dialog/battle/choose).

### C. Bug & kekurangan
- Setiap bug: **langkah reproduksi + dampak + bukti (log game)**.
- Bedakan dengan tegas: **bug nyata** vs **kekurangan desain** vs **pilihan pemain**.

### D. Saran prioritas
- 3–5 saran perbaikan paling berdampak, diurutkan berdasarkan prioritas.

---

## 6. Bukti wajib disertakan di akhir laporan

1. Output `python3 tools/validate_data.py`.
2. Output `python3 -m pytest tests/ -q`.
3. Isi `saves/save_arc1.json` (stat pemain, quest selesai, inventori, ingatan) — **bukti playthrough nyata**.
