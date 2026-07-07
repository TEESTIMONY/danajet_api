# Danajet Django REST API

Backend scaffold for the Danajet website. This directory is separate from the React/Vite frontend so it can be pushed to its own GitHub repository.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API Routes

- `GET /api/health/`
- `GET /api/products/`
- `GET /api/courses/`
- `GET /api/portfolio/`
- `GET /api/services/`
- `GET /api/reviews/`
- `POST /api/project-requests/`
- `POST /api/contact-messages/`

Admin is available at `/admin/`.
