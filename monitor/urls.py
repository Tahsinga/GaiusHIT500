from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/latest', views.api_latest, name='api_latest'),
    path('api/history', views.api_history, name='api_history'),
    path('api/assign_monitor', views.api_assign_monitor, name='api_assign_monitor'),
    path('api/monitors', views.api_monitors, name='api_monitors'),
    path('api/rooms', views.api_rooms, name='api_rooms'),
    path('api/patients', views.api_patients, name='api_patients'),
    path('api/set_room_patient', views.api_set_room_patient, name='api_set_room_patient'),
]
