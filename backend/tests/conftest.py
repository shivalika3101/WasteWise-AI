"""Shared pytest configuration.

`ml/models/` is gitignored, so a fresh clone — including every CI runner — has
no checkpoints on disk. Tests that need the real files are marked
`requires_models` and skip with a clear reason when they are absent, rather
than failing and making the pipeline red for an environment issue.

Deliberately does not import `ml.inference.model`: that pulls in torch and
keras at collection time, which is slow and would fail confusingly if the
dependencies were not installed yet.
"""

import pathlib as _pathlib

import pytest as _pytest

_MODEL_DIR = _pathlib.Path(__file__).resolve().parents[2] / "ml" / "models"

_CHECKPOINTS = (
    "mobilenetv2_best.pth",
    "efficientnet_b0_best.pth",
    "resnet50_best.pth",
    "densenet_final.keras",
)


def missing_checkpoints() -> list[str]:
    return [name for name in _CHECKPOINTS if not (_MODEL_DIR / name).exists()]


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "requires_models: needs the real checkpoints in ml/models to be present on disk",
    )


def pytest_collection_modifyitems(config, items):
    missing = missing_checkpoints()
    if not missing:
        return

    skip = _pytest.mark.skip(
        reason=f"checkpoints not on disk: {', '.join(missing)} (see ml/MODEL.md)"
    )
    for item in items:
        if "requires_models" in item.keywords:
            item.add_marker(skip)


def pytest_report_header(config):
    missing = missing_checkpoints()
    if missing:
        return f"model checkpoints MISSING ({len(missing)}/{len(_CHECKPOINTS)}) - inference tests will skip"
    return f"model checkpoints present ({len(_CHECKPOINTS)}/{len(_CHECKPOINTS)})"
