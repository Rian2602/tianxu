# AGENTS.md — Tian Xu: Second Life

RPG kultivasi (wuxia) berbasis teks — vertical slice Fase 1, Arc Akademi. Python 3.12, stdlib-only (pytest untuk dev). Semua teks game, komentar, dan dokumen berbahasa Indonesia; istilah teknis ber-pinyin/hanzi.

## Perintah (jalankan dari root repo)

- `python3 src/cli.py` — jalankan game CLI (`-l <nama>` untuk lanjut dari save)
- `python3 -m pytest -q` — semua test. Wajib dari root (tidak ada pytest.ini/pyproject; `import src` butuh cwd di sys.path)
- `python3 tools/validate_data.py` — validasi konsistensi data (16 aturan = ENGINE_ARCHITECTURE §14). Exit non-zero jika error. **WAJIB** jalan dan exit 0 setelah menyentuh `data/`.

## Arsitektur

- **Data-driven**: semua konten di `data/` (JSON untuk struktur, CSV untuk tabel datar lewat `csv.DictReader`). Tambah konten = edit data, bukan kode. `src/loader.py::DataRegistry` memuat semua dan membuat index lookup sekali saat startup.
- **Alur aksi**: `src/cli.py` memetakan input teks → dict aksi → `GameSession.apply_action()` (`src/engine/session.py`). Fitur baru lewat engine, jangan langsung menulis ke state.
- **Engine** (`src/engine/`): session (orchestrator) · state · battle · dialog · cultivation · morality · memory · quest · events · effects.
- **Quest**: satu quest utama aktif; percabangan lewat pilihan dialog (`choice_id`/options → dialog). Graf quest harus DAG — ditegakkan `tests/test_quest_dag.py` + validator. Side quest (repeatable) data terpisah dan tak boleh memakai NPC/lokasi/objek quest utama.
- **web/** = server stdlib-only (`python3 web/app.py` → `http://localhost:8000`) + halaman statis. Satu sesi aktif per proses; v1 tersedia lewat CLI & web.
- **Save**: `saves/*.json`, hanya di lokasi aman, di-gitignore. Path `__file__`-relative → cwd-independen.

## Konvensi & gotchas

- Uji alur pakai helper `tests/conftest.py`: `finish_dialog`, `move_path`, `play_to_incident`, `god_mode` (battle deterministik).
- Elemen 五行: peta siklus (`element_advantage`) di `data/config.json`; multiplier 1.5× / 0.67× hardcoded di `src/engine/battle.py::_calc_damage`. Kritikal (`crit_chance`/`crit_multiplier`) bisa diatur di `data/config.json` → `battle` (default kode 0.08 / 1.5).
- Mengubah skema field data harus disertai pembaruan validator `tools/validate_data.py`, dan sebaliknya.
- Dokumen resmi: `docs/GDD.md` (desain) · `docs/ENGINE_ARCHITECTURE.md` (§14 = aturan validasi) · `docs/STORY_FASE1.md` (alur cerita) · `docs/DESIGN_SUMMARY.md` (keputusan yang sudah disahkan).
- Tidak ada config lint/typecheck; tidak ada dependency selain pytest.
