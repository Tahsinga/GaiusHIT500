# Arduino WiFi Setup Guide - HIT500 Monitor

## Overview
Your ESP32 Arduino code has been updated to send sensor data (temperature, heart rate, SpO2) directly to your Django website via WiFi instead of serial communication.

---

## Step 1: Install Required Libraries in Arduino IDE

You need to install the following libraries. In Arduino IDE:
1. Go to **Sketch** → **Include Library** → **Manage Libraries**
2. Search for and install each library:

- **ArduinoJson** (by Benoit Blanchon) - Version 6.x or higher
  - Used for creating JSON payloads

- **ESP32** (if not already installed)
  - Core library for ESP32 board

These are the ONLY new libraries needed:
- `Wire.h` - Already included with ESP32
- `WiFi.h` - Already included with ESP32
- `HTTPClient.h` - Already included with ESP32

---

## Step 2: Configure Arduino Code Settings

Open the updated file: `Max30102CodeUpdate.ino`

At the top of the file, you'll see configuration settings. **Update these with your settings:**

```cpp
const char* ssid = "YOUR_WIFI_SSID";           // Your WiFi network name
const char* password = "YOUR_WIFI_PASSWORD";   // Your WiFi password
const char* server_ip = "192.168.1.100";       // Django server IP
const int server_port = 8000;                  // Django server port
const char* monitor_id = "1";                  // Unique monitor ID (e.g., "1", "2", "3")
```

### Finding Your Django Server IP Address

**If running on the same machine (development):**
- Find your computer's IP address:
  - **Windows**: Open Command Prompt, type `ipconfig`, look for "IPv4 Address" (usually 192.168.x.x)
  - The port is typically `8000` (default Django development server)

**If Django is running on a different machine:**
- Find the machine's IP address using `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
- Ensure both the Arduino and Django server are on the same network

**Example configurations:**
```cpp
// Development on localhost
const char* server_ip = "192.168.1.100";
const int server_port = 8000;

// Production server
const char* server_ip = "192.168.1.50";
const int server_port = 80;

// Or use hostname if available
const char* server_ip = "django-server.local";
```

---

## Step 3: Flash the Arduino

1. Select your ESP32 board: **Tools** → **Board** → **ESP32 Dev Module** (or your specific model)
2. Select the correct COM port: **Tools** → **Port**
3. Click **Upload** (or Ctrl+U)
4. Open the Serial Monitor (Ctrl+Shift+M) to see connection logs

---

## Step 4: Expected Serial Output

When the Arduino starts and connects successfully, you should see:

```
ESP32 Multi Sensor Monitor with WiFi
=====================================
Initializing DS18B20 Temperature Sensor...
Initializing I2C...
Initializing MAX30102 Heart Rate/SpO2 Sensor...
MAX30102 initialized successfully

Connecting to WiFi...
.....
WiFi connected!
IP address: 192.168.1.xxx

Connecting to: http://192.168.1.100:8000/api/receive_reading
Sending JSON payload:
{"monitor_id":"1","temp_c":36.5,"temp_f":97.7,"bpm":72,"spo2":98}
HTTP Response code: 200
Response from server: {"status":"saved","reading_id":5,"monitor_id":"1","room":"Room 1"}
```

---

## Step 5: Troubleshooting

### Arduino Won't Connect to WiFi
- **Check SSID and password**: Verify your WiFi network name and password are correct (case-sensitive)
- **WiFi compatibility**: Some WiFi networks require specific settings. Try 2.4GHz band (5GHz may not work)
- **Signal strength**: Move Arduino closer to WiFi router

**Serial output if connection fails:**
```
Connecting to YOUR_WIFI_SSID
.......................
Failed to connect to WiFi. Data will be sent when WiFi is available.
```

### Arduino Won't Find Server
- **Check IP address**: Verify the `server_ip` matches your Django server's actual IP
- **Check port**: Ensure Django is running on the specified port
- **Network connectivity**: Ping the server from another device to confirm it's reachable
- **Firewall**: Check if Windows Firewall is blocking Django on port 8000

**Serial output if server connection fails:**
```
Error sending HTTP request: -1
```

### Data Not Appearing in Django
- Check the Django console for error messages
- Ensure the monitor has been assigned to a room via the web interface:
  1. Go to `http://your-server-ip:8000/`
  2. Find the Arduino monitor in the list
  3. Assign it to a room
- Check the database: `python manage.py shell` and query the Reading model

---

## Step 6: Data Format

Your Arduino sends this JSON data to the Django endpoint `/api/receive_reading`:

```json
{
  "monitor_id": "1",
  "temp_c": 36.5,
  "temp_f": 97.7,
  "bpm": 72,
  "spo2": 98
}
```

- **monitor_id**: Unique identifier for this Arduino device
- **temp_c**: Temperature in Celsius
- **temp_f**: Temperature in Fahrenheit  
- **bpm**: Heart rate (beats per minute)
- **spo2**: Blood oxygen saturation (%)

Django automatically:
1. Creates a Reading record in the database
2. Associates it with the assigned room
3. Stores it with a timestamp
4. Returns success to the Arduino

---

## Step 7: Multiple Monitors

If you have multiple ESP32 monitors:

1. **Change monitor_id for each**: Edit the `monitor_id` constant for each Arduino
   ```cpp
   const char* monitor_id = "1";  // First monitor
   const char* monitor_id = "2";  // Second monitor
   const char* monitor_id = "3";  // Third monitor
   ```

2. **Assign each to a room** via the web interface at `http://your-server-ip:8000/`

3. Each monitor will send data independently to the same Django server

---

## Step 8: Running Django Server

Make sure your Django server is running and accessible:

```bash
# In the project directory
python manage.py runserver 0.0.0.0:8000
```

The `0.0.0.0` makes it accessible from other machines on the network.

---

## Additional Notes

- **Baud Rate**: Serial monitor set to 115200 baud
- **Sampling Rate**: Data sent every 2 seconds
- **Network Requirements**: Arduino and Django server must be on the same network
- **Production**: For production, consider adding authentication and using HTTPS

---

## Quick Checklist

- [ ] ArduinoJson library installed
- [ ] WiFi SSID and password updated in code
- [ ] Server IP address verified
- [ ] Server port matches Django server (default 8000)
- [ ] Monitor ID set uniquely for each device
- [ ] Arduino flashed successfully
- [ ] Serial monitor shows successful WiFi connection
- [ ] Django server running and accessible
- [ ] Monitor assigned to a room in web interface
- [ ] Data appearing in Django dashboard

---

**Questions?** Check the Serial Monitor output for specific error messages and refer to the troubleshooting section above.
