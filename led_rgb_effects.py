import time
import math

from adafruit_itertools import adafruit_itertools as itertools
import adafruit_fancyled.adafruit_fancyled as fancy

from utils import  millis, beat8, random, constrain

from mock_firmware import NoL


class RGBEffect:
    rgb_controller = None

    def __init__(self, rgb_controller):
        self.rgb_controller = rgb_controller

    def setup(self):
        pass

    def process_state(self, keyboard):
        pass

    def tear_down(self):
        pass


class SolidRGBEffect(RGBEffect):
    def process_state(self, keyboard):
        self.rgb_controller.fill(
            fancy.CHSV(
                self.rgb_controller.hue,
                self.rgb_controller.saturation,
                self.rgb_controller.brightness
            )
        )


class StarsRGBEffect(RGBEffect):
    effect_speed = 200

    def setup(self):
        self.last_change = millis()

    def process_state(self, keyboard):
        # Fade all
        self.rgb_controller.fade_all(0.1)

        if (keyboard.current_millis - self.last_change) > self.effect_speed:
            self.rgb_controller.strip[random(0, self.rgb_controller.num_led)] = fancy.CHSV(
                self.rgb_controller.hue,
                self.rgb_controller.saturation,
                self.rgb_controller.brightness
            )
            self.last_change = millis()

        for i in range(self.rgb_controller.num_led):
                self.rgb_controller.set_led_color(i, self.rgb_controller.strip[i])



class SolidRainbowRGBEffect(RGBEffect):
    def setup(self):
        self.last_change = millis()
    def process_state(self, keyboard):
        if millis() - self.last_change > 10:
            h = beat8(8)
            color = fancy.CHSV(h,self.rgb_controller.saturation, self.rgb_controller.brightness)
            self.rgb_controller.fill(color)
            self.last_change = millis()


class ReactiveRGBEffect(RGBEffect):
    fade_time = 1000

    def setup(self):
        self.last_pass = millis()

    def process_state(self, keyboard):
        self.rgb_controller.fade_all(
            (self.rgb_controller.brightness/self.fade_time) * (millis() - self.last_pass)
        )
        for key in keyboard.keys:
            if key.is_pressed:
                self.rgb_controller.set_led_color_by_key_number(
                    key.key_number,
                    fancy.CHSV(
                        self.rgb_controller.hue,
                        self.rgb_controller.saturation,
                        self.rgb_controller.brightness
                    )
                )
        self.last_pass = millis()


class RainbowReactiveRGBEffect(RGBEffect):
    fade_time = 1000
    rainbow_effect_speed = 32;

    def setup(self):
        self.last_pass = millis()

    def process_state(self, keyboard):
        self.rgb_controller.fade_all(
            (self.rgb_controller.brightness/self.fade_time) * (millis() - self.last_pass)
        )
        for key in keyboard.keys:
            if key.is_pressed:
                self.rgb_controller.set_led_color_by_key_number(
                    key.key_number,
                    fancy.CHSV(
                        beat8(self.rainbow_effect_speed),
                        self.rgb_controller.saturation,
                        self.rgb_controller.brightness
                    )
                )
        self.last_pass = millis()


class SnakeRGBEffect(RGBEffect):
    last_change = None
    snake_head = 0
    snake_path = []
    snake_length = 1000
    effect_speed = 1

    def setup(self):
        self.rgb_controller.fill(fancy.CHSV(0, 0, 0))
        self.last_change = millis()
        self.last_pass = self.last_change
        self.snake_path = []
        self.snake_head = 0

        for row_num in range(self.rgb_controller.num_rows):
            cols_scan = list(range(self.rgb_controller.num_cols))
            if row_num % 2 != 0:
                cols_scan.reverse()
            for col_num in cols_scan:
                if self.rgb_controller.matrix[row_num][col_num] != NoL:
                    self.snake_path.append(self.rgb_controller.matrix[row_num][col_num])

    def process_state(self, keyboard):
        for i in range(self.rgb_controller.num_led):
            self.rgb_controller.strip[i].hue = self.rgb_controller.hue / 255.0
            self.rgb_controller.strip[i].saturation = self.rgb_controller.saturation

        self.rgb_controller.fade_all(
            (self.rgb_controller.brightness/self.snake_length) * (millis() - self.last_pass)
        )

        if (keyboard.current_millis - self.last_change) > self.effect_speed:
            self.snake_head = (self.snake_head + 1) % self.rgb_controller.num_led
            self.rgb_controller.set_led_brightness(self.snake_path[self.snake_head], self.rgb_controller.brightness)

        self.last_pass = millis()


class BreathingRGBEffect(RGBEffect):
    pulse = 0.5
    start_brightness = 0.1

    def process_state(self, keyboard):
        end_brightness = self.rgb_controller.brightness

        current_millis = millis()
        brightness_delta = (
            math.exp(math.sin(self.pulse * current_millis / 2000.0 * math.pi))
            - 0.36787944
        ) * ((end_brightness - self.start_brightness) / 2.35040238)

        breathing_brightness = self.start_brightness + brightness_delta
        color = fancy.CHSV(
            self.rgb_controller.hue,
            self.rgb_controller.saturation,
            breathing_brightness
        )
        self.rgb_controller.fill(color)


class ScanColsRGBEffect(RGBEffect):
    last_change = None
    last_pass = None
    effect_speed = 50
    tail_length = 750

    column = 0

    def setup(self):
        self.column = 0
        self.last_change = millis()
        self.last_pass = self.last_change
        self.rgb_controller.fill(
            fancy.CHSV(
                self.rgb_controller.hue,
                self.rgb_controller.saturation,
                0
            )
        )

    def process_state(self, keyboard):
        for i in range(self.rgb_controller.num_led):
            self.rgb_controller.strip[i].hue = self.rgb_controller.hue / 255.0
            self.rgb_controller.strip[i].saturation = self.rgb_controller.saturation


        self.rgb_controller.fade_all(
            (self.rgb_controller.brightness/self.tail_length) * (millis() - self.last_pass)
        )

        if (keyboard.current_millis - self.last_change) > self.effect_speed:
            self.column = (self.column + 1) % self.rgb_controller.num_cols

            for i in range(len(self.rgb_controller.matrix)):
                if self.rgb_controller.matrix[i][self.column] != NoL:
                    self.rgb_controller.set_led_brightness(self.rgb_controller.matrix[i][self.column], self.rgb_controller.brightness)
            self.last_change = millis()

        self.last_pass = millis()


class ScanRowsRGBEffect(RGBEffect):
    last_change = None
    last_pass = None
    effect_speed = 50
    tail_length = 450

    row = 0

    def setup(self):
        self.row = 0
        self.last_change = millis()
        self.last_pass = self.last_change
        self.rgb_controller.fill(
            fancy.CHSV(
                self.rgb_controller.hue,
                self.rgb_controller.saturation,
                0
            )
        )

    def process_state(self, keyboard):
        for i in range(self.rgb_controller.num_led):
            self.rgb_controller.strip[i].hue = self.rgb_controller.hue / 255.0
            self.rgb_controller.strip[i].saturation = self.rgb_controller.saturation


        self.rgb_controller.fade_all(
            (self.rgb_controller.brightness/self.tail_length) * (millis() - self.last_pass)
        )

        if (keyboard.current_millis - self.last_change) > self.effect_speed:
            self.row = (self.row + 1) % self.rgb_controller.num_rows

            for i in range(len(self.rgb_controller.matrix[self.row])):
                if self.rgb_controller.matrix[self.row][i] != NoL:
                    self.rgb_controller.set_led_brightness(self.rgb_controller.matrix[self.row][i], self.rgb_controller.brightness)
            self.last_change = millis()

        self.last_pass = millis()


class RainbowColsRGBEffect(RGBEffect):
    # effect_speed controls how fast the colors change
    rainbow_effect_speed = 32;

    # rainbow_rate how agressively the colors transition from one led to the next.
    # The direction of flow can be controlled with positive and negative values.
    # Absolute value of 1 mean a full rainbow is displayed at any given time.
    # Absolute values less than 1 would show only partial rainbows at any given time.
    # Absolute values greater than display that many rainbows at any given time.
    # 0 would should the all leads displaying the same color
    rainbow_rate = -0.5

    def process_state(self, keyboard):
        rainbow_hue = beat8(self.rainbow_effect_speed);

        for i in range(self.rgb_controller.num_rows):
            for j in range(self.rgb_controller.num_cols):
                if self.rgb_controller.matrix[i][j] != NoL:
                    self.rgb_controller.set_led_color(
                        self.rgb_controller.matrix[i][j],
                        fancy.CHSV(
                            int(rainbow_hue + (self.rainbow_rate * 255 / self.rgb_controller.num_cols) * j),
                            self.rgb_controller.saturation,
                            self.rgb_controller.brightness
                        )
                    )


class RainbowRowsRGBEffect(RGBEffect):
    # effect_speed controls how fast the colors change
    rainbow_effect_speed = 32;

    # rainbow_rate how agressively the colors transition from one led to the next.
    # The direction of flow can be controlled with positive and negative values.
    # Absolute value of 1 mean a full rainbow is displayed at any given time.
    # Absolute values less than 1 would show only partial rainbows at any given time.
    # Absolute values greater than display that many rainbows at any given time.
    # 0 would should the all leads displaying the same color
    rainbow_rate = -0.5

    def process_state(self, keyboard):
        rainbow_hue = beat8(self.rainbow_effect_speed);
        for i in range(self.rgb_controller.num_cols):
            for j in range(self.rgb_controller.num_rows):
                if self.rgb_controller.matrix[j][i] != NoL:
                    self.rgb_controller.set_led_color(
                        self.rgb_controller.matrix[j][i],
                        fancy.CHSV(
                            int(rainbow_hue + (self.rainbow_rate * 255 / self.rgb_controller.num_rows) * j),
                            self.rgb_controller.saturation,
                            self.rgb_controller.brightness
                        )
                    )

EFFECTS = [
    SolidRGBEffect,
    BreathingRGBEffect,
    ReactiveRGBEffect,
    StarsRGBEffect,
    SnakeRGBEffect,
    ScanColsRGBEffect,
    ScanRowsRGBEffect,
    SolidRainbowRGBEffect,
    RainbowColsRGBEffect,
    RainbowRowsRGBEffect,
    RainbowReactiveRGBEffect
]
