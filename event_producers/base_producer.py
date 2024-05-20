from abc import ABC, abstractmethod


class BaseProducer(ABC):
    @abstractmethod
    def get_producer(self):
        pass
