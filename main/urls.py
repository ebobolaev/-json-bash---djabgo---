from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('run-script/', views.bash_script, name='run_script'),
]