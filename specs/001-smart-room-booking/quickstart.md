# Quickstart: Smart Room Booking

## Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python -m app.scripts.seed
uvicorn app.main:app --reload
```

Verify:
```bash
curl http://localhost:8000/api/v1/health
# → {"status":"ok","version":"1.0.0"}

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"pass123"}'
# → {"access_token":"eyJ...","token_type":"bearer"}
```

## Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

## Docker

```bash
docker compose build
docker compose up -d
# Open http://localhost:8000
```

## Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
```
