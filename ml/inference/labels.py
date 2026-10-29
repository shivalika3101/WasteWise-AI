import json as _json
import pathlib as _pathlib

_LABELS_PATH = _pathlib.Path(__file__).parent / "labels.json"

LABELS = _json.loads(_LABELS_PATH.read_text(encoding="utf-8"))
