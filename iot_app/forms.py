from django import forms
from .models import Device

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_id', 'monitoring_time', 'state']
        widgets = {
            'state': forms.Select(choices=[('ON', 'ON'), ('OFF', 'OFF')]),
        }
