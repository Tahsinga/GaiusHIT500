#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"
#include <OneWire.h>
#include <DallasTemperature.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <LiquidCrystal_I2C.h>   // ✅ LCD

// ============================================
// CONFIGURATION
// ============================================
const char* ssid = "Wifi_123";
const char* password = "1234567890";
const char* server_ip = "172.16.13.252";
const int server_port = 8000;
const char* monitor_id = "1";

// ============================================

// ✅ LCD (0x27, 16 columns, 2 rows)
LiquidCrystal_I2C lcd(0x27, 16, 2);

MAX30105 particleSensor;

// DS18B20
#define ONE_WIRE_BUS 4
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// BUZZER
#define BUZZER_PIN 5

// MAX30102 buffers
uint32_t irBuffer[100];
uint32_t redBuffer[100];

int32_t bufferLength = 100;
int32_t spo2;
int8_t validSPO2;
int32_t heartRate;
int8_t validHeartRate;

bool wifi_connected = false;

// ================= SETUP =================
void setup()
{
  Serial.begin(115200);
  delay(1000);

  Serial.println("\nESP32 Multi Sensor Monitor");

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  sensors.begin();
  Wire.begin(21, 22);

  // ✅ LCD INIT
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Initializing...");
  
  if (!particleSensor.begin(Wire))
  {
    Serial.println("ERROR: MAX30102 not found!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("MAX30102 ERROR");
    while (1);
  }

  particleSensor.setup(); 
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeIR(0x0A);

  connectToWiFi();

  lcd.clear();
}

// ================= WIFI =================
void connectToWiFi()
{
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int attempts = 0;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");

  while (WiFi.status() != WL_CONNECTED && attempts < 20)
  {
    delay(500);
    Serial.print(".");
    lcd.setCursor(attempts % 16, 1);
    lcd.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println("\nWiFi connected");
    Serial.println(WiFi.localIP());
    wifi_connected = true;

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Connected");
    delay(1000);
  }
  else
  {
    Serial.println("\nWiFi failed");
    wifi_connected = false;

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Failed");
    delay(1000);
  }
}

// ================= SEND =================
void sendDataToServer(float tempC, float tempF, int32_t bpm, int32_t spo2)
{
  if (WiFi.status() != WL_CONNECTED)
  {
    connectToWiFi();
    if (WiFi.status() != WL_CONNECTED) return;
  }

  HTTPClient http;

  String url = "http://" + String(server_ip) + ":" + String(server_port) + "/api/receive_reading";

  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> doc;
  doc["monitor_id"] = monitor_id;
  doc["temp_c"] = tempC;
  doc["temp_f"] = tempF;
  doc["bpm"] = bpm;
  doc["spo2"] = spo2;

  String json;
  serializeJson(doc, json);

  int code = http.POST(json);

  Serial.print("HTTP Code: ");
  Serial.println(code);

  http.end();
}

// ================= LOOP =================
void loop()
{
  // ===== TEMPERATURE =====
  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);
  float tempF = tempC * 9.0 / 5.0 + 32.0;

  if (tempC == DEVICE_DISCONNECTED_C)
  {
    Serial.println("Temp sensor error");
    tempC = 0;
    tempF = 0;
  }

  // ===== MAX30102 =====
  for (byte i = 0; i < bufferLength; i++)
  {
    while (!particleSensor.available())
      particleSensor.check();

    redBuffer[i] = particleSensor.getRed();
    irBuffer[i] = particleSensor.getIR();
    particleSensor.nextSample();
  }

  maxim_heart_rate_and_oxygen_saturation(
    irBuffer,
    bufferLength,
    redBuffer,
    &spo2,
    &validSPO2,
    &heartRate,
    &validHeartRate
  );

  int32_t hr_value = (validHeartRate) ? heartRate : 0;
  int32_t spo2_value = (validSPO2) ? spo2 : 0;

  // ===== SERIAL =====
  Serial.println("\n========== SENSOR DATA ==========");
  Serial.print("Temp: "); Serial.print(tempC); Serial.println(" °C");
  Serial.print("Heart Rate: "); Serial.println(hr_value);
  Serial.print("SpO2: "); Serial.println(spo2_value);
  Serial.println("=================================\n");

  // ===== LCD DISPLAY =====
  lcd.clear();

  // Row 1
  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(tempC, 1);
  lcd.print("C ");

  lcd.print("H:");
  lcd.print(hr_value);

  // Row 2
  lcd.setCursor(0, 1);
  lcd.print("SpO2:");
  lcd.print(spo2_value);
  lcd.print("%");

  // ===== BUZZER =====
  bool alarm = false;

  if (hr_value > 0 && spo2_value > 0)
  {
    if (spo2_value < 90) alarm = true;
    if (hr_value < 50 || hr_value > 120) alarm = true;
  }

  digitalWrite(BUZZER_PIN, alarm ? HIGH : LOW);

  // ===== SEND =====
  sendDataToServer(tempC, tempF, hr_value, spo2_value);

  delay(2000);
}