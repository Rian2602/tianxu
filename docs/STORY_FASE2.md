# STORY — Arc Sekte & Kekaisaran (Fase 2)

> **Status**: Dokumen desain konten Fase 2 — siap diimplementasikan sebagai data JSON/CSV  
> **Merujuk**: GDD.md §3–§4 (struktur naratif, quest DAG), §12 (roadmap)  
> **Input teknis**: ENGINE_ARCHITECTURE.md §5–§7 (skema quest/dialog/NPC/ingatan)  
> **Prasyarat**: Fase 1 (Arc Akademi) selesai — semua fitur engine sudah ada (§11 GDD)  
> **Durasi target**: 3–4 jam per playthrough · **4 playthrough** (kombinasi cabang Fase 1 + pilihan Fase 2)

---

## 1. Ringkasan Eksekutif

**Fase 2** melanjutkan cerita Chen Xu setelah Arc Akademi (q07). Pemain kini:
- Membawa **world-state dari Fase 1** (flags: `zhouyan_status`, `elder_exposed`, `academy_knows_truth`)
- Memiliki **2 ingatan terpulih** (mem_01 + satu dari mem_02/03/04)
- Berada di **ranah Pembangun Fondasi (筑基)** tingkat 3–5 (grinding via side quest Fase 1)
- Siap memasuki **konflik skala lebih besar**: sekte → kekaisaran

**Struktur Fase 2**:
```
Arc Sekte (q_sekte_01 → q_sekte_08)
    ↓
Arc Kekaisaran (q_kek_01 → q_kek_10)
    ↓
Konvergensi → Quest Final Fase 2 (q_f2_final)
```

**Fitur Baru Fase 2**:
| Fitur | Status Engine | Konten Baru |
|-------|---------------|-------------|
| Multi-companion (2+ rekan) | ✅ Sudah ada (`companions.json`) | Tambah 3 companion baru |
| Teknik tingkat lanjut (ranah 3–5) | ✅ Sudah ada (`techniques.csv`) | Tambah 15 teknik baru |
| Crafting/alat tingkat tinggi | ✅ Sudah ada (`recipes.json`) | Tambah 8 resep baru |
| Reputation/faksi sistem | ✅ Sudah ada (relations) | Tambah 4 faksi sekte |
| Time-sensitive events | ✅ Sudah ada (`time_window`) | 5 event terjadwal baru |
| Branching bertingkat (DAG kompleks) | ✅ Sudah ada (q_akademi_3aa/3ab) | 6 percabangan baru |
| Memory gating dialog | ✅ Sudah ada (`condition.memory`) | 4 ingatan baru (mem_05–08) |
| World-state carryover | ✅ Sudah ada (flags) | 8 flags baru dari Fase 1 |

---

## 2. Sinopsis — Tiga Babak Fase 2

### Act 1 — Arc Sekte: Undangan & Konflik Internal *(tone: transisi gelap)*

**Premis**: Setelah kebenaran Lonceng Angin Panjang terungkap, Chen Xu menerima **undangan dari 3 sekte besar** yang menguasai benua. Ini adalah promosi alami — murid akademi berbakat direkrut sekte untuk konflik skala regional.

**3 Sekte Besar**:
| Sekte | Hanzi | Pinyin | Filosofi | Bonus |
|-------|-------|--------|----------|-------|
| **Sekte Pedang Langit** | 天剑宗 | Tiānjiàn Zōng | "Satu tebasan membelah takdir" | +20% attack speed, teknik pedang udara |
| **Sekte Alkimia Surgawi** | 天丹阁 | Tiāndān Gé | "Pil adalah jalan keabadian" | +30% efektivitas pil, crafting pil langka |
| **Sekte Roh Kuno** | 古灵宗 | Gǔlíng Zōng | "Ikatan jiwa dengan roh leluhur" | +1 companion slot, summon roh kuno |

**Konflik Internal**: Setiap sekte ternyata **terkontaminasi korupsi** — mirip Penatua An tapi skala更大 (lebih besar). Chen Xu harus memilih:
- **Infiltrasi**: Masuk sekte, bongkar dari dalam (jalan reformis)
- **Konfrontasi**: Serang langsung, risiko tinggi (jalan destroyer)
- **Manipulasi**: Mainkan kedua sisi untuk keuntungan pribadi (jalan oportunis)

**Puncak Act 1**: Chen Xu menemukan bukti bahwa **ketiga sekte berkolusi** dalam eksperimen terlarang — mencoba menciptakan "senjata hidup" dari kultivator muda. Ini mengingatkannya pada **pengkhianatan kolektif** di kehidupan pertama (Long Tianxu).

---

### Act 2 — Arc Kekaisaran: Tahta yang Hilang *(tone: tragis, revelasi)*

**Premis**: Setelah konflik sekte, Chen Xu tertarik ke **ibukota kekaisaran** — tempat Long Tianxu lahir dan dibuang. Di sini ia bertemu **sisa-sisa jaringan lama**: mantan pengikut setia ayahanda, sekarang tersebar atau tewas.

**Tokoh Kunci Arc Kekaisaran**:
| ID | Nama | Peran | Rahasia |
|----|------|-------|---------|
| `npc_jenderal_liu` | Liu Feng | Jenderal tua pensiunan | Dulu jenderal pribadi ayahanda Long Tianxu |
| `npc_selir_mei` | Selir Mei | Selir ayahanda (masih hidup) | Bukan yang meracuni — korban fitnah |
| `npc_pangeran_muda` | Pangeran Hao | Adik tiri Long Tianxu | Mengira Tianxu sudah mati, naik tahta |
| `npc_mantan_kekasih` | Lin Yue | Eks-kekasih Long Tianxu | **Masih hidup**, sekarang permaisuri Pangeran Hao |
| `npc_pembunuh_bayangan` | Bayangan Merah | Assassin misterius | Mantan murid kesayangan Long Tianxu (pengkhianat utama) |

**Revelasi Utama**:
1. **Istri & anak Long Tianxu benar-benar tewas** — tidak bisa diselamatkan, tidak ada twist "mereka hidup"
2. **Pengkhianat utama** adalah **mantan murid kesayangan** (bukan selir, bukan eks-kekasih) — ini yang paling menyakitkan
3. **Pangeran Hao** (adik tiri) **tidak tahu** Chen Xu = Long Tianxu — mengira kakaknya mati tahun lalu
4. **Lin Yue** (eks-kekasih) **tahu identitas Chen Xu** — tapi diam, terjebak antara cinta lama & kewajiban baru

**Percabangan Moral Arc Kekaisaran**:
| Cabang | Pilihan | Konsekuensi |
|--------|---------|-------------|
| **K1** | Ampuni Selir Mei & Lin Yue | Naik moralitas (+), dapat aliansi lemah |
| **K2** | Eksekusi semua pengkhianat | Turun moralitas (−), dapat kekuatan militer |
| **K3** | Biarkan Pangeran Hao tetap berkuasa | Netral (0), fokus ke musuh sebenarnya (sistem) |
| **K4** | Ambil tahta untuk diri sendiri | Moralitas netral, buka ending "Reformer" awal |

---

### Act 3 — Konvergensi: Menuju Arc Final *(tone: determinasi)*

**Premis**: Setelah Arc Sekte & Kekaisaran, Chen Xu menyadari **musuh sebenarnya bukan individu** — tapi **struktur dunia kultivasi** yang memungkinkan pengkhianatan terjadi berulang.

**Quest Final Fase 2** (`q_f2_final`):
- **Objektif**: Putuskan apakah akan:
  - (A) Mulai membangun **gerakan reformasi** (jalan pahlawan)
  - (B) Kumpulkan kekuatan untuk **menghancurkan sistem** (jalan destroyer)
  - (C) **Meninggalkan dunia ini** dan mencari jalan ascension (jalan pelarian)
- **Tidak ada battle final** — ini adalah **pilihan filosofis** yang menentukan arah Fase 3
- **Reward**: Bukan item/exp, tapi **unlock tree ending** untuk Fase 3

**World-State yang Dibawa ke Fase 3**:
| Flag | Nilai Mungkin | Dampak Fase 3 |
|------|---------------|---------------|
| `sekte_alliance` | `tianjian` / `tiandan` / `guling` / `none` | Sekte mana yang jadi aliansi/musuh |
| `kaisar_status` | `hao_bekuasa` / `chen_xu_tahta` / `kosong` | Struktur kekuasaan ibukota |
| `lin_yue_nasib` | `hidup_bersekutu` / `hidup_musuhan` / `mati` | Romance arc Fase 3 |
| `murid_pengkhianat_nasib` | `hidup` / `mati` / `hilang` | Boss fight potensial Fase 3 |
| `reform_movement` | `aktif` / `tidak` / `ditindas` | Ketersediaan opsi ending "Reformer" |
| `moralitas_total` | `-100` sampai `+100` | Ending lock/unlock |
| `ingatan_terkumpul` | `6/8` (Fase 1+2) | Persentase reveal cerita |
| `companion_count` | `1–4` | Kekuatan party Fase 3 |

---

## 3. Tokoh Fase 2

### 3.1 Companion Baru (Total: 4 Aktif)

| ID | Nama | Asal | Element | Skill Unik | Unlock Condition |
|----|------|------|---------|------------|------------------|
| `comp_liuyan` | Liu Yan | Sekte Pedang Langit | Api | `combo_attack` (serang 2x giliran) | Selesaikan q_sekte_03 cabang Pedang |
| `comp_danmo` | Dan Mo | Sekte Alkimia Surgawi | Tanah | `craft_pil_battle` (buat pil saat combat) | Selesaikan q_sekte_03 cabang Alkimia |
| `comp_linghu` | Ling Hu | Sekte Roh Kuno | Kayu | `summon_roh_leluhur` (panggil temporary NPC fighter) | Selesaikan q_sekte_03 cabang Roh |
| `comp_xue` | Xue | Ibukota (misterius) | Es | `freeze_enemy` (chance stun 1 turn) | Temui di q_kek_05, pilih ampuni Lin Yue |

**Mekanik Multi-Companion**:
- Max 2 companion aktif di party (selain Chen Xu)
- Companion lain di-"bench", bisa swap di titik aman
- Setiap companion punya **relationship meter** terpisah
- Relationship tinggi unlock **combo technique** (Chen Xu + companion)

---

### 3.2 NPC Utama Fase 2

| ID | Nama | Hanzi | Peran | Lokasi | Dialog ID |
|----|------|-------|-------|--------|-----------|
| `npc_guru_sekte_tj` | Elder Jian | 简长老 | Guru Sekte Pedang Langit | `loc_sekte_tianjian` | `dlg_guru_tj` |
| `npc_guru_sekte_td` | Master Ding | 鼎大师 | Guru Sekte Alkimia | `loc_sekte_tiandan` | `dlg_guru_td` |
| `npc_guru_sekte_gl` | Nenek Ling | 灵婆婆 | Guru Sekte Roh Kuno | `loc_sekte_guling` | `dlg_guru_gl` |
| `npc_jenderal_liu` | Liu Feng | 刘风 | Jenderal Pensiunan | `loc_ibukota_pasukan` | `dlg_liufeng` |
| `npc_selir_mei` | Selir Mei | 梅妃 | Selir Ayahanda | `loc_istana_sayap_timur` | `dlg_selirmei` |
| `npc_pangeran_hao` | Pangeran Hao | 浩皇子 | Adik Tiri, Kaisar Sekarang | `loc_istana_tahta` | `dlg_pangeranhao` |
| `npc_lin_yue` | Lin Yue | 林月 | Eks-Kekasih, Permaisuri | `loc_istana_permaisuri` | `dlg_linyue` |
| `npc_pembunuh_bayangan` | Bayangan Merah | 红影 | Mantan Murid Kesayangan | `loc_rahasia_gudang` | `dlg_bayanganmerah` |

---

## 4. Ingatan Fase 2 (mem_05 – mem_08)

| ID | Judul | Isi Singkat | Terbuka Via | Dampak Dialog |
|----|-------|-------------|-------------|---------------|
| `mem_05` | **Mahkota yang Berat** | Long Tianxu dinobatkan sebagai Pelindung Dunia; ia menolak mahkota, tapi menerima tanggung jawab | q_sekte_05 (cabang infiltrasi) | Opsi dialog "Aku tahu beban kepemimpinan" |
| `mem_06` | **Perjanjian Darah** | Tianxu bersumpah dengan 3 sekutu untuk melindungi kekaisaran; mereka semua berkhianat nanti | q_sekte_05 (cabang konfrontasi) | Opsi dialog "Sumpah itu mudah diucapkan" |
| `mem_07` | **Anak yang Tak Pernah Lahir** | Istri Tianxu hamil; mereka berencana kabur setelah tugas selesai; anak itu tewas bersama ibunya | q_kek_06 (temui Lin Yue) | Opsi dialog khusus tentang keluarga |
| `mem_08` | **Murid Terbaikku** | Tianxu menyelamatkan seorang anak jalanan, mengangkatnya sebagai murid; anak itu yang menusuk dari belakang di akhir | q_kek_08 (konfrontasi Bayangan Merah) | Opsi dialog "Pengkhianatan paling tajam datang dari yang kau percaya" |

**Total Ingatan Fase 2**: 4 (total kumulatif: 8/??)

---

## 5. Quest DAG — Arc Sekte

### 5.1 Flow Diagram

```
q_sekte_01 (Undangan Sekte)
    ↓
q_sekte_02 (Pilih Sekte) ─┬─> q_sekte_03a (Pedang) ─┐
                          ├─> q_sekte_03b (Alkimia) ─┼─> q_sekte_04 (Pelatihan)
                          └─> q_sekte_03c (Roh) ─────┘
                                    ↓
                          q_sekte_05 (Eksperimen Terlarang)
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
              q_sekte_06a      q_sekte_06b     q_sekte_06c
            (Infiltrasi)    (Konfrontasi)    (Manipulasi)
                    │               │               │
                    └───────────────┼───────────────┘
                                    ↓
                          q_sekte_07 (Kebenaran Kolusi)
                                    ↓
                          q_sekte_08 (Keputusan)
                                    ↓
                            → q_kek_01 ←
```

### 5.2 Detail Quest (Schema JSON-ready)

#### `q_sekte_01` — Undangan Sekte
```json
{
  "id": "q_sekte_01",
  "title": "Undangan Tiga Sekte",
  "arc": "sekte",
  "kind": "main",
  "summary": "Tiga utusan sekte besar tiba di Changfeng, membawa undangan resmi untuk Chen Xu.",
  "objective": {
    "kind": "talk",
    "npc": "npc_utusan_gabung",
    "target": 3,
    "hint": "Bicaralah dengan ketiga utusan sekte di Aula Ujian."
  },
  "next": [{"quest": "q_sekte_02", "branch": "b1", "label": "Lanjut"}],
  "on_complete": {
    "effects": [{"type": "flag", "key": "met_utusan", "value": true}],
    "system_msg": "[Sistem] Jalanmu mulai menarik perhatian para kuat.",
    "rewards": {"exp": 10, "gold": 20}
  }
}
```

#### `q_sekte_02` — Pilih Sekte
```json
{
  "id": "q_sekte_02",
  "title": "Pilih Jalan Sekte",
  "arc": "sekte",
  "kind": "main",
  "summary": "Chen Xu harus memilih salah satu dari tiga sekte besar untuk bergabung.",
  "objective": {
    "kind": "choose",
    "options": [
      {"label": "Sekte Pedang Langit (天剑宗)", "value": "sekte_tianjian"},
      {"label": "Sekte Alkimia Surgawi (天丹阁)", "value": "sekte_tiandan"},
      {"label": "Sekte Roh Kuno (古灵宗)", "value": "sekte_guling"}
    ],
    "hint": "Pilihan ini menentukan teknik, companion, dan alur quest berikutnya."
  },
  "next": [
    {"quest": "q_sekte_03a", "branch": "b_tj", "choice_id": "dlg_pilih_sekte", "option": "opt_tj"},
    {"quest": "q_sekte_03b", "branch": "b_td", "choice_id": "dlg_pilih_sekte", "option": "opt_td"},
    {"quest": "q_sekte_03c", "branch": "b_gl", "choice_id": "dlg_pilih_sekte", "option": "opt_gl"}
  ],
  "on_complete": {
    "effects": [{"type": "flag", "key": "sekte_dipilih", "value": true}],
    "system_msg": "Kau memilih jalanmu. Tidak ada jalan kembali.",
    "rewards": {"exp": 15}
  }
}
```

#### `q_sekte_03a/b/c` — Quest Awal Sekte (3 Varian)
```json
{
  "id": "q_sekte_03a",
  "title": "Ujian Pedang Langit",
  "arc": "sekte",
  "kind": "main",
  "summary": "Sekte Pedang Langit menguji Chen Xu dengan duel melawan 3 senior.",
  "objective": {
    "kind": "battle_sequence",
    "enemies": ["eno_senior_pedang_1", "eno_senior_pedang_2", "eno_senior_pedang_3"],
    "hint": "Kalahkan 3 senior secara beruntun di Arena Pedang Langit."
  },
  "next": [{"quest": "q_sekte_04", "branch": "b_tj_conv", "label": "Konvergen"}],
  "on_complete": {
    "effects": [
      {"type": "flag", "key": "sekte_tianjian_masuk", "value": true},
      {"type": "technique", "id": "tek_tj_langit_terbelah"},
      {"type": "companion", "id": "comp_liuyan"}
    ],
    "rewards": {"exp": 25, "gold": 30}
  }
}
```

*(q_sekte_03b/03c serupa, reward teknik & companion berbeda)*

#### `q_sekte_04` — Pelatihan Sekte
```json
{
  "id": "q_sekte_04",
  "title": "Pelatihan Intensif",
  "arc": "sekte",
  "kind": "main",
  "summary": "Chen Xu menjalani pelatihan intensif selama 30 hari di sekte pilihan.",
  "objective": {
    "kind": "advance_time",
    "day_offset": 30,
    "hour": 8,
    "hint": "Habiskan 30 hari untuk pelatihan. Ranahmu akan naik."
  },
  "next": [{"quest": "q_sekte_05", "branch": "b2", "label": "Lanjut"}],
  "on_complete": {
    "effects": [
      {"type": "realm_exp", "value": 500},
      {"type": "flag", "key": "pelatihan_sekte_selesai", "value": true}
    ],
    "system_msg": "30 hari berlalu. Kau merasa Qi-mu mengalir lebih deras.",
    "rewards": {"exp": 50}
  }
}
```

#### `q_sekte_05` — Eksperimen Terlarang
```json
{
  "id": "q_sekte_05",
  "title": "Eksperimen Terlarang",
  "arc": "sekte",
  "kind": "main",
  "summary": "Chen Xu menemukan dokumen rahasia tentang eksperimen 'Senjata Hidup' di sekte.",
  "objective": {
    "kind": "search",
    "location": "loc_rahasia_gudang_sekte",
    "time_window": {"hour_start": 23, "hour_end": 4},
    "hint": "Selidiki gudang rahasia pada malam hari."
  },
  "next": [
    {"quest": "q_sekte_06a", "branch": "b_infil", "choice_id": "dlg_reaksi_eksperimen", "option": "opt_infil", "label": "Infiltrasi — cari bukti lebih banyak"},
    {"quest": "q_sekte_06b", "branch": "b_konfr", "choice_id": "dlg_reaksi_eksperimen", "option": "opt_konfr", "label": "Konfrontasi — hadapi guru sekte"},
    {"quest": "q_sekte_06c", "branch": "b_manip", "choice_id": "dlg_reaksi_eksperimen", "option": "opt_manip", "label": "Manipulasi — pakai informasi ini untuk untung"}
  ],
  "on_complete": {
    "effects": [{"type": "flag", "key": "temu_eksperimen", "value": true}],
    "memory_unlock": "mem_05",
    "system_msg": "[Sistem] Sejarah berulang. Kali ini kau punya pilihan.",
    "rewards": {"exp": 30}
  }
}
```

*(q_sekte_06a/b/c memiliki struktur serupa dengan q_akademi_3aa/3ab/3b/3c — cabang moral)*

#### `q_sekte_07` — Kebenaran Kolusi
```json
{
  "id": "q_sekte_07",
  "title": "Kolusi Terungkap",
  "arc": "sekte",
  "kind": "main",
  "summary": "Ketiga sekte ternyata berkolusi dalam eksperimen Senjata Hidup — ini lebih besar dari yang dikira.",
  "objective": {
    "kind": "talk",
    "npc": "npc_mata_mata_netral",
    "target": 1,
    "hint": "Temui mata-mata yang membawa bukti kolusi."
  },
  "next": [{"quest": "q_sekte_08", "branch": "b3", "label": "Lanjut"}],
  "on_complete": {
    "effects": [
      {"type": "flag", "key": "kolusi_terbukti", "value": true},
      {"type": "flag", "key": "sekte_musuh", "value": ["sekte_tianjian", "sekte_tiandan", "sekte_guling"]}
    ],
    "rewards": {"exp": 35}
  }
}
```

#### `q_sekte_08` — Keputusan Akhir Arc Sekte
```json
{
  "id": "q_sekte_08",
  "title": "Jalan yang Kau Pilih",
  "arc": "sekte",
  "kind": "main",
  "summary": "Chen Xu memutuskan bagaimana menghadapi kolusi sekte.",
  "objective": {
    "kind": "choose",
    "options": [
      {"label": "Hancurkan ketiganya (jalan kekerasan)", "value": "hancurkan_sekte"},
      {"label": "Bongkar ke publik (jalan reformis)", "value": "bongkar_publik"},
      {"label": "Biarkan, fokus ke kekaisaran (jalan pragmatis)", "value": "abaikan_sekte"}
    ],
    "hint": "Pilihan ini memengaruhi world-state Fase 3."
  },
  "next": [{"quest": "q_kek_01", "branch": "b4", "label": "Lanjut ke Kekaisaran"}],
  "on_complete": {
    "effects": [
      {"type": "flag", "key": "arc_sekte_selesai", "value": true},
      {"type": "morality", "value": 10},
      {"type": "relation", "npc": "npc_guru_sekte_tj", "value": -10},
      {"type": "relation", "npc": "npc_guru_sekte_td", "value": -10},
      {"type": "relation", "npc": "npc_guru_sekte_gl", "value": -10}
    ],
    "system_msg": "[Sistem] Langkah pertama menuju perubahan — atau kehancuran.",
    "rewards": {"exp": 40, "gold": 50}
  }
}
```

---

## 6. Quest DAG — Arc Kekaisaran

### 6.1 Flow Diagram

```
q_kek_01 (Tiba di Ibukota)
    ↓
q_kek_02 (Temui Liu Feng)
    ↓
q_kek_03 (Masuk Istana)
    ↓
q_kek_04 (Temui Selir Mei) ─┬─> q_kek_05a (Ampuni) ─┐
                            ├─> q_kek_05b (Eksekusi) ─┼─> q_kek_06 (Lin Yue)
                            └─> q_kek_05b (Abaikan) ──┘
                                      ↓
                            q_kek_07 (Pangeran Hao)
                                      ↓
                            q_kek_08 (Bayangan Merah)
                                      ↓
                            q_kek_09 (Tahta atau Bebas?)
                                      ↓
                            q_kek_10 (Keputusan Akhir)
                                      ↓
                              → q_f2_final ←
```

*(Detail quest Arc Kekaisaran mengikuti pola sama seperti Arc Sekte — schema JSON-ready)*

---

## 7. Quest Final Fase 2

### `q_f2_final` — Menuju Arc Final

```json
{
  "id": "q_f2_final",
  "title": "Titik Balik",
  "arc": "konvergensi_fase2",
  "kind": "main",
  "summary": "Chen Xu berdiri di persimpangan jalan. Apa yang akan kau lakukan dengan kekuatan yang kau bangun?",
  "objective": {
    "kind": "choose",
    "options": [
      {
        "label": "Bangun gerakan reformasi — ubah sistem dari dalam (Jalan Pahlawan)",
        "value": "jalan_reformer",
        "requirement": {"morality_min": 20}
      },
      {
        "label": "Kumpulkan kekuatan untuk menghancurkan segalanya (Jalan Destroyer)",
        "value": "jalan_destroyer",
        "requirement": {"morality_max": -20}
      },
      {
        "label": "Tinggalkan dunia ini, cari jalan ascension (Jalan Pelarian)",
        "value": "jalan_ascetic"
      },
      {
        "label": "Ambil tahta dan perbaiki satu per satu (Jalan Raja)",
        "value": "jalan_raja",
        "requirement": {"flag": {"key": "kaisar_status", "value": "kosong"}}
      }
    ],
    "hint": "Pilihan ini menentukan ending tree di Fase 3."
  },
  "next": [],
  "on_complete": {
    "effects": [
      {"type": "flag", "key": "fase2_selesai", "value": true},
      {"type": "flag", "key": "ending_tree_unlocked", "value": true}
    ],
    "system_msg": "[Sistem] Jalanmu telah ditetapkan. Fase berikutnya: perang sesungguhnya.",
    "rewards": {"exp": 100, "gold": 100},
    "unlock_arc": "fase3_final"
  }
}
```

---

## 8. Data Baru yang Diperlukan

### 8.1 File JSON Baru

| File | Isi | Baris Estimasi |
|------|-----|----------------|
| `data/quests/quests_sekte.json` | 8 quest Arc Sekte | ~400 |
| `data/quests/quests_kekaisaran.json` | 10 quest Arc Kekaisaran | ~500 |
| `data/quests/quests_f2_final.json` | 1 quest konvergensi | ~50 |
| `data/dialogs/dialogs_sekte.json` | Dialog NPC sekte | ~600 |
| `data/dialogs/dialogs_kekaisaran.json` | Dialog NPC istana | ~800 |
| `data/npcs_f2.json` | 8 NPC baru + 4 companion | ~200 |
| `data/locations_f2.json` | 12 lokasi baru (3 sekte + 6 istana + 3 rahasia) | ~300 |
| `data/memories_f2.json` | 4 ingatan baru (mem_05–08) | ~150 |

### 8.2 File CSV Baru

| File | Isi | Baris Estimasi |
|------|-----|----------------|
| `data/enemies_f2.csv` | 15 musuh baru (senior sekte, penjaga istana, assassin) | ~20 |
| `data/techniques_f2.csv` | 15 teknik baru (ranah 3–5) | ~20 |
| `data/items_f2.csv` | 20 item baru (pil langka, artefak sekte) | ~25 |
| `data/recipes_f2.csv` | 8 resep crafting baru | ~10 |

**Total Estimasi**: ~3.000 baris data baru (tanpa mengubah engine)

---

## 9. Testing Plan Fase 2

### 9.1 Test Coverage Target

| Kategori | Test Cases | Deskripsi |
|----------|-----------|-----------|
| **Quest Flow** | 24 | Semua quest main arc (sekte + kekaisaran + final) |
| **Branching** | 12 | Semua percabangan moral (3 di sekte × 4 di kekaisaran) |
| **Dialog** | 40 | Semua node dialog NPC baru |
| **Combat** | 15 | Battle vs musuh baru (termasuk boss sequence) |
| **Companion** | 8 | Multi-companion mechanics, combo techniques |
| **World-State Carryover** | 16 | Flags Fase 1 → dampak di Fase 2 |
| **Memory Gating** | 8 | Opsi dialog unlock via ingatan |
| **Integration** | 4 | Full playthrough (kombinasi cabang) |

**Total Test Cases Fase 2**: ~127 (ditambah ke 368 existing = **~495 total**)

### 9.2 Contoh Test Case

```python
def test_quest_sekte_05_branching():
    """Test q_sekte_05 membuka 3 cabang sesuai pilihan dialog."""
    state = new_game()
    state.flags["sekte_dipilih"] = True
    state.active_quest = "q_sekte_05"
    
    # Simpan state sebelum pilihan
    state_before = copy(state)
    
    # Pilih infiltrasi
    action = {"kind": "dialog_choice", "choice_id": "dlg_reaksi_eksperimen", "option": "opt_infil"}
    state = apply_action(state, action)
    
    assert state.active_quest == "q_sekte_06a"
    assert state.flags["branch_infil"] == True
    
    # Reset, pilih konfrontasi
    state = copy(state_before)
    action["option"] = "opt_konfr"
    state = apply_action(state, action)
    
    assert state.active_quest == "q_sekte_06b"
    assert state.flags["branch_konfr"] == True
```

---

## 10. Timeline Implementasi (Estimasi)

| Minggu | Tugas | Output |
|--------|-------|--------|
| **1** | Tulis quests JSON (sekte + kekaisaran) | 3 file quests.json |
| **2** | Tulis dialogs JSON (NPC sekte + istana) | 2 file dialogs.json |
| **3** | Tambah NPCs, locations, memories | 4 file data baru |
| **4** | Balance enemies, techniques, items | 4 file CSV baru |
| **5** | Tulis test cases (127 tests) | `tests/test_fase2/*.py` |
| **6** | Playtesting internal, fix bugs | Report playtest + hotfixes |
| **7** | Validasi data (tools/validate_data.py) | 100% pass 16 rules |
| **8** | Dokumentasi update (GDD, STORY_FASE2.md) | Dokumen final |

**Total Estimasi**: 8 minggu (2 bulan) untuk konten data-only

---

## 11. Kriteria Selesai Fase 2 (DoD)

- [ ] Semua quest Arc Sekte & Kekaisaran dapat diselesaikan tanpa softlock
- [ ] Semua percabangan moral berfungsi (min 3 playthrough untuk cover semua branch)
- [ ] World-state dari Fase 1 berdampak nyata di Fase 2 (flags carryover)
- [ ] 4 companion baru fully functional (combat + relationship)
- [ ] 4 ingatan baru (mem_05–08) unlock sesuai quest
- [ ] 127 test cases baru passing
- [ ] Validator data lolos 100%
- [ ] Playtest duration 3–4 jam per run
- [ ] Dokumentasi lengkap (STORY_FASE2.md, update GDD)

---

## 12. Catatan untuk Penulis Konten

1. **Tone Progression**: Fase 2 lebih gelap dari Fase 1 — transisi dari "akademi cerah" ke "politik kotor dewasa"
2. **Show, Don't Tell**: Revelasi cerita lewat dialog & ingatan, bukan exposition dump
3. **Player Agency**: Setiap pilihan harus terasa bermakna — hindari "illusion of choice"
4. **Consistency**: Karakter Fase 1 (Gu Canghai, Su Qing, Han Xiu) bisa muncul cameo, tapi jangan dominasi
5. **Pacing**: Jangan rush ending — biarkan pemain merasakan berat setiap keputusan moral
6. **Bahasa**: Tetap Bahasa Indonesia + Pinyin untuk istilah (disahkan GDD §13-5)

---

## 13. Referensi Silang

- **GDD.md**: §3 (struktur naratif), §4 (quest DAG), §12 (roadmap)
- **ENGINE_ARCHITECTURE.md**: §5 (schema quest), §6 (schema dialog), §9 (cultivation system)
- **STORY_FASE1.md**: §3 (tokoh), §4 (ingatan), §7 (quest mapping)
- **Data Existing**: `data/quests/quests_akademi.json` (template structure)

---

**Dokumen ini siap dijadikan spesifikasi implementasi.** Engine sudah mendukung semua fitur yang dibutuhkan — tinggal isi konten data sesuai schema yang ada.
