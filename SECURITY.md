# Kebijakan Keamanan — Tian Xu: Second Life

## Melaporkan kerentanan

Proyek ini adalah game single-player lokal tanpa server produksi, namun kami tetap menerima laporan kerentanan dengan serius.

- **Privasi**: jangan membuka issue publik untuk kerentanan yang belum dipatch.
- **Cara melaporkan**: gunakan **GitHub Security Advisory** (tab *Security* → *Report a vulnerability*) atau hubungi maintainer melalui jalur kontak di profil GitHub.
- **Waktu respons**: konfirmasi penerimaan dalam 3 hari kerja; perbaikan & rilis patch mengikuti tingkat keparahan.

## Yang termasuk lingkup

- Kerentanan pada engine (`src/`) yang dapat merusak save game atau eksekusi kode (mis. path traversal pada save/load).
- Kerentanan pada server web dev (`web/app.py`, stdlib `http.server`) — proyek ini hanya untuk penggunaan lokal/development.
- Kerentanan pada data (mis. referensi tidak valid yang memicu crash saat load).

## Yang di luar lingkup

- Isu keseimbangan game, bug naratif, atau bug gameplay non-keamanan — laporkan sebagai issue biasa.
- Kerentanan pada dependency — proyek ini stdlib-only; jika dependency dev (pytest) bermasalah, laporkan ke upstream.
