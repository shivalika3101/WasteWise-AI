"""Record how long a four-model prediction actually takes.

The upload journey sends one image to every approved model. This measures that
cost so a regression is noticed by the team rather than by a marker.

    python tools/inference_smoke.py
    python tools/inference_smoke.py --runs 10 --out docs/inference-smoke.md

Reports cold start (first call, includes loading checkpoints) separately from
warm calls, because only the warm figure represents what a user waits for once
the service is up.

Exits non-zero if the warm median exceeds --budget, so it can be wired into CI
later. It is not in the pipeline by default: CI runners have no checkpoints and
their CPU allocation is too variable to threshold meaningfully.
"""

import argparse as _argparse
import pathlib as _pathlib
import statistics as _statistics
import sys as _sys
import time as _time

_ROOT = _pathlib.Path(__file__).resolve().parents[1]
if str(_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_ROOT))

_DEFAULT_IMAGE = _ROOT / "backend" / "tests" / "fixtures" / "plastic_water_bottle.png"


def _measure(image_bytes, runs):
    import ml.inference.model as model
    import ml.inference.predictor as predictor

    model.load_models.cache_clear()

    started = _time.perf_counter()
    model.load_models()
    load_seconds = _time.perf_counter() - started

    started = _time.perf_counter()
    predictor.predict_models(image_bytes)
    cold_seconds = _time.perf_counter() - started

    warm = []
    for _ in range(runs):
        started = _time.perf_counter()
        predictor.predict_models(image_bytes)
        warm.append(_time.perf_counter() - started)

    return load_seconds, cold_seconds, warm


def main():
    parser = _argparse.ArgumentParser(description=__doc__, formatter_class=_argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--image", type=_pathlib.Path, default=_DEFAULT_IMAGE)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--budget", type=float, default=0.0, help="fail if warm median exceeds this, in seconds")
    parser.add_argument("--out", type=_pathlib.Path, help="append a markdown row to this file")
    arguments = parser.parse_args()

    if not arguments.image.exists():
        print(f"image not found: {arguments.image}", file=_sys.stderr)
        return 2

    import ml.inference.model as model

    missing = [name for name, path in model.MODEL_PATHS.items() if not path.exists()]
    if missing:
        print(f"checkpoints missing, cannot measure: {', '.join(missing)}", file=_sys.stderr)
        return 2

    image_bytes = arguments.image.read_bytes()
    load_seconds, cold_seconds, warm = _measure(image_bytes, arguments.runs)

    median = _statistics.median(warm)
    print(f"image        : {arguments.image.name}")
    print(f"models       : {len(model.MODEL_PATHS)}")
    print(f"load (once)  : {load_seconds:.2f}s")
    print(f"first call   : {cold_seconds:.2f}s")
    print(f"warm median  : {median:.2f}s   over {arguments.runs} runs")
    print(f"warm slowest : {max(warm):.2f}s")
    print(f"warm fastest : {min(warm):.2f}s")

    if arguments.out:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        new = not arguments.out.exists()
        with arguments.out.open("a") as handle:
            if new:
                handle.write("| date | models | load | first call | warm median | runs |\n")
                handle.write("| --- | --- | --- | --- | --- | --- |\n")
            handle.write(
                f"| {_time.strftime('%Y-%m-%d')} | {len(model.MODEL_PATHS)} | "
                f"{load_seconds:.2f}s | {cold_seconds:.2f}s | {median:.2f}s | {arguments.runs} |\n"
            )
        print(f"\nrecorded to {arguments.out}")

    if arguments.budget and median > arguments.budget:
        print(f"\nFAIL: warm median {median:.2f}s exceeds budget {arguments.budget:.2f}s", file=_sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    _sys.exit(main())
