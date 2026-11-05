"""Turn a folder of hand images into ``data/data.pickle``.

One row per image, one column per feature (42 of them). Images where MediaPipe
finds no hand are skipped and counted, so a badly lit session shows up as a
warning instead of quietly shrinking the dataset.

    python -m silent_voice.vision.dataset --data-dir data/raw
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import cv2
import mediapipe as mp

from silent_voice import config
from silent_voice.vision.landmarks import features_from_hand

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def build_dataset(data_dir: Path, output_path: Path) -> tuple[int, int]:
    """Return ``(rows_written, images_skipped)``."""
    data: list[list[float]] = []
    labels: list[str] = []
    skipped = 0

    hands_module = mp.solutions.hands
    with hands_module.Hands(static_image_mode=True, min_detection_confidence=0.3) as hands:
        for class_dir in sorted(data_dir.iterdir()):
            if not class_dir.is_dir():
                continue

            scanned = kept = 0
            for image_path in sorted(class_dir.iterdir()):
                if image_path.suffix.lower() not in IMAGE_SUFFIXES:
                    continue
                scanned += 1

                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"  skipped (unreadable): {image_path}")
                    skipped += 1
                    continue

                results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                if not results.multi_hand_landmarks:
                    print(f"  skipped (no hand detected): {image_path}")
                    skipped += 1
                    continue

                # Use the first hand only, mirroring inference.
                features = features_from_hand(results.multi_hand_landmarks[0])
                data.append(features.tolist())
                labels.append(class_dir.name)
                kept += 1

            print(f"class {class_dir.name}: kept {kept}/{scanned}")

    if not data:
        raise SystemExit("No usable images found - nothing written.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        pickle.dump({"data": data, "labels": labels}, handle)

    print(f"\n{len(data)} samples across {len(set(labels))} classes -> {output_path}")
    print(f"{skipped} images skipped")
    return len(data), skipped


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=config.DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, default=config.DATASET_PATH)
    args = parser.parse_args()

    if not args.data_dir.is_dir():
        raise SystemExit(f"{args.data_dir} does not exist - run collect first.")

    build_dataset(args.data_dir, args.output)


if __name__ == "__main__":
    main()
