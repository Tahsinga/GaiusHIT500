# Add missing import for time
import time
# API endpoint to list all monitors and their room assignments
from django.utils import timezone
from datetime import timedelta

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
    import os
    import glob
    from pathlib import Path
    base = Path(__file__).resolve().parent.parent
    monitor_files = glob.glob(str(base / 'latest_Monitor_*.json'))
    active_monitor_ids = set()
    for f in monitor_files:
        try:
            mtime = os.path.getmtime(f)
            if mtime >= (time.time() - 120):  # 2 minutes
                ident = os.path.basename(f).split('_')[-1].split('.')[0]
                active_monitor_ids.add(ident)
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
        result.append({
            'identifier': m.identifier,
            'room': m.room.name if m.room else None,
            'patient_name': m.room.current_patient.name if m.room and m.room.current_patient else None
        })

    # Add active identifiers detected via per-monitor JSON files that don't have Monitor rows yet
    for ident in sorted(active_monitor_ids):
        if ident in seen:
            continue
        result.append({'identifier': ident, 'room': None, 'patient_name': None})

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
        # Auto-create the room if it doesn't exist
        room, _ = Room.objects.get_or_create(name=room_name)
        
        # Create or get patient if provided
        if patient_name:
            patient, _ = Patient.objects.get_or_create(name=patient_name)
            room.current_patient = patient
            room.save()

        monitor.room = room
        monitor.save()
        return JsonResponse({'success': True, 'monitor_id': monitor_id, 'room_name': room_name, 'patient_name': patient_name})
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

        # If no patient_id is provided, use the room's currently assigned patient
        if not patient_id and room_obj and room_obj.current_patient:
            patient_id = str(room_obj.current_patient.id)
        elif not patient_id:
            # No patient assigned to this room, return 404
            return JsonResponse({'error': 'no_patient_assigned', 'room': room}, status=404)


        # Build queryset and filter by patient if requested
        qs = Reading.objects.filter(room__name=room)
        if patient_id:
            try:
                pid = int(patient_id)
                qs = qs.filter(patient__id=pid)
            except Exception:
                # invalid patient id -> no data
                return JsonResponse({'error': 'invalid_patient_id', 'room': room}, status=400)

        # Find the latest reading for this room (and patient if provided)
        reading = qs.order_by('-timestamp').first()
        if reading:
            data = {
                'temp_c': str(reading.temp_c) if reading.temp_c is not None else None,
                'temp_f': str(reading.temp_f) if reading.temp_f is not None else None,
                'bpm': reading.bpm,
                'room': reading.room.name,
                'patient_id': reading.patient.id if reading.patient else None,
                'timestamp': reading.timestamp.isoformat()
            }
            return JsonResponse(data)
        else:
            # No reading in DB for this room/patient -> 404 so frontend shows "no data"
            return JsonResponse({'error': 'no_data', 'room': room}, status=404)
    except Exception:
        # If anything goes wrong with DB access, fall back to file-based behavior
        pass

    # File-based fallback (legacy behaviour)
    try:
        room_file = BASE / f'latest_{room.replace(" ", "_")}.json'
        if room_file.exists():
            data = json.loads(room_file.read_text())
            return JsonResponse(data)
        elif room == 'Room 1' and LATEST_FILE.exists():
            data = json.loads(LATEST_FILE.read_text())
            return JsonResponse(data)
        else:
            return JsonResponse({'temp_c': None, 'temp_f': None, 'bpm': None, 'room': room, 'status': 'waiting'}, status=404)
    except Exception as e:
        return JsonResponse({'temp_c': None, 'temp_f': None, 'bpm': None, 'error': str(e)}, status=500)


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

        # Allow history requests filtered by patient_id. If no patient_id, use room's assigned patient.
        patient_id = request.GET.get('patient_id')

        # If no patient_id is provided, use the room's currently assigned patient
        if not patient_id and room_obj and room_obj.current_patient:
            patient_id = str(room_obj.current_patient.id)
        elif not patient_id:
            # No patient assigned to this room, return empty list with 404
            return JsonResponse([], safe=False, status=404)

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

