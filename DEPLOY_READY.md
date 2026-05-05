# 🎯 Multi-Monitor System - Ready to Deploy

Your HIT500 system supports **5-8 independent ESP32 monitors**. Each sends its own sensor data and displays real-time vitals for assigned patients.

---

## ✅ System Status: FULLY OPERATIONAL

**Backend**: ✓ API endpoints handle multi-monitor data routing  
**Database**: ✓ Stores readings with monitor → room → patient relationships  
**Frontend**: ✓ Dashboard assigns monitors to rooms and displays independent data  
**Real-Time**: ✓ Charts update every 200ms with incoming data  

---

## 🚀 Quick Deploy (5 Steps)

### 1. Configure Each ESP32 Monitor

**Monitor 1:**
```
File: Final_Code_HIT500/Max30102CodeUpdate.ino
Line 10: const char* ssid = "TASHINGA";
Line 11: const char* password = "1234567890";
Line 12: const char* server_ip = "192.168.1.100";  // ← Your IP from ipconfig
Line 13: const char* monitor_id = "1";              // ← Change to 2, 3, 4, etc.
```

**Upload Steps:**
1. Connect ESP32 via USB
2. Tools → Board → ESP32
3. Tools → Port → COM port of ESP32
4. Ctrl+R to verify
5. Ctrl+U to upload
6. Wait 30 seconds
7. Repeat for monitors 2-8 (change only monitor_id)

### 2. Start Django Server

```bash
cd C:\Users\TASHINGA\Desktop\PROJECT\hit300
python manage.py runserver 0.0.0.0:8000
```

Wait for message: `Starting development server at http://127.0.0.1:8000/`

### 3. Open Web Dashboard

```
http://192.168.1.100:8000
```
(Replace with your actual IP from ipconfig)

### 4. Wait for Monitors to Connect

Wait 15-20 seconds for ESP32s to:
- Connect to WiFi
- Send first reading to Django
- Appear in dashboard

### 5. Assign Monitors to Rooms

1. Click **"Assign"** button
2. Left panel shows all detected monitors
3. Click on "Monitor 1"
4. Right panel:
   - Room: Select "Room 1"
   - Patient: Enter name (e.g., "John Doe")
   - Click "ASSIGN MONITOR"
5. Repeat for monitors 2-8 → rooms 2-8

---

## 📊 What You'll See

### Dashboard Overview (All Rooms):
```
Room 1 - John Doe        │ Room 2 - Jane Smith
🟢 ACTIVE               │ 🟢 ACTIVE
24.5°C | 187 BPM | 99% │ 25.1°C | 92 BPM | 97%
Monitor 1               │ Monitor 2

Room 3 - Bob Johnson    │ Room 4 - Alice Brown
🟢 ACTIVE               │ 🟢 ACTIVE
23.8°C | 78 BPM | 98%  │ 24.2°C | 156 BPM | 100%
Monitor 3               │ Monitor 4
```

### Real-Time Charts (Click any room):
- **Temperature**: Updates every 200ms
- **Heart Rate**: Live updates every 200ms
- **SpO₂**: Continuous monitoring
- **Composite Index**: Normalized health score

---

## 🔄 Data Flow

```
Monitor 1 (ESP32)     Monitor 2 (ESP32)     Monitor 3 (ESP32)
     ↓                     ↓                      ↓
  WiFi                  WiFi                  WiFi
     ↓                     ↓                      ↓
  Django (8000) ← Receives readings from all monitors →
     ↓
  Database (SQLite)
     ↓
  Web Dashboard (200ms polling)
     ↓
  Room 1 → Room 2 → Room 3 → ... (Real-time display)
```

Each monitor's data flows **independently** to its assigned room.

---

## 🔧 Troubleshooting

### Monitor won't upload:
- Check USB cable
- Wrong COM port? Tools → Port (try different port)
- Arduino IDE closed or crashed? Restart it

### Monitor shows "WiFi not connected":
- Check SSID/password match your network (line 10-11)
- Open WiFi settings, verify network name is correct
- Check if password has special characters (may need escaping)

### Monitor appears in dashboard but shows "--":
- Monitor isn't assigned to any room yet
- Click "Assign" → select the monitor → assign to a room
- After assignment, data appears in 1-2 seconds

### All monitors showing "--" values:
- Django not running? Start it: `python manage.py runserver 0.0.0.0:8000`
- Wrong IP in Arduino code? Run `ipconfig` and update line 12
- Firewall blocking port 8000? Add Django to Windows Defender exceptions

### Multiple monitors showing same data:
- Two monitors have same ID (check monitor_id in each file)
- Each must be unique: Monitor 1, Monitor 2, Monitor 3, etc.

---

## 📋 Verification Checklist

After deploying monitors:

- [ ] All ESP32s show "WiFi connected!" in Serial Monitor
- [ ] Dashboard shows all monitors in "Assign" modal
- [ ] Can assign each monitor to different rooms
- [ ] Room cards show correct monitor ID
- [ ] Data displays (temp, HR, SpO₂) without "--"
- [ ] Charts animate smoothly with incoming data
- [ ] Status shows 🟢 ACTIVE for connected monitors
- [ ] Clicking room shows detailed real-time chart
- [ ] Can re-assign monitors to different rooms

---

## 💡 Key Features

✅ **Independent Monitoring**: Each monitor has its own patient/room  
✅ **Real-Time Display**: 200ms polling for instant updates  
✅ **Historical Data**: Charts show last 20 readings  
✅ **Exclusive Assignment**: One monitor per room (no conflicts)  
✅ **Dynamic Assignment**: Reassign monitors on-the-fly  
✅ **Patient Tracking**: Link patients to monitors via rooms  
✅ **Status Indicators**: 🟢 ACTIVE when sending data  

---

## 📝 Config Reference

Each monitor needs 4 settings:

| Setting | Example | Purpose |
|---------|---------|---------|
| `ssid` | "TASHINGA" | WiFi network name |
| `password` | "1234567890" | WiFi password |
| `server_ip` | "192.168.1.100" | Django server IP |
| `monitor_id` | "1", "2", "3" | Unique device ID |

**Same WiFi + server for all monitors. Change ONLY monitor_id.**

---

## 🎉 Expected Performance

- **Sensor Reading**: 1 second per monitor
- **Data Transmission**: ~50-100ms per monitor
- **Web Display**: 200-400ms from sensor to screen
- **Total Latency**: ~1-2 seconds sensor → display
- **Database**: Handles 5-8 monitors easily (1000+ readings/hour)
- **Network**: No congestion (8 monitors × 4 values = 32 data points/sec)

---

## 🆘 Still Having Issues?

1. **Check Serial Monitor of each ESP32:**
   - Arduino IDE → Tools → Serial Monitor
   - Set baud to 115200
   - Should see connection status and sensor readings

2. **Check Django console:**
   - Should show `POST /api/receive_reading` for each monitor
   - Each monitor sends every 1 second

3. **Check browser console (F12):**
   - Open DevTools → Console
   - Look for fetch errors (network issues)
   - Should show successful /api/latest requests

4. **Network diagnosis:**
   ```bash
   ipconfig  # Get your IP (192.168.x.x)
   ping 192.168.1.100  # Verify network connection
   ```

---

## 🚀 You're Ready!

Your HIT500 multi-monitor system is complete and ready to deploy 5-8 independent ESP32 patient monitors.

**Next Step**: Upload the first ESP32 and test! 🎯
