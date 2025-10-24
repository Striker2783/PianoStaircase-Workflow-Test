import serial
import serial.tools.list_ports
from serial.threaded import ReaderThread, LineReader

serial_numbers = ["D2CC78A7249375CD4E42"]
serial_communicators = list()

class Port:
    def __init__(self, com_port, baud_rate=9600):
        self.serial = serial.Serial(com_port, baud_rate, timeout=2)

def setup():
    global serial_communicators, serial_numbers
    ports = serial.tools.list_ports.comports()
    mapped = dict()
    for port in ports:
        if port.serial_number is None:
            continue
        mapped[port.serial_number] = port.device
    for serial_number in serial_numbers:
        serial2 = mapped[serial_number]
        if serial2 is None:
            serial_communicators.append(None)
        serial_communicators.append(Port(port.name))

setup()

def get_distance(input):
    voltage = input * (5.0 / 1023.0)
    dist = 15.0 * pow(voltage, -1.1)
    return dist

class Event(LineReader):
    def handle_line(self, line):
        dist = get_distance(int(line))
        print(f"Distance: {dist:.4f} cm")

try:
    for ser in serial_communicators:
        thread = ReaderThread(ser.serial, Event)
        thread.start()
    while True:
        pass
except KeyboardInterrupt:
    print("Stopping")
finally:
    ser.close()