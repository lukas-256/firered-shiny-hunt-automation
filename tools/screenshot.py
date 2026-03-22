from __future__ import annotations

import argparse
from pathlib import Path

import cv2

DEVICE_INDEX = 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Capture one frame from device 0 to images/<filename>")
    p.add_argument("filename", help="Output filename, for example switch_frame_dark_blue_bg.png")
    return p


def main() -> int:
    args = parser().parse_args()
    output = Path("images") / args.filename
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
