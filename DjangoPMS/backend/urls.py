from django.urls import path
from . import views

app_name = "api"
urlpatterns = [
    path("logout/", views.logout, name="logout"),
    path("ban/<int:pk>", views.ban, name="ban"),
    path("unban/<int:pk>", views.unban, name="unban"),
]
