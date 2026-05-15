from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('book/<int:business_id>/', views.book_appointment, name='book_appointment'),
    path('payment/<int:business_id>/', views.payment_info, name='payment_info'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('settings/payment/', views.update_payment_info, name='update_payment_info'),
]