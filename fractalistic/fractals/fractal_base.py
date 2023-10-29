from abc import ABC, abstractmethod
from ..query_config import QueryConfig

class FractalBase(ABC):
    """Base class for fractals."""
    
    message: str | None

    @staticmethod
    @abstractmethod
    def get(config: QueryConfig) -> int:
        """Returns the number of iterations required to classify a point as convergent (or -1 if it diverges)."""
        pass

