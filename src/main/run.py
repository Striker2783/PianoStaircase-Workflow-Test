import sensors


def get_distance(input):
    voltage = input * (5.0 / 1023.0)
    try:
        dist = 15.0 * pow(voltage, -1.1)
        return dist
    except ZeroDivisionError:
        return 0


def handle_line(line, info: sensors.SerialDeviceInfo):
    dist = get_distance(int(line))
    print(f"Distance: {dist:.4f} cm by {info['name']}")


try:
    for i, serial in sensors.SERIAL_DEVICES.items():
        serial["protocol"].add_callback(handle_line)
    while True:
        pass
except KeyboardInterrupt:
    print("Terminated...")
finally:
    sensors.shutdown()
