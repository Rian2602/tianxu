# API Reference — Tian Xu: Second Life

## Endpoint

```
POST /api/action
Content-Type: application/json

{
  "action": {
    "type": "<action_type>",
    ...parameters
  }
}
```

## Action Types

| Action | Parameters | Description |
|--------|-----------|-------------|
| `talk` | `npc: str` | Bicara dengan NPC |
| `dialog_choice` | `choice_index: int` | Pilih opsi dialog (-1 = skip) |
| `move` | `to: str` | Pindah ke lokasi |
| `choose` | `option: str` | Pilih opsi quest (akademi, dll) |
| `battle_action` | `action: str, ...` | Aksi dalam battle (lihat bawah) |
| `use_item` | `item: str` | Pakai item consumable |
| `use_key_item` | `item: str` | Pakai key_item (scroll/resep) |
| `equip` | `item: str` | Pasang senjata |
| `meditate` | — | Meditasi (butuh dantian penuh) |
| `spar` | `npc: str` | Sparing dengan NPC |
| `hunt` | `hunt?: str` | Berburu (zone optional) |
| `search` | — | Cari item di area |
| `rest` | — | Istirahat di kamar |
| `shop_buy` | `item: str, count?: int` | Beli dari pedagang |
| `shop_sell` | `item: str, count?: int` | Jual ke pedagang |
| `craft` | `recipe: str` | Racik resep |
| `upgrade_technique` | `technique: str` | Upgrade teknik |
| `learn_technique` | `technique: str` | Pelajari teknik |
| `unlock_technique` | `technique: str` | Buka teknik terkunci |
| `fuse_technique` | `source1: str, source2: str` | Gabung teknik |
| `switch_companion` | `companion: str` | Ganti companion aktif |
| `companion_heal` | — | Heal companion (Qi cost) |
| `mine` | `mine?: str` | Tambang (zone optional) |
| `save` | `save_name: str` | Simpan game |
| `advance_time` | `hours?: int` | Lewatkan waktu |

## Battle Actions

Dikirim via `{"type": "battle_action", "action": "<battle_action>"}`

| Battle Action | Parameters | Description |
|---------------|-----------|-------------|
| `attack` | — | Serang musuh |
| `technique` | `technique: str` | Pakai teknik |
| `item` | `item: str` | Pakai item di battle |
| `guard` | — | Bertahan (50% damage reduction) |
| `flee` | — | Kabur dari battle |
| `companion_heal` | — | Heal companion (Qi cost) |
