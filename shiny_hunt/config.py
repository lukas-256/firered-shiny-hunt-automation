from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2


@dataclass(frozen=True)
class CaptureConfig:
    device_index: int = 0
    backend: int = cv2.CAP_AVFOUNDATION
    width: int = 1920
    height: int = 1080
    fps: int = 60


@dataclass(frozen=True)
class MatchConfig:
    pixel_tolerance: int = 1
    similarity_threshold: float = 0.99
    missing_image_similarity: float = 0.0


@dataclass(frozen=True)
class RuntimeConfig:
    check_interval_seconds: float = 0.5
    log_similarity: bool = False
    max_loops: Optional[int] = None
    startup_press_a_seconds: float = 0.6
    startup_press_a_interval_seconds: float = 0.4
    shiny_no_match_streak_threshold: int = 40
    shiny_no_match_notify_runtime_states: tuple[str, ...] = ("s1",)
    reset_on_no_match_threshold_outside_notify_states: bool = False
    ntfy_topic: str = "shiny_hunt_noti_ignotus"
    reset_counter_initial: int = 0
    reset_counter_increment: int = 1
    success_probability_per_try: float = 1.0 / 8192.0


@dataclass(frozen=True)
class ControllerConfig:
    port: str = "/dev/cu.usbserial-BG03S8AW"
    baud_rate: int = 19200
    timeout: float = 0.2
    connect_delay_seconds: float = 1.0
    tap_hold_seconds: float = 0.08
    release_delay_seconds: float = 0.03


@dataclass(frozen=True)
class AppConfig:
    project_root: Path
    state_profile: str = "eevee"
    initial_runtime_state: str = "s0"
    capture: CaptureConfig = CaptureConfig()
    match: MatchConfig = MatchConfig()
    runtime: RuntimeConfig = RuntimeConfig()
    controller: ControllerConfig = ControllerConfig()


def default_app_config() -> AppConfig:
    return AppConfig(project_root=Path.cwd())
