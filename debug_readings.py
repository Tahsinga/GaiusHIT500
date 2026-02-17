import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hitmonitor.settings')
import django
django.setup()

from monitor.models import Reading, Patient, Room
from django.db.models import Count

# Check readings per patient
print("=== Readings per Patient ===")
patient_counts = Reading.objects.values('patient__name').annotate(cnt=Count('id')).order_by('patient__name')
for p in patient_counts:
    print(f"{p['patient__name']}: {p['cnt']} readings")

print("\n=== Readings per Room ===")
room_counts = Reading.objects.values('room__name').annotate(cnt=Count('id')).order_by('room__name')
for r in room_counts:
    print(f"{r['room__name']}: {r['cnt']} readings")

print("\n=== Readings per Room and Patient ===")
room_patient = Reading.objects.values('room__name', 'patient__name').annotate(cnt=Count('id')).order_by('room__name', 'patient__name')
for rp in room_patient:
    print(f"Room {rp['room__name']} -> Patient {rp['patient__name']}: {rp['cnt']} readings")

print("\n=== Sample Latest Readings (first 5) ===")
latest = Reading.objects.all().order_by('-timestamp')[:5]
for r in latest:
    print(f"ID {r.id}: Room={r.room.name}, Patient={r.patient.name if r.patient else 'None'}, Temp={r.temp_c}C, Time={r.timestamp}")

print("\n=== Check Room-Patient Assignments ===")
for room in Room.objects.all():
    patient = room.current_patient
    print(f"Room {room.name}: current_patient = {patient.name if patient else 'None'}")
