#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <MAX30105.h>
#include <spo2_algorithm.h>  // Add this for SpO₂ algorithm
#include <OneWire.h>
#include <DallasTemperature.h>

// I2C LCD setup
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Change to 0x3F if needed

// MAX30102 setup
MAX30105 particleSensor;

// DS18B20 setup
#define ONE_WIRE_BUS 4
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature ds18b20(&oneWire);

// Buffer for SpO₂ calculation
#if defined(__AVR_ATmega328P__) || defined(__AVR_ATmega168__)
uint16_t irBuffer[100]; // infrared LED sensor data
uint16_t redBuffer[100]; // red LED sensor data
#else
uint32_t irBuffer[100]; // infrared LED sensor data
uint32_t redBuffer[100]; // red LED sensor data
#endif

int32_t bufferLength; // data length
int32_t spo2; // SPO2 value
int8_t validSPO2; // indicator if SPO2 calculation is valid
int32_t heartRate; // heart rate value
int8_t validHeartRate; // indicator if heart rate calculation is valid

// Heart rate variables for fallback
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 0;
int beatAvg = 0;

// Timing variables
unsigned long lastDisplayUpdate = 0;
const unsigned long displayInterval = 1000; // Update display every 1 second
unsigned long lastSampleTime = 0;
int sampleCounter = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("Initializing...");
  
  // Initialize I2C
  Wire.begin(21, 22);
  
  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Initializing...");
  
  // Initialize MAX30102
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102 not found!");
    lcd.setCursor(0, 1);
    lcd.print("MAX30102 Error!");
    while (1);
  }
  
  // Configure MAX30102 for SpO₂ measurement [citation:5]
  byte ledBrightness = 60; // Options: 0=Off to 255=50mA
  byte sampleAverage = 4; // Options: 1, 2, 4, 8, 16, 32
  byte ledMode = 2; // Options: 1 = Red only, 2 = Red + IR
  int sampleRate = 100; // Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
  int pulseWidth = 411; // Options: 69, 118, 215, 411
  int adcRange = 4096; // Options: 2048, 4096, 8192, 16384
  
  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);
  
  // Initialize DS18B20
  ds18b20.begin();
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Place finger...");
  lcd.setCursor(0, 1);
  lcd.print("Hold steady");
  
  Serial.println("Setup complete!");
  delay(2000);
}

void loop() {
  // Read temperature
  ds18b20.requestTemperatures();
  float temperatureC = ds18b20.getTempCByIndex(0);
  
  // Check if finger is on sensor [citation:5]
  long irValue = particleSensor.getIR();
  
  if (irValue < 50000) {
    // No finger detected
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("No Finger");
    lcd.setCursor(0, 1);
    lcd.print("Place finger");
    delay(1000);
    return;
  }
  
  // Collect samples for SpO₂ calculation [citation:2][citation:5]
  bufferLength = 100; // 100 samples = ~4 seconds at 25 sps
  
  // Read first 100 samples
  for (byte i = 0; i < bufferLength; i++) {
    while (particleSensor.available() == false)
      particleSensor.check(); // Check for new data
      
    redBuffer[i] = particleSensor.getRed();
    irBuffer[i] = particleSensor.getIR();
    particleSensor.nextSample(); // Move to next sample
    
    // Optional: Print raw data for debugging
    // Serial.print("red="); Serial.print(redBuffer[i]);
    // Serial.print(", ir="); Serial.println(irBuffer[i]);
  }
  
  // Calculate heart rate and SpO₂ using Maxim's algorithm [citation:5][citation:8]
  maxim_heart_rate_and_oxygen_saturation(irBuffer, bufferLength, redBuffer, 
                                         &spo2, &validSPO2, 
                                         &heartRate, &validHeartRate);
  
  // Continue taking samples and recalculating every second
  while (true) {
    unsigned long startTime = millis();
    
    // Shift buffer: discard oldest 25 samples, keep last 75 [citation:5]
    for (byte i = 25; i < 100; i++) {
      redBuffer[i - 25] = redBuffer[i];
      irBuffer[i - 25] = irBuffer[i];
    }
    
    // Take 25 new samples
    for (byte i = 75; i < 100; i++) {
      while (particleSensor.available() == false)
        particleSensor.check();
        
      redBuffer[i] = particleSensor.getRed();
      irBuffer[i] = particleSensor.getIR();
      particleSensor.nextSample();
      
      // Small delay to maintain sampling rate
      delay(10);
    }
    
    // Recalculate with new samples
    maxim_heart_rate_and_oxygen_saturation(irBuffer, bufferLength, redBuffer, 
                                           &spo2, &validSPO2, 
                                           &heartRate, &validHeartRate);
    
    // Read temperature again
    ds18b20.requestTemperatures();
    temperatureC = ds18b20.getTempCByIndex(0);
    
    // Update display
    updateDisplay(heartRate, validHeartRate, spo2, validSPO2, temperatureC);
    
    // Ensure we're running at ~1 second per cycle
    unsigned long elapsed = millis() - startTime;
    if (elapsed < 1000) {
      delay(1000 - elapsed);
    }
  }
}

void updateDisplay(int32_t hr, int8_t hrValid, int32_t sPO2, int8_t sPO2Valid, float temp) {
  lcd.clear();
  lcd.setCursor(0, 0);
  // Display Heart Rate and SpO2 on first line
  if (hrValid && hr > 30 && hr < 200) {
    lcd.print("H:");
    lcd.print(hr);
    lcd.print("");
  } else {
    lcd.print("HR:-- ");
  }
  if (sPO2Valid && sPO2 > 70 && sPO2 < 100) {
    lcd.print("S:");
    lcd.print(sPO2);
    // lcd.print("%");
  } else {
    lcd.print("S:---");
  }

  // Second line: Temperature
  lcd.setCursor(0, 1);
  if (temp > 0 && temp < 50) {
    lcd.print("Temp:");
    lcd.print(temp, 1);
    lcd.print((char)223);
    lcd.print("C");
  } else {
    lcd.print("Temp:Error");
  }

  // Send structured data to Serial for web ingestion
  Serial.print("DATA,");
  Serial.print(hrValid && hr > 30 && hr < 200 ? hr : -1);
  Serial.print(",");
  Serial.print(sPO2Valid && sPO2 > 70 && sPO2 < 100 ? sPO2 : -1);
  Serial.print(",");
  Serial.print(temp > 0 && temp < 50 ? temp : -1);
  Serial.println();
  // Debug output to Serial Monitor
  Serial.print("HR: ");
  Serial.print(hr);
  Serial.print(" (valid: ");
  Serial.print(hrValid);
  Serial.print("), SpO2: ");
  Serial.print(sPO2);
  Serial.print(" (valid: ");
  Serial.print(sPO2Valid);
  Serial.print("), Temp: ");
  Serial.println(temp);
}