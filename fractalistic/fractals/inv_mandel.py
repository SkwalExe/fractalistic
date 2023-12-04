from gmpy2 import mpc
from ..settings import RenderSettings
from .fractal_base import FractalBase


class InverseMandelbrot(FractalBase):
    """
    With U0 = 0 and c being the point in the complex plane,
    Un+1 = b/(Un² + c)
    """
    message = "The inverse mandelbrot uses your configured mandelbrot values."

    @staticmethod
    def get(point: mpc, settings: RenderSettings) -> int:
        i = 0
        z = settings.mandelbrot_starting_value
        while abs(z) < 2 and i < settings.max_iter:
            z = settings.inv_mandel_numerator/(z.__pow__(settings.mandelbrot_exponent) + point)
            i += 1

        if i == settings.max_iter:
            return -1

        return i
