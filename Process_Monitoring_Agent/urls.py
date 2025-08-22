from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/', include('monitor.urls')),
    # Frontend
    path('', TemplateView.as_view(template_name="index.html"), name='home'),
]

