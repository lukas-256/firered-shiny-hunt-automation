from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shiny_hunt.config import CaptureConfig, default_app_config
from shiny_hunt.reference_tools import (
    discover_capture_devices,
    save_crop,
    save_full_frame,
)


def build_capture_config(device_index: int | None) -> CaptureConfig:
    cfg = default_app_config().capture
    if device_index is None:
        return cfg
    return CaptureConfig(
        device_index=device_index,
        backend=cfg.backend,
        width=cfg.width,
        height=cfg.height,
        fps=cfg.fps,
    )


def cmd_list_devices(_args: argparse.Namespace) -> int:
    devices = discover_capture_devices()
    if not devices:
        print("No working capture devices found.")
        return 1

    print("Working capture devices:")
    for idx in devices:
        print(f"- {idx}")
    return 0


def cmd_save_full(args: argparse.Namespace) -> int:
    cap_cfg = build_capture_config(args.device)
    output = Path(args.out)
    saved = save_full_frame(output, cap_cfg)
    print(f"Saved {saved}")
    return 0


def cmd_save_crop(args: argparse.Namespace) -> int:
    cap_cfg = build_capture_config(args.device)
    output = Path(args.out)
    saved = save_crop(
        output,
        cap_cfg,
        x=args.x,
        y=args.y,
        w=args.w,
        h=args.h,
    )
    print(f"Saved {saved}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Utilities for reference screenshot workflow")
    sub = p.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-devices", help="List working capture device indexes")
    p_list.set_defaults(func=cmd_list_devices)

    p_full = sub.add_parser("save-full", help="Capture full frame to a file")
    p_full.add_argument("--out", default="images/reference_full.png", help="Output image path")
    p_full.add_argument("--device", type=int, default=None, help="Capture device index override")
    p_full.set_defaults(func=cmd_save_full)

    p_crop = sub.add_parser("save-crop", help="Capture cropped region to a file")
    p_crop.add_argument("--out", default="images/reference_crop.png", help="Output image path")
    p_crop.add_argument("--x", type=int, required=True, help="Crop start X")
    p_crop.add_argument("--y", type=int, required=True, help="Crop start Y")
    p_crop.add_argument("--w", type=int, required=True, help="Crop width")
    p_crop.add_argument("--h", type=int, required=True, help="Crop height")
    p_crop.add_argument("--device", type=int, default=None, help="Capture device index override")
    p_crop.set_defaults(func=cmd_save_crop)

    return p


def main() -> int:
    p = parser()
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
