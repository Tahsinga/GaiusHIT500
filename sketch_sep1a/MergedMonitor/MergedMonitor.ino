#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Temperature Sensor Setup (DS18B20)
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Heartbeat Sensor Setup
const uint8_t pulsePin = 3;    // D3 (hardware interrupt pin on Arduino UNO)
const uint8_t blinkPin = 13;   // LED blink on beat

volatile unsigned long lastBeatMicros = 0;
volatile unsigned long IBI = 0;      // ms between beats (rounded)
volatile bool newBeat = false;
const unsigned long minBeatIntervalMicros = 200000UL; // ignore intervals <200ms (300 BPM)

// LCD Setup (I2C address 0x27, 16x2 display)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Variables
float Celsius = 0;
float Fahrenheit = 0;
int currentBPM = 0;
unsigned long lastDisplayUpdate = 0;
const unsigned long displayUpdateInterval = 1000; // Update display every 1 second

void setup() {
  // Initialize Serial Communication
  Serial.begin(9600);
  
  // Initialize Temperature Sensor
  sensors.begin();
  
  // Initialize Heartbeat Sensor
  pinMode(pulsePin, INPUT);
  pinMode(blinkPin, OUTPUT);
  digitalWrite(blinkPin, LOW);
  attachInterrupt(digitalPinToInterrupt(pulsePin), onBeatRising, RISING);
  
  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Initializing...");
  delay(1000);
  lcd.clear();
  
  Serial.println("System Initialized");
}

void loop() {
  // Request temperature reading
  sensors.requestTemperatures();
  Celsius = sensors.getTempCByIndex(0);

  // DO NOT PRINT IF SENSOR IS DISCONNECTED
  if (Celsius != DEVICE_DISCONNECTED_C) {
    Fahrenheit = sensors.toFahrenheit(Celsius);
  }

  // Check if new beat detected
  if (newBeat) {
    noInterrupts();
    unsigned long ibi = IBI;
    newBeat = false;
    interrupts();

    if (ibi > 0) {
      currentBPM = (int)round(60000.0 / (double)ibi);
      
      // Print to Serial Monitor
      Serial.print("IBI (ms): ");
      Serial.print(ibi);
      Serial.print("  BPM: ");
      Serial.println(currentBPM);
    }
    
    // Blink LED on beat
    digitalWrite(blinkPin, HIGH);
    delay(50);
    digitalWrite(blinkPin, LOW);
  }

  // Update display every second
  unsigned long currentMillis = millis();
  if (currentMillis - lastDisplayUpdate >= displayUpdateInterval) {
    lastDisplayUpdate = currentMillis;
    
    // Display Temperature and Celsius on LCD (Line 1)
    lcd.setCursor(0, 0);
    if (Celsius != DEVICE_DISCONNECTED_C) {
      lcd.print("T:");
      lcd.print(Celsius, 1);
      lcd.print("C ");
      lcd.print(Fahrenheit, 1);
      lcd.print("F");
    } else {
      lcd.print("Sensor Error!   ");
    }
    
    // Display BPM on LCD (Line 2)
    lcd.setCursor(0, 1);
    lcd.print("BPM: ");
    if (currentBPM > 0) {
      lcd.print(currentBPM);
      lcd.print("     ");
    } else {
      lcd.print("--  ");
    }
    
    // Print to Serial Monitor
    Serial.print("Temperature: ");
    Serial.print(Celsius);
    Serial.print(" C  ");
    Serial.print(Fahrenheit);
    Serial.println(" F");
  }

  delay(20);
}

// Interrupt handler — triggered on rising edge of the pulse
void onBeatRising() {
  unsigned long now = micros();
  unsigned long interval = 0;
  if (lastBeatMicros != 0) {
    interval = (now - lastBeatMicros + 500) / 1000; // convert to ms (rounded)
  }
  // protect against spurious/very-fast pulses (debounce)
  if (interval >= (minBeatIntervalMicros / 1000) || lastBeatMicros == 0) {
    IBI = interval;
    newBeat = true;
  }
  lastBeatMicros = now;
}
