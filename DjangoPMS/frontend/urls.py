from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('contact/', views.contact, name='contact'),
    path('message', views.messaging, name='msg'),
    path('driver_message/', views.driver_messaging, name='driver_msg'),
    path('admin_message/', views.admin_messages, name='admin_msg'),
    path(
        'admin_message/<sender>/',
        views.admin_message_ctx,
        name='admin_msg_ctx',
    ),
    path('reserve/', views.ReserveView.as_view(), name='reserve'),
    path('lot/<int:pk>', views.LotView.as_view(), name='lot'),
]
