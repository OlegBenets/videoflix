from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from core.utils.tasks import enqueue_after_commit

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Ensures unique email, matching passwords, generates username,
    and enqueues activation email.
    """

    confirmed_password = serializers.CharField(write_only=True)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirmed_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirmed_password"):
            raise serializers.ValidationError({"confirmed_password": "Passwords do not match"})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    @staticmethod
    def generate_username(email: str) -> str:
        """
        Generate a unique username based on email.
        """
        local_part, domain_part = email.split("@", 1)
        domain_clean = domain_part.replace(".", "_")
        return f"{local_part}_{domain_clean}"

    def save(self):
        email = self.validated_data["email"]
        password = self.validated_data["password"]
        username = self.generate_username(email)

        user = User(username=username, email=email, is_active=False)
        user.set_password(password)
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        from auth_app.tasks import send_activation_email

        enqueue_after_commit(send_activation_email, user.pk, uid, token)
        return user, token


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to authenticate using email instead of username.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No valid email or password.")

        if not user.check_password(password):
            raise serializers.ValidationError("No valid email or password.")

        return super().validate({"username": user.username, "password": password})


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset.
    """
    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming new password.
    """

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data["new_password"])
        return data
