

from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('api/price-quote/', views.price_quote, name='price_quote'),
    path('api/initialize-paystack/', views.initialize_paystack, name='initialize_paystack'),
    path('paystack/webhook/', views.paystack_webhook, name='paystack_webhook'),
    path("paystack/callback/", views.paystack_callback, name="paystack_callback"), 

    # normal user views
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('', lambda request: redirect('home')),
]

