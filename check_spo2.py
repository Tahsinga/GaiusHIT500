#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hitmonitor.settings')
django.setup()

from monitor.models import Reading

reading = Reading.objects.latest('timestamp')
print("=== Latest Reading from DB ===")
print(f"Room: {reading.room.name}")
print(f"Temp C: {reading.temp_c}")
print(f"BPM: {reading.bpm}")
print(f"SpO2: {reading.spo2}")  # Check if it's actually saved
print(f"Timestamp: {reading.timestamp}")
