from __future__ import annotations

import cv2
import numpy as np

from .config import CaptureConfig


class FrameGrabber:
    def __init__(self, config: CaptureConfig) -> None:
        self._config = config
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> None:
        self._cap = cv2.VideoCapture(self._config.device_index, self._config.backend)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.height)
        self._cap.set(cv2.CAP_PROP_FPS, self._config.fps)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open capture device {self._config.device_index}")

    def read(self) -> np.ndarray | None:
        if self._cap is None:
            raise RuntimeError("FrameGrabber must be opened before read()")
        ok, frame = self._cap.read()
        if not ok:
            return None
        return frame

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
