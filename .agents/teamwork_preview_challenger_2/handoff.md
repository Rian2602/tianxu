# Laporan Handoff Challenger 2: Adversarial Constraints & Edge Cases

**Target Dokumen**: `docs/superpowers/plans/next-roadmap.md`  
**Peran**: Challenger 2 (Adversarial Constraints, Validation Invariants & Edge Cases)  
**Tanggal**: 14 Agustus 2026  
**Status / Verdict**: `REQUEST_CHANGES` (Perlu Revisi Spesifikasi Sebelum Eksekusi Subagent)

---

## 1. Observation (Hasil Pengamatan Langsung & Kutipan Berkas)

Berdasarkan pengujian empiris, eksekusi perintah verifikasi, serta audit baris per baris terhadap `docs/superpowers/plans/next-roadmap.md`, `tools/validate_data.py`, `data/*.json`, dan modul `src/engine/`, ditemukan fakta-fakta observasi berikut:

### Obs-1: Baseline Pengujian & Validasi
- Perintah `python3 -m pytest -q && python3 tools/validate_data.py` menghasilkan exit code 0:
  ```
  ........................................................................ [ 77%]
  .....................                                                    [100%]
  93 passed in 1.38s
  VALIDASI LULUS — quest: 14, dialog: 10, npc: 9, lokasi: 9, item: 6, musuh: 3, ingatan: 4
  ```
- Perintah `python3 -m pytest --cov=src --cov-report=term-missing` menunjukkan basis kode saat ini memiliki coverage 84% dengan tepat 231 baris logika belum teruji (persis seperti klaim pada roadmap §1.1 & §4 EP3-T1).

### Obs-2: Cacat Logika Kritis pada Spesifikasi Jadwal NPC (`EP2-T2`, Baris 507–520)
Pada spesifikasi tugas `EP2-T2` baris 507–520 tertera potongan kode helper:
```python
def _is_npc_available(self, npc: dict) -> bool:
    schedules = npc.get("schedule", [])
    if not schedules:
        return True
    for s in schedules:
        # Cek apakah hari dan rentang jam cocok
        if s.get("day") is not None and s.get("day") != self.state.day:
            continue
        h_start = s.get("hour_start", 0)
        h_end = s.get("hour_end", 24)
        if h_start <= self.state.hour <= h_end:
            return True
    return True
```
- **Kondisi 1 (No-op)**: Baris 519 memiliki `return True` di luar loop. Jika tidak ada jadwal yang cocok (misal Penatua An jam 02:00 dini hari), fungsi tetap mengembalikan `True`. Pengujian empiris membuktikan helper ini **tidak pernah memblokir aksi apa pun** (100% no-op).
- **Kondisi 2 (Softlock Hari 2+)**: Seluruh 9 NPC pada `data/npcs.json` memiliki field `"day": 1` (misalnya `"schedule": [ { "day": 1, "hour_start": 9, "hour_end": 17, ... } ]`). Jika subagent implementer secara naif mengubah baris 519 menjadi `return False`, maka pada `self.state.day >= 2` (setelah istirahat malam / grounding lintas hari / quest `q_akademi_3c`), evaluasi `s.get("day") != self.state.day` bernilai `True` sehingga semua jadwal diabaikan dan fungsi mengembalikan `False`. Akibatnya, **seluruh NPC di dunia game menjadi terkunci permanen pada Hari ke-2 dan seterusnya**, memicu softlock total pada quest utama, sparing, dan toko.

### Obs-3: Penghilangan Data Side Quest pada Payload Tianyuan Ling (`EP1-T3`, Baris 321–331)
Pada spesifikasi tugas `EP1-T3` baris 321–331 tertera:
```python
# 1. Status Misi
q = session.quest.current_main()
mission = {
    "id": q["id"], "title": q["title"],
    "objective": session.quest.objective_text(q),
    "side_quests": [
        {"id": sq["id"], "title": sq["title"], "objective": session.quest.objective_text(sq)}
        for sq in session.quest.active_side()
    ]
} if q else None
```
- Saat seluruh quest utama selesai (`q_akademi_07` tamat atau dalam masa transisi ketiadaan quest utama aktif), `q` bernilai `None`.
- Konstruksi ternary `... if q else None` menyebabkan variabel `mission` menjadi `None`, sehingga daftar `side_quests` aktif hilang total dari payload endpoint `/api/tianyuan`.

### Obs-4: Risiko Perulangan Modal Penutup Arc 1 di Web UI (`EP2-T3`, Baris 574–608)
Pada spesifikasi tugas `EP2-T3`:
- Saat `q_akademi_07` berada di `state.completed_quests`, `session.view()` akan selalu menyertakan objek `arc_summary`.
- Spesifikasi frontend Web UI belum merinci mekanisme *dismissal / single-fire flag*. Tanpa penanda penutupan pada level UI frontend, setiap kali pemain mengambil aksi lanjutan (misalnya `move`, `hunt`, `craft` di mode eksplorasi bebas pasca-tamat), Web UI akan terus-menerus memunculkan kembali modal ringkasan penutup Arc 1 (*infinite modal popup loop*).

### Obs-5: Kebutuhan Deserialisasi Aman Backward-Compatible (`EP2-T1` & `EP2-T2`)
- Penambahan field `side_quest_cooldowns` (`EP2-T1`) dan `last_hunt_time` (`EP2-T2`) pada dataclass `GameState` memerlukan pembaruan fungsi `GameState.from_dict()`.
- Spesifikasi teks tidak secara eksplisit mewajibkan pemanggilan `.get("side_quest_cooldowns", {})` dan `.get("last_hunt_time", None)`. Jika implementer memakai pengindeksan langsung `d["side_quest_cooldowns"]`, berkas simpanan lama (`saves/*.json`) akan gagal dimuat dengan `KeyError` -> `SaveError`.

### Obs-6: Diskrepansi Matriks Alokasi Berkas Gelombang Eksekusi (§5, Baris 821–827)
- Tabel Matriks Keamanan Eksekusi Paralel (baris 825) mencantumkan berkas yang dimodifikasi untuk Wave 2 Engine hanya `src/engine/session.py` dan `src/cli.py`.
- Namun, spesifikasi `EP2-T2` (baris 491, 542, 547) mewajibkan modifikasi pada `src/engine/state.py` untuk menambahkan field `last_hunt_time`.

---

## 2. Logic Chain (Rantai Penalaran dari Observasi ke Kesimpulan)

1. **Dari Obs-1**: Sistem saat ini berada dalam kondisi hijau stabil (93 test lulus, 16 aturan validasi lulus 0 error). Hal ini membuktikan arsitektur inti sangat kuat dan tidak boleh dirusak oleh ambiguitas spesifikasi tugas baru.
2. **Dari Obs-2**: Spesifikasi `_is_npc_available` pada `EP2-T2` mengandung cacat fatal:
   - Jika diterapkan apa adanya (`return True` di akhir), fitur jadwal NPC tidak berfungsi sama sekali.
   - Jika diperbaiki secara sederhana (`return False`), hardcoded `"day": 1` pada 9 NPC di `data/npcs.json` akan menyebabkan softlock total di Hari 2+.
   - **Inferensi**: Roadmap harus mengoreksi rancangan helper jadwal agar memperlakukan jadwal harian sebagai rutinitas berulang (atau menangani ketiadaan jadwal spesifik hari) serta menyertakan pesan sistem informatif saat NPC di luar jam tugas.
3. **Dari Obs-3**: Struktur payload `_tianyuan_payload()` pada `EP1-T3` menggabungkan `side_quests` di dalam blok `if q else None`.
   - **Inferensi**: Saat quest utama selesai, pemain tetap dapat menjalankan side quest berulang di fase endgame. Hilangnya data `side_quests` saat `q is None` merupakan bug payload yang memutus visibilitas UI. Struktur payload harus dipisahkan menjadi `{"main": ..., "side_quests": [...]}`.
4. **Dari Obs-4**: Payload `arc_summary` yang bersifat persisten di `session.view()` pasca quest tamat akan memicu render ulang modal pada setiap `act()` di frontend jika tidak ada state gating di `app.js`.
   - **Inferensi**: Roadmap harus menambahkan panduan implementasi frontend flag (`arcSummaryDismissed` / tombol penutup) agar eksplorasi bebas pasca-tamat berjalan mulus.
5. **Dari Obs-5 & Obs-6**: Ketiadaan penegasan pola `.get()` pada deserialisasi save dan kelalaian penulisan `src/engine/state.py` pada tabel Wave 2 berpotensi memicu regresi save format dan ambiguitas kepemilikan berkas.
6. **Kesimpulan Akhir**: Walaupun arsitektur umum, pemisahan tugas, dan kepatuhan stdlib sudah sangat baik, adanya celah logika kritis pada jadwal NPC (Obs-2) dan cacat struktural payload (Obs-3 & Obs-4) mewajibkan status **`REQUEST_CHANGES`** agar peta jalan disempurnakan sebelum didelegasikan ke subagent pelaksana.

---

## 3. Caveats (Batasan & Asumsi Investigasi)

- **Batasan Ruang Lingkup**: Evaluasi difokuskan pada integritas logika, kepatuhan 16 aturan validator §14, penanganan edge cases runtime, dan ketiadaan dependensi eksternal pada roadmap `docs/superpowers/plans/next-roadmap.md`.
- **Asumsi Data**: Asumsi bahwa format `data/npcs.json` saat ini dengan `"day": 1` dimaksudkan sebagai data template rutinitas harian untuk Fase 1 (Arc Akademi), bukan jadwal satu kali seumur hidup yang kedaluwarsa setelah hari pertama.

---

## 4. Conclusion (Kesimpulan & Putusan Akhir)

**Putusan**: **`REQUEST_CHANGES`**

### Tindakan Perbaikan Wajib (Actionable Roadmap Corrections):

1. **Perbaikan Logika Jadwal NPC (`EP2-T2`)**:
   Perbarui potongan kode spesifikasi dan template prompt subagent untuk `_is_npc_available(self, npc: dict) -> bool` menjadi:
   ```python
   def _is_npc_available(self, npc: dict) -> bool:
       schedules = npc.get("schedule", [])
       if not schedules:
           return True
       for s in schedules:
           # Cocokkan jadwal: jika hari tidak ditentukan atau hari cocok, evaluasi jam
           # Catatan: di Fase 1, jadwal npcs.json berlaku sebagai jam harian
           h_start = s.get("hour_start", 0)
           h_end = s.get("hour_end", 24)
           if h_start <= self.state.hour <= h_end:
               return True
       return False
   ```
   Dan pastikan pada `_talk` dan `_spar` diberikan pesan log sistem yang ramah ketika NPC sedang tidak bertugas (misal: `"Penatua An sedang bertapa dan tidak menerima tamu saat ini."`).

2. **Perbaikan Struktur Payload Tianyuan Ling (`EP1-T3`)**:
   Perbarui `_tianyuan_payload()` agar `side_quests` tidak terikat pada keberadaan `current_main()`:
   ```python
   def _tianyuan_payload() -> dict:
       if not session:
           return {"mission": None, "memories": [], "unlocked_count": 0, "total_count": 4, "system_log": []}
       
       q = session.quest.current_main()
       mission = {
           "main": {"id": q["id"], "title": q["title"], "objective": session.quest.objective_text(q)} if q else None,
           "side_quests": [
               {"id": sq["id"], "title": sq["title"], "objective": session.quest.objective_text(sq)}
               for sq in session.quest.active_side()
           ],
       }
       ...
   ```

3. **Gating Modal Penutup Arc 1 di Frontend (`EP2-T3`)**:
   Tambahkan kriteria penerimaan di `EP2-T3` bahwa Web UI (`app.js`) harus mengelola status penutupan modal (`arcSummaryDismissed = true`) saat tombol "Lanjut Eksplorasi Bebas" diklik, sehingga modal tidak muncul berulang-ulang pada setiap aksi selanjutnya.

4. **Penegasan Defensive Deserialization (`EP2-T1` & `EP2-T2`)**:
   Tambahkan instruksi eksplisit pada `EP2-T1` dan `EP2-T2` bahwa `GameState.from_dict()` wajib menggunakan `.get("side_quest_cooldowns", {})` dan `.get("last_hunt_time", None)` demi menjaga kompatibilitas mundur save data lama.

5. **Koreksi Tabel Matriks Wave 2 (§5)**:
   Tambahkan `src/engine/state.py` ke dalam daftar berkas yang dimodifikasi pada Wave 2 Engine Track B.

---

## 5. Verification Method (Metode Verifikasi Independen)

Untuk memverifikasi keabsahan seluruh temuan di atas secara mandiri:

1. **Uji Logika Helper Jadwal NPC**:
   Jalankan skrip verifikasi berikut:
   ```bash
   python3 -c "
   import json
   with open('data/npcs.json') as f:
       npcs = json.load(f)['npcs']
   penatua = next(n for n in npcs if n['id'] == 'npc_penatua')

   # Versi roadmap baris 507-520
   def is_avail_roadmap(npc, hour):
       s = npc.get('schedule', [])
       for item in s:
           if item.get('hour_start', 0) <= hour <= item.get('hour_end', 24):
               return True
       return True

   assert is_avail_roadmap(penatua, 2) is True  # Membuktikan bug no-op di jam 02:00
   print('Verifikasi Bug Jadwal: Terkonfirmasi!')
   "
   ```

2. **Uji Payload Tianyuan Saat Main Quest Selesai**:
   Jalankan simulasi berikut:
   ```bash
   python3 -c "
   q = None
   active_side = [{'id': 'q_side_berburu'}]
   mission = {'id': q['id'], 'side_quests': active_side} if q else None
   assert mission is None  # Membuktikan side_quests hilang jika q None
   print('Verifikasi Bug Tianyuan Payload: Terkonfirmasi!')
   "
   ```

3. **Verifikasi Kepatuhan Validator & Test Suite**:
   Jalankan perintah pengujian standar repositori:
   ```bash
   python3 -m pytest -q
   python3 tools/validate_data.py
   python3 -m pytest --cov=src --cov-report=term-missing
   ```
   *Kondisi invalidasi temuan*: Jika kode roadmap yang diuji terbukti dapat membedakan jam aktif NPC tanpa mengunci Hari 2+, mempertahankan side quest saat main quest None, dan mencegah popup loop di web UI, maka rekomendasi perbaikan ini dapat disesuaikan.
