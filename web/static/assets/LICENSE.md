# Lisensi Aset Web — Tian Xu: Second Life

Semua aset di direktori ini dipakai **self-host** (tanpa CDN saat runtime) — konsisten dengan prinsip stdlib-only proyek.

## Tekstur, Avatar, Audio — milik proyek

- `textures/*.png` (paper-dark, silk-dark, ink-wash, cloud-mist, gold-noise)
- `img/avatar.jpg`
- `audio/dawn-over-tian-xu.mp3`

Dibuat/di-generate untuk proyek Tian Xu: Second Life (AI-assisted, milik penulis proyek).
Bebas didistribusikan bersama proyek ini. Dilarang dijual terpisah sebagai paket aset.

**Catatan pemrosesan** (lihat `tools/optimize_png.py` + catatan commit):
- Tekstur: downscale 2× (768×512 → 384×256, box filter) + re-encode filter terbaik/zlib 9 — proses bisa diulang via `tools/optimize_png.py` (versi sumber 768×512 ada di backup lokal, bukan di repo).
- Avatar: 2816×1536 → 300×164 (ditampilkan 120px di UI).
- Audio: 192 kbps stereo 44.1 kHz → 64 kbps mono 22.05 kHz (ambient, volume default 0.3).

## Font — Noto Serif SC & Noto Sans SC

`fonts/*.woff2` = subset dari Google Fonts, © Google, dilisensikan di bawah
**SIL Open Font License 1.1** (OFL-1.1).

- Noto Serif SC — https://fonts.google.com/noto/specimen/Noto+Serif+SC
- Noto Sans SC — https://fonts.google.com/noto/specimen/Noto+Sans+SC
- Teks lengkap OFL-1.1: https://openfontlicense.org

`fonts.css` memetakan subset (Latin + Hanzi yang dipakai game) ke `@font-face`
dengan `unicode-range` — hanya subset yang relevan diunduh browser.

## Ikon — Lucide

`icons/*.svg` = **Lucide** (lucide-static v0.454.0), lisensi **ISC** —
lihat `icons/LICENSE.lucide.txt` untuk teks lengkap. Sumber: https://lucide.dev
