from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve
from rest_framework.routers import DefaultRouter

from accounts.views import CsrfView, CustomerAddressViewSet, CustomerProfileViewSet, LoginView, LogoutView, MeView, RegisterView
from catalog.views import (
    BlogPostViewSet,
    BrandViewSet,
    CategoryViewSet,
    CourseViewSet,
    PortfolioProjectViewSet,
    ProductViewSet,
    ReviewViewSet,
    ServiceViewSet,
)
from commerce.views import (
    CartItemViewSet,
    CartViewSet,
    CheckoutViewSet,
    CouponViewSet,
    CourseEnrollmentViewSet,
    OrderViewSet,
    PaymentViewSet,
    ShippingRateViewSet,
)
from contacts.views import ContactMessageViewSet, NewsletterSubscriptionViewSet, ProjectRequestViewSet, TransportWaitlistViewSet
from sitecontent.views import (
    CallToActionViewSet,
    MediaAssetViewSet,
    NavigationItemViewSet,
    PageSectionViewSet,
    RequestFormOptionSetViewSet,
    SiteSettingViewSet,
    SocialLinkViewSet,
)


router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("courses", CourseViewSet, basename="course")
router.register("portfolio", PortfolioProjectViewSet, basename="portfolio")
router.register("services", ServiceViewSet, basename="service")
router.register("reviews", ReviewViewSet, basename="review")
router.register("brands", BrandViewSet, basename="brand")
router.register("blog-posts", BlogPostViewSet, basename="blog-post")
router.register("customer-profiles", CustomerProfileViewSet, basename="customer-profile")
router.register("customer-addresses", CustomerAddressViewSet, basename="customer-address")
router.register("carts", CartViewSet, basename="cart")
router.register("cart-items", CartItemViewSet, basename="cart-item")
router.register("orders", OrderViewSet, basename="order")
router.register("checkout", CheckoutViewSet, basename="checkout")
router.register("payments", PaymentViewSet, basename="payment")
router.register("shipping-rates", ShippingRateViewSet, basename="shipping-rate")
router.register("coupons", CouponViewSet, basename="coupon")
router.register("course-enrollments", CourseEnrollmentViewSet, basename="course-enrollment")
router.register("project-requests", ProjectRequestViewSet, basename="project-request")
router.register("contact-messages", ContactMessageViewSet, basename="contact-message")
router.register("newsletter-subscriptions", NewsletterSubscriptionViewSet, basename="newsletter-subscription")
router.register("transport-waitlist", TransportWaitlistViewSet, basename="transport-waitlist")
router.register("navigation", NavigationItemViewSet, basename="navigation")
router.register("page-sections", PageSectionViewSet, basename="page-section")
router.register("ctas", CallToActionViewSet, basename="cta")
router.register("media-assets", MediaAssetViewSet, basename="media-asset")
router.register("site-settings", SiteSettingViewSet, basename="site-setting")
router.register("social-links", SocialLinkViewSet, basename="social-link")
router.register("request-form-options", RequestFormOptionSetViewSet, basename="request-form-option")


def health_check(_request):
    return JsonResponse({"status": "ok", "service": "danajet-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/auth/csrf/", CsrfView.as_view(), name="auth-csrf"),
    path("api/auth/register/", RegisterView.as_view(), name="auth-register"),
    path("api/auth/login/", LoginView.as_view(), name="auth-login"),
    path("api/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("api/auth/me/", MeView.as_view(), name="auth-me"),
    path("api/", include(router.urls)),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
