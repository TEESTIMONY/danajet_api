from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cart, CartItem, Coupon, CourseEnrollment, Order, Payment, ShippingRate
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    CheckoutSerializer,
    CouponSerializer,
    CourseEnrollmentSerializer,
    OrderSerializer,
    PaymentSerializer,
    ShippingRateSerializer,
)


class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        owner = getattr(obj, "user", None)
        if owner:
            return owner == request.user
        cart = getattr(obj, "cart", None)
        return bool(cart and cart.user == request.user)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["status", "currency"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        queryset = Cart.objects.prefetch_related("items", "items__product", "items__course")
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return queryset
            return queryset.filter(user=self.request.user)
        session_key = self.request.query_params.get("session_key")
        return queryset.filter(session_key=session_key, user__isnull=True) if session_key else Cart.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)

    @action(detail=True, methods=["post"], url_path="items")
    def add_item(self, request, pk=None):
        cart = self.get_object()
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        product = data.get("product")
        course = data.get("course")
        item_type = data["item_type"]
        target_filter = {"product": product} if item_type == "product" else {"course": course}
        item = cart.items.filter(item_type=item_type, **target_filter).first()
        source = product or course
        if item:
            item.quantity += data["quantity"]
            item.save(update_fields=["quantity", "updated_at"])
        else:
            item = CartItem.objects.create(
                cart=cart,
                item_type=item_type,
                product=product,
                course=course,
                title=source.title,
                sku=getattr(source, "sku", ""),
                unit_price=source.price,
                quantity=data["quantity"],
            )
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="clear")
    def clear(self, request, pk=None):
        cart = self.get_object()
        cart.items.all().delete()
        return Response(self.get_serializer(cart).data)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["cart", "item_type", "product", "course"]

    def get_queryset(self):
        queryset = CartItem.objects.select_related("cart", "product", "course")
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return queryset
            return queryset.filter(cart__user=self.request.user)
        session_key = self.request.query_params.get("session_key")
        return queryset.filter(cart__session_key=session_key, cart__user__isnull=True) if session_key else CartItem.objects.none()


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["status", "payment_status", "email"]
    search_fields = ["order_number", "email", "first_name", "last_name"]
    ordering_fields = ["created_at", "updated_at", "total", "status"]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related("items", "payments")
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return queryset
            return queryset.filter(user=self.request.user)
        return Order.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)


class CheckoutViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ["discount_type", "is_active"]
    search_fields = ["code"]
    ordering_fields = ["code", "amount", "created_at"]

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny], url_path="validate")
    def validate_coupon(self, request):
        code = request.data.get("code", "")
        coupon = Coupon.objects.filter(code__iexact=code, is_active=True).first()
        if not coupon:
            return Response({"valid": False}, status=status.HTTP_404_NOT_FOUND)
        return Response({"valid": True, "coupon": self.get_serializer(coupon).data})


class ShippingRateViewSet(viewsets.ModelViewSet):
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    filterset_fields = ["country", "region", "is_active"]
    search_fields = ["name", "country", "region"]
    ordering_fields = ["amount", "name", "created_at"]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user and self.request.user.is_staff:
            return queryset
        return queryset.filter(is_active=True)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["order", "provider", "status"]
    search_fields = ["provider_reference", "order__order_number"]
    ordering_fields = ["created_at", "amount", "status"]

    def get_queryset(self):
        queryset = Payment.objects.select_related("order")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(order__user=self.request.user)

    @action(detail=False, methods=["post"], url_path="intent")
    def intent(self, request):
        order_id = request.data.get("order")
        order = Order.objects.filter(pk=order_id).first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_staff and order.user_id != request.user.id:
            return Response({"detail": "You do not have access to this order."}, status=status.HTTP_403_FORBIDDEN)
        payment = Payment.objects.create(
            order=order,
            provider=request.data.get("provider", "manual"),
            amount=order.total,
            currency=order.currency,
            metadata={"intent": "placeholder"},
        )
        return Response(self.get_serializer(payment).data, status=status.HTTP_201_CREATED)


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course", "status"]
    ordering_fields = ["created_at", "progress", "status"]

    def get_queryset(self):
        queryset = CourseEnrollment.objects.select_related("user", "course", "order")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
