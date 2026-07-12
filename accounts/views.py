from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from commerce.models import Cart

from .models import CustomerAddress, CustomerProfile
from .serializers import (
    CustomerAddressSerializer,
    CustomerProfileSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


def claim_guest_cart(user, session_key):
    if not session_key:
        return
    Cart.objects.filter(session_key=session_key, user__isnull=True, status="active").update(user=user)


class CsrfView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        claim_guest_cart(user, request.data.get("cart_session_key", ""))
        login(request, user)
        return Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        claim_guest_cart(user, request.data.get("cart_session_key", ""))
        login(request, user)
        return Response({"user": UserSerializer(user).data})


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"user": None})
        return Response({"user": UserSerializer(request.user).data})


class CustomerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomerProfile.objects.select_related("user").all()
        return CustomerProfile.objects.select_related("user").filter(user=self.request.user)

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        profile, _created = CustomerProfile.objects.get_or_create(user=request.user)
        if request.method == "PATCH":
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(self.get_serializer(profile).data)


class CustomerAddressViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["address_type", "is_default"]
    search_fields = ["first_name", "last_name", "city", "country", "postal_code"]
    ordering_fields = ["created_at", "is_default", "city", "country"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomerAddress.objects.select_related("user").all()
        return CustomerAddress.objects.select_related("user").filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
