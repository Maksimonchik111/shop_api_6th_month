import random
import string

from django.contrib.auth import authenticate
from django.core.cache import cache
from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .models import CustomUser
from .serializers import (
    AuthValidateSerializer,
    ConfirmationSerializer,
    RegisterValidateSerializer,
)


class AuthorizationAPIView(CreateAPIView):
    serializer_class = AuthValidateSerializer

    def post(self, request):
        serializer = AuthValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)

        if user:
            if not user.is_active:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={"error": "User account is not activated yet!"},
                )

            token, _ = Token.objects.get_or_create(user=user)
            return Response(data={"key": token.key})

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={"error": "User credentials are wrong!"},
        )


class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email, password=password, is_active=False
            )

            code = "".join(random.choices(string.digits, k=6))

            cache.set(f"confirmation_code:{user.id}", code, timeout=300)

        return Response(
            status=status.HTTP_201_CREATED,
            data={"user_id": user.id, "confirmation_code": code},
        )


class ConfirmUserAPIView(CreateAPIView):
    serializer_class = ConfirmationSerializer

    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]

        with transaction.atomic():
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()

            token, _ = Token.objects.get_or_create(user=user)

            cache.delete(f"confirmation_code:{user_id}")

        return Response(
            status=status.HTTP_200_OK,
            data={"message": "User аккаунт успешно активирован", "key": token.key},
        )