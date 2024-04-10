import random
from typing import List

from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)


class ComposedChromosomeMutationRateDeterminator(
    BaseChromosomeMutationRateDeterminator
):
    """
    Allows for the composition of multiple determinators to be used in a random order.
    """

    def __init__(self) -> None:
        super().__init__()
        self.determinators: List[BaseChromosomeMutationRateDeterminator] = []

    def append(self, determinator: BaseChromosomeMutationRateDeterminator):
        """
        Appends determinator to the composition of determinators
        """
        self.determinators.append(determinator)

    def _get_number_of_mutation_chromosomes(
        self, population, max_number_of_mutation_chromosomes
    ):
        if population is None:
            raise Exception("Population must not be null")
        if len(self.determinators) == 0:
            raise Exception("at least one mutator must be added")
        if len(self.determinators) > 1:
            random.shuffle(self.determinators)
        current_determinator = self.determinators[0]
        return current_determinator.get_number_of_mutation_chromosomes(
            population, max_number_of_mutation_chromosomes
        )
