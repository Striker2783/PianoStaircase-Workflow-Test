from __future__ import annotations
import serial
import serial.tools.list_ports
from serial.threaded import LineReader, ReaderThread
from typing import Callable, Dict, List, Set, TypedDict


BASIC_SENSOR_CONFIGURATION: List[SerialDeviceConfig] = [
    {"serial_number": "74134373633351D09221", "baudrate": 9600, "name": "Step1"},
    {"serial_number": "D2CC78A7249375CD4E42", "baudrate": 9600, "name": "Step2"},
]


# --- Configuration type ---
class SerialDeviceConfig(TypedDict):
    serial_number: str
    baudrate: int
    name: str


# --- Custom LineReader with multiple removable callbacks ---
class MultiCallbackReader(LineReader):
    TERMINATOR = b"\n"

    def __init__(self, info: SerialDeviceInfo) -> None:
        super().__init__()
        self.callbacks: Set[Callable[[str, SerialDeviceInfo], None]] = set()
        self.info = info

    def set_serial_device_info(self, info: SerialDeviceInfo):
        self.info = info

    def add_callback(self, func: Callable[[str, SerialDeviceInfo], None]) -> None:
        """Register a new callback (must accept a single str argument)."""
        if callable(func):
            self.callbacks.add(func)

    def remove_callback(self, func: Callable[[str, SerialDeviceInfo], None]) -> None:
        """Unregister a previously added callback."""
        self.callbacks.discard(func)

    def clear_callbacks(self) -> None:
        """Remove all callbacks."""
        self.callbacks.clear()

    def handle_line(self, line: str) -> None:
        """Dispatch received lines to all registered callbacks."""
        for cb in list(self.callbacks):
            try:
                cb(line, self.info)
            except Exception as e:
                print(f"Callback error: {e}")

    def handle_exception(self, exc: Exception):
        print("⚠️ Serial error:", exc)
        if self.on_disconnect:
            self.on_disconnect(exc)


# --- Utility functions ---
def get_serial_ports_by_serial_number() -> Dict[str, str]:
    """Return mapping: serial_number → device path."""
    ports = serial.tools.list_ports.comports()
    return {p.serial_number: p.device for p in ports if p.serial_number}


class SerialDeviceInfo(TypedDict):
    name: str
    serial: serial.Serial
    reader: ReaderThread
    protocol: MultiCallbackReader
    index: int


def initialize_serial_devices(
    configs: List[SerialDeviceConfig],
) -> Dict[int, SerialDeviceInfo]:
    """Initialize serial devices and start threaded readers."""
    serial_map = get_serial_ports_by_serial_number()
    devices: Dict[int, SerialDeviceInfo] = {}

    for idx, cfg in enumerate(configs):
        sn = cfg["serial_number"]
        baud = cfg["baudrate"]
        name = cfg["name"]

        if sn not in serial_map:
            print(f"Device {idx} ({name}, S/N {sn}) not found.")
            continue

        port = serial_map[sn]
        try:
            ser = serial.Serial(port, baudrate=baud, timeout=1)
            protocol = MultiCallbackReader()
            thread = ReaderThread(ser, lambda: protocol)

            devices[idx] = {
                "name": name,
                "serial": ser,
                "reader": thread,
                "protocol": protocol,
                "index": idx,
            }

            protocol.set_serial_device_info(devices[idx])
            thread.start()
            thread.connect()

        except serial.SerialException as e:
            print(f"Could not open [{idx}] {name} ({port}): {e}")

    return devices


def shutdown():
    global SERIAL_DEVICES
    print("\nClearing callbacks and closing connections...")
    for dev in SERIAL_DEVICES.values():
        proto = dev["protocol"]
        proto.clear_callbacks()
        dev["reader"].close()
        dev["serial"].close()


SERIAL_DEVICES = initialize_serial_devices(BASIC_SENSOR_CONFIGURATION)
