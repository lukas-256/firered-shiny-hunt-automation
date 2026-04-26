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
        return cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

    def compare(self, reference: np.ndarray | None, frame: np.ndarray | None) -> MatchResult:
        if reference is None or frame is None:
            similarity = self._config.missing_image_similarity
            return MatchResult(similarity=similarity, is_match=False)
        if frame.shape[:2] != reference.shape[:2]:
            return MatchResult(similarity=0.0, is_match=False)

        if reference.ndim != 3 or frame.ndim != 3:
            return MatchResult(similarity=0.0, is_match=False)

        if reference.shape[2] == 4:
            alpha = reference[:, :, 3]
            mask = alpha > 0
            if not np.any(mask):
                return MatchResult(similarity=0.0, is_match=False)

            reference_bgr = reference[:, :, :3]
            diff = cv2.absdiff(reference_bgr, frame)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

            same_pixels = np.sum((gray_diff < self._config.pixel_tolerance) & mask)
            total_pixels = int(np.sum(mask))
        elif reference.shape[2] == 3 and frame.shape[2] == 3:
            diff = cv2.absdiff(reference, frame)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

            same_pixels = np.sum(gray_diff < self._config.pixel_tolerance)
            total_pixels = gray_diff.size
        else:
            return MatchResult(similarity=0.0, is_match=False)

        similarity = float(same_pixels / total_pixels)

        return MatchResult(
            similarity=similarity,
            is_match=similarity >= self._config.similarity_threshold,
        )
