import random
from typing import List

from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_selector import (
    BaseChromosomeMutationSelector,
)


class ComposedChromosomeMutationSelector(BaseChromosomeMutationSelector):
    def __init__(
        self,
        chromosome_mutation_rate_determinator: BaseChromosomeMutationRateDeterminator,
    ) -> None:
        super().__init__(chromosome_mutation_rate_determinator)
        self.selectors: List[BaseChromosomeMutationSelector] = []

    def append(self, selector: BaseChromosomeMutationSelector):
        """
        Appends selector to the composition of selectors
        """
        self.selectors.append(selector)

    def _mutate_population(self, population, max_number_of_mutation_chromosomes):
        if population is None:
            raise Exception("Population must not be null")
        if len(self.selectors) == 0:
            raise Exception("at least one mutator must be added")
        if len(self.selectors) > 1:
            random.shuffle(self.selectors)
        nmc = 0
        number_of_mutation_chromosomes = self._chromosome_mutation_rate_determinator.get_number_of_mutation_chromosomes(
            population, max_number_of_mutation_chromosomes
        )
        if number_of_mutation_chromosomes == 0:
            return 0
        for m in self.selectors:
            if nmc < number_of_mutation_chromosomes:
                mc = m._mutate_population(
                    population, number_of_mutation_chromosomes - nmc
                )
                nmc += mc
        return nmc
