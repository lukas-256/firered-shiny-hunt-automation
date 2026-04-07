from __future__ import annotations

from pathlib import Path

from .state_types import ScreenState


def build_default_states(project_root: Path) -> list[ScreenState]:
    images_dir = project_root / "images" / "magikarp"
    return [ScreenState(
            name="throw_rod",
            screenshot_path=images_dir / "throw_rod.png",
            action_name="press_y",
            match_x=200,
            match_y=850,
            match_text="Throw fishing rod.",
        ),
        ScreenState(
            name="hooked",
            screenshot_path=images_dir / "hooked.png",
            action_name="press_a",
            match_x=250,
            match_y=800,
            match_text="You hooked a Pokemon.",
        ),
        ScreenState(
            name="wild_magikarp_appeared",
            screenshot_path=images_dir / "magikarp_appeared.png",
            action_name="press_a",
            match_x=230,
            match_y=800,
            match_text="A wild Magikarp appeared.",
        ),
        ScreenState(
            name="run",
            screenshot_path=images_dir / "run.png",
            action_name="start_run_sequence", # -> right joystick, bottom joystick, a button
            match_x=0,
            match_y=0,
            match_text="No shiny, start running away.",
        ),
        ScreenState(
            name="got_away_safely",
            screenshot_path=images_dir / "got_away.png",
            action_name="press_a",
            match_x=230,
            match_y=800,
            match_text="Got away safely.",
        ),
        ScreenState(
            name="not_even_nible",
            screenshot_path=images_dir / "nible.png",
            action_name="press_a",
            match_x=250,
            match_y=800,
            match_text="Not even a nible.",
        ),]
