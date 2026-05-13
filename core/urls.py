from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register, name='register'),
    path('login/', views.business_login, name='login'),
    path('logout/', views.business_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('setup-payment/', views.setup_payment, name='setup_payment'),
    path('<str:username>/', views.home, name='home'),
    path('<str:username>/book/', views.book, name='book'),
    path('<str:username>/payment/', views.payment, name='payment'),
    path('<str:username>/appointments/', views.appointments, name='appointments'),
    path('<str:username>/cancel/', views.cancel, name='cancel'),
]
