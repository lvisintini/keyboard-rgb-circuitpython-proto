import time
from adafruit_itertools import adafruit_itertools as itertools

from hardware_config import (
    ROW_PINS,
    COL_PINS,
    RGB_PIN,
    RGB_ORDER,
    KEYMAP,
    LAYER1,
    LED_MATRIX,
    KEY_LED_MAPPING,
    NUM_LEDS,
    NUM_KEYS,
    RGB_HUE, RGB_SATURATION, RGB_BRIGHTNESS, RGB_ON
)
from mock_firmware import Keyboard
from led_rgb import RGBController
from led_rgb_effects import EFFECTS
from utils import delay, millis

keyboard = Keyboard(ROW_PINS, COL_PINS, KEYMAP, LAYER1)

rgb_controller = RGBController(
    RGB_ON,
    NUM_LEDS,
    RGB_PIN,
    RGB_ORDER,
    KEYMAP,
    LED_MATRIX,
    KEY_LED_MAPPING,
    NUM_KEYS,
    RGB_HUE,
    RGB_SATURATION,
    RGB_BRIGHTNESS
)

rgb_controller.fill((255, 0, 0))
rgb_controller.show()
delay(1000)

RGB_MODES = itertools.cycle([effect_cls(rgb_controller) for effect_cls in EFFECTS])

current_rgb_effect = next(RGB_MODES)
current_rgb_effect.setup()


while True:
    pressed_keys = keyboard.scan()
    if pressed_keys:
        print([key.key_code for key in pressed_keys])

        current_keycodes = [key.key_code for key in pressed_keys]
        for x in current_keycodes:
            if x in ["F5", "F6"]:
                # Change RGB mode
                current_rgb_effect.tear_down()
                current_rgb_effect = next(RGB_MODES)
                current_rgb_effect.setup()
                delay(100)
            elif x in ["Esc", "F12"]:
                # Toggle RGB ON/OFF
                rgb_controller.toggle()
                delay(100)
            elif x in ["F1", "F11"]:
                # Toggle RGB ON/OFF
                rgb_controller.cycle_hue()
                delay(100)

    current_rgb_effect.process_state(keyboard)

    rgb_controller.show()


