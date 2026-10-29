# ML

Training notebooks, trained checkpoints, and the inference package used by the backend.

The inference package is framework-independent from FastAPI and PostgreSQL. It performs image classification only.

See `MODEL.md` for the complete model contract.

---

# Layout

| Path | Contents |
|------|----------|
| data/ | Dataset loading utilities |
| notebooks/ | Training and evaluation notebooks |
| models/ | Trained model checkpoints |
| results/ | Evaluation reports and confusion matrices |
| inference/ | Runtime inference package |

---

# Inference package

The inference package accepts the bytes of a single image and returns one prediction.

Example

```python
import ml.inference.predictor as predictor

prediction = predictor.predict(image_bytes)

prediction.label_index
prediction.label
prediction.confidence
```

The backend never needs to know which models are being used internally.

---

# Ensemble architecture

The inference package loads four models:

- MobileNetV2
- EfficientNet-B0
- ResNet50
- DenseNet121

All four models classify the image independently.

Each produces a probability vector over the same 30 classes.

The vectors are averaged to produce the final prediction.

```
Image
   │
   ├── MobileNetV2
   ├── EfficientNet-B0
   ├── ResNet50
   └── DenseNet121
           │
Average probabilities
           │
 Argmax
           │
 Final Prediction
```

---

# Label contract

The ordered labels are stored in

```
inference/labels.json
```

Every model uses exactly this class ordering.

The order is derived from the alphabetical ImageFolder directory ordering used during training.

Changing the order invalidates every prediction.

---

# Preprocessing

Three PyTorch models use

- RGB conversion
- Resize to 224×224
- ToTensor()

DenseNet121 uses

- RGB conversion
- Resize to 224×224

The saved Keras model performs its own preprocessing internally and runs
through the existing PyTorch backend.

---

# Model loading

Models are loaded only once.

The loaded models are cached for the lifetime of the process.

This avoids repeatedly loading checkpoints from disk for every prediction.

---

# Smoke test

A smoke test is included.

Run from the repository root:

```cmd
python -m ml.inference.smoke_test
```

The default image path is resolved from the script location, so this command
also works when launched from another directory. An alternative image path can
be supplied as the command's final argument.

Expected output:

```
Loading models...
Loaded: mobilenet, efficientnet, resnet, densenet

Per-model results
mobilenet: index=..., label=..., confidence=...
efficientnet: index=..., label=..., confidence=...
resnet: index=..., label=..., confidence=...
densenet: index=..., label=..., confidence=...

Ensemble result
Index: ...
Label: ...
Confidence: ...
Models used: ...
Failed models: none
```

The smoke test verifies

- every checkpoint loads successfully
- every model produces valid output
- the ensemble returns a valid prediction

---

# Running tests

From `backend/`

```cmd
poetry run pytest
```

The test suite covers

- model loading
- preprocessing
- label contract
- predictor validation
- backend integration

---

# Current limitations

- CPU-only inference
- Equal weighting of all models
- No confidence threshold
- No uncertainty estimation
- No model calibration beyond the comparison completed in Issue #51
