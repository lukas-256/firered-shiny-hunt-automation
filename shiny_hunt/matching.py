from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .config import MatchConfig


@dataclass(frozen=True)
class MatchResult:
    similarity: float
    is_match: bool


class ImageMatcher:
    def __init__(self, config: MatchConfig) -> None:
        self._config = config

    def load_reference(self, path: Path) -> np.ndarray | None:
        if not path.exists():
            return None
        return cv2.imread(str(path))

    def compare(self, reference: np.ndarray | None, frame: np.ndarray | None) -> MatchResult:
        if reference is None or frame is None:
            similarity = self._config.missing_image_similarity
            return MatchResult(similarity=similarity, is_match=False)
        if frame.shape != reference.shape:
            return MatchResult(similarity=0.0, is_match=False)

        diff = cv2.absdiff(reference, frame)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        same_pixels = np.sum(gray_diff < self._config.pixel_tolerance)
        total_pixels = gray_diff.size
        similarity = float(same_pixels / total_pixels)

        return MatchResult(
            similarity=similarity,
            is_match=similarity >= self._config.similarity_threshold,
        )
