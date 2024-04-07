from abc import ABC, abstractmethod


class BasePopulationImmigrator(ABC):
    """
    Base class for population immigration
    """

    def immigrate(self, population):
        """
        Immigrates chromosomes into the population
        Args:
            population: Population to immigrate new chromosomes
        """
        self._immigrate_population(population)

    @abstractmethod
    def _immigrate_population(self, population):
        pass
