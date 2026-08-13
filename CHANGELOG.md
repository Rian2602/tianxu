# Changelog

Semua perubahan penting pada **Tian Xu: Second Life**.

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
