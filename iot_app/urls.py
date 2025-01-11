from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Update this line
    path('devices/<str:device_id>/', views.device_detail, name='device_detail'),
    path('devices/<str:device_id>/config/', views.update_device_configuration, name='update_device_configuration'),
    path('devices/<str:device_id>/monitoring_time/', views.update_device_monitoring_time, name='update_device_monitoring_time'),
    path('devices/<str:device_id>/publish/', views.publish_command, name='publish_command'),
    path('devices/<str:device_id>/logs/', views.view_device_logs, name='view_device_logs'),
    path('devices/<str:device_id>/get_logs/', views.get_logs, name='get_logs'),
    path('devices/<str:device_id>/clear_logs/', views.clear_logs, name='clear_logs'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='accounts_login'),
    

]

# path('devices/', views.device_list, name='device_list'),
# path('devices/add/', views.add_device, name='add_device'),
# path('devices/<str:device_id>/state/', views.update_device_state, name='update_device_state'),
