from abc import ABC, abstractmethod


class IEvent(ABC):

    @property
    @abstractmethod
    def event_type(self):
        pass

    @property
    @abstractmethod
    def event_name(self):
        pass

    @abstractmethod
    def on_start(self, *args, **kwargs):
        pass

    @abstractmethod
    def on_execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def on_end(self, *args, **kwargs):
        pass


class BaseCallbackHandler(ABC):
    @abstractmethod
    def handle(self, *args, **kwargs):
        pass
