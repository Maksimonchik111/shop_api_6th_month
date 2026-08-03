from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import ConfirmationCode, CustomUser



class OAuthSerializer(serializers.Serializer):
    code = serializers.CharField()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["phone_number"] = user.phone_number
        token["email"] = user.email
        token["is_staff"] = user.is_staff
        token["is_active"] = user.is_active
        if user.birthday:
            token["birthday"] = user.birthday.isoformat()
        else:
            token["birthday"] = None

        return token


class UserBaseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class AuthValidateSerializer(UserBaseSerializer):
    pass


class RegisterValidateSerializer(UserBaseSerializer):
    def validate_email(self, email):
        try:
            User.objects.get(email=email)
        except:
            return email
        raise ValidationError("User уже существует!")


class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        code = attrs.get("code")

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError("User не существует!")

        try:
            confirmation_code = ConfirmationCode.objects.get(user=user)
        except ConfirmationCode.DoesNotExist:
            raise ValidationError("Код подтверждения не найден!")

        if confirmation_code.code != code:
            raise ValidationError("Неверный код подтверждения!")

        return attrs