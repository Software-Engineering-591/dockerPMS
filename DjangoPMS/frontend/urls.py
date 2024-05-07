from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('contact/', views.contact, name='contact'),
    path('message/', views.messaging, name='msg'),
    path('message/<int:sender>', views.messaging, name='msg_ctx'),
    path('reserve/', views.ReserveView.as_view(), name='reserve'),
    path('lot/<int:pk>', views.LotView.as_view(), name='lot'),
    path('raph', views.request_and_payment, name='request_and_payment'),
    path('admin/', views.AdminView.as_view(), name='admin'),
]
