# Danajet Django REST API

Backend scaffold for the Danajet website. This directory is separate from the React/Vite frontend so it can be pushed to its own GitHub repository later.

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
- `/api/categories/`
- `GET /api/products/`
- `GET /api/courses/`
- `GET /api/portfolio/`
- `GET /api/services/`
- `GET /api/reviews/`
- `GET /api/brands/`
- `GET /api/blog-posts/`
- `/api/navigation/`
- `/api/page-sections/`
- `/api/ctas/`
- `/api/media-assets/`
- `/api/site-settings/`
- `/api/social-links/`
- `/api/request-form-options/`
- `POST /api/project-requests/`
- `POST /api/contact-messages/`
- `POST /api/newsletter-subscriptions/`
- `POST /api/transport-waitlist/`

Catalog and site-content endpoints are publicly readable and staff-writable. Lead/contact endpoints allow public `POST` submissions, while list/retrieve/update/delete are staff-only. Django admin is available at `/admin/`.

Full endpoint documentation and Postman-ready sample payloads are in:

```text
docs/api-endpoints.md
```

## Render deployment

This backend is ready for Render with `render.yaml`, `build.sh`, and `Procfile`.

Recommended Render settings if creating manually:

- Root directory: `django-api`
- Build command: `bash build.sh`
- Start command: `gunicorn danajet_api.wsgi:application`
- Health check path: `/api/health/`
- Add a PostgreSQL database and set `DATABASE_URL` from its internal connection string.
- Add a persistent disk mounted at `/var/data` and set `DJANGO_MEDIA_ROOT=/var/data/media` so uploaded files persist.

Required environment variables:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<generate a strong secret>
DJANGO_ALLOWED_HOSTS=<your-render-service>.onrender.com
DJANGO_CORS_ALLOWED_ORIGINS=<your-frontend-origin>
DATABASE_URL=<render-postgres-internal-url>
DJANGO_MEDIA_ROOT=/var/data/media
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SESSION_COOKIE_SAMESITE=None
DJANGO_CSRF_COOKIE_SAMESITE=None
DJANGO_SUPERUSER_EMAIL=<admin-email>
DJANGO_SUPERUSER_USERNAME=<admin-username-or-email>
DJANGO_SUPERUSER_PASSWORD=<admin-password>
```

The deploy build runs `python manage.py ensure_superuser`, so Render will create or update the admin account automatically when the `DJANGO_SUPERUSER_*` variables are set.
