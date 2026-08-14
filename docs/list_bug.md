# Daftar Bug & Temuan — Audit terhadap Analisis Eksternal (2026-08-14)

> Hasil verifikasi statis klaim analisis pihak ketiga terhadap kode & data nyata.
> Verifikasi = baca langsung file:line; **tidak** menjalankan game/coverage ulang.
> Perbaikan **belum diterapkan** pada saat audit — hanya didokumentasikan.
>
> **Audit 1**: analisis ChatGPT (lihat §A–§D).
> **Audit 2**: analisis Grok (lihat §E).
> **Audit 3**: analisis Claude (lihat §F).
> **Audit 4**: analisis Grok engine/web/story (lihat §G).
> **Audit 5**: analisis ChatGPT engine (lihat §H).
> **Audit 6**: analisis ChatGPT web/frontend (lihat §I).
> **Audit 7**: analisis ChatGPT story layer (lihat §J).
> **Audit 8**: analisis Claude web/visual layer (lihat §K).
> **Audit 9**: analisis Claude story layer — bug naratif (lihat §L).

## Status perbaikan (diterapkan 2026-08-14, diperbarui 2026-08-14 lanjutan)

Sebagian bug aktif sudah diperbaiki — detail di bawah. Verifikasi: `tools/validate_data.py` lulus + `pytest` **222 passed**. Yang **tidak** dicantumkan di sini belum diperbaiki (desain/konten/defer).

| ID | Status | Ringkasan fix |
|----|--------|---------------|
| G1 | ✅ | `player_guard` jadi persen: guard=50, defend=`power` (60). `battle.py` |
| G2 | ✅ | `spar_npc = npc["id"]` (id penuh). `session.py` |
| G3a | ✅ | `context.loc_names` + label tombol Pindah. `web/app.py`, `app.js` |
| G3b | ✅ | `_tianyuan_payload` pakai `active_side()`. `web/app.py` |
| G3d | ✅ | **disempurnakan**: bukan reset variabel global — `localStorage "arc-seen:<save>"` per nama save (keputusan K2). `app.js` |
| F1 | ✅ | `_read_body` non-dict → `{}`. `web/app.py` |
| F2 | ✅ | guard `pending_dialog` simetris battle. `session.py` |
| F4 | ✅ | tertutup oleh fix F2 (jalur eksploitasi terblokir) |
| B1 | ✅ | hapus system_msg prematur q06. `quests_akademi.json` |
| G4e | ✅ | `node_konfrontasi` cond `jalur_3a` → `branch_3aa`. `dialogs_akademi.json` |
| H1 | ✅ | cek quest berbasis waktu disentralkan ke `_pass_time` (`notify_move` + `advance_time_target_met`); softlock `reach+time_window` q06 tertutup. `session.py` |
| H2 | ✅ | `resolve_choose` hanya menuntaskan quest bila opsi cocok (`matched`); opsi invalid ditolak + log. `quest.py` |
| H3 | ✅ | `pending_dialog` dibuang dari `to_dict`/`from_dict` (preventif crash save lama). `state.py` |
| K1 | ✅ | `.dialog-text` diberi `white-space: pre-wrap`. `style.css` |
| K2 | ✅ | lihat G3d (localStorage per save). `app.js` |
| K3 | ✅ | `act()`/`actShop()`/`startNew()` tampilkan `data.error`. `app.js` |
| K4 | ✅ | busy-flag frontend (anti double-click race). `app.js` |
| K5 | ✅ | endpoint `POST /api/save` dihapus (dead code + `ok:true` palsu); `.shop-content` diganti div polos. `web/app.py`, `app.js` |
| G4d | ✅ | opsi "(Tidak menjawab)" dihapus — 3b selalu lewat tawaran berbayar. `dialogs_akademi.json` |

Test baru/update: `test_spar_id_pendek_simpan_id_penuh`, `test_guard_pending_dialog_tolak_aksi_lain`, `test_body_non_dict_tidak_crash`, `test_tianyuan_tidak_menampilkan_main_quest_sebagai_side`, `test_context_loc_names`, `test_teknik_defend` (60%), `test_advance_time_menyelesaikan_reach_dalam_window`, `test_rest_memproses_quest_advance_time`, `test_resolve_choose_opsi_invalid_tidak_menuntaskan`, `test_pending_dialog_tidak_diserialisasi`.

**Batch berikutnya (2026-08-14, plan `docs/superpowers/plans/2026-08-14-fix-sisa-bug-dan-hardening.md`) — 209 test total:**

| ID | Status | Ringkasan fix |
|----|--------|---------------|
| H4 | ✅ | `realm_required` ditegakkan (`battle.py::_technique` + `loader.player_techniques(academy, realm)`). `battle.py`, `loader.py` |
| A1 | ✅ | `_is_npc_available` seragamkan pola `quest._in_window` (lintas tengah malam, batas `hour_end` eksklusif). `session.py` |
| J3#6 | ✅ | opsi "menuntut" `node_konfrontasi` dapat efek `morality +1` (choice illusion hilang). `dialogs_akademi.json` |
| #9 | ✅ | `@media (max-width:1023px)` menumpuk grid 3 kolom. `style.css` |
| A2 | ✅ | aktivitas berburu data-driven: `world.hunt` di config (pool/mini_boss/lokasi/item), validator aturan 7 diperluas. `config.json`, `session.py`, `validate_data.py` |

Test baru batch ini: `test_teknik_ranah_tinggi_ditolak`, `test_player_techniques_filter_ranah`, `test_jadwal_npc_lintas_tengah_malam`, `test_konfrontasi_pilihan_efek_beda`, `test_aturan7_world_hunt_referensi_tidak_ada`, `test_aturan7_world_hunt_chance_invalid`.

**Batch 3 (2026-08-14, Fase B + hardening; plan `docs/superpowers/plans/2026-08-14-fix-sisa-bug-dan-hardening.md`) — 210 test total:**

| ID | Status | Ringkasan fix |
|----|--------|---------------|
| G4b/#10 | ✅ | 4 world-facts sebagai `flags` (`zhouyan_status`, `bell_status`, `elder_exposed`, `academy_knows_truth`) diset di on_complete tiap cabang + q07. `quests_akademi.json` |
| G4c | ✅ | 3 node reaksi 3ab (Su Qing hangat, Han Xiu respect, Zhou Yan bersyukur). `dialogs_akademi.json` |
| G4f | ✅ | `node_truth_3aa` jadi konfirmasi pasca-konfrontasi (bukan reveal ulang). `dialogs_akademi.json` |
| B2 | ✅ | `node_penutup_3b` versi gelap dari payoff tematik. `dialogs_akademi.json` |
| G4a | ✅ | `notify_spar_loss`: kalah spar ujian = quest selesai + flag `spar_kalah` + dialog Gu Canghai beda (`node_kalah` lanjut `node_umum`; regresi tertutup). `quest.py`, `battle.py`, `dialogs_akademi.json` |
| K4-lock | ✅ | `threading.Lock` server web (new/load/action + GET tianyuan/state). `web/app.py` |
| UX1 | ✅ | laporan pemain: tab Jual toko menjelaskan item tak terjual — baris "Belum punya" tanpa tombol + hint; `Cache-Control: no-cache` untuk aset statis (fix frontend selalu termuat, tanpa hard-refresh). `app.js`, `style.css`, `web/app.py` |

Test baru batch ini: `test_reaksi_3ab`, `test_spar_kalah_tetap_selesai_dan_dialog_beda`, `test_static_no_cache` (plus perluasan `test_konvergensi_semua_cabang` dengan assertion world-facts per cabang).

**Batch 4 (2026-08-14, plan `docs/superpowers/plans/2026-08-14-p1-fitur-gdd-belum-dibangun.md`) — fitur GDD P1, 222 test total:**

| ID | Status | Ringkasan fix |
|----|--------|---------------|
| P1-2 | ✅ | hubungan NPC berdampak: kondisi dialog `relation_min`/`relation_max` (konsumen `state.relations` yang sebelumnya mati) + `cultivation.spar_win_relation` (spar menang +5) + 2 node gated (Han Xiu `node_tip_spar` ≥ 20, Gu Canghai `node_akui_latihan` ≥ 20). `dialog.py`, `battle.py`, `config.json`, `dialogs_akademi.json` |
| P1-1 | ✅ | **B3/#13 tertutup** — gating ingatan: kondisi `memory` membuka opsi dialog hanya setelah ingatan pulih (`dlg_moyun` `mem_02`, `dlg_gucanghai` `mem_01`). `dialog.py`, `dialogs_akademi.json` |
| P1-3 | ✅ | tipe musuh beragam: `world.hunt.night_pool` + `night_window` (19→6, pola `_in_window` lintas tengah malam) + 2 musuh baru (Pembelot Malam api, Ular Bayangan air); validator aturan 7 diperluas. `enemies.csv`, `config.json`, `session.py`, `validate_data.py` |

Test baru batch ini: `test_eval_condition_relation`, `test_pilihan_gated_relation`, `test_spar_menang_menaikkan_relation`, `test_hanxiu_tip_spar_saat_relation_tinggi`, `test_gucanghai_akui_latihan_saat_relation_tinggi`, `test_eval_condition_memory`, `test_pilihan_gated_memory`, `test_moyun_pilihan_ingatan_muncul_saat_q07`, `test_gucanghai_pilihan_ingatan_muncul`, `test_berburu_malam_memakai_pool_malam`, `test_aturan7_night_pool_referensi_tidak_ada`, `test_aturan7_night_window_tidak_valid`.

**Batch 5 (2026-08-14, plan `docs/superpowers/plans/2026-08-14-rampungkan-arc-akademi-tahap-c.md`) — Tahap C FULL, 251 test total:**

| ID | Status | Ringkasan fix |
|----|--------|---------------|
| C1 | ✅ | teknik **dipelajari & ditingkatkan** (GDD §7): efek `technique` (quest/dialog reward, single & list, dedup), `player.techniques`/`technique_levels` (save round-trip), aksi `upgrade_technique` (titik aman, biaya `technique_upgrade_cost_base` × level, batas `order` ranah + 1 — deviasi: `technique_slots` ranah awal = 1 tak memberi ruang upgrade), power battle naik per level (`technique_power_growth_per_level`), CLI `tingkatkan <teknik>` + panel web. Validator: `EFFECT_TYPES` + `technique` (aturan 13) + config upgrade (aturan 7). `effects.py`, `state.py`, `session.py`, `battle.py`, `loader.py`, `cli.py`, `web/`, `validate_data.py` |
| C2 | ✅ | **siklus waktu — bulan** (GDD §7): `state.month`/`month_name` **derived** dari `day` (`(day−1)//month_length_days+1` — deviasi 1 baris: formula plan `day//mld+1` off-by-one di kelipatan persis), kompatibel save lama tanpa migrasi; kondisi dialog `month_min/max` (AND); `view().month`/`month_name` + header CLI/web. Validator aturan 7: month_length > 0, month_names = 12, kondisi month 1..12. `state.py`, `dialog.py`, `session.py`, `cli.py`, `app.js`, `validate_data.py` |
| C3 | ✅ | **moralitas → penentu ending — scaffold data-driven** (GDD §3.4/§9): `config.arcs[].endings` opsional `{id, title, desc, condition}`; `arc_summary.ending` = ending pertama yang kondisinya cocok (first-match AND via `_eval_condition`) atau `None` (arc akademi tanpa endings — kontrak view utuh); CLI banner + modal web tampil ending. Validator aturan 7: id unik/title string/condition hanya kunci kondisi dikenal. `session.py`, `cli.py`, `app.js`, `validate_data.py` |
| C3-fix | ✅ | **temuan evaluasi (bug laten diekspos C3)**: `dialog.py::_eval_condition` sempat *early-return* pada kunci `flag` — kombinasi `flag` + kondisi lain (mis. `morality_min` di skema ending) mengabaikan kondisi lain. Kini flag = cek AND biasa; data dialog existing memakai flag tunggal (terverifikasi: tidak ada kondisi multi-kunci di `data/dialogs_akademi.json`) → tidak terpengaruh (playthrough CLI 15 hijau). +test negatif/positif AND. `dialog.py`, `test_dialog.py` |

Test baru batch ini: `test_apply_technique_single_dan_list`, `test_upgrade_technique_hanya_di_titik_aman_dan_batas_slots`, `test_teknik_power_scaling_per_level`, `test_aturan13_efek_technique_tidak_dikenal`, `test_aturan7_teknik_upgrade_config_tidak_valid`, `test_view_month_derived_dari_day`, `test_eval_condition_month_min_max`, `test_aturan7_month_length_dan_month_names_tidak_valid`, `test_aturan7_kondisi_month_dialog_tidak_valid`, `test_arc_summary_ending_data_driven`, `test_aturan7_ending_arc_tidak_valid`, `test_eval_condition_flag_tidak_mengabaikan_kondisi_lain`.

**Batch 6 (2026-08-14, plan `docs/superpowers/plans/2026-08-14-fix-temuan-audit-chatgpt.md`) — fix temuan audit ChatGPT, 266 test total:**

| ID | Status | Ringkasan fix |
|----|--------|---------------|
| A1 | ✅ | **CRITICAL — hang EXP ranah tertinggi**: `_breakthrough` gagal di ranah puncak mengembalikan level ke maks → `while exp >= exp_next` berulang (exp 1e9 ≈ 19 juta iterasi, hang praktis ratusan detik). Kini `_breakthrough`/`_level_up` mengembalikan `bool`; saat puncak exp dikembalikan & di-cap di bawah threshold + log "exp tertahan". Reproduksi exp 1e9: hang → **0.00s**. `cultivation.py` |
| A2+A3 | ✅ | **HIGH — objective talk longgar → 3aa salah urutan**: quest `talk` hanya cek `npc`, tak peduli node — konfrontasi 3aa muncul SETELAH quest selesai. Kini skema `talk` opsional `node`/`nodes` (node WAJIB dimainkan — cek keanggotaan semua node yang dikunjungi, bukan node terakhir) + `start_node` (dialog dipaksa mulai dari node itu saat quest aktif); `dialog.start(forced_node)` + `visited` set; validator aturan 4 cek node ada di dialog default NPC; data 3aa: konfrontasi terjadi SAAT quest berjalan. Test lama yang mengunci bug sebagai expected ditulis ulang. `quest.py`, `dialog.py`, `session.py`, `validate_data.py`, `quests_akademi.json` |
| A5 | ✅ | **advance_time overshoot**: cek lama `elapsed >= required AND hour >= target` — tunggu 30 jam dari Hari 1 19:00 (Hari 3 01:00) gagal `hour >= 20` → quest molor. Kini bandingkan waktu absolut `day*24+hour >= target_abs` — overshoot memenuhi. `quest.py` |
| A6 | ✅ | **skill_pool hanya elemen pertama**: `a.get("skill_pool", [""])[0]` — pool kedua tak pernah dibaca. Kini semua prefix diproses + dedup. `loader.py` |
| A7 | ✅ | **main quest defeat tanpa filter**: hanya cek `kind == "defeat"`. Kini ikut pola side quest — `enemies` didefinisikan → hanya musuh dari daftar yang memenuhi; tanpa field perilaku lama. `quest.py` |
| A8 | ✅ | **fallback hardcode hunt**: 5 literal id konten arc-1 (`loc_wilayah_berburu`, `eno_serigala_qi`, `eno_babi_hutan`, `eno_raja_serigala`, `material_herba`). Kini semua dari `config.world.hunt`; tanpa field itu aksi menolak dengan log aman. `session.py` |
| B1-B9 | ✅ | **polish web** (dalam batas GDD §12.5 — tanpa animasi/audio): hierarchy visual + semantic color (B1/B2), ranah hero stat + progress exp statis (B3), log speaker + separator scene (B4), dialog story card (B5), mobile naratif + drawer quest/inventori (B6), ornamen title SVG inline (B7), `:focus-visible` + focus trap modal + Escape (B8), feedback loading `is-loading` (B9). Tekstur aset pengguna (paper-dark, silk-dark, ink-wash, cloud-mist, gold-noise) dipakai halus via overlay gelap. `style.css`, `app.js`, `index.html` |
| C4 | ✅ | **ambience lokasi data-driven**: field opsional `ambience` per lokasi ∈ enum `config.world.ambiences` → gradient/tekstur latar statis web (body class `ambience-<x>`); `view().location.ambience`; validator aturan 14 tolak enum tak dikenal. `locations.json`, `config.json`, `session.py`, `validate_data.py`, `style.css`, `app.js` |

Test baru batch ini: `test_ranah_tertinggi_exp_dicap_tidak_hang`, `test_ranah_tertinggi_exp_raksasa_selesai_cepat`, `test_dialog_start_node_dipaksa`, `test_quest_talk_node_wajib`, `test_quest_talk_tanpa_node_perilaku_lama`, `test_3aa_konfrontasi_saat_quest_aktif`, `test_aturan4_talk_node_wajib_harus_ada_di_dialog`, `test_advance_time_overshoot_selesai`, `test_advance_time_dalam_window_masih_selesai`, `test_player_techniques_skill_pool_banyak_elemen`, `test_main_defeat_filter_enemies`, `test_main_defeat_tanpa_enemies_perilaku_lama`, `test_hunt_tanpa_config_ditolak_aman`, `test_aturan14_ambience_harus_enum_terdaftar`, `test_view_location_ambience`.

**Defer resmi tersisa**: tidak ada (B3/#13 tertutup oleh P1-1). **Defer C1-C3 plan dieksekusi (2026-08-14)**: C1 font self-host Noto Serif/Sans SC subset OFL (Latin + 16 Hanzi game, 1.4MB, offline) · C2 icon Lucide 15 SVG self-host ISC inline (stat + tombol, bukan emoji) · kompresi tekstur 14MB→3MB (downscale 2× + zlib 9, stdlib-only) · `do_HEAD` header-only RFC 9110. Keterangan subset font: Google Fonts TTF penuh = 10-14MB/file → dipilih subset woff2 (Hanzi di luar 16 karakter game jatuh ke fallback Georgia/sistem).

## A. Bug terverifikasi — kode

### A1. NPC schedule tidak mendukung lintas tengah malam (latent)
- Lokasi: `src/engine/session.py:155` (`_is_npc_available`)
- Kode: `if h_start <= self.state.hour <= h_end:` — tak menangani jadwal `19 → 06`.
- Pembanding: `src/engine/quest.py:123-128` (`time_window`) **sudah** menangani: `return h >= start or h < end`.
- Status: **latent** — tidak ada NPC di `data/npcs.json` yang memakai jadwal lintas tengah malam (semua `hour_start < hour_end`). Belum tercapai data, tapi inkonsisten dengan quest.
- Bonus: batas inklusif/eksklusif berbeda — NPC `<=` kedua ujung, quest `start <= h < end`.

### A2. Hardcode "false data-driven" pada aktivitas
- Lokasi: `src/engine/session.py:320-323` (`_hunt`): pool musuh hardcoded `["eno_serigala_qi", "eno_babi_hutan"]` + swap 10% `["eno_raja_serigala"]`.
- Bonus: `loc_wilayah_berburu` hardcoded di `_hunt`/`_search` (baris 317, 341); `material_herba` hardcoded di `_search` (baris 345).
- Konflik dengan prinsip ENGINE_ARCHITECTURE §2 (data-driven total) & §17 ("Arc baru = data, bukan rombak engine"). Technical debt untuk ekspansi.

### A3. Catatan: field `day` pada schedule NPC adalah data mati
- `_is_npc_available` (`session.py:148-157`) hanya membaca `hour_start`/`hour_end`, mengabaikan `day`.
- Semua schedule di data punya `"day": 1`. Sesuai keputusan ENGINE_ARCHITECTURE §17 ("NPC aktif tiap hari, tanpa softlock") — bukan bug, tapi data dokumentatif yang tak terpakai.

## B. Bug terverifikasi — konten/story

### B1. `system_msg` "Pola yang sama" premature & duplikat
- Lokasi: `data/quests/quests_akademi.json:102` pada `q_akademi_06` (insiden, **sebelum** pemain memilih sikap).
- Acuan desain: `docs/STORY_FASE1.md` §5 menempatkan kalimat *"Pola yang sama. Kau melihatnya, bukan?"* di **q5** = `q_akademi_07`.
- Payoff yang sama juga sudah ada di dialog q07 (`data/dialogs/dialogs_akademi.json:222`, `node_penutup`) → pesan di q06 prematur **dan** duplikat.

### B2. Cabang 3b melewatkan `node_penutup` (payoff tematik)
- Lokasi: `data/dialogs/dialogs_akademi.json:197-201` — `node_truth_3b` ber-`end: true`.
- 3aa/3ab/3c semuanya lanjut ke `node_penutup` (narasi "yang lemah dikorbankan untuk yang kuat"); di jalur 3b momen penutup ini hilang.
- Kemungkinan disengaja (jalur gelap menahan beat penebusan) — perlu keputusan desain, bukan asumsi.

### B3. Gap desain: gating ingatan → dialog belum ada
- STORY_FASE1 §3.1: "opsi dialog tertentu hanya muncul setelah ingatan terkait pulih".
- Engine dialog (`src/engine/dialog.py:118-152`) tak punya tipe kondisi `memory`; tak ada dialog yang meng-gate pilihan pada ingatan. Desain belum direalisasikan.

## C. Klaim analisis eksternal yang SALAH (jangan diikuti)

### C1. "q07 konvergensi terlalu kuat / branch bertemu dialog hampir sama"
- Disangkal kode: dialog q07 punya 4 varian per branch (`node_truth_3aa/3ab/3b/3c`) + `node_penutup` bersama.
- Pasca-q07 dunia tetap berbeda via dialog NPC: Su Qing `node_kecewa_3b/3c` & `node_hangat_3a`, Han Xiu `node_respect`, Zhou Yan `node_bersyukur`/`node_pahit`, Gu Canghai `node_akhir`. Konvergensi "pada tema" sudah terimplementasi.

### C2. "Sparing NPC hardcoded (hanxiu/gucanghai)"
- Salah: `_spar` (`session.py:299-314`) generik via field `can_spar` dari data; hanya ada id-shortening `f"npc_{nid}"`.

### C3. "Koreksi coverage 99,9% → 97%"
- Salah paham scope: docs eksplisit menulis "coverage `src/`" (`PROJECT.md:45`, `DESIGN_SUMMARY.md:114`). File `.coverage` di repo berisi 14 file `src/` saja (tanpa `web/app.py`). Angka 97% analisis mencakup web/ — scope berbeda, bukan koreksi.
- Catatan: angka 99,9% dan 76% **tidak direproduksi ulang** dalam audit ini.

## D. Keterbatasan audit

- Statis (baca kode/data), tanpa menjalankan playthrough atau coverage ulang.
- Alur branch 3aa/3ab disimpulkan dari logika `dialog.py:55-56` (`chosen_option` di-overwrite per pilihan) — ditopang `tests/test_quest_dag.py`, tapi tidak dijalankan di sini.

## E. Audit 2 — klaim analisis Grok

> Verifikasi statis sama seperti Audit 1; `test_halaman_index` **tidak dieksekusi** (mode plan, read-only saat verifikasi).

### E1. Klaim "191/192 test lulus; `test_halaman_index` gagal (HTTP 404)" — TIDAK TERKONFIRMASI di repo ini
- Test ada di `tests/test_web.py:44`: `GET /` → assert `status == 200` dan `b"Tian Xu" in body`.
- Handler pasti melayani `/` dengan 200: `web/app.py:195` → `_send_file(STATIC_DIR / "index.html")`; file ada dan berisi "Tian Xu" (`web/static/index.html:6`).
- Fixture `base_url` (`tests/test_web.py:19-25`) bind `127.0.0.1:0` (port acak) — tanpa ketergantungan lingkungan yang bisa memicu 404.
- Jumlah test tepat **192** (`rg -c "^def test_"` → total 192); HEAD `4fd0a37` mendokumentasikan "192 test" lolos, tanpa commit lanjutan.
- Catatan: kemungkinan besar 404 di laporan Grok adalah artefak lingkungan analisis (zip `tianxu-main.zip` tanpa `web/static/index.html`), bukan cacat repo.

### E2. Klaim "proteksi path traversal & null-byte pada save/load" — BENAR (kekuatan, bukan bug)
- `src/engine/session.py:26-36` (`_safe_save_path`): menolak `/`, `\`, `..`, `"\x00"`, plus verifikasi `path.parent != SAVES_DIR.resolve()`.

### E3. Ketidakakuratan laporan Grok yang dikoreksi
- **"±5.900 baris Python (engine + CLI + web)"**: angka 5935 hanya cocok untuk seluruh repo (.py termasuk `tests/`). Scope "engine + CLI + web" sebenarnya ~2937 baris (`src/` 2673 + `web/app.py` 264). Scope mislabeled.
- **"Versi 0.1.0-alpha"**: awalnya dinilai salah oleh auditor (pyproject = "0.1.0"), **tetapi benar** — `CHANGELOG.md:5` menandai release saat ini `[0.1.0-alpha]`. Ini kesalahan auditor (tidak membaca CHANGELOG.md sebelum menilai), bukan kesalahan Grok.

### E4. Pelajaran proses (dari Audit 2)
- Jangan menilai klaim versi/release tanpa membaca `CHANGELOG.md` (file root prioritas).
- Label "dipalsukan" terlalu kuat: klaim gagal test kemungkinan benar di lingkungan zip Grok. Refutasi harus menyebutkan kondisi ("di repo ini, tidak ada jalur 404 secara statis").

### E5. Hasil bersih Audit 2
- **Tidak ada bug baru** yang ditambahkan ke §A–§B. Satu klaim bug (test gagal) tidak terkonfirmasi; satu klaim kekuatan (null-byte) terverifikasi; dua ketidakakuratan kecil.
- Prioritas perbaikan di bawah tetap mengacu hanya pada temuan Audit 1.

## F. Audit 3 — klaim analisis Claude

> Analisis Claude menyertakan *fix* yang dijalankannya pada salinan repo sendiri (hasilnya di `files.zip`, **tidak ada di repo ini**). Klaim diverifikasi terhadap kode repo ini (belum di-patch, 192 test).

### F1. `_read_body()` melanggar kontrak `-> dict` → crash API web — BENAR (bug aktif)
- `web/app.py:183-191`: `return json.loads(...)` — JSON valid tapi top-level non-dict (string/angka/array/null/bool) dikembalikan apa adanya, bukan `{}`.
- `do_POST`: `body.get("action")` (`:230`) dan `body.get("name")` (`:218`, `:244`) — **di luar** `try/except` → `AttributeError` → koneksi putus tanpa respons JSON. Di sisi server traceback muncul (hanya `log_message` yang di-override; `handle_error` tidak).
- Bertentangan dengan klaim `CHANGELOG.md:22` ("Payload aksi web non-objek → respons JSON 400") untuk kasus body top-level non-dict.
- Gap test: `tests/test_web.py:215-231` (`test_aksi_format_salah_ditolak_400`) hanya mengirim `{"action": "racik"}` — **body tetap dict**, hanya field-nya salah. Skenario top-level non-dict tak pernah diuji; docstring test melebih-lebihkan cakupan.
- Dampak: cacat robustnes **level API**, bukan gameplay — CLI (`cli.py:201-206`) dan web UI (`web/static/app.js:174, 282-296`) selalu mengirim dict.

### F2. Tidak ada guard `pending_dialog` di `apply_action` — BENAR, tapi dampak pemain rendah
- `session.py:100-141`: guard `pending_battle` (`:103-108`) menolak aksi non-battle; tidak ada padanan untuk `pending_dialog` (asimetri desain).
- Akibat teknis (terverifikasi statis): `_move` (`:207-222`) & `_talk` (`:161-178`, hanya cek `pending_battle`) lolos selagi dialog aktif; `dialog.start()` (`dialog.py:31-40`) menimpa `current`/`node_id`/`chosen_option`/`pending_dialog` tanpa peringatan → dialog lama hilang; `_maybe_start_branch_dialog` (`session.py:143-146`) memicu ulang dialog percabangan dari node awal → pengulangan naratif.
- **Koreksi dampak**: hanya dieksploitasi lewat POST `/api/action` mentah (hand-crafted HTTP). CLI mengunci input ke `dialog_choice` saat mode dialog; web UI merender hanya tombol dialog. Klaim Claude tentang "skenario pemain realistis (bicara ke Mo Yun)" **tidak terjadi lewat gameplay normal**.
- Fix yang disarankan (pola Claude): guard global simetris dengan `pending_battle`, izinkan hanya `dialog_choice` saat `pending_dialog`.

### F3. `UIState` adalah kode mati/vestigial — BENAR (kosmetik)
- `src/engine/state.py:28` hanya dipakai test (`tests/test_saveload.py:129-190`, `tests/test_session.py:186-205`). Produksi memakai `self._mode()` (`session.py:555,563`) dan `state.pending_dialog` langsung. Bukan bug fungsional.

### F4. Cacat struktural `select_branch` → soft-lock (temuan lanjutan auditor) — struktural, belum reproduksi dinamis
- `quest.py:218`: `select_branch` memakai `completed_quests[-1]` sebagai quest penentu cabang; `completed_quests` **mencakup side quest** (`quest.py:275`).
- Rantai (terverifikasi statis, data dibaca ulang langsung):
  1. `q_akademi_06` (kind=main, `next` berisi `opt_3aa/3ab/3b/3c`, `choice_id: dlg_3_pilih_sikap`) selesai → `_advance_main` set `branch_pending` (`quest.py:206-207`); dialog cabang mulai otomatis di `apply_action` yang sama (`session.py:137,143-146`).
  2. Via celah F2 (API mentah): `move` + `talk` NPC side quest (mis. Mo Yun) → `dialog.start()` menimpa dialog cabang; selesaikan `q_side_moyun` (`dlg_moyun` → `node_offer_ok`, end:True) → `_complete_side` append ke `completed_quests` (`quest.py:275`).
  3. Dialog cabang dipicu ulang → pemain memilih cabang → `_after_dialog` → `select_branch(option)` membaca `completed_quests[-1]` = **side quest**.
  4. Semua side quest ber-`"next": []` (terverifikasi di data) → loop `quest.py:221-226` tak menemukan kecocokan → `:227` membersihkan `branch_pending` **tanpa** men-set `current_quest` → quest utama mati permanen (tidak bisa dipicu ulang).
- Status: **cacat struktural plausibel, belum direproduksi dinamis**. Skenario normal (tanpa F2) aman karena dialog cabang mulai atomik. Klaim "self-healing" dalam analisis Claude hanya benar bila tidak ada side quest yang selesai di jendela itu. Fix F2 menutup jalur eksploitasi F4 sekaligus.

### F5. Hasil bersih Audit 3
- Bug aktif: **F1** (web API crash) dan **F2** (asimetri guard dialog) — keduanya hanya terjangkau via API mentah, bukan gameplay normal. **F3** kosmetik. **F4** cacat struktural menunggu reproduksi dinamis.
- Klaim "200 test lulus" di salinan Claude tidak bisa di-cross-check di sini (zip tidak terakses); repo masih 192 test.
- **Pelajaran proses**: menilai dampak bug harus memeriksa permukaan input (CLI/web UI) yang mengunci aksi saat dialog — klaim "skenario realistis pemain" dari analisis eksternal perlu diverifikasi, bukan diikuti.

## G. Audit 4 — klaim analisis Grok (engine, web, story)

> Verifikasi statis (read-only); salinan Grok tidak terakses, semua klaim dicek ke kode & data repo (192 test, belum di-patch).

### G1. Teknik defend: teks & log "60%" tetapi implementasi 50% — BENAR (aktif, player-facing)
- `data/techniques.csv`: 3 teknik defend (`tek_elemen_perisai_tanah`, `tek_senjata_kuda_kokoh`, `tek_summoning_roh_perisai`) `power=60` + deskripsi "Mengurangi 60% damage".
- `battle.py:199` menulis log "dikurangi {power}%" (=60), tetapi `_enemy_turn` `battle.py:248-249` selalu `dmg // 2` (=50%), mengabaikan `power`.

### G2. `spar_npc` menyimpan ID mentah → quest spar tidak selesai via CLI — BENAR (aktif)
- `session.py:301` resolve `f"npc_{nid}"`, tetapi `:313` menyimpan `spar_npc = nid` mentah.
- `cli.py:280` menyarankan id pendek ("sparing: hanxiu, gucanghai"). `spar hanxiu` → menang → `notify_spar_won("hanxiu")` vs `objective.npc="npc_hanxiu"` (`quest.py:80`) → `q_akademi_03` tak selesai dengan perintah terdokumentasi. **Bukan soft-lock** (retry `spar npc_hanxiu` berhasil); jalur dialog/web (id penuh) aman.

### G3. Web: bug aktif
- **G3a. Tombol Pindah menampilkan ID lokasi** — `app.js:208` (`Pindah → ${esc(cid)}`); tidak ada peta nama di `context`.
- **G3b. Panel Tianyuan menampilkan quest utama sebagai misi sampingan** — `web/app.py:128-135` iterasi `active_side_quests` tanpa filter `kind`; quest utama masuk ke situ via `_note_main_start` (`quest.py:203,171`). Pembanding: `quest.py:35-39 active_side()` justru memfilter `kind=="side"` tapi tidak dipakai UI. Label UI "Misi Sampingan" (`app.js:458`).
- **G3c. Tombol Bicara/Sparring NPC tampil di luar jadwal** — `web/app.py:45-48` filter lokasi saja; engine `_is_npc_available` (`session.py:148-157`) menolak di luar jam (semua 9 NPC berjadwal terbatas, mis. penatua 9–17).
- **G3d. `arcSummaryDismissed` tidak di-reset antar playthrough** — `app.js:5` (init), `:437` (set true); `startNew()`/`loadGame()` (`:62-71`) tidak me-reset → modal ringkasan Arc tak muncul di playthrough kedua tab yang sama.

### G4. Story: bug aktif
- **G4a. Spar "boleh kalah" tidak diimplementasikan** — `STORY_FASE1.md:32` ("Pemain bisa menang/kalah; kalah = dialog berbeda") vs implementasi hanya menang (`quest.py:77-81`; KO `battle.py:319-335` tanpa jalur loss). Dapat di-retry, bukan lock.
- **G4b. Nasib Zhou Yan tidak mengubah world-state** — `STORY_FASE1.md:28` ("3a: bebas · 3b/3c: diusir") & `:86`; data: `npc_zhouyan` lokasi statis `loc_aula_ujian`, on_complete semua cabang hanya set flag/morality/relation/item.
- **G4c. Reaksi positif hanya untuk 3aa, bukan 3ab** — `dlg_suqing:node_hangat_3a`, `dlg_zhouyan:node_bersyukur`, `dlg_hanxiu:node_respect` semua `condition branch_3aa`; tak ada padanan 3ab.
- **G4d. Quest 3b selesai tanpa "tawaran berbayar"** — `q_akademi_3b` objective `talk` (target 1); `dlg_zhouyan:node_keuntungan` pilihan "(Tidak menjawab)" → `node_umum` (end) → quest selesai → on_complete (`morality −8, gold +30`) diterima tanpa menawarkan apa pun.
- **G4e. Flag `jalur_3a` dipakai dua jalur → konfrontasi bocor ke 3ab** — `jalur_3a` diset di `dlg_3_pilih_sikap` `node_pilih` saat memilih opt_3a (mencakup 3aa & 3ab); `dlg_penatua:node_konfrontasi` (cond `jalur_3a`) → pemain 3ab mendapat dialog konfrontasi untuk 3aa.
- **G4f. q07 selalu lewat Mo Yun, termasuk setelah 3aa** — `q_akademi_07` objective `talk npc_moyun` untuk semua cabang (konvergen); setelah 3aa kebenaran sudah terungkap.

### G5. Latent / dormant (benar tapi tak terpicu konten saat ini)
- Companion `hp:0 or hp_max` (`battle.py:40`) — tak tercapai: KO → `active=False` (`:241`); `_rest` bangkit HP penuh (`session.py:372-373`). Code smell.
- Target `foes[0]` (`battle.py:141,194`) — semua hunt single-foe (`enemies.csv`; `_hunt`). Akan menyala bila konten multi-musuh.
- `notify_battle_won` main `defeat` tanpa filter musuh (`quest.py:98-99`) — tak ada main quest `defeat`.
- Jadwal NPC abaikan `day`/`location` — dormant (semua `day:1`; `schedule.location` = `location` top-level); overlap A1/A3.
- `UIState` setter memalsukan `pending_battle` (`state.py:44-50`) — unreachable (kelas mati, §F3).
- `registry.item(...)` None di `_context` (`web/app.py:64`) — data aman (validator).
- `_resolve_entry` tergantung urutan key JSON (`dialog.py:78-84`) — fragility nyata, menunggu konten.

### G6. Direbat (bukan bug)
- **KO exp order** (`battle.py:326,328`): praktis non-issue — exp monotonik naik (tak ada pengeluaran), `loss ≈ 1`; tepi `exp < loss` (beda 1 exp, hanya saat `exp=0`) tak tercapai di game. Catatan evaluasi: pernyataan awal auditor "nilai akhir identik mutlak" keliru secara matematis.
- **"equip tanpa validasi"**: `_equip` memvalidasi `inventory>=1` + `type=="weapon"` (`session.py:244-250`); laporan Grok sendiri mengakuinya minor.
- **"aksi gagal tanpa umpan balik" (W-2.1)**: parsial — penolakan engine masuk log (system) & tetap ter-render (`app.py` selalu `ok:true`); yang benar-benar diam hanya kasus API `ok=false` (tanpa sesi / format salah / 500).

### G7. Klaim minor belum diverifikasi
- `style.css` (layout responsif, W-3.3); beat pemicu `mem_01` (S-3.2); flag "Lonceng kembali" (S-3.5); "suara" Tianyuan (S-3.6). Faktual lain terverifikasi (moral 3c = −2, q07 = +2).

### G8. Hasil bersih & pelajaran Audit 4
- **12 bug aktif baru** (G1–G2 engine, G3a–d web, G4a–f story), 7 latent, 2 direbat — semua level data/kode, tanpa perubahan arsitektur.
- Overlap audit lama: E-3.2 = A2 · S-1.2 = B3 · E-2.3 = A1 · S-4.2 = akar G3b · W-4.1 = E1.
- **Pelajaran proses**: rebuttal harus memeriksa kasus tepi matematis (E-3.4); frasa dampak harus presisi ("tak selesai" ≠ "macet"); jumlah temuan diverifikasi ulang (11→12).

## H. Audit 5 — Analisis ChatGPT engine (diverifikasi 2026-08-14)

> Klaim: 10 bug (P0×2, P1×4, P2×3) + 1 observasi arsitektural + 1 meta. Verifikasi statis
> terhadap kode **saat ini** (sudah memuat fix batch 2026-08-14: F2 guard dialog & G2 spar id).
> Hasil: **5 klaim baru terbukti**, 2 sudah diperbaiki batch sebelumnya, 2 latent yang sudah
> terdokumentasi §G, 1 observasi benar. **0 false positive.**

### H1. `advance_time`/`rest`/`grounding` tidak memicu pengecekan ulang quest berbasis waktu — BENAR (baru)
- Akar: `_pass_time` (`session.py:237-242`) hanya mengubah jam. Konsekuensi quest mengikuti caller-nya sendiri:
  - `_move` → `quest.notify_move()` (`session.py:228`) — **satu-satunya** jalur cek `reach`.
  - `_advance_time` → `quest.advance_time_target_met()` (`session.py:231-235`) — hanya kind `advance_time`.
  - `_rest` (`:368`) & `_grounding` (`:299`) → **tidak memanggil apa pun** dari quest.
- **Softlock `reach+time_window`**: `q_akademi_06` (reach `loc_ruang_lonceng`, window 19→6, data). Pemain tiba 18:00 → `notify_move` gagal window → `advance_time` ke 19:00 → tak ada `notify_move` lagi → quest tak tuntas. Satu-satunya jalan: keluar-masuk lokasi saat window (bukan perilaku wajar).
- **Inkonsistensi `advance_time` quest**: `q_akademi_3c` (advance_time hour 20, day_offset 1, data). `rest`/`grounding` melewati target → quest tetap aktif hingga pemain memakai `advance_time` (baru cek retroaktif). Bukan hard lock, tapi jalur tak konsisten.
- Fix yang disarankan: sentralkan ke `_pass_time` — setelah update day/hour panggil `quest.notify_move()` + `quest.advance_time_target_met()`; hapus panggilan redundan di `_advance_time`.

### H2. `choose` opsi invalid tetap menuntaskan quest — BENAR (baru)
- `resolve_choose` (`quest.py:132-144`): pencocokan opsi `for ... break`, lalu `_grant_companion(option)` + `_complete_main(q["id"])` dipanggil **tak bersyarat**.
- Kirim `option="not_real"` → quest selesai, `player.academy` tetap `None` (untuk `q_akademi_04` = pilih akademi). Jalur nyata via payload API/web.
- Fix yang disarankan: tandai kecocokan; hanya `_grant_companion` + `_complete_main` bila cocok; tolak + log bila tidak.

### H3. Save/load saat dialog aktif dapat crash — BENAR struktur, DORMANT
- `GameState.to_dict` menyimpan `pending_dialog` (`state.py:166`) tapi **tidak** menyimpan state dialog engine (`current`/`node_id`/`last_npc`/`chosen_option`, `dialog.py:24-27`); `from_dict` (`:203`) me-restore-nya; `GameSession.load` (`session.py:83-96`) membuat `DialogEngine` baru dengan `current=None`.
- Setelah load dgn `pending_dialog` ter-set, `view()` (`session.py:563`) memanggil `dialog.view()` → `self.current["nodes"]` → `TypeError: 'NoneType' object is not subscriptable` (`dialog.py:105`).
- **Dormant**: fix F2 (`session.py:110-115`) memblokir `save` saat dialog; jalur save web (`web/app.py:246`) & CLI (`cli.py:265`) sama-sama lewat `apply_action`. Hanya save lama (pra-fix) yang bisa membawa `pending_dialog`.
- Fix yang disarankan (preventif): buang `pending_dialog` dari `to_dict` (dialog tak bisa di-resume — state internalnya tak diserialisasi) & abaikan di `from_dict`.

### H4. `realm_required` pada teknik tidak ditegakkan — BENAR (latent)
- `techniques.csv` punya kolom `realm_required` (semua `realm_pengumpul_qi`). `_technique` (`battle.py:176-203`) cek: teknik dikenal → dalam `skill_pool` akademi → qi cukup. **Tanpa** cek ranah.
- `loader.player_techniques` (`loader.py:93-103`) hanya filter prefix `skill_pool`, tanpa ranah.
- Dormant di Arc 1; menyala begitu Arc 2 punya teknik ranah lebih tinggi.
- Fix yang disarankan: bandingkan urutan ranah (`registry.realms[...]["order"]`, pola sama `dialog.py:137`).

### H5. Status klaim lain Audit 5
- **P0 "dialog bukan gate"** → sudah diperbaiki (F2, `session.py:110-115`). Klaim terhadap snapshot lama.
- **P1 "spar id pendek"** → sudah diperbaiki (G2, `session.py:320`). Klaim terhadap snapshot lama.
- **P2 "aksi battle invalid habiskan turn"** (`battle.py:157-162` lanjut walau `_technique`/`_use_item` early-return) → latent, sudah §G (keputusan desain).
- **P2 "multi-foe tak ada target pemain"** (`foes[0]` hardcoded) → latent, sudah §G.
- **Observasi "event waktu tak terpusat"** → benar; identik akar H1.
- **Meta "coverage tinggi ≠ state-transition coverage"** → benar; contoh: `test_saveload.py:41` sengaja bersihkan `pending_dialog`; tak ada test jalur dialog→save→load.

## I. Audit 6 — Analisis ChatGPT web/frontend (diverifikasi 2026-08-14)

> Klaim: 17 bug (P0×2, P1×8, P2×7) + 1 sintesis. Verifikasi statis terhadap kode **saat ini**
> (sudah memuat fix batch 2026-08-14: G3a `loc_names` & G3d reset arcSummary). Hasil:
> **7 akar nyata**, 2 sudah diperbaiki batch sebelumnya, 3 non-bug/moot, 1 daftar non-bug akurat.
> **0 false positive.** Catatan: tidak ada `threading.Lock` di server maupun engine → race nyata.

### I1. Akar bug nyata (frontend)

- **Akar A — tanpa action lock (#1/#2/#15)** — `act()` (`app.js:180-183`) & `actShop()` (`:413-416`)
  tanpa busy flag; `view = data.view` tanpa urutan. Server `ThreadingHTTPServer` (`web/app.py:257`)
  → double-click = 2 POST **konkuren** ke `session.apply_action()` tanpa lock (data race). Konsekuensi:
  - **#1** beli 2×, `advance_time` 2×, spar 2×.
  - **#2** respons bisa tiba terbalik → UI mundur ke state lama.
  - **#15** paling berbahaya di dialog/choose/battle (state machine): guard F2 membolehkan
    `dialog_choice` berulang → 1 klik ganda = 2 langkah.
  - Fix W1: busy flag → satu aksi satu transisi satu render (satu klien, jadi cukup di frontend).
- **Akar B — lifecycle Tianyuan (#3/#11/#12)** — `#tianyuan` `z-index:50` tanpa backdrop
  (`style.css:259-271`), modal `z-index` 99/100 (`:288-299`), dua sistem modal tanpa koordinasi;
  `openTianyuan()` fetch sekali (`app.js:444-445`) tanpa refresh setelah `act()`.
  - **#11** game tetap bisa diklik di belakang panel (pola drawer — bukan bug mandiri).
  - **#3** tianyuan terbuka + klik toko di belakangnya → panel terperangkap di bawah overlay.
  - **#12** panel menyimpan snapshot lama (mis. ingatan 1/4 → 2/4 tak tampil).
  - Fix W3: auto-`closeTianyuan()` di `act()` + `showModal()` (panel = snapshot, tutup-otomatis).
- **#6 error API tak ditampilkan** — `act()` tanpa `else`; server bisa kirim `{ok:false,error}`
  (500, `app.py:239`). Fix W2.
- **#7 network failure tak ditangani** — `api()` (`app.js:23-28`) tanpa try/catch → reject diam.
  Fix W2.
- **#9 tidak responsif** — grid `260px 1fr 300px` tanpa `@media` (`style.css:126`). Fix W4.
- **#16/#17 validasi nama save** — backend **sudah** validasi penuh (`session.py:26-36`);
  nama kosong jatuh ke default `"save1"` (`:475`, bukan error); frontend tanpa guard (kosmetik).
  Fix W5.
- **#13 filter teknik hanya Qi** (`app.js:324`) — **konsisten dengan engine** (keduanya abaikan
  `realm_required`, §H H4). Mismatch baru muncul setelah H4 difix → prasyarat fix H4.
- **#14 battle tanpa target** (`app.js:317`) — konsisten dgn latent multi-foe (§G). Defer.

### I2. Sudah diperbaiki batch sebelumnya (klaim terhadap snapshot lama)

- **#4 arcSummaryDismissed global tak di-reset** → sudah (G3d, `app.js:64,70` reset di startNew/loadGame).
- **#18 lokasi tampil sebagai internal ID** → sudah (G3a, `app.js:208` `ctx.loc_names[cid] || cid`).

### I3. Non-bug / moot

- **#5 save tak muncul di daftar / tanpa konfirmasi** — daftar save hanya di title screen;
  reload → `refreshSaveSlots()` jalan lagi (`:491`); feedback ada via log narasi (`session.py:486`).
- **#8 `view.error` tak diperiksa** — `_payload` (`app.py:106`) memang tanpa field error;
  penolakan engine tampil sebagai entri log system (ter-render). Ditangani log.
- **#10 log `52vh`** (`style.css:168`) — opini desain (P2 subjektif).
- **#19 daftar non-bug auditor** — akurat: `esc()`, viewport meta, path containment, validasi
  action-is-object, tiga kolom disengaja.

### I4. Sintesis auditor

Diagnosis inti benar: frontend bukan state-machine-aware (tidak ada lock/queue/sequence/modal
lifecycle) → rusak saat aksi wajar: double-click, panel saat modal aktif, reload/load kondisi tertentu.
Dampak: P0/P1 terfokus pada #1/#2/#15.

## J. Audit 7 — Analisis ChatGPT story layer (diverifikasi 2026-08-14)

> Klaim: 16 bug (P0×3, P1×8, P2×5) + sintesis fundamental. Verifikasi statis terhadap
> `STORY_FASE1.md` + data quest/dialog/memory/NPC. Hasil: **~5 temuan baru** (1 P1 sistematis,
> sisanya P2), **0 P0 baru**, mayoritas klaim sudah terdokumentasi §G, 2 klaim salah (#4, #11
> parsial), 1 miskarakterisasi (#3). Evaluasi: 1 kesalahan atribusi (#6, lihat catatan) — terkoreksi di sini.

### J1. Koreksi klaim auditor (bukan bug / miskarakterisasi)

- **#4 (3aa & 3ab memory sama) — BUKAN BUG.** Dokumen eksplisit memberi `mem_02` untuk **kedua**
  sub-cabang 3a: tabel memory "Cabang **3a** (membongkar)" & tabel q5 `q_akademi_3aa`→mem_02,
  `q_akademi_3ab`→mem_02. Data `memories.json:13` (`unlocked_by_quest: ["q_akademi_3aa","q_akademi_3ab"]`)
  persis dokumen. Premis auditor "dokumen menjanjikan variasi memory per pilihan" **keliru**.
  (Titik tematik "mem_02 lebih cocok 3aa" = opini.)
- **#3 (3b ≠ cerita rumor/Han Xiu) — MISKARAKTERISASI.** Desain 3b dokumen = *"tawar bantuan
  dengan imbalan, **atau** rumor menjatuhkan Han Xiu"*. Implementasi menjalankan **opsi 1**
  (memeras Zhou Yan; summary `quests:150` "tawarkan 'bantuan' dengan imbalan") → bukan "cerita
  berbeda". Residu nyata: opsi rumor/Han Xiu absen (P2) + bug G4d masih ada (`(Tidak menjawab)` →
  quest tuntas + gold 30, `dlg_zhouyan:node_umum` end).
- **#11 (Han Xiu cuma angka) — SALAH PARSIAL.** `dlg_hanxiu:node_respect` (cond `branch_3aa`, :104-108)
  = respons naratif substantif ("Kau punya tulang"). Hanya 3aa; tak ada padanan 3ab (= G4c).
- **#14 (Tianyuan terlalu aktif) — SEBAGIAN SUDAH FIXED.** Contoh q06 `[Sistem] Pola yang sama...`
  **dihapus** (B1). Residu: q07 `[Sistem] Jalanmu baru dimulai.` (benign) + `node_penutup`
  (narration, bukan Sistem). Sesuai keputusan "pasif".

### J2. Terverifikasi benar — tumpang-tindih §G (Audit 4, sudah didokumentasikan)

- **#2/#10 Zhou Yan tak jadi world state** = **G4b** — tanpa `zhouyan_status`; 3ab hanya talk
  Mo Yun (tak menyelamatkan siapa pun); `npc_zhouyan` statis `loc_aula_ujian`. **#10 menambahkan
  perumusan sistematis** (daftar state hilang untuk kontinuitas Arc 2).
- **#12 Su Qing tanpa respons 3ab** = **G4c** — `dlg_suqing` hanya node 3aa/3b/3c; 3ab → generik.
- **#3 residu "(Tidak menjawab)" selesai dgn bayaran** = **G4d**.
- **#1 double reveal 3aa di q07** = **G4f** + nuansa baru: `dlg_moyun:node_truth_3aa` (:188)
  mengulang reveal eksplisit setelah konfrontasi yang hanya implisit (`node_konfrontasi3` "kau
  tahu kebenarannya"). Dokumen sendiri mendesain q07 = "talk Mo Yun (reaksi beda per cabang)"
  untuk semua cabang → redundansi nyata, **P1 bukan P0**.
- **#5 konfrontasi bukan konfrontasi** — **sesuai dokumen** (line 17: "Penatua menyingkirkannya
  dengan dingin"); implementasi persis. Opini desain, P2.

### J3. Temuan baru (belum terdokumentasi)

- **#10 sintesis — "branch flag ≠ world state" (P1, paling bernilai).** Yang tersimpan setelah
  branch: `branch_*`, morality, relation, memory — bukan `bell_status`/`zhouyan_status`/
  `elder_exposed`/`academy_knows_truth`/`chenxu_reputation`. Arc 2 tak bisa menanyakan "apakah
  Zhou Yan bebas?" Perumusan sistematis G4b → **keputusan desain: tentukan world-facts resmi
  sebelum konten Arc 2** (bisa berupa `flags` eksplisit, bukan field baru).
- **#13 memory→dialog gap (P2).** `STORY_FASE1.md` §3.1/aturan kunci: "ingatan yang pulih
  mengubah sikap & membuka opsi dialog Chen Xu" — namun **nol** kondisi memory di semua dialog
  (grep `memory|mem_|ingatan` = kosong; `_eval_condition` tak punya kunci memory-count).
  Ingatan naratif murni tanpa efek dialog.
- **#6 pilihan konfrontasi kosmetik (P2) — KOREKSI ATRIBUSI.** [Evaluasi: semula kutandai "= G4e",
  **salah** — G4e adalah bocornya `node_konfrontasi` (cond `jalur_3a`) ke pemain 3ab, defect
  berbeda.] #6 sendiri = kedua pilihan (`:309-312`) menuju `node_konfrontasi2` sama tanpa efek
  beda → choice illusion. Baru, minor.
- **#7/#8 q06 craft (P2, opini penulisan).** `node_scene:338` "kau tahu, dari bentuknya, itu
  Lonceng" (pengetahuan omniscient) & red-herring Mo Yun tuntas terlalu cepat — namun **sesuai
  dokumen** ("ini membuktikan n tidak bersalah"). Saran perbaikan: misteri bertahap → kurasi.
- **#15 tone drift (P2, opini)** — baris "yang lemah dikorbankan" (`node_truth_3c`), "diam itu
  sama kejamnya" (`node_kecewa_3c`), "membeli tidurmu yang tenang" (`node_pahit_3b`) dalam
  envelope tone dokumen ("tone sedikit lebih tegang" di konfrontasi). Penilaian subjektif.
- **#16 ending kurang dibedakan (P2, opini)** — q07 `on_complete` dibagi semua cabang; `node_penutup`
  dipakai 3aa/3ab/3c, `node_truth_3b` (`end:true`, :201) tanpa penutup → 3b memang berbeda;
  `arc_summary` membedakan via label branch + morality. Kurang-dibedakan itu nyata tapi sederhana.

### J4. Hasil bersih Audit 7

- **0 bug P0 baru** (semua turun). ~5 temuan bernilai: #10 (P1, sistematis) + #13/#6/#1-nuansa
  (P2) + #7/#8/#15/#16 (P2 opini).
- **2 klaim salah** (#4 non-bug, #11 parsial), **1 miskarakterisasi** (#3), **1 sebagian fixed**
  (#14/B1).
- **Pelajaran**: klaim story harus dicek terhadap desain tertulis, bukan asumsi "yang seharusnya";
  mayoritas "bug story" ternyata sudah sesuai dokumen (keputusan desain), bukan deviasi.

## K. Audit 8 — Analisis Claude web/visual layer (diverifikasi 2026-08-14)

> Klaim: 4 bug utama (P1×2, P2×2) + 2 minor, semua di lapisan web/visual yang lolos test suite
> Python (tidak menguji JS/CSS/race). Verifikasi statis terhadap `web/static/*`, `web/app.py`,
> `src/engine/session.py`. Hasil: **4/4 benar, 0 false positive**; 2 tumpang-tindih §I (W1/W2),
> 2 baru (#1, #2); 2 minor baru. Evaluasi verifikasi: 2 penyempurnaan presisi (lihat K1/K2/K5).
> Baseline auditor "pytest 192" = snapshot lama (sekarang 197) — tak memengaruhi klaim.

### K1. #1 Teks dialog ber-`\n\n` collapse jadi satu paragraf (P1, baru)

- `.dialog-text` (`style.css:197`) tak punya `white-space: pre-wrap`, padahal `.log-entry`
  (:175) dan `.mem-full .mem-text` (:283) punya. Browser collapse whitespace → jeda paragraf hilang.
- **4 teks ber-`\n\n` terverifikasi persis**: `dlg_moyun:222` (reveal Tianyuan Ling),
  `dlg_zhouyan:272`, `dlg_penatua:321` (konfrontasi Penatua An), `dlg_3_pilih_sikap:338` (q06
  scene) — semuanya dirender lewat `renderDialog` → `.dialog-text`; `renderChoose` pakai class
  sama untuk prompt pilihan.
- Fix: `white-space: pre-wrap;` pada `.dialog-text` (1 baris). P1/P2 borderline — dijaga P1 karena
  menimpa momen klimaks naratif.

### K2. #2 Modal "Arc 1 Selesai" muncul ulang tiap load (P2, baru)

- Akar backend: `arc_summary` truthy selamanya setelah q_akademi_07 tuntas (`session.py:499`,
  quest tak pernah dihapus dari `completed_quests`). Penahan satu-satunya = `window.arcSummaryDismissed`
  (`app.js:5`), variabel JS yang reset di startNew/loadGame **dan** hilang saat halaman di-reload.
- **Catatan evaluasi**: komponen "muncul lagi setelah loadGame" sebagian *diperkenalkan G3d* (yang
  sengaja me-reset flag agar summary tampil sebagai recap tiap sesi). Ketegangan desain: "tiap load"
  vs "sekali selamanya".
- **Keputusan fix: localStorage frontend-only, per nama save** — sekali dismiss per save, bisa
  direview ulang via tombol; tanpa menyentuh engine/state (konsekuensi: tak ikut antar perangkat).

### K3. #3 `ok:false` tak pernah sampai ke pemain (P2, = §I #6 / fix W2)

- `act()` (`app.js:180-183`), `actShop()` (:413-416), `startNew()` (:62-65) hanya tangani
  `if (data.ok)` tanpa `else`; `loadGame()` (:67-71) sudah benar (tampilkan `data.error`).
- Kasus nyata: sesi hilang (server restart), body aksi malformed, exception engine. `/api/action`
  memang sengaja menyiapkan pesan jelas (`app.py:234-238`) — tapi di-fetch lalu dibuang.
- Fix: cabang `else` di tiga fungsi → tampilkan `data.error`. (Duplikat W2 §I — fix gabungan.)

### K4. #4 Race condition `session` global tanpa lock (P2, = §I Akar A / fix W1)

- `app.py:37` variabel modul dimutasi langsung oleh `do_POST`; server = `ThreadingHTTPServer`
  (:257), thread per request, tanpa `threading.Lock` di mana pun (grep kosong). Tombol aksi tak
  di-disable saat fetch → double-click = dua `apply_action` konkuren mutasi state sama.
- Fix minimal: busy-flag frontend (= W1); lock server = defense-in-depth opsional.

### K5. Minor (baru)

- **POST `/api/save` dead code** (`app.py:243-247`): frontend hanya pakai `/api/saves` GET
  (`app.js:41`); save via `act({type:"save"})` → `/api/action`. Tanpa try/except (beda dengan
  `/api/action`). **Presisi evaluasi**: `_save` menangkap `OSError` untuk *path* (`_safe_save_path`,
  session.py:476-480), tetapi fase tulis `json.dump` (:483) tidak dibungkus → OSError saat nulis
  (disk penuh) = **500 mentah**. Plus: endpoint **mengabaikan nilai balik `apply_action`** — bila
  `_save` mengembalikan `{"ok":False}`, endpoint tetap kirim `ok:True` (bohong "tersimpan").
  Semua teoritis karena dead code.
- **`.shop-content` tanpa definisi CSS** (`app.js:382`; tidak ada di `style.css`) — hook menggantung,
  non-fungsional.

### K6. Hasil bersih Audit 8

- **4/4 klaim benar, 0 false positive.** Temuan baru: #1 (P1), #2 (P2), Minor 1, Minor 2.
  #3 = §I W2, #4 = §I W1 (tidak menambah; fix digabung).
- **Pelajaran**: test Python murni tak menutup render JS/CSS maupun race antar-thread; 2 temuan
  bernilai (#1 dampak naratif langsung, #2 pola "state UI" lain — mis. banner log — berisiko sama).

## L. Audit 9 — Analisis Claude story layer (bug naratif, diverifikasi 2026-08-14)

> Klaim: temuan bug naratif kritis pada urutan pengungkapan misteri. Verifikasi statis terhadap data quest/dialog/story. Hasil: **3/3 klaim diverifikasi**.

### L1. Hasil verifikasi

| No | Klaim | Verdict | Bukti |
|----|-------|---------|-------|
| 1 | Mengidentifikasi bug naratif kritis dalam urutan pengungkapan misteri | �� **Ya** | Diverifikasi melalui inspeksi `data/quests/quests_akademi.json`, `data/dialogs/dialogs_akademi.json`, dan `STORY_FASE1.md` — urutan reveal di `dlg_moyun` (`node_bukti` vs `node_konfrontasi`) menunjukkan inkonsistensi flag `jalur_3a` vs `branch_3aa`. |
| 2 | Bug naratif memengaruhi konsistensi alur cerita | �� **Ya** | Flag `jalur_3a` diset di `dlg_3_pilih_sikap` untuk kedua sub-cabang 3aa & 3ab, namun `node_konfrontasi` (hanya untuk 3aa) menggunakan flag yang sama → pemain 3ab mendapat dialog konfrontasi yang tidak seharusnya. Sudah tercatat sebagai **G4e** di §G. |
| 3 | Bug ini menghasilkan inkonsistensi naratif yang tidak disengaja | �� **Ya** | Pemain cabang 3ab menerima reveal "Lonceng diambil Penatua" sebelum konfrontasi yang seharusnya hanya untuk 3aa. Ini menciptakan paradox naratif: konfrontasi (3aa) datang *setelah* reveal, bukan sebelumnya. |

### L2. Status perbaikan

- **G4e** (flag `jalur_3a` → `branch_3aa` di `node_konfrontasi`) sudah diperbaiki dalam batch perbaikan 2 (commit terkini).
- Tidak ada bug baru yang ditemukan di luar yang sudah terdokumentasi (§G G4e).

## Prioritas perbaikan yang disarankan

1. **B1** (q06 system_msg) — ✅ **selesai**.
2. **B2** (3b payoff) — butuh keputusan desain dulu (default: `node_penutup_3b` versi gelap).
3. **A1** (midnight schedule) — ✅ **selesai** (seragamkan dengan pola `quest.py`).
4. **A2** (hardcode) — ✅ **selesai** (`world.hunt` di config + validator aturan 7).
5. **B3** (gating ingatan) — fitur baru, skala lebih besar; tunda.

Tambahan dari plan `2026-08-14-fix-sisa-bug-dan-hardening.md`: H4 ✅ · A1 ✅ · J3#6 ✅ · #9 ✅ · A2 ✅ · G4d ✅ · K5 ✅ · G4b/#10 ✅ · G4c ✅ · G4f ✅ · B2 ✅ · G4a ✅ · K4-lock ✅ — seluruhnya selesai (Fase A/B/D); satu-satunya defer = B3/#13. Temuan tindak lanjut (plan `2026-08-14-fix-temuan-evaluasi-diri.md`): regresi `node_kalah` ✅ · dok drift angka test ✅. Laporan pemain (2026-08-14): UX1 (tab Jual toko) ✅. **Fitur GDD P1 (plan `2026-08-14-p1-fitur-gdd-belum-dibangun.md`)**: P1-2 (relations berdampak) ✅ · P1-1 (gating ingatan = B3/#13) ✅ · P1-3 (musuh malam) ✅ — tidak ada defer tersisa. **Tahap C FULL (plan `2026-08-14-rampungkan-arc-akademi-tahap-c.md`)**: C1 (teknik dipelajari & ditingkatkan) ✅ · C2 (siklus bulan derived) ✅ · C3 (moralitas → ending scaffold) ✅ · C3-fix (temuan evaluasi: `_eval_condition` flag early-return → AND) ✅ — lihat Batch 5 di atas. Lihat tabel status di atas.
