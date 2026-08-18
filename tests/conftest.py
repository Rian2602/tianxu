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
