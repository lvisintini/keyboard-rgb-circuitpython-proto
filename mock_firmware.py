import time
from digitalio import DigitalInOut
import adafruit_matrixkeypad


class KeyStates:
    RELEASED = 0
    PRESSED = 1


class Key:
    key_number = None
    key_code = None
    last_changed = None
    state = KeyStates.RELEASED

    def __init__(self, key_number, key_code):
        self.key_number = key_number
        self.key_code = key_code

    def press(self, current_millis):
        self.last_changed = current_millis
        self.state = KeyStates.PRESSED

    def clear(self, current_millis):
        self.last_changed = current_millis
        self.state = KeyStates.RELEASED

    def get_millis_since(self, current_millis):
        if self.last_changed is None:
            return None
        return current_millis - self.last_changed

    @property
    def is_pressed(self):
        return self.state == KeyStates.PRESSED

    def __repr__(self):
        return f"<Key {self.key_number}:'{self.key_code}'>"


class NoKey:
    pass

NoK = NoKey()
NoL = NoK


class Keyboard:
    keypad = None
    keys = None
    mapping = None
    current_millis = None
    _previous_pressed = set()

    def __init__(self, row_pins, col_pins, keymap_macro, layer_1):
        self.keys = [Key(key_number, key_code) for key_number, key_code in enumerate(layer_1)]
        self.mapping = keymap_macro(*self.keys)

        self.keypad = adafruit_matrixkeypad.Matrix_Keypad(
            [DigitalInOut(pin) for pin in row_pins],
            [DigitalInOut(pin) for pin in col_pins],
            self.mapping
        )

        self.current_millis = time.monotonic() * 1000

    def scan(self):
        # This part manages the state of the keys.
        # It is a crude imitation of what the BlueMicro_BLE firmware does
        # It is here so the RGBFeature has an "API" that is similar to that of the firmware
        self.current_millis = time.monotonic() * 1000

        pressed_keys = self.keypad.pressed_keys


        for key in self.keypad.pressed_keys:
            key.press(self.current_millis)

        for key in self._previous_pressed.difference(pressed_keys):
            key.clear(self.current_millis)

        self._previous_pressed = set(pressed_keys)
        return pressed_keys

