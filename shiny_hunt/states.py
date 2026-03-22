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


# Existing screenshots in your folder are wired in directly.
# Missing screenshots are represented as None and can be filled later.
def build_default_states(project_root: Path) -> list[ScreenState]:
    images_dir = project_root / "images"
    return [
        ScreenState(
            name="flying_star",
            screenshot_path=images_dir / "flying_stars.png",
            action_name="press_a",
            match_x=200,
            match_y=225,
            match_text="Matched the blue background of the flying stars intro.",
        ),
        ScreenState(
            name="start_screen",
            screenshot_path=images_dir / "start_screen.png",
            action_name="press_a",
            match_x=180,
            match_y=950,
            match_text="Matched Start Screen",
        ),
        ScreenState(
            name="save_screen",
            screenshot_path=images_dir / "save_screen.png",
            action_name="press_a",
            match_x=0,
            match_y=0,
            match_text="Matched save screen",
        ),
        ScreenState(
            name="diary_skip",
            screenshot_path=images_dir / "diary_skip.png",
            action_name="press_b",
            match_x=0,
            match_y=0,
            match_text="Matched diary screen",
        ),
        ScreenState(
            name="start charmander pickup sequence",
            screenshot_path=images_dir / "pickup_charmander.png",
            action_name="press_a",
            match_x=0,
            match_y=0,
            match_text="Started pickup charmander sequence",
        ),
        ScreenState(
            name="is charmander is your choice question",
            screenshot_path=images_dir / "charmander_is_your_choice.png",
            action_name="press_a",
            match_x=250,
            match_y=800,
            match_text="Choice Question",
        ),
        ScreenState(
            name="are you claming charmander",
            screenshot_path=images_dir / "charmander_you_are_claiming.png",
            action_name="press_a",
            match_x=250,
            match_y=800,
            match_text="Claming Question",
        ),
        ScreenState(
            name="charmander looks energetic",
            screenshot_path=images_dir / "charmander_quite_energetic.png",
            action_name="press_a",
            match_x=0,
            match_y=0,
            match_text="Energetic Message",
        ),
        ScreenState(
            name="charmander nickname skip",
            screenshot_path=images_dir / "charmander_nickname.png",
            action_name="press_b",
            match_x=0,
            match_y=0,
            match_text="Nickname skip",
        ),
        ScreenState(
            name="gary dialog",
            screenshot_path=images_dir / "gary_dialog.png",
            action_name="press_a",
            match_x=0,
            match_y=0,
            match_text="Gary Dialog",
        ),
        ScreenState(
            name="open menu",
            screenshot_path=images_dir / "open_menu.png",
            action_name="press_x",
            match_x=0,
            match_y=0,
            match_text="Open Menu",
        ),
        ScreenState(
            name="open pokemon",
            screenshot_path=images_dir / "open_pokemon.png",
            action_name="press_a",
            match_x=0,
            match_y=0,
            match_text="Open Pokemon",
        ),
        ScreenState(
            name="check charmander",
            screenshot_path=images_dir / "check_charmander.png",
            action_name="press_a",
            match_x=1000,
            match_y=0,
            match_text="Check Charmander",
        ),
        ScreenState(
            name="check summary",
            screenshot_path=images_dir / "check_summary.png",
            action_name="press_a",
            match_x=1000,
            match_y=0,
            match_text="Check Summary",
        ),
        ScreenState(
            name="check shiny",
            screenshot_path=images_dir / "check_shiny.png",
            action_name="press_abxy",
            match_x=320,
            match_y=130,
            match_text="Check Summary",
        ),
    ]
