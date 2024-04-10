from abc import ABC, abstractmethod


class BaseNotification(ABC):

    @abstractmethod
    def send_text(self, txt: str):
        pass

    @abstractmethod
    def send_markdown(self, *args, **kwargs):
        pass
