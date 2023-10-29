from gmpy2 import mpc
from ..query_config import QueryConfig
from .fractal_base import FractalBase

class Mandelbrot(FractalBase):
    """
    With U0 = 0 and c being the point in the complex plane, 
    Un+1 = Un² + c
    """
    message = None

    @staticmethod
    def get(config: QueryConfig) -> int:
        i = 0
        z = mpc(0, 0)
        while abs(z) < 2 and i < config.max_iter:
            z = z*z + config.point_in_plane
            i+=1

        if i == config.max_iter:
            return -1
        
        return i