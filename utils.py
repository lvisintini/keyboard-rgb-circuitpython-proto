import time


def millis():
    return int(time.monotonic() * 1000)


def delay(milliseconds):
    time.sleep(milliseconds/1000)


def beat8(beats_per_minute):
    frequency = 1 / beats_per_minute
    current = (millis() % (60000 * frequency)) / (60000 * frequency)
    return int(current * 256)
