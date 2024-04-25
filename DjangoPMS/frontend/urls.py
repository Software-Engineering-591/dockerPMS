from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('contact/', views.contact),
    path('message/', views.driverMessaging, name='message'),
    path('adminMessage/', views.adminMessages, name='admin'),
    path('adminMessage/<sender>/', views.adminMessageContext, name='adminMessageContext')
    path('reserve/', views.ReserveView.as_view(), name='reserve'),
]

