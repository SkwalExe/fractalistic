from ..settings import RenderSettings
from .fractal_base import FractalBase
from gmpy2 import mpc


class Julia(FractalBase):
    """
    With U0 being the point in the complex plane,
    Un+1 = Un² - 1
    """
    message = "Click a point in the complex plane to generate the corresponding Julia set."

    @staticmethod
    def get(point: mpc, settings: RenderSettings) -> int:
        i = 0

        while abs(point) < 4 and i < settings.max_iter:
            point = point*point - settings.julia_click
            i += 1

        if i == settings.max_iter:
            return -1

        return i
