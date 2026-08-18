"""Jenis item & slot equipment — satu sumber kebenaran (F2.1a).

Sebelumnya konstanta ini lokal di `src/validate.py` — melanggar prinsip
"validator import dari modul yang sama dengan eksekusi". Dipindah ke sini;
validator & engine sama-sama import dari modul ini. F2.4 (opsional) tinggal
memperluas set ini + menambah mekanik `use_effects[]` bila arc berikutnya butuh.
"""

from __future__ import annotations

# Jenis item yang punya makna mekanik. Tipe lain (scroll, ...) TIDAK boleh
# dipakai sampai mekaniknya ada — validator menolak saat load (kontrak ketat).
# `key_item`: item naratif/kunci — tersimpan di inventori, tampil di UI, tapi
# tidak bisa dipakai/dipasang (guard _use_item/_equip hanya consumable/weapon).
ITEM_TYPES = {"consumable", "weapon", "key_item"}

# Slot equipment yang didukung engine. Perluasan slot = kerja mekanik baru
# (state schema, _equip dispatch, agregasi stat battle) — bukan sekadar data.
EQUIPMENT_SLOTS = {"weapon"}

# Catatan: key item use effects (data/key_items.json) hidup di `registry.key_items`
# (PER-INSTANCE, bukan global modul) — lihat loader.py. Map: key_item id →
# {"description": str, "consumed": bool, "use_effects": list[dict]}
