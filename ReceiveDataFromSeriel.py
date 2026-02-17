import serial
import re
import time
import sys
import datetime
import requests
import json
from pathlib import Path
try:
    import serial
    from serial.tools import list_ports
except Exception:
    serial = None
    list_ports = None

# Optional: helper to save readings into Django DB if available
def save_reading_to_db(monitor_identifier, temp_c, temp_f, bpm):
    """Save a reading into DB if the monitor is assigned to a Room with a patient.

    Returns tuple (saved_to_db: bool, assigned_room_name: str|None, patient_name: str|None).
    If the monitor exists but has no assigned room or patient, no Reading is created and (False, None, None) is returned.
    """
    try:
        import os
        from decimal import Decimal
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hitmonitor.settings')
        import django
        django.setup()
        from monitor.models import Monitor, Reading

        monitor_obj, _ = Monitor.objects.get_or_create(identifier=str(monitor_identifier))
        if monitor_obj.room and monitor_obj.room.current_patient:
            reading = Reading.objects.create(
                room=monitor_obj.room,
                patient=monitor_obj.room.current_patient,
                temp_c=Decimal(temp_c) if temp_c is not None else None,
                temp_f=Decimal(temp_f) if temp_f is not None else None,
                bpm=int(bpm) if bpm is not None else None,
            )
            return True, monitor_obj.room.name, monitor_obj.room.current_patient.name
        else:
            # Monitor not assigned to a room or room has no patient yet
            return False, None, None
    except Exception as e:
        # DB not available or error - let caller fall back to json file
        print(f"DB save failed: {e}", file=sys.stderr)
        return False, None, None



def list_serial_ports():
    if list_ports is None:
        return []
    ports = list_ports.comports()
    return [p.device for p in ports]


PORT = None  # Auto-detect
BAUD = 9600


def auto_detect_port():
    """Try to find and connect to Arduino on available COM ports."""
    ports = list_serial_ports()
    print(f"Scanning ports: {ports}")
    
    for port in ports:
        try:
            print(f"Trying {port}...", end=" ", flush=True)
            ser = serial.Serial(port, BAUD, timeout=2)
            time.sleep(1)  # Give Arduino time to initialize
            ser.close()
            print("✓ Connected!")
            return port
        except Exception as e:
            print(f"✗")
    
    return None


def parse_line(line: str):
    """Parse a single line from HIT500 serial output.

    Returns tuple (monitor_id, room, celsius, fahrenheit, bpm). monitor_id is the numeric identifier as a string.
    """
    monitor_id = None
    room = None
    celsius = None
    fahr = None
    bpm = None

    # Extract room/monitor identifier: "Monitor 1:", "Room 1:", etc.
    m_room = re.search(r'(?:Monitor|Room)\s*(\d+)', line, re.IGNORECASE)
    if m_room:
        monitor_id = m_room.group(1)
        room = f"Room {monitor_id}"
    else:
        monitor_id = '1'
        room = "Room 1"  # Default to Room 1 if no identifier

    # Try the exact Temp line first: "Temp: 26.3 C 79.3 F"
    m_temp = re.search(r'Temp[:\s]*([-+]?[0-9]*\.?[0-9]+)\s*C\s*([-+]?[0-9]*\.?[0-9]+)\s*F', line, re.IGNORECASE)
    if m_temp:
        celsius = m_temp.group(1)
        fahr = m_temp.group(2)

    # Also allow separate Celsius/Fahrenheit patterns
    if not celsius:
        m_c = re.search(r'([-+]?[0-9]*\.?[0-9]+)\s*°?\s*C', line, re.IGNORECASE)
        if m_c:
            celsius = m_c.group(1)
    if not fahr:
        m_f = re.search(r'([-+]?[0-9]*\.?[0-9]+)\s*°?\s*F', line, re.IGNORECASE)
        if m_f:
            fahr = m_f.group(1)

    # BPM / IBI line: e.g. "IBI (ms): 830  BPM: 72"
    m_b = re.search(r'BPM[:\s]*([0-9]+)', line, re.IGNORECASE)
    if m_b:
        bpm = m_b.group(1)

    return monitor_id, room, celsius, fahr, bpm


def print_header():
    print('-' * 60)
    print(f"{'Time':<10} | {'Room':<8} | {'Temp (C)':<9} | {'Temp (F)':<9} | {'BPM':<4}")
    print('-' * 60)


def print_status(ts, room, c, f, b):
    cval = c or '--'
    fval = f or '--'
    bval = b or '--'
    print(f"{ts:<10} | {room:<8} | {cval:>7}   | {fval:>7}   | {bval:>3}")


def main(simulate=False):
    last_c = None
    last_f = None
    last_b = None
    last_room = None

    if simulate:
        # sample lines from HIT500 output with room identifiers
        sample_lines = [
            "Monitor 1: Temp: 26.3 C 79.3 F",
            "Monitor 1: IBI (ms): 830  BPM: 72",
            "Monitor 2: Temp: 25.4 C 77.7 F",
            "Monitor 2: IBI (ms): 800  BPM: 75",
            "Monitor 1: Temp: 26.4 C 79.5 F",
        ]

        print_header()
        for ln in sample_lines:
            monitor_id, room, c, f, b = parse_line(ln)
            now = datetime.datetime.now().strftime('%H:%M:%S')
            if c:
                last_c = c
            if f:
                last_f = f
            if b:
                last_b = b
            if room:
                last_room = room

            # Print status line
            print_status(now, last_room or "Room 1", last_c, last_f, last_b)

            # write latest.json per room
            try:
                json_path = Path(__file__).resolve().parent / f'latest_{(last_room or "Room 1").replace(" ", "_")}.json'
                json_data = {'temp_c': last_c, 'temp_f': last_f, 'bpm': last_b, 'room': last_room}
                json_path.write_text(json.dumps(json_data))
            except Exception:
                pass

            # Always write per-monitor JSON for visibility
            try:
                per_monitor = Path(__file__).resolve().parent / f'latest_Monitor_{monitor_id}.json'
                monitor_json = {'temp_c': last_c, 'temp_f': last_f, 'bpm': last_b, 'monitor': monitor_id}
                per_monitor.write_text(json.dumps(monitor_json))
            except Exception:
                pass

            # also attempt to save into database (if Django is available) and if monitor assigned to a room write room file
            try:
                saved, assigned_room, patient_name = save_reading_to_db(monitor_id, last_c, last_f, last_b)
                if saved and assigned_room:
                    try:
                        json_path = Path(__file__).resolve().parent / f'latest_{assigned_room.replace(" ", "_")}.json'
                        json_data = {'temp_c': last_c, 'temp_f': last_f, 'bpm': last_b, 'room': assigned_room}
                        json_path.write_text(json.dumps(json_data))
                    except Exception:
                        pass
            except Exception:
                pass

            time.sleep(0.4)
        sys.exit(1)

    # Determine which port to use: explicit `PORT` constant or attempt auto-detection
    port = PORT or auto_detect_port()
    if not port:
        print("No serial port found. Set `PORT` or connect the device.", file=sys.stderr)
        sys.exit(1)

    try:
        ser = serial.Serial(port, BAUD, timeout=1)
    except (serial.SerialException, AttributeError) as e:
        print(f"Could not open serial port {port}: {e}", file=sys.stderr)
        sys.exit(1)

    # brief startup delay
    try:
        for _ in range(10):
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Startup interrupted")
        ser.close()
        sys.exit(0)

    print_header()

    try:
        while True:
            raw = ser.readline()
            if not raw:
                continue
            line = raw.decode('utf-8', errors='replace').strip()
            if not line:
                continue

            # parse_line returns (monitor_id, room, celsius, fahrenheit, bpm)
            monitor_id, room, c, f, b = parse_line(line)
            now = datetime.datetime.now().strftime('%H:%M:%S')
            updated = False
            if c:
                last_c = c
                updated = True
            if f:
                last_f = f
                updated = True
            if b:
                last_b = b
                updated = True
            if room:
                last_room = room
                updated = True

            if updated:
                print_status(now, last_room or "Room 1", last_c, last_f, last_b)
                # write latest.json per room for web dashboard
                try:
                    room_name = last_room or "Room 1"
                    # Always write per-monitor JSON
                    try:
                        per_monitor = Path(__file__).resolve().parent / f'latest_Monitor_{monitor_id}.json'
                        monitor_json = {'temp_c': last_c, 'temp_f': last_f, 'bpm': last_b, 'monitor': monitor_id}
                        per_monitor.write_text(json.dumps(monitor_json))
                    except Exception:
                        pass

                    # attempt to save to DB (best-effort). If monitor is mapped, this will also create a room file
                    saved, assigned_room, patient_name = save_reading_to_db(monitor_id, last_c, last_f, last_b)
                    if saved:
                        print(f"  -> Saved reading to DB for monitor {monitor_id} (room: {assigned_room})", file=sys.stderr)
                        if assigned_room:
                            try:
                                json_path = Path(__file__).resolve().parent / f'latest_{assigned_room.replace(" ", "_")}.json'
                                json_data = {'temp_c': last_c, 'temp_f': last_f, 'bpm': last_b, 'room': assigned_room}
                                json_path.write_text(json.dumps(json_data))
                                print(f"  -> Wrote to {json_path.name}: {json_data}", file=sys.stderr)
                            except Exception:
                                pass
                    else:
                        # not saved to DB because monitor unassigned; indicate per-monitor write only
                        print(f"  -> Monitor {monitor_id} unassigned; wrote per-monitor JSON only", file=sys.stderr)
                except Exception as e:
                    print(f"  ERROR writing JSON or DB: {e}", file=sys.stderr)
            else:
                # show raw if we couldn't parse it (useful for debugging)
                print(f"RAW: {line}")

    except KeyboardInterrupt:
        print("\nInterrupted by user - closing serial port")
    finally:
        try:
            ser.close()
        except Exception:
            pass


if __name__ == '__main__':
    simulate = False
    if len(sys.argv) > 1 and sys.argv[1].lower() in ('--test', 'test'):
        simulate = True
    main(simulate=simulate)
