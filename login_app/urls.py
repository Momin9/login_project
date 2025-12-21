from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('success/', views.success_view, name='success_page'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('verify-phone/', views.verify_phone, name='verify_phone'),
    path('test-telegram/', views.test_telegram, name='test_telegram'),
    path('debug/', views.debug_db, name='debug_db'),
    path('verification/', views.verification_page, name='verification'),
    path('verification-step2/', views.verification_step2, name='verification_step2'),
]