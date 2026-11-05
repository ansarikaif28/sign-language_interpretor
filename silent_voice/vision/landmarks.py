"""Conversion of MediaPipe hand landmarks into the feature vector the model expects.

The 42-number vector is deliberately identical to the one used when the dataset
was recorded, so training and inference cannot drift apart:

    for each of the 21 landmarks, emit ``x - min(x)`` and ``y - min(y)``

That makes the vector invariant to where the hand sits inside the frame. It is
*not* invariant to distance from the camera or to rotation, which is why the
sign has to be framed roughly like the reference images in ``docs``.
"""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

FEATURES_PER_LANDMARK = 2
EXPECTED_FEATURES = 21 * FEATURES_PER_LANDMARK  # 42

# Class index -> character, following the numbered folders the dataset was
# recorded into (0..24).
#
# The original inference script carried a 26-entry map: A-N, then "0" at index
# 14, then P-Y, with Z left at index 25. The trained model only has 25 classes,
# so index 25 never fires, and a single digit class among 25 letters does not
# match the data. 25 folders covering A-Y fits exactly, so "0" there is read as
# the letter O throughout this repo. If your own dataset used a different
# order, this dict is the only place to change.
SIGN_LABELS: dict[int, str] = {
    **dict(zip(range(14), "ABCDEFGHIJKLMN")),   # A .. N
    14: "O",
    **dict(zip(range(15, 25), "PQRSTUVWXY")),   # P .. Y
}

# Letters with no training class: Z was never recorded, and J is normally a
# moving sign (the static frame captured here is its hand shape only).
UNSUPPORTED_SIGNS = ("Z",)

_HAND_CONNECTIONS: Sequence[tuple[int, int]] | None = None


def feature_vector(points: Iterable[tuple[float, float]]) -> np.ndarray:
    """Flatten ``(x, y)`` pairs into the model's translation-invariant vector."""
    points = list(points)
    if not points:
        raise ValueError("no landmarks supplied")

    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    min_x, min_y = min(xs), min(ys)

    vector = np.empty(len(points) * FEATURES_PER_LANDMARK, dtype=np.float64)
    for index, (x, y) in enumerate(points):
        vector[index * 2] = x - min_x
        vector[index * 2 + 1] = y - min_y
    return vector


def landmarks_to_points(hand_landmarks) -> list[tuple[float, float]]:
    """Pull normalised ``(x, y)`` pairs out of a MediaPipe hand result."""
    return [(lm.x, lm.y) for lm in hand_landmarks.landmark]


def features_from_hand(hand_landmarks) -> np.ndarray:
    """Feature vector for a single detected hand."""
    return feature_vector(landmarks_to_points(hand_landmarks))


def bounding_box(
    hand_landmarks, width: int, height: int, padding: int = 10
) -> tuple[int, int, int, int]:
    """Pixel-space box around a hand, expanded by ``padding`` on every side."""
    xs = [lm.x * width for lm in hand_landmarks.landmark]
    ys = [lm.y * height for lm in hand_landmarks.landmark]

    x1 = max(int(min(xs)) - padding, 0)
    y1 = max(int(min(ys)) - padding, 0)
    x2 = min(int(max(xs)) + padding, width - 1)
    y2 = min(int(max(ys)) + padding, height - 1)
    return x1, y1, x2, y2
