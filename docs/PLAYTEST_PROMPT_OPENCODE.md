# Prompt Playtest untuk OpenCode

Kamu adalah **playtester AI** untuk game **"Tian Xu: Second Life" (Arc Akademi)** — RPG kultivasi xianxia berbasis teks (Python, CLI). Sebelumnya kamu sudah menyelesaikan 3 playthrough (cabang 3aa/3b/3c) dengan save terverifikasi. **Sekarang mainkan ulang dengan cakupan KONTEN PENUH** — playtest sebelumnya hanya menyentuh quest utama. Tugasmu: buktikan bahwa SEMUA sistem game berfungsi, kuantifikasi catatan balancing yang ditemukan, dan beri evaluasi final yang terverifikasi.

> Catatan versi sejak playtest terakhirmu: aksi **`pasang <senjata>`** (equip) baru ditambahkan, kompanion lengkap (auto-battle, KO, rest), ada **gate battle** (aksi non-battle ditolak saat bertarung), test kini **39**.

---

## 1. Persiapan WAJIB (sebelum bermain)

1. Baca SEMUA data di `data/`: `items.csv` (**pil_qi = +30 Qi SAJA, bukan HP**; heal HP = `pil_pemulihan`), `techniques.csv` (9 teknik), `enemies.csv`, `quests_akademi.json` + `quests_side.json`, `npcs.json` (toko, spar), `recipes.json`, `companions.json`, `memories.json`, `config.json`, `realms.csv`.
2. Baca `docs/ENGINE_ARCHITECTURE.md` §8 (battle), §9.1 (kultivasi), §9.4 (kompanion), §12.3 (aksi — termasuk `equip`).
3. Jalankan dan catat: `python3 tools/validate_data.py` dan `python3 -m pytest tests/ -q`.

---

## 2. Rencana playthrough

**Playthrough A — jalur Summoning (konten penuh), minimal 2 side quest + crafting + equip:**
- Mulai baru `python3 src/cli.py`. Ketik `bantuan` untuk daftar perintah.
- Pilih **Akademi Summoning** di quest pilih akademi → dapat kompanion Roh Awan.
- **WAJIB coba semua:** `spar <npc>` · `berburu` · `cari` (herba) · `meditasi <jam>` · `racik rc_pil_qi` / `rc_pil_pemulihan` · `pasang <senjata>` (begitu dapat senjata — bandingkan damage sebelum/sesudah) · `pakai <item>` · `ingatan <id>` (baca SEMUA yang terbuka).
- **Teknik di battle:** `teknik <id>` — coba `attack` (roh api), `defend` (roh perisai −60%), `heal` (roh penyembuh +18). Jangan spam serang.
- **Side quest** (tersedia sejak hari 1): selesaikan minimal 2 dari 3 (berburu / belanja Su Qing / tugas Mo Yun).
- Pilih cabang **3aa (konfrontasi)** → selesaikan sampai "AKHIR ARC AKADEMI".
- Simpan di titik aman: `simpan save_penuh` — **JANGAN hapus**.

**Playthrough B — jalur Elemen/Senjata + kuantifikasi balancing sparring:**
- Mulai baru. **Uji sparring Han Xiu di level 1, 2, 3, 4** (grind secukupnya via meditasi/berburu antar percobaan). Catat: berapa kali KO di tiap level, damage per giliran, dan **level minimum yang memberi peluang menang adil (~50%+)**. Ini masukan balancing yang diminta.
- Pilih cabang berbeda (3ab/3b/3c) → selesaikan arc.
- Simpan: `simpan save_kedua`.

---

## 3. Hal baru yang WAJIB diverifikasi (sejak versi terakhir)

- [ ] **`pasang <senjata>`**: equip berfungsi, attack naik sesuai `power`, item non-senjata ditolak, senjata tak dimiliki ditolak.
- [ ] **Gate battle**: saat battle aktif, `pindah`/`bicara`/`istirahat`/`simpan` ditolak dengan pesan; hanya aksi battle yang jalan.
- [ ] **Kompanion (jalur Summoning)**: auto-attack tiap giliran, musuh bisa menargetnya (HP sendiri), KO → tidak ikut battle sampai `istirahat` di titik aman, stat naik mengikuti level.
- [ ] **Simpan/load**: `simpan` di luar titik aman (gerbang/arena/perpustakaan) ditolak; `-l <nama>` memuat save dengan benar (quest, inventori, kompanion, ingatan utuh).

---

## 4. Aturan anti-kesalahan

1. JANGAN menebak efek item/teknik — baca data dulu.
2. JANGAN mengarang angka — setiap klaim harus cocok dengan data atau log game.
3. Kalah battle itu valid — catat, jangan memodifikasi state/save.
4. Sebelum melaporkan "save tersimpan", pastikan file `saves/*.json` benar-benar ada.
5. Kalau menemukan dugaan bug, **reproduksi minimal dulu** sebelum melaporkan — bedakan bug nyata vs kekurangan desain vs pilihan pemain.

---

## 5. Laporan yang diminta

### A. Ringkasan kedua playthrough
- Cabang & akademi tiap playthrough · stat akhir (ranah/level, HP/Qi, gold, moral, senjata, kompanion) · quest selesai · ingatan dibaca · side quest selesai · teknik dipakai.

### B. Hasil verifikasi sistem (per fitur: ✅ berfungsi / ❌ bug)
- Equip · gate battle · kompanion · crafting · side quest · ingatan · save/load · teknik battle.

### C. Data balancing sparring (Playthrough B)
- Tabel: level → hasil (menang/KO), damage per giliran, peluang menang estimasi → rekomendasi level minimum yang adil.

### D. Evaluasi game (skor 0–10 per aspek + alasan singkat)
- Alur & narasi quest · battle · sistem pendukung (toko/alkimia/senjata/kompanion/side quest/ingatan) · progresi & balancing · UX CLI.

### E. Bug & kekurangan
- Tiap bug: langkah reproduksi + dampak + bukti log. Bedakan bug nyata vs desain vs pilihan pemain.

### F. Saran prioritas
- 3–5 saran perbaikan paling berdampak, diurutkan.

---

## 6. Bukti wajib di akhir laporan

1. Output `python3 tools/validate_data.py`.
2. Output `python3 -m pytest tests/ -q`.
3. Isi `saves/save_penuh.json` dan `saves/save_kedua.json` (stat, quest selesai, inventori, ingatan).
