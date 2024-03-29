import time
from random import randrange


def millis():
    return int(time.monotonic() * 1000)


def delay(milliseconds):
    time.sleep(milliseconds/1000)


def beat8(beats_per_minute):
    frequency = 1 / beats_per_minute
    current = (millis() % (60000 * frequency)) / (60000 * frequency)
    val =  int(current * 256)
    return val

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def random(start, stop):
    return randrange(start, stop)
