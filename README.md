# Tian Xu: Second Life

> **天缘灵 · RPG Kultivasi Xianxia Berbasis Teks**

**Tian Xu: Second Life** adalah RPG kultivasi (wuxia/xianxia) berbasis teks yang menceritakan Long Tianxu (龙天序) — pangeran yang dikhianati dan mati dalam kesendirian — yang terlahir kembali sebagai Chen Xu (陈旭) berkat **Tianyuan Ling (天缘灵)**, item pemberian dewa. Pemain bebas menentukan arah moral di kehidupan kedua.

Repo ini berisi **vertical slice Fase 1: Arc Akademi** — bukti konsep yang dapat dimainkan penuh dari awal hingga akhir cerita, dengan percabangan moral di babak akhir.

## Fitur

- **3 akademi pilihan** — Elemen (五行阁), Senjata (兵锋院), Summoning (御灵宗) — tiap jalur punya `skill_pool` teknik tersendiri
- **Sistem pertarungan berbasis giliran** — elemen 五行 (1.5× / 0.67×), kritikal, kompanion auto-attack dengan HP persisten
- **Kultivasi** — ranah, teknik, eksp (Qi), pil & ramuan, moralitas (3 sikap akhir cerita)
- **Quest & dialog bercabang** — satu quest utama (DAG), side quest repeatable sejak hari 1
- **Ingatan** — 4 ingatan naratif dari kehidupan pertama
- **Dua antarmuka** — CLI terminal & Web UI gelap-emas

## Teknologi

- Python **3.12**, **stdlib-only** (tanpa dependency runtime; `pytest` untuk dev)
- Data-driven: JSON (struktur) + CSV (tabel datar/balancing) di `data/`
- Server web stdlib (`http.server`), tanpa build step

## Menjalankan

```bash
# CLI — mulai baru
python3 src/cli.py

# CLI — lanjut dari save (disimpan otomatis di saves/)
python3 src/cli.py -l save1

# Web UI — buka http://localhost:8000
python3 web/app.py
```

## Pengembangan

```bash
# Semua test (wajib dari root)
python3 -m pytest -q

# Validasi konsistensi data (16 aturan, ENGINE_ARCHITECTURE §14)
python3 tools/validate_data.py
```

> **Pengembangan**: `pytest` adalah satu-satunya dependency dev. Pada sistem dengan Python *externally-managed* (PEP 668 — mis. Ubuntu/Debian), install di virtualenv: `python3 -m venv .venv && source .venv/bin/activate && pip install pytest`. Tanpa itu, `python3 -m pytest` tetap jalan selama `pytest` tersedia.

## Struktur

```
data/            # konten: quest, dialog, NPC, item, musuh, lokasi, ingatan, resep, teknik
docs/            # GDD · arsitektur engine · alur cerita · ringkasan desain · prompt playtest
src/             # engine Python: session, battle, dialog, cultivation, morality, memory, quest
tests/           # 209 test (pytest)
tools/           # validator data
web/             # server web stdlib + halaman statis (index.html, app.js, style.css)
saves/           # save game (di-gitignore)
```

## Lisensi

[MIT](LICENSE) © 2026 Rian2602
