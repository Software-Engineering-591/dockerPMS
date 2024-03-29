from django.urls import path
from . import views

app_name = "api"
urlpatterns = [
    path("logout/", views.logout, name="logout"),
]
