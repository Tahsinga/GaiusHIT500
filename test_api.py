import os
import requests
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hitmonitor.settings')
import django
django.setup()

from monitor.models import Room, Patient

# Show current room-patient assignments
print("=== Current Room-Patient Assignments ===")
for room in Room.objects.all():
    patient = room.current_patient
    print(f"Room {room.name}: {patient.name if patient else 'None'} (ID: {patient.id if patient else 'None'})")

# Wait for server to start
print("\nWaiting for server...")
time.sleep(2)

# Test the API
print("\n=== Testing API Endpoints ===")

base_url = "http://localhost:8000"

# Test Room 3 (has patient KUDZAYI MOYO with ID 2)
print("\nTesting Room 3 (should have patient KUDZAYI MOYO):")
resp = requests.get(f"{base_url}/api/latest?room=Room%203")
print(f"  /api/latest?room=Room%203 -> Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"    Data: temp_c={data.get('temp_c')}, patient_id={data.get('patient_id')}")
else:
    print(f"    Error: {resp.json()}")

# Test Room 5 (has patient TASHINGA MUNQITSHWA with ID 1)
print("\nTesting Room 5 (should have patient TASHINGA MUNQITSHWA):")
resp = requests.get(f"{base_url}/api/latest?room=Room%205")
print(f"  /api/latest?room=Room%205 -> Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"    Data: temp_c={data.get('temp_c')}, patient_id={data.get('patient_id')}")
else:
    print(f"    Error: {resp.json()}")

# Test Room 1 (has patient TASHINGA MUNQITSHWA with ID 1)
print("\nTesting Room 1 (should have patient TASHINGA MUNQITSHWA):")
resp = requests.get(f"{base_url}/api/latest?room=Room%201")
print(f"  /api/latest?room=Room%201 -> Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"    Data: temp_c={data.get('temp_c')}, patient_id={data.get('patient_id')}")
else:
    print(f"    Error: {resp.json()}")

print("\nDone!")
