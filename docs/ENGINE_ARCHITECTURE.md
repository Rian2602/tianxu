# ENGINE_ARCHITECTURE — Tian Xu: Second Life

> **Status**: Kontrak teknis (draft kerja) — acuan implementasi engine & data
> **Merujuk**: GDD.md versi 2.1 (keputusan §13 telah disahkan)
> **Fase 1**: Arc Akademi — bukti konsep (quest DAG, dialog eksplisit, 3 akademi, pertarungan giliran, kultivasi dasar, panel Tianyuan Ling)

---

## 1. Tujuan Dokumen

Dokumen ini adalah **kontrak teknis** antara GDD dan kode. Ia menjabarkan:

1. Skema data (JSON quest DAG, dialog, NPC, CSV balancing) — **kontrak data**.
2. Struktur modul Python — **arsitektur engine**.
3. API engine & API web — **antarmuka** yang dipakai UI.
4. Aturan validasi data — **pengaman startup**.
5. Desain panel Tianyuan Ling — **fitur UI kunci Fase 1**.

Aturan emas: **setiap perubahan skema data wajib disertai pembaruan dokumen ini + validator data** (`tools/`). Skema adalah kontrak — konten tidak boleh menyimpang dari skema tanpa validasi menolaknya.

---

## 2. Prinsip Arsitektur (dari GDD §10.1)

| # | Prinsip | Konsekuensi teknis |
|---|---|---|
| 1 | **Data-driven total** | Semua konten (quest, dialog, NPC, item, musuh, event, ingatan) ada di `data/` sebagai JSON/CSV. Engine tidak boleh berisi hardcode konten. |
| 2 | **Engine adaptif** | Arc, akademi, ranah, mekanik baru = data. Engine membaca *daftar* dari data, tidak mengasumsikan jumlah/jenis tertentu. |
| 3 | **Validasi saat startup** | File rusak / referensi salah / DAG melingkar **ditolak sebelum game jalan** — bukan crash misterius di tengah main. |
| 4 | **Pemisahan ingatan vs kekuatan** | Ingatan (memories) = **naratif murni**, tidak membuka skill/power. Power didapat lewat kultivasi konvensional. Engine memisahkan kedua jalur ini secara eksplisit. |
| 5 | **Engine murni, UI tipis** | `src/engine/` = logika murni (stdlib Python, tanpa dependensi web). `web/` = lapisan tipis (server + render). |
| 6 | **Satu quest utama aktif** | Invariant yang dijaga engine & diverifikasi test: quest utama satu-aktif-satu-waktu. Quest sampingan boleh aktif bersamaan. |

---

## 3. Gambaran Arsitektur

```
┌──────────────┐  HTTP/JSON   ┌──────────────────┐  memakai   ┌─────────────────────┐
│  Web UI      │◄────────────►│  web/app.py      │◄──────────►│  src/engine/*       │
│  (browser)   │              │  (Flask + API)   │            │  (logika murni)     │
└──────────────┘              └──────────────────┘            └──────────┬──────────┘
                                                                         │ membaca
                                                                         ▼
                                                              ┌─────────────────────┐
                                                              │  data/ (JSON + CSV) │
                                                              └─────────────────────┘
```

- **Browser** menampilkan teks + panel statistik + panel Tianyuan Ling.
- Setiap aksi pemain = 1 request JSON ke API → engine memproses → UI menerima state baru → render ulang.
- Engine **tanpa state global**: setiap sesi game adalah objek `GameSession` mandiri (mendukung banyak sesi/multiplaythrough).

---

## 4. Struktur Direktori (Fase 1)

```
tian-xu-second-life/
├── docs/
│   ├── GDD.md                  # (final: dipindah dari root ke sini)
│   ├── ENGINE_ARCHITECTURE.md  # ← dokumen ini
│   └── DATA_CONTRACTS.md       # (opsional: contoh data lengkap, dihasilkan saat konten)
├── data/                       # SEMUA konten game
│   ├── quests/
│   │   ├── quests_akademi.json # quest utama DAG Arc Akademi
│   │   └── quests_side.json    # quest sampingan (boleh paralel)
│   ├── dialogs/
│   │   ├── dialogs_akademi.json
│   │   └── dialogs_side.json
│   ├── npcs.json
│   ├── locations.json
│   ├── memories.json           # ingatan naratif (Tianyuan Ling)
│   ├── items.csv               # item & balancing
│   ├── enemies.csv             # musuh & balancing
│   ├── realms.csv              # ranah kultivasi
│   ├── techniques.csv          # teknik per akademi
│   └── config.json             # state awal, akademi, pengaturan waktu
├── src/
│   ├── engine/                 # logika game murni (stdlib only)
│   │   ├── __init__.py
│   │   ├── session.py          # GameSession: orkestrasi state+aksi
│   │   ├── state.py            # dataclass GameState / PlayerState / SaveData
│   │   ├── quest.py            # QuestEngine (DAG)
│   │   ├── dialog.py           # DialogEngine
│   │   ├── battle.py           # BattleEngine (giliran menu)
│   │   ├── cultivation.py      # ranah, teknik, akar spiritual
│   │   ├── items.py            # inventori, pemakaian item
│   │   ├── npc.py              # NPC, hubungan, reputasi faksi
│   │   ├── world.py            # lokasi, waktu, event terjadwal
│   │   ├── morality.py         # skala moralitas (baik→jahat)
│   │   ├── memory.py           # ingatan naratif (Tianyuan Ling)
│   │   ├── save.py             # serialisasi save/load (JSON)
│   │   └── events.py           # log peristiwa / notifikasi Sistem
│   ├── loader.py               # baca JSON/CSV → objek bertipe
│   ├── validator.py            # validasi startup (dipakai tools & engine)
│   └── cli.py                  # CLI debug/main tanpa web (opsional)
├── web/
│   ├── app.py                  # Flask: serve static + API JSON
│   └── static/
│       ├── index.html
│       ├── app.js              # render state → DOM, kirim aksi
│       └── style.css           # tema xianxia + panel Tianyuan Ling
├── tests/                      # pytest
│   ├── test_quest_dag.py       # invariant DAG, satu-aktif, konvergensi
│   ├── test_dialog.py
│   ├── test_battle.py
│   ├── test_validator.py
│   └── test_save.py
├── tools/
│   ├── validate_data.py        # CLI: jalankan validasi penuh pada data/
│   └── check_quest_dag.py      # CLI: visualisasi/analisis DAG utk penulis konten
└── saves/                      # file save JSON (runtime, gitignored)
```

**Konvensi kode**:
- Python **3.10+**, `dataclasses`, **stdlib only** di `src/engine/`.
- Satu-satunya dependensi eksternal: **Flask** (lapisan `web/`). Pengujian: **pytest** (dev-only).
- ID global unik (quest, dialog, NPC, item, musuh, lokasi, teknik, ingatan) — dipakai untuk semua referensi.
- Tidak ada akses file langsung dari engine selain lewat loader/validator.

---

## 5. Kontrak Data

### 5.1 Quest Utama — JSON DAG

Struktur graf: **Directed Acyclic Graph**. Setiap quest punya daftar `next` (sisi keluar). Sisi yang >1 pada satu quest = **titik percabangan**; beberapa quest yang menunjuk quest yang sama = **titik konvergensi** (menyatu).

```json
{
  "quests": [
    {
      "id": "q_akademi_01",
      "title": "Pintu Gerbang Akademi",
      "arc": "akademi",
      "kind": "main",
      "summary": "Chen Xu tiba di gerbang akademi dan bertemu penjaga.",
      "objective": {
        "kind": "talk",
        "npc": "npc_penjaga",
        "target": 1,
        "hint": "Bicaralah dengan Penjaga Gerbang."
      },
      "next": [
        { "quest": "q_akademi_02", "branch": "b1", "label": "Lanjut" }
      ],
      "on_complete": {
        "effects": [ { "type": "flag", "key": "met_penjaga", "value": true } ],
        "memory_unlock": "mem_01",
        "system_msg": "Ingatan baru terbuka: 'Istana yang Sunyi'.",
        "rewards": { "exp": 10 }
      }
    }
  ]
}
```

**Percabangan — contoh (sesuai diagram GDD §4.3)**:

```json
{
  "id": "q3",
  "next": [
    { "quest": "q3a",  "branch": "b_3a",  "choice_id": "dlg_3_pilih_jalur", "option": "opt_3a", "label": "Jalur A" },
    { "quest": "q3b",  "branch": "b_3b",  "choice_id": "dlg_3_pilih_jalur", "option": "opt_3b", "label": "Jalur B" },
    { "quest": "q3c",  "branch": "b_3c",  "choice_id": "dlg_3_pilih_jalur", "option": "opt_3c", "label": "Jalur C" }
  ]
}
```

- Saat `q3` selesai dan `next` berisi >1 sisi → engine **memaksa** menampilkan dialog `choice_id`; opsi yang dipilih menentukan quest penerus (`option` di dialog ↔ `option` di `next`).
- `next` berisi tepat 1 sisi → lanjut otomatis (tanpa dialog pilih).
- **Konvergensi**: `q3a`, `q3ba`, `q3bb`, `q3c` semuanya bisa menunjuk `q5`. Aman karena hanya satu jalur yang aktif pada satu waktu (satu-aktif invariant).

**Skema lengkap field quest**:

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `id` | string | ✓ | Unik global |
| `title` | string | ✓ | Judul quest |
| `arc` | string | ✓ | Nama arc (bebas, data-driven: `akademi`, `sekte`, …) |
| `kind` | `main` / `side` | ✓ | Utama (satu-aktif) / sampingan |
| `summary` | string | – | Ringkasan 1-2 kalimat (untuk log/UI) |
| `objective` | object | ✓ | Lihat tabel objektif di bawah |
| `next` | array | ✓ | Sisi keluar DAG (boleh kosong = quest terakhir arc) |
| `on_complete` | object | – | `effects`, `memory_unlock`, `system_msg`, `rewards` |
| `requires` | object | – | Prasyarat: `flags`, `morality_min/max`, `realm_min` |
| `available_from` | object | – | Waktu tersedia (hari/jam) — untuk quest sampingan |

**Jenis objektif** (`objective.kind`):

| `kind` | Data tambahan | Perilaku |
|---|---|---|
| `talk` | `npc` | Buka dialog NPC; selesai saat dialog berakhir (atau setelah `target` kali) |
| `defeat` | `enemies` (list id), `target` | Kalahkan N musuh (dari data) |
| `gather` | `item`, `target` | Kumpulkan N item |
| `reach` | `location` | Tiba di lokasi |
| `choose` | `options` (list) | Pilihan eksplisit (mis. pilih akademi, pilih jalur) |
| `advance_time` | `day`/`hour` | Tunggu hingga waktu tertentu |

**Aturan sisi `next`**:

| Field | Tipe | Keterangan |
|---|---|---|
| `quest` | string | ID quest penerus (wajib ada) |
| `branch` | string | ID unik cabang (untuk tracking replayability) |
| `choice_id` | string | Dialog pilih jalur (wajib jika quest ini punya >1 sisi) |
| `option` | string | Opsi dalam dialog yang memilih cabang ini |
| `label` | string | Label cabang (untuk UI "jalur yang tidak dipilih") |

### 5.2 Dialog — Choice Nodes Eksplisit

Percabangan quest **hanya** dipicu pilihan dialog eksplisit (GDD §4.2) — tidak ada kondisi tersembunyi.

```json
{
  "dialogs": [
    {
      "id": "dlg_3_pilih_jalur",
      "npc": "npc_mentor",
      "start": "node_pilih",
      "nodes": {
        "node_pilih": {
          "speaker": "npc_mentor",
          "text": "Tiga jalan terbuka di hadapanmu, murid baru.",
          "choices": [
            { "label": "Jalur A — kekuatan langsung.", "option": "opt_3a",
              "effects": { "morality": -1 }, "next": "node_a" },
            { "label": "Jalur B — jalan panjang.", "option": "opt_3b",
              "effects": { "reputation": { "akademi_elemen": 2 } }, "next": "node_b" },
            { "label": "Jalur C — menunggu waktu.", "option": "opt_3c", "next": "node_c" }
          ]
        },
        "node_a": { "speaker": "npc_mentor", "text": "Baiklah. Pergilah.", "end": true }
      }
    }
  ]
}
```

**Skema node dialog**:

| Field | Tipe | Keterangan |
|---|---|---|
| `speaker` | string | `npc:<id>` atau `player` atau `system` (Tianyuan Ling) |
| `text` | string | Teks yang ditampilkan |
| `choices` | array | Opsi pemain; tiap opsi: `label`, opsional `option`, `effects`, `condition`, `next` |
| `condition` | object | Syarat tampil: `flags`, `morality_min/max`, `has_item`, `realm_min` |
| `next` | string | Node berikutnya |
| `end` | bool | Akhiri dialog |
| `effects` | object | Diterapkan saat opsi dipilih (lihat tabel efek) |

**Jenis efek** (`effects`):

| Efek | Contoh | Keterangan |
|---|---|---|
| `morality` | `{ "morality": -5 }` | Ubah skala moralitas (baik→jahat) |
| `reputation` | `{ "reputation": { "faksi_x": 2 } }` | Ubah reputasi faksi/NPC |
| `relation` | `{ "relation": { "npc_mentor": 5 } }` | Ubah hubungan NPC |
| `flag` | `{ "flag": { "key": "bantu_petani", "value": true } }` | Set flag dunia |
| `item` | `{ "item": { "id": "pil_qi", "count": 2 } }` | Beri/kurang item (count negatif = kurangi) |
| `branch_select` | `{ "branch_select": "opt_3a" }` | (internal) pilih cabang quest — diisi otomatis oleh engine |

### 5.3 NPC

```json
{
  "npcs": [
    {
      "id": "npc_penjaga",
      "name": "Penjaga Gerbang",
      "location": "loc_gerbang_akademi",
      "role": "gate_guard",
      "default_dialog": "dlg_penjaga",
      "schedule": [ { "day": 1, "hour_start": 6, "hour_end": 18, "location": "loc_gerbang_akademi" } ]
    }
  ]
}
```

### 5.4 CSV Balancing

**items.csv** — header wajib:

```
id,name,type,description,price,hp_restore,qi_restore,power,rarity,usable
pil_qi,Pil Qi,consumable,Pulihkan 30 Qi.,50,0,30,0,common,true
```

**enemies.csv**:

```
id,name,realm,hp,qi,attack,defense,speed,element,exp_reward,drop_item,drop_chance
eno_serigala_qi,Serigala Qi,pengumpul_qi_1,40,10,8,3,10,tanah,15,pil_qi,0.3
```

**realms.csv**:

```
id,name_pinyin,name_id,order,base_hp,base_qi,technique_slots
realm_pq1,Pengumpul Qi Tahap 1,pengumpul_qi_1,1,80,40,1
```

**techniques.csv**:

```
id,name,academy,element,realm_required,qi_cost,power,kind,description
tek_elemen_bola_api,Bola Api,elemen,api,realm_pq1,8,15,attack,Serangan api dasar.
```

**konvensi**: CSV wajib punya baris header persis sesuai contoh; id unik; referensi (mis. `academy`, `realm_required`, `element`) wajib valid.

### 5.5 Ingatan Naratif (Tianyuan Ling)

```json
{
  "memories": [
    {
      "id": "mem_01",
      "title": "Istana yang Sunyi",
      "unlocked_by_quest": "q_akademi_02",
      "text": "Kulihat kembali bayangan istana tempatku lahir...",
      "type": "narrative"
    }
  ]
}
```

**Aturan kunci**: ingatan **tidak pernah** memberikan power mekanik (GDD §2.1). `memory_unlock` pada quest hanya membuka entri naratif di panel Tianyuan Ling.

### 5.6 config.json — State Awal & Konfigurasi

```json
{
  "game_title": "Tian Xu: Second Life",
  "starting": {
    "location": "loc_gerbang_akademi",
    "player": { "name": "Chen Xu", "hp": 80, "qi": 40, "realm": "realm_pq1" },
    "inventory": [ { "id": "pil_qi", "count": 3 } ],
    "morality": 0,
    "current_quest": "q_akademi_01",
    "flags": { "hari_pertama": true }
  },
  "academies": [
    { "id": "akademi_elemen",   "name": "Akademi Elemen",    "hanzi": "五行阁", "pinyin": "Wǔxíng Gé", "skill_pool": ["tek_elemen_*"] },
    { "id": "akademi_senjata",  "name": "Akademi Senjata",   "hanzi": "兵锋院", "pinyin": "Bīngfēng Yuàn", "skill_pool": ["tek_senjata_*"] },
    { "id": "akademi_summoning","name": "Akademi Summoning", "hanzi": "御灵宗", "pinyin": "Yùlíng Zōng", "skill_pool": ["tek_summoning_*"] }
  ],
  "time": { "day_length_hours": 24, "start_day": 1, "start_hour": 8 },
  "elements_cycle": ["logam", "kayu", "tanah", "air", "api"],
  "element_advantage": { "logam": "kayu", "kayu": "tanah", "tanah": "air", "air": "api", "api": "logam" },
  "morality": { "min": -100, "max": 100 }
}
```

- **Akademi = data**, bukan hardcode: engine membaca `academies` dari config. Pilihan akademi (quest `choose`) hanya membuka `skill_pool` akademi itu (GDD §5.2 — sejajar DAG, tidak berpotongan naratif).
- `element_advantage` = siklus 五行 (克制): logam克kayu, kayu克tanah, tanah克air, air克api, api克logam — dipakai battle engine dengan multiplier.

---

## 6. Quest Engine (DAG)

### 6.1 Invariant (dijaga kode + test)

1. **Satu-aktif**: tepat 0 atau 1 quest utama aktif per sesi; quest utama berikutnya hanya muncul setelah quest utama aktif selesai.
2. **Urutan ketat**: quest N+1 hanya muncul setelah N selesai (tidak ada skip lewat kondisi tersembunyi).
3. **Tidak bertabrakan**: tidak ada dua quest (utama×samping, samping×samping) yang aktif bersamaan menuntut NPC/lokasi/objek yang sama. Diverifikasi validator + test.
4. **Graf adalah DAG**: tidak ada siklus (validasi startup).

### 6.2 Algoritma Transisi

```
selesaikan_quest(q):
    terapkan on_complete(q)          # effects, rewards, memory_unlock, system_msg
    tandai q selesai
    if q.next kosong:                # ujung arc
        main_quest = null            # arc selesai (Fase 1: layar "Akhir Arc" / pratinjau)
        return
    if len(q.next) == 1:
        main_quest = q.next[0].quest # lanjut otomatis
        return
    else:
        tampilkan dialog q.next[i].choice_id   # pemain pilih 1 jalur
        # opsi dialog ber-option ↔ sisi next ber-option; pilihan menentukan:
        main_quest = sisi terpilih.quest
        catat branch terpilih; branch lain → available_branches (replayability)
```

### 6.3 Sesi & Multiplaythrough

- Satu `GameSession` = satu playthrough. `completed_quests`, `choices_made`, `available_branches` disimpan di save.
- **Replayability** (GDD §4.3): branch yang tidak dipilih tetap tercatat sebagai konten yang *belum pernah dipilih* di save itu; playthrough baru bisa memilih jalur lain. UI "Playthrough 2+" bisa menunjukkan cabang yang belum dijelajahi.

### 6.4 Quest Sampingan

- `kind: "side"` — boleh aktif bersamaan dengan quest utama dan side lain (selama aturan "tidak bertabrakan" terpenuhi).
- Selesai side quest → reward + efek, tidak memengaruhi alur utama kecuali efek yang dideklarasikan (reputasi, flag).

---

## 7. Dialog Engine

- Sesi dialog = stateful (`dialog_id` + `current_node`), disimpan di `GameState`.
- `start(dialog_id)` → node `start`. `choose(choice_index)` → terapkan `effects` → pindah `next` / `end`.
- Opsi dengan `condition` yang tidak terpenuhi **disembunyikan** dari UI (GDD §3.4: skala moralitas membuka/menutup pilihan dialog).
- Saat dialog berakhir, engine memeriksa apakah quest aktif `objective.kind == "talk"` dengan NPC itu → selesaikan objektif → jalankan transisi quest (§6.2).
- `option` pada opsi dialog dicocokkan dengan `option` pada sisi `next` quest → **pemilihan cabang** (transparan untuk pemain: label opsi menjelaskan jalurnya).

---

## 8. Battle Engine (Giliran Menu)

### 8.1 Alur

```
battle_start(enemy_ids, context)
  → giliran: player → musuh (bergantian berdasarkan speed)
player_action(menu):
  - serang        : damage dasar (attack - defense musuh), minimal 1
  - teknik        : pilih teknik; cost Qi; multiplier elemen jika jalur elemen
  - item          : gunakan item HP/Qi dari inventori
  - bertahan      : kurangi damage 50% giliran ini
  - kabur         : peluang sukses berdasarkan speed; gagal = giliran musuh
```

### 8.2 Elemen (五行)

- Damage multiplier elemen: serangan elemen X ke musuh elemen Y:
  - `element_advantage[X] == Y` → **1.5×** (克制)
  - `element_advantage[Y] == X` → **0.67×** (被克)
  - selain itu → 1.0×
- Siklus dibaca dari `config.json` (data-driven).

### 8.3 KO & Pemulihan

- Pemain KO → respawn di **titik aman** terakhir (lokasi aman / kota), HP/Qi pulih — **tidak ada game over permanen** di jalur utama (GDD §8).
- Pertarungan **wajib** hanya di quest utama; pertarungan opsional (wilayah berburu) bisa dihindari.

---

## 9. Kultivasi, Item & Simulasi Waktu

- **Ranah**: urutan dari `realms.csv`; naik ranah membutuhkan EXP/event cerita; membuka slot teknik & batas HP/Qi.
- **Teknik**: `techniques.csv`, terkunci ke akademi (`academy`), dibatasi ranah (`realm_required`), biaya Qi (`qi_cost`).
- **Inventori**: map item→count; item consumable (`usable=true`) bisa dipakai di luar/dalam battle.
- **Waktu**: `world.py` memajukan waktu (hari/jam). Quest sampingan & NPC dengan `schedule` hanya tersedia pada waktu tertentu. Fase 1: ringan (1 kota, beberapa NPC, tanpa siklus hidup penuh).

---

## 10. Moralitas & Konsekuensi Dunia

- Skala integer `[-100, +100]`, mulai 0 (netral). Disimpan di `GameState`.
- Diubah lewat `effects.morality` pada pilihan dialog & quest.
- Dipakai untuk: membuka/menutup opsi dialog (`condition.morality_min/max`) dan menentukan ending.
- **Ending (disahkan §13)**: 3 tematik — Reformer / Destroyer / Ascetic — ditentukan kombinasi **pilihan kunci di quest percabangan + skala moralitas akhir**. Semua ending valid secara naratif.

---

## 11. Tianyuan Ling — Panel UI & Log (Desain Disahkan)

> Keputusan §13-6: **panel UI terpisah (bisa dibuka/ditutup) + log teks notifikasi**.

### 11.1 Tampilan

- Tombol toggle di pojok kanan atas UI: **「天缘灵」Tianyuan Ling** — aksen emas menyala (tema misterius, kontras dengan UI biasa).
- Panel terbuka berisi **3 bagian**:

```
┌─ 天缘灵 Tianyuan Ling ────────────────┐
│  [✕]                                  │
│  ── Status Misi ──                     │
│  Quest aktif: Pintu Gerbang Akademi    │
│  Objektif: Bicaralah dengan Penjaga    │
│  (0/1)                                │
│  ── Ingatan (2/6) ──                   │
│  • Istana yang Sunyi        [baca]     │
│  • ...                                 │
│  • ??? (terkunci)                      │
│  ── Log Sistem ──                       │
│  [Sistem] Ingatan baru terbuka: ...    │
│  [Sistem] Quest utama diperbarui: ...  │
└────────────────────────────────────────┘
```

### 11.2 Perilaku

| Bagian | Sumber data | Perilaku |
|---|---|---|
| Status Misi | `GameState.quest` | Quest utama aktif + objektif + progress; quest sampingan (jika ada) di bawahnya |
| Ingatan | `memories.json` + `unlocked_memories` | Entri terbuka = bisa dibaca (naratif); entri terkunci tampil `???` |
| Log Sistem | `events.py` (tipe `system`) | Notifikasi Sistem, ber-timestamp, warna khusus |

- Pesan Sistem juga mengalir ke **log utama** dengan prefiks `[Sistem]` — suara Tianyuan Ling dibedakan secara visual.
- **Pemisahan ketat**: membuka ingatan **tidak** menambah power (GDD §2.1). Panel murni menampilkan status + naratif + notifikasi.
- Interaksi panel = data-driven: `system_msg` pada quest, `memory_unlock`, dst. — tanpa hardcode teks di engine.

---

## 12. Web UI & API

### 12.1 Komunikasi

- `web/app.py` (Flask) menyajikan `web/static/` + endpoint JSON.
- Satu sesi = satu `GameSession` di server (in-memory) + save ke `saves/`.
- UI render ulang penuh dari state (tidak ada state DOM yang kompleks — Fase 1).

### 12.2 Endpoint API

| Method & Path | Body | Balasan |
|---|---|---|
| `GET /api/health` | – | `{"ok": true}` |
| `POST /api/game/new` | – | `{"game_id": "..."}` |
| `POST /api/game/load` | `{"save_name": "..."}` | `{"game_id": "..."}` |
| `POST /api/game/{id}/save` | `{"save_name": "..."}` | `{"ok": true}` |
| `GET /api/game/{id}/state` | – | `StateJSON` (kontrak §12.4) |
| `POST /api/game/{id}/action` | `ActionJSON` (§12.3) | `{"state": StateJSON, "log_delta": [...], "error": null}` |

### 12.3 Aksi (discriminated union pada `type`)

| `type` | Payload | Dipakai |
|---|---|---|
| `talk` | `{"npc": "<id>"}` | Mulai dialog NPC |
| `dialog_choice` | `{"choice_index": 0}` | Pilih opsi dialog |
| `battle_action` | `{"action": "attack"\|"guard"\|"flee"}` atau `{"action": "technique", "technique": "<id>"}` / `{"action": "item", "item": "<id>"}` | Giliran battle |
| `use_item` | `{"item": "<id>"}` | Pakai item di luar battle |
| `move` | `{"to": "<location_id>"}` | Pindah lokasi |
| `advance_time` | `{"hours": 8}` | Majukan waktu (kemungkinan memicu event) |
| `open_tianyuan` / `close_tianyuan` | – | Buka/tutup panel |

### 12.4 Kontrak State (potongan utama `StateJSON`)

```json
{
  "player": { "name": "Chen Xu", "realm": "Pengumpul Qi Tahap 1", "hp": 80, "hp_max": 80,
              "qi": 40, "qi_max": 40, "academy": null, "morality": 0 },
  "location": "loc_gerbang_akademi",
  "time": { "day": 1, "hour": 8 },
  "quest": { "current": "q_akademi_01", "objective_text": "Bicaralah dengan Penjaga Gerbang.",
             "progress": "0/1", "side": [] },
  "inventory": [ { "id": "pil_qi", "name": "Pil Qi", "count": 3 } ],
  "flags": { "hari_pertama": true },
  "log": [ { "type": "narration|npc|system|battle", "text": "...", "day": 1, "hour": 8 } ],
  "tianyuan": { "open": false, "memories": [ { "id": "mem_01", "title": "Istana yang Sunyi", "unlocked": true } ],
                "system_log": [ "...", "..." ] },
  "ui": { "mode": "explore|dialog|battle|tianyuan",
          "dialog": null, "battle": null, "options": [] }
}
```

- `ui.mode` + `ui.options` menentukan panel yang dirender (mis. `dialog` → tampilkan `ui.dialog`; `battle` → tampilkan menu battle + status musuh).
- `log_delta` pada respons aksi = entri log baru sejak aksi (UI append, tidak render ulang seluruh log).

### 12.5 Frontend (Fase 1 — tanpa build step)

- `index.html` + `app.js` (vanilla JS + `fetch`) + `style.css`.
- Panel: **Teks utama** (narasi/dialog/log), **Action bar** (kontekstual: Bicara/Pindah/Serang/Item), **Panel statistik** (HP/Qi/ranah/inventori, selalu terlihat), **Panel Tianyuan Ling** (toggle).
- Tema xianxia: latar gelap, aksen emas/tinta, font serif untuk narasi.

---

## 13. Save / Load

- Format: **JSON** per playthrough di `saves/` (gitignored).
- Isi save = `GameState` lengkap (player, quest, dialog aktif, battle aktif, inventori, waktu, moralitas, reputasi, flag, memories, tianyuan log).
- `src/engine/save.py`: `to_dict()` / `from_dict()` + validasi minimal saat load (reject save rusak → pesan jelas, bukan crash).
- Multi-slot: nama save bebas; `POST /api/game/load` membaca daftar save.

---

## 14. Validasi Data (Startup)

Dijalankan **sebelum server/CLI jalan** (`tools/validate_data.py` atau engine saat inisialisasi). Semua kegagalan → daftar error jelas + exit non-zero. Tidak ada mode "abaikan".

| # | Aturan | Contoh pesan error |
|---|---|---|
| 1 | Semua JSON parse & CSV well-formed | `items.csv baris 5: kolom 'price' bukan angka` |
| 2 | Semua referensi valid | `quest q3.next[0].quest 'q_nonexist' tidak ditemukan` |
| 3 | Graf quest **acyclic** (DFS deteksi siklus) | `siklus terdeteksi: q5 → q7 → q5` |
| 4 | Quest dengan >1 sisi punya `choice_id` & semua `option` terpetakan ke dialog | `q3: sisi b_3a tidak punya option di dlg_3_pilih_jalur` |
| 5 | Tidak ada konflik NPC/lokasi/objek antar quest yang bisa aktif bersamaan | `quest q_side_02 & q_side_05 sama-sama butuh npc_pedagang` |
| 6 | ID unik (quest/dialog/NPC/item/musuh/lokasi/teknik/ingatan) | `duplikat id 'mem_01' di memories.json` |
| 7 | `config.json`: starting quest ada, akademi valid, referensi `element_advantage` valid | `config.starting.current_quest tidak ditemukan` |
| 8 | Setiap quest sampingan punya `requires`/`available_from` yang konsisten | `q_side_03 menuntut item 'x' yang tidak ada di items.csv` |

---

## 15. Pengujian (DoD Fase 1 — GDD §11.2)

| Test | Memverifikasi |
|---|---|
| `test_quest_dag.py` | Satu-aktif invariant; urutan ketat; konvergensi (q3a/q3b/q3c → q5); percabangan via dialog; branch tak terpilih tercatat; 3 playthrough akademi bisa selesai |
| `test_dialog.py` | Traversal node, efek diterapkan, `condition` menyembunyikan opsi, `option` memilih cabang |
| `test_battle.py` | Giliran, damage elemen (1.5×/0.67×), KO → respawn titik aman, kabur |
| `test_validator.py` | Setiap aturan §14 menolak data yang sengaja dirusak |
| `test_save.py` | round-trip save/load identik; save rusak ditolak |
| `test_cultivation.py` | Ranah naik, teknik terkunci akademi & ranah |

Kriteria selesai tambahan: `tools/validate_data.py` lolos tanpa error pada data Fase 1; minimal 1 pertarungan nyata melawan musuh dari data; panel statistik menampilkan HP/Qi/ranah/inventori.

---

## 16. Roadmap Implementasi (urutan kerja)

| Langkah | Deliverable | Bergantung pada |
|---|---|---|
| 1 | Dokumen ini + skema data final | – |
| 2 | `data/` contoh lengkap Arc Akademi (quest DAG 3 jalur, dialog, NPC, item, musuh, ranah, teknik, config, memories) + `tools/validate_data.py` | 1 |
| 3 | `src/loader.py` + `src/validator.py` | 2 |
| 4 | `src/engine/state.py`, `events.py`, `morality.py`, `memory.py` | 3 |
| 5 | `src/engine/quest.py` (DAG) + `dialog.py` | 4 |
| 6 | `src/engine/battle.py` + `cultivation.py` + `items.py` + `npc.py` + `world.py` | 5 |
| 7 | `src/engine/save.py` + `session.py` (orkestrasi aksi) | 6 |
| 8 | `src/cli.py` (debug tanpa web) | 7 |
| 9 | `web/app.py` + `web/static/*` (UI + panel Tianyuan Ling) | 7 |
| 10 | `tests/` (semua §15) + penyesuaian | 8-9 |
| 11 | Playtest Arc Akademi (3 jalur), perbaikan konten, validasi DoD | 10 |

---

## 17. Catatan & Keputusan Terbuka

- **Bahasa konten** (disahkan §13-5): Bahasa Indonesia; istilah teknis (ranah, teknik, item) disertai Pinyin.
- **Durasi Fase 1** (disahkan): 1–2 jam per playthrough — volume konten quest disesuaikan target ini.
- **Ending** (disahkan): 3 tematik; mekanisme penentu final (bobot pilihan kunci + moralitas) dijabarkan lebih rinci saat konten arc final.
- **Engine adaptif**: arc baru (Sekte/Kekaisaran/Final) = tambah data + field skema bila perlu, bukan rombak engine. Jika mekanik baru butuh field skema baru → wajib update dokumen ini + validator + test.
- **GDD.md** saat ini di root; saat struktur folder dirapikan, dipindah ke `docs/GDD.md`.
