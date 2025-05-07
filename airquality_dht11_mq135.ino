#include <WiFi.h>
#include <PubSubClient.h>
#include <MQUnifiedsensor.h>
#include "DHT.h"
//#include "Adafruit_PM25AQI.h"

// ---------- WiFi Credentials ----------
const char* ssid = "HOME-1E66-2.4";
const char* password = "almost4528coast";

// ---------- MQTT Broker ----------
const char* mqtt_server = "test.mosquitto.org"; // Replace with your PC's IP
const int mqtt_port = 1883;
const char* mqtt_topic = "airquality/data";

// ---------- WiFi & MQTT ----------
WiFiClient espClient;
PubSubClient client(espClient);

// ---------- MQ135 Setup ----------
#define Board "ESP32"
#define Voltage_Resolution 3.3
#define ADC_Bit_Resolution 12
#define MQ135_PIN 34  // Analog input pin connected to MQ-135 Aout

// ---------- DHT11 Setup ----------
#define DHTPIN 4          // Choose a digital pin for DHT11 (adjust if needed)
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

MQUnifiedsensor MQ135(Board, Voltage_Resolution, ADC_Bit_Resolution, MQ135_PIN, "MQ-135");

// ---------- PMS5003 Setup ----------
//Adafruit_PM25AQI aqi;
//#define PMS_TX 17  // Connect PMS5003 RX to ESP32 TX (17)
//#define PMS_RX 16  // Connect PMS5003 TX to ESP32 RX (16)

// ---------- Setup ----------
void setup() {
  Serial.begin(115200);

  // Initialize WiFi
  WiFi.begin(ssid, password);
  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");

  // Initialize MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setKeepAlive(60);  // Important for stable connection

  // Setup MQ135
  MQ135.init();
  MQ135.setRegressionMethod(1);  // Exponential
  MQ135.setA(110.47); MQ135.setB(-2.862); // CO2 Equation
  MQ135.setRL(10);       // Load resistance value in kOhms
  MQ135.setR0(10);       // Initial calibration resistance

  // Setup DHT11
  dht.begin();

  // Setup PMS5003
  /*Serial2.begin(9600, SERIAL_8N1, PMS_RX, PMS_TX);
  if (!aqi.begin_UART(&Serial2)) {
    Serial.println("Could not find PMS5003 sensor! Check wiring.");
    while (1) delay(10);
  }*/
}

// ---------- Main Loop ----------
void loop() {
  ensureWiFi();
  
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();  // Important: keep MQTT alive

  // ----- Read MQ-135 Sensor -----
  MQ135.update();
  float co2_ppm = MQ135.readSensor();
  Serial.print("CO2 (ppm): ");
  Serial.println(co2_ppm);
  
  // ----- Read DHT11 Sensor -----
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // ----- Read PMS5003 Sensor -----
 // PM25_AQI_Data data;
 // bool pms_ok = aqi.read(&data);

  // ----- Construct JSON Payload -----
  String payload = "{";
  payload += "\"co2_ppm\":" + String(co2_ppm, 2);
  payload += ",\"temperature\":" + String(temperature, 2);
  payload += ",\"humidity\":" + String(humidity, 2);
  /*if (pms_ok) {
    payload += ",\"pm1_0\":" + String(data.pm10_standard);
    payload += ",\"pm2_5\":" + String(data.pm25_standard);
    payload += ",\"pm10\":" + String(data.pm100_standard);
  }*/
  payload += ",\"location\":\"indoor\"";
  payload += "}";

  // ----- Publish to MQTT Broker -----
  Serial.println("Publishing payload: " + payload);
  client.publish(mqtt_topic, payload.c_str());

  delay(5000); // Send every 5 seconds
}

// ---------- WiFi Reconnect ----------
void ensureWiFi() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    WiFi.disconnect();
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println("\nWiFi reconnected.");
  }
}

// ---------- MQTT Reconnect ----------
void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-" + String(random(0xffff), HEX);

    if (client.connect(clientId.c_str(), "status/esp32", 0, true, "offline")) {
      Serial.println("connected!");
      client.publish("status/esp32", "online", true);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(". Trying again in 5 seconds...");
      delay(5000);
    }
  }
}
