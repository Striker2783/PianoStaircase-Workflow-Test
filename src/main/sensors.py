import serial
import serial.tools.list_ports
import serial.threaded
import typing


BASIC_SENSOR_CONFIGURATION = [
    {"serial_number": "74134373633351D09221", "baudrate": 9600, "name": "Step1"},
    {"serial_number": "D2CC78A7249375CD4E42", "baudrate": 9600, "name": "Step2"},
]


class Config:
    def __init__(self, basic_config, index, port):
        self.index = index
        self.serial_number = basic_config.serial_number
        self.baudrate = basic_config.baudrate
        self.name = basic_config.name
        self.port = port


sensor_configuration: typing.Dict[int, Config] = {}


def setup():
    """Setups the sensors configuration."""
    global BASIC_SENSOR_CONFIGURATION, sensor_configuration
    ports = serial.tools.list_ports.comports()
    mapped = dict()
    for port in ports:
        if port.serial_number is None:
            continue
        mapped[port.serial_number] = port.device
    for i in range(len(BASIC_SENSOR_CONFIGURATION)):
        port = mapped.get(BASIC_SENSOR_CONFIGURATION[i]["serial_number"])
        if port is None:
            continue
        sensor_configuration[i] = Config(BASIC_SENSOR_CONFIGURATION[i], i, port)
    setup_serial()


serial_devices: typing.Dict[int, serial.Serial] = dict()


class SerialListener(serial.threaded.LineReader):
    def __init__(self, index):
        super().__init__()
        self.index = index
        self.listeners = {}

    def handle_line(self, line):
        for listener in self.listeners.keys():
            listener(line, self.index)

    def addListener(self, callback):
        self.listeners[callback] = True

    def removeListener(self, callback):
        self.listeners.pop(callback)


reader_threads: typing.Dict[int, serial.threaded.ReaderThread] = dict()
serial_listeners: typing.Dict[int, SerialListener] = dict()


def setup_serial():
    global serial_devices, sensor_configuration
    for i, config in sensor_configuration.items():
        serial_devices[i] = serial.Serial(
            port=config.port, baudrate=config.baudrate, timeout=2
        )
    for i, serial_device in serial_devices.items():

        def factory():
            serial_listener = SerialListener(i)
            serial_listeners[i] = serial_listener
            return serial_listener

        reader_threads[i] = serial.threaded.ReaderThread(serial_device, factory)
        reader_threads[i].start()


def shutdown():
    for _, reader_thread in reader_threads.items():
        if reader_thread is None:
            continue
        reader_thread.stop()


setup()
