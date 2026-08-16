from abc import ABC, abstractmethod


class Runtime(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def run(self, request):
        pass

    @abstractmethod
    def get_info(self):
        pass
