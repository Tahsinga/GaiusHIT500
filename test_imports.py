import serial
import requests
import sys

print("serial module:", getattr(serial, '__version__', 'unknown'))
print("requests version:", getattr(requests, '__version__', 'unknown'))
print("python executable:", sys.executable)
