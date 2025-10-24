import sensors


def get_distance(input):
    voltage = input * (5.0 / 1023.0)
    try:
        dist = 15.0 * pow(voltage, -1.1)
        return dist
    except ZeroDivisionError:
        return 0


def handle_line(line, index):
    dist = get_distance(int(line))
    print(f"Distance: {dist:.4f} cm by {index}")


try:
    for serial in sensors.serial_listeners.values():
        serial.addListener(handle_line)
        pass
    while True:
        pass
except KeyboardInterrupt:
    print("Terminated...")
finally:
    sensors.shutdown()
