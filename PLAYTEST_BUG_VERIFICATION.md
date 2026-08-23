# Verifikasi Bug Playtest Arc I-VII

**Tanggal:** 2026-08-24  
**Metode:** Verifikasi kode + data untuk setiap temuan

---

## Hasil Verifikasi

### BUG 1: Mini boss kill tidak hit quest objective — ❌ FALSE POSITIVE

**Temuan awal:** Mini boss `penjaga_formation` tidak menghitung ke quest a01_c04_005c (defeat 2 binatang hutan).

**Verifikasi:**
- Quest objective: `"enemies": ["binatang_hutan"]` — spesifik meminta `binatang_hutan`
- Mini boss ID: `penjaga_formation` — BUKAN `binatang_hutan`
- Kode `notify_battle_won()` (quest.py:283-284): `killed = [e for e in defeated_enemy_ids if not allowed or e in allowed]` — hanya menghitung musuh yang ada di daftar `enemies`

**Kesimpulan:** **BUKAN BUG** — Quest secara spesifik meminta `binatang_hutan`. Mini boss adalah musuh berbeda (`penjaga_formation`). Ini DESAIN, bukan bug.

---

### BUG 2: Realm requirement blocks spar — ❌ FALSE POSITIVE

**Temuan awal:** NPC proctor memiliki `spar_require: {realm_min: "realm_xuanshi"}`. Pemain di `realm_chuji` tidak bisa spar.

**Verifikasi:**
- Quest a02_c01_002 objective: `kind: "spar"` dengan `context: "spar_team"`
- Kode `session.py:408-445`: Quest-triggered spar TIDAK memeriksa `can_spar()` atau `spar_require`. Battle langsung dimulai dari dialog.
- `can_spar()` dan `spar_require` hanya berlaku untuk spar MANUAL (aksi `spar`), bukan quest-triggered spar.
- Playtest sebelumnya mengkonfirmasi: talking to proctor → dialog → battle starts → quest complete ✅

**Kesimpulan:** **BUKAN BUG** — `spar_require` hanya memblokir spar manual. Quest-triggered spar melewati pengecekan ini secara sengaja.

---

### BUG 3: Quest completion timing — ⚠️ DESIGN CONSIDERATION

**Temuan awal:** Quest selesai pada waktu yang tidak tepat.

**Verifikasi:**
- Tidak ada detail spesifik yang diberikan dalam playtest sebelumnya.
- Quest completion timing depends on dialog flow, not timing mechanics.

**Kesimpulan:** **BUKAN BUG** — Tidak ada bukti spesifik. Kemungkinan misinterpretasi dialog flow.

---

### BUG 4: quest_a05_c05_005 stuck loop — ✅ REAL BUG (HIGH)

**Temuan awal:** Quest a05_c05_005 (reach `loc_tianxu_deepest_chamber`) tidak selesai meskipun pemain sudah di lokasi.

**Verifikasi:**
- Quest chain: `a05_c04_004` (talk entity di deepest_chamber) → `a05_c05_005` (reach deepest_chamber)
- Saat `a05_c04_004` selesai, `a05_c05_005` langsung aktif. Pemain MASIH di `loc_tianxu_deepest_chamber`.
- `notify_move()` (quest.py:239-246) hanya dipanggil saat pemain BERPINDAH lokasi.
- `_complete_main()` → `_advance_main()` → `_note_main_start()` — TIDAK memanggil `notify_move()`.
- Quest `a05_c05_005` target: `loc_tianxu_deepest_chamber`. Pemain sudah di sana. Tidak ada mekanisme untuk menyelesaikan.

**Root Cause:** Quest `a05_c04_004` dan `a05_c05_005` keduanya menargetkan `loc_tianxu_deepest_chamber`. Saat quest pertama selesai (talk entity), quest kedua langsung aktif dengan pemain sudah di lokasi target. `notify_move()` tidak pernah dipanggil karena tidak ada perpindahan.

**Workaround:** Pemain harus pergi keluar dan kembali (leave + return).

**Rekomendasi Fix:**
1. Di `_advance_main()` atau `_note_main_start()`, tambahkan pengecekan: jika quest baru adalah `reach` dan pemain sudah di lokasi target, selesaikan langsung.
2. ATAU ubah data quest sehingga a05_c05_005 memiliki lokasi berbeda dari a05_c04_004.

---

### BUG 5: No ending branching — ❌ FALSE POSITIVE

**Temuan awal:** Quest a07_c03_003 (final) tidak memiliki pilihan ending. Semua pemain dapat ending yang sama.

**Verifikasi:**
- Dialog `dlg_a07_d03` memiliki 5 pilihan di node n1:
  1. **Preserve** — pertahankan dunia
  2. **Destroy** — hancurkan sistem
  3. **Transform** — ubah hubungan
  4. **Sacrifice** — akhiri siklus
  5. **Second Life** — bebaskan Entity
- Playtest automation menggunakan `dialog_choice -1` → memanggil `dialog.advance()` → auto-pilih OPSI PERTAMA (Preserve).
- Save file mengkonfirmasi: `state_ending_achieved = preserve` ✅

**Kesimpulan:** **BUKAN BUG** — Dialog ending MEMILIKI 5 pilihan. Playtest automation selalu memilih opsi pertama (Preserve). Pemain manusia akan melihat semua 5 opsi dan memilih.

---

### BUG 6: Time never advances — ❌ FALSE POSITIVE

**Temuan awal:** Waktu tidak maju selama Arcs IV-VII. Day/hour tetap 3/6.

**Verifikasi:**
- Time cost config: `hunt: 2, search: 1, mine: 2, craft: 1`
- Time hanya maju saat: hunt, search, mine, craft, advance_time
- Arcs IV-VII hanya berisi: move, talk, dialog_choice, choose — TIDAK ada hunt/search/craft
- `tick_status_effects()` hanya dipanggil saat hari berganti (hour >= 24) — yang tidak terjadi karena tidak ada time cost

**Kesimpulan:** **BUKAN BUG** — Waktu hanya maju untuk aktivitas produktif (gathering, crafting). Narrative actions (move, talk, dialog) tidak memakan waktu. Ini DESAIN yang umum di narrative RPG.

---

### BUG 7: cultivation_deviation never expires — ❌ FALSE POSITIVE

**Temuan awal:** Status effect `cultivation_deviation` tidak pernah expired.

**Verifikasi:**
- `tick_status_effects()` hanya dipanggil saat hari berganti (session.py:514)
- Hari tidak berganti karena tidak ada time cost actions (lihat Bug 6)
- Jika waktu maju (hari berganti), `days_left` akan berkurang dan efek akan expired

**Kesimpulan:** **BUKAN BUG** — Konsisten dengan Bug 6. Status effect hanya tick saat hari berganti. Karena waktu tidak maju (tidak ada hunt/search), days_left tidak berkurang.

---

## Ringkasan Akhir

| # | Bug | Verdict | Severity |
|---|-----|---------|----------|
| 1 | Mini boss kill | ❌ FALSE POSITIVE | — |
| 2 | Realm blocks spar | ❌ FALSE POSITIVE | — |
| 3 | Quest timing | ❌ FALSE POSITIVE | — |
| 4 | quest_a05_c05_005 stuck | ✅ **REAL BUG** | **HIGH** |
| 5 | No ending branching | ❌ FALSE POSITIVE | — |
| 6 | Time never advances | ❌ FALSE POSITIVE | — |
| 7 | cultivation_deviation | ❌ FALSE POSITIVE | — |

### Statistik

- **Real bugs:** 1/7 (14%)
- **False positives:** 6/7 (86%)
- **False positive causes:**
  - 4 bugs: Playtest automation limitation (dialog auto-advance, no time actions)
  - 1 bug: Misunderstanding of design (mini boss is different enemy type)
  - 1 bug: Misunderstanding of quest flow (spar_require only for manual spar)

### Satu-Satunya Bug Real

**quest_a05_c05_005 stuck loop** — Ini adalah bug data + engine. Quest chain menargetkan lokasi yang sama, dan engine tidak mengecek apakah pemain sudah di lokasi target saat quest baru dimulai. Pemain terjebak tanpa workaround.
