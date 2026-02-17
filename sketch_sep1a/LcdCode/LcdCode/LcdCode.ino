#include <LiquidCrystal_I2C_Hangul.h>
#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

//////////////////////////////////////////////////////////////////////////////////////////
float Celsius = 0;
float Fahrenheit = 0;

LiquidCrystal_I2C_Hangul lcd(0x20, 20, 4); // LCD 20x4

// Digital-pulse approach — measures time between rising edges on D3
const uint8_t pulsePin = 3;    // D3 (hardware interrupt pin on Arduino UNO)
const uint8_t blinkPin = 13;   // LED blink on beat

volatile unsigned long lastBeatMicros = 0;
volatile unsigned long IBI = 0;      // ms between beats (rounded)
volatile bool newBeat = false;

const unsigned long minBeatIntervalMicros = 200000UL; // ignore intervals <200ms (300 BPM) - protects from noise
/////////////////////////////////////////////////////////////////////////////////

void setup() {
  sensors.begin();
  Serial.begin(9600);
  
  lcd.init();
  lcd.backlight();

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Temp Monitor");

  /////////////////////////////////////////////////////////////////////////////////////
  pinMode(pulsePin, INPUT); // sensor output
  pinMode(blinkPin, OUTPUT);
  digitalWrite(blinkPin, LOW);
  // attach interrupt on rising edge
  attachInterrupt(digitalPinToInterrupt(pulsePin), onBeatRising, RISING);
  /////////////////////////////////////////////////////////////////////////////////////

}

void loop() {
  int bpm;

  sensors.requestTemperatures();
  Celsius = sensors.getTempCByIndex(0);

  if (Celsius == DEVICE_DISCONNECTED_C) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sensor Error!");
    return;
  }

  Fahrenheit = sensors.toFahrenheit(Celsius);

  // ----- LCD OUTPUT -----
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("Celsius: ");
  lcd.print(Celsius);
  lcd.print(" C");

  lcd.setCursor(0, 1);
  lcd.print("Fahrenheit: ");
  lcd.print(Fahrenheit);
  lcd.print(" F");

  // ----- SERIAL OUTPUT -----
  Serial.print(Celsius);
  Serial.print(" C  ");
  Serial.print(Fahrenheit);
  Serial.println(" F");

  ////////////////////////////////////////////////////////////////////////////////////
  // If ISR flagged a new beat, compute BPM and print
  if (newBeat) {
    noInterrupts();
    unsigned long ibi = IBI; // copy volatile
    newBeat = false;
    interrupts();

    if (ibi > 0) {
      bpm = (int)round(60000.0 / (double)ibi);
      Serial.print("IBI (ms): ");
      Serial.print(ibi);
      Serial.print("  BPM: ");
      Serial.println(bpm);
    } else {
      Serial.println("No valid IBI yet");
    }
  }
  lcd.setCursor(0, 2);
  lcd.print("IBI: ");
  lcd.print(bpm);
  /////////////////////////////////////////////////////////////////////////////////////

  delay(1000); // update every second
}

// Interrupt — triggered on rising edge of the pulse
void onBeatRising() {

  unsigned long now = micros();
  unsigned long interval = 0;
  if (lastBeatMicros != 0) {
    interval = (now - lastBeatMicros + 500) / 1000; // convert to ms (rounded)
  }
  // protect against spurious/very-fast pulses (debounce)
  if (interval >= (minBeatIntervalMicros / 1000) || lastBeatMicros == 0) {
    IBI = interval;          // store IBI in ms (0 for the very first detection)
    newBeat = true;
    // blink LED briefly (non-blocking-ish)
    digitalWrite(blinkPin, HIGH);
    // schedule LED off after small delay using a timerless method: we'll turn off below quickly
  }
  lastBeatMicros = now;
  // quick LED off: turn off after a tiny pause using a short delay is allowed inside ISR? NO — avoid delay in ISR.
  // Instead, we'll turn it off from loop() soon after. Use millis flag alternative if you want longer blink.
  
}
