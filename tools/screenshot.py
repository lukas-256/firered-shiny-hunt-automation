from __future__ import annotations

import argparse
from pathlib import Path
import sys

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shiny_hunt.config import default_app_config

DEVICE_INDEX = 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Capture one frame from device 0 to images/<state_profile>/<filename>")
    p.add_argument("filename", help="Output filename, for example switch_frame_dark_blue_bg.png")
    return p


def main() -> int:
    args = parser().parse_args()
    cfg = default_app_config()
    output = Path("images") / cfg.state_profile / args.filename
    output.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(DEVICE_INDEX, cv2.CAP_AVFOUNDATION)
    ok, frame = cap.read()
    cap.release()

    if not ok:
        raise RuntimeError("Could not grab frame from device index 0")

    cv2.imwrite(str(output), frame)
    print(f"Saved {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
