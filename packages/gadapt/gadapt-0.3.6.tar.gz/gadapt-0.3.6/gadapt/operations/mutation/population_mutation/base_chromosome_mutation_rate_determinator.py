from abc import ABC, abstractmethod


class BaseChromosomeMutationRateDeterminator(ABC):
    """
    Provides a framework for determining the number of chromosomes to be mutated in a population.
    """

    def __init__(self) -> None:
        super().__init__()

    def get_number_of_mutation_chromosomes(
        self, population, max_number_of_mutation_chromosomes
    ):
        if population is None:
            raise Exception("Population must not be null")
        return self._get_number_of_mutation_chromosomes(
            population, max_number_of_mutation_chromosomes
        )

    @abstractmethod
    def _get_number_of_mutation_chromosomes(
        self, population, max_number_of_mutation_chromosomes
    ) -> int:
        pass
