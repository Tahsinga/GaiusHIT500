# HIT Monitor - Modern Dashboard for HIT500 Arduino Project

A Django-based web dashboard that displays real-time temperature and heartbeat data from your HIT500 Arduino sensor module with modern animated gauges.

## Features

- **Live Dashboard**: Modern UI with animated semi-circle gauges for Temperature (°C & °F) and Heart Rate (BPM)
- **Real-time Updates**: Polls API every 1 second for latest sensor readings
- **Terminal Monitor**: Nicely formatted table output of all incoming sensor data
- **JSON Data Source**: `latest.json` acts as a bridge between Arduino and web app
- **Bootstrap & Chart.js**: Responsive, modern design using industry-standard libraries

## Project Structure

```
hit300/
├── manage.py                 # Django entry point
├── requirements.txt          # Python dependencies
├── ReceiveDataFromSeriel.py  # Serial data reader → writes latest.json
├── latest.json              # Live sensor data (auto-written by ReceiveDataFromSeriel.py)
├── README.md                # This file
├── hitmonitor/              # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── monitor/                 # Django app (dashboard & API)
    ├── views.py
    ├── urls.py
    ├── apps.py
    ├── templates/monitor/
    │   └── index.html       # Main dashboard page
    └── static/              # CSS, JS (if needed)
```

## Quick Start

### 1. Activate Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run Both Services Simultaneously

**Terminal 1 — Data Reader** (polls Arduino, writes to `latest.json`):

```powershell
python ReceiveDataFromSeriel.py
```

Or use test mode (simulates data without hardware):

```powershell
python ReceiveDataFromSeriel.py --test
```

**Terminal 2 — Django Server** (serves the web dashboard):

```powershell
python manage.py runserver
```

Then open your browser to **http://127.0.0.1:8000/**

### 4. View the Dashboard

You should see:
- Three animated gauge displays (Temperature in °C, Temperature in °F, Heart Rate in BPM)
- Live JSON data below (for debugging)
- Auto-refreshing every 1 second

## Configuration

### Arduino Serial Port

If your Arduino is on a different COM port, edit the top of `ReceiveDataFromSeriel.py`:

```python
PORT = 'COM3'  # Change to your port (e.g., COM3, COM4, etc.)
BAUD = 9600    # Baud rate (must match HIT500.ino)
```

To find available COM ports, run:

```powershell
python -c "from serial.tools import list_ports; print([p.device for p in list_ports.comports()])"
```

### Web Server Address

By default, Django serves at `127.0.0.1:8000`. To allow remote access:

```powershell
python manage.py runserver 0.0.0.0:8000
```

Then access from other machines on your network at `http://<your-ip>:8000/`

## API Endpoints

- **GET /**: Main dashboard page
- **GET /api/latest**: JSON API with latest readings
  ```json
  {"temp_c": "26.3", "temp_f": "79.3", "bpm": "72"}
  ```

## Troubleshooting

### "Cannot open serial port" Error

- Check the COM port in `ReceiveDataFromSeriel.py`
- Verify Arduino is connected to USB
- Make sure the port isn't in use by another application

### Dashboard shows "--" (no data)

- Start `ReceiveDataFromSeriel.py` first (it creates `latest.json`)
- Check that `latest.json` exists in the project root
- Try `python ReceiveDataFromSeriel.py --test` to test with simulated data

### ModuleNotFoundError: No module named 'django'

- Ensure venv is activated: `.\.venv\Scripts\Activate.ps1`
- Install requirements: `pip install -r requirements.txt`

## Next Steps

- **Logging**: Add CSV export to log readings over time
- **Alerts**: Send email/SMS if temperature or BPM exceed thresholds
- **History**: Store readings in database; add charts showing 1-hour, 1-day, 1-week trends
- **Deployment**: Use Docker or host on cloud platform (Heroku, AWS, etc.)

