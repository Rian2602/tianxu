# Kontribusi — Tian Xu: Second Life

Terima kasih sudah meluangkan waktu untuk berkontribusi! Repo ini adalah vertical slice **Fase 1 (Arc Akademi)** dari RPG kultivasi xianxia berbasis teks. Panduan berikut menjaga kualitas proyek agar tetap konsisten dan mudah dikelola.

## Prinsip inti

- **Data-driven**: konten game (quest, dialog, NPC, item, musuh) hidup di `data/` — tambah konten = edit data, **bukan** kode. Kode hanya berisi engine.
- **stdlib-only**: tanpa dependency runtime. Satu-satunya dependency dev adalah `pytest`.
- **Bahasa**: semua teks game, komentar, dan dokumen berbahasa Indonesia; istilah teknis ber-pinyin/hanzi.

## Setup pengembangan

```bash
# Python >= 3.12 (dari root repo)
python3 -m venv .venv && source .venv/bin/activate
pip install pytest          # satu-satunya dependency dev

# Jalankan game
python3 src/cli.py                      # CLI
python3 web/app.py                      # Web UI → http://localhost:8000

# Verifikasi (WAJIB sebelum commit)
python3 tools/validate_data.py          # 16 aturan konsistensi data — exit 0
python3 -m pytest -q                    # seluruh test suite
```

Urutan baku (sama dengan CI): **validate → pytest**.

## Menambah konten (quest / dialog / NPC)

1. Edit file data yang sesuai di `data/` (lihat `docs/ENGINE_ARCHITECTURE.md` §5 untuk skema).
2. Jika skema field berubah, **wajib** perbarui:
   - `tools/validate_data.py` (validator 16 aturan, §14),
   - `docs/ENGINE_ARCHITECTURE.md` (aturan emas: skema adalah kontrak),
   - test validator bila perlu.
3. Jalankan `python3 tools/validate_data.py` sampai exit 0.
4. Tambahkan/update test alur di `tests/` (pakai helper `tests/conftest.py`: `finish_dialog`, `move_path`, `play_to_incident`, `god_mode`).

## Menambah fitur engine

- Fitur baru lewat engine, jangan langsung menulis ke state.
- Aksi baru: daftarkan di handler-map `src/engine/session.py::apply_action`.
- Pertahankan invariant: satu quest utama aktif, graf quest DAG (ditegakkan `tests/test_quest_dag.py`).
- Setiap fitur harus punya test.

## Konvensi commit

Format: `<jenis>: <ringkasan>` — Bahasa Indonesia, fokus pada **alasan** perubahan.

| Jenis | Contoh |
|---|---|
| `feat:` | `feat: spar boleh kalah dengan dialog berbeda (G4a)` |
| `fix:` | `fix: jadwal NPC lintas tengah malam (A1)` |
| `test:` | `test: cakupan aturan validasi §14` |
| `docs:` | `docs: sinkronkan status bug & test (209)` |
| `ci:` | `ci: cache pip di GitHub Actions` |
| `chore:` | `chore: untrack artefak orchestration .agents/` |

Referensi ID bug (mis. `(A1)`, `(H4)`) mengacu pada `docs/list_bug.md` — gunakan bila perubahan menjawab temuan audit.

## Aturan sebelum mengirim perubahan

- [ ] `python3 tools/validate_data.py` exit 0 (bila menyentuh `data/`)
- [ ] `python3 -m pytest -q` hijau
- [ ] Tidak ada file artefak ikut ter-commit (`saves/*.json`, `.venv/`, `.coverage`, `.pytest_cache/`, `.agents/`, `.superpowers/`)
- [ ] Skema data yang diubah disertai pembaruan validator + `docs/ENGINE_ARCHITECTURE.md`

## Dokumen acuan

- `docs/GDD.md` — visi, cerita, desain game
- `docs/ENGINE_ARCHITECTURE.md` — kontrak teknis (skema data, arsitektur, §14 validasi)
- `docs/STORY_FASE1.md` — alur cerita Arc Akademi
- `docs/DESIGN_SUMMARY.md` — keputusan desain yang disahkan
- `docs/list_bug.md` — daftar bug & temuan audit (dengan status perbaikan)
