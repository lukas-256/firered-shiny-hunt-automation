from __future__ import annotations

import time
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shiny_hunt.config import default_app_config
from shiny_hunt.controller import ProMicroController


def main() -> int:
    cfg = default_app_config().controller
    controller = ProMicroController(
        port=cfg.port,
        baud_rate=cfg.baud_rate,
        timeout=cfg.timeout,
        connect_delay_seconds=cfg.connect_delay_seconds,
        tap_hold_seconds=cfg.tap_hold_seconds,
        release_delay_seconds=cfg.release_delay_seconds,
    )

    try:
        print("syncing...")
        controller.connect()
        print("sync ok")

        for button in ("A", "B", "X", "Y"):
            print(button)
            controller.tap(button)
            time.sleep(1.0)

        print("ABXY")
        controller.tap_buttons(("A", "B", "X", "Y"), hold_seconds=0.12)
    finally:
        controller.disconnect()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
