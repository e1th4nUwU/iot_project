#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h> // Biblioteca para el sensor DHT

// Definir tus credenciales Wi-Fi y broker MQTT
const char *ssid = "";
const char *password = """;
const char *mqtt_server = "";
int response_time = 1000; // Tiempo de respuesta del servidor

WiFiClient espClient;
PubSubClient client(espClient);

String device_id = "dht11"; // Cambiar por el ID de tu dispositivo
String response_topic = "devices/" + device_id + "/response";
String publish_topic = "devices/" + device_id + "/logs";
String connect_topic = "devices/" + device_id + "/connect";

// Definición del sensor DHT
#define DHTPIN 13         // Pin donde está conectado el sensor
#define DHTTYPE DHT11     // Tipo de sensor (DHT11 o DHT22)
DHT dht(DHTPIN, DHTTYPE); // Inicializamos el sensor DHT

// Conectar a la red Wi-Fi
void setup_wifi()
{
    delay(10);
    // Conectar a Wi-Fi
    Serial.print("Conectando a Wi-Fi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("¡Conectado!");
}

// Función de callback cuando se recibe un mensaje MQTT
void callback(char *topic, byte *payload, unsigned int length)
{
    String message = "";
    for (int i = 0; i < length; i++)
    {
        message += (char)payload[i];
    }

    if (String(topic) == "devices/" + device_id + "/response")
    {
        // Recibir el tiempo de respuesta del servidor
        Serial.print("Tiempo de respuesta del servidor: ");
        Serial.println(message.toInt());
        response_time = message.toInt() * 1000;
    }
}

// Conectar al servidor MQTT
void reconnect()
{
    // Loop hasta que estemos conectados
    while (!client.connected())
    {
        Serial.print("Intentando conectar al MQTT...");
        if (client.connect(device_id.c_str()))
        {
            Serial.println("Conectado al servidor MQTT");

            // Convertir el tópico de respuesta a const char* antes de suscribirse
            client.subscribe(response_topic.c_str()); // Usar c_str() aquí

            // Enviar un mensaje de conexión al servidor
            client.publish(connect_topic.c_str(), "connected");
        }
        else
        {
            Serial.print("Falló la conexión, reintentando...");
            delay(5000);
        }
    }
}

void setup()
{
    Serial.begin(115200);
    setup_wifi();
    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);

    // Inicializar el sensor DHT
    dht.begin();
}

void loop()
{
    if (!client.connected())
    {
        reconnect();
    }

    client.loop();

    // Medir las lecturas del sensor
    float h = dht.readHumidity();    // Humedad
    float t = dht.readTemperature(); // Temperatura en grados Celsius

    // Verificar si las lecturas son válidas
    if (isnan(h) || isnan(t))
    {
        Serial.println("Error al leer del sensor DHT!");
        return;
    }

    // Publicar las lecturas al servidor
    String payload = "Humedad: " + String(h) + "%, Temperatura: " + String(t) + "°C";
    Serial.println(payload);
    client.publish(publish_topic.c_str(), payload.c_str());

    // Esperar antes de la siguiente lectura
    delay(response_time);
}
