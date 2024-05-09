from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('contact/', views.contact, name='contact'),
    path('message/', views.messaging, name='msg'),
    path('message/<int:sender>', views.messaging, name='msg_ctx'),
    path('reserve/', views.ReserveView.as_view(), name='reserve'),
    path('lot/<int:pk>', views.LotView.as_view(), name='lot'),
    path("profile/", views.profile, name="profile"),
    path("change_password/", views.change_password, name="change_password"),
    path("reset_password/", auth_views.PasswordResetView.as_view(template_name='frontend/profile/password_reset.html'),
         name="reset_password"),
    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(
        template_name='frontend/profile/password_reset_done.html'), name="password_reset_done"),
    path("reset/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(template_name='frontend/profile/password_reset_confirm.html'),
         name="password_reset_confirm"),
    path("reset_password_complete/",
         auth_views.PasswordResetCompleteView.as_view(template_name='frontend/profile/password_reset_complete.html'),
         name="password_reset_complete"),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
