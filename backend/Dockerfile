FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=180 \
    PIP_RETRIES=10

WORKDIR /repo

# CPU-only PyTorch.
#
# ml/inference/model.py loads the checkpoint with map_location="cpu", so the GPU
# build is never used. The default PyPI wheel pulls ~3 GB of nvidia-* CUDA
# packages, which is what makes this layer slow and prone to failing partway
# through with IncompleteRead / ChunkedEncodingError. The CPU wheels are a few
# hundred MB instead.
RUN pip install \
        --index-url https://download.pytorch.org/whl/cpu \
        --extra-index-url https://pypi.org/simple \
        "torch>=2.13.0,<3.0.0" \
        "torchvision>=0.28.0,<0.29.0"

# Remaining runtime dependencies, mirroring backend/pyproject.toml.
# NOTE: keep this list in sync if backend/pyproject.toml gains a dependency.
RUN pip install \
        "fastapi[standard]>=0.139.0,<0.140.0" \
        "keras==3.15.0" \
        "pillow>=12.3.0,<13.0.0" \
        "pydantic-settings>=2.14.2,<3.0.0" \
        "sqlalchemy>=2.0.51,<3.0.0" \
        "psycopg[binary]>=3.3.4,<4.0.0" \
        "alembic>=1.18.5,<2.0.0" \
        "bcrypt>=5.0.0,<6.0.0" \
        "pyjwt>=2.13.0,<3.0.0" \
        "numpy>=2.5.1,<3.0.0"

# Source is copied after the dependency layers so that editing application code
# does not invalidate the (expensive) dependency install on rebuild.
#
# app/predictor.py adds the repo root to sys.path itself, so the "ml" package is
# imported by path and does not need to be pip-installed.
COPY ml /repo/ml
COPY backend /repo/backend

WORKDIR /repo/backend

EXPOSE 8000

# Startup order matters:
#   1. bootstrap.run() creates the database if missing and applies Alembic migrations
#   2. seeds.seed populates reference data and self-verifies counts / labels / mappings
#   3. the API starts
# Both steps are idempotent, so restarting the container is safe.
CMD ["sh", "-c", "python -c 'import app.bootstrap as b; b.run()' && python -m seeds.seed && exec fastapi run app/main.py --host 0.0.0.0 --port 8000"]
