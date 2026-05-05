# 🔧 Arduino Connection Diagnostic Guide

## Step 1: Find Your Actual Server IP Address

### Windows Command Prompt:
```bash
ipconfig
```

Look for output like:
```
Ethernet adapter Ethernet:
   Connection-specific DNS Suffix: 
   Link-local IPv6 Address: ...
   IPv4 Address: 192.168.1.100          ← THIS IS YOUR IP
   Subnet Mask: 255.255.255.0
```

**Copy the IPv4 Address** (e.g., 192.168.1.100)

---

## Step 2: Update Arduino Code with CORRECT IP

In `Max30102CodeUpdate.ino`, find line 15:

```cpp
const char* server_ip = "192.168.1.100";  // CHANGE THIS
```

Replace with YOUR actual IPv4 address from Step 1:
```cpp
const char* server_ip = "192.168.X.X";  // Replace with your IP
```

**IMPORTANT**: Must be the same network (192.168.x.x or 10.0.x.x range)

---

## Step 3: Verify Django is Running

Open a **NEW PowerShell window** and run:

```bash
cd C:\Users\TASHINGA\Desktop\PROJECT\hit300
python manage.py runserver 0.0.0.0:8000
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

**KEEP THIS WINDOW OPEN** while testing Arduino

---

## Step 4: Test Connection from Arduino

### Method A: Check Serial Monitor
After uploading code, open Serial Monitor (115200 baud):

Should show:
```
Connecting to: http://192.168.1.100:8000/api/receive_reading
Sending JSON payload:
{"monitor_id":"1","temp_c":36.5,...}
HTTP Response code: 200    ← SUCCESS!
```

If you see:
```
Error sending HTTP request: -1    ← CONNECTION FAILED
```

---

## Step 5: Common Fixes

### Fix 1: Wrong IP Address
- [ ] Check IPCONFIG again
- [ ] Update Arduino code
- [ ] Recompile and upload
- [ ] Check Serial Monitor

### Fix 2: Django Not Running
- [ ] Open PowerShell
- [ ] Run: `python manage.py runserver 0.0.0.0:8000`
- [ ] Keep window open
- [ ] Re-upload Arduino code

### Fix 3: Firewall Blocking Port 8000
- [ ] Search: "Windows Defender Firewall"
- [ ] Click "Allow an app through firewall"
- [ ] Find "Python"
- [ ] Check both Private and Public
- [ ] Click OK

### Fix 4: Different WiFi Networks
- [ ] Check if Arduino and PC on same WiFi
- [ ] If not, configure Arduino to your network
- [ ] Update SSID and password in code

---

## Step 6: Verify Connection Works

Once you see `HTTP Response code: 200`, check the web:

1. Open browser: `http://192.168.1.100:8000/`
2. Click "Assign" button
3. Your monitor should appear in the list
4. Select it and assign to a room
5. Click room card to see live data

---

## Quick Checklist

- [ ] Got IP address from IPCONFIG
- [ ] Updated Arduino code with correct IP
- [ ] Django server running in PowerShell
- [ ] Uploaded new Arduino code
- [ ] Serial Monitor shows HTTP 200 (success)
- [ ] Monitor appears in "Assign" modal
- [ ] Monitor assigned to room
- [ ] Room card shows live data

---

## If Still Not Working

**Test connectivity manually:**

In PowerShell:
```powershell
# Test if Arduino can reach server
Test-NetConnection -ComputerName 192.168.1.100 -Port 8000

# Should show: TcpTestSucceeded: True
```

If it shows `False`, then:
- Check firewall
- Check if Django is really running
- Check if correct IP address

---

## What "Error -1" Means

| Error Code | Meaning | Solution |
|-----------|---------|----------|
| -1 | Connection refused/timeout | Check IP, check Django running, check firewall |
| 0 | Unknown error | Restart Arduino, check WiFi |
| 200 | ✓ SUCCESS | Data sent! |
| 404 | Endpoint not found | Check API path is correct |
| 500 | Django error | Check Django console for errors |

---

**MOST COMMON FIX**: Wrong IP address in Arduino code  
**Check IPCONFIG and update the IP in the code!**
