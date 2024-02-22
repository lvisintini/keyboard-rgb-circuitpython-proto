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
                self.rgb_controller.set_led_value(i, self.rgb_controller.strip[i])



class SolidRainbowRGBEffect(RGBEffect):
    def setup(self):
        self.last_change = millis()
    def process_state(self, keyboard):
        if millis() - self.last_change > 10:
            h = beat8(8)
            color = fancy.CHSV(h,self.rgb_controller.saturation, self.rgb_controller.brightness)
            self.rgb_controller.fill(color)
            self.last_change = millis()


class ReactiveRGBEffect1(RGBEffect):
    def process_state(self, keyboard):
        fade_time = 1500
        max_brightness = self.rgb_controller.brightness

        for key in keyboard.keys:
            since = key.get_millis_since(keyboard.current_millis)
            if key.is_pressed:
                # Currently pressed
                color = fancy.CHSV(
                    self.rgb_controller.hue,
                    self.rgb_controller.saturation,
                    self.rgb_controller.brightness
                )

            elif since is None:
                # Not pressed yet
                color = fancy.CHSV(0, 0, 0)  # no brightness by default

            elif since >= fade_time:
                # Pressed too long ago
                color = fancy.CHSV(0, 0, 0)  # no brightness by default

            else:
                brightness = max_brightness - (since / fade_time)
                color = fancy.CHSV(self.rgb_controller.hue, self.rgb_controller.saturation, brightness)

            self.rgb_controller.set_led_value_by_key_number(key.key_number, color)


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


class RainbowColsRGBEffect(RGBEffect):
    last_change = None
    effect_speed = 150
    wave_length = 9
    columns = None
    wave = None

    def setup(self):
        columns = []
        for col_num in range(self.rgb_controller.num_cols):
            column = []
            for row_num in range(self.rgb_controller.num_rows):
                led_number = self.rgb_controller.matrix[row_num][col_num]
                if led_number != NoL:
                    column.append(led_number)

            columns.append(column)

        self.columns = itertools.cycle(columns)
        self.wave = [next(self.columns) for i in range(self.wave_length)]

        self.last_change = millis()

    def process_state(self, keyboard):

        self.rgb_controller.fill(fancy.CHSV(0, 0, 0))

        if (keyboard.current_millis - self.last_change) > self.effect_speed:
            self.wave = self.wave[1:]
            self.wave.append(next(self.columns))
            self.last_change = millis()

        for column in self.wave:
            color = fancy.CHSV(beat8(64), self.rgb_controller.saturation, self.rgb_controller.brightness)

            for led_number in column:
                self.rgb_controller.set_led_value(led_number, color)


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




class SnakeRGBEffect2(RGBEffect):
    last_change = None
    snake = None
    snake_path = None
    snake_length = 6
    effect_speed = 100

    def setup(self):
        self.last_change = millis()
        snake_path = []

        for row_num in range(self.rgb_controller.num_rows):
            cols_scan = list(range(self.rgb_controller.num_cols))
            if row_num % 2 != 0:
                cols_scan.reverse()
            for col_num in cols_scan:
                if self.rgb_controller.matrix[row_num][col_num] != NoL:
                    snake_path.append(self.rgb_controller.matrix[row_num][col_num])

        self.snake_path = itertools.cycle(snake_path)
        self.snake = [next(self.snake_path) for i in range(self.snake_length)]

    def process_state(self, keyboard):
        max_brightness = self.rgb_controller.brightness

        self.rgb_controller.fill(fancy.CHSV(0, 0, 0))

        if (keyboard.current_millis - self.last_change) > self.effect_speed:
            self.snake = self.snake[1:]
            self.snake.append(next(self.snake_path))
            self.last_change = millis()

        brightness = 0
        for snake_segment in self.snake:
            brightness += max_brightness / self.snake_length
            color = fancy.CHSV(
                self.rgb_controller.hue,
                self.rgb_controller.saturation,
                brightness
            )
            self.rgb_controller.set_led_value(snake_segment, color)

EFFECTS = [
    SnakeRGBEffect,
    SnakeRGBEffect2,
    SolidRGBEffect,
    BreathingRGBEffect,
    ReactiveRGBEffect1,
    StarsRGBEffect,
    SnakeRGBEffect,
    ScanColsRGBEffect,
    ScanRowsRGBEffect,
    SolidRainbowRGBEffect,
    RainbowColsRGBEffect,
]
