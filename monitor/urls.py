from django.urls import path
from . import views

urlpatterns = [
    path("process-data/", views.receive_process_data),
    path("latest/", views.latest_snapshot),
    path("frontend/", views.frontend),
]
