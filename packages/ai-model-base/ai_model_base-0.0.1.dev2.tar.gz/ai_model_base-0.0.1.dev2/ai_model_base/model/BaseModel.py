from abc import ABC, abstractmethod


class BaseModel(ABC):

    def get_model_name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def get_model_path(self) -> str:
        pass

    @abstractmethod
    def startup(self) -> None:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass
