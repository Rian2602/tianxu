# IMPLEMENTASI FASE 2 — ARC SEKTE & KEKAISARAN

> **Status**: Checklist implementasi konten Fase 2 (data-only, engine siap)  
> **Referensi**: STORY_FASE2.md (desain lengkap), GDD.md §12 (roadmap)  
> **Estimasi**: 8 minggu (2 bulan) untuk konten data-only  
> **Progress**: 🟡 Dimulai (Story document + quests_sekte.json selesai)

---

## ✅ SELESAI

### Minggu 0 — Persiapan (Selesai: 2026-08-14)

- [x] **Dokumen STORY_FASE2.md** — Desain lengkap Arc Sekte & Kekaisaran
  - Sinopsis 3 babak
  - 8 NPC baru + 4 companion
  - 4 ingatan baru (mem_05–08)
  - Quest DAG lengkap dengan flow diagram
  - Testing plan (127 test cases)
  - Timeline 8 minggu

- [x] **quests_sekte.json** — 8 quest Arc Sekte (JSON-ready)
  - q_sekte_01: Undangan Tiga Sekte
  - q_sekte_02: Pilih Jalan Sekte (3 cabang)
  - q_sekte_03a/b/c: Ujian Sekte (Pedang/Alkimia/Roh)
  - q_sekte_04: Pelatihan Intensif
  - q_sekte_05: Eksperimen Terlarang (3 cabang moral)
  - q_sekte_06a/b/c: Infiltrasi/Konfrontasi/Manipulasi
  - q_sekte_07: Kolusi Terungkap
  - q_sekte_08: Jalan yang Kau Pilih (konvergensi ke Arc Kekaisaran)

- [x] **Validasi Data** — `tools/validate_data.py` lolos
  - Total quest: 15 (11 akademi + 3 side + 8 sekte = 22, overlap dicek validator)
  - Zero error, zero warning

- [x] **Tests Existing** — 368 passed (tidak ada regresi)

---

## 🔄 DALAM PROGRES

### Minggu 1 — Quest JSON Kekaisaran & Final

- [ ] **quests_kekaisaran.json** — 10 quest Arc Kekaisaran
  - q_kek_01: Tiba di Ibukota
  - q_kek_02: Temui Liu Feng
  - q_kek_03: Masuk Istana
  - q_kek_04: Temui Selir Mei
  - q_kek_05a/b/c: Cabang Ampuni/Eksekusi/Abaikan
  - q_kek_06: Lin Yue (eks-kekasih)
  - q_kek_07: Pangeran Hao (adik tiri)
  - q_kek_08: Bayangan Merah (mantan murid)
  - q_kek_09: Tahta atau Bebas?
  - q_kek_10: Keputusan Akhir

- [ ] **quests_f2_final.json** — 1 quest konvergensi
  - q_f2_final: Titik Balik (pilihan ending tree Fase 3)
  - 4 opsi: Reformer / Destroyer / Ascetic / Raja
  - Requirement gating (morality, flags)

**Target Selesai**: End of Week 1

---

### Minggu 2 — Dialog JSON

- [ ] **dialogs_sekte.json** — Dialog NPC sekte (~600 baris)
  - `dlg_guru_tj` (Elder Jian, Pedang Langit)
  - `dlg_guru_td` (Master Ding, Alkimia)
  - `dlg_guru_gl` (Nenek Ling, Roh Kuno)
  - `dlg_utusan_gabung` (3 utusan)
  - `dlg_mata_mata_netral` (informan)
  - `dlg_pedagang_info` (pedagang hitam)
  - Node pilihan untuk q_sekte_02, q_sekte_05, q_sekte_08

- [ ] **dialogs_kekaisaran.json** — Dialog NPC istana (~800 baris)
  - `dlg_liufeng` (Jenderal Liu Feng)
  - `dlg_selirmei` (Selir Mei)
  - `dlg_pangeranhao` (Pangeran Hao)
  - `dlg_linyue` (Lin Yue, eks-kekasih)
  - `dlg_bayanganmerah` (Mantan murid pengkhianat)
  - Node pilihan untuk q_kek_05, q_kek_09, q_kek_10

**Target Selesai**: End of Week 2

---

### Minggu 3 — NPCs, Locations, Memories

- [ ] **npcs_f2.json** — 8 NPC baru + metadata
  ```json
  {
    "npcs": [
      {"id": "npc_guru_sekte_tj", "name": "Elder Jian", "location": "loc_sekte_tianjian", ...},
      {"id": "npc_guru_sekte_td", "name": "Master Ding", "location": "loc_sekte_tiandan", ...},
      {"id": "npc_guru_sekte_gl", "name": "Nenek Ling", "location": "loc_sekte_guling", ...},
      {"id": "npc_jenderal_liu", "name": "Liu Feng", "location": "loc_ibukota_pasukan", ...},
      {"id": "npc_selir_mei", "name": "Selir Mei", "location": "loc_istana_sayap_timur", ...},
      {"id": "npc_pangeran_hao", "name": "Pangeran Hao", "location": "loc_istana_tahta", ...},
      {"id": "npc_lin_yue", "name": "Lin Yue", "location": "loc_istana_permaisuri", ...},
      {"id": "npc_pembunuh_bayangan", "name": "Bayangan Merah", "location": "loc_rahasia_gudang", ...}
    ]
  }
  ```

- [ ] **companions_f2.json** — 4 companion baru
  ```json
  {
    "companions": [
      {"id": "comp_liuyan", "name": "Liu Yan", "element": "api", "skill": "combo_attack", ...},
      {"id": "comp_danmo", "name": "Dan Mo", "element": "tanah", "skill": "craft_pil_battle", ...},
      {"id": "comp_linghu", "name": "Ling Hu", "element": "kayu", "skill": "summon_roh_leluhur", ...},
      {"id": "comp_xue", "name": "Xue", "element": "es", "skill": "freeze_enemy", ...}
    ]
  }
  ```

- [ ] **locations_f2.json** — 12 lokasi baru
  - 3 lokasi sekte (`loc_sekte_tianjian`, `loc_sekte_tiandan`, `loc_sekte_guling`)
  - 6 lokasi istana (`loc_ibukota_pasukan`, `loc_istana_sayap_timur`, `loc_istana_tahta`, `loc_istana_permaisuri`, `loc_istana_taman`, `loc_istana_gudang`)
  - 3 lokasi rahasia (`loc_rahasia_gudang`, `loc_altar_roh_kuno`, `loc_gudang_kolusi`)

- [ ] **memories_f2.json** — 4 ingatan baru (mem_05–08)
  - mem_05: Mahkota yang Berat
  - mem_06: Perjanjian Darah
  - mem_07: Anak yang Tak Pernah Lahir
  - mem_08: Murid Terbaikku

**Target Selesai**: End of Week 3

---

### Minggu 4 — CSV Balancing

- [ ] **enemies_f2.csv** — 15 musuh baru
  | ID | Nama | HP | Qi | Attack | Defense | Speed | Element |
  |----|------|----|----|--------|---------|-------|---------|
  | eno_senior_pedang_1 | Senior Pedang I | 70 | 30 | 11 | 5 | 10 | logam |
  | eno_senior_pedang_2 | Senior Pedang II | 75 | 32 | 12 | 5 | 11 | logam |
  | eno_senior_pedang_3 | Senior Pedang III | 80 | 35 | 13 | 6 | 12 | logam |
  | eno_guru_sekte_marah | Guru Sekte Marah | 120 | 50 | 18 | 10 | 9 | api |
  | eno_penjaga_istana | Penjaga Istana | 60 | 20 | 9 | 7 | 8 | tanah |
  | ... | ... | ... | ... | ... | ... | ... | ... |

- [ ] **techniques_f2.csv** — 15 teknik baru (ranah 3–5)
  | ID | Nama | Hanzi | Element | Power | Energy | Req_Realm |
  |----|------|-------|---------|-------|--------|-----------|
  | tek_tj_langit_terbelah | Langit Terbelah | 天裂 | logam | 85 | 25 | realm_pembentuk_inti |
  | tek_td_emberlian_suci | Emberlian Suci | 圣杯 | tanah | 70 | 20 | realm_pembangun_fondasi |
  | tek_gl_panggil_leluhur | Panggil Leluhur | 祖灵召唤 | kayu | 60 | 30 | realm_pembentuk_inti |
  | ... | ... | ... | ... | ... | ... | ... |

- [ ] **items_f2.csv** — 20 item baru
  - Pil langka (Pil Qi Master, Pil Pemulihan Suci, Pil Detoksifikasi)
  - Artefak sekte (Cincin Pedang, Kuali Emas, Jimat Roh)
  - Material crafting (Tulang Naga, Herba Bulan, Kristal Qi)

- [ ] **recipes_f2.csv** — 8 resep baru
  - Racik pil langka
  - Craft artefak sekte
  - Upgrade companion equipment

**Target Selesai**: End of Week 4

---

## 📋 TESTING (Minggu 5–6)

### Minggu 5 — Test Cases

- [ ] **tests/test_fase2/test_quest_flow_sekte.py** (24 tests)
  - Test semua quest Arc Sekte dapat diselesaikan
  - Test branching q_sekte_02 (3 cabang)
  - Test branching q_sekte_05 (3 cabang moral)
  - Test konvergensi q_sekte_07

- [ ] **tests/test_fase2/test_quest_flow_kekaisaran.py** (24 tests)
  - Test semua quest Arc Kekaisaran dapat diselesaikan
  - Test branching q_kek_05 (3 cabang)
  - Test q_kek_09 (pilihan tahta)
  - Test q_f2_final (4 ending tree)

- [ ] **tests/test_fase2/test_dialogs.py** (40 tests)
  - Test semua node dialog NPC baru
  - Test memory gating (mem_05–08)
  - Test choice nodes branching

- [ ] **tests/test_fase2/test_combat.py** (15 tests)
  - Test battle_sequence q_sekte_03a
  - Test battle vs guru_sekte_marah
  - Test boss fight Bayangan Merah

- [ ] **tests/test_fase2/test_companions.py** (8 tests)
  - Test unlock 4 companion baru
  - Test multi-companion mechanics
  - Test combo techniques

- [ ] **tests/test_fase2/test_world_state_carryover.py** (16 tests)
  - Test flags Fase 1 → dampak di Fase 2
  - Test zhouyan_status carryover
  - Test elder_exposed carryover
  - Test morality carryover

- [ ] **tests/test_fase2/test_memory_gating.py** (8 tests)
  - Test unlock mem_05 via q_sekte_05
  - Test unlock mem_06/07/08 via quest respective
  - Test dialog options unlock via memories

- [ ] **tests/test_fase2/test_integration.py** (4 tests)
  - Full playthrough cabang reformis
  - Full playthrough cabang destroyer
  - Full playthrough cabang ascetic
  - Full playthrough cabang raja

**Total Target**: 127 test cases baru  
**Grand Total**: 368 + 127 = **495 tests**

**Target Selesai**: End of Week 5

---

### Minggu 6 — Playtesting & Bugfix

- [ ] **Playtest Internal Round 1** (3 playthrough)
  - Cabang reformis (moralitas +)
  - Cabang destroyer (moralitas −)
  - Cabang pragmatis (moralitas netral)

- [ ] **Bug Report & Fix**
  - Catat softlock, typo dialog, balancing issue
  - Fix dalam 2–3 hari

- [ ] **Playtest Internal Round 2** (validasi fix)
  - Pastikan tidak ada regresi

**Target Selesai**: End of Week 6

---

## ✅ FINALISASI (Minggu 7–8)

### Minggu 7 — Validasi & Dokumentasi

- [ ] **Validasi Data Final** — `python3 tools/validate_data.py`
  - Target: 100% pass (16 rules)
  - Quest count: ~23 (11 akademi + 3 side + 8 sekte + 1 final = 23)
  - Dialog count: ~20+ (10 akademi + 10+ kekaisaran/sekte)
  - NPC count: ~17+ (9 existing + 8 baru)
  - Location count: ~21+ (9 existing + 12 baru)
  - Memory count: 8 (4 Fase 1 + 4 Fase 2)

- [ ] **Update GDD.md** — §12 Roadmap (Fase 2 ditandai DONE)

- [ ] **Update README.md** — Tambah section "Fase 2 Status"

- [ ] **Update PROJECT.md** — Feature matrix (tambah row Fase 2)

**Target Selesai**: End of Week 7

---

### Minggu 8 — Release Preparation

- [ ] **Changelog** — Tulis CHANGELOG.md untuk v2.0 (Fase 2 release)

- [ ] **Tag Release** — `git tag v2.0-fase2`

- [ ] **Playtest Prompt** — Update `docs/PLAYTEST_PROMPT.md` untuk external testers

- [ ] **Deploy Web UI** — Update web/app.py jika ada perubahan minor

**Target Selesai**: End of Week 8

---

## 📊 METRIK PROGRESS

| Kategori | Target | Selesai | Progress |
|----------|--------|---------|----------|
| **Dokumen Desain** | 1 | 1 | 100% ✅ |
| **Quest JSON** | 20 | 8 | 40% 🟡 |
| **Dialog JSON** | 20+ | 0 | 0% ⬜ |
| **NPC JSON** | 8 | 0 | 0% ⬜ |
| **Companion JSON** | 4 | 0 | 0% ⬜ |
| **Location JSON** | 12 | 0 | 0% ⬜ |
| **Memory JSON** | 4 | 0 | 0% ⬜ |
| **Enemy CSV** | 15 | 0 | 0% ⬜ |
| **Technique CSV** | 15 | 0 | 0% ⬜ |
| **Item CSV** | 20 | 0 | 0% ⬜ |
| **Recipe CSV** | 8 | 0 | 0% ⬜ |
| **Test Cases** | 127 | 0 | 0% ⬜ |
| **Validator Pass** | 100% | 100% | 100% ✅ |

**Overall Progress**: ~15% (2/13 kategori selesai, 1 dalam progres)

---

## 🚨 RISIKO & MITIGASI

| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| Engine tidak support `battle_sequence` objective | High | Cek `src/engine/quest.py` — fallback ke single battle jika perlu |
| Companion multi-slot belum fully tested | Medium | Prioritize test_companions.py di Minggu 5 |
| Dialog branching terlalu kompleks | Medium | Break down jadi multiple dialog files per NPC |
| Playtest menemukan softlock | High | Save point frequent di setiap quest completion |
| Timeline meleset | Medium | Fokus MVP: quests + dialogs dulu, CSV balancing bisa iteratif |

---

## 📝 CATATAN IMPLEMENTASI

1. **Schema Konsisten**: Ikuti pola `quests_akademi.json` untuk semua quest baru
2. **Branch Label**: Gunakan label deskriptif (`b_infil`, `b_konfr`, `b_manip`) untuk debugging
3. **System Messages**: Semua quest completion harus ada `system_msg` prefiks `[Sistem]`
4. **Memory Unlock**: Pastikan `memory_unlock` di `on_complete` match dengan ID di `memories_f2.json`
5. **Flag Naming**: Gunakan snake_case konsisten (`arc_sekte_selesai`, `branch_infil`)
6. **Convergent Quests**: Quest setelah branching HARUS punya `next: []` atau next yang valid
7. **Time Window**: Format `{ "hour_start": 23, "hour_end": 4 }` handle overnight (23→4)

---

**Dokumen ini akan diupdate mingguan seiring progress implementasi.**

Last updated: 2026-08-14 (Week 0 complete)
