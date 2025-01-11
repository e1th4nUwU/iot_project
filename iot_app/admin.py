from django.contrib import admin
from .models import Device, DeviceLog

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'monitoring_time', 'state')
    search_fields = ("device_id", "user__username")

@admin.register(DeviceLog)
class DeviceLogAdmin(admin.ModelAdmin):
    list_display = ("device", "message", "timestamp")
