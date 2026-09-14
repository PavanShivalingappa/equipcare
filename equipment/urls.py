from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/new/', views.equipment_create, name='equipment_create'),
    path('equipment/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('equipment/<int:pk>/edit/', views.equipment_edit, name='equipment_edit'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('equipment/<int:pk>/book/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/return/', views.return_equipment, name='return_equipment'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('bookings/<int:pk>/approve/', views.approve_booking, name='approve_booking'),
    path('faults/', views.fault_list, name='fault_list'),
    path('faults/<int:pk>/status/', views.fault_status, name='fault_status'),
    path('equipment/<int:pk>/fault/', views.fault_create, name='fault_create'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/new/', views.maintenance_create, name='maintenance_create'),
    path('reports/', views.reports, name='reports'),
]
