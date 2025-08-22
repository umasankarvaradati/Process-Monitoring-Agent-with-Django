from django.contrib import admin
from .models import ProcessSnapshot,Process

# Register your models here.
admin.site.register(ProcessSnapshot)
admin.site.register(Process)