from __future__ import annotations

from pathlib import Path

from .state_types import ScreenState


def build_default_states(project_root: Path) -> list[ScreenState]:
    _images_dir = project_root / "images" / "magikarp"
    return []
