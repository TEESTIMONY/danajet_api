# Danajet API Endpoints

Base URL for local testing:

```text
http://127.0.0.1:8000
```

All API routes are prefixed with:

```text
/api/
```

For `POST` requests, send JSON with:

```http
Content-Type: application/json
```

## Health

### Check API Health

```http
GET /api/health/
```

Example response:

```json
{
  "status": "ok",
  "service": "danajet-api"
}
```

## Shared Read Query Parameters

Most content list endpoints support:

```text
?search=keyword
?ordering=title
?ordering=-created_at
?page=2
```

Some endpoints also support filters such as:

```text
?category=books
?featured=true
?status=Coming%20Soon
```

Detail endpoints use `slug`:

```http
GET /api/products/the-ultimate-tanzania-activity-book/
```

## Products

### List Products

```http
GET /api/products/
```

Useful filters:

```http
GET /api/products/?category=activity-book
GET /api/products/?featured=true
GET /api/products/?search=tanzania
GET /api/products/?ordering=price
```

### Retrieve Product

```http
GET /api/products/{slug}/
```

Response fields include:

```json
{
  "id": 1,
  "title": "The Ultimate Tanzania Activity Book",
  "slug": "the-ultimate-tanzania-activity-book",
  "subtitle": "Activities for curious young readers",
  "category": "activity-book",
  "author": "Danajet",
  "price": "12.99",
  "sale_price": null,
  "amazon_url": "https://amazon.com/...",
  "rating": "5.0",
  "review_count": 12,
  "age_range": "Ages 6-10",
  "format": "Paperback",
  "featured": true,
  "summary": "Short product description.",
  "image": "/media/catalog/book.jpg",
  "is_published": true,
  "display_order": 1,
  "created_at": "2026-07-08T00:00:00Z",
  "updated_at": "2026-07-08T00:00:00Z"
}
```

## Courses

### List Courses

```http
GET /api/courses/
```

Useful filters:

```http
GET /api/courses/?category=publishing
GET /api/courses/?status=Coming%20Soon
GET /api/courses/?featured=true
GET /api/courses/?level=Beginner
GET /api/courses/?search=epub
```

### Retrieve Course

```http
GET /api/courses/{slug}/
```

## Categories

Categories group products, courses, portfolio projects, services, and blog posts.

```http
GET /api/categories/
GET /api/categories/{slug}/
```

Useful filters:

```http
GET /api/categories/?category_type=product
GET /api/categories/?is_visible=true
```

## Portfolio Projects

### List Portfolio Projects

```http
GET /api/portfolio/
```

Useful filters:

```http
GET /api/portfolio/?category=educational-materials
GET /api/portfolio/?featured=true
GET /api/portfolio/?service_type=Book%20Design
GET /api/portfolio/?search=MISA
```

### Retrieve Portfolio Project

```http
GET /api/portfolio/{slug}/
```

## Services

### List Services

```http
GET /api/services/
```

Useful examples:

```http
GET /api/services/?search=formatting
GET /api/services/?ordering=display_order
```

### Retrieve Service

```http
GET /api/services/{slug}/
```

## Reviews

### List Reviews

```http
GET /api/reviews/
```

Useful filters:

```http
GET /api/reviews/?service=amazon
GET /api/reviews/?rating=5
GET /api/reviews/?search=Richard
```

### Retrieve Review

```http
GET /api/reviews/{slug}/
```

## Brands

### List Brands

```http
GET /api/brands/
```

### Retrieve Brand

```http
GET /api/brands/{slug}/
```

## Blog Posts

### List Blog Posts

```http
GET /api/blog-posts/
```

Useful examples:

```http
GET /api/blog-posts/?author=Danajet
GET /api/blog-posts/?search=publishing
GET /api/blog-posts/?ordering=-published_at
```

### Retrieve Blog Post

```http
GET /api/blog-posts/{slug}/
```

## Site Content / CMS

These endpoints hold content that is shared across pages or controlled from the admin dashboard. Public users can read visible/published records. Staff users can create, update, and delete records through the API or Django admin.

### Navigation

```http
GET /api/navigation/
GET /api/navigation/?area=header
GET /api/navigation/?area=footer
```

### Page Sections

```http
GET /api/page-sections/
GET /api/page-sections/?page=about
GET /api/page-sections/?section_key=hero
```

### Reusable CTAs

```http
GET /api/ctas/
GET /api/ctas/{slug}/
GET /api/ctas/?location=Homepage%20hero
```

### Media Assets

Use this for images, videos, PDFs, documents, and external media links.

```http
GET /api/media-assets/
GET /api/media-assets/{slug}/
GET /api/media-assets/?asset_type=video
POST /api/media-assets/
```

For file uploads, send `multipart/form-data` as an authenticated staff user.

Example staff upload fields:

```text
title=Danajet About Intro
asset_type=video
file=@about-intro.mp4
usage=About page
alt_text=Daniel introducing Danajet
```

### Site Settings

```http
GET /api/site-settings/
GET /api/site-settings/{key}/
GET /api/site-settings/?group=seo
```

### Social Links

```http
GET /api/social-links/
GET /api/social-links/?platform=TikTok
```

### Request Form Options

Use this for admin-controlled dropdowns and checkbox lists.

```http
GET /api/request-form-options/
GET /api/request-form-options/services/
GET /api/request-form-options/?is_active=true
```

## Project Requests

### Create Project Request

```http
POST /api/project-requests/
```

Body:

```json
{
  "name": "Jane Author",
  "email": "jane@example.com",
  "phone": "+1 555 0100",
  "service": "Book formatting",
  "services": ["Print Book Formatting", "KDP Upload Support"],
  "book_title": "My First Workbook",
  "book_size": "8.5 x 11",
  "page_count": "80",
  "budget": "$500 - $1,000",
  "stage": "Manuscript ready",
  "timeline": "2-4 weeks",
  "referral_source": "Instagram",
  "preferred_contact_method": "email",
  "message": "I need formatting and KDP upload support."
}
```

Expected response:

```http
201 Created
```

### List Project Requests

```http
GET /api/project-requests/
```

Requires staff authentication.

Useful examples:

```http
GET /api/project-requests/?search=jane
GET /api/project-requests/?ordering=-created_at
```

## Contact Messages

### Create Contact Message

```http
POST /api/contact-messages/
```

Body:

```json
{
  "name": "Jane Author",
  "email": "jane@example.com",
  "phone": "+1 555 0100",
  "reason": "Book project",
  "subject": "Publishing question",
  "message": "Can you help with a children's workbook?"
}
```

### List Contact Messages

```http
GET /api/contact-messages/
```

Requires staff authentication.

## Newsletter Subscriptions

### Create Newsletter Subscription

```http
POST /api/newsletter-subscriptions/
```

Body:

```json
{
  "name": "Reader Name",
  "email": "reader@example.com",
  "source": "footer"
}
```

Duplicate emails return a validation error.

### List Newsletter Subscriptions

```http
GET /api/newsletter-subscriptions/
```

Requires staff authentication.

## Transport Waitlist

### Join Transport Waitlist

```http
POST /api/transport-waitlist/
```

Body:

```json
{
  "email": "traveler@example.com",
  "name": "Future Rider",
  "phone": "+1 555 0100",
  "city": "Lagos",
  "notes": "Interested in launch updates."
}
```

Duplicate emails return a validation error.

### List Transport Waitlist

```http
GET /api/transport-waitlist/
```

Requires staff authentication.

## Staff Writes

Catalog and site-content endpoints use the same pattern:

```text
GET    public for published/visible records
POST   staff only
PUT    staff only
PATCH  staff only
DELETE staff only
```

Contact and lead endpoints use:

```text
POST   public
GET    staff only
PUT    staff only
PATCH  staff only
DELETE staff only
```

## Admin

```text
/admin/
```

Use the Django admin to create and manage catalog content, reviews, brands, blog posts, project requests, contact messages, newsletter subscriptions, and transport waitlist entries.

## Notes Before Production

The contact and lead endpoints currently allow list access to make local Postman testing easy. Before production, add authentication or restrict list/retrieve access for:

```text
/api/project-requests/
/api/contact-messages/
/api/newsletter-subscriptions/
/api/transport-waitlist/
```
