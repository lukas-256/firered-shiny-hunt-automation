from __future__ import annotations

from pathlib import Path

from .state_types import ScreenState


def build_default_states(project_root: Path) -> list[ScreenState]:
    images_dir = project_root / "images" / "eevee"
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
            screenshot_path=images_dir / "diary_skip_2.png",
            action_name="press_b",
            match_x=0,
            match_y=0,
            match_text="Matched diary screen and perform skip",
            required_runtime_state="s0",
            next_runtime_state="s0",
        ),
        ScreenState(
            name="pickup_eevee",
            screenshot_path=images_dir / "pickup_eevee.png",
            action_name="press_a",
            match_x=0,
            match_y=0,
            match_text="Pickup eevee pokeball",
            required_runtime_state="s0",
            next_runtime_state="s0",
        ),
        ScreenState(
            name="skip_nickname",
            screenshot_path=images_dir / "skip_nickname.png",
            action_name="press_b",
            match_x=0,
            match_y=0,
            match_text="Skip nickname dialog",
            required_runtime_state="s0",
            next_runtime_state="s0",
        ),
        ScreenState(
            name="open_menu",
            screenshot_path=images_dir / "open_menu.png",
            action_name="open_menu_eevee", # button x, joystick down, button a, joystick down, button a, button a
            match_x=0,
            match_y=0,
            match_text="Open menu to check for eevee",
            required_runtime_state="s0",
            next_runtime_state="s1",
        ),
        ScreenState(
            name="no_shiny",
            screenshot_path=images_dir / "shiny_not_found.png",
            action_name="press_abxy",
            match_x=360,
            match_y=130,
            match_text="No shiny -> perform reset",
            required_runtime_state="s1",
            next_runtime_state="s0",
        ),
        ScreenState(
            name="shiny_found",
            screenshot_path=images_dir / "shiny_found.png",
            action_name="notify_and_exit",
            match_x=360,
            match_y=130,
            match_text="Shiny found!!!",
            required_runtime_state="s1",
            next_runtime_state="s1",
        ),
    ]
