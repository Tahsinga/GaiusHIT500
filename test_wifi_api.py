#!/usr/bin/env python3
"""
Test script to verify the Django API receives data correctly.
Run this script to simulate Arduino data being sent to your Django server.

Usage:
    python test_wifi_api.py
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
SERVER_IP = "127.0.0.1"  # Change to your Django server IP
SERVER_PORT = 8000
MONITOR_ID = "1"

# Construct the API endpoint
API_URL = f"http://{SERVER_IP}:{SERVER_PORT}/api/receive_reading"

def test_connection():
    """Test if the Django server is reachable"""
    print(f"\n[1/3] Testing connection to Django server at {API_URL}...")
    try:
        response = requests.get(f"http://{SERVER_IP}:{SERVER_PORT}/", timeout=5)
        print("✓ Django server is reachable!")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Django server!")
        print(f"  Make sure Django is running: python manage.py runserver 0.0.0.0:{SERVER_PORT}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def send_test_data():
    """Send test sensor data to the API"""
    print(f"\n[2/3] Sending test sensor data to {API_URL}...")
    
    test_payload = {
        "monitor_id": MONITOR_ID,
        "temp_c": 37.2,
        "temp_f": 98.96,
        "bpm": 72,
        "spo2": 98
    }
    
    print(f"  Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(API_URL, json=test_payload, headers=headers, timeout=5)
        
        print(f"\n✓ Request sent successfully!")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n✓ Response parsed successfully:")
                print(f"  - Status: {data.get('status')}")
                print(f"  - Reading ID: {data.get('reading_id')}")
                print(f"  - Room: {data.get('room', 'Not assigned')}")
                return True
            except:
                return False
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection refused! Is Django running?")
        return False
    except Exception as e:
        print(f"✗ Error sending data: {e}")
        return False

def check_data_in_database():
    """Check if the data was saved to the database"""
    print(f"\n[3/3] Checking if data was saved to database...")
    print("  (This requires the monitor to be assigned to a room in the web interface)")
    
    try:
        # Try to read the API to see latest reading
        api_url = f"http://{SERVER_IP}:{SERVER_PORT}/api/latest?room=Room%201"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Latest reading retrieved:")
            print(f"  - Room: {data.get('room')}")
            print(f"  - Temperature: {data.get('temp_c')}°C / {data.get('temp_f')}°F")
            print(f"  - Heart Rate: {data.get('bpm')} BPM")
            print(f"  - SpO2: {data.get('spo2')}%")
            print(f"  - Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"✗ Could not retrieve data (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Django API Test for Arduino WiFi Monitor")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Server: {SERVER_IP}:{SERVER_PORT}")
    print(f"  Endpoint: /api/receive_reading")
    print(f"  Monitor ID: {MONITOR_ID}")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    
    # Run tests
    if not test_connection():
        print("\n" + "=" * 60)
        print("FAILED: Cannot connect to server")
        print("=" * 60)
        sys.exit(1)
    
    if not send_test_data():
        print("\n" + "=" * 60)
        print("FAILED: Could not send test data")
        print("=" * 60)
        sys.exit(1)
    
    check_data_in_database()
    
    print("\n" + "=" * 60)
    print("✓ API Test Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Update the Arduino code with your WiFi credentials:")
    print("   - ssid: Your WiFi network name")
    print("   - password: Your WiFi password")
    print("   - server_ip: Your Django server IP")
    print("   - server_port: " + str(SERVER_PORT))
    print("   - monitor_id: Unique ID for this Arduino")
    print("\n2. Flash the updated code to your ESP32")
    print("\n3. Open Serial Monitor to see data being sent")
    print("\n4. Assign the monitor to a room in the web interface")
    print("   at http://" + SERVER_IP + ":" + str(SERVER_PORT))

if __name__ == "__main__":
    main()
