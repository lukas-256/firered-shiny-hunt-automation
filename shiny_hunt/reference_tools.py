from __future__ import annotations

from pathlib import Path

import cv2

from .capture import FrameGrabber
from .config import CaptureConfig


def save_full_frame(output_path: Path, capture_config: CaptureConfig) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    grabber = FrameGrabber(capture_config)
    grabber.open()
    try:
        frame = grabber.read()
        if frame is None:
            raise RuntimeError("Could not grab frame")
        cv2.imwrite(str(output_path), frame)
        return output_path
    finally:
        grabber.close()


def save_crop(
    output_path: Path,
    capture_config: CaptureConfig,
    x: int,
    y: int,
    w: int,
    h: int,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    grabber = FrameGrabber(capture_config)
    grabber.open()
    try:
        frame = grabber.read()
        if frame is None:
            raise RuntimeError("Could not grab frame")
        crop = frame[y : y + h, x : x + w]
        cv2.imwrite(str(output_path), crop)
        return output_path
    finally:
        grabber.close()


def discover_capture_devices(max_index: int = 10, backend: int = cv2.CAP_AVFOUNDATION) -> list[int]:
    working = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i, backend)
        ok, _frame = cap.read()
        cap.release()
        if ok:
            working.append(i)
    return working
