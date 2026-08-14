# Changelog

Semua perubahan penting pada **Tian Xu: Second Life**.

## [Unreleased]

### Added
- File standar repo profesional: `.editorconfig`, `.gitattributes`, `CONTRIBUTING.md`, `SECURITY.md`.
- Packaging: `pyproject.toml` kini punya `[build-system]` (setuptools), `[project.urls]`, dan console script `tianxu` (`python -m pip install -e .` lalu jalankan `tianxu`).
- README: badge Python 3.12, lisensi MIT, status CI; seksi Dokumentasi & Kontribusi.

### Fixed
- Batch audit `docs/list_bug.md` (diverifikasi): guard `pending_dialog` simetris battle (F2), body API non-objek → 400 (F1), teknik lintas ranah ditolak via `realm_required` (H4), jadwal NPC lintas tengah malam (A1), berburu data-driven `world.hunt` (A2), spar kalah = quest selesai + dialog berbeda (G4a), world-facts cabang untuk kontinuitas Arc 2 (G4b/#10), reaksi NPC untuk cabang 3ab (G4c), q07 pasca-konfrontasi 3aa (G4f), penutup tematik cabang 3b (B2), choice illusion konfrontasi (J3#6), lock server web (K4), breakpoint responsif (I1#9).
- Konten: `system_msg` prematur q06 dihapus (B1); opsi "(Tidak menjawab)" dihapus — cabang 3b wajib lewat tawaran berbayar (G4d); flag `branch_3aa` membocorkan dialog konfrontasi ke 3ab diperbaiki (G4e); dialog Gu Canghai tetap terbuka setelah konsolasi kalah.
- Toko (laporan pemain, UX1): tab Jual menjelaskan item yang belum dimiliki — baris "Belum punya" tanpa tombol + hint; `Cache-Control: no-cache` untuk aset statis agar perbaikan frontend selalu termuat.
- **Fitur GDD P1** (plan `docs/superpowers/plans/2026-08-14-p1-fitur-gdd-belum-dibangun.md`): hubungan NPC berdampak pada dialog (P1-2 — kondisi `relation_min/max`, `spar_win_relation`, node gated Han Xiu/Gu Canghai); gating ingatan membuka opsi dialog (P1-1 — kondisi `memory`, menutup B3/#13); tipe musuh beragam + pool berburu malam (P1-3 — `night_pool`/`night_window`, 2 musuh baru).
- **Rampungkan Arc Akademi — Tahap A** (plan `docs/superpowers/plans/2026-08-14-rampungkan-arc-akademi-tahap-a.md`): playthrough end-to-end 3 akademi (tutup DoD §11.2 #1); keputusan playtest §17 — `turn_order: "speed"` (urutan giliran berbasis speed), reward quest q3 diturunkan (exp 8→4), side quest defeat butuh lapor (`report_to`), cap exp grinding harian (`daily_grind_exp_cap` 60).
- **Rampungkan Arc Akademi — Tahap B FULL (engine adaptif)** (plan `docs/superpowers/plans/2026-08-14-rampungkan-arc-akademi-tahap-b.md`): 0 hardcode arc-1 di `src/` — (B1) `arc_summary` data-driven via `config.arcs` (final_quest/title/teaser/memories_total/branches, arc terakhir selesai yang tampil); (B2) respawn KO via `world.safe_fallback_location` → lokasi `is_safe` pertama data; (B3) banner CLI dipicu `arc_summary` (bukan flag literal); (B4) teknik lintas akademi via kolom opsional `unlock_arc` di `techniques.csv` (GDD §5.2). Arc berikutnya = data saja, tanpa ubah engine.
- **Rampungkan Arc Akademi — Tahap C Task C1** (plan `docs/superpowers/plans/2026-08-14-rampungkan-arc-akademi-tahap-c.md`): teknik **dipelajari & ditingkatkan** (GDD §7) — efek `technique` memberi teknik baru dari quest/dialog (data-driven, single & list, dedup); `player.techniques`/`technique_levels` diserialisasi (save round-trip); aksi `upgrade_technique` di titik aman (biaya `technique_upgrade_cost_base` 20 × level, batas `order` ranah + 1 — deviasi dari plan: `technique_slots` ranah awal = 1 tak memberi ruang upgrade); power battle naik per level (`technique_power_growth_per_level` 0.15); CLI `tingkatkan <teknik>` + panel web (level + tombol Tingkatkan). Validator: `EFFECT_TYPES` + `technique` (aturan 13, quest & dialog) + config upgrade (aturan 7) — jumlah aturan tetap 16.
- **Rampungkan Arc Akademi — Tahap C Task C2** (plan yang sama): **siklus waktu — bulan** (GDD §7) — `state.month`/`month_name` **derived** dari `day` (`config.time.month_length_days` 30 + `month_names` 12; `(day−1)//mld+1`, kompatibel save lama tanpa migrasi — deviasi 1 baris: formula plan `day//mld+1` off-by-one di kelipatan persis); kondisi dialog `month_min/max` (AND, pola `_eval_condition`); `view().month`/`month_name` + header CLI (`Bulan X — Hari Y, jam Z`) & web. Validator: aturan 7 (month_length > 0, month_names = 12) + kondisi dialog month 1..12.
- **Rampungkan Arc Akademi — Tahap C Task C3** (plan yang sama): **moralitas → penentu ending — scaffold data-driven** (GDD §3.4/§9) — `config.arcs[].endings` opsional `{id, title, desc, condition}`; `view().arc_summary.ending` = ending pertama yang kondisinya cocok (first-match AND, `_eval_condition` dipakai ulang) atau `None`; arc akademi **tanpa endings** (kontrak view utuh, non-breaking); CLI banner + modal web menampilkan ending bila ada; 3 ending tematik (Reformer/Destroyer/Ascetic) siap diisi arc final. Validator aturan 7: id unik/title string/condition hanya kunci kondisi dikenal (`_check_dialog_condition` — `mood_min` dsb. ditolak).
- Dokumentasi: `docs/list_bug.md` (status perbaikan terverifikasi + fitur P1), 5 plan implementasi (`docs/superpowers/plans/`), sinkronisasi ENGINE_ARCHITECTURE / STORY_FASE1 / DESIGN_SUMMARY / README / PROJECT.

### Changed
- Jumlah test: 192 → **250**; validator 16 aturan tetap exit 0 (aturan 7 & 13 diperluas: `arcs`/`safe_fallback_location`/`unlock_arc`; aturan 14 wajib ≥1 lokasi `is_safe`; upgrade teknik & efek `technique` (C1); time month + kondisi dialog month (C2); endings arc + kunci kondisi tak dikenal ditolak (C3)).
- `README.md` & `PROJECT.md`: jumlah test disinkronkan (250).

## [0.1.0-alpha] — 2026-08-14

### Added
- Vertical slice Fase 1: Arc Akademi playable penuh (CLI & Web UI).
- Engine: session, battle (elemen 五行, kritikal, kompanion), dialog bercabang, kultivasi, moralitas, ingatan, quest DAG.
- 3 akademi pilihan (Elemen/Senjata/Summoning) dengan `skill_pool` teknik.
- Web UI gelap-emas (`python3 web/app.py` → localhost:8000): menu Mulai Baru/Lanjut, panel Tianyuan Ling, battle, save/load.
- CI GitHub Actions (validate data + pytest).
- Lisensi MIT, README, pyproject.toml.

### Changed
- Rebalancing hasil playtest: exp quest & aktivitas diturunkan agar arc selesai di Lv.4–6 (sebelumnya Lv.10).
- Side quest tersedia sejak hari 1.

### Fixed
- Teknik lintas akademi ditolak di battle (validasi `skill_pool`).
- Meracik (craft) hanya di titik aman.
- Payload aksi web non-objek → 400; exception engine → respons JSON 500.
- HP kompanion persisten antar battle; KO → `istirahat` di titik aman.
