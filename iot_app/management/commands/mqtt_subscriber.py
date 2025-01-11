import threading
import os
import django
import logging
import paho.mqtt.client as mqtt, paho.mqtt.publish as publish
from django.core.management.base import BaseCommand
from iot_app.models import Device, DeviceLog
import time

# Set up Django settings for the subscriber service
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iot_project.settings")
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("mqtt_subscriber.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def on_message(client, userdata, message):
    logger.info(f"Message received on topic {message.topic}")
    try:
        topic_parts = message.topic.split('/')
        if len(topic_parts) < 3 or topic_parts[0] != 'devices':
            logger.warning(f"Invalid topic format: {message.topic}")
            return
        
        if topic_parts[2] == 'connect':
            # Change device state to 'connected' when a connection message is received
            device_id = topic_parts[1]
            logger.debug(f"Device ID: {device_id}")
            device = Device.objects.filter(device_id=device_id).first()
            if device:
                time.sleep(2)
                device.update_last_seen()
                monitor_time = device.monitoring_time
                mqtt_topic = f"devices/{device.device_id}/response"
                payload = str(monitor_time)
                mqtt_broker = "127.0.0.1"
                publish.single(mqtt_topic, payload, hostname=mqtt_broker)
                device.state = 'connected'
                device.save()
                logger.info(f"Device connected: {device.device_id}")
            else:
                logger.error(f"No device found for device_id: {device_id}, skipping message")

        if topic_parts[2] == 'logs':
            device_id = topic_parts[1]
            message_payload = message.payload.decode()  # Rename 'message' to avoid conflict with MQTT 'message'
            logger.debug(f"Device ID: {device_id}, Message: {message_payload}")
            device = Device.objects.filter(device_id=device_id).first()
            
            if device:
                DeviceLog.objects.create(
                    device=device,
                    message=message_payload
                )
                device.update_last_seen()
                device.save()
                logger.info(f"Log saved for device {device.device_id}")
            else:
                logger.error(f"No device found for device_id: {device_id}, skipping message")
        
    except Exception as e:
        logger.exception(f"Error processing message: {e}")

# Función para verificar dispositivos inactivos
def check_device_timeout():
    timeout_multiplier = 2  # Tiempo máximo permitido = monitoring_time * 2
    check_interval = 2  # Intervalo en segundos para ejecutar la verificación

    while True:
        try:
            logger.info("Checking for inactive devices...")
            devices = Device.objects.all()

            for device in devices:
                if device.last_seen:
                    elapsed_time = now() - device.last_seen
                    allowed_time = timedelta(milliseconds=device.monitoring_time * timeout_multiplier)

                    if elapsed_time > allowed_time and device.state != 'not connected':
                        device.state = 'not connected'
                        device.save()
                        logger.info(f"Device {device.device_id} marked as not connected")
        except Exception as e:
            logger.exception(f"Error during device timeout check: {e}")

        time.sleep(check_interval)

def start_mqtt_subscriber():
    try:
        logger.info("Starting MQTT subscriber and timeout checker")
        
        # Iniciar el hilo para verificar dispositivos inactivos
        timeout_thread = threading.Thread(target=check_device_timeout, daemon=True)
        timeout_thread.start()

        # Configurar e iniciar el cliente MQTT
        client = mqtt.Client()
        client.connect("127.0.0.1", 1883)
        client.subscribe("devices/+/logs")
        client.subscribe("devices/+/connect")
        client.subscribe("devices/+/state")
        client.on_message = on_message
        client.loop_forever()

    except Exception as e:
        logger.critical(f"Subscriber crashed: {e}", exc_info=True)


class Command(BaseCommand):
    help = "Start the MQTT subscriber to listen for device messages"

    def handle(self, *args, **options):
        logger.info("Running MQTT subscriber as a Django management command")
        start_mqtt_subscriber()

