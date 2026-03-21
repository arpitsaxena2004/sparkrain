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
]
