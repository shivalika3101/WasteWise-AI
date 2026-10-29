import argparse
import pathlib
import sys


_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import ml.inference.model as model
import ml.inference.predictor as predictor


DEFAULT_IMAGE = (
    _REPO_ROOT
    / "backend"
    / "tests"
    / "fixtures"
    / "plastic_water_bottle.png"
)


def main():
    parser = argparse.ArgumentParser(description="Smoke-check the ML ensemble")
    parser.add_argument(
        "image",
        nargs="?",
        type=pathlib.Path,
        default=DEFAULT_IMAGE,
        help="image to classify (defaults to the committed test fixture)",
    )
    args = parser.parse_args()

    image_path = args.image.resolve()
    image_bytes = image_path.read_bytes()

    print(f"Image: {image_path}")
    print("Loading models...")
    loaded_models = model.load_models()
    print("Loaded:", ", ".join(loaded_models))

    model_predictions, failed_models = predictor.predict_models(image_bytes)

    print("\nPer-model results")
    for result in model_predictions:
        print(
            f"{result.model_name}: index={result.label_index}, "
            f"label={result.label}, confidence={result.confidence:.4f}"
        )

    prediction = predictor.combine_predictions(
        model_predictions,
        failed_models,
    )

    print("\nEnsemble result")
    print("Index:", prediction.label_index)
    print("Label:", prediction.label)
    print(f"Confidence: {prediction.confidence:.4f}")
    print("Models used:", ", ".join(prediction.models_used))
    print("Failed models:", ", ".join(failed_models) or "none")


if __name__ == "__main__":
    main()
