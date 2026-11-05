"""Train the hand-sign classifier.

    python -m silent_voice.vision.train --data data/data.pickle --model models/model.p

Prints a held-out accuracy figure and writes the same ``{"model": ...}`` pickle
that ``SignClassifier`` loads. A random seed is exposed so runs are repeatable.
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import cross_val_score, train_test_split

from silent_voice import config


def train(
    dataset_path: Path,
    model_path: Path,
    random_state: int = 42,
    test_size: float = 0.2,
    n_estimators: int = 100,
) -> float:
    with dataset_path.open("rb") as handle:
        payload = pickle.load(handle)

    features = np.asarray(payload["data"])
    labels = np.asarray(payload["labels"])

    x_train, x_test, y_train, y_test = train_test_split(
        features, labels, test_size=test_size, shuffle=True, stratify=labels,
        random_state=random_state,
    )

    model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)

    cv_scores = cross_val_score(model, features, labels, cv=5)
    print(f"samples        : {len(features)}")
    print(f"features       : {features.shape[1]}")
    print(f"classes        : {len(set(labels))}")
    print(f"hold-out acc.  : {accuracy * 100:.2f}%  ({len(y_test)} samples)")
    print(f"5-fold CV acc. : {cv_scores.mean() * 100:.2f}% "
          f"(+/- {cv_scores.std() * 100:.2f})")
    print()
    print(classification_report(y_test, predictions, digits=3, zero_division=0))

    model_path.parent.mkdir(parents=True, exist_ok=True)
    with model_path.open("wb") as handle:
        pickle.dump({"model": model}, handle)
    print(f"saved -> {model_path}")

    return accuracy


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=config.DATASET_PATH)
    parser.add_argument("--model", type=Path, default=config.MODEL_PATH)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--trees", type=int, default=100)
    args = parser.parse_args()

    if not args.data.exists():
        raise SystemExit(f"{args.data} not found - run the dataset step first.")

    train(args.data, args.model, args.seed, args.test_size, args.trees)


if __name__ == "__main__":
    main()
