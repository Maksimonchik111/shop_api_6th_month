from django.urls import path

from users.google_oauth import GoogleLoginAPIView
from users.views import AuthorizationAPIView, ConfirmUserAPIView, RegistrationAPIView

urlpatterns = [
    path("registration/", RegistrationAPIView.as_view()),
    path("authorization/", AuthorizationAPIView.as_view()),
    path("confirm/", ConfirmUserAPIView.as_view()),
    path("google_login", GoogleLoginAPIView.as_view()),
]