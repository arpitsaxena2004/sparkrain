from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.savings_dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/download/', views.analytics_download, name='analytics_download'),
    path('savings/', views.savings_dashboard, name='savings_dashboard'),
    path('api/savings/latest/', views.savings_latest_api, name='savings_latest_api'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('about/', views.about, name='about'),
    path('vendors/', views.vendor_list, name='vendors'),
    path('calculate/', views.calculate, name='calculate'),
    
    # Flood prediction & water management
    path('flood/', views.flood_dashboard, name='flood_dashboard'),
    path('mvp/', views.water_guard_mvp, name='water_guard_mvp'),
    path('api/flood/predict/', views.flood_prediction_api, name='flood_prediction_api'),
    path('api/tank/update/', views.update_tank_level, name='update_tank_level'),
    path('flood/history/', views.prediction_history, name='prediction_history'),
    
    # Borewell depth estimation
    path('api/borewell/estimate/', views.borewell_estimation_api, name='borewell_estimation_api'),
    path('borewell/history/', views.borewell_history, name='borewell_history'),
    path('api/district/rainfall/', views.get_district_rainfall_api, name='get_district_rainfall_api'),
    path('api/districts/', views.get_all_districts_api, name='get_all_districts_api'),
]
