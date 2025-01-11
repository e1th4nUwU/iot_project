from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from paho.mqtt import publish
from .models import Device, DeviceLog
from .forms import DeviceForm



@login_required
def device_detail(request, device_id):
    """
    Display device details
    
    :param request: HTTP request
    :param device_id: Device ID
    """
    device = get_object_or_404(Device, device_id=device_id)
    
    if request.user != device.user:
        return redirect('dashboard')
    
    return render(request, 'device_detail.html', {'device': device})



@login_required
def update_device_state(request, device_id):
    """
    Update device state
    
    :param request: HTTP request
    :param device_id: Device ID
    """
    device = get_object_or_404(Device, device_id=device_id)
    if request.method == 'POST':
        
        if request.user != device.user:
            return redirect('dashboard')
        
        new_state = request.POST.get('state')
        device.state = new_state
        device.save()
        return redirect('device_detail', device_id=device.device_id)
    return render(request, 'update_device_state.html', {'device': device})


def update_device_configuration(request, device_id):
    """
    Update device configuration
    
    :param request: HTTP request
    :param device_id: Device ID
    """
    device = get_object_or_404(Device, device_id=device_id)
    if request.method == 'POST':
        
        if request.user != device.user:
            return redirect('dashboard')
        
        monitoring_time = request.POST.get('monitoring_time')
        mqtt_topic = f"devices/{device.device_id}/response"
        payload =  monitoring_time
        mqtt_broker = "127.0.0.1"  # Replace with your broker address
        publish.single(mqtt_topic, str(payload), hostname=mqtt_broker)
        device.monitoring_time = int(monitoring_time)
        device.save()
        return redirect('device_detail', device_id=device.device_id)
    return render(request, 'update_device_configuration.html', {'device': device})



def update_device_monitoring_time(request, device_id):
    """
    Updates device monitoring time
    
    :param request: HTTP request
    :param device_id: Device ID
    """
    device = get_object_or_404(Device, device_id=device_id)
    if request.method == 'POST':
        
        if request.user != device.user:
            return redirect('dashboard')
        
        new_monitoring_time = request.POST.get('monitoring_time')
        mqtt_topic = f"devices/{device.device_id}/response"
        device.monitoring_time = new_monitoring_time
        publish.single(mqtt_topic, new_monitoring_time, hostname="127.0.0.1")
        device.save()
        
        return redirect('device_detail', device_id=device.device_id)
    return render(request, 'update_device_monitoring_time.html', {'device': device})


def publish_command(request, device_id):
    """
    Publish command to the device
    
    :param request: HTTP request
    :param device_id: Device ID
    """
    device = get_object_or_404(Device, device_id=device_id)
    if request.method == 'POST':
        
        if request.user != device.user:
            return redirect('dashboard')
        
        command = request.POST.get('command')
        mqtt_topic = f"devices/{device.device_id}/commands"
        mqtt_broker = "127.0.0.1"
        publish.single(mqtt_topic, command, hostname=mqtt_broker)
        return redirect('device_detail', device_id=device.device_id)
    return render(request, 'publish_command.html', {'device': device})


def view_device_logs(request, device_id):
    """
    Mostrar los detalles del dispositivo
    
    :param request: HTTP request
    :param device_id: ID del dispositivo
    """
    device = get_object_or_404(Device, device_id=device_id)
    if request.user != device.user:
        return redirect('dashboard')
    # Traemos los logs más recientes del dispositivo
    logs = DeviceLog.objects.filter(device=device).order_by('-timestamp')[:10]  # Traer solo los 10 últimos logs
    return render(request, 'device_logs.html', {'device': device, 'logs': logs})



def get_logs(request, device_id):
    """
    Ver los logs de un dispositivo.
    """
    device = get_object_or_404(Device, device_id=device_id)
    if request.user != device.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    logs = DeviceLog.objects.filter(device=device).order_by('-timestamp')
    
    log_data = [{
        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'message': log.message
    } for log in logs]

    # Retornar los logs como JSON
    return JsonResponse({'logs': log_data})


@login_required
def clear_logs(request, device_id):
    """
    Eliminar los logs de un dispositivo.

    :param request: HTTP request
    :param device_id: ID del dispositivo
    """
    device = get_object_or_404(Device, device_id=device_id)
    if request.user != device.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Eliminar todos los logs asociados con el dispositivo
    DeviceLog.objects.filter(device=device).delete()

    # Retornar una respuesta de éxito
    return JsonResponse({'status': 'success'})



@login_required
def dashboard(request):
    """
    Display the dashboard
    
    :param request: HTTP request
    """
    # Replace with actual MQTT integration for real-time status
    #
    devices = Device.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'devices': devices})
