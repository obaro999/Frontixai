from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.book, name='book'),
    path('appointments/', views.appointments, name='appointments'),
    path('cancel/', views.cancel, name='cancel'),
    path('payment/', views.payment, name='payment'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
