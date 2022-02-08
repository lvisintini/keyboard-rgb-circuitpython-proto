import time
import math

from adafruit_itertools import adafruit_itertools as itertools
import adafruit_fancyled.adafruit_fancyled as fancy

from utils import millis, beat8

from mock_firmware import NoL


class RGBEffect:
    rgb_controller = None

    def __init__(self, rgb_controller):
        self.rgb_controller = rgb_controller

    def setup(self):
        self.rgb_controller.leds.fill((0, 0, 0))

    def process_state(self, keyboard):
        pass

    def tear_down(self):
        pass


class SolidRGBEffect(RGBEffect):
    def process_state(self, keyboard):
        self.rgb_controller.fill(fancy.CHSV(self.rgb_controller.hue).pack())


class SolidRainbowRGBEffect(RGBEffect):
    def setup(self):
        self.last_change = millis()
    def process_state(self, keyboard):
        if millis() - self.last_change > 10:
            h = beat8(8)
            color = fancy.CHSV(h)
            self.rgb_controller.leds.fill(color.pack())
            self.last_change = millis()


class ReactiveRGBEffect1(RGBEffect):
    def process_state(self, keyboard):
        fade_time = 1500
        max_brightness = 1.0

        for key in keyboard.keys:
            since = key.get_millis_since(keyboard.current_millis)
            if key.is_pressed:
                # Currently pressed
                color = fancy.gamma_adjust(
                    fancy.CRGB(255, 0, 0), brightness=max_brightness
                )

            elif since is None:
                # Not pressed yet
                color = fancy.CRGB(0, 0, 0)  # no brightness by default

            elif since >= fade_time:
                # Pressed too long ago
                color = fancy.CRGB(0, 0, 0)  # no brightness by default

            else:
                brightness = max_brightness - (since / fade_time)
                color = fancy.gamma_adjust(fancy.CRGB(255, 0, 0), brightness=brightness)

            self.rgb_controller.set_led_value_by_key_number(key.key_number, color.pack())


class SnakeRGBEffect(RGBEffect):
    last_change = None
    snake = None
    snake_path = None
    snake_length = 6
    effect_speed = 100

    def setup(self):
        self.last_change = millis()
        snake_path = []

        flat_led_list = [
            lp for row in self.rgb_controller.matrix for lp in row if lp != NoL
        ]
        flat_led_list.reverse()

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
        self.rgb_controller.leds.fill((0, 0, 0))

        if (keyboard.current_millis - self.last_change) > self.effect_speed:
            self.snake = self.snake[1:]
            self.snake.append(next(self.snake_path))
            self.last_change = millis()

        brightness = 0
        for snake_segment in self.snake:
            brightness += 1 / self.snake_length
            color = fancy.gamma_adjust(fancy.CRGB(255, 0, 0), brightness=brightness)
            self.rgb_controller.set_led_value(snake_segment, color.pack())


class BreathingRGBEffect(RGBEffect):
    pulse = 0.5
    start_brightness = 0.1
    end_brightness = 1.0

    def process_state(self, keyboard):
        current_millis = millis()
        brightness_delta = (
            math.exp(math.sin(self.pulse * current_millis / 2000.0 * math.pi))
            - 0.36787944
        ) * ((self.end_brightness - self.start_brightness) / 2.35040238)

        breathing_brightness = self.start_brightness + brightness_delta

        color = fancy.gamma_adjust(
            fancy.CRGB(0, 255, 0), brightness=breathing_brightness
        ).pack()
        self.rgb_controller.leds.fill(color)


class ScanColsRGBEffect(RGBEffect):
    last_change = None
    effect_speed = 150
    wave_length = 5
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
        self.rgb_controller.leds.fill((0, 0, 0))

        if (keyboard.current_millis - self.last_change) > self.effect_speed:
            self.wave = self.wave[1:]
            self.wave.append(next(self.columns))
            self.last_change = millis()

        brightness = 0
        for column in self.wave:
            brightness += 1 / self.wave_length
            color = fancy.gamma_adjust(fancy.CRGB(255, 0, 0), brightness=brightness).pack()
            for led_number in column:
                self.rgb_controller.set_led_value(led_number, color)


class ScanRowsRGBEffect(RGBEffect):
    last_change = None
    effect_speed = 200
    wave_length = 3
    columns = None
    wave = None

    def setup(self):
        rows = []
        for row in self.rgb_controller.matrix:
            rows.append([r for r in row if r is not NoL])

        self.rows = itertools.cycle(rows)
        self.wave = [next(self.rows) for i in range(self.wave_length)]

        self.last_change = millis()

    def process_state(self, keyboard):
        self.rgb_controller.leds.fill((0, 0, 0))

        if (keyboard.current_millis - self.last_change) > self.effect_speed:
            self.wave = self.wave[1:]
            self.wave.append(next(self.rows))
            self.last_change = millis()

        brightness = 0
        for row in self.wave:
            brightness += 1 / self.wave_length
            color = fancy.gamma_adjust(fancy.CRGB(255, 0, 0), brightness=brightness).pack()
            for led_number in row:
                self.rgb_controller.set_led_value(led_number, color)


EFFECTS = [
    SolidRGBEffect,
    SolidRainbowRGBEffect,
    ScanRowsRGBEffect,
    ScanColsRGBEffect,
    SnakeRGBEffect,
    ReactiveRGBEffect1,
    BreathingRGBEffect,
]


# Now convert everything to HUEs -> fancy.CHSV
