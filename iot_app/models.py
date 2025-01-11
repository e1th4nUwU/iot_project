from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Device(models.Model):
    device_id = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    monitoring_time = models.IntegerField()
    state = models.CharField(max_length=10)
    last_seen = models.DateTimeField(null=True, blank=True)  # Última vez conectado

    def update_last_seen(self):
        self.last_seen = now()
        self.save()

    def __str__(self):
        return self.device_id

class DeviceLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return f"Log for {self.device.device_id} at {self.timestamp}"
