from django.contrib import admin
from .models import Visit


@admin.register(Visit)
class YourModelAdmin(admin.ModelAdmin):
    pass
