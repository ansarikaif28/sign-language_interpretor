"""
One-time offline converter: exports scikit-learn RandomForestClassifier in `model.p`
into a compact static `model.json` (~93 KB) for pure browser/JS inference.

Works with or without scikit-learn installed.
"""

import json
import os
import pickle
import struct


LABELS = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
    "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
    "U", "V", "W", "X", "Y",
]


class _Stub:
    def __init__(self, *args, **kwargs):
        pass

    def __setstate__(self, state):
        self._state = state

    def __call__(self, *args, **kwargs):
        return _Stub(*args, **kwargs)


class _RawSklearnUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except Exception:
            return _Stub


def export_with_sklearn(model_path: str) -> dict:
    with open(model_path, "rb") as f:
        rf = pickle.load(f)["model"]

    classes = [int(c) for c in rf.classes_]
    trees = []
    for est in rf.estimators_:
        t = est.tree_
        nodes = []
        for i in range(t.node_count):
            left = int(t.children_left[i])
            right = int(t.children_right[i])
            if left == -1:
                slot = int(t.value[i][0].argmax())
                nodes.append(classes[slot])
            else:
                feat = int(t.feature[i])
                thresh = round(float(t.threshold[i]), 7)
                nodes.append([feat, thresh, left, right])
        trees.append(nodes)

    return {"labels": LABELS, "classOrder": classes, "trees": trees}


def export_raw_pickle(model_path: str) -> dict:
    with open(model_path, "rb") as f:
        rf = _RawSklearnUnpickler(f).load()["model"]

    cls_bytes = rf._state["classes_"]._state[4]
    n_classes = rf._state["n_classes_"]
    classes = [
        int(cls_bytes[i * 8 : (i + 1) * 8].decode("utf-32-le").rstrip("\x00"))
        for i in range(n_classes)
    ]

    trees = []
    for est in rf._state["estimators_"]:
        t = est._state["tree_"]._state
        node_count = t["node_count"]
        node_bytes = t["nodes"]._state[4]
        val_bytes = t["values"]._state[4]

        nodes = []
        for i in range(node_count):
            left, right, feat, thresh = struct.unpack_from("<qqqd", node_bytes, i * 64)
            if left == -1:
                vals = struct.unpack_from(f"<{n_classes}d", val_bytes, i * n_classes * 8)
                slot = max(range(n_classes), key=lambda k: vals[k])
                nodes.append(classes[slot])
            else:
                nodes.append([feat, round(thresh, 7), left, right])
        trees.append(nodes)

    return {"labels": LABELS, "classOrder": classes, "trees": trees}


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(repo_root, "model.p")
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.json")

    try:
        import sklearn  # noqa: F401
        exported = export_with_sklearn(model_path)
    except ImportError:
        exported = export_raw_pickle(model_path)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(exported, f, separators=(",", ":"))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Exported {len(exported['trees'])} trees ({len(exported['labels'])} labels) -> {out_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
