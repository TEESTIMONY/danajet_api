from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from rest_framework import serializers

from .models import CustomerAddress, CustomerProfile


User = get_user_model()

LOGIN_LOCKOUT_THRESHOLD = 5
LOGIN_LOCKOUT_WINDOW_SECONDS = 15 * 60


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "full_name", "is_staff", "date_joined"]
        read_only_fields = ["id", "is_staff", "date_joined"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=80, required=False, allow_blank=True)
    marketing_opt_in = serializers.BooleanField(required=False, default=False)

    def validate_email(self, value):
        email = value.lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        phone = validated_data.pop("phone", "")
        marketing_opt_in = validated_data.pop("marketing_opt_in", False)
        email = validated_data["email"]
        user = User.objects.create_user(username=email, email=email, password=validated_data["password"])
        user.first_name = validated_data.get("first_name", "")
        user.last_name = validated_data.get("last_name", "")
        user.save(update_fields=["first_name", "last_name"])
        CustomerProfile.objects.create(user=user, phone=phone, marketing_opt_in=marketing_opt_in)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].lower().strip()
        # Locked per-account (not per-IP) so a distributed attack spread across
        # many source IPs can't bypass the request-rate throttle on the view.
        lockout_key = f"login-attempts:{email}"
        attempts = cache.get(lockout_key, 0)
        if attempts >= LOGIN_LOCKOUT_THRESHOLD:
            raise serializers.ValidationError(
                "Too many failed login attempts for this account. Please try again in a few minutes."
            )

        user = User.objects.filter(email__iexact=email).first()
        username = user.get_username() if user else email
        authenticated_user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=attrs["password"],
        )
        if not authenticated_user:
            cache.set(lockout_key, attempts + 1, LOGIN_LOCKOUT_WINDOW_SECONDS)
            raise serializers.ValidationError("Invalid email or password.")

        cache.delete(lockout_key)
        attrs["user"] = authenticated_user
        return attrs


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]
