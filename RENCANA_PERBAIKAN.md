# Rencana Perbaikan — Bug/Inkonsistensi Naratif

**Tanggal:** 27 Agustus 2026
**Status:** ✅ Selesai dieksekusi (27 Agustus 2026)

---

## Ringkasan

12 edit across 6 files (9 data edits + 3 test edits), 0 kode baru, 0 file baru.

| Prioritas | Bug | File | Effort | Dampak |
|---|---|---|---|---|
| P1 | B1: Pavilion dialog false promise (5 nodes) | `data/dialogs/arc01.json` | 10 min | Tinggi |
| P2 | B3: Mis-route dialog Lin Yue | `data/dialogs/arc01.json` | 1 min | Sedang |
| P2 | B2: Typo "Perintahlah" | `data/quests/arc02.json` | 1 min | Rendah |
| P3 | B4: Dead flag `world_event_a05_spiritual_collapse` | `data/quests/arc05.json` + test | 2 min | Rendah |
| P3 | B5: Dead flag `world_event_a07_the_last_night` | `data/quests/arc07.json` + test | 2 min | Rendah |
| P3 | B6: Dead reputation `faction_liberation` | `data/dialogs/arc02.json` | 1 min | Rendah |

---

## P1: B1 — Pavilion Dialog False Promise

### Root cause

Dialog proctor (`dlg_proctor_pavilion_explain`) menyuruh pemain "temui gurumu di ruang latihan" untuk teknik khas pavilion. Tapi mekanik sebenarnya adalah tombol "Pelajari" di panel kurikulum (selalu terlihat di sidebar kanan), dan teknik hanya bisa dipelajari saat pemain berada di lokasi pavilion sendiri. Guru NPC (`npc_teacher_*`) hanya flavor text — zero effects, zero quest.

### Data verified

- `quest.py:336-366` — pavilion selection grant: companion + starter_kit + passive. **No technique.**
- `session.py:1064-1127` — `_learn_technique()` action exists, requires location = pavilion
- `app.js:566-569` — Pelajari button shows when `t.status === "available"`
- `app.py:93-122` — curriculum status logic (available/learned/locked)
- Guru dialogs (`dlg_a01_d007-010`) — pure flavor text, zero effects
- Zero quests reference teacher NPCs

### Edits

**File: `data/dialogs/arc01.json`**

| Node | Line | Action |
|---|---|---|
| `wx3` | 479 | Replace "temui gurumu di ruang latihan dan ikuti pelajaran pertama" dengan "Teknik Pelepasan bisa dipelajari di pavilionmu. Pelajari melalui kurikulum saat kau kunjungilah pavilionmu." |
| `jx3` | 507 | Replace "temui gurumu di ruang latihan dan ikuti pelajaran pertama" dengan "Tebasan Pedang Jantung bisa dipelajari di pavilionmu. Pelajari melalui kurikulum saat kau kunjungilah pavilionmu." |
| `yz3` | 535 | Replace "temui gurumu di ruang latihan dan ikuti pelajaran pertama" dengan "Analisa Prinsip bisa dipelajari di pavilionmu. Pelajari melalui kurikulum saat kau kunjungilah pavilionmu." |
| `lg3` | 563 | Replace "temui gurumu di ruang latihan dan ikuti pelajaran pertama" dengan "Teknik Adaptasi bisa dipelajari di pavilionmu. Pelajari melalui kurikulum saat kau kunjungilah pavilionmu." |
| `n2` | 578 | Replace "Pergilah ke sana dan bicara dengan gurumu. Mereka akan mengajarkan teknik dasar pavilion dan memberikan companion yang sesuai dengan jalan kultivasimu." dengan "Teknik dan companion pavilionmu sudah aktif. Teknik khas bisa dipelajari di pavilion melalui kurikulum." |

---

## P2: B3 — Mis-route Dialog Lin Yue

### Root cause

`dlg_a01_d003/n_has_quest` — pemain yang sudah punya quest Lin Yue aktif, memilih "Aku punya waktu" → di-route ke `n1` (generic first-meeting line "Kau murid baru juga?") bukan ke kelanjutan quest.

### Data verified

- `arc01.json:115-130` — `n_has_quest` condition: `quest_active: quest_char_lin_yue_001`
- `arc01.json:121` — choice "Aku punya waktu" routes to `n1`
- `arc01.json:132-134` — `n1` is the generic first-meeting line

### Edit

**File: `data/dialogs/arc01.json`**

| Line | Current | New |
|---|---|---|
| ~121 | `"next": "n1"` | `"next": "n2"` |

**Catatan:** n2 adalah terminal closing line ("Sampai jumpa di pelajaran"). Lebih baik dari n1 (tidak mengulang perkenalan), tapi percakapan langsung tanpa quest content. Fix proper butuh dedicated quest-continuation node — future work.

---

## P2: B2 — Typo "Perintahlah"

### Root cause

Quest `quest_a02_c02_003` (kind: "reach") menggunakan hint "Perintahlah" (memberi perintah) padahal seharusnya "Pergilah" (pergi ke suatu tempat).

### Edit

**File: `data/quests/arc02.json`**

| Line | Current | New |
|---|---|---|
| 83 | "Perintahlah ke wilayah luar untuk tugas rutin." | "Pergilah ke wilayah luar untuk tugas rutin." |

---

## P3: B4 — Dead Flag `world_event_a05_spiritual_collapse`

### Root cause

Flag ditulis oleh `quest_a05_c01_001` saat quest selesai, tapi tidak pernah dibaca oleh quest/dialog/manapun. Ada di 14 dokumen desain sebagai planned consumption yang tidak pernah diimplementasikan.

### Data verified

- SET: `arc05.json:17` — on_complete effect
- READ: 0 locations in data/ atau src/
- Test: `tests/test_arc5_data.py:185` — assertion harus dihapus

### Edits

**File: `data/quests/arc05.json`** — hapus flag effect (baris 15-19)
**File: `tests/test_arc5_data.py`** — hapus assertion (baris 185)

---

## P3: B5 — Dead Flag `world_event_a07_the_last_night`

### Root cause

Flag ditulis oleh `quest_a07_c01_001` saat quest selesai, tapi tidak pernah dibaca oleh quest/dialog/manapun.

### Data verified

- SET: `arc07.json:22` — on_complete effect
- READ: 0 locations in data/ atau src/
- Test: `tests/test_arc7_data.py:70,146` — assertions harus dihapus

### Edits

**File: `data/quests/arc07.json`** — hapus flag effect (baris 20-24)
**File: `tests/test_arc7_data.py`** — hapus assertions (baris 70, 146)

---

## P3: B6 — Dead Reputation `faction_liberation`

### Root cause

Reputasi ditulis sekali di `arc02.json:200` (confront option), tapi tidak pernah dicek oleh `faction_min`/`faction_max` manapun. `faction_reformists` dicek di 3 tempat, `faction_tianxu_orthodox` di 2 tempat, `faction_liberation` di 0 tempat.

### Data verified

- SET: `arc02.json:198-202` — dialog choice effect (part of effects array with orthodox -3, gu_han +3, reformists +1)
- CHECKED: 0 locations
- Faction definition di `factions.json:14` — dipertahankan untuk potensi konten masa depan

### Edit

**File: `data/dialogs/arc02.json`** — hapus reputation effect (baris 198-202)

---

## Verification

```bash
python3 -c "from src.loader import DataRegistry; DataRegistry('data')"
pytest
grep -r "world_event_a05_spiritual_collapse\|world_event_a07_the_last_night\|faction_liberation" data/
```

---

## Temuan yang TIDAK diperbaiki (by design, bukan bug)

| Temuan | Alasan |
|---|---|
| "Gerakan tadi" muncul sebelum aksi fisik | Foreshadowing disengaja — tema ingatan tubuh dari kehidupan sebelumnya |
| Group exam allies bebas lokasi | By design — spar_team pull stats dari NPC registry, bukan lokasi |
| Dialog bisa terpicu dini | By design — NPC bisa diajak bicara kapan saja tanpa quest gate |
| Dialog bisa terulang identik | Minor — butuh quest gate atau condition, effort tidak sebanding |
| 5x duplicated ending menu | Maintenance risk, bukan bug. Refactor candidate untuk nanti |
| No priority untuk multi-condition nodes | First-match-in-JSON-order deterministik dan terdokumentasi |

---

## Temuan yang terbukti FALSE POSITIVE

| Temuan | Alasan |
|---|---|
| 5 write-only flags | Hanya 2 dari 5 (B4, B5). 3 lainnya consumed di dialog/locations |
| Condition keys silently pass | Fail-closed — unknown keys cause `return False` dengan warning log |
| Reputation "faksi" non-standard | Standard convention, 25 uses across 8 files |
| Branches converge without differentiation | All branches punya flags, relations, companion statuses berbeda |
| Gu Han tidak disebut namanya | Semua3 nama ada: "Lin Yue, Shen Luo, Gu Han" |
| Log quest identik 3x | Judul quest berbeda per NPC, log pakai `q['title']` |
| Claude menemukan dialog terminal node bug | Bug sudah diperbaiki di commit `8d590db` sebelum playtest Claude |
| Flowchart Shen Luo gate >=2 | Actual adalah >=1 |
| Orthdox side-arc depends on main-story | Chain self-contained: +2 dari quest 001 = threshold untuk quest 002 |
