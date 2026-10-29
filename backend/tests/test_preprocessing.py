import io as _io
import PIL.Image as _image
import pytest as _pytest
import torch as _torch
import ml.inference.preprocessing as _preprocessing


def _encode(mode, colour="white", size=(80, 50), image_format="PNG"):
    buffer = _io.BytesIO()
    _image.new(mode, size, colour).save(buffer, format=image_format)
    return buffer.getvalue()


def test_batch_shape():
    assert tuple(_preprocessing.preprocess(_encode("RGB")).shape) == (1, 3, 224, 224)


def test_dtype():
    assert _preprocessing.preprocess(_encode("RGB")).dtype is _torch.float32


def test_white_scales_to_one():
    assert _preprocessing.preprocess(_encode("RGB")).max().item() == 1.0


def test_black_scales_to_zero():
    assert _preprocessing.preprocess(_encode("RGB", colour="black")).min().item() == 0.0


def test_greyscale_becomes_three_channels():
    assert _preprocessing.preprocess(_encode("L")).shape[1] == 3


def test_transparency_becomes_three_channels():
    assert _preprocessing.preprocess(_encode("RGBA")).shape[1] == 3


def test_jpeg_is_accepted():
    encoded = _encode("RGB", image_format="JPEG")
    assert tuple(_preprocessing.preprocess(encoded).shape) == (1, 3, 224, 224)


def test_undecodable_bytes_raise():
    with _pytest.raises(_preprocessing.InvalidImageError):
        _preprocessing.preprocess(b"this is not an image")


def test_empty_bytes_raise():
    with _pytest.raises(_preprocessing.InvalidImageError):
        _preprocessing.preprocess(b"")


def test_truncated_image_raises():
    encoded = _encode("RGB", image_format="JPEG", size=(400, 400))
    with _pytest.raises(_preprocessing.InvalidImageError):
        _preprocessing.preprocess(encoded[: len(encoded) // 3])
