"""Fixtures bersama — F0.1 (ENGINE_ADAPTATION_PLAN).

Semua test memakai dataset minimal di `tests/fixtures/minimal_data/`, disalin ke
tmp_path per-test sehingga tidak pernah menyentuh `data/` asli repo. `DataRegistry`
selalu dibuat dengan `data_dir` eksplisit (bukan default repo).
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FIXTURES_DIR = ROOT / "tests" / "fixtures" / "minimal_data"


def skip_intro(session) -> None:
    """Skip intro narrative dialog jika aktif."""
    while session.state.pending_dialog:
        session.apply_action({"type": "dialog_choice", "choice_index": -1})


def _walks(session, start: str, goal: str, max_len: int, cap: int = 200):
    """Semua walk start→goal sampai panjang max_len, terpendek dulu.

    Revisit lokasi diIZINKAN — pola leave-return (mis. outer→hutan→outer)
    justru kunci membuka gerbang lewat penyelesaian quest di tengah jalan.
    Memakai connections MENTAH: gerbang boleh masuk rencana, keabsahan
    dicek saat eksekusi."""
    queue = [[start]]
    yielded = 0
    while queue and yielded < cap:
        path = queue.pop(0)
        if len(path) > max_len:
            continue  # dibiarkan mati — tidak diperpanjang lagi
        cur = path[-1]
        if cur == goal and len(path) > 1:
            yielded += 1
            yield list(path)
            continue
        for nxt in session.reg.location(cur).get("connections", []):
            queue.append(path + [nxt])
        queue.sort(key=len)


def reach_safe(session, target: str, max_len: int = 6) -> None:
    """_reach yang sadar connection_gates (playtest #6) — otomatis penuh.

    Rencana = walk optimistik menembus gerbang; dieksekusi hop demi hop.
    Hop ditolak gerbang bukan masalah: bila sudah ada kemajuan posisi
    (quest 'reach' bisa selesai di tengah jalan dan MEMBUKA gerbang
    berikutnya) re-plan dari realitas baru; bila langkah pertama langsung
    ditolak, coba kandidat walk berikutnya. Menangani pola leave-return
    otomatis tanpa pengetahuan quest; sekalian memverifikasi tiba
    (_reach diam saja bila gerak ditolak)."""
    for _ in range(32):
        if session.state.location == target:
            return
        for walk in _walks(session, session.state.location, target, max_len):
            moved = False
            for hop in walk[1:]:
                session.apply_action({"type": "move", "to": hop})
                if session.state.location != hop:  # ditolak gerbang
                    break
                moved = True
            if not moved:
                continue  # langkah pertama saja yang ditolak — walk berikutnya
            break  # ada kemajuan — re-plan dari posisi baru
        else:
            raise AssertionError(
                f"tidak ada walk ke {target} dari {session.state.location}")
    raise AssertionError(
        f"tidak sampai {target} dari {session.state.location} (max_len={max_len})")


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Salinan dataset minimal ke direktori sementara."""
    dest = tmp_path / "data"
    shutil.copytree(FIXTURES_DIR, dest)
    return dest


@pytest.fixture
def registry(data_dir: Path):
    """DataRegistry yang dimuat dari dataset minimal (tmp)."""
    from src.loader import DataRegistry
    return DataRegistry(data_dir=data_dir)


@pytest.fixture
def session(registry):
    """GameSession baru dari dataset minimal."""
    from src.engine.session import GameSession
    return GameSession.new(registry)
