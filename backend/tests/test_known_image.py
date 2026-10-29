import pathlib as _pathlib
import ml.inference.predictor as _predictor
import pytest as _pytest
_FIXTURE = _pathlib.Path(__file__).parent / "fixtures" / "plastic_water_bottle.png"

@_pytest.mark.requires_models
def test_known_image_is_classified():
    prediction = _predictor.predict(_FIXTURE.read_bytes())
    assert prediction.label == "plastic_water_bottles"
    assert prediction.label_index == 24
    assert prediction.confidence > 0.8
