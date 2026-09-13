from __future__ import annotations

from pathlib import Path

from .state_types import ScreenState


def build_default_states(project_root: Path) -> list[ScreenState]:
    images_dir = project_root / "images" / "snorlax"
    return [
        ScreenState(
            name="flying_star",
            screenshot_path=images_dir / "flying_stars.png",
            action_name="press_a",
            match_x=200,
            match_y=225,
            match_text="Matched the blue background of the flying stars intro.",
            required_runtime_state="s0",
            next_runtime_state="s0",
        ),
        ScreenState(
            name="start_screen",
            screenshot_path=images_dir / "start_screen.png",
            action_name="press_a",
            match_x=180,
            match_y=950,
            match_text="Matched start screen",
            required_runtime_state="s0",
            next_runtime_state="s0",
        ),
        ScreenState(
            name="save_screen",
            screenshot_path=images_dir / "save_screen.png",
            action_name="press_a",
            match_x=0,
            match_y=0,
            match_text="Matched save screen",
            required_runtime_state="s0",
            next_runtime_state="s0",
        ),
        ScreenState(
            name="diary_skip",
            screenshot_path=images_dir / "diary_skip.png",
            action_name="press_b",
            match_x=0,
            match_y=0,
            match_text="Matched diary screen and perform skip",
            required_runtime_state="s0",
            next_runtime_state="s1",
        ),
        ScreenState(
            name="speak to relaxo",
            screenshot_path=images_dir / "init.png",
            action_name="press_a",
            match_x=0,
            match_y=0,
            match_text="Speaking to relaxo",
            required_runtime_state="s1",
            next_runtime_state="s1",
        ),
        ScreenState(
            name="is not shiny",
            screenshot_path=images_dir / "shiny_not_found.png",
            action_name="press_abxy",
            match_x=1210,
            match_y=330,
            match_text="Speaking to relaxo",
            required_runtime_state="s1",
            next_runtime_state="s0",
        ),
    ]
