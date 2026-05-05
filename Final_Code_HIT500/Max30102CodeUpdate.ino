#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"
#include <OneWire.h>
#include <DallasTemperature.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============================================
// CONFIGURATION - UPDATE THESE SETTINGS
// ============================================
const char* ssid = "YOUR_WIFI_SSID";           // Replace with your WiFi network name
const char* password = "YOUR_WIFI_PASSWORD";   // Replace with your WiFi password
const char* server_ip = "192.168.1.100";       // Replace with Django server IP
const int server_port = 8000;                  // Replace with Django server port (8000 for dev, 80 for production)
const char* monitor_id = "1";                  // Unique identifier for this monitor device
// ============================================

MAX30105 particleSensor;

// MAX30102 variables
#define MAX_BRIGHTNESS 255
// DS18B20 pin
#define ONE_WIRE_BUS 4

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

uint32_t irBuffer[100];
uint32_t redBuffer[100];

int32_t bufferLength = 100;
int32_t spo2;
int8_t validSPO2;
int32_t heartRate;
int8_t validHeartRate;

// WiFi connection status
bool wifi_connected = false;

void setup()
{
  Serial.begin(115200);
  delay(1000); // Give serial time to initialize
  
  Serial.println("\n\nESP32 Multi Sensor Monitor with WiFi");
  Serial.println("=====================================");

  // Initialize temperature sensor
  Serial.println("Initializing DS18B20 Temperature Sensor...");
  sensors.begin();

  // Start I2C for MAX30102
  Serial.println("Initializing I2C...");
  Wire.begin(21, 22);

  // Start MAX30102
  Serial.println("Initializing MAX30102 Heart Rate/SpO2 Sensor...");
  if (!particleSensor.begin(Wire))
  {
    Serial.println("ERROR: MAX30102 not found. Check wiring!");
    while (1);
  }

  Serial.println("MAX30102 initialized successfully");

  particleSensor.setup(); 
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeIR(0x0A);

  // Initialize WiFi
  Serial.println("\nConnecting to WiFi...");
  connectToWiFi();
}

void connectToWiFi()
{
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20)
  {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  Serial.println("");
  if (WiFi.status() == WL_CONNECTED)
  {
    wifi_connected = true;
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  }
  else
  {
    wifi_connected = false;
    Serial.println("Failed to connect to WiFi. Data will be sent when WiFi is available.");
  }
}

void sendDataToServer(float tempC, float tempF, int32_t bpm, int32_t spo2)
{
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("WiFi not connected. Attempting to reconnect...");
    connectToWiFi();
    if (WiFi.status() != WL_CONNECTED)
    {
      Serial.println("Cannot send data - WiFi unavailable");
      return;
    }
  }

  HTTPClient http;

  // Construct the URL for the Django API endpoint
  String url = "http://";
  url += server_ip;
  url += ":";
  url += server_port;
  url += "/api/receive_reading";

  Serial.print("Connecting to: ");
  Serial.println(url);

  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["monitor_id"] = monitor_id;
  doc["temp_c"] = tempC;
  doc["temp_f"] = tempF;
  doc["bpm"] = bpm;
  doc["spo2"] = spo2;

  String json;
  serializeJson(doc, json);

  Serial.println("Sending JSON payload:");
  Serial.println(json);

  // Send POST request
  int httpResponseCode = http.POST(json);

  // Check response
  if (httpResponseCode > 0)
  {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    
    String response = http.getString();
    Serial.println("Response from server: ");
    Serial.println(response);
  }
  else
  {
    Serial.print("Error sending HTTP request: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}

void loop()
{
  // ============================
  // READ TEMPERATURE
  // ============================
  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);
  float tempF = tempC * 9.0 / 5.0 + 32.0; // Convert Celsius to Fahrenheit

  if (tempC == DEVICE_DISCONNECTED_C)
  {
    Serial.println("Error: Temperature sensor not detected!");
    tempC = 0;
    tempF = 0;
  }
  else
  {
    Serial.print("Temperature: ");
    Serial.print(tempC);
    Serial.print(" °C / ");
    Serial.print(tempF);
    Serial.println(" °F");
  }

  // ============================
  // MAX30102 READ - Heart Rate & SpO2
  // ============================
  for (byte i = 0; i < bufferLength; i++)
  {
    while (particleSensor.available() == false)
      particleSensor.check();

    redBuffer[i] = particleSensor.getRed();
    irBuffer[i] = particleSensor.getIR();
    particleSensor.nextSample();
  }

  // Calculate HR and SpO2
  maxim_heart_rate_and_oxygen_saturation(
    irBuffer,
    bufferLength,
    redBuffer,
    &spo2,
    &validSPO2,
    &heartRate,
    &validHeartRate
  );

  // ============================
  // DISPLAY AND SEND SENSOR DATA
  // ============================
  Serial.println("\n========== SENSOR DATA ==========");

  // Heart Rate
  int32_t hr_value = 0;
  if (validHeartRate)
  {
    Serial.print("Heart Rate: ");
    Serial.print(heartRate);
    Serial.println(" BPM");
    hr_value = heartRate;
  }
  else
  {
    Serial.println("Heart Rate: Invalid reading");
    hr_value = 0;
  }

  // SpO2
  int32_t spo2_value = 0;
  if (validSPO2)
  {
    Serial.print("SpO2: ");
    Serial.print(spo2);
    Serial.println(" %");
    spo2_value = spo2;
  }
  else
  {
    Serial.println("SpO2: Invalid reading");
    spo2_value = 0;
  }

  Serial.println("=================================\n");

  // Send data to Django server via HTTP POST
  sendDataToServer(tempC, tempF, hr_value, spo2_value);

  // Wait before next reading (1 second)
  delay(1000);
}