# Add missing import for time
import time
# API endpoint to list all monitors and their room assignments
from django.utils import timezone
from datetime import timedelta
import json
import glob
import os
from pathlib import Path

def api_monitors(request):
    from .models import Monitor, Reading
    # Define 'active' as having a reading in the last 2 minutes
    active_cutoff = timezone.now() - timedelta(minutes=2)
    # Find all unique monitor identifiers from recent readings
    # A reading is linked to a room, but we want the monitor that sent it (by identifier in the reading's per-monitor JSON)
    # So, we need to find all Monitor objects that have had a reading for their assigned room in the last 2 minutes
    # But also, if a monitor is unassigned but sending, we want to show it
    # We'll look for all Monitor objects that have a Reading in the last 2 minutes for their assigned room, or that have a per-monitor JSON file updated recently

    # First, get all monitor identifiers that have a Reading in the last 2 minutes (by room assignment)
    active_room_ids = set(Reading.objects.filter(timestamp__gte=active_cutoff).values_list('room', flat=True))
    monitors_by_room = Monitor.objects.filter(room__in=active_room_ids)

    # Second, get all monitor identifiers that have a per-monitor JSON file updated in the last 2 minutes
    # (This is a fallback for unassigned monitors, using the per-monitor JSON files written by ReceiveDataFromSeriel.py)
    base = Path(__file__).resolve().parent.parent
    monitor_files = glob.glob(str(base / 'latest_Monitor_*.json'))
    active_monitor_ids = set()
    latest_readings = {}
    for f in monitor_files:
        try:
            mtime = os.path.getmtime(f)
            if mtime >= (time.time() - 120):  # 2 minutes
                ident = os.path.basename(f).split('_')[-1].split('.')[0]
                active_monitor_ids.add(ident)
                try:
                    latest_readings[ident] = json.loads(Path(f).read_text())
                except Exception:
                    latest_readings[ident] = None
        except Exception:
            pass
    monitors_by_file = Monitor.objects.filter(identifier__in=active_monitor_ids)

    # Build result: include monitors found in DB plus any active identifiers not yet in DB
    result = []
    seen = set()
    for m in list(monitors_by_room) + list(monitors_by_file):
        if m.identifier in seen:
            continue
        seen.add(m.identifier)

        latest_reading = latest_readings.get(str(m.identifier))
        if not latest_reading and m.room:
            last_reading = Reading.objects.filter(room=m.room).order_by('-timestamp').first()
            if last_reading:
                latest_reading = {
                    'temp_c': str(last_reading.temp_c) if last_reading.temp_c is not None else None,
                    'temp_f': str(last_reading.temp_f) if last_reading.temp_f is not None else None,
                    'bpm': last_reading.bpm,
                    'spo2': last_reading.spo2,
                    'room': last_reading.room.name,
                    'timestamp': last_reading.timestamp.isoformat(),
                }

        result.append({
            'identifier': m.identifier,
            'room': m.room.name if m.room else None,
            'patient_name': m.room.current_patient.name if m.room and m.room.current_patient else None,
            'latest_reading': latest_reading
        })

    # Add active identifiers detected via per-monitor JSON files that don't have Monitor rows yet
    for ident in sorted(active_monitor_ids):
        if ident in seen:
            continue
        result.append({
            'identifier': ident,
            'room': None,
            'patient_name': None,
            'latest_reading': latest_readings.get(ident)
        })

    return JsonResponse(result, safe=False)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
# API endpoint to assign a monitor to a room
@csrf_exempt
@require_POST
def api_assign_monitor(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        monitor_id = data.get('monitor_id')
        room_name = data.get('room_name')
        patient_name = data.get('patient_name', '')
        if not monitor_id or not room_name:
            return JsonResponse({'error': 'Missing monitor_id or room_name'}, status=400)

        from .models import Monitor, Room, Patient
        # Create monitor if it doesn't exist so users can assign new detected monitors
        monitor, _ = Monitor.objects.get_or_create(identifier=str(monitor_id))
        
        # Check if another monitor is already assigned to this room
        other_monitors = Monitor.objects.filter(room__name=room_name).exclude(identifier=monitor_id)
        if other_monitors.exists():
            # Unassign the other monitor(s) from this room
            other_monitors.update(room=None)
        
        # If this monitor is already assigned to a different room, clear the old room first
        if monitor.room and monitor.room.name != room_name:
            old_room_obj = monitor.room
            old_room_obj.current_patient = None  # Clear patient assignment from old room
            old_room_obj.save()
        
        old_room = monitor.room.name if monitor.room else None
        
        # Auto-create the room if it doesn't exist
        room, _ = Room.objects.get_or_create(name=room_name)
        
        # Clear any existing patient assignment from the target room
        if room.current_patient:
            room.current_patient = None
            room.save()
        
        # Create or get patient if provided
        if patient_name:
            patient, _ = Patient.objects.get_or_create(name=patient_name)
            room.current_patient = patient
            room.save()

        monitor.room = room
        monitor.save()
        
        response = {
            'success': True, 
            'monitor_id': monitor_id, 
            'room_name': room_name, 
            'patient_name': patient_name,
            'old_room': old_room
        }
        if old_room and old_room != room_name:
            response['message'] = f'Monitor reassigned from {old_room} to {room_name}'
        
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_patients(request):
    """Return all patients, or create a new one."""
    try:
        from .models import Patient
        if request.method == 'POST':
            data = json.loads(request.body.decode('utf-8'))
            patient_name = data.get('name', '').strip()
            if not patient_name:
                return JsonResponse({'error': 'Patient name required'}, status=400)
            patient, created = Patient.objects.get_or_create(name=patient_name)
            return JsonResponse({'id': patient.id, 'name': patient.name, 'created': created})
        else:
            patients = Patient.objects.all().values('id', 'name')
            return JsonResponse(list(patients), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_set_room_patient(request):
    """Set the current patient for a room."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        room_name = data.get('room_name')
        patient_id = data.get('patient_id')
        if not room_name or not patient_id:
            return JsonResponse({'error': 'Missing room_name or patient_id'}, status=400)
        
        from .models import Room, Patient
        room = Room.objects.get(name=room_name)
        patient = Patient.objects.get(id=patient_id)
        room.current_patient = patient
        room.save()
        return JsonResponse({'success': True, 'room_name': room_name, 'patient_name': patient.name})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_rooms(request):
    """Return all rooms with their current patient."""
    try:
        from .models import Room
        rooms = Room.objects.all()
        result = [{'name': r.name, 'patient_id': r.current_patient.id if r.current_patient else None, 'patient_name': r.current_patient.name if r.current_patient else ''} for r in rooms]
        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

import json
import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LATEST_FILE = BASE / 'latest.json'


def index(request):
    return render(request, 'monitor/index.html')


def api_latest(request):
    """Return the latest reading for a given room.

    First attempt to read from the database (if migrations have been applied).
    If the DB is not available or there are no readings, fall back to the
    legacy `latest_{Room_N}.json` file behaviour.
    """
    room = request.GET.get('room', 'Room 1')
    room_obj = None

    # Try DB first (gracefully fall back if models/migrations not ready)
    try:
        from .models import Reading, Room as RoomModel, Monitor

        # Get the room object first
        try:
            room_obj = RoomModel.objects.get(name=room)
        except:
            room_obj = None

        # Allow filtering by patient when provided so UI can request data per-patient
        patient_id = request.GET.get('patient_id')

        # If patient_id is provided, use it
        if patient_id:
            try:
                pid = int(patient_id)
                qs = Reading.objects.filter(room__name=room, patient__id=pid)
            except Exception:
                # invalid patient id -> return empty data
                return JsonResponse({'temp_c': None, 'temp_f': None, 'bpm': None, 'spo2': None, 'room': room}, status=404)
        else:
            # No patient_id provided, just get latest reading for the room regardless of patient
            qs = Reading.objects.filter(room__name=room)

        # Find the latest reading for this room (and patient if provided)
        reading = qs.order_by('-timestamp').first()
        if reading:
            data = {
                'temp_c': str(reading.temp_c) if reading.temp_c is not None else None,
                'temp_f': str(reading.temp_f) if reading.temp_f is not None else None,
                'bpm': reading.bpm,
                'spo2': reading.spo2,
                'room': reading.room.name,
                'patient_id': reading.patient.id if reading.patient else None,
                'timestamp': reading.timestamp.isoformat()
            }
            return JsonResponse(data)
        else:
            # No reading in DB for this room -> try file fallback
            pass
    except Exception:
        # If anything goes wrong with DB access, fall back to file-based behavior
        pass

    # File-based fallback (legacy behaviour)
    try:
        room_file = BASE / f'latest_{room.replace(" ", "_")}.json'
        if room_file.exists():
            data = json.loads(room_file.read_text())
            return JsonResponse(data)
        elif room_obj and room_obj.monitor:
            monitor_file = BASE / f'latest_Monitor_{room_obj.monitor.identifier}.json'
            if monitor_file.exists():
                data = json.loads(monitor_file.read_text())
                data['room'] = room
                return JsonResponse(data)
        elif room == 'Room 1' and LATEST_FILE.exists():
            data = json.loads(LATEST_FILE.read_text())
            return JsonResponse(data)
        else:
            # Return empty reading instead of 404 so frontend can still show the room
            return JsonResponse({'temp_c': None, 'temp_f': None, 'bpm': None, 'spo2': None, 'room': room, 'status': 'waiting'})
    except Exception as e:
        # Return empty reading instead of 500 error
        return JsonResponse({'temp_c': None, 'temp_f': None, 'bpm': None, 'spo2': None, 'room': room, 'error': str(e)})


def api_history(request):
    """Return the last N readings for a given room as JSON array.

    Query params:
      - room: room name (e.g., "Room 1")
      - limit: number of readings to return (default 8)
    """
    room = request.GET.get('room', 'Room 1')
    try:
        limit = int(request.GET.get('limit', 8))
    except Exception:
        limit = 8

    try:
        from .models import Reading, Monitor

        from .models import Reading, Monitor, Room as RoomModel

        # Get the room object first
        try:
            room_obj = RoomModel.objects.get(name=room)
        except:
            room_obj = None

        # Allow history requests filtered by patient_id. If no patient_id is provided,
        # return all readings for the room so live graphs still work when the monitor is
        # assigned to a room without a current patient.
        patient_id = request.GET.get('patient_id')

        qs = Reading.objects.filter(room__name=room)
        if patient_id:
            try:
                pid = int(patient_id)
                qs = qs.filter(patient__id=pid)
            except Exception:
                return JsonResponse({'error': 'invalid_patient_id'}, status=400)

        readings = qs.order_by('-timestamp')[:limit]
        result = []
        for r in readings:
            result.append({
                'temp_c': str(r.temp_c) if r.temp_c is not None else None,
                'temp_f': str(r.temp_f) if r.temp_f is not None else None,
                'bpm': r.bpm,
                'spo2': r.spo2,
                'timestamp': r.timestamp.isoformat(),
                'room': r.room.name,
            })
        # Return in chronological order (oldest first)
        return JsonResponse(list(reversed(result)), safe=False)
    except Exception:
        # DB not available or other error - fall back to returning single latest file if present
        try:
            room_file = BASE / f'latest_{room.replace(" ", "_")}.json'
            if room_file.exists():
                data = json.loads(room_file.read_text())
                # single-element history
                return JsonResponse([data], safe=False)
            else:
                return JsonResponse([], safe=False, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_patient_logs(request):
    """Return patient logs with search and filtering capabilities."""
    try:
        from .models import Reading, Patient, Room as RoomModel

        # Get query parameters
        search = request.GET.get('search', '').strip()
        patient_id = request.GET.get('patient_id')
        limit = int(request.GET.get('limit', 50))

        # Base queryset
        readings_qs = Reading.objects.select_related('patient', 'room').order_by('-timestamp')

        # Filter by patient if specified
        if patient_id:
            try:
                pid = int(patient_id)
                readings_qs = readings_qs.filter(patient__id=pid)
            except ValueError:
                return JsonResponse({'error': 'Invalid patient_id'}, status=400)

        # Search by patient name if search term provided
        elif search:
            readings_qs = readings_qs.filter(patient__name__icontains=search)

        # Limit results
        readings = readings_qs[:limit]

        # Group by patient
        patients_data = {}
        for reading in readings:
            if not reading.patient:
                continue

            pid = reading.patient.id
            if pid not in patients_data:
                patients_data[pid] = {
                    'id': pid,
                    'name': reading.patient.name,
                    'total_readings': 0,
                    'rooms': set(),
                    'readings': []
                }

            patient_data = patients_data[pid]
            patient_data['total_readings'] += 1
            patient_data['rooms'].add(reading.room.name)

            patient_data['readings'].append({
                'temp_c': float(reading.temp_c) if reading.temp_c is not None else None,
                'temp_f': float(reading.temp_f) if reading.temp_f is not None else None,
                'bpm': reading.bpm,
                'spo2': reading.spo2,
                'timestamp': reading.timestamp.isoformat(),
                'room': reading.room.name,
                'date': reading.timestamp.strftime('%Y-%m-%d'),
                'time': reading.timestamp.strftime('%H:%M:%S')
            })

        # Convert sets to lists and sort readings by timestamp
        result = []
        for pid, data in patients_data.items():
            data['rooms'] = sorted(list(data['rooms']))
            data['readings'].sort(key=lambda x: x['timestamp'], reverse=True)
            result.append(data)

        # Sort patients by most recent reading
        result.sort(key=lambda x: x['readings'][0]['timestamp'] if x['readings'] else '', reverse=True)

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_patients_list(request):
    """Return list of all patients with their data summary."""
    try:
        from .models import Patient, Reading

        patients = Patient.objects.all().order_by('name')
        result = []

        for patient in patients:
            # Get reading count and rooms for this patient
            readings = Reading.objects.filter(patient=patient)
            reading_count = readings.count()

            if reading_count > 0:
                rooms = set(readings.values_list('room__name', flat=True))
                latest_reading = readings.order_by('-timestamp').first()

                result.append({
                    'id': patient.id,
                    'name': patient.name,
                    'total_readings': reading_count,
                    'rooms': sorted(list(rooms)),
                    'latest_reading': {
                        'timestamp': latest_reading.timestamp.isoformat(),
                        'temp_c': float(latest_reading.temp_c) if latest_reading.temp_c else None,
                        'bpm': latest_reading.bpm,
                        'spo2': latest_reading.spo2,
                        'room': latest_reading.room.name
                    }
                })

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_receive_reading(request):
    """Receive a reading from Arduino device via HTTP POST."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        monitor_id = data.get('monitor_id', '1')
        temp_c = data.get('temp_c')
        temp_f = data.get('temp_f')
        bpm = data.get('bpm')
        spo2 = data.get('spo2')

        # Try to save to DB if the monitor is assigned to a room.
        from .models import Monitor, Reading
        monitor_obj, _ = Monitor.objects.get_or_create(identifier=str(monitor_id))
        if monitor_obj.room:
            reading = Reading.objects.create(
                room=monitor_obj.room,
                patient=monitor_obj.room.current_patient if monitor_obj.room.current_patient else None,
                temp_c=temp_c,
                temp_f=temp_f,
                bpm=bpm,
                spo2=spo2,
            )
            return JsonResponse({'status': 'saved', 'reading_id': reading.id, 'monitor_id': monitor_id, 'room': monitor_obj.room.name})
        else:
            # Save to JSON file as fallback for unassigned monitors
            base = Path(__file__).resolve().parent.parent
            filename = base / f'latest_Monitor_{monitor_id}.json'
            json_data = {
                'temp_c': temp_c,
                'temp_f': temp_f,
                'bpm': bpm,
                'spo2': spo2,
                'monitor_id': monitor_id,
                'timestamp': timezone.now().isoformat()
            }
            filename.write_text(json.dumps(json_data))
            return JsonResponse({'status': 'saved_to_file', 'monitor_id': monitor_id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

