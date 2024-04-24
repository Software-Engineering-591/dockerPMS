from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('Message/', views.DriverMessaging, name='Message'),
    # path('AdminMessage/', views.AdminMessages, name='Admin')
]
