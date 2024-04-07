from abc import ABC, abstractmethod
from typing import Any


class BasePredictor(ABC):

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def predict(self, **kwargs: Any) -> Any:
        """
        Run a single prediction on the model
        """
        pass
