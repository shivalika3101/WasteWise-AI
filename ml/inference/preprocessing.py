import io as _io
import PIL.Image as _image
import torch as _torch
import torchvision.transforms as _transforms

IMAGE_SIZE = (224, 224)

_transform = _transforms.Compose([
    _transforms.Resize(IMAGE_SIZE),
    _transforms.ToTensor(),
])


class InvalidImageError(Exception):
    pass


def preprocess(image_bytes: bytes) -> _torch.Tensor:
    try:
        image = _image.open(_io.BytesIO(image_bytes)).convert("RGB")
    except (OSError, _image.DecompressionBombError) as error:
        raise InvalidImageError from error
    return _transform(image).unsqueeze(0)
