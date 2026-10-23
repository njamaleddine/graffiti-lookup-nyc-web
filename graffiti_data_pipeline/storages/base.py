from abc import ABC, abstractmethod


class Storage(ABC):
    """
    Abstract base class for storage implementations.
    """

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def load(self) -> list[dict]:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def save(self, service_requests: list[dict]):
        raise NotImplementedError("Subclasses must implement this method.")
