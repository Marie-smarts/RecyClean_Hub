from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.payment_history_view, name='payment_history'),
    path('initiate/', views.initiate_payment_view, name='initiate_payment'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
]