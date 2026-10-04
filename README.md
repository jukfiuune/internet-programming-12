# Internet Programming 12

Django REST Framework backend and React + Vite frontend.

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Question bank

Load the initial question bank fixture (6 categories, 12 choice questions, 12 numeric questions):

```bash
python backend/manage.py loaddata questions/question_bank.json
```

### Tests

```bash
python backend/manage.py test accounts questions
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on http://localhost:5173 and proxies `/api` to the Django server on port 8000.
