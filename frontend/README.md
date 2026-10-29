# WasteWise AI Frontend

Frontend for the WasteWise AI project developed using React and Vite.

## Features

- React + Vite
- React Router
- Responsive user interface
- Home page
- Image Upload page
- Live Scan page
- Prediction Result page
- Bin Verification page
- About page

## Requirements

- Node.js (v18 or later)
- npm

## Installation

Clone the repository and navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

## Running the development server

The API and PostgreSQL database must be running before registration, sign-in,
upload and history can work. From the repository root, start the database:

```bash
docker compose -f db_scripts/docker-compose.yml up -d
```

Then, in a separate terminal, start the API from `backend/`:

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Finally, from `frontend/`, run:

```bash
npm run dev
```

The application will be available at:

```
http://localhost:5173
```

## Build for production

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   ├── services/
│   ├── App.jsx
│   └── main.jsx
├── package.json
└── vite.config.js
```

## Current Status

The frontend is integrated with the FastAPI authentication, prediction and
prediction-history endpoints through the Vite development proxy.
