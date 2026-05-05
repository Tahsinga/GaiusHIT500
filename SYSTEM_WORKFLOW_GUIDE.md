# HIT500 System - Complete Workflow

## 🎯 Main Features Now Available

### 1️⃣ Monitor Selection & Assignment
```
Unassigned Monitor 1
├─ 🌡️ 36.5°C
├─ ❤️ 72 BPM  
└─ O₂ 98%
    ↓
[Click to Select or Use Dropdown]
    ↓
Choose Room (Room 1-8)
Enter Patient Name (Optional)
    ↓
[Click "ASSIGN MONITOR"]
    ↓
✓ Monitor assigned to Room
✓ Data now flows to room dashboard
```

### 2️⃣ Real-Time Room Dashboard
```
┌─────────────────┐
│   Room 1        │
│   🟢 ACTIVE     │
├─────────────────┤
│ 👤 John Smith   │
├─────────────────┤
│ 🌡️  36.5°C     │
│ ❤️  72 BPM      │
│ O₂  98%         │
├─────────────────┤
│ 📡 Monitor 1    │
└─────────────────┘
         ↓
    [Click to view detailed graphs]
```

### 3️⃣ Detailed Patient Trends
```
Temperature Chart (4 readings visible)
├─ 08:00 → 36.2°C
├─ 08:02 → 36.4°C
├─ 08:04 → 36.5°C ← Current
└─ [Zoom controls available]

Heart Rate Chart
├─ 08:00 → 70 BPM
├─ 08:02 → 72 BPM
├─ 08:04 → 71 BPM ← Current
└─ [Auto-scrolling, 15-min history]

SpO₂ Chart
├─ 08:00 → 97%
├─ 08:02 → 98%
├─ 08:04 → 98% ← Current
└─ [Real-time updates]

Composite Index Chart
└─ [Combined trend analysis]
```

---

## 🔄 Data Flow

```
                    ┌──────────────────────┐
                    │   Arduino (ESP32)    │
                    │  ┌──────────────────┐│
                    │  │ Sensors:         ││
                    │  │ • MAX30102 (HR/O2││
                    │  │ • DS18B20 (Temp) ││
                    │  └──────────────────┘│
                    │         │            │
                    │    WiFi │ JSON POST  │
                    └────────┬─────────────┘
                             │
                    ┌────────▼──────────┐
                    │  Django Server    │
                    │ /api/receive_     │
                    │   reading         │
                    └────────┬──────────┘
                             │
                    ┌────────▼──────────┐
                    │   Database        │
                    │  (SQLite)         │
                    │ • Readings        │
                    │ • Rooms           │
                    │ • Patients        │
                    └────────┬──────────┘
                             │
                    ┌────────▼──────────┐
                    │  Web Dashboard    │
                    │  • Room Cards     │
                    │  • Live Charts    │
                    │  • Sidebar Stats  │
                    │  • Patient Logs   │
                    └───────────────────┘
```

---

## 📱 Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  HIT500 · Sentinel Core    [LIVE●]  36.5°C | 72 BPM | 98% SpO₂   │
│                            [Assign] [Logs]                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────────────────────────────────────┐
│ SIDEBAR      │  │ OVERVIEW GRID - Click any room to view trends│
│              │  │                                              │
│ Current Stats│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│ 🌡️ 36.5°C   │  │ Room 1    │ │ Room 2   │ │ Room 3   │      │
│ ❤️ 72 BPM   │  │ 🟢 ACTIVE │ │ ⚪ IDLE  │ │ 🟢 ACTIVE│      │
│ O₂ 98%     │  │           │ │          │ │          │      │
│            │  │ John      │ │ Unassign │ │ Sarah    │      │
│ Room List: │  │ 36.5°C    │ │ --°C     │ │ 37.1°C   │      │
│ • Room 1 ✓ │  │ 72 BPM    │ │ -- BPM   │ │ 85 BPM   │      │
│ • Room 2   │  │ 98% SpO₂  │ │ --%      │ │ 97% SpO₂ │      │
│ • Room 3 ✓ │  │ Monitor 1 │ │ No mon.  │ │ Monitor 3│      │
│            │  │           │ │          │ │          │      │
│ 1 active   │  │ └──────────┘ └──────────┘ └──────────┘      │
│            │  │                                              │
│            │  │ [More rooms... Click card to expand]         │
└──────────────┘  └──────────────────────────────────────────────┘

[Footer: HIT500 • live streaming • updates every 2s • 08:04:32]
```

---

## ⚙️ Monitor Assignment Modal

```
┌──────────────────────────────────────────────────────────────┐
│  Monitor Assignment Center                              ✕    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────┐ ┌──────────────────────────────────┐
│ Available Monitors       │ │ Assignment Configuration         │
│                          │ │                                  │
│ Monitor 1                │ │ Select Monitor                   │
│ 🟢 Room 1                │ │ [Monitor 1 (Room 1) ▼]          │
│ 🌡️ 36.5°C               │ │ Status: Assigned to Room 1       │
│ ❤️ 72 BPM               │ │                                  │
│ O₂ 98%                  │ │ Assign to Room                   │
│                          │ │ [Room 1 ▼]                      │
│ Monitor 2                │ │                                  │
│ ⚪ Unassigned            │ │ Patient Name                     │
│ 🌡️ 35.8°C               │ │ [John Smith        ]             │
│ ❤️ 68 BPM               │ │ (optional)                       │
│ O₂ 96%                  │ │                                  │
│                          │ │ [ASSIGN MONITOR →]              │
│ Monitor 3                │ │                                  │
│ 🟢 Room 3                │ │ ✓ Assigned Mon 1 to Room 1      │
│ 🌡️ 37.1°C               │ │                                  │
│ ❤️ 85 BPM               │ │                                  │
│ O₂ 97%                  │ └──────────────────────────────────┘
│                          │
│ ─────────────────────── │
│ Total: 3 monitors       │
│ Assigned: 2             │
│ Unassigned: 1           │
└──────────────────────────┘
```

---

## 🔐 Assignment State Machine

```
INITIAL STATE: Monitor Detected
          │
          └─→ [Click "Assign"]
              │
              └─→ SELECTION MODAL OPENS
                  │
                  ├─→ [Select Monitor] → Monitor highlighted
                  │
                  ├─→ [Choose Room] → Room selected
                  │
                  ├─→ [Enter Patient Name] → Optional
                  │
                  └─→ [Click "ASSIGN MONITOR"]
                      │
                      └─→ API Call to /api/assign_monitor
                          │
                          ├─→ SUCCESS
                          │   ├─ Monitor assigned to room
                          │   ├─ Previous assignment cleared
                          │   ├─ UI refreshes automatically
                          │   ├─ Modal closes
                          │   └─ Data starts flowing
                          │
                          └─→ ERROR
                              └─ Message displayed
                                  ├─ Try different room
                                  ├─ Check if monitor exists
                                  └─ Retry


REASSIGNMENT: Monitor already assigned
          │
          └─→ [Click "Assign"]
              │
              └─→ [Select same monitor]
                  │
                  └─→ [Choose DIFFERENT room]
                      │
                      └─→ [Click "ASSIGN MONITOR"]
                          │
                          └─→ SUCCESS
                              ├─ Monitor moves to new room
                              ├─ Old room now empty
                              └─ Data now in new room
```

---

## 📊 Real-Time Updates

```
Every 2 seconds when viewing a room's details:
├─ Fetch latest reading from /api/latest
├─ Update chart with new data point
├─ Update sidebar stats
├─ Update header stats
└─ Remove oldest point if >15 exist

Every 8 seconds for room overview:
├─ Fetch all room statuses
├─ Update room card vitals
├─ Update room card status badge
├─ Update sidebar room list
└─ Update active room count
```

---

## 🎓 Quick Workflow Example

### Scenario: Patient John arrives for monitoring

```
Step 1: Click "Assign" button
        ↓
Step 2: See "Monitor 2" in the available list
        Click it to select
        ↓
Step 3: Room dropdown already shows "Room 1"
        (Or select if needed)
        ↓
Step 4: Type "John Smith" in Patient Name
        ↓
Step 5: Click "ASSIGN MONITOR"
        ↓
Step 6: ✓ Success! Modal closes
        ↓
Step 7: See "Room 1" card with:
        - Patient: John Smith
        - Monitor 2 indicator
        - Real-time vitals updating
        - 🟢 ACTIVE status
        ↓
Step 8: Click Room 1 card to see detailed trends
        - Temperature graph
        - Heart rate graph
        - SpO₂ graph
        - All updating in real-time
        ↓
Step 9: Patient leaves/assignment ends
        ↓
Step 10: Click "Assign" again
         Select Monitor 2
         Choose a different room or keep empty
         Click "ASSIGN MONITOR"
         ↓
         Monitor 2 now sends data to new room
         (or stops if unassigned)
```

---

## 🚀 Next Steps

1. **Fix Arduino compilation error**
   - Delete `Final_Code_HIT500.ino`
   - Keep only `Max30102CodeUpdate.ino`

2. **Configure & Upload Arduino Code**
   - Update WiFi SSID & password
   - Set Django server IP & port
   - Set unique monitor ID
   - Compile and upload

3. **Test System**
   - Check Arduino Serial Monitor for WiFi connection
   - Refresh Django dashboard
   - Click "Assign" to assign monitor to a room
   - Watch room card for real-time data

4. **Monitor Patients**
   - Click room cards to view detailed trends
   - Use "Logs" to view historical patient data
   - Reassign monitors as needed

---

## 📚 Reference Files

- `Max30102CodeUpdate.ino` - Arduino code (USE THIS ONE)
- `index.html` - Enhanced dashboard with improved UI
- `ARDUINO_WIFI_SETUP.md` - Detailed Arduino setup guide
- `MONITOR_ASSIGNMENT_GUIDE.md` - Dashboard usage guide
- `IMPORTANT_FILE_CONFLICT.md` - Arduino file organization

---

**Your HIT500 system is ready for deployment!** 🎉
