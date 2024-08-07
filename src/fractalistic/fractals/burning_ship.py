from gmpy2 import mpc  # type: ignore

from ..settings import RenderSettings
from .fractal_base import FractalBase


class BurningShip(FractalBase):
    """
    With U0 = 0 and c being the point in the complex plane,
    Un+1 = (|Re(Un)| + i|Im(Un)|)² + c
    """

    message = None

    @staticmethod
    def get(point: mpc, settings: RenderSettings) -> int:
        i = 0
        z = mpc(0, 0)
        while abs(z) < 5 and i < settings.max_iter:
            z = mpc(abs(z.real), abs(z.imag))
            z = z.__pow__(settings.burning_ship_exponent) - point
            i += 1

        if i == settings.max_iter:
            return -1

        return i
