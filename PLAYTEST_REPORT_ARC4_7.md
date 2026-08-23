# Playtest Report: Arc IV → VII (Game Complete)

**Tanggal:** 2026-08-24  
**Save起点:** `pt_final_playtest.json` (Arc IV, quest a04_c04_004)  
**Hasil:** Game TAMAT — 44 quests selesai, quest=None

---

## 📊 Ringkasan Eksekusi

| Arc | Quests | Status | Bug |
|-----|--------|--------|-----|
| **IV** (False History) | 1/1 | ✅ Selesai | — |
| **V** (World Remembers) | 5/5 | ✅ Selesai | 1 BUG (stuck loop) |
| **VI** (Last Cycle) | 4/4 | ✅ Selesai | — |
| **VII** (Second Life) | 3/3 | ✅ Selesai | — |
| **TOTAL** | **13/13** | ✅ **GAME TAMAT** | **1 BUG** |

---

## 🐛 Bug Ditemukan

### BUG-1: Quest a05_c05_005 Stuck Loop (HIGH)

**Quest:** `quest_a05_c05_005` — "Apa yang Kucoba Kubunuh"  
**Objective:** `reach` ke `loc_tianxu_deepest_chamber`  
**Masalah:** Quest dimulai saat pemain SUDAH berada di `loc_tianxu_deepest_chamber` (selesai dari a05_c04_004). Method `notify_move()` hanya dipanggil saat pemain BERPINDAH lokasi, sehingga objective tidak pernah selesai.

**Root Cause:** Quest chain `a05_c04_004 → a05_c05_005` keduanya menargetkan lokasi yang SAMA. Saat a05_c04_004 selesai (talk entity di deepest_chamber), a05_c05_005 langsung aktif dengan pemain masih di deepest_chamber.

**Workaround:** Pemain harus pergi keluar dan kembali ke deepest_chamber.

**Rekomendasi Fix:** Di `notify_move()`, tambahkan juga pengecekan saat quest baru dimulai (on quest start), bukan hanya saat pemain berpindah. Atau ubah data quest sehingga a05_c05_005 memiliki lokasi berbeda.

---

## 📈 Statistik Perjalanan

| Metric | Nilai |
|--------|-------|
| Quests completed | 31 → 44 (+13) |
| Arc IV quests | 1 (reach deepest chamber) |
| Arc V quests | 5 (talk elder, talk guard, talk lin_yue, talk entity, reach deepest) |
| Arc VI quests | 4 (reach records, talk mentor, reach deepest, talk mentor) |
| Arc VII quests | 3 (talk lin_yue, talk imprint, talk imprint — ending) |
| Total gold earned | 80 → 135 (+55) |
| HP throughout | 45/45 (tidak berubah — TANPA BATTLE) |
| Qi throughout | 30/30 (tidak berubah) |
| Day/Hour | 3/6 (tidak berubah — TANPA TIME ADVANCEMENT) |
| Status effects | cultivation_deviation (selalu aktif, tidak pernah expired) |

---

## ⚠️ Observasi Penting

### 1. TANPA BATTLE di Arcs IV-VII
Seluruh Arc IV-VII TIDAK ADA pertarungan. HP dan Qi tetap 45/45 dan 30/30. Ini mungkin desain (narrative-heavy arcs), tapi menurunkan engagement.

### 2. Waktu TIDAK Maju
Day/hour tetap 3/6 dari Arc IV sampai Arc VII selesai. Tidak ada fatigue, tidak ada time cost. Ini berarti:
- Fatigue system tidak aktif
- Meditation/rest system tidak terpakai
- Tidak ada urgency mechanic

### 3. cultivation_deviation Tidak Pernah Expired
Status effect `cultivation_deviation` dengan `days_left: 2` tetap ada selama 13 quests tanpa berkurang. Karena waktu tidak maju, duration tidak pernah tick down.

### 4. Ending Hanya Satu Jalur
Quest a07_c03_003 (final) hanya talk + complete. Tidak ada `choose` mechanic untuk menentukan ending (5 endings di docs). Semua pemain mendapat ending yang sama.

### 5. Connection Gates Bekerja dengan Baik
- `loc_forbidden_archive → loc_tianxu_deepest_chamber`: membutuhkan `flag_stakes_of_stopping_source_known` ✅
- `loc_archive_public → loc_forbidden_archive`: membutuhkan `flag_version_iii_read` ✅  
- `loc_tianxu_gate → loc_tianxu_main_hall`: membutuhkan `state_final_principle` (BLOCKED — tidak tercapai di jalur ini)

### 6. NPC Locations Konsisten
NPC berada di lokasi yang benar sesuai jadwal/quest progression:
- `npc_villager_elder` di `loc_affected_village` ✅
- `npc_mountain_guard` di `loc_mountain_gate` ✅
- `npc_lin_yue` di `loc_training_hall` ✅
- `npc_entity` di `loc_tianxu_deepest_chamber` ✅
- `npc_mentor` di `loc_mentor_ground` ✅
- `npc_jiang_yan_imprint` di `loc_below_deepest` ✅

---

## 🔧 Bug dari Playtest Sebelumnya (Arc I-III)

| # | Bug | Severity | Status |
|---|-----|----------|--------|
| 1 | Mini boss tidak count ke quest objective | MEDIUM | Belum diperbaiki |
| 2 | Realm requirement blocks spar | HIGH | Belum diperbaiki |
| 3 | Quest completion timing | LOW | Belum diperbaiki |

---

## 📋 Total Bug Playtest Arc I-VII

| # | Bug | Severity | Arc |
|---|-----|----------|-----|
| 1 | Mini boss kill tidak hit objective | MEDIUM | Arc I |
| 2 | Realm requirement blocks spar dialog | HIGH | Arc II |
| 3 | Quest completion timing issue | LOW | Arc II |
| 4 | quest_a05_c05_005 stuck (already at target) | HIGH | Arc V |
| 5 | No ending branching (5 endings not realized) | MEDIUM | Arc VII |
| 6 | Time never advances (fatigue/rest useless) | MEDIUM | IV-VII |
| 7 | cultivation_deviation never expires | LOW | IV-VII |

---

## ✅ Sistem Terverifikasi

| System | Status | Catatan |
|--------|--------|---------|
| Quest progression | ✅ | 44 quests, chain works correctly |
| Dialog system | ✅ | Dialog triggers correctly |
| Connection gates | ✅ | Gates block correctly |
| NPC location/schedules | ✅ | NPCs at correct locations |
| Navigation/pathfinding | ✅ | BFS works (with gate awareness) |
| Save/load | ✅ | pt_final_playtest loads correctly |
| Battle system | ✅ | Tested in Arc I-II (not used in IV-VII) |
| Gold economy | ✅ | Gold earned correctly from quests |
| Memory system | ✅ | Memory unlock working |
| Faction system | ✅ | Flags set correctly |
