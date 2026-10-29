import functools as _functools
import logging as _logging
import os as _os
import pathlib as _pathlib

_os.environ["KERAS_BACKEND"] = "torch"

import keras as _keras
import torch as _torch
import torchvision.models as _models

import ml.inference.labels as _labels


_LOGGER = _logging.getLogger(__name__)

MODEL_DIR = _pathlib.Path(__file__).parents[1] / "models"
MODEL_PATHS = {
    "mobilenet": MODEL_DIR / "mobilenetv2_best.pth",
    "efficientnet": MODEL_DIR / "efficientnet_b0_best.pth",
    "resnet": MODEL_DIR / "resnet50_best.pth",
    "densenet": MODEL_DIR / "densenet_final.keras",
}
MODEL_NAMES = tuple(MODEL_PATHS)

NUM_CLASSES = len(_labels.LABELS)


class ModelLoadError(RuntimeError):
    pass


def _check_label_contract() -> None:
    if NUM_CLASSES != 30:
        raise RuntimeError(
            f"labels.json contains {NUM_CLASSES} labels. Expected 30."
        )


def _load_mobilenet():
    model = _models.mobilenet_v2(weights=None)
    model.classifier[1] = _torch.nn.Linear(
        model.classifier[1].in_features,
        NUM_CLASSES,
    )
    model.load_state_dict(
        _torch.load(MODEL_PATHS["mobilenet"], map_location="cpu")
    )
    model.eval()
    return model


def _load_efficientnet():
    model = _models.efficientnet_b0(weights=None)
    model.classifier[1] = _torch.nn.Linear(
        model.classifier[1].in_features,
        NUM_CLASSES,
    )
    model.load_state_dict(
        _torch.load(MODEL_PATHS["efficientnet"], map_location="cpu")
    )
    model.eval()
    return model


def _load_resnet():
    model = _models.resnet50(weights=None)
    model.fc = _torch.nn.Linear(
        model.fc.in_features,
        NUM_CLASSES,
    )
    model.load_state_dict(
        _torch.load(MODEL_PATHS["resnet"], map_location="cpu")
    )
    model.eval()
    return model


def _load_densenet():
    return _keras.models.load_model(MODEL_PATHS["densenet"])


def _model_loaders():
    return {
        "mobilenet": _load_mobilenet,
        "efficientnet": _load_efficientnet,
        "resnet": _load_resnet,
        "densenet": _load_densenet,
    }


@_functools.lru_cache
def load_models():
    """Load each available approved model once.

    A single failed package is skipped so the remaining models can still make
    a prediction. Startup fails only when none of the packages load.
    """
    _check_label_contract()

    loaded = {}
    failures = []

    for name, loader in _model_loaders().items():
        try:
            loaded[name] = loader()
        except Exception:
            failures.append(name)
            _LOGGER.exception("Failed to load %s model", name)

    if not loaded:
        raise ModelLoadError(
            f"All models failed to load: {', '.join(failures)}"
        )

    return loaded
