# accounts/urls.py
from django.urls import path
from .views import RegisterView, LogoutView, CurrentUserView, DeleteUserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("user/", CurrentUserView.as_view(), name="current_user"),
    path("delete/", DeleteUserView.as_view(), name="delete_user"),
]
