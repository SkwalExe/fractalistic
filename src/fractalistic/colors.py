from typing import Callable

from textual.color import Color


def get_intensity(i: int) -> int:
    return 16 * i % 255


# These colors are picked from UF6
# https://www.ultrafractal.com/
BLUE_BROWN = [
    Color(12, 4, 50),
    Color(7, 7, 76),
    Color(3, 10, 103),
    Color(15, 47, 141),
    Color(27, 85, 180),
    Color(60, 128, 212),
    Color(137, 184, 232),
    Color(214, 239, 251),
    Color(244, 236, 194),
    Color(251, 204, 97),
    Color(255, 173, 3),
    Color(207, 131, 3),
    Color(156, 90, 3),
    Color(109, 55, 6),
    Color(69, 33, 19),
    Color(28, 10, 29),
]


def blue_brown(i: int) -> Color:
    return BLUE_BROWN[i % len(BLUE_BROWN)]


def hsl_wheel(i: int) -> Color:
    return Color.from_hsl((0.0 + i / 80) % 1, 1, 0.4)


def blue(i: int) -> Color:
    return Color(0, 0, get_intensity(i))


def green(i: int) -> Color:
    return Color(0, get_intensity(i), 0)


def emerald(i: int) -> Color:
    intensity = get_intensity(i)
    return Color(0, intensity, intensity)


def red(i: int) -> Color:
    return Color(get_intensity(i), 0, 0)


def violet(i: int) -> Color:
    intensity = get_intensity(i)
    return Color(intensity, 0, intensity)


def yellow(i: int) -> Color:
    intensity = get_intensity(i)
    return Color(intensity, intensity, 0)


def gray(i: int) -> Color:
    intensity = get_intensity(i)
    return Color(intensity, intensity, intensity)


def black_and_white(_: int) -> Color:
    return Color(255, 255, 255)


basic_colors = [blue, green, emerald, red, violet, yellow, gray]

# Every color function should be referenced here
color_renderers: list[Callable] = [blue_brown, hsl_wheel, *basic_colors, black_and_white]
