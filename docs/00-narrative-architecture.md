# TIAN XU: SECOND LIFE — STORY PRODUCTION BIBLE v1.0
## 00. Narrative Architecture

**Status:** DRAFT — Phase 1 of 18
**Source of Truth:** Master Story Bible (MSB), diberikan lengkap tanpa modifikasi terhadap premis, 7 Arc, tema, protagonis, Jiang Yan, Cycle Formation, atau kelima ending.
**Aturan kerja dokumen ini:** setiap klaim naratif yang tidak berasal langsung dari MSB ditandai `[DESIGN GAP]`. Tidak ada gap yang diisi diam-diam. Rekomendasi pengisian gap selalu dipisahkan dari spesifikasi itu sendiri.

---

### 0.1 Model Data Engine

```
DATA → STORY STATE → QUEST/CONTENT AVAILABILITY → PLAYER ACTION
→ CONSEQUENCE → UPDATED STATE → FUTURE CONTENT
```

Setiap content object di seluruh dokumen ini (quest, dialogue, memory, NPC, location, event, ending) harus dapat dipetakan ke model ini tanpa memerlukan logika linear tersembunyi. Tidak ada quest yang "hanya muncul karena quest sebelumnya selesai" — setiap transisi harus melalui state eksplisit yang dapat dibaca/ditulis oleh content lain.

### 0.2 Prinsip Kausalitas Wajib

Struktur yang **dilarang**:
```
Quest A selesai → Quest B muncul → Quest C muncul
```

Struktur yang **wajib**:
```
EVENT → STATE CHANGE → CONSEQUENCE → NEW POSSIBILITY
→ PLAYER CHOICE → BRANCH → CONSEQUENCE → CONVERGENCE → FUTURE PAYOFF
```

Implikasi produksi: setiap quest_id di Phase 4 (Quest Graph) harus mencantumkan state yang ia *baca* (prerequisite) dan state yang ia *tulis* (world_state_changes), bukan sekadar quest_id pendahulunya. ID quest pendahulu boleh dicatat untuk referensi manusia, tapi bukan mekanisme gating.

### 0.3 Naming Convention (mengikuti Section 19 MSB-prompt)

| Content Type | Pola | Contoh |
|---|---|---|
| Arc | `arc_XX` | `arc_01` |
| Chapter | `chapter_XX_YY` | `chapter_01_02` |
| Main Quest | `quest_aXX_cYY_NNN` | `quest_a02_c01_003` |
| Branch | `branch_aXX_cYY_bNN` | `branch_a02_c01_b02` |
| Character Quest | `charquest_[name]_NNN` | `charquest_linyue_001` |
| Faction Quest | `factionquest_[faction]_NNN` | `factionquest_reformists_001` |
| Memory | `memory_aXX_mNN` | `memory_a03_m01` |
| Dialogue | `dialog_aXX_dNNN` | `dialog_a02_d014` |
| NPC | `npc_[name]` | `npc_lin_yue` |
| Location | `loc_[area]_[detail]` | `loc_tianxu_main_hall` |
| World Event | `event_aXX_[slug]` | `event_a05_spiritual_collapse` |
| Faction | `faction_[slug]` | `faction_tianxu_orthodox` |
| Ending | `ending_[slug]` | `ending_unbroken_heaven` |
| Convergence | `convergence_aXX_cYY_NN` | `convergence_a02_c03_01` |
| State/Flag | `state_[category]_[slug]` | `state_rep_tianxu` |

ID tidak pernah berbasis urutan file. Setelah ID diberikan pada draft pertama, ID tersebut permanen sepanjang dokumen ini — perubahan ID di kemudian hari harus dicatat sebagai breaking change di changelog (belum ada; akan dibuat saat revisi pertama diperlukan).

### 0.4 Pemisahan Data / State / Logic

Dokumen ini **tidak** berisi:
- Kode Python atau pseudocode
- Schema JSON final
- Implementasi engine

Dokumen ini **berisi**:
- Definisi content (quest, NPC, dialogue, dll) sebagai spesifikasi terstruktur
- Definisi state (flag, relationship value, faction value) sebagai katalog dengan tipe dan pemilik baca/tulis
- Hubungan antar keduanya, dinyatakan secara deklaratif (bukan prosedural)

Contoh yang **benar** (deklaratif):
> `quest_a02_c01_003` memerlukan `state_rep_tianxu >= 20` DAN `flag_archive_suspicious == false`. Jika sukses, menulis `flag_archive_suspicious = true`.

Contoh yang **salah** (prosedural, dilarang di dokumen ini):
> `if player.reputation.tianxu >= 20 and not player.flags.archive_suspicious: unlock_quest(...)`

### 0.5 Eskalasi Sosial Protagonis (dari MSB §4)

```
Murid baru
→ Cultivator pemula
→ Anggota kelompok (Found Family)
→ Penyelidik
→ Pihak yang terlibat dalam konflik Tian Xu
→ Orang yang mengetahui rahasia dunia
→ Orang yang harus menentukan masa depan cultivation
```

Tujuh Arc dipetakan satu-ke-satu terhadap tujuh tahap eskalasi ini (lihat 0.7). Ini bukan pemetaan arbitrer — ini pemetaan yang **sudah tersirat** di MSB dan menjadi kontrak pacing untuk Phase 3 (Chapter Breakdown): setiap Arc harus membuka Chapter pertamanya di level eskalasi yang sesuai, bukan melompat.

### 0.6 Tujuh Tema Arc dan Enam Tema Pendukung

Tema Arc (MSB, tidak boleh diubah):

| Arc | Judul | Tema |
|---|---|---|
| I | A New Life | Belonging |
| II | The First Trial | Trust |
| III | Echoes of Another Self | Identity |
| IV | The False History | Truth |
| V | The World That Remembers | Consequence |
| VI | The Last Cycle | Forgiveness |
| VII | Second Life | Choice |

Tema pendukung (MSB §3), dipetakan ke Arc tempat tema tersebut paling dominan **secara analitis** — MSB tidak menyatakan pemetaan eksplisit Arc↔tema-pendukung, sehingga pemetaan ini ditandai:

`[DESIGN GAP — tema pendukung tidak dipetakan eksplisit ke Arc di MSB]`

Rekomendasi pengisian (lihat 0.6.1) diberikan terpisah dari klaim canon.

**0.6.1 Rekomendasi (bukan canon):**

| Tema Pendukung | Arc Paling Relevan | Alasan |
|---|---|---|
| Identity | III (utama), VI, VII | Tema utama Arc III secara eksplisit |
| Choice | II, VII (utama) | Tema utama Arc VII secara eksplisit |
| Trust | II (utama), V, VI | Tema utama Arc II secara eksplisit |
| Legacy | IV, VI | Forbidden Archive dan Jiang Yan's truth |
| Power | IV, V | Origin of Cultivation, Spiritual Collapse |
| Sacrifice | VI, VII | Final Choice, Ending Path IV |

Ini adalah rekomendasi penekanan, bukan eksklusivitas — semua tema pendukung dapat muncul di Arc mana pun secara sekunder.

### 0.7 Struktur Master: 7 Arc ke Content Hierarchy

```
ARC (7)
 └─ CHAPTER (jumlah mengikuti kebutuhan pacing — lihat Phase 3)
     └─ QUEST GROUP
         ├─ MAIN QUEST (quest graph, causal chain)
         │   └─ BRANCH → CONSEQUENCE → STATE → CONVERGENCE
         ├─ CHARACTER QUEST (9 karakter, agency independen)
         ├─ FACTION QUEST (5 faksi termasuk Entity sebagai 5th force)
         ├─ INVESTIGATION QUEST (mystery-driven)
         ├─ MEMORY QUEST (fragment → interpretation → contradiction → revelation)
         └─ SIDE/OPTIONAL QUEST (world-building, tidak filler)
     └─ DIALOGUE (state-conditional, multi-versi)
     └─ NPC (6 kategori: Main/Supporting/Recurring/Quest/Faction/Ambient)
     └─ LOCATION (fungsi naratif/gameplay wajib)
     └─ WORLD EVENT (state-triggered, mengubah state dunia)
 └─ CONSEQUENCE (immediate → short → mid → long → ending)
 └─ CONVERGENCE POINT (branch bertemu, state tidak terhapus)
 └─ ENDING CONDITION (5 ending: 4 utama + 1 hidden)
```

### 0.8 Sembilan Karakter Inti dan Agency Requirement

Dari MSB, sembilan karakter dengan questline wajib:

1. **Lin Yue** — sahabat terdekat, emotional anchor (MSB §5, §37)
2. **Shen Luo** — rival → possible successor/enemy (MSB §5, §37)
3. **Mei Ruo** — pintu masuk mystery, historian (MSB §5, §37)
4. **Gu Han** — skeptis institusi, representasi konsekuensi sosial (MSB §5, §37)
5. **Mentor** — hubungan tersembunyi dengan Jiang Yan (MSB §38)
6. **Grandmaster** — antagonist institusional, bukan villain sederhana (MSB §19, §39)
7. **Mo Chen** — stranger yang mengenali Jiang Yan (MSB §13)
8. **Jiang Yan / Past Self** — protagonis kehidupan pertama (MSB §26-31)
9. **Entity** — 5th force, bukan villain sederhana (MSB §24, §34, §41)

**Agency requirement** (dari system prompt, ditegaskan ulang di sini karena berlaku ke semua fase berikutnya): kesembilan karakter ini **tidak boleh menunggu protagonis**. Jika kondisi state tertentu terpenuhi (mis. `state_rep_tianxu` rendah + `world_event_a05_spiritual_collapse` terjadi), karakter dapat mengambil keputusan sendiri yang terjadi *off-screen* relatif terhadap player, lalu muncul sebagai state baru yang player temukan. Ini akan dispesifikasikan per karakter di Phase 5 sebagai `autonomous_trigger_condition`.

### 0.9 Lima Faksi (empat + Entity sebagai 5th force)

1. `faction_tianxu_orthodox` — MSB §41
2. `faction_reformists` — MSB §41
3. `faction_liberation` — MSB §41
4. `faction_hidden_guardians` — MSB §41
5. Entity — bukan faction konvensional (tidak punya "anggota" atau "wilayah"), tapi punya ideologi, hidden position, dan possible outcomes seperti faction lain. Diperlakukan sebagai faction ke-5 secara struktural di Phase 6.

**Prinsip wajib:** tidak ada faction yang sepenuhnya good/evil (instruksi eksplisit). Grandmaster (Orthodox) mempertahankan sistem karena takut, bukan haus kekuasaan (MSB §19, §39). Entity punya sudut pandang valid ("manusialah yang menyerang lebih dahulu", MSB §34) sekaligus tidak innocent (telah membalas dengan menghancurkan manusia).

### 0.10 Empat Belas Mystery Question (Wajib Payoff, Tidak Boleh Muncul di Final Arc)

Dari instruksi Phase 15, dipetakan ke jawaban yang **sudah eksplisit** di MSB:

| # | Mystery Question | Jawaban (MSB source) |
|---|---|---|
| 1 | Siapa protagonis? | Jiang Yan, murid Tian Xu kehidupan pertama (§26) |
| 2 | Siapa Jiang Yan? | Murid biasa, bukan chosen one, membangun found family serupa (§26) |
| 3 | Mengapa memory kembali? | Cycle Formation, eksperimen kehidupan kedua (§29-30) |
| 4 | Mengapa Tian Xu menyembunyikan sejarah? | Mencegah panik/exploitation, dan menyembunyikan kegagalan pendiri (§17) |
| 5 | Apa yang ada di bawah Tian Xu? | Formation raksasa yang menyerap energi seluruh akademi (§20) |
| 6 | Apa asal-usul cultivation? | Sumber spiritual purba yang melahirkan entitas saat digunakan (§18) |
| 7 | Apa itu Entity? | Kelahiran dari sumber cultivation, bukan villain sederhana (§18, §34) |
| 8 | Apa yang terjadi di kehidupan pertama? | Jiang Yan membuka gerbang, eksperimen gagal, Cycle Formation tercipta (§29) |
| 9 | Apa itu Cycle Formation? | Formation yang mengulang kondisi dunia untuk melahirkan Second Life (§29) |
| 10 | Mengapa sejarah berulang? | Cycle Formation tidak sempurna, mengulang event tertentu (§22, §29) |
| 11 | Apa yang sebenarnya dilakukan Jiang Yan? | Mencoba memisahkan entitas dari sumber, bukan membebaskan (§29) |
| 12 | Apa arti sebenarnya Second Life? | Kesempatan eksperimental, bukan hadiah/takdir (§30) |

**Catatan:** MSB menyediakan jawaban *final* untuk semua 12 pertanyaan ini, tapi **tidak** menyediakan struktur hint-bertahap (First Hint → Second Hint → False Interpretation → Contradiction) secara eksplisit untuk tiap pertanyaan. Struktur bertahap ini akan dirancang di Phase 14 (Mystery/Reveal Matrix) sebagai turunan dari fondasi MSB, dan bagian yang murni desain baru (bukan langsung dari MSB) akan ditandai `[DESIGN GAP]` di level granular saat itu.

### 0.11 Kondisi yang TIDAK Boleh Berubah (Restated dari Critical Constraint)

Daftar berikut adalah restatement literal dari batasan wajib — dicantumkan di sini sebagai referensi cepat untuk semua fase berikutnya, bukan sebagai bagian baru dari spesifikasi:

- Premis (MSB §1)
- Tujuh Arc dan judulnya
- Tema masing-masing Arc
- Second Life premise (MSB §30, §36)
- Identitas protagonis (murid biasa → Jiang Yan)
- Sifat memory: fragmented, distorted, dapat menyesatkan (MSB §11)
- Tian Xu sebagai academy + guardian institution + prison (tersirat kuat di §18-20, eksplisit sebagai "Tian Xu bukan hanya menjaga segel. Tian Xu memberi makan segel.")
- Entity sebagai primordial (§18, §34)
- Origin cultivation (§18)
- Jiang Yan sebagai identitas protagonis kehidupan pertama (§26-30)
- Cycle Formation (§29)
- Struktur antagonisme hybrid (Grandmaster bukan villain murni, Entity bukan villain murni)
- Lima ending (empat utama + hidden resolution)
- Hidden resolution sebagai ending kelima yang butuh kombinasi kondisi (§36)
- Main story spine (Arrival → ... → Final Decision)
- Model branching (choice → consequence → convergence yang mempertahankan state)
- Prinsip reactive world (state-driven content availability)

---

### 0.12 Ringkasan Status Fase Ini

**READY:** struktur naming convention, model data engine, pemetaan tema-Arc utama, sembilan karakter dan lima faksi teridentifikasi, 12 mystery question dengan jawaban final tersedia dari MSB.

**DESIGN GAP terbuka di fase ini:**
1. Pemetaan tema pendukung → Arc (rekomendasi diberikan di 0.6.1, belum canon)
2. Struktur hint-bertahap untuk 12 mystery question (akan dirancang Phase 14)
3. Jumlah Chapter per Arc (akan ditentukan Phase 3 berdasarkan kebutuhan pacing, bukan angka arbitrer)

Dokumen berikutnya (`01-arc-overview.md`) membangun ARC OVERVIEW lengkap untuk ketujuh Arc mengikuti template Phase 1 dari prompt asli.
