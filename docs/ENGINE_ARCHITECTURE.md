# ENGINE_ARCHITECTURE — Tian Xu: Second Life

> **Status**: Kontrak teknis (draft kerja) — acuan implementasi engine & data
> **Merujuk**: GDD.md versi 2.1 (keputusan §13 telah disahkan)
> **Fase 1**: Arc Akademi — bukti konsep (quest DAG, dialog eksplisit, 3 akademi, pertarungan giliran, kultivasi dasar, panel Tianyuan Ling)
> **Riwayat**: 2026-08-14 — sinkronisasi EP3-T2: endpoint API, kontrak state, status fitur Verified (toko web, resep dinamis, cooldown side quest, respawn monster, jadwal NPC, layar penutup Arc 1)

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
│  (browser)   │              │  (http.server + API)│          │  (logika murni)     │
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
│   │   └── dialogs_akademi.json
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
│   │   ├── session.py          # GameSession: orkestrasi state+aksi (item/NPC/world inline)
│   │   ├── state.py            # dataclass GameState / PlayerState + to_dict/from_dict
│   │   ├── quest.py            # QuestEngine (DAG)
│   │   ├── dialog.py           # DialogEngine
│   │   ├── battle.py           # BattleEngine (giliran menu)
│   │   ├── cultivation.py      # ranah, teknik, akar spiritual
│   │   ├── morality.py         # skala moralitas (baik→jahat)
│   │   ├── memory.py           # ingatan naratif (Tianyuan Ling)
│   │   ├── events.py           # log peristiwa / notifikasi Sistem
│   │   └── effects.py          # penerapan efek aksi (quest/dialog)
│   ├── loader.py               # baca JSON/CSV → dict (DataRegistry)
│   └── cli.py                  # CLI main tanpa web
├── web/
│   ├── app.py                  # http.server stdlib: serve static + API JSON
│   └── static/
│       ├── index.html
│       ├── app.js              # render state → DOM, kirim aksi
│       └── style.css           # tema xianxia + panel Tianyuan Ling
├── tests/                      # pytest
│   ├── conftest.py             # helper: finish_dialog, move_path, play_to_incident, god_mode
│   ├── test_quest_dag.py       # invariant DAG, satu-aktif, konvergensi
│   ├── test_dialog.py
│   ├── test_battle.py
│   ├── test_cultivation.py
│   ├── test_validator.py
│   ├── test_session.py
│   ├── test_effects.py         # dispatcher efek quest/dialog
│   ├── test_saveload.py        # round-trip save/load, save rusak
│   ├── test_companion.py
│   ├── test_cli.py
│   └── test_web.py
├── tools/
│   └── validate_data.py        # CLI: validasi penuh 16 aturan pada data/
└── saves/                      # file save JSON (runtime, gitignored)
```

**Konvensi kode**:
- Python **3.12**, `dataclasses`, **stdlib only** (tanpa dependensi runtime). Pengujian: **pytest** (dev-only).
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
| `on_complete` | object | – | `effects` (list, format type-based §5.2), `memory_unlock`, `system_msg`, `rewards` (`exp`/`gold`) |
| `repeatable` | bool | – | Hanya `kind: "side"` — bisa diambil ulang (grinding) |
| `cooldown` | number | – | Jam tunggu sebelum bisa diambil lagi; divalidasi §14-8 (harus > 0 jika ada), diterapkan engine (§6.4) |
| `giver` | string | – | NPC pemberi side quest (opsi `start_quest` hanya tampil lewat giver) |
| `requires` | object | – | Prasyarat: `flags`, `morality_min/max`, `realm_min` |
| `available_from` | object | – | Waktu tersedia (hari/jam) — untuk quest sampingan |

**Jenis objektif** (`objective.kind`):

| `kind` | Data tambahan | Perilaku |
|---|---|---|
| `talk` | `npc` | Buka dialog NPC; selesai saat dialog berakhir (atau setelah `target` kali) |
| `defeat` | `enemies` (list id), `target` | Kalahkan N musuh (dari data) |
| `gather` | `item`, `target` | Kumpulkan N item |
| `reach` | `location` (+ opsional `time_window`) | Tiba di lokasi; jika `time_window` (`hour_start`/`hour_end`) ada, hanya sah pada waktu itu — **event terjadwal** |
| `choose` | `options` (list) | Pilihan eksplisit (mis. pilih akademi, pilih jalur) |
| `spar` | `npc` | Sparring wajib: bicara NPC ber-`combat` → battle; **menang = objektif selesai** (dipakai sparing ujian) |
| `defeat` (+opsional `report_to`) | `enemies`, `target`, `report_to` | Side quest: kalahkan `target` musuh dari `enemies`. **A2 (2026-08-14)**: dengan `report_to`, quest hanya selesai setelah **lapor ke NPC pemberi** (`npc`) — `quest.py::notify_dialog_ended` memeriksa `defeat + report_to`; validator aturan 2 memeriksa referensi npc |
| `advance_time` | `hour` (+ opsional `day_offset`) | Tunggu hingga jam tertentu; `day_offset` = maju N hari |

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
| `speaker` | string | `npc:<id>` atau `player` atau `system` (Tianyuan Ling) atau `narration` (narasi) |
| `text` | string | Teks yang ditampilkan |
| `choices` | array | Opsi pemain; tiap opsi: `label`, opsional `option`, `effects`, `condition`, `next` |
| `condition` | object | Syarat tampil (lihat daftar kondisi di bawah) |
| `next` | string | Node berikutnya |
| `end` | bool | Akhiri dialog |
| `effects` | array | Diterapkan saat node/opsi dijalankan (lihat tabel efek) |

**Entri kondisional**: node ber-`condition` di level atas dialog = *entri alternatif* — engine memilih **entri pertama (urutan JSON) yang kondisinya benar**, jika tidak ada yang cocok memakai `start`. Pola ini memungkinkan satu dialog melayani banyak situasi (mis. reaksi NPC per cabang quest).

**Kondisi** (`condition`):

| Kunci | Contoh | Keterangan |
|---|---|---|
| `flag` | `{ "flag": { "key": "branch_3aa", "value": true } }` | Flag dunia bernilai tertentu |
| `morality_min` / `morality_max` | `{ "morality_min": 10 }` | Batas skala moralitas |
| `has_item` | `{ "has_item": "pil_qi" }` | Punya item (count ≥ 1) |
| `realm_min` | `{ "realm_min": "realm_pengumpul_qi" }` | Ranah minimum |
| `academy` | `{ "academy": "akademi_elemen" }` | Akademi pilihan pemain |
| `quest_active` / `quest_not_active` | `{ "quest_not_active": "q_side_suqing" }` | Status quest (dipakai penawaran side quest) |
| `relation_min` / `relation_max` | `{ "relation_min": { "npc": "npc_hanxiu", "value": 20 } }` | Ambang hubungan NPC — P1-2 (GDD §7): sparring berulang & on_complete quest menaikkan/menurunkan `relations`, kondisi membuka/menutup node/opsi dialog |
| `memory` | `{ "memory": "mem_02" }` | Ingatan tertentu sudah pulih — P1-1 (GDD §3.1, B3/#13): opsi dialog hanya muncul setelah `memory_unlock` quest terkait; ingatan tetap tanpa power mekanik |

**Jenis efek** (`effects`, format type-based):

| Efek | Contoh | Keterangan |
|---|---|---|
| `morality` | `{ "type": "morality", "value": -8 }` | Ubah skala moralitas (baik→jahat) |
| `reputation` | `{ "type": "reputation", "faksi": "x", "value": 2 }` | Ubah reputasi faksi/NPC |
| `relation` | `{ "type": "relation", "npc": "npc_mentor", "value": 5 }` | Ubah hubungan NPC |
| `flag` | `{ "type": "flag", "key": "bantu_petani", "value": true }` | Set flag dunia |
| `item` | `{ "type": "item", "id": "pil_qi", "count": 2 }` | Beri/kurang item (count negatif = kurangi) |
| `gold` | `{ "type": "gold", "value": 30 }` | Beri/kurang uang |
| `start_quest` | `{ "type": "start_quest", "quest": "q_side_x" }` | Mulai side quest — opsi ini **hanya tampil** jika quest dapat ditawarkan (giver, `available_from` terpenuhi, tidak aktif) |
| `branch_select` | `{ "type": "branch_select", "option": "opt_3a" }` | (internal) pilih cabang quest — diisi otomatis oleh engine |

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
      "schedule": [ { "day": 1, "hour_start": 6, "hour_end": 18, "location": "loc_gerbang_akademi" } ],
      "shop": { "buy": [ { "item": "pil_qi", "price": 50 } ], "sell": [ { "item": "material_herba", "price": 8 } ] },
      "can_spar": true
    }
  ]
}
```

- Opsional `shop`: NPC pedagang — `buy` (item yang dijual toko) & `sell` (item yang dibeli toko dari pemain) dengan harga tetap; tanpa `shop` = NPC biasa (ekonomi sederhana Fase 1, disahkan).
- Opsional `can_spar: true`: NPC bisa diajak sparing **tanpa batas frekuensi** (disahkan) — mis. Han Xiu & Gu Canghai.
- Opsional `combat`: stat battle NPC (`hp`/`qi`/`attack`/`defense`/`speed`/`element`) — dipakai untuk sparing & objektif `spar`.

### 5.4 CSV Balancing

**items.csv** — header wajib:

```
id,name,type,description,price,hp_restore,qi_restore,power,rarity,usable
pil_qi,Pil Qi,consumable,Pulihkan 30 Qi.,50,0,30,0,common,true
material_herba,Herba Awan,material,Bahan alkimia umum.,8,0,0,0,common,false
pedang_bambu,Pedang Bambu,weapon,Pedang latihan ringan (+3 serangan).,100,0,0,3,common,false
```

- `type` = `consumable` (dipakai) / `material` (bahan) / `weapon` (senjata — `power` = tambahan attack, dipasang di slot senjata).

**enemies.csv**:

```
id,name,realm,hp,qi,attack,defense,speed,element,exp_reward,drop_item,drop_chance
eno_serigala_qi,Serigala Qi,pengumpul_qi_1,40,10,8,3,10,tanah,15,pil_qi,0.3
```

**realms.csv**:

```
id,name_pinyin,name_id,order,levels,base_hp,base_qi,hp_per_level,qi_per_level,technique_slots
realm_pengumpul_qi,Pengumpul Qi (炼气 Liànqì),pengumpul_qi,1,10,80,40,5,3,1
realm_pembangun_fondasi,Pembangun Fondasi (筑基 Zhùjī),pembangun_fondasi,2,10,150,80,8,5,2
realm_pembentuk_inti,Pembentuk Inti (金丹 Jīndān),pembentuk_inti,3,10,250,140,12,8,3
realm_jiwa_baru_lahir,Jiwa Baru Lahir (元婴 Yuányīng),jiwa_baru_lahir,4,10,400,240,18,12,4
realm_transformasi_roh,Transformasi Roh (化神 Huàshén),transformasi_roh,5,10,600,380,25,16,5
realm_pemurni_kehampaan,Pemurni Kehampaan (炼虚 Liànxū),pemurni_kehampaan,6,10,900,600,35,22,6
realm_penyatu,Penyatu (合体 Hétǐ),penyatu,7,10,1300,900,50,30,7
realm_mahayana,Mahayana (大乘 Dàchéng),mahayana,8,10,1800,1300,70,40,8
realm_penantang_surga,Penantang Surga (渡劫 Dùjié),penantang_surga,9,10,2500,1800,100,55,9
```

- **`levels`** = jumlah tingkat dalam ranah (**10 tingkat per ranah**, disahkan). Status pemain = `realm` + `realm_level` (1..10).
- **HP/Qi maks** = `base + (realm_level−1) × per_level` (mis. Pengumpul Qi lvl 5 → HP 80+4×5=100, Qi 40+4×3=52).
- **Tangga 9 ranah penuh** didefinisikan sekarang (keputusan penulis) — engine membaca urutan dari `order`; **Fase 1 hanya memakai Pengumpul Qi** (dan Pembangun Fondasi sebagai ranah berikutnya).

**techniques.csv**:

```
id,name,academy,element,realm_required,qi_cost,power,kind,description
tek_elemen_bola_api,Bola Api,elemen,api,realm_pengumpul_qi,8,15,attack,Serangan api dasar.
```

- `kind` = `attack` (`power` = damage) / `defend` (`power` = persen pengurangan damage, mis. 60) / `heal` (`power` = HP pulih).

**konvensi**: CSV wajib punya baris header persis sesuai contoh; id unik; referensi (mis. `academy`, `realm_required`, `element`) wajib valid.

### 5.5 Ingatan Naratif (Tianyuan Ling)

```json
{
  "memories": [
    {
      "id": "mem_01",
      "title": "Istana yang Sunyi",
      "unlocked_by_quest": "q_akademi_05",
      "text": "Kulihat kembali bayangan istana tempatku lahir...",
      "type": "narrative"
    }
  ]
}
```

**Aturan kunci**: ingatan **tidak pernah** memberikan power mekanik (GDD §2.1). `memory_unlock` pada quest membuka entri naratif di panel Tianyuan Ling **dan** (P1-1, 2026-08-14) mengaktifkan kondisi dialog `memory` — opsi tertentu hanya muncul setelah ingatan terkait pulih (mis. pilihan "pengembara" di `dlg_moyun:node_penutup` setelah `mem_02`, dan pertanyaan duka tua di `dlg_gucanghai:node_umum` setelah `mem_01`). Gating ini mewujudkan GDD §3.1 / STORY_FASE1 §3.1 (sebelumnya B3/#13 defer). `unlocked_by_quest` bisa berupa string atau list (mis. mem_02 via 3aa/3ab); dokumentatif — mekanisme aktual tetap `on_complete.memory_unlock` di quest.

### 5.6 config.json — State Awal & Konfigurasi

```json
{
  "game_title": "Tian Xu: Second Life",    "starting": {
    "location": "loc_gerbang_akademi",
    "player": { "name": "Chen Xu", "hp": 80, "qi": 40, "realm": "realm_pengumpul_qi", "realm_level": 1 },
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
  "morality": { "min": -100, "max": 100 },
  "cultivation": {
    "levels_per_realm": 10,
    "exp_per_level_base": 10,
    "exp_growth_per_level": 1.2,
    "grounding_exp_per_hour": 2,
    "grounding_max_hours_per_day": 8,
    "spar_win_exp": 8,
    "spar_win_relation": 5,
    "spar_loss_exp": 3,
    "hunt_exp_per_kill": 6,
    "breakthrough": "auto"
  },
  "currency": { "name": "Koin Emas", "start_gold": 20 },
  "roots": {
    "tiers": [
      { "id": "akar_low",  "name": "Akar Bawah (下品)",    "exp_multiplier": 0.8 },
      { "id": "akar_mid",  "name": "Akar Menengah (中品)", "exp_multiplier": 1.0 },
      { "id": "akar_high", "name": "Akar Atas (上品)",     "exp_multiplier": 1.25 },
      { "id": "akar_peak", "name": "Akar Puncak (极品)",   "exp_multiplier": 1.5 }
    ],
    "default": "akar_mid"
  },
  "ko_penalty": { "exp_loss_ratio": 0.1 },
  "companion": { "hp_per_level": 12, "attack_per_level": 2, "defense_per_level": 1, "speed_per_level": 0.5 },
  "world": {
    "monster_respawn_hours": 5,
    "hunt": {
      "location": "loc_wilayah_berburu",
      "pool": ["eno_serigala_qi", "eno_babi_hutan"],
      "night_pool": ["eno_pembelot_malam", "eno_ular_bayangan"],
      "night_window": { "hour_start": 19, "hour_end": 6 },
      "mini_boss": "eno_raja_serigala",
      "mini_boss_chance": 0.1,
      "search_item": "material_herba"
    }
  },
  "battle": {
    "damage_formula": "percent",
    "qi_regen_percent_per_turn": 5,
    "crit_chance": 0.08,
    "crit_multiplier": 1.5,
    "turn_order": "speed"
  }
}
```

- **Akademi = data**, bukan hardcode: engine membaca `academies` dari config. Pilihan akademi (quest `choose`) hanya membuka `skill_pool` akademi itu (GDD §5.2 — sejajar DAG, tidak berpotongan naratif).
- `element_advantage` = siklus 五行 (克制): logam克kayu, kayu克tanah, tanah克air, air克api, api克logam — dipakai battle engine dengan multiplier.
- `roots.tiers` = tier akar spiritual + `exp_multiplier`; `ko_penalty.exp_loss_ratio` = penalti KO ringan (10% exp progres tingkat).

### 5.7 Resep Alkimia (recipes.json)

```json
{
  "recipes": [
    { "id": "rc_pil_qi", "result": "pil_qi", "count": 1,
      "ingredients": [ { "item": "material_herba", "count": 2 } ],
      "description": "Meracik Pil Qi dari 2 Herba Awan." }
  ]
}
```

- Alkimia dasar Fase 1 (disahkan): 2 resep (Pil Qi, Pil Pemulihan). `craft` mengonsumsi bahan & menghasilkan item.

### 5.8 Lokasi (locations.json)

```json
{
  "locations": [
    { "id": "loc_gerbang_akademi", "name": "Gerbang Akademi", "is_safe": false, "connections": ["loc_aula_ujian"] },
    { "id": "loc_asrama", "name": "Asrama Murid", "is_safe": true, "connections": ["loc_aula_ujian"] }
  ]
}
```

- `is_safe: true` = **titik aman**: tempat respawn saat KO, tempat **simpan game** (disahkan), & tempat aksi `rest`.
- `connections` = peta pergerakan pemain (pindah lokasi lewat aksi `move`).

### 5.9 Kompanion (companions.json) — jalur Summoning

```json
{
  "companions": [
    { "id": "komp_roh_awan", "name": "Roh Awan", "element": "kayu",
      "base_hp": 20, "base_attack": 5, "base_defense": 2, "base_speed": 9,
      "description": "Binatang roh kecil pemberian Akademi Summoning." }
  ]
}
```

- Hanya jalur **Summoning** yang mendapat kompanion (disahkan): diberikan saat memilih akademi (event/quest).
- Statistik akhir = base + `level × scale` (`config.companion`); `level` = level ranah pemain.

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
- **Repeatable (disahkan)**: side quest bisa diulang untuk grinding ranah.
  - Field `repeatable: true` pada quest (hanya untuk `kind: "side"`) + opsional `cooldown` (jam, divalidasi §14-8).
  - Setelah selesai, quest masuk daftar **tersedia lagi**; progres objektif direset.
  - Data side quest **terpisah** (`quests_side.json`) dan **dilarang bertabrakan** dengan quest utama (validator §14-10).

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
  → giliran: `battle.turn_order` — "speed" (default, A2 2026-08-14): yang lebih cepat
    bertindak dulu tiap ronde (foe_speed > pc.speed → musuh dulu); "fixed_alternate"
    tetap didukung (pemain → musuh, berulang)
player_action(menu):
  - serang        : damage = attack × (100 / (100 + defense musuh)), minimal 1
  - teknik        : pilih teknik; cost Qi; multiplier elemen (§8.2)
  - item          : gunakan item HP/Qi dari inventori
  - bertahan      : kurangi damage 50% giliran ini
  - kabur         : peluang sukses berdasarkan speed; gagal = giliran musuh
```

- **RNG (disahkan)**: damage dasar bervariasi **±10–20%**; **kritikal** peluang `crit_chance` (8%) damage ×`crit_multiplier` (1.5); drop item mengikuti `drop_chance` musuh (acak); peluang kabur berdasarkan speed.
- **Regen Qi (disahkan)**: pemain & musuh memulihkan `qi_regen_percent_per_turn` (5%) Qi maks di awal giliran masing-masing.
- **Sparing (disahkan)**: mekanik sama seperti battle biasa — kalah = penalti KO berlaku (respawn di titik aman + kehilangan 10% exp).

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

### 9.1 Ranah & 10 Tingkat (disahkan)

- Tiap ranah (dari `realms.csv`) punya **`levels` = 10 tingkat** (`realm_level` 1..10).
- Progresi via **Pengalaman Kultivasi (exp)** dari **aktivitas** (keputusan penulis: rajin beraktivitas = makin cepat naik tingkat):
  - **Berkultivasi / grounding (打坐 dǎzuò)** — aksi berulang di lokasi aman: habiskan waktu (jam) → dapat `grounding_exp_per_hour` exp + pulih Qi pelan; **maks `grounding_max_hours_per_day` (8) jam per hari** (disahkan).
  - **Berburu monster** — kalahkan musuh liar di wilayah berburu → `hunt_exp_per_kill` exp + material/drop.
  - **Sparing NPC** — tantang NPC ber-`can_spar: true` (Han Xiu, Gu Canghai) — **tanpa batas frekuensi** (disahkan) → menang = `spar_win_exp` exp + `spar_win_relation` (5) hubungan naik; kalah = `spar_loss_exp` exp kecil + **penalti KO berlaku** (disahkan, konsisten dengan battle biasa). (G4a, 2026-08-14): objektif quest `spar` **selesai saat kalah juga** — `notify_spar_loss` men-set flag `spar_kalah` → dialog Gu Canghai berbeda (entri kondisional), tanpa game over permanen; konsisten STORY_FASE1 #19. **(P1-2, 2026-08-14, GDD §7)**: `relations` kini **dikonsumsi** — kondisi dialog `relation_min/max` membuka node baru saat hubungan tumbuh (Han Xiu `node_tip_spar` ≥ 20, Gu Canghai `node_akui_latihan` ≥ 20), melengkapi efek relation yang sudah ada di on_complete quest; siklus penuh: spar/quest → relation → dialog berbeda.
- **Naik tingkat**: `exp_needed(level) = round(exp_per_level_base × exp_growth_per_level^(level-1))` (kurva dari `config.cultivation`, data-driven). Saat exp ≥ ambang → `realm_level` naik, exp tersisa dibawa.
- **Target balancing Fase 1 (disahkan)**: pemain yang rajin (grinding side quest/berburu) mencapai **Pengumpul Qi tingkat 5–6** di akhir arc.
  - **Rebalancing (hasil playtest, disahkan)**: exp quest dikurangi ~40% (q1–q07: 3–18) & exp aktivitas diturunkan (`grounding 2/jam`, `spar_win 8`, `hunt 6`) — playtest awal mencapai Lv.10 (maks) di akhir arc, melampaui target; dengan angka ini quest saja ≈ Lv.5, rajin ≈ Lv.6.
- **Akar spiritual (mekanik ringan, disahkan)**: semua perolehan exp dikali `roots.exp_multiplier` tier akar pemain (akar bagus = exp lebih cepat). Tier ditentukan di ujian masuk — usulan: Chen Xu = **中品 (Akar Menengah)**, cocok premis "bayi kultivator biasa" (GDD §2).
- **Breakthrough**: `realm_level` mencapai maks (10) → **breakthrough otomatis** (`breakthrough: "auto"`) ke ranah berikutnya (`order+1`), `realm_level` = 1. Ranah membuka slot teknik & batas HP/Qi baru.

### 9.2 Teknik, Item & Waktu

- **Teknik**: `techniques.csv`, terkunci ke akademi (`academy`), dibatasi ranah (`realm_required`), biaya Qi (`qi_cost`). **Enforcement (H4, 2026-08-14)**: `battle.py::_technique` menolak teknik dengan `realm_required` lebih tinggi dari ranah pemain (bandingkan `order` realm, pola sama `dialog.py`); `loader.player_techniques(academy, realm)` menyaring ranah sehingga UI web hanya menampilkan teknik yang bisa dipakai.
- **Inventori**: map item→count; item consumable (`usable=true`) bisa dipakai di luar/dalam battle.
- **Grinding loop Fase 1**: side quest repeatable (berburu / bantu Su Qing / tugas Mo Yun) + aktivitas grounding & sparing = sumber exp untuk menaikkan ranah tanpa mengganggu alur main quest.
- **Mini-boss (disahkan)**: 1 binatang liar kuat / penjaga wilayah di area berburu — opsional, respawn, reward lebih besar; puncak tantangan Fase 1.
- **Respawn monster (disahkan)**: monster area berburu muncul kembali setelah `world.monster_respawn_hours` (5) jam in-game — grinding butuh menunggu. (A2, 2026-08-14): pool musuh, lokasi berburu, mini-boss & item pencarian dibaca dari `world.hunt` di config (divalidasi aturan 7) — aktivitas berburu sepenuhnya data-driven. **(P1-3, 2026-08-14, GDD §8)**: tipe musuh beragam — `world.hunt.night_pool` + `night_window` (pola `quest._in_window`, lintas tengah malam 19→6): jam malam memakai pool malam (`eno_pembelot_malam`, `eno_ular_bayangan` — elemen api/air, drop berbeda); fallback pool siang bila field absen (non-breaking). Validator aturan 7 memeriksa referensi `night_pool` & sanitasinya `night_window`.
- **Waktu**: `world.py` memajukan waktu (hari/jam). Quest sampingan & NPC dengan `schedule` hanya tersedia pada waktu tertentu. **Event terjadwal (disahkan)**: beberapa momen hanya muncul pada waktu tertentu — mis. bukti malam Act 2 memakai objektif `reach` + `time_window` (malam) atau `advance_time` ke malam hari. Fase 1: ringan (1 kota, beberapa NPC, tanpa siklus hidup penuh).

### 9.3 Ekonomi, Alkimia & Senjata (disahkan Fase 1)

- **Ekonomi sederhana**: pemain punya uang (`gold`); **1 toko pedagang** (NPC dengan field `shop`): beli item & jual material buruan, harga tetap (bukan pasar dinamis). **Isi toko (disahkan)**: Pil Qi, material alkimia, dan **1 senjata dasar**. Uang didapat dari reward quest (`rewards.gold`) & jual material.
- **Alkimia dasar**: resep di `recipes.json` — kumpulkan material → aksi `craft` di menu (lokasi aman) → hasil pil. Fase 1: 2 resep.
- **Senjata dasar**: item `type: weapon` (`power` = tambahan attack) dipasang di slot `equipment.weapon`; didapat dari reward quest (mis. sparing Han Xiu / ujian masuk) atau dibeli di toko.
- **Penalti KO ringan (disahkan)**: saat KO, kehilangan `ko_penalty.exp_loss_ratio` (10%) dari exp progres tingkat saat ini — item & progress quest tidak hilang.

### 9.4 Kompanion — jalur Summoning (disahkan)

- Pemain jalur **Summoning** mendapat **1 binatang roh** (dari `companions.json`) saat memilih akademi; pemain jalur lain tanpa kompanion.
- **Di battle**: kompanion bertindak **otomatis** tiap giliran (AI: serangan dasar, atau teknik saat Qi cukup), punya HP sendiri & bisa diserang musuh.
- **KO**: kompanion KO → tidak aktif sampai **istirahat di titik aman** (aksi `rest`).
- **Leveling**: `level` kompanion = level ranah pemain; statistik = base + `level × scale` (`config.companion`).

**Detail implementasi (engine, disepakati saat pembangunan):**
- **Pemberian data-driven**: akademi dengan field `companion` di `config.json` (mis. `akademi_summoning.companion = "komp_roh_awan"`) memberi binatang roh saat quest `choose` akademi selesai — tidak ada hardcode ID akademi di engine.
- **Urutan battle**: kompanion menyerang otomatis **setelah aksi pemain** (sebelum giliran musuh) tiap ronde; AI = serangan dasar (`attack × 100/(100+defense)` + elemen, sama dengan formula pemain). Teknik kompanion ditunda (data belum punya teknik kompanion).
- **Validasi kepemilikan teknik**: aksi `technique` **menolak teknik di luar `skill_pool` akademi pemain** (dan sebelum akademi dipilih, semua teknik ditolak) — diperbaiki dari temuan playtest (teknik lintas akademi).
- **Target musuh**: tiap musuh **50% peluang** menarget kompanion saat kompanion aktif & HP > 0; `guard` pemain tidak melindungi kompanion.
- **Gate battle**: saat battle aktif, semua aksi non-battle ditolak session (pesan sistem) — mencegah korupsi alur dari klien web/terskrip.
- **HP persisten**: HP kompanion tersimpan di `GameState.companion` dan **tidak pulih otomatis** setelah battle menang — hanya aksi `rest` di titik aman yang membangkitkan (KO) & memulihkan penuh.
- **Gate battle (session)**: saat battle aktif, hanya aksi `battle_action` yang diterima — aksi lain (pindah, bicara, dll.) ditolak dengan pesan, mencegah state korup dari klien web/terskrip.
- **Stat**: `base + level × scale` (`config.companion`: hp/attack/defense/speed_per_level); `level` = level ranah pemain saat ini (naik otomatis mengikuti breakthrough pemain).
- **Save**: `companion` diserialisasi di save (id, hp, active).

---

## 10. Moralitas & Konsekuensi Dunia

- Skala integer `[-100, +100]`, mulai 0 (netral). Disimpan di `GameState`.
- Diubah lewat `effects.morality` pada pilihan dialog & quest.
- Dipakai untuk: membuka/menutup opsi dialog (`condition.morality_min/max`) dan menentukan ending.
- **World-facts (G4b/#10, 2026-08-14)**: konsekuensi cabang quest disimpan sebagai `flags` eksplisit (nilai string/bool apa pun didukung `effects.py`) — `zhouyan_status` (`bebas`/`diusir`), `elder_exposed`, `academy_knows_truth`, `bell_status` — sehingga konten Arc 2 bisa menanyakan kondisi dunia ("apakah Zhou Yan bebas?") tanpa field state baru.
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

- `web/app.py` (http.server stdlib) menyajikan `web/static/` + endpoint JSON.
- Satu sesi = satu `GameSession` di server (in-memory) + save ke `saves/`.
- UI render ulang penuh dari state (tidak ada state DOM yang kompleks — Fase 1).

### 12.2 Endpoint API

| Method & Path | Body | Balasan |
|---|---|---|
| `GET /api/state` | – | View sesi aktif (kontrak §12.4) atau `null` (belum ada sesi) |
| `GET /api/saves` | – | Daftar slot save (untuk menu utama "Lanjut") |
| `GET /api/tianyuan` | – | Payload panel Tianyuan Ling (mission/memories/system_log) |
| `POST /api/new` | – | Mulai game baru → `{ok, view, context}` |
| `POST /api/load` | `{"name": "..."}` | Muat save → `{ok, view, context}`; 404 jika save tidak ada, 400 jika save rusak |
| `POST /api/action` | `{"action": ActionJSON (§12.3)}` | Proses aksi → `{ok, view, context}`; 400 jika format aksi salah |
| `POST /api/save` | `{"name": "..."}` | Simpan (ditolak di luar titik aman) → `{ok, view, context}` |

- Setiap respons (kecuali `GET /api/tianyuan` & `GET /api/saves`) = `{ok, view, context}`: `view` = output `session.view()` (kontrak §12.4), `context` = data UI dari `web/app.py::_context()` (§12.5). Tidak ada `log_delta` terpisah — entri log baru terlihat di `view.log` (UI merender ulang penuh per aksi).

### 12.3 Aksi (discriminated union pada `type`)

| `type` | Payload | Dipakai |
|---|---|---|
| `talk` | `{"npc": "<id>"}` | Mulai dialog NPC |
| `dialog_choice` | `{"choice_index": 0}` | Pilih opsi dialog |
| `battle_action` | `{"action": "attack"\|"guard"\|"flee"}` atau `{"action": "technique", "technique": "<id>"}` / `{"action": "item", "item": "<id>"}` | Giliran battle |
| `use_item` | `{"item": "<id>"}` | Pakai item di luar battle |
| `equip` | `{"item": "<id>"}` | Pasang senjata (`type: weapon`) ke slot `equipment.weapon`; menambah attack di battle |
| `move` | `{"to": "<location_id>"}` | Pindah lokasi |
| `advance_time` | `{"hours": 8}` | Majukan waktu (kemungkinan memicu event) |
| `grounding` | `{"hours": 4}` | Berkultivasi di lokasi aman: waktu maju, dapat exp (sesuai `cultivation.grounding_exp_per_hour`) + pulih Qi pelan |
| `spar` | `{"npc": "<id>"}` | Tantang NPC sparing → masuk battle; menang/kalah memberi exp (§9.1) |
| `hunt` | – | Berburu monster di wilayah berburu; ditolak selama cooldown respawn (§9.2) |
| `search` | – | Cari herba material di lokasi berburu |
| `choose` | `{"value": "<option_value>"}` | Pilih opsi objektif `choose` (mis. pilih akademi) |
| `shop_buy` | `{"item": "<id>", "count": 1}` | Beli item di toko NPC (cek uang & stok) |
| `shop_sell` | `{"item": "<id>", "count": 1}` | Jual item ke toko (dapat uang) |
| `craft` | `{"recipe": "<id>"}` | Racik item dari resep (konsumsi material) — **hanya di titik aman** (lokasi `is_safe`) |
| `rest` | `{"hours": 8}` | Istirahat di **titik aman**: pulihkan HP/Qi penuh, bangkitkan kompanion, waktu maju |
| `save` | `{"save_name": "..."}` | Simpan game — **hanya di titik aman** (§13) |

> **Catatan**: panel Tianyuan Ling **bukan** aksi mutasi sesi — tidak ada handler `open_tianyuan`/`close_tianyuan` di `session.py`. Panel dibuka/tutup sepenuhnya di frontend: data dimuat via `GET /api/tianyuan` (modal penampil) dan status terbuka/tertutup dikelola `app.js`; `view()` menyediakan data ingatan & log yang dibutuhkan panel.

### 12.4 Kontrak State (potongan utama `StateJSON`)

```json
{
  "location": { "id": "loc_gerbang_akademi", "name": "Gerbang Akademi",
                "description": "...", "is_safe": false, "connections": ["loc_aula_ujian"] },
  "day": 1, "hour": 8,
  "player": { "name": "Chen Xu", "realm": "Pengumpul Qi", "realm_level": 3, "exp": 45, "exp_next": 60,
              "roots": "Akar Menengah (中品)", "gold": 20, "equipment": { "weapon": "pedang_bambu" },
              "hp": 80, "hp_max": 80, "qi": 40, "qi_max": 40, "academy": null, "morality": 0 },
  "current_quest": { "id": "q_akademi_01", "title": "Pintu Gerbang Akademi",
                     "objective": "Bicaralah dengan Penjaga Gerbang." } | null,
  "side_quests": [ { "id": "q_side_suqing", "title": "...", "objective": "..." } ],
  "inventory": [ { "id": "pil_qi", "name": "Pil Qi", "count": 3, "type": "consumable" } ],
  "memories": [ { "id": "mem_01", "title": "Istana yang Sunyi" } ],
  "companion": { "id": "komp_roh_awan", "name": "Roh Awan", "element": "kayu", "hp": 30, "hp_max": 30,
                 "attack": 7, "defense": 3, "speed": 9 } | null,
  "mode": "explore|dialog|battle|choose",
  "dialog": { "dialog_id": "dlg_penjaga", "node_id": "node_awal", "speaker": "npc_penjaga",
              "text": "...", "choices": [ { "index": 0, "label": "..." } ], "ended": false } | null,
  "battle": { "mode": "battle", "player": { "hp": 80, "hp_max": 80, "qi": 40, "qi_max": 40 },
              "foes": [ { "name": "Serigala Qi", "hp": 40, "hp_max": 40, "element": "tanah" } ],
              "companion": null, "over": false, "won": false, "fled": false } | null,
  "choose": { "prompt": "Pilih salah satu.", "options": [ { "value": "akademi_elemen", "label": "..." } ] } | null,
  "log": [ { "type": "narration|npc|system|battle", "text": "...", "day": 1, "hour": 8 } ],
  "arc_summary": null
}
```

- `mode` menentukan panel yang dirender: `dialog` → render `dialog` (node aktif + opsi); `battle` → render `battle` (menu battle + status musuh); `choose` → render `choose` (objektif pilih, mis. pilih akademi). Panel Tianyuan Ling memakai `GET /api/tianyuan`, bukan `view()`.
- `companion` = `null` untuk non-Summoning atau kompanion KO; `arc_summary` terisi saat `q_akademi_07` selesai (layar penutup Arc 1).
- `view.log` memuat seluruh log; UI merender ulang penuh per aksi — tidak ada `log_delta` terpisah.

### 12.5 Frontend (Fase 1 — tanpa build step)

- `index.html` + `app.js` (vanilla JS + `fetch`) + `style.css`.
- **Menu utama sederhana** (disahkan): layar judul dengan **Mulai Baru / Lanjut** (daftar slot dari `GET /api/saves`).
- **Layout 3 kolom (disahkan)**: teks utama di tengah · panel statistik di kiri (HP/Qi/ranah/inventori) · panel inventori/quest di kanan.
- **Tampilan teks polos (disahkan)**: tanpa ikon emoji — nama item/lokasi ditulis teks; **HP/Qi = angka saja** (mis. `HP 80/100`), tanpa bar.
- **Statis (disahkan)**: tanpa animasi — fade/glow/efek gerak ditiadakan; tema gelap + emas tetap lewat warna & tipografi.
- **Lokasi (disahkan)**: nama lokasi + deskripsi teks + tombol daftar tempat tujuan (`connections`); tanpa mini-peta.
- **Desktop dulu (disahkan)**: tidak dioptimalkan untuk layar HP (responsif ditunda).
- Panel: **Teks utama** (narasi/dialog/log), **Action bar** (kontekstual: Bicara/Pindah/Serang/Item), **Panel statistik** (HP/Qi/ranah/inventori, selalu terlihat), **Panel Tianyuan Ling** (modal — tombol "Baca Ingatan" / tombol panel membukanya, ✕ menutupnya).
- **Tema (disahkan)**: xianxia **gelap + emas** — latar gelap, aksen emas, font serif untuk narasi.

**Detail implementasi (engine web, disepakati saat pembangunan):**
- `web/app.py` — server **stdlib-only** (`http.server.ThreadingHTTPServer`), satu sesi aktif per proses (single-player lokal); jalankan `python3 web/app.py [port]`.
- Endpoint API: `GET /` · `GET /static/*` · `GET /api/state` · `GET /api/saves` · `GET /api/tianyuan` (ingatan + log sistem) · `POST /api/new` · `POST /api/load {name}` · `POST /api/action {action}` · `POST /api/save {name}`.
- Setiap respons state = `{ok, view, context}`: `view` = output engine `session.view()` (kontrak §12.4); `context` = data UI yang tidak ada di view — dari `web/app.py::_context()`: `npcs` (di lokasi, dengan `can_spar` & `shop`), `merchant_shop` (isi toko buy/sell di lokasi), `recipes` (daftar resep), `npc_names` / `item_names` (peta nama tampilan), `techniques` (skill_pool akademi), `academy` (nama tampilan akademi terpilih).
- `view.inventory` menyertakan `type` item (consumable/weapon/material) agar UI bisa memfilter aksi (pakai/racik/pasang).
- Frontend `web/static/` (index.html + style.css + app.js, vanilla, tanpa build): render ulang penuh per aksi (statis — sesuai keputusan visual); mode explore/dialog/battle/choose dirender dari `view.mode`; panel Tianyuan Ling = modal yang fetch `GET /api/tianyuan` (bukan aksi mutasi sesi, lihat §12.3).

---

## 13. Save / Load

- **Simpan hanya di titik aman** (disahkan): lokasi dengan `is_safe: true` (asrama/kota). Aksi `save` **ditolak** di luar titik aman dengan pesan jelas; pemain harus kembali ke titik aman.
- Format: **JSON** per playthrough di `saves/` (gitignored).
- Isi save = `GameState` lengkap (player, quest, dialog aktif, battle aktif, inventori, waktu, moralitas, reputasi, flag, memories, tianyuan log, kompanion).
- `src/engine/state.py`: `GameState.to_dict()` / `from_dict()` + validasi minimal saat load (reject save rusak → pesan jelas, bukan crash). Entrypoint save/load ada di `src/engine/session.py` (`GameSession.load` & aksi `save`).
- Multi-slot: nama save bebas; `POST /api/load {name}` memuat save, `GET /api/saves` membaca daftar slot.

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
| 8 | Setiap quest sampingan punya `available_from {day, hour}`; `cooldown` valid jika ada | `q_side_x: side quest butuh available_from {day, hour}` |
| 9 | `repeatable: true` hanya untuk quest `kind: "side"` | `q_main_x: repeatable=true tapi kind='main'` |
| 10 | Quest repeatable dilarang menuntut NPC/lokasi/objek yang dipakai quest utama | `q_side_berburu & q_akademi_04: konflik lokasi loc_ruang_lonceng` |
| 11 | Resep alkimia: hasil & bahan valid, bahan ≠ hasil | `rc_pil_qi: bahan 'x' tidak ada di items.csv` |
| 12 | Toko NPC: item `buy`/`sell` valid | `npc_pedagang: shop.buy[0].item 'x' tidak ada` |
| 13 | Item `weapon` punya `power`; `config.roots.tiers` valid & `default` ada | `items.csv: weapon tanpa power` |
| 14 | Lokasi: `is_safe` bool; `connections` merujuk lokasi yang ada | `loc_x: connections[0] 'loc_y' tidak ditemukan` |
| 15 | Kompanion: id unik, base stat valid, referensi elemen valid | `companions.json: id duplikat` |
| 16 | `config.battle`: `crit_chance` 0–1, `turn_order` valid, `damage_formula` valid | `config.battle.crit_chance: harus 0–1` |

---

## 15. Pengujian (DoD Fase 1 — GDD §11.2)

| Test | Memverifikasi |
|---|---|
| `test_quest_dag.py` | Satu-aktif invariant; urutan ketat; konvergensi (q3a/q3b/q3c → q5); percabangan via dialog; branch tak terpilih tercatat; 3 playthrough akademi bisa selesai; side quest repeatable & event malam (Act 2) |
| `test_dialog.py` | Traversal node, efek diterapkan, `condition` menyembunyikan opsi, `option` memilih cabang, entri kondisional, `start_quest` hanya saat bisa ditawarkan, side quest mulai & selesai |
| `test_battle.py` | Urutan giliran tetap; damage persentase (attack × 100/(100+defense)); elemen (1.5×/0.67×); regen Qi per giliran; kritikal; KO → respawn titik aman + penalti exp 10%; kabur; sparing kalah = penalti KO; teknik terkunci akademi |
| `test_validator.py` | Setiap aturan §14 (16 aturan) menolak data yang sengaja dirusak |
| `test_cultivation.py` | **multiplier akar spiritual**; breakthrough level 10 → ranah berikutnya; ranah tertinggi tidak breakthrough |
| `test_session.py` | Pergerakan via `connections`; grounding/save/rest/craft hanya di titik aman; ekonomi toko (beli/jual, uang tak cukup ditolak); round-trip save/load; pakai item; racik; gate battle; equip senjata; waktu maju; respawn timer berburu; jadwal NPC |
| `test_effects.py` | Dispatcher efek: tiap jenis efek quest/dialog diterapkan benar pada state |
| `test_saveload.py` | Round-trip `to_dict`/`from_dict`; save rusak ditolak dengan pesan jelas |
| `test_companion.py` | Kompanion jalur Summoning ikut battle otomatis; KO → istirahat di titik aman; scaling level; musuh bisa menyerang kompanion |
| `test_cli.py` | Playthrough CLI penuh cabang 3aa dari awal sampai selesai — **parametrize 3 akademi (elemen/senjata/summoning)** (A1, 2026-08-14, tutup DoD §11.2 #1): assert banner arc, cabang, header akademi, kompanion "Roh" (summoning), dan **arc-end `realm_level` Lv 4–6** (baseline pacing — guardrail rebalancing A2) |
| `test_battle.py` | (+A1) `test_teknik_akademi_dipakai_di_battle` — teknik khas tiap akademi (elemen/senjata/summoning) tereksekusi di battle |
| `test_web.py` | Endpoint API: new/load/action/save/tianyuan; aksi tanpa sesi & format salah ditolak (400); save di luar titik aman ditolak |

Kriteria selesai tambahan: `tools/validate_data.py` lolos tanpa error pada data Fase 1; minimal 1 pertarungan nyata melawan musuh dari data; panel statistik menampilkan HP/Qi/ranah/inventori.

---

## 16. Roadmap Implementasi (urutan kerja)

| Langkah | Deliverable | Bergantung pada | Status |
|---|---|---|---|
| 1 | Dokumen ini + skema data final | – | ✅ selesai |
| 2 | `data/` contoh lengkap Arc Akademi (quest DAG 3 jalur, dialog, NPC, item, musuh, ranah, teknik, config, memories) + `tools/validate_data.py` | 1 | ✅ selesai |
| 3 | `src/loader.py` + validasi startup (`tools/validate_data.py`) | 2 | ✅ selesai |
| 4 | `src/engine/state.py`, `events.py`, `morality.py`, `memory.py` | 3 | ✅ selesai |
| 5 | `src/engine/quest.py` (DAG) + `dialog.py` | 4 | ✅ selesai |
| 6 | `src/engine/battle.py` + `cultivation.py` (item/NPC/world inline di `session.py`) | 5 | ✅ selesai |
| 7 | `src/engine/session.py` (orkestrasi aksi + save/load lewat `state.py`) | 6 | ✅ selesai |
| 8 | `src/cli.py` (debug tanpa web) | 7 | ✅ selesai |
| 9 | `web/app.py` + `web/static/*` (UI + panel Tianyuan Ling) | 7 | ✅ selesai |
| 10 | `tests/` (semua §15) + penyesuaian | 8-9 | ✅ selesai |
| 11 | Playtest Arc Akademi (3 jalur), perbaikan konten, validasi DoD | 10 | ✅ selesai (rebalancing v0.1.0-alpha) |

---

## 17. Catatan & Keputusan Terbuka

- **Bahasa konten** (disahkan §13-5): Bahasa Indonesia; istilah teknis (ranah, teknik, item) disertai Pinyin.
- **Durasi Fase 1** (disahkan): 1–2 jam per playthrough — volume konten quest disesuaikan target ini.
- **Ending** (disahkan): 3 tematik; mekanisme penentu final (bobot pilihan kunci + moralitas) dijabarkan lebih rinci saat konten arc final.
- **Engine adaptif**: arc baru (Sekte/Kekaisaran/Final) = tambah data + field skema bila perlu, bukan rombak engine. Jika mekanik baru butuh field skema baru → wajib update dokumen ini + validator + test.
- **Cooldown side quest — SELESAI (Verified)**: field `cooldown` divalidasi validator (§14-8) dan **diterapkan engine** — quest repeatable tidak langsung tersedia lagi selama cooldown. Implementasi: `GameState.side_quest_cooldowns` (peta `qid → absolute hour`) menyimpan waktu selesai; `quest.py` menolak penawaran ulang jika `(jam_sekarang − waktu_selesai) < cooldown`.
- **Fitur Fase 1 — SELESAI (Verified)** (diverifikasi terhadap `web/app.py` & `src/engine/`, 2026-08-14):
  - **Toko Web**: modal beli/jual di Pasar Changfeng — data dari `context.merchant_shop`, aksi `shop_buy`/`shop_sell`.
  - **Dinamisasi Resep**: tombol racik dirender dari `context.recipes` (hanya resep yang bahan terpenuhi) — bukan list hardcode.
  - **Cooldown Side Quest**: lihat catatan di atas (`side_quest_cooldowns` + `quest.py`).
  - **Timer Respawn Monster**: `_hunt()` menolak berburu ulang sebelum `world.monster_respawn_hours` (5 jam) sejak `last_hunt_time` (log sistem informatif).
  - **Jadwal Harian NPC**: `_is_npc_available(npc)` membatasi `_talk`/`_spar` pada `schedule.hour_start..hour_end` — NPC aktif tiap hari, tanpa softlock. (A1, 2026-08-14): pola diseragamkan dengan `quest._in_window` — mendukung jadwal lintas tengah malam (19 → 6) dan batas `hour_end` eksklusif. **Verifikasi 2026-08-14**: seluruh 9 schedule di `data/npcs.json` memenuhi `hour_start < hour_end` (6–22, 6–20, 8–18, 7–19, 9–17, …) — perubahan batas eksklusif tidak berdampak playthrough saat ini.
  - **Layar Penutup Arc 1**: `view().arc_summary` saat `q_akademi_07` selesai → banner ANSI emas di CLI + modal penutup di web (`modal-arc-summary`). **Batasan (G3d)**: sekali-dismiss per save disimpan di `localStorage` frontend (`arc-seen:<nama-save>`) — **tidak ikut antar perangkat/browser** (keputusan K2; Fase 1 = lokal single-player, diterima). Opsi backend (flag di save) ditunda.
- **Playtest putaran 2 — observasi → KEPUTUSAN (disahkan 2026-08-14, Tahap A plan `2026-08-14-rampungkan-arc-akademi-tahap-a.md`)** — tidak ada lagi item "open":
  - **Han Xiu undertuned → `turn_order: "speed"`** (keputusan: dukung urutan giliran berbasis `speed`, bukan naikkan stat): `battle.turn_order` kini `"speed"` — yang lebih cepat bertindak dulu tiap ronde (`battle.py::player_action`, `foe_speed > pc.speed` → `_enemy_turn` dulu). Han Xiu (speed 11) & serigala (10) kini menyerang duluan — gate ujian q3 jadi menantang (pemain bisa kalah; jalur kalah aman via G4a). `fixed_alternate` tetap didukung (validator aturan 16 menerima keduanya). Guard: god_mode test mematikan `_enemy_turn` (deterministik).
  - **Reward ganda spar q3 → reward quest q3 diturunkan** `exp 8 → 4` (total spar ujian = `spar_win_exp` 8 + 4 = 12 exp + 10 koin — tidak dobel penuh).
  - **Side quest "kalahkan" tanpa lapor → objektif defeat kini punya `report_to`**: `q_side_berburu` butuh lapor ke `npc_pemburu` setelah 2 kill (`quest.py::notify_dialog_ended` memeriksa `defeat + report_to`; validator aturan 2 memeriksa referensi npc). `objective_text` menampilkan status lapor (✓/—).
  - **Over-leveling via grind → cap exp grinding harian**: `cultivation.daily_grind_exp_cap` (60) — exp dari berburu, spar, dan side quest dibatasi per hari (`gain_grind_exp`, `state.exp_grind_today`, reset saat ganti hari); main quest & grounding tidak terpengaruh. Playthrough parametrize meng-assert arc-end Lv 4–6 sebagai guardrail pacing.
  - Save tak ditemukan TIDAK diam-diam — pesan jelas di CLI (`cli.py:165`) — tanpa perubahan.
- **GDD.md** sudah dipindah ke `docs/GDD.md` (struktur folder final sesuai GDD §10.3).
