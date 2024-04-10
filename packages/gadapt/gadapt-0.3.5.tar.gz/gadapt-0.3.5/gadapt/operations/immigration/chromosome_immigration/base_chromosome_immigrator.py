from abc import ABC, abstractmethod


class BaseChromosomeImmigrator(ABC):
    """
    Base class for chromosome immigration
    """

    def immigrate(self, c):
        """
        Makes one chromosome immigrant
        Args:
            c: chromosome to become the immigrant
        """
        self._immigrate_chromosome(c)
        self._chromosome_immigrated(c)

    @abstractmethod
    def _immigrate_chromosome(self, c):
        pass

    def _chromosome_immigrated(self, c):
        c.is_immigrant = True
        if c.first_immigrant_generation == 0:
            c.first_immigrant_generation += 1
        c.last_immigrant_generation = 1
        c.first_mutant_generation = 0
        c.last_mutant_generation = 0
        c.set_chromosome_string_none()
