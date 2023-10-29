from ..query_config import QueryConfig
from .fractal_base import FractalBase
from gmpy2 import mpc

class Julia(FractalBase):
    """
    With U0 being the point in the complex plane, 
    Un+1 = Un² - 1
    """
    message = "Click a point in the complex plane to generate the corresponding Julia set."
    
    @staticmethod
    def get(config: QueryConfig) -> int:
        i = 0
        n = config.point_in_plane

        while abs(n) < 4 and i < config.max_iter:
            n = n*n - config.julia_click
            i+=1

        if i == config.max_iter:
            return -1
        
        return i