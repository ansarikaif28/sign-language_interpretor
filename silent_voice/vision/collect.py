"""Record a training set from the webcam.

For each class in turn the preview opens; hold the sign, press ``Q``, and the
next ``--per-class`` frames are written to ``data/raw/<class>/``.

    python -m silent_voice.vision.collect --classes 25 --per-class 100
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2

from silent_voice import config


def collect(
    output_dir: Path,
    number_of_classes: int,
    per_class: int,
    camera_index: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise RuntimeError(
            f"Could not open camera {camera_index}. "
            "Try another index (see CAMERA_INDEX in .env)."
        )

    try:
        for class_id in range(number_of_classes):
            class_dir = output_dir / str(class_id)
            class_dir.mkdir(parents=True, exist_ok=True)

            print(f"Class {class_id}: press Q when your hand is in position.")
            while True:
                ok, frame = capture.read()
                if not ok:
                    raise RuntimeError("Camera stopped returning frames.")

                cv2.putText(
                    frame,
                    f'Class {class_id} - ready? Press "Q"',
                    (60, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.1,
                    (0, 255, 0),
                    3,
                    cv2.LINE_AA,
                )
                cv2.imshow("Collecting data", frame)
                if cv2.waitKey(25) & 0xFF == ord("q"):
                    break

            print(f"  capturing {per_class} frames...")
            for counter in range(per_class):
                ok, frame = capture.read()
                if not ok:
                    raise RuntimeError("Camera stopped returning frames.")

                cv2.imshow("Collecting data", frame)
                cv2.waitKey(25)
                cv2.imwrite(str(class_dir / f"{counter}.jpg"), frame)

            # Small pause so the operator can move before the next class starts.
            time.sleep(0.3)
    finally:
        capture.release()
        cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=config.DEFAULT_DATA_DIR)
    parser.add_argument("--classes", type=int, default=25)
    parser.add_argument("--per-class", type=int, default=100)
    parser.add_argument("--camera", type=int, default=config.CAMERA_INDEX)
    args = parser.parse_args()

    collect(args.output, args.classes, args.per_class, args.camera)


if __name__ == "__main__":
    main()
