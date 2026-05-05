# 🚀 IMMEDIATE ACTION CHECKLIST

## ⚠️ CRITICAL - Fix Compilation Error First

### Arduino File Conflict
**Problem**: Compilation error: `redefinition of 'const char* ssid'`  
**Reason**: Both `Final_Code_HIT500.ino` and `Max30102CodeUpdate.ino` are being compiled

**SOLUTION** - Delete the old file:
- [ ] Open File Explorer
- [ ] Navigate to: `C:\Users\TASHINGA\Desktop\PROJECT\hit300\Final_Code_HIT500\`
- [ ] Delete: `Final_Code_HIT500.ino`  
- [ ] Keep: `Max30102CodeUpdate.ino` (this is the one with WiFi)
- [ ] Close and reopen Arduino IDE

**OR Alternative** - If you want to keep backup:
- [ ] Rename `Final_Code_HIT500.ino` to `Final_Code_HIT500.ino.bak`
- [ ] Arduino won't try to compile `.bak` files

✓ After either step, compilation error should be gone!

---

## 🔧 Configure Arduino Code

### Edit Max30102CodeUpdate.ino

Find these lines (around line 13-17):
```cpp
const char* ssid = "YOUR_WIFI_SSID";           
const char* password = "YOUR_WIFI_PASSWORD";   
const char* server_ip = "192.168.1.100";       
const int server_port = 8000;                  
const char* monitor_id = "1";                  
```

**Update with YOUR values:**
- [ ] `ssid` = Your WiFi network name (e.g., "TASHINGA")
- [ ] `password` = Your WiFi password
- [ ] `server_ip` = Your Django server IP (from IPCONFIG)
- [ ] `server_port` = 8000 (or your Django port)
- [ ] `monitor_id` = "1" (or "2", "3" for multiple monitors)

**Example after update:**
```cpp
const char* ssid = "TASHINGA";
const char* password = "1234567890";
const char* server_ip = "192.168.1.100";
const int server_port = 8000;
const char* monitor_id = "1";
```

---

## 📤 Upload Arduino Code

- [ ] Select Board: **Tools → Board → ESP32 Dev Module**
- [ ] Select Port: **Tools → Port → COM3** (or your COM port)
- [ ] Install Library: **Sketch → Include Library → Manage Libraries**
  - [ ] Search: "ArduinoJson"
  - [ ] Install (by Benoit Blanchon, v6.x or higher)
- [ ] Click Upload (Ctrl+U)
- [ ] Wait for "Leaving... Hard resetting via RTS pin"

---

## ✅ Verify Arduino Connection

- [ ] Open Serial Monitor: **Tools → Serial Monitor** (Ctrl+Shift+M)
- [ ] Set Baud Rate: **115200** (bottom right)
- [ ] You should see:

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

- [ ] If you see **"WiFi connected!"** → ✓ Arduino ready!
- [ ] If you see **"Failed to connect to WiFi"** → Check SSID/password

---

## 🌐 Verify Django Server

- [ ] Open Command Prompt
- [ ] Navigate to: `C:\Users\TASHINGA\Desktop\PROJECT\hit300`
- [ ] Run: `python manage.py runserver 0.0.0.0:8000`
- [ ] You should see: `Starting development server at http://127.0.0.1:8000/`
- [ ] Keep this window open (don't close it)

---

## 🌍 Test in Browser

- [ ] Open browser: `http://192.168.1.100:8000/` (use your server IP)
- [ ] You should see HIT500 dashboard with 8 rooms
- [ ] All rooms should show: "⚪ STANDBY" status
- [ ] Click "Assign" button in top right

---

## 📡 Assign Your First Monitor

- [ ] Click **"Assign"** button
- [ ] Left panel should show **"Monitor 1"** with readings
- [ ] Click it to select (or use dropdown)
- [ ] Room dropdown: Select **"Room 1"**
- [ ] Patient Name: Enter any name (e.g., "Test Patient")
- [ ] Click **"ASSIGN MONITOR"**
- [ ] Wait for ✓ Success message
- [ ] Modal closes automatically

---

## 📊 View Live Data

- [ ] Go back to room overview
- [ ] Room 1 should now show:
  - [ ] ✓ Your patient name
  - [ ] ✓ "Monitor 1" indicator at bottom
  - [ ] ✓ Real-time temperatures, BPM, SpO₂
  - [ ] ✓ 🟢 **ACTIVE** status (if Arduino is sending data)
- [ ] Click **Room 1 card** to see detailed graphs
- [ ] Charts should update every 2 seconds with live data

---

## 🎉 Success Indicators

When everything works, you should see:

✓ Arduino connects to WiFi  
✓ Arduino sends data to Django  
✓ Django displays rooms with live data  
✓ Room cards show assigned monitor ID  
✓ Charts update in real-time when you click a room  
✓ Sidebar shows current vitals  
✓ You can assign/reassign monitors instantly  

---

## 📞 Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| **Compilation error** | Delete `Final_Code_HIT500.ino` |
| **WiFi won't connect** | Check SSID/password spelling in code (case-sensitive) |
| **Can't reach server** | Verify Django IP in code and run Django server |
| **No data appearing** | Assign monitor to room first, wait 2 seconds |
| **Port already in use** | Change port: `python manage.py runserver 0.0.0.0:8001` |

---

## 📚 Full Documentation

- **ARDUINO_WIFI_SETUP.md** - Detailed Arduino setup
- **MONITOR_ASSIGNMENT_GUIDE.md** - Dashboard guide  
- **SYSTEM_WORKFLOW_GUIDE.md** - Complete system overview
- **CHANGES.md** - Summary of what was updated
- **IMPORTANT_FILE_CONFLICT.md** - Arduino file organization

---

## ⏱️ Estimated Time

- Fix compilation: **2 minutes**
- Configure Arduino: **3 minutes**
- Upload code: **2 minutes**
- Test connection: **2 minutes**
- Assign monitor: **1 minute**

**Total: ~10 minutes to get everything working!**

---

## 🎯 Current Status

✅ Arduino code updated with WiFi  
✅ Django backend ready (no changes needed)  
✅ Web dashboard enhanced for monitor assignment  
✅ Documentation complete  
⏳ Waiting for you to: Delete old Arduino file → Configure → Test

**Everything is ready! Next step: Delete Final_Code_HIT500.ino** 👉

---

Last Updated: 2026-05-04  
System: HIT500 · Sentinel Core
