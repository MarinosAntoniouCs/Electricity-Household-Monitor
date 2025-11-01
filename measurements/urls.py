from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/measurements/insert/', views.insert_measurement, name='insert_measurement'),
    path('measurements/', views.list_measurements, name='list_measurements'),
    path('dashboard/', views.dashboard, name='dashboard'),
]