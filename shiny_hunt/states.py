from __future__ import annotations

from pathlib import Path

from .charmander_states import build_default_states as build_charmander_states
from .dratini_states import build_default_states as build_dratini_states
from .eevee_states import build_default_states as build_eevee_states
from .magikarp_states import build_default_states as build_magikarp_states
from .snorlax_states import build_default_states as build_snorlax_states
from .state_types import ScreenState


def build_states(project_root: Path, state_profile: str) -> list[ScreenState]:
    profile = state_profile.strip().lower()
    builders = {
        "charmander": build_charmander_states,
        "dratini": build_dratini_states,
        "eevee": build_eevee_states,
        "magikarp": build_magikarp_states,
        "snorlax": build_snorlax_states,
    }
    builder = builders.get(profile)
    if builder is None:
        supported = ", ".join(sorted(builders))
        raise ValueError(f"Unknown state profile '{state_profile}'. Supported profiles: {supported}")
    return builder(project_root)
