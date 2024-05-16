from django.urls import path
from . import views

app_name = "api"
urlpatterns = [
    path("logout/", views.logout, name="logout"),
    path("ban/<int:pk>", views.ban, name="ban"),
    path("unban/<int:pk>", views.unban, name="unban"),
    path("block/<int:slot_pk>", views.block, name="block"),
    path("free/<int:slot_pk>", views.free, name="free"),
    path("remove/<int:slot_pk>", views.remove, name="remove"),

    path("accept/<int:request_pk>", views.accept, name="accept"),
    path("reject/<int:request_pk>", views.reject, name="reject"),
]
