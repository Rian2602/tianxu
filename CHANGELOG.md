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
- Dokumentasi: `docs/list_bug.md` (status perbaikan terverifikasi), 2 plan implementasi (`docs/superpowers/plans/`), sinkronisasi ENGINE_ARCHITECTURE / DESIGN_SUMMARY / README / PROJECT.

### Changed
- Jumlah test: 192 → **209**; validator 16 aturan tetap exit 0.
- `README.md` & `PROJECT.md`: jumlah test disinkronkan (209).

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
