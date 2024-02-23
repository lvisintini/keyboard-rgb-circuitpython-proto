import board
import digitalio
import neopixel
import adafruit_fancyled.adafruit_fancyled as fancy
from adafruit_itertools import adafruit_itertools as itertools
from mock_firmware import NoK, NoL
from utils import constrain



external_vcc_cutoff_pin = digitalio.DigitalInOut(board.P0_13)
external_vcc_cutoff_pin.direction = digitalio.Direction.OUTPUT
external_vcc_cutoff_pin.value = True


class RGBController:
    strip = None
    num_led = None
    num_rows = None
    num_cols = None

    _is_on = False
    neopixel_strip = None

    hue_step = 8
    saturation_step = 0.075
    brightness_step = 0.075

    # Settings
    hue = 0
    saturation = 1.0
    brightness = 1.0

    default_hue = 0
    default_saturation = 1.0
    default_brightness = 1.0

    @property
    def is_on(self):
        return self._is_on

    @is_on.setter
    def is_on(self, value):
        self._is_on = bool(value)
        # This is additional functionality that nicenano has.
        if self._is_on:
            external_vcc_cutoff_pin.value = True
        else:
            external_vcc_cutoff_pin.value = False

    def __init__(
        self,
        init_state,  # Default/Initial status for RBG handling and effects (RGB_ON setting, though could it be toggled)
        num_led,  # The number of leads in the LED "strip". (NUM_LEDS setting)
        rgb_pin,  # The pin used to control the LED "strip". (RGB_PIN setting)
        rgb_order,  # Depends on the type of RGB LED used, it releates to how the values provided to the LEDs are interpreted  (RGB_ORDER setting)
        num_keys,  # We also need an indication of how many keys does the matrix have.
        keymap_macro,  # Used as a fallback to match the key matrix to LED strip, provided led_matrix and/or key_led_map_macro are not provkded (KEYMAP setting)
        led_matrix=None,  # A macro used to model how the LEDs (wired linearly) are presented as a matrix. It need not match KEYMAP but reduces configuration if it does. (LED_MATRIX setting)
        key_led_map_macro=None,  # If the number of keys in the does not match the number of LEDs in the strip or if LED_MATRIX and KEYMAP do not mesh very well, this macro wouyld be used to match individual keys to individual LEDs (setting KEY_LED_MAPPING)
        hue=None,  # Default Hue for all effects. An integer in the 0-255 range. (RGB_HUE setting, though could it be adjusted)
        saturation=None,  # Default saturation for all effects. An integer in the 0-255 range. (RGB_SATURATION setting, though could it be adjusted)
        brightness=None,  # Default brightness. A float value in the 0.0-1.0 range that determines the maximum level of brightness for the LEDs (RGB_BRIGHTNESS setting, though could it be adjusted)
    ):
        self.is_on = init_state

        self.num_led = num_led

        self.hue = hue or self.hue
        self.saturation = saturation or self.saturation
        self.brightness = brightness or self.brightness

        # This are here in case the RGB effects need them.
        self.default_hue = self.hue
        self.default_saturation = self.saturation
        self.default_brightness = self.brightness

        # If led_matrix is not provided, we should assume the LED wiring matches the logical sequence
        # this firmware uses for the mapping the keys.
        # This may not always hold true, but it at least reduces the amount of config required
        if led_matrix:
            self.matrix = led_matrix(*range(num_led))
        else:
            self.matrix = [
                [key if key != NoK else NoL for key in row]
                for row in keymap_macro(*range(num_keys))
            ]

        # For reactive effects only.

        # The keys in the matrix are numbered sequentially from zero and their numbers are computed with
        # by `row * len(column_pins) + column` (in layman terms "left to right, top to bottom")
        # If this same "order of appearance" is used also in the LED matrix then it is possible to automatically
        # match key #1 with LED #1 (event if that LED is not the first one on strip), key #2 with LED #2 and so on and so forth.

        # The assumption here is that the values returned by both macros have the same number of keys and LEDs
        # and that the "order of appearance" of the LED matches in the led_matrix match the order of "order of
        # appearance" of the keys

        # If that assumption does not hold True, then a KEY_LED_MAPPING macro needs to be provided to account for
        # a more nuanced setup/wiring.
        if key_led_map_macro:
            params = list(range(num_keys))
            params.extend(range(self.num_led))
            self.key_led_mapping = dict(key_led_map_macro(*params))
        else:
            self.key_led_mapping = dict(
                zip(
                    [
                        key
                        for row in keymap_macro(*range(num_keys))
                        for key in row
                        if key != NoK
                    ],
                    [led for row in self.matrix for led in row if led != NoL],
                )
            )

        self.num_rows = len(self.matrix)
        self.num_cols = len(
            self.matrix[0]
        )  # Assume all rows have the same length (# of columns)

        # It's difficult (if not impossible) to read the brightness values of individual LEDs in the Neopixel strip.
        # To overcome this, each effect may chose to maintain a cache of the state of the LEDs.
        self.strip = []
        for i in range(self.num_led):
            self.strip.append(
                fancy.CHSV(
                    self.hue,
                    self.saturation,
                    0
                )
            )

        self.neopixel_strip = neopixel.NeoPixel(
            rgb_pin,
            num_led,
            brightness=brightness,
            auto_write=False,
            pixel_order=rgb_order,
        )

    def set_led_color_by_key_number(self, key_number, color):
        led_number = self.key_led_mapping[key_number]
        if led_number is not NoL:
            self.strip[led_number] = color

    def set_led_color(self, led_number, color):
        self.strip[led_number] = color

    def fade_all(self, lower_by):
        for i in range(self.num_led):
            self.strip[i].value = fancy.clamp_norm(self.strip[i].value - lower_by)

    def fade_led(self, led_number, lower_by):
        self.strip[led_number].value = fancy.clamp_norm(self.strip[led_number].value - lower_by)

    def set_led_brightness(self, led_number, brightness):
        self.strip[led_number].value = fancy.clamp_norm(brightness)

    def fill(self, color):
        for i in range(self.num_led):
            self.strip[i] = fancy.CHSV(
                color.hue,
                color.saturation,
                color.value
            )

    def show(self):
        for i in range(self.num_led):
            self.neopixel_strip[i] = self.strip[i].pack()
        self.neopixel_strip.show()

    def toggle(self):
        self.is_on = not self.is_on

    def cycle_hue(self):
        if self.hue % self.hue_step == 0:
            if (self.default_hue - (self.default_hue % self.hue_step)) == self.hue and self.hue != self.default_hue:
                self.hue = self.default_hue
            else:
                self.hue = self.hue + self.hue_step
        else:
            self.hue = self.hue - (self.hue % self.hue_step) + self.hue_step
        self.hue = self.hue % 256

    def lower_saturation(self):
        self.saturation = fancy.clamp_norm(self.saturation - self.saturation_step)

    def raise_saturation(self):
        self.saturation = fancy.clamp_norm(self.saturation + self.saturation_step);

    def lower_brightness(self):
        self.brightness = fancy.clamp_norm(self.brightness - self.brightness_step)

    def raise_brightness(self):
        self.brightness = fancy.clamp_norm(self.brightness + self.brightness_step);

