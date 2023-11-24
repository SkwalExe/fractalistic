from gmpy2 import mpc
from ..settings import RenderSettings
from .fractal_base import FractalBase


class Mandelbrot(FractalBase):
    """
    With U0 = 0 and c being the point in the complex plane,
    Un+1 = Un² + c
    """
    message = None

    @staticmethod
    def get(point: mpc, settings: RenderSettings) -> int:
        i = 0
        z = mpc(0, 0)
        while abs(z) < 2 and i < settings.max_iter:
            z = z*z + point
            i += 1

        if i == settings.max_iter:
            return -1

        return i
