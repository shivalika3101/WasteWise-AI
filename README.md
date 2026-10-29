# WasteWise AI

A full-stack web app that identifies household waste from a photo or live camera, sorts it into one of 30 categories and recommends the right bin, with an on-screen bin-door animation.

This was a team project at Cardiff University. This repository is a public copy of the team's code.

## My contribution

- React frontend and login flow
- Protected image-classification API in FastAPI
- Prediction history and bin-verification feedback
- Integration of the four-model CNN ensemble (MobileNetV2, EfficientNet-B0, ResNet50, DenseNet121), trained by teammates

## Project approach

The team is using the [Recyclable and Household Waste Classification dataset](https://www.kaggle.com/datasets/alistairking/recyclable-and-household-waste-classification), which contains approximately 15,000 images across 30 categories. The ML team trains and evaluates transfer-learning CNN models using studio and real-world image splits. Model comparison considers accuracy, precision/recall/F1, confusion matrices, and inference time. The application integrates four approved models as an equal-weight probability ensemble.

Python notebooks support experimentation and training. Streamlit is used internally to present and compare ML results; it is not the user-facing product.

## Technology stack

- Frontend: React with Vite
- Backend: FastAPI with Python
- Database: PostgreSQL
- Database access and migrations: SQLAlchemy and Alembic
- Machine learning: PyTorch and TensorFlow/Keras transfer-learning CNNs, Python notebooks, and Streamlit for internal model review
- Development environment: Docker and Docker Compose

## Repository structure

```text
backend/
  app/
    routers/
  tests/
frontend/
  public/
  src/
    assets/
    components/
    hooks/
    pages/
    services/
ml/
  notebooks/
  streamlit/
  data/       # ignored: training data
  models/     # ignored: exported model artefacts
  results/
docs/
db_scripts/
```

## Getting started

> **Model files are not included.** The trained model weights (about 160 MB) are too large for this repository. To run predictions, place `mobilenetv2_best.pth`, `efficientnet_b0_best.pth`, `resnet50_best.pth` and `densenet_final.keras` in `ml/models/`. You can train them with the notebooks in `ml/notebooks/`.

### Prerequisites

Make sure you have the following installed:

- **Python** `>=3.12, !=3.14.1, <4.0`
- **Git**
- **Docker Desktop** 
- **Node.js and npm** `v18 or higher`  

---

### 1. Clone the repository

```bash
git clone https://github.com/shivalika3101/WasteWise-AI.git
cd WasteWise-AI
```

---

### 2. Database setup

Open Docker Desktop and keep it running. From the repository root open a terminal:

```cmd
docker compose -f db_scripts/docker-compose.yml up -d
```

Verify that the container is running:

```cmd
docker ps
```

---

### 3. Backend setup 

Open a **new terminal**.

Navigate to the backend folder.

```cmd
cd backend
python -m venv .venv
```

Activate the virtual environment.

```cmd
.venv\Scripts\activate
```

Install Poetry.

```cmd
pip install poetry
```

Install all backend dependencies.

```cmd
poetry install
```

Copy the environment file.

```cmd
copy .env.example .env
```

---

Start the backend (with the virtual environment activated):

```cmd
python -m uvicorn app.main:app --reload
```

The backend will be available at:

```
http://127.0.0.1:8000
```

You can verify it is running by opening:

```
http://127.0.0.1:8000/docs
```

---

### 4. Frontend setup

Open a **new terminal**.

Navigate to the frontend folder.

```cmd
cd frontend
```

Install the frontend dependencies.

```cmd
npm install
```

Start the development server.

```cmd
npm run dev
```

The frontend will usually be available at:

```
http://localhost:5173
```

---

### 5. Running the application

To use the application, ensure all three services are running:

- PostgreSQL (Docker)
- FastAPI backend
- React frontend

Then open your browser and navigate to:

```
http://localhost:5173
```

The frontend communicates with the FastAPI backend, which loads the machine-learning ensemble and retrieves disposal guidance from PostgreSQL.