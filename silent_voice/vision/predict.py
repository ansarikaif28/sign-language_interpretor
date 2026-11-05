"""The inference loop: webcam in, predicted character out, annotated frame shown."""

from __future__ import annotations

import pickle
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

from silent_voice import config
from silent_voice.vision.landmarks import (
    EXPECTED_FEATURES,
    SIGN_LABELS,
    bounding_box,
    features_from_hand,
)

BOX_COLOUR = (0, 0, 0)
TEXT_COLOUR = (255, 255, 255)
WINDOW_NAME = "Silent Voice"


class SignClassifier:
    """Thin wrapper around the pickled scikit-learn model."""

    def __init__(self, model_path: Path | str | None = None) -> None:
        self.model_path = Path(model_path or config.MODEL_PATH)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"No model at {self.model_path}. Train one first:\n"
                "    python -m silent_voice.vision.train"
            )
        with self.model_path.open("rb") as handle:
            self.model = pickle.load(handle)["model"]

    def predict(self, features: np.ndarray) -> tuple[int, str]:
        """Return ``(class_index, character)`` for one 42-value feature vector."""
        if features.shape[0] != EXPECTED_FEATURES:
            msg = (
                f"expected {EXPECTED_FEATURES} features ({EXPECTED_FEATURES // 2} "
                f"landmarks), got {features.shape[0]}"
            )
            raise ValueError(msg)

        index = int(self.model.predict([features])[0])
        return index, SIGN_LABELS.get(index, "?")


def annotate(frame, box: tuple[int, int, int, int], character: str) -> None:
    """Draw the hand box and the predicted character onto ``frame`` in place."""
    x1, y1, x2, y2 = box
    cv2.rectangle(frame, (x1, y1), (x2, y2), BOX_COLOUR, 4)
    cv2.putText(
        frame,
        character,
        (x1, max(y1 - 10, 30)),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.3,
        TEXT_COLOUR,
        3,
        cv2.LINE_AA,
    )


def run_webcam(
    model_path: Path | str | None = None,
    camera_index: int | None = None,
    min_confidence: float = 0.3,
) -> None:
    """Open the webcam and label hand signs until the user presses ``Q``."""
    classifier = SignClassifier(model_path)
    camera_index = config.CAMERA_INDEX if camera_index is None else camera_index

    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise RuntimeError(
            f"Could not open camera {camera_index}. "
            "Try another index (see CAMERA_INDEX in .env)."
        )

    hands_module = mp.solutions.hands
    drawing = mp.solutions.drawing_utils
    drawing_styles = mp.solutions.drawing_styles

    try:
        with hands_module.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=min_confidence,
        ) as hands:
            while True:
                ok, frame = capture.read()
                if not ok:
                    break

                height, width, _ = frame.shape
                results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            hands_module.HAND_CONNECTIONS,
                            drawing_styles.get_default_hand_landmarks_style(),
                            drawing_styles.get_default_hand_connections_style(),
                        )
                        _, character = classifier.predict(
                            features_from_hand(hand_landmarks)
                        )
                        annotate(
                            frame,
                            bounding_box(hand_landmarks, width, height),
                            character,
                        )

                cv2.imshow(WINDOW_NAME, frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        capture.release()
        cv2.destroyAllWindows()


def predict_frame(classifier: SignClassifier, frame_rgb: np.ndarray) -> list[dict]:
    """Classify every hand in a single RGB frame (used by the smoke test)."""
    hands_module = mp.solutions.hands
    results_out: list[dict] = []

    with hands_module.Hands(static_image_mode=True, max_num_hands=1) as hands:
        results = hands.process(frame_rgb)

    for hand_landmarks in results.multi_hand_landmarks or []:
        index, character = classifier.predict(features_from_hand(hand_landmarks))
        results_out.append({"index": index, "character": character, "landmarks": hand_landmarks})

    return results_out


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run the sign interpreter.")
    parser.add_argument("--model", default=None, help="path to model.p")
    parser.add_argument("--camera", type=int, default=None, help="camera index")
    parser.add_argument("--confidence", type=float, default=0.3,
                        help="MediaPipe detection confidence")
    args = parser.parse_args()

    run_webcam(args.model, args.camera, args.confidence)


if __name__ == "__main__":
    main()
