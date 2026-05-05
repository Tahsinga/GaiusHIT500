// ============================================
// WiFi Configuration Template
// Copy and paste these values into Max30102CodeUpdate.ino
// ============================================

// STEP 1: Find your WiFi network
// Open any device connected to WiFi and look for the network name (SSID)
const char* ssid = "YOUR_WIFI_SSID";

// STEP 2: Enter your WiFi password
const char* password = "YOUR_WIFI_PASSWORD";

// STEP 3: Find your Django server IP address
// On Windows: Open Command Prompt and type: ipconfig
// Look for "IPv4 Address" (usually starts with 192.168.x.x)
const char* server_ip = "192.168.1.100";

// STEP 4: Set Django server port
// Default for Django development server is 8000
// If running production, use 80 or 443
const int server_port = 8000;

// STEP 5: Set unique monitor ID
// Use "1", "2", "3", etc. for multiple monitors
const char* monitor_id = "1";

// ============================================
// Example Configurations
// ============================================

/* Home WiFi Setup:
const char* ssid = "MyHomeWiFi";
const char* password = "MyPassword123";
const char* server_ip = "192.168.1.50";
const int server_port = 8000;
const char* monitor_id = "1";
*/

/* Work Network with Hostname:
const char* ssid = "OfficeNetwork";
const char* password = "OfficePassword456";
const char* server_ip = "django-server.local";  // or 192.168.0.100
const int server_port = 8000;
const char* monitor_id = "2";
*/

/* Production Server:
const char* ssid = "MyWiFi";
const char* password = "MyPassword";
const char* server_ip = "192.168.1.200";  // External IP or domain
const int server_port = 80;
const char* monitor_id = "room-1";
*/

// ============================================
// Finding Django Server IP Address
// ============================================

// Method 1: From Windows Command Prompt
// 1. Press Win+R, type "cmd", press Enter
// 2. Type: ipconfig
// 3. Look for "IPv4 Address" under your network adapter
// 4. Should look like: 192.168.1.100

// Method 2: From Django Server
// 1. In Python terminal where Django is running:
//    import socket
//    socket.gethostbyname(socket.gethostname())
// 2. Result will be your IP address

// Method 3: Automatically detect (doesn't work with Arduino)
// If you want to use a hostname instead of IP:
// const char* server_ip = "your-server-name.local";

// ============================================
// Running Django Server
// ============================================

// Make sure Django is running with:
// python manage.py runserver 0.0.0.0:8000
//
// The "0.0.0.0" makes it accessible from other machines
// If you omit 0.0.0.0, it will only be accessible from localhost

// ============================================
// Troubleshooting Tips
// ============================================

// WiFi not connecting?
// - Check SSID spelling (case-sensitive)
// - Check password spelling (case-sensitive)  
// - Try rebooting the router
// - Move Arduino closer to router
// - Check if WiFi is 2.4GHz (5GHz may not work with ESP32)

// Can't reach server?
// - Verify server_ip is correct (ping from another device)
// - Verify server_port matches Django port
// - Check if firewall is blocking the port
// - Check if Django server is actually running
// - Check Serial Monitor for specific error

// Data not appearing in Django?
// - Check Django console for error messages
// - Verify monitor is assigned to a room in web interface
// - Try the test_wifi_api.py script first
// - Check database: python manage.py shell
