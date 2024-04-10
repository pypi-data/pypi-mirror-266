from abc import ABC, abstractmethod
from gadapt.ga_model.gene import Gene


class BaseGeneMutator(ABC):
    """
    Mutates the variable value of a gene.
    """

    def __init__(self) -> None:
        pass

    def mutate(self, g: Gene):
        g.variable_value = self._make_mutated_value(g)

    @abstractmethod
    def _make_mutated_value(self, g: Gene):
        pass
