# Rencana Implementasi: Skill System Overhaul (v2)

**Tanggal**: 21 Agustus 2026
**Sumber**: Rekomendasi ChatGPT + Claude, diverifikasi oleh Buffy, direvisi berdasarkan feedback ChatGPT
**Status**: Revised — menunggu approval
**Catatan**: Semua perubahan dari v1 ditandai dengan `[REVISI v2]`

---

## Ringkasan Perubahan dari v1

| Dari v1 | Ke v2 | Alasan |
|---------|-------|--------|
| 7 fase | **9 fase** | Tambah Fase 8 (Balance Audit) + Fase 9 (Migration Test) |
| `power` untuk defend (3→30) | **`guard_pct` field terpisah** | [REVISI] Jangan overload `power` untuk semantik berbeda |
| STATUS_KINDS = {dot, stun, weaken, ...} | **STATUS_KINDS = {dot, stun, debuff, hot, buff}** | [REVISI] Taxonomy: `kind` = kategori, `id` = nama status |
| Combo pakai `combo_with` (pairwise) | **Combo pakai `combo_with_tag` (tag-based)** | [REVISI] Lebih scalable dari pairwise |
| Fase 1+2 paralel | **Semua fase sequential** | [REVISI] Balance dependency antar fase |
| Burn = subset dot (tanpa rules) | **Status stacking/refresh/cap rules** | [REVISI] Prevent exploitation |
| Tanpa mitigation cap | **MAX_DAMAGE_REDUCTION = 75%** | [REVISI] Prevent invulnerability |
| Mastery XP dari battle win | **Mastery XP dari technique usage** | [REVISI] Lebih meaningful |
| Passive = power bonus | **Passive = identity passive** | [REVISI] Jangan membuat Pavilion terlalu menentukan |
| Fusion recipe = linear | **Fusion recipe = progression chain** | [REVISI] Logika lebih masuk akal |
| Tanpa balance audit | **Fase 8: Balance Audit** | [REVISI] Wajib sebelum release |
| Tanpa migration test | **Fase 9: Migration Test** | [REVISI] Save backward compatibility |
| `teknik_pamungkas_wuxing` di Fase 2 | **Fusion-only di Fase 7** | [REVISI-Claude] Eksklusivitas fusion |
| Evolution semantics belum diputuskan | **Evolution = REPLACE** | [REVISI-Claude] Teknik dasar hilang, jadi varian |
| guard_pct tanpa cap | **guard_pct ∈ [0, 80] + no level scale** | [REVISI-Claude] Prevent near-invulnerability |

---

## Fase 0: Contract & Bug Fix [REVISI v2]

### Task 0.1: Define canonical element contract
- **File**: `src/engine/battle.py`
- **Tambah**: `SUPPORTED_ELEMENTS = frozenset({"logam", "kayu", "tanah", "air", "api", "angin", "petir", "kosong"})`
- **Tambah**: `NEUTRAL_ELEMENTS = frozenset({"angin", "petir", "kosong"})` — tidak counter apapun, tidak dicounter
- **Ubah**: `DEFAULT_ELEMENT_ADVANTAGE` — tambah explicit neutral handling:
  ```python
  DEFAULT_ELEMENT_ADVANTAGE = {
      "logam": "kayu",
      "kayu": "tanah",
      "tanah": "air",
      "air": "api",
      "api": "logam",
  }
  ```
  Neutral elements: `adv.get(elem_att) == elem_def` returns None → mult = 1.0 (sudah benar)
- **Note**: Jangan bergantung pada "tidak ada di dictionary berarti aman". Validator harus tahu secara eksplisit.

### Task 0.2: Fix companion element mismatch
- **File**: `data/companions.json`
- **Ubah**: `earth`→`tanah`, `wind`→`angin`, `fire`→`api`, `water`→`air`, `metal`→`logam`, `wood`→`kayu`, `void`→`kosong`, `lightning`→`petir`

### Task 0.3: Add element ke enemies.csv + validator
- **File**: `data/enemies.csv`
- **Tambah**: Column `element` — semua enemy WAJIB punya element
- **Data**:
  - `penjaga_formation`: `logam`
  - `binatang_hutan`: `kayu`
  - `serigala_bayangan`: `api`
  - `golem_batu`: `tanah`
  - `guard_spirit`: `logam`
- **File**: `src/validate.py`
- **Tambah**: Validasi `enemy.element ∈ SUPPORTED_ELEMENTS` — wajib, bukan optional

### Task 0.4: Add element ke 5 teknik existing
- **File**: `data/techniques.csv`
- **Isi**:
  - `teknik_dasar`: (kosong — netral)
  - `teknik_wuxin`: `tanah`
  - `teknik_jianxin`: `logam`
  - `teknik_yanzhi`: `kayu`
  - `teknik_liuguang`: `air`

### Task 0.5: Fix defend semantics — tambah `guard_pct` [REVISI v2]
- **File**: `data/techniques.csv`
- **Tambah column**: `guard_pct` (opsional, default 0)
- **Data existing**:
  - `teknik_wuxin`: `guard_pct=30` (power tetap 3 untuk compatibilitas)
  - `teknik_liuguang`: `guard_pct=40`
- **File**: `src/engine/battle.py`
- **Ubah**: `_use_technique()` — untuk defend, baca `guard_pct` dulu, fallback ke `power`:
  ```python
  elif kind == "defend":
      pct = int(tek.get("guard_pct", 0)) or power
      b["player_guard"] = pct
      add_log(self.state, "battle", f"{tek['name']} — damage masuk dikurangi {pct}%.")
  ```
- **Note**: `power` tetap kompatibel dengan semantic lama. `guard_pct` secara eksplisit = mitigasi.
- **[REVISI v2 — Claude]**: `guard_pct` **TIDAK scale dengan level** — dibaca langsung dari data, bukan melalui formula `power × (1 + (level-1) × growth)`. Alasan: jika guard_pct=55% di-scale ke level 5 = 88% → near invulnerability. Defend mitigation harus statis atau pakai growth formula terpisah yang lebih kecil.
- **[REVISI v2 — Claude]**: Tambah validator range check: `guard_pct ∈ [0, 80]` — mencegah input manual yang overflow. `MAX_DAMAGE_REDUCTION = 75` sudah ada di Task 1.5, tapi guard_pct perlu cap individual juga.

### Task 0.6: Add regression tests untuk Fase 0
- **File**: `tests/test_element_contract.py` (baru)
- **Test**:
  - Semua companions punya element ∈ SUPPORTED_ELEMENTS
  - Semua enemies punya element ∈ SUPPORTED_ELEMENTS
  - Semua techniques punya element ∈ SUPPORTED_ELEMENTS ∪ {""}
  - Element advantage trigger correctly (logam vs kayu = 1.5x)
  - Neutral element = 1.0x (no advantage)
  - Defend guard_pct works correctly

---

## Fase 1: Status Foundation [REVISI v2]

### Task 1.1: Define status taxonomy
- **File**: `src/engine/battle.py`
- **Ubah**: `STATUS_KINDS = frozenset({"dot", "stun", "debuff", "hot", "buff"})`
- **Note**: `kind` = kategori engine. `id` = nama status (burn, weaken, expose, regen, guard, focus)

### Task 1.2: Define status config di config.json
- **File**: `data/config.json`
- **Ubah**: `battle.statuses`:
  ```json
  {
    "burn": {"kind": "dot", "name": "Terbakar", "damage_pct": 5, "max_duration": 10},
    "poison": {"kind": "dot", "name": "Racun", "damage_pct": 3, "max_duration": 10},
    "weaken": {"kind": "debuff", "name": "Melemah", "atk_mult": 0.8, "max_duration": 5},
    "expose": {"kind": "debuff", "name": "Terbuka", "def_mult": 0.7, "max_duration": 5},
    "stun": {"kind": "stun", "name": "Terpana", "max_duration": 3},
    "regen": {"kind": "hot", "name": "Regenerasi", "heal_pct": 3, "max_duration": 5},
    "guard": {"kind": "buff", "name": "Bertahan", "dmg_reduction": 15, "max_duration": 3},
    "focus": {"kind": "buff", "name": "Fokus", "power_mult": 1.2, "max_duration": 2}
  }
  ```

### Task 1.3: Status stacking/refresh/cap rules [REVISI v2]
- **File**: `src/engine/battle.py`
- **Tambah rules**:
  ```
  DoT (burn, poison):
    tidak stack damage
    reapply → duration diperpanjang (add remaining)
    max duration = config.max_duration

  Debuff (weaken, expose):
    tidak stack magnitude
    reapply → refresh duration ke max
    max duration = config.max_duration

  Stun:
    tidak stack
    refresh duration

  Buff (guard, focus):
    tidak stack magnitude
    reapply → refresh duration
    max duration = config.max_duration
  ```

### Task 1.4: Implement status processing di battle loop
- **File**: `src/engine/battle.py`
- **Ubah**: `_apply_player_statuses()` — expand untuk handle semua kind:
  - `dot`: damage per turn (sudah ada)
  - `stun`: skip turn (sudah ada)
  - `debuff`: kurangi stat (attack/defense) berdasarkan config
  - `hot`: heal per turn
  - `buff`: tambah stat (damage reduction/power) berdasarkan config
- **Tambah**: Durasi tracking — `player_statuses: dict[str, int]` → `{status_id: turns_remaining}`
- **Tambah**: Tick durasi — setiap turn, kurangi 1. Hapus saat 0.

### Task 1.5: Mitigation stacking cap [REVISI v2]
- **File**: `src/engine/battle.py`
- **Tambah**: `MAX_DAMAGE_REDUCTION = 75`
- **Ubah**: Damage calculation — gunakan multiplicative stacking:
  ```python
  reductions = []
  if b.get("player_guard"):
      reductions.append(b["player_guard"] / 100)
  if "guard" in b.get("player_statuses", {}):
      reductions.append(cfg["statuses"]["guard"]["dmg_reduction"] / 100)
  # Apply passive reductions
  total_reduction = 1.0
  for r in reductions:
      total_reduction *= (1 - r)
  total_reduction = max(1 - MAX_DAMAGE_REDUCTION/100, total_reduction)
  dmg = max(1, int(dmg * total_reduction))
  ```

### Task 1.6: Deterministic RNG handling [REVISI v2]
- **File**: `src/engine/battle.py`
- **Catatan**: Engine sudah pakai `random.random()` global. Status procs harus pakai pattern yang sama:
  ```python
  if random.random() < chance:
      apply_status(...)
  ```
- **Note**: Tidak perlu seeded RNG — engine sudah konsisten pakai global random. Test bisa kontrol via mock.

### Task 1.7: Update validator
- **File**: `src/validate.py`
- **Tambah**: Validasi `battle.statuses[id].kind ∈ STATUS_KINDS` — validasi terhadap **`kind`** (kategori: dot/stun/debuff/hot/buff), BUKAN terhadap `id` (nama: burn/weaken/expose). `id` adalah key di config.json, bukan field yang divalidasi against STATUS_KINDS.
- **Tambah**: Validasi `battle.statuses[id].max_duration` ada dan > 0
- **Tambah**: Validasi `apply_status` di techniques.csv harus ada di `battle.statuses` keys

### Task 1.8: Test
- **File**: `tests/test_status_effects.py` (baru)
- **Test**:
  - Status application (burn, weaken, expose, regen, guard, focus)
  - Duration tick (decreases each turn, removed at 0)
  - Stacking rules (no double damage, refresh duration)
  - Mitigation cap (max 75% reduction)
  - Status interaction (guard + defend = multiplicative)

---

## Fase 2: Technique Expansion [REVISI v2]

### Task 2.1: Tambah 11 teknik ke techniques.csv
- **File**: `data/techniques.csv`
- **Tambah columns**: `tags`, `combo_with_tag`, `apply_status`, `status_chance`, `status_duration`

**Catatan balance**: Angka ini FINAL SETELAH Fase 1 stabil. Power/Qi ratio = 1.5-2.5 untuk attack, lebih rendah untuk utility.

#### Chu Ji (2 tambahan)
| ID | Kind | Power | Qi | Element | Tags | Status |
|----|------|-------|-----|---------|------|--------|
| `teknik_langkah_bayangan` | defend | 2 | 2 | `air` | defensive, evasion | — |
| `teknik_gelombang_qi` | attack | 6 | 3 | `air` | offensive, combo_starter | — |

#### Xuan Shi (3 tambahan)
| ID | Kind | Power | Qi | Element | Tags | Status |
|----|------|-------|-----|---------|------|--------|
| `teknik_pedang_logam` | attack | 12 | 5 | `logam` | pedang, offensive, combo_finisher | — |
| `teknik_perisai_tanah` | defend | 2 | 3 | `tanah` | defensive, guard_pct=35 | — |
| `teknik_pemulihan_kayu` | heal | 9 | 5 | `kayu` | heal, regen | regen 50% 2 turns |

#### Di Shi (3 tambahan)
| ID | Kind | Power | Qi | Element | Tags | Status |
|----|------|-------|-----|---------|------|--------|
| `teknik_badai_api` | attack | 18 | 7 | `api` | offensive, combo_starter | burn 40% 2 turns |
| `teknik_aliran_air` | heal | 14 | 6 | `air` | heal | — |
| `teknik_benteng_logam` | defend | 2 | 5 | `logam` | defensive, guard_pct=50 | — |

#### Tian Shi (3 tambahan)
| ID | Kind | Power | Qi | Element | Tags | Status |
|----|------|-------|-----|---------|------|--------|
| `teknik_naga_kayu` | attack | 28 | 9 | `kayu` | offensive, combo_finisher | — |
| `teknik_inti_bumi` | heal | 20 | 8 | `tanah` | heal | — |
| `teknik_tirai_air` | defend | 2 | 7 | `air` | defensive, guard_pct=60 | — |

#### Shen Wu — TIDAK ada teknik baru di Fase 2
**[REVISI v2 — Claude]**: `teknik_pamungkas_wuxing` (Siklus Wuxing Sempurna) dipindahkan ke **Fase 7 (Fusion)** sebagai fusion-only technique. Alasan: jika teknik ini bisa didapat dari quest DAN fusion, fusion kehilangan nilai prestise/eksklusif. Teknik Shen Wu hanya tersedia melalui fusion chain.

### Task 2.2: Tambah tags ke semua teknik
- **File**: `data/techniques.csv`
- **Tambah column**: `tags` (comma-separated)
- **Tag yang didukung**: `pedang`, `offensive`, `defensive`, `heal`, `combo_starter`, `combo_finisher`, `evasion`, `guard`

### Task 2.3: Update quest rewards + loot tables
- **File**: `data/quests/*.json`, `data/items.csv`
- **Tambah**: Technique scrolls sebagai quest reward di Arc III-VII

### Task 2.4: Update validator
- **File**: `src/validate.py`
- **Tambah**: Validasi semua 16 teknik (5 existing + 11 baru) tervalidasi dengan benar. `teknik_pamungkas_wuxing` ditambahkan di Fase 7 (fusion-only).

### Task 2.5: Test
- **Command**: `python3 -m pytest -v --tb=short`

---

## Fase 3: Elemental Mastery [REVISI v2]

### Task 3.1: Tambah element_mastery ke GameState
- **File**: `src/engine/state.py`
- **Tambah field**: `element_mastery: dict = field(default_factory=lambda: {"logam": 0, "kayu": 0, "tanah": 0, "air": 0, "api": 0})`
- **Tambah**: SCHEMA_VERSION migration (v7→v8) — default 0 untuk save lama

### Task 3.2: Mastery XP dari technique usage [REVISI v2]
- **File**: `src/engine/battle.py`
- **Ubah**: `_use_technique()` — setelah pakai teknik, tambah XP:
  ```python
  tek_element = tek.get("element")
  if tek_element and tek_element in state.element_mastery:
      state.element_mastery[tek_element] += 1
  ```
- **Note**: +1 per usage, bukan +5 per battle win. Lebih meaningful.

### Task 3.3: Mastery levels + damage modifier
- **File**: `src/engine/battle.py`
- **Tambah**: Fungsi `get_mastery_level(state, element)`:
  ```python
  def get_mastery_level(state, element):
      xp = state.element_mastery.get(element, 0)
      if xp >= 600: return 3
      if xp >= 300: return 2
      if xp >= 100: return 1
      return 0
  ```
- **Tambah**: Mastery bonus di `_calc_damage()`:
  ```python
  mastery_level = get_mastery_level(state, elem_att)
  mult *= (1 + mastery_level * 0.05)  # +5% per level, max +15%
  ```

### Task 3.4: Mastery cap [REVISI v2]
- **Catatan**: Mastery bonus = max 15%. Bersama element advantage (20%), passive (5-10%), combo (15-25%) — total max modifier = ~75%. Masih di bawah MAX_DAMAGE_REDUCTION (75%).

### Task 3.5: Tambah mastery ke session view + web UI
- **File**: `src/engine/session.py`, `web/static/app.js`
- **Tambah**: Mastery panel — tampilkan level mastery per elemen

### Task 3.6: Update validator
- **File**: `src/validate.py`
- **Tambah**: Validasi element_mastery di save data

### Task 3.7: Test
- **Command**: `python3 -m pytest -v --tb=short`

---

## Fase 4: Pavilion Passive [REVISI v2]

### Task 4.1: Buat data passives.json
- **File**: `data/passives.json` (baru)
- **Data** (identity passive, bukan power passive):

```json
{
  "passives": [
    {
      "id": "passive_sword_intent",
      "name": "Sword Intent",
      "description": "+5% damage untuk teknik bertag pedang",
      "effect": "bonus_damage_tag",
      "tag": "pedang",
      "value": 5,
      "realm_required": "realm_chuji",
      "source": "pavilion_jianxin"
    },
    {
      "id": "passive_flowing_qi",
      "name": "Flowing Qi",
      "description": "+1 Qi saat menggunakan defend",
      "effect": "qi_on_defend",
      "value": 1,
      "realm_required": "realm_chuji",
      "source": "pavilion_wuxin"
    },
    {
      "id": "passive_phoenix_blood",
      "name": "Phoenix Blood",
      "description": "+10% heal effectiveness saat HP < 30%",
      "effect": "heal_bonus_low_hp",
      "threshold_hp_pct": 30,
      "value": 10,
      "realm_required": "realm_chuji",
      "source": "pavilion_yanzhi"
    },
    {
      "id": "passive_earth_guardian",
      "name": "Earth Guardian",
      "description": "+5% damage reduction saat HP > 70%",
      "effect": "damage_reduction_high_hp",
      "threshold_hp_pct": 70,
      "value": 5,
      "realm_required": "realm_chuji",
      "source": "pavilion_liuguang"
    }
  ]
}
```

**Catatan**: Hanya 4 passive pavilion. Tidak ada `qi_per_turn` universal — terlalu kuat dengan Wuxin's +1 Qi defend.

### Task 4.2: Load passives di DataRegistry
- **File**: `src/loader.py`
- **Tambah**: Load `passives.json` → `registry.passives`

### Task 4.3: Apply passives saat battle mulai
- **File**: `src/engine/battle.py`
- **Ubah**: `BattleEngine.start()` — baca passives dan apply modifiers

### Task 4.4: Tambah passive ke GameState
- **File**: `src/engine/state.py`
- **Tambah field**: `passives: list = field(default_factory=list)`
- **Tambah**: SCHEMA_VERSION migration (v8→v9)

### Task 4.5: Assign passive ke pavilion
- **File**: `data/config.json`
- **Ubah**: Setiap pavilion punya `passive` field

### Task 4.6: Test
- **Command**: `python3 -m pytest -v --tb=short`

---

## Fase 5: Synergy System [REVISI v2]

### Task 5.1: Tag-based synergy [REVISI v2]
- **File**: `data/techniques.csv`
- **Tambah columns**: `combo_with_tag`, `combo_bonus_pct`
- **Data**:
  - `teknik_pedang_logam`: `combo_with_tag=pedang`, `combo_bonus_pct=25`
  - `teknik_naga_kayu`: `combo_with_tag=combo_starter`, `combo_bonus_pct=20`
  - `teknik_pamungkas_wuxing`: `combo_with_tag=combo_finisher`, `combo_bonus_pct=15` (fusion-only, dari Fase 7)
- **Note**: Tag-based lebih scalable — bisa tambah 30 teknik tanpa membuat pairwise kombinasi

### Task 5.2: Track last_technique_used + last_technique_tags
- **File**: `src/engine/battle.py`
- **Tambah**: `b["last_technique_used"] = None` + `b["last_technique_tags"] = []`

### Task 5.3: Apply synergy bonus
- **File**: `src/engine/battle.py`
- **Ubah**: `_use_technique()` — cek synergy:
  ```python
  combo_tag = tek.get("combo_with_tag", "")
  if combo_tag and combo_tag in b.get("last_technique_tags", []):
      bonus_pct = int(tek.get("combo_bonus_pct", 0))
      power = int(power * (1 + bonus_pct / 100))
  ```

### Task 5.4: Synergy cap — max 1 per technique use [REVISI v2]
- **File**: `src/engine/battle.py`
- **Tambah**: Flag `b["synergy_used_this_technique"]` — reset setiap kali teknik baru dipakai
- **Catatan**: Lebih tepat dari "per turn" karena 1 turn = 1 technique

### Task 5.5: Update validator
- **File**: `src/validate.py`
- **Tambah**: Validasi `combo_with_tag` ∈ tags yang exist

### Task 5.6: Test
- **Command**: `python3 -m pytest -v --tb=short`

---

## Fase 6: Technique Evolution [REVISI v2]

### Task 6.1: Design evolution structure
- **File**: `docs/superpowers/specs/2026-08-21-technique-evolution-design.md` (baru)
- **[REVISI v2 — Claude]**: **Evolution = REPLACE** — teknik dasar HILANG dan digantikan oleh varian. Alasan:
  - Jika menambah (base + variant), pemain punya 2 teknik sejenis → redundan
  - Replace memaksa pemain memilih playstyle → meaningful choice
  - `apply_status` dari teknik dasar perlu dipindah/diwariskan ke varian
  - Branch_group validation: hanya 1 teknik per branch_group yang boleh ter-unlock
- **Isi**: Spesifikasi evolution per pavilion:
  - Wuxin: `teknik_wuxin` → `teknik_wuxin_perisai` (defend murni, higher guard_pct) vs `teknik_wuxin_balas` (defend + counter)
  - Jianxin: `teknik_jianxin` → `teknik_jianxin_penembus` (bonus vs defense tinggi) vs `teknik_jianxin_pemecah` (chance weaken)
  - Yanzhi: `teknik_yanzhi` → `teknik_yanzhi_dalam` (heal besar) vs `teknik_yanzhi_celup` (heal + cleanse)
  - Liuguang: `teknik_liuguang` → `teknik_liuguang_arus` (defend + qi restore) vs `teknik_liuguang_pantul` (defend + reflect)

### Task 6.2: Tambah evolution fields ke techniques.csv
- **File**: `data/techniques.csv`
- **Tambah columns**: `branch_group`, `requires_technique`

### Task 6.3: Implement evolution validation + unlock logic
- **File**: `src/validate.py`, `src/engine/session.py`

### Task 6.4: Test
- **Command**: `python3 -m pytest -v --tb=short`

---

## Fase 7: Technique Fusion [REVISI v2]

### Task 7.1: Redesign fusion recipes [REVISI v2]
- **File**: `data/fusion_recipes.json` (baru)
- **Data** (progression chain, bukan linear):
  ```json
  {
    "fusions": [
      {
        "id": "fusion_pedang_api",
        "name": "Pedang Api Membara",
        "requires": ["teknik_jianxin", "teknik_badai_api"],
        "requires_level": 2,
        "result": "teknik_pedang_api_membara",
        "description": "Fusi pedang dan api"
      },
      {
        "id": "fusion_wuxing",
        "name": "Siklus Wuxing Sempurna",
        "requires": ["teknik_pedang_api_membara", "teknik_naga_kayu"],
        "requires_level": 3,
        "result": "teknik_pamungkas_wuxing",
        "description": "Fusi puncak — menguasai siklus lima unsur"
      }
    ]
  }
  ```

### Task 7.2-7.5: Implementasi (load, check, unlock, quest)
- **Files**: `src/loader.py`, `src/engine/session.py`, `data/quests/*.json`

### Task 7.6: Test
- **Command**: `python3 -m pytest -v --tb=short`

---

## Fase 8: Balance Audit [BARU v2]

### Task 8.1: Balance spreadsheet
- **File**: `docs/superpowers/specs/2026-08-21-balance-audit.md` (baru)
- **Isi**: Hitung DPS untuk setiap build di setiap realm:

```
Build yang ditest:
1. Pure Attack (teknik_dasar + upgrade)
2. Defensive (defend + guard + passive)
3. Heal/Sustain (heal + regen + passive)
4. Elemental (element advantage + mastery)
5. Combo (starter + finisher)
6. Hybrid (campuran)

Metric:
- Damage per turn
- Qi efficiency
- Mitigation %
- Heal per turn
- Time to kill (musuh realm sama)
- Time to die (dari musuh realm sama)
```

### Task 8.2: Test scenarios
- **File**: `tests/test_balance.py` (baru)
- **Test**:
  - Chu Ji vs Chu Ji enemy
  - Xuan Shi vs Xuan Shi enemy
  - dst.
  - Pastikan tidak ada build yang selalu dominan

### Task 8.3: Adjust numbers jika perlu
- **File**: `data/techniques.csv`, `data/config.json`
- **Catatan**: Ini adalah iterative process — adjust → test → adjust

---

## Fase 9: Migration Test [BARU v2]

### Task 9.1: Save migration test
- **File**: `tests/test_migration.py` (baru)
- **Test**:
  ```
  v7 save → load → migration → save → load again → state preserved
  ```
- **Pastikan**:
  - Technique lama tetap dimiliki
  - Pavilion tetap sama
  - Companion tetap sama
  - Quest progress tetap sama
  - Flags tetap sama
  - Memory tetap sama
  - Realm tetap sama
  - Element mastery default 0
  - Passive default sesuai desain
  - Tidak ada data lama yang hilang

### Task 9.2: Backward compatibility test
- **File**: `tests/test_backward_compat.py` (baru)
- **Test**:
  - Data lama tanpa field baru tetap valid
  - Default values applied correctly
  - No crash on old save files

---

## Estimasi Total (v2)

| Fase | Hari | Effort | Dependencies |
|------|------|--------|-------------|
| Fase 0: Contract & Bug Fix | 1-2 | Small | — |
| Fase 1: Status Foundation | 2-3 | Medium | Fase 0 |
| Fase 2: Technique Expansion | 1-2 | Small | Fase 1 |
| Fase 3: Elemental Mastery | 2 | Medium | Fase 0, Fase 1 |
| Fase 4: Pavilion Passive | 1-2 | Medium | Fase 0 |
| Fase 5: Synergy System | 2 | Medium | Fase 1, Fase 2 |
| Fase 6: Technique Evolution | 2-3 | Large | Fase 2 |
| Fase 7: Technique Fusion | 2 | Large | Fase 2, Fase 6 |
| Fase 8: Balance Audit | 2-3 | Medium | Semua fase |
| Fase 9: Migration Test | 1 | Small | Fase 3, Fase 4 |
| **Total** | **18-23 hari** | | |

## 7 Perubahan Wajib dari Feedback ChatGPT [REVISI v2]

| # | Perubahan | Status |
|---|-----------|--------|
| 1 | Jangan overload `power` untuk defend; gunakan `guard_pct` | ✅ Task 0.5 |
| 2 | Tetapkan canonical element contract + validator | ✅ Task 0.1 |
| 3 | Perbaiki taxonomy STATUS_KINDS (kind = kategori, id = nama) | ✅ Task 1.1 |
| 4 | Tetapkan aturan status stacking/refresh/duration cap | ✅ Task 1.3 |
| 5 | Batasi stacking mitigation + global cap 75% | ✅ Task 1.5 |
| 6 | Ubah combo dari pairwise ke tag-based synergy | ✅ Task 5.1 |
| 7 | Tambahkan Fase 8 Balance Audit + Fase 9 Migration Test | ✅ Fase 8, 9 |

## 5 Perubahan Tambahan dari Feedback Claude [REVISI v2-Claude]

| # | Perubahan | Status |
|---|-----------|--------|
| 1 | `guard_pct` does NOT scale with level + range check [0, 80] | ✅ Task 0.5 |
| 2 | `teknik_pamungkas_wuxing` = fusion-only (hapus dari Fase 2) | ✅ Task 2.1, 7.1 |
| 3 | Evolution semantics = REPLACE (teknik dasar hilang) | ✅ Task 6.1 |
| 4 | Validator pakai `kind` (kategori), bukan `id` (nama status) | ✅ Task 1.7 |
| 5 | Validator `apply_status` harus exist di `battle.statuses` keys | ✅ Task 1.7 |

## Yang TIDAK Dilakukan (tetap dari v1)

| Fitur | Alasan |
|-------|--------|
| Cooldown per skill | Bikin battle lambat |
| Skill tree kompleks | Over-engineering |
| Multi-resource system | Over-engineering |
| Random proc berlebihan | Sulit balance |
| Combo chain panjang | Max 1 synergy per technique |
| Skill rarity | Tidak cocok tema cultivation |
| Weapon-specific skills | Terlalu kompleks |
| Auto-counter element (Pedang Lima Unsur) | Melemahkan strategi elemen |
| Qi_per_turn universal passive | Terlalu kuat dengan Wuxin |

## Konsistensi dengan Engine Philosophy (tetap)

- ✅ **Data-driven**: Semua teknik baru = data CSV/JSON
- ✅ **Dispatch tables**: Status effects pakai dispatch, bukan if/elif
- ✅ **Backward compatible**: Field baru optional, default value untuk data lama
- ✅ **Validator**: Semua data tervalidasi saat startup
- ✅ **No new dependencies**: Tetap stdlib-only
- ✅ **UI text Bahasa Indonesia**: Semua nama teknik dan deskripsi dalam Bahasa Indonesia
- ✅ **Explicit validation over silent failure**: Semua field baru punya validator
