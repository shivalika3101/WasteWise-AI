import json as _json
import pathlib as _pathlib

import torch as _torch

import ml.inference.labels as _labels


_ML_DIR = _pathlib.Path(__file__).parents[2] / "ml"
_MODEL_DIR = _ML_DIR / "models"


def test_labels_unique():
    assert len(set(_labels.LABELS)) == len(_labels.LABELS)


def test_labels_sorted():
    assert _labels.LABELS == sorted(_labels.LABELS)


def test_labels_match_training_class_order():
    training_labels = _json.loads(
        (_ML_DIR / "notebooks" / "class_names.json").read_text(
            encoding="utf-8"
        )
    )
    assert _labels.LABELS == training_labels


def test_labels_match_pytorch_model_outputs():
    heads = {
        "mobilenetv2_best.pth": "classifier.1.weight",
        "efficientnet_b0_best.pth": "classifier.1.weight",
        "resnet50_best.pth": "fc.weight",
    }

    for filename, head in heads.items():
        state = _torch.load(_MODEL_DIR / filename, map_location="cpu")
        assert state[head].shape[0] == len(_labels.LABELS)
