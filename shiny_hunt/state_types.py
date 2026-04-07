from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScreenState:
    name: str
    screenshot_path: Path | None
    action_name: str
    match_x: int = 0
    match_y: int = 0
    match_text: str | None = None
