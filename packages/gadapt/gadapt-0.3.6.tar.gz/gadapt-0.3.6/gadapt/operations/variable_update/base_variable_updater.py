from abc import ABC, abstractmethod


class BaseVariableUpdater(ABC):
    """
    Base class for variable update
    """

    @abstractmethod
    def update_variables(self, population):
        pass
