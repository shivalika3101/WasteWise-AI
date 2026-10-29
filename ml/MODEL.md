# Ensemble model hand-off

Record of the models used by the inference package and the locked
ML/backend contract. The team agreed to use all four approved model packages
and average their class-probability vectors.

## Models included in the ensemble

All paths are relative to the repository root.

| Name | Package | Architecture | Runtime and loading method |
| --- | --- | --- | --- |
| `mobilenet` | `ml/models/mobilenetv2_best.pth` | MobileNetV2 | PyTorch `state_dict`, rebuilt with torchvision and loaded on CPU |
| `efficientnet` | `ml/models/efficientnet_b0_best.pth` | EfficientNet-B0 | PyTorch `state_dict`, rebuilt with torchvision and loaded on CPU |
| `resnet` | `ml/models/resnet50_best.pth` | ResNet50 | PyTorch `state_dict`, rebuilt with torchvision and loaded on CPU |
| `densenet` | `ml/models/densenet_final.keras` | DenseNet121 | Keras 3.15 package loaded with the PyTorch backend |

The PyTorch models are put into evaluation mode after loading. All model
packages are loaded once and cached for later predictions.

## Ensemble strategy

Each available model returns a probability vector with 30 entries. The
vectors are normalised and averaged class by class:

```text
average_probability = sum(available_probability_vectors) / available_model_count
label_index = argmax(average_probability)
confidence = average_probability[label_index]
```

An exact tie resolves to the lowest canonical label index.

Arithmetic mean probability was chosen as the team ensemble rule. Equal
weighting is reasonable for this checkpoint because the models achieved
similar test accuracy, but the current evidence does not prove that their
confidence values are calibrated.

## Model formats

### MobileNetV2

```python
model = torchvision.models.mobilenet_v2(weights=None)
model.classifier[1] = torch.nn.Linear(
    model.classifier[1].in_features,
    30,
)
model.load_state_dict(torch.load(path, map_location="cpu"))
model.eval()
```

### EfficientNet-B0

```python
model = torchvision.models.efficientnet_b0(weights=None)
model.classifier[1] = torch.nn.Linear(
    model.classifier[1].in_features,
    30,
)
model.load_state_dict(torch.load(path, map_location="cpu"))
model.eval()
```

### ResNet50

```python
model = torchvision.models.resnet50(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, 30)
model.load_state_dict(torch.load(path, map_location="cpu"))
model.eval()
```

### DenseNet121

```python
os.environ["KERAS_BACKEND"] = "torch"
model = keras.models.load_model(path)
```

Using Keras with the existing PyTorch backend avoids a second large ML runtime
and remains compatible with the project's supported Python versions.

## Framework versions

| Package | Version |
| --- | --- |
| Python | 3.12 to 3.14, excluding 3.14.1 |
| torch | 2.13 |
| torchvision | 0.28 |
| keras | 3.15 |
| pillow | 12.x |

## Ordered labels and output contract

All four models use the canonical class order in
`ml/inference/labels.json`. It matches
`ml/notebooks/class_names.json`, which records the alphabetical directory
ordering used during training.

Changing the order would silently invalidate predictions. A replacement model
with a different class order must include and test an explicit mapping.

Every model output must contain 30 finite, non-negative values with positive
total probability. It is normalised before ensemble averaging.

The ensemble returns:

```text
Prediction(
    label_index,
    label,
    confidence,
    models_used,
    failed_models,
)
```

- `label_index` is an integer from 0 to 29.
- `label` equals `labels.json[label_index]`.
- `confidence` is a probability between 0 and 1.
- `models_used` records the successful model names.
- `failed_models` records packages that failed to load or predict.

## Preprocessing

The three PyTorch models use the shared preprocessing in
`ml/inference/preprocessing.py`:

- RGB conversion
- resize to 224 by 224
- `ToTensor()` scaling to `[0, 1]`
- batch shape `(1, 3, 224, 224)`

No additional normalisation is applied because the models were trained without
it.

DenseNet receives RGB pixels resized to 224 by 224 in NHWC format. Its saved
Keras graph contains the DenseNet preprocessing layer.

## Failure and confidence rules

1. If one model fails to load or predict, inference uses the remaining models
   and records the failed name.
2. If every model fails, inference raises an error and returns no
   classification.
3. Low-confidence results are returned with their confidence. This hand-off
   does not define a rejection threshold.

## Evidence and limitations

The comparison recorded in Issue #51 reported:

| Model | Test accuracy |
| --- | ---: |
| MobileNetV2 | 85.33% |
| EfficientNet-B0 | 86.22% |
| ResNet50 | 85.73% |
| DenseNet121 | 82.80% |

Per-class confusion matrices and classification reports in `ml/results/`
remain the source for model-specific weaknesses. Current limitations are:

- CPU-only inference
- equal model weighting
- no rejection threshold
- no calibration study beyond the Issue #51 comparison

The MobileNet training notebook saved the final epoch under the
`mobilenetv2_best.pth` filename because its best-checkpoint block was outside
the epoch loop. The recorded result was measured from that package, but the
filename overstates its selection method.

## Smoke check

From the repository root:

```text
python -m ml.inference.smoke_test
```

The default image is the committed fixture at
`backend/tests/fixtures/plastic_water_bottle.png`. The path is resolved from
the script location, so the smoke check also works when launched from another
directory.

An alternative repository-relative or absolute path can be supplied:

```text
python -m ml.inference.smoke_test path/to/image.png
```

The command prints each successful model's name, label index, label and
confidence, followed by the ensemble result and any failed model names.
