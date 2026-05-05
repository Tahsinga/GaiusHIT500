# Monitor Assignment & Data Display Guide

## Overview
Your HIT500 monitoring system now has an enhanced interface for assigning Arduino monitors to rooms, viewing real-time data, and managing patient information.

---

## Quick Start: Assigning Your First Monitor

### Step 1: Click "Assign" Button
- Located in the top-right header
- Opens the Monitor Assignment Center modal

### Step 2: Select Your Monitor
**Two ways to select:**

**Method A - From the Monitor List (Left Panel)**
- See all available monitors with their current status
- Shows real-time readings if available
- Click any monitor to auto-select it in the dropdown
- Shows which room it's currently assigned to (if any)

**Method B - From the Dropdown (Right Panel)**
- Uses the "Select Monitor" dropdown
- Shows Monitor ID and current temperature reading
- Shows current assignment status (Assigned to Room X or Unassigned)

### Step 3: Choose a Room
- Use the "Assign to Room" dropdown
- Select from Room 1-8

### Step 4: Enter Patient Name (Optional)
- Enter the patient name in "Patient Name" field
- Leave blank to keep existing patient assignment
- Can be changed later without reassigning the monitor

### Step 5: Click "ASSIGN MONITOR"
- System will assign the monitor to the room
- Previous assignments will be cleared automatically
- Success message appears when complete

---

## Using the Dashboard

### Overview Grid
- Shows all 8 rooms in a grid layout
- Each card displays:
  - Room name and status (🟢 Active or ⚪ Standby)
  - Patient name
  - Current vitals: Temperature (°C), Heart Rate (BPM), SpO₂ (%)
  - **Which monitor is assigned** (Monitor ID shown at bottom)

### Sidebar
- Quick reference of current readings
- List of all rooms with patient names
- Shows which rooms are actively receiving data
- Click any room to view detailed trends

### Detailed View (Charts)
- Click any room card to see detailed graphs
- Shows 4 charts: Temperature, Heart Rate, SpO₂, and Composite Index
- Real-time updates every 2 seconds when data is being received
- **Zoom & Pan Controls**:
  - Mouse wheel to zoom in/out
  - Click and drag to pan
  - Use zoom/reset buttons on each chart

---

## Interpreting Monitor Status

### Monitor List Shows:
- **Monitor ID**: Unique identifier (1, 2, 3, etc.)
- **Status Badge**: 
  - ✓ Green = Currently assigned to a room
  - ⊘ Yellow = Unassigned (not in any room yet)
- **Latest Readings**: Temperature, Heart Rate, SpO₂ (if available)
- **"No data yet"**: Monitor detected but hasn't sent readings yet

### Room Card Shows:
- **Status Badge** (top right):
  - 🟢 **ACTIVE**: Receiving data within the last 12 seconds
  - ⚪ **STANDBY**: No recent data (idle state)
- **Patient Name**: Who is being monitored
- **Monitor Info** (bottom):
  - Shows "Monitor X" if assigned
  - Shows "No monitor assigned" if room has no monitor

---

## Common Tasks

### Reassign a Monitor to a Different Room
1. Click "Assign" button
2. Select the monitor from the list (left panel)
3. Choose a different room
4. Click "ASSIGN MONITOR"
5. Previous room assignment will be cleared

### Change Patient Name for a Room
1. Click "Assign" button
2. Select any monitor (or the currently assigned one)
3. Choose the room
4. Enter new patient name
5. Click "ASSIGN MONITOR"
*Note: You don't need to change the monitor to change the patient*

### View Detailed Patient Data
1. Click any room card
2. Detailed charts appear for that room
3. Charts show up to 15 minutes of history
4. Data updates every 2 seconds in real-time
5. Click "Back to rooms" to return to overview

### View All Patient Logs
1. Click "Logs" button in header
2. Select a patient from the list
3. View:
   - All readings for that patient (table or chart)
   - Which rooms the patient has been monitored in
   - Latest vital readings
4. Search by patient name using search box

---

## Data Display Features

### Real-Time Updates
- All rooms update every 2-8 seconds
- No page refresh needed
- Status updates automatically when monitors connect/disconnect

### Historical Data
- Last 10 readings available per room
- Charts show up to 15-minute history
- Click into a room to see detailed trends
- Patient logs show all-time readings

### Status Indicators
- **LIVE (green pulse dot)**: Room receiving active data
- **STANDBY (red indicator)**: Room idle (no recent data)
- **Patient Name**: Shows "unassigned" if no patient selected

---

## Troubleshooting

### Monitor Shows in List But No Data
- **Check Arduino**: 
  - Is it powered on?
  - Is WiFi connected? (Check Serial Monitor)
  - Can it reach your Django server IP?
- **Check Django**: 
  - Is it running? (`python manage.py runserver 0.0.0.0:8000`)
  - Is the API endpoint working? (Visit `/api/receive_reading`)

### Monitor Not Appearing in List
- Monitor sends first reading → appears in system
- Check Arduino serial monitor for WiFi errors
- Verify Django server is accessible at the configured IP

### Data Not Showing on Room Cards
1. Assign the monitor to a room first
2. Wait for next reading (up to 2 seconds)
3. Check if monitor is online (green badge should appear)
4. Click room card to see if any historical data exists

### Room Shows "No monitor assigned"
- No monitor is currently assigned to that room
- Click "Assign" button to assign one
- Multiple rooms can have monitors assigned independently

---

## Keyboard Shortcuts

- **Ctrl+Shift+M**: Open Arduino Serial Monitor (if in IDE)
- **Enter** in search: Search for patients
- **Escape** in modal: Close assignment modal

---

## Tips & Best Practices

✓ **Assign monitors** to rooms before expecting data
✓ **Use patient names** for better record tracking  
✓ **Check sidebar** for quick current status overview
✓ **Click charts** to see zoomed-in detailed trends
✓ **Refresh logs** if data seems stale
✓ **Use search** to find specific patient records quickly

---

## Technical Details

### Polling Intervals
- Silent updates: Every 8 seconds (no UI flicker)
- Live detail view: Every 2 seconds (when viewing a room)
- Signal timeout: 12 seconds (marks room as standby if no data)

### Data Stored
- Current room assignments in database
- Patient information and names
- All historical readings with timestamps
- Monitor-to-room mappings

### API Endpoints Used
- `/api/monitors` - List all monitors
- `/api/assign_monitor` - Assign monitor to room
- `/api/latest` - Get latest reading for a room
- `/api/history` - Get historical readings
- `/api/patients_list` - Get all patient records
- `/api/patient_logs` - Get data for a specific patient

---

## What Happens When You Assign a Monitor?

1. **Arduino begins sending data** to `/api/receive_reading` endpoint
2. **System receives JSON payload**: `{monitor_id, temp_c, temp_f, bpm, spo2}`
3. **Data saved to database** associated with the assigned room
4. **Room card updates** with latest vital signs
5. **Charts populate** when you click to view details
6. **Historical data** becomes available for patient logs
7. **Room status changes** from Standby to Active

---

## Next Steps

1. **Configure Arduino**: Update WiFi credentials and server IP in code
2. **Flash Arduino**: Upload the updated code to your ESP32
3. **Test WiFi**: Check Serial Monitor for connection confirmation
4. **Assign First Monitor**: Use the Assign button to assign to a room
5. **Verify Data**: Watch room cards for real-time updates
6. **Monitor Patients**: Click room cards to view detailed trends

---

For detailed Arduino WiFi setup, see: **ARDUINO_WIFI_SETUP.md**
