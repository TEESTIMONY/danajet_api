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
- Create a Supabase Postgres project and set `DATABASE_URL` from its Session Pooler connection string.
- Create a Supabase Storage bucket and set the `SUPABASE_STORAGE_*` variables so uploaded files persist outside Render.

Required environment variables:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<generate a strong secret>
DJANGO_ALLOWED_HOSTS=<your-render-service>.onrender.com
DJANGO_CORS_ALLOWED_ORIGINS=<your-frontend-origin>
DATABASE_URL=postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require
DJANGO_ADMIN_EMAIL=<verified-admin-sender@example.com>
DJANGO_DEFAULT_FROM_EMAIL=<verified-admin-sender@example.com>
DJANGO_EMAIL_HOST=smtp.resend.com
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_HOST_USER=resend
DJANGO_EMAIL_HOST_PASSWORD=<resend-api-key>
DJANGO_EMAIL_USE_TLS=True
DJANGO_EMAIL_USE_SSL=False
SUPABASE_STORAGE_ENABLED=True
SUPABASE_STORAGE_BUCKET=danajet-media
SUPABASE_STORAGE_ENDPOINT=https://<project-ref>.supabase.co/storage/v1/s3
SUPABASE_STORAGE_PUBLIC_URL=https://<project-ref>.supabase.co/storage/v1/object/public/danajet-media
SUPABASE_STORAGE_ACCESS_KEY_ID=<supabase-storage-s3-access-key>
SUPABASE_STORAGE_SECRET_ACCESS_KEY=<supabase-storage-s3-secret-key>
SUPABASE_STORAGE_REGION=us-east-1
MEDIA_UPLOAD_MAX_MB=100
MEDIA_IMAGE_MAX_WIDTH=1800
MEDIA_IMAGE_MAX_HEIGHT=1800
MEDIA_IMAGE_QUALITY=82
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SESSION_COOKIE_SAMESITE=None
DJANGO_CSRF_COOKIE_SAMESITE=None
DJANGO_SUPERUSER_EMAIL=<admin-email>
DJANGO_SUPERUSER_USERNAME=<admin-username-or-email>
DJANGO_SUPERUSER_PASSWORD=<admin-password>
```

The deploy build runs `python manage.py ensure_superuser`, so Render will create or update the admin account automatically when the `DJANGO_SUPERUSER_*` variables are set.

For Supabase on Render, use the Session Pooler connection string in `DATABASE_URL` and keep `?sslmode=require` at the end of the URL. Do not use the direct `db.<project-ref>.supabase.co` URL on Render, because it can resolve to IPv6 and fail with `Network is unreachable`. Render still hosts the Django API; Supabase only provides the Postgres database.

For Supabase Storage, create a public bucket such as `danajet-media`, then create S3 access keys in Supabase Storage settings. The API optimizes uploaded images before saving them: images are resized to fit within `MEDIA_IMAGE_MAX_WIDTH` x `MEDIA_IMAGE_MAX_HEIGHT`, converted to WebP, and saved at `MEDIA_IMAGE_QUALITY`. Videos are not compressed by Django, so keep short intro videos small and use a dedicated video host later for full course lessons.

For newsletter welcome emails, Resend SMTP is used through Django's email backend. Set `DJANGO_EMAIL_HOST_PASSWORD` to your Resend API key, keep `DJANGO_EMAIL_HOST_USER=resend`, and set `DJANGO_DEFAULT_FROM_EMAIL` to a verified Resend sender/domain. When someone subscribes from the footer or popup, Django saves the subscription and sends a professional welcome email from this sender.
