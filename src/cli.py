#!/usr/bin/env python3
"""CLI Tian Xu: Second Life — main game di terminal (vertical slice).

Pemakaian:
    python3 src/cli.py            # mulai baru
    python3 src/cli.py -l save1   # lanjut dari save
"""

from __future__ import annotations

import sys
from pathlib import Path

# jalankan baik sebagai `python3 src/cli.py` maupun `python3 -m src.cli`
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.loader import DataRegistry
from src.engine.session import GameSession, SaveError

RESET = "\033[0m"
GOLD = "\033[33m"
CYAN = "\033[36m"
RED = "\033[31m"
GREEN = "\033[32m"
DIM = "\033[2m"
BOLD = "\033[1m"


def color(tag: str) -> str:
    return {
        "narration": "",
        "npc": CYAN,
        "player": "",
        "system": GOLD,
        "battle": RED,
    }.get(tag, "")


def print_header(session: GameSession) -> None:
    v = session.view()
    loc = v["location"]
    p = v["player"]
    print()
    print(f"{BOLD}═══ Hari {v['day']}, jam {v['hour']:02d}:00 — {loc['name']} ═══{RESET}")
    print(DIM + loc["description"] + RESET)
    print()
    print(f"{BOLD}Chen Xu{RESET} — {p['realm']} Lv.{p['realm_level']} | "
          f"HP {p['hp']}/{p['hp_max']} | Qi {p['qi']}/{p['qi_max']} | "
          f"{GOLD}{p['gold']} Koin{RESET} | Moral {p['morality']} | Exp {p['exp']}/{p['exp_next']}")
    if p["academy"]:
        for a in session.reg.config["academies"]:
            if a["id"] == p["academy"]:
                print(DIM + f"Akademi: {a['name']} ({a['hanzi']} {a['pinyin']})" + RESET)
    w = p.get("equipment", {}).get("weapon")
    if w:
        wi = session.reg.item(w)
        if wi:
            print(DIM + f"Senjata: {wi['name']} (+{wi.get('power', 0)} serangan)" + RESET)
    comp = v.get("companion")
    if comp:
        status = " (KO — pulih di titik aman)" if comp["hp"] <= 0 else ""
        print(DIM + f"Roh: {comp['name']} HP {comp['hp']}/{comp['hp_max']}{status}" + RESET)
    if v["current_quest"]:
        q = v["current_quest"]
        print(f"{GOLD}◇ Quest: {q['title']}{RESET}")
        print(f"  {q['objective']}")
    for sq in v["side_quests"]:
        print(f"◇ Side: {sq['title']} — {sq['objective']}")
    for m in v["memories"]:
        print(DIM + f"天缘灵 · Ingatan: {m['title']}" + RESET)


def print_log(session: GameSession, start: int) -> None:
    for e in session.state.log[start:]:
        txt = e["text"]
        prefix = f"[H{e['day']}:{e['hour']:02d}] " if False else ""
        print(color(e["type"]) + txt + RESET)


def explore_menu(session: GameSession) -> None:
    v = session.view()
    print()
    print("Kau bisa:")
    # NPC di lokasi
    npcs = [n for n in session.reg.npcs if n.get("location") == v["location"]["id"]]
    for n in npcs:
        spar = " (sparing)" if n.get("can_spar") else ""
        shop = " (toko)" if n.get("shop") else ""
        print(f"  {GREEN}[bicara]{RESET} {n['name']}{spar}{shop}")
    for c in v["location"]["connections"]:
        lc = session.reg.location(c)
        print(f"  {GREEN}[pindah]{RESET} {lc['name']}")
    if v["location"]["id"] == "loc_wilayah_berburu":
        print(f"  {GREEN}[berburu]{RESET} cari pertarungan · {GREEN}[cari]{RESET} herba")
    if v["location"]["is_safe"]:
        print(f"  {GREEN}[meditasi]{RESET} berkultivasi (jam) · {GREEN}[istirahat]{RESET} pulihkan HP/Qi · {GREEN}[simpan]{RESET} game")
    for n in npcs:
        if n.get("can_spar"):
            print(f"  {GREEN}[spar]{RESET} latihan vs {n['name']}")
    if v["location"]["is_safe"] and any(i["id"] == "material_herba" and i["count"] >= 2 for i in v["inventory"]):
        print(f"  {GREEN}[racik]{RESET} pil dari bahan (rc_pil_qi / rc_pil_pemulihan)")
    if any((session.reg.item(i["id"]) or {}).get("type") == "weapon" for i in v["inventory"]):
        print(f"  {GREEN}[pasang]{RESET} <senjata> — pasang ke slot senjata")
    print(f"  {GREEN}[tunggu]{RESET} beberapa jam · {GREEN}[pakai]{RESET} <item> · {GREEN}[ingatan]{RESET} baca ingatan")
    print(f"  {GREEN}[bantuan]{RESET} · {GREEN}[keluar]{RESET}")


def dialog_view(session: GameSession) -> None:
    v = session.view()
    d = v["dialog"]
    if not d:
        return
    sp = d["speaker"]
    if sp == "narration":
        print(DIM + d["text"] + RESET)
    elif sp.startswith("npc:"):
        n = session.reg.npc(sp[4:])
        print(CYAN + f"{n['name']}: {d['text']}" + RESET)
    elif sp == "system":
        print(GOLD + d["text"] + RESET)
    else:
        print(d["text"])
    if not d["choices"]:
        print(DIM + "(tekan enter untuk melanjutkan)" + RESET)
    else:
        for c in d["choices"]:
            print(f"  {GREEN}[{c['index'] + 1}]{RESET} {c['label']}")


def battle_view(session: GameSession) -> None:
    v = session.view()
    b = v["battle"]
    p = b["player"]
    print(f"{BOLD}⚔️  Battle{RESET} | HP {p['hp']}/{p['hp_max']} | Qi {p['qi']}/{p['qi_max']}")
    for f in b["foes"]:
        print(f"  {RED}{f['name']}{RESET} HP {f['hp']}/{f['hp_max']}")
    comp = b.get("companion")
    if comp:
        print(f"  {GREEN}{comp['name']}{RESET} (otomatis) HP {comp['hp']}/{comp['hp_max']}")
    print("Aksi: [1] Serang  [2] Teknik  [3] Item  [4] Bertahan  [5] Kabur")


def choose_view(session: GameSession) -> None:
    v = session.view()
    ch = v["choose"]
    if not ch:
        return
    print(GOLD + ch["prompt"] + RESET)
    for i, o in enumerate(ch["options"], 1):
        print(f"  {GREEN}[{i}]{RESET} {o['label']}")


def main() -> None:
    registry = DataRegistry()
    args = sys.argv[1:]
    if "-l" in args:
        idx = args.index("-l")
        save_name = args[idx + 1] if len(args) > idx + 1 else "save1"
        try:
            session = GameSession.load(registry, save_name)
            print(f"Memuat save '{save_name}'...")
        except FileNotFoundError:
            print(f"Save '{save_name}' tidak ditemukan. Memulai baru.")
            session = GameSession.new(registry)
        except SaveError as e:
            print(f"Gagal memuat save '{save_name}': {e}")
            return
    else:
        session = GameSession.new(registry)

    log_start = 0
    print(f"{GOLD}{BOLD}═══ 天缘灵 · TIAN XU: SECOND LIFE — Arc Akademi ═══{RESET}")
    print("Ketik 'bantuan' untuk daftar perintah, 'keluar' untuk berhenti.\n")

    arc_ended = False
    while True:
        v = session.view()
        print_header(session)
        print_log(session, log_start)
        log_start = len(session.state.log)

        mode = v["mode"]
        if mode == "dialog":
            dialog_view(session)
        elif mode == "battle":
            battle_view(session)
        elif mode == "choose":
            choose_view(session)
        else:
            explore_menu(session)

        try:
            raw = input(f"\n{GOLD}> {RESET}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw and mode != "dialog":
            continue

        action = None
        if mode == "dialog":
            if raw.isdigit():
                action = {"type": "dialog_choice", "choice_index": int(raw) - 1}
            elif raw in {"", "lanjut", "next", "enter"}:
                action = {"type": "dialog_choice", "choice_index": -1}
        elif mode == "battle":
            parts = raw.split()
            if parts[0] == "1" or parts[0] == "serang":
                action = {"type": "battle_action", "action": "attack"}
            elif parts[0] == "2" or parts[0] == "teknik":
                if len(parts) > 1:
                    action = {"type": "battle_action", "action": "technique", "technique": parts[1]}
                else:
                    teks = session.reg.player_techniques(session.state.player.academy or "")
                    if teks:
                        print("Teknik: " + ", ".join(t["id"] for t in teks))
                        action = {"type": "battle_action", "action": "guard"}  # fallback aman
                    else:
                        action = {"type": "battle_action", "action": "attack"}
            elif parts[0] == "3" or parts[0] == "item":
                action = {"type": "battle_action", "action": "item", "item": parts[1] if len(parts) > 1 else None}
            elif parts[0] == "4" or parts[0] == "bertahan":
                action = {"type": "battle_action", "action": "guard"}
            elif parts[0] == "5" or parts[0] == "kabur":
                action = {"type": "battle_action", "action": "flee"}
            else:
                print("Perintah battle: serang · teknik <id> · item <id> · bertahan · kabur")
        elif mode == "choose":
            opts = v["choose"]["options"]
            if raw.isdigit():
                i = int(raw) - 1
                if 0 <= i < len(opts):
                    action = {"type": "choose", "option": opts[i]["value"]}
            else:
                # dukung "pilih <value>" atau value/label langsung
                parts = raw.split()
                val = parts[1] if parts and parts[0] in {"pilih", "choose"} else raw
                for o in opts:
                    if val in (o["value"], o["label"].lower()):
                        action = {"type": "choose", "option": o["value"]}
                        break
        else:
            parts = raw.split()
            cmd = parts[0]
            if cmd in {"bicara", "talk"}:
                if len(parts) > 1:
                    action = {"type": "talk", "npc": parts[1]}
                else:
                    npcs = [n for n in registry.npcs if n.get("location") == v["location"]["id"]]
                    if npcs:
                        print("NPC di sini: " + ", ".join(n["id"] for n in npcs))
            elif cmd in {"pindah", "move", "go"}:
                if len(parts) > 1:
                    action = {"type": "move", "to": parts[1]}
                else:
                    print("Tujuan: " + ", ".join(v["location"]["connections"]))
            elif cmd in {"tunggu", "waktu", "wait"}:
                action = {"type": "advance_time", "hours": int(parts[1]) if len(parts) > 1 else 4}
            elif cmd in {"meditasi", "grounding", "berkultivasi"}:
                action = {"type": "grounding", "hours": int(parts[1]) if len(parts) > 1 else 4}
            elif cmd == "istirahat":
                action = {"type": "rest", "hours": int(parts[1]) if len(parts) > 1 else 8}
            elif cmd == "simpan":
                action = {"type": "save", "save_name": parts[1] if len(parts) > 1 else "save1"}
            elif cmd == "berburu":
                action = {"type": "hunt"}
            elif cmd == "cari":
                action = {"type": "search"}
            elif cmd in {"pasang", "equip"}:
                if len(parts) > 1:
                    action = {"type": "equip", "item": parts[1]}
                else:
                    print("Senjata di inventori: " + ", ".join(
                        i["id"] for i in v["inventory"] if (session.reg.item(i["id"]) or {}).get("type") == "weapon"))
            elif cmd == "spar":
                if len(parts) > 1:
                    action = {"type": "spar", "npc": parts[1]}
                else:
                    print("NPC sparing: hanxiu, gucanghai")
            elif cmd == "pakai" or cmd == "use":
                if len(parts) > 1:
                    action = {"type": "use_item", "item": parts[1]}
            elif cmd == "beli":
                if len(parts) > 1:
                    action = {"type": "shop_buy", "item": parts[1], "count": int(parts[2]) if len(parts) > 2 else 1}
            elif cmd == "jual":
                if len(parts) > 1:
                    action = {"type": "shop_sell", "item": parts[1], "count": int(parts[2]) if len(parts) > 2 else 1}
            elif cmd == "racik" or cmd == "craft":
                action = {"type": "craft", "recipe": parts[1] if len(parts) > 1 else "rc_pil_qi"}
            elif cmd == "ingatan":
                mids = session.state.memories
                if not mids:
                    print("Belum ada ingatan yang terbuka.")
                else:
                    mid = parts[1] if len(parts) > 1 else mids[-1]
                    mem = registry.memory(mid)
                    if mem:
                        print(GOLD + f"─── {mem['title']} ───" + RESET)
                        print(mem["text"])
            elif cmd == "bantuan":
                print("Perintah: bicara <npc> · pindah <lokasi> · tunggu <jam> · meditasi <jam> · istirahat"
                      " · berburu · cari · spar <npc> · pakai <item> · beli <item> · jual <item> · racik <resep>"
                      " · simpan <nama> · ingatan <id> · bantuan · keluar")
            elif cmd in {"keluar", "quit", "exit"}:
                break

        if action:
            session.apply_action(action)
        # cek selesai arc (tampilkan sekali; lanjutkan loop agar pemain bisa simpan)
        if not arc_ended and "arc_akademi_selesai" in session.state.flags:
            arc_ended = True
            print()
            print(GOLD + "═══ AKHIR ARC AKADEMI ═══" + RESET)
            print("Terima kasih sudah memainkan bukti konsep Fase 1!")
            print("Lanjutan: Arc Sekte (Fase 2). Simpan progressmu di titik aman.")


if __name__ == "__main__":
    main()
