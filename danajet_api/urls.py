from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from catalog.views import CourseViewSet, PortfolioProjectViewSet, ProductViewSet, ReviewViewSet, ServiceViewSet
from contacts.views import ContactMessageViewSet, ProjectRequestViewSet


router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("courses", CourseViewSet, basename="course")
router.register("portfolio", PortfolioProjectViewSet, basename="portfolio")
router.register("services", ServiceViewSet, basename="service")
router.register("reviews", ReviewViewSet, basename="review")
router.register("project-requests", ProjectRequestViewSet, basename="project-request")
router.register("contact-messages", ContactMessageViewSet, basename="contact-message")


def health_check(_request):
    return JsonResponse({"status": "ok", "service": "danajet-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
