import board
import neopixel

from mock_firmware import NoK, NoL


class LAYOUTS:
    LEFT = "LEFT"
    RIGHT = "RIGHT"


LAYOUT = LAYOUTS.RIGHT

ROW_PINS = (
    board.P1_06,
    board.P1_04,
    board.P0_11,
    board.P1_00,
    board.P0_24,
    board.P0_22,
    board.P0_20,
)

COL_PINS = (
    board.P0_09,
    board.P0_10,
    board.P1_11,
    board.P1_13,
    board.P1_15,
    board.P0_02,
    board.P0_29,
)

RGB_PIN = board.P0_17
RGB_ORDER = neopixel.GRB
RGB_HUE = 0
RGB_SATURATION = 255
RGB_BRIGHTNESS = 1.0
RGB_ON = True

if LAYOUT == LAYOUTS.LEFT:

    def KEYMAP(
            k00, k01, k02, k03, k04, k05,
            k10, k11, k12, k13, k14, k15,
            k20, k21, k22, k23, k24, k25,
            k30, k31, k32, k33, k34, k35,
            k40, k41, k42, k43, k44, k45,
            k52, k53, k54, k55,
            k60, k61, k62, k63, k64):
        return [
            [k00,   k01,   k02,   k03,   k04,   k05,   NoK],
            [k10,   k11,   k12,   k13,   k14,   k15,   NoK],
            [k20,   k21,   k22,   k23,   k24,   k25,   NoK],
            [k30,   k31,   k32,   k33,   k34,   k35,   NoK],
            [k40,   k41,   k42,   k43,   k44,   k45,   NoK],
            [NoK,   NoK,   k52,   k53,   k54,   k55,   NoK],
            [k60,   k61,   k62,   k63,   k64,   NoK,   NoK]
        ]


    LAYER1 = [
        "F5", "F4", "F3", "F2", "F1", "Esc",
        "5", "4", "3", "2", "1", "~",
        "T", "R", "E", "W", "Q", "Tab",
        "G", "F", "D", "S", "A", "Caps",
        "B", "V", "C", "X", "Z", "Shift",
        "Win", "Fn", "Alt", "Ctrl",
        "PGDN", "END", "HOME", "PGUP", "MUTE",
    ]

    NUM_LEDS = 39

    # If not provided, we use KEYMAP instead, which assumes that LEDs are wired in the same logical sequence as the keys
    def LED_MATRIX(
            l00, l01, l02, l03, l04, l05,
            l06, l07, l08, l09, l10, l11,
            l12, l13, l14, l15, l16, l17,
            l18, l19, l20, l21, l22, l23,
            l24, l25, l26, l27, l28, l29,
            l30, l31, l32, l33,
            l34, l35, l36, l37, l38):
        return [
            [l00,   l01,   l02,   l03,   l04,   l05,   NoL],
            [l11,   l10,   l09,   l08,   l07,   l06,   NoL],
            [l12,   l13,   l14,   l15,   l16,   l17,   NoL],
            [l23,   l22,   l21,   l20,   l19,   l18,   NoL],
            [l24,   l25,   l26,   l27,   l28,   l29,   NoL],
            [NoL,   NoL,   l33,   l32,   l31,   l30,   NoL],
            [l38,   l37,   l36,   l35,   l34,   NoL,   NoL],
        ]
    KEY_LED_MAPPING = None
    NUM_KEYS = len(LAYER1) # 39


else:

    def KEYMAP(
            k00, k01, k02, k03, k04, k05, k06,
            k10, k11, k12, k13, k14, k15, k16,
            k20, k21, k22, k23, k24, k25, k26,
            k30, k31, k32, k33, k34, k35, k36,
            k40, k41, k42, k43, k44, k45, k46,
            k52, k53, k54, k55, k56,
            k60, k61, k62, k63, k64):
        return [
            [k00,   k01,   k02,   k03,   k04,   k05,   k06],
            [k10,   k11,   k12,   k13,   k14,   k15,   k16],
            [k20,   k21,   k22,   k23,   k24,   k25,   k26],
            [k30,   k31,   k32,   k33,   k34,   k35,   k36],
            [k40,   k41,   k42,   k43,   k44,   k45,   k46],
            [NoK,   NoK,   k52,   k53,   k54,   k55,   k56],
            [k64,   k63,   k62,   k61,   k60,   NoK,   NoK],
        ]

    LAYER1 = [
        "F6", "F7", "F8", "F9", "F10", "F11", "F12",
        "6", "7", "8", "9", "0", "-", "=",
        "Y", "U", "I", "O", "P", "[", "]",
        "H", "J", "K", "L", ";", "'", "\\",
        "N", "M", ",", ".", "/", "Up", "Shift",
        "Cal", "PS", "Left", "Down", "Right",
        "Enter", "Del", "Ins", "Backspace", "Space",
    ]

    NUM_LEDS = 45

    def LED_MATRIX(
            l00, l01, l02, l03, l04, l05, l06,
            l07, l08, l09, l10, l11, l12, l13,
            l14, l15, l16, l17, l18, l19, l20,
            l21, l22, l23, l24, l25, l26, l27,
            l28, l29, l30, l31, l32, l33, l34,
            l35, l36, l37, l38, l39,
            l40, l41, l42, l43, l44):
        return [
            [NoL,   NoL,   l00,   l01,   l02,   l03,   l04,   l05,  l06],
            [NoL,   NoL,   l13,   l12,   l11,   l10,   l09,   l08,  l07],
            [NoL,   NoL,   l14,   l15,   l16,   l17,   l18,   l19,  l20],
            [NoL,   NoL,   l27,   l26,   l25,   l24,   l23,   l22,  l21],
            [NoL,   NoL,   l28,   l29,   l30,   l31,   l32,   l33,  l34],
            [l42,   l41,   l40,   NoL,   l39,   l38,   l37,   l36,  l35],
            [l43,   l44,   NoL,   NoL,   NoL,   NoL,   NoL,   NoL,  NoL],
        ]

    # If the number of LEDs does not match the number of keys, then an additional macro needs to be provided to match
    # the keys to the LED
    KEY_LED_MAPPING = None
    NUM_KEYS = len(LAYER1) # 45

    def KEY_LED_MAPPING(
            k00, k01, k02, k03, k04, k05, k06,
            k10, k11, k12, k13, k14, k15, k16,
            k20, k21, k22, k23, k24, k25, k26,
            k30, k31, k32, k33, k34, k35, k36,
            k40, k41, k42, k43, k44, k45, k46,
            k52, k53, k54, k55, k56,
            k60, k61, k62, k63, k64,
            l00, l01, l02, l03, l04, l05, l06,
            l07, l08, l09, l10, l11, l12, l13,
            l14, l15, l16, l17, l18, l19, l20,
            l21, l22, l23, l24, l25, l26, l27,
            l28, l29, l30, l31, l32, l33, l34,
            l35, l36, l37, l38, l39,
            l40, l41, l42, l43, l44):
        return [
            (k00, l00),
            (k01, l01),
            (k02, l02),
            (k03, l03),
            (k04, l04),
            (k05, l05),
            (k06, l06),
            (k10, l13),
            (k11, l12),
            (k12, l11),
            (k13, l10),
            (k14, l09),
            (k15, l08),
            (k16, l07),
            (k20, l14),
            (k21, l15),
            (k22, l16),
            (k23, l17),
            (k24, l18),
            (k25, l19),
            (k26, l20),
            (k30, l27),
            (k31, l26),
            (k32, l25),
            (k33, l24),
            (k34, l23),
            (k35, l22),
            (k36, l21),
            (k40, l28),
            (k41, l29),
            (k42, l30),
            (k43, l31),
            (k44, l32),
            (k45, l33),
            (k46, l34),
            (k52, l39),
            (k53, l38),
            (k54, l37),
            (k55, l36),
            (k56, l35),
            (k60, l40),
            (k61, l41),
            (k62, l42),
            (k63, l43),
            (k64, l44),
        ]
