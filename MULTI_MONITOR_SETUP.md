# 🔄 Multi-Monitor Setup Guide (5-8 ESP32 Devices)

## Overview

Your HIT500 system supports **multiple independent monitors** (ESP32 devices). Each:
- Has a unique identifier (1-8)
- Sends its own sensor data (temp, HR, SpO₂)
- Can be assigned to ONE room
- Displays independently on the dashboard

---

## ⚡ Quick Setup

### Step 1: Configure Each ESP32 Monitor

For **Monitor 1** (existing):
```cpp
const char* ssid = "TASHINGA";
const char* password = "1234567890";
const char* server_ip = "192.168.1.100";        // Your Django server IP
const char* monitor_id = "1";                   // CHANGE THIS FOR EACH DEVICE
```

For **Monitor 2**:
```cpp
const char* monitor_id = "2";
```

For **Monitor 3**:
```cpp
const char* monitor_id = "3";
```

**Continue for monitors 4-8, changing ONLY the `monitor_id` value each time.**

---

## 🔧 How to Change Monitor ID

### In Arduino IDE:

1. Open `Max30102CodeUpdate.ino`
2. Locate line with: `const char* monitor_id = "1";`
3. Change `"1"` to your desired ID: `"2"`, `"3"`, etc.
4. Click **Verify** (Ctrl+R) to check for errors
5. Click **Upload** (Ctrl+U) to send to ESP32
6. **Wait 30 seconds** for upload to complete
7. Check **Serial Monitor** (Tools → Serial Monitor, 115200 baud)
8. Should see: `ESP32 Multi Sensor Monitor - Monitor [ID]`

---

## 📋 Multi-Monitor Checklist

- [ ] Monitor 1 uploaded (ID="1")
- [ ] Monitor 2 uploaded (ID="2")
- [ ] Monitor 3 uploaded (ID="3")
- [ ] Monitor 4 uploaded (ID="4")
- [ ] Monitor 5 uploaded (ID="5")
- [ ] Monitor 6 uploaded (ID="6") - *optional*
- [ ] Monitor 7 uploaded (ID="7") - *optional*
- [ ] Monitor 8 uploaded (ID="8") - *optional*

---

## 🌐 Django Server Setup

Start Django server (ONE TIME):
```bash
python manage.py runserver 0.0.0.0:8000
```

This binds to **all network interfaces**, so all 5-8 ESP32s can reach it.

---

## 💻 Web Dashboard: Assigning Monitors

### In Browser (http://192.168.x.x:8000):

1. **Wait 10 seconds** for all monitors to connect
2. Click **"Assign"** button (top right)
3. In left panel, you'll see all monitors that connected:
   - Monitor 1 ✓ (if sending data)
   - Monitor 2 ✓ (if sending data)
   - Monitor 3 ✓ (if sending data)
   - etc.

### To Assign a Monitor to a Room:

1. **Left panel**: Click on "Monitor 1" (it highlights)
2. **Right panel**:
   - Select "Room 1" from dropdown
   - Enter patient name (e.g., "John Doe")
   - Click "ASSIGN MONITOR"

3. **Result**: Room 1 now shows data from Monitor 1

### Repeat for each room/monitor pair:
- Monitor 1 → Room 1 (Patient A)
- Monitor 2 → Room 2 (Patient B)
- Monitor 3 → Room 3 (Patient C)
- Monitor 4 → Room 4 (Patient D)
- Monitor 5 → Room 5 (Patient E)

---

## 🔍 Monitor Status on Dashboard

### Room Cards Show:

```
┌─────────────────────┐
│   Room 1            │
│   🟢 ACTIVE         │  ← Shows when Monitor 1 is sending data
├─────────────────────┤
│   John Doe          │  ← Patient name
├─────────────────────┤
│ 📊 24.5°C          │  ← Temperature from Monitor 1 only
│ ❤️ 187 BPM         │  ← Heart rate from Monitor 1 only
│ 💨 99% SpO₂        │  ← SpO₂ from Monitor 1 only
├─────────────────────┤
│ 🖥️ Monitor 1       │  ← Shows which monitor
└─────────────────────┘
```

---

## 📈 Real-Time Data Flow

```
Monitor 1 (ESP32)  → WiFi → Django API → Web Dashboard
  (sends every 1s)         (stores)      (updates every 200ms)

Monitor 2 (ESP32)  → WiFi → Django API → Web Dashboard
  (sends every 1s)         (stores)      (updates every 200ms)

Monitor 3 (ESP32)  → WiFi → Django API → Web Dashboard
  (sends every 1s)         (stores)      (updates every 200ms)

... (repeat for monitors 4-8)
```

**Each monitor's data displays INDEPENDENTLY in its assigned room.**

---

## 🔴 Troubleshooting Multi-Monitors

### Monitor isn't appearing in "Assign" modal:

1. **Check Serial Monitor** of that ESP32
2. Should see:
   ```
   Connecting to WiFi...
   WiFi connected!
   IP address: 192.168.x.x
   ```

3. If NOT connected:
   - Check WiFi SSID and password in code (line 10-11)
   - Re-upload

4. If connected but not showing in modal:
   - Wait 20 seconds (may need to send first reading)
   - Refresh web browser
   - Monitor must send valid JSON data first

### Monitor sends data but shows "--" on dashboard:

1. Check if monitor is **assigned to a room**
2. Look for this on room card: `🖥️ Monitor X`
3. If it says "No monitor assigned", click "Assign"
4. If error appears, see **Monitor ID Conflicts** below

### Multiple monitors assigned to SAME room:

✗ This is NOT allowed - system allows only **1 monitor per room**

When assigning Monitor 3 to Room 1:
- Monitor 1 automatically unassigns from Room 1
- Monitor 3 becomes the exclusive monitor for Room 1
- All data from Monitor 1 for Room 1 stops showing

### Monitor ID Conflicts:

Each monitor must have a UNIQUE identifier (1-8).

✗ **Don't do this:**
```
Monitor 1: monitor_id = "1"
Monitor 2: monitor_id = "1"   ← DUPLICATE! Both send as "1"
```

✓ **Do this:**
```
Monitor 1: monitor_id = "1"
Monitor 2: monitor_id = "2"   ← Unique
Monitor 3: monitor_id = "3"   ← Unique
```

---

## 📊 Viewing Data for Each Monitor

### Dashboard Overview:
- Shows all 8 rooms with assigned monitors
- Each room card displays data from ITS assigned monitor ONLY
- Status shows 🟢 ACTIVE when that specific monitor is sending

### Detailed View (Click Room Card):
- Charts show 10 recent readings from that monitor
- Charts update every 200ms with new readings
- Sidebar shows latest vitals from that monitor

### Logs Modal:
- Click "Logs" to see all historical readings
- Filter by patient to see their specific monitor's data

---

## 🎯 Example: 5 Monitors / 5 Rooms Setup

| Monitor | Room | Patient | Status |
|---------|------|---------|--------|
| 1 | Room 1 | John Doe | 🟢 ACTIVE |
| 2 | Room 2 | Jane Smith | 🟢 ACTIVE |
| 3 | Room 3 | Bob Johnson | 🟢 ACTIVE |
| 4 | Room 4 | Alice Brown | 🟢 ACTIVE |
| 5 | Room 5 | Charlie Wilson | 🟢 ACTIVE |
| unassigned | - | - | ⚪ STANDBY |
| unassigned | - | - | ⚪ STANDBY |
| unassigned | - | - | ⚪ STANDBY |

Each monitor sends independent sensor readings continuously.

---

## ✅ Validation Checklist

After setting up all monitors:

- [ ] All ESP32s show "WiFi connected!" in Serial Monitor
- [ ] Django server shows POST requests from all monitors
- [ ] Web dashboard shows all monitors in "Assign" modal
- [ ] Can assign each monitor to different rooms
- [ ] Each room card shows correct monitor ID
- [ ] Charts update smoothly with each monitor's data
- [ ] Status shows 🟢 ACTIVE for monitors sending data
- [ ] Status shows ⚪ STANDBY for idle monitors

---

## 🚀 Performance Notes

- **Total data per second**: 5-8 monitors × 4 values = 20-32 data points/sec
- **Web update interval**: 200ms (5 updates/sec per monitor)
- **Django database**: Can handle 1000+ readings/hour easily
- **Network**: No congestion - each 1KB packet every 1 second per monitor

---

## 📝 Advanced: Custom Monitor Configurations

Need different sampling rates? Edit the Arduino code:

```cpp
// FAST mode (every 500ms) - for high-acuity monitoring
delay(500);

// STANDARD mode (every 1s) - default (current)
delay(1000);

// SLOW mode (every 2s) - to save bandwidth
delay(2000);
```

Each monitor can have a DIFFERENT delay!

---

## 🆘 Emergency: Reset Everything

If monitors get confused:

1. Power off all ESP32s
2. Clear Django database (WARNING):
   ```bash
   python manage.py shell
   >>> from monitor.models import *
   >>> Monitor.objects.all().delete()
   >>> Reading.objects.all().delete()
   >>> exit()
   ```
3. Restart Django
4. Power on ESP32s one at a time
5. Re-assign monitors to rooms

---

## 📞 Support

Monitor won't connect? Follow these steps:
1. Check SSID/password in Arduino code
2. Check server_ip matches Django machine IP (run `ipconfig`)
3. Check firewall allows port 8000
4. Verify Django server is running
5. Reset ESP32 (power cycle)

**Each monitor can be debugged independently via its Serial Monitor!**
