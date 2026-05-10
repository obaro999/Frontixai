from django.contrib import admin
from .models import Appointment, BusinessConfig

admin.site.register(Appointment)
admin.site.register(BusinessConfig)