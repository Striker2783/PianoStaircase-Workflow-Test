import serial
from serial.threaded import ReaderThread, LineReader

ser = serial.Serial(
    port='COM4',
    baudrate=9600,
    timeout=2
)

class Event(LineReader):
    def handle_line(self, line):
        voltage = int(line) * (5.0 / 1023.0)
        print(f"Voltage: {voltage:.4f}")

try:
    thread = ReaderThread(ser, Event)
    thread.start()
    while True:
        pass
except KeyboardInterrupt:
    print("Stopping")
finally:
    ser.close()