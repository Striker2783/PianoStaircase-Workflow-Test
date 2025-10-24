import serial
import serial.tools.list_ports
import threading

serial_numbers = ["74134373633351D09221", "D2CC78A7249375CD4E42"]
serial_communicators = list()


class Port:
    def __init__(self, number, com_port, baud_rate=9600):
        self.serial = serial.Serial(com_port, baud_rate, timeout=2)
        self.number = number


def setup():
    global serial_communicators, serial_numbers
    ports = serial.tools.list_ports.comports()
    mapped = dict()
    for port in ports:
        if port.serial_number is None:
            continue
        mapped[port.serial_number] = port.device
    for i in range(len(serial_numbers)):
        serial2 = mapped.get(serial_numbers[i])
        if serial2 is None:
            serial_communicators.append(None)
        serial_communicators.append(Port(i, port.name))


def get_distance(input):
    voltage = input * (5.0 / 1023.0)
    dist = 15.0 * pow(voltage, -1.1)
    return dist


def handle_line(line, serial):
    dist = get_distance(int(line))
    print(f"Distance: {dist:.4f} cm by {serial.number}")


def read_from_port(ser, callback, event):
    while not event.is_set():
        data = ser.serial.readline().decode("utf-8").strip()
        if data:
            callback(data, ser)


setup()

threads = []
event = threading.Event()
try:
    for ser in serial_communicators:
        thread = threading.Thread(
            target=read_from_port, args=(ser, handle_line, event), daemon=False
        )
        threads.append(thread)
        thread.start()
    while True:
        pass
except KeyboardInterrupt:
    event.set()
    for thread in threads:
        thread.join()
