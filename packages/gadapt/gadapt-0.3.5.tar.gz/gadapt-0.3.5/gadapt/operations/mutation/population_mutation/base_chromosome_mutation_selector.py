from abc import ABC, abstractmethod
import math
import random
from typing import List
from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)


class BaseChromosomeMutationSelector(ABC):
    """
    Selects and mutates the chromosomes in the population based on a specified number of mutated chromosomes.
    """

    def mutate(self, population):
        """
        Mutates chromosomes in the population
        Args:
            population: Population to mutate
        """
        number_of_mutated_chromosomes = (
            population.options.number_of_mutation_chromosomes
        )
        self._mutate_population(population, number_of_mutated_chromosomes)

    def __init__(
        self,
        chromosome_mutation_rate_determinator: BaseChromosomeMutationRateDeterminator,
    ) -> None:
        """
        Base class for mutating chromosomes in population
        Args:
            options: genetic algorithm options
        """
        super().__init__()
        self._chromosome_mutation_rate_determinator = (
            chromosome_mutation_rate_determinator
        )

    @abstractmethod
    def _mutate_population(self, population, number_of_mutated_chromosomes):
        pass

    def _get_unallocated_chromosomes(
        self, population, sort_key_function=None
    ) -> List[Chromosome]:
        def unallocated_chromosomes_condition(c: Chromosome) -> bool:
            return (
                math.isnan(c.cost_value)
                and (not c.is_immigrant)
                and c.population_generation == population.population_generation
                and not c.is_mutated
            )

        lst = [c for c in population if (unallocated_chromosomes_condition(c))]
        if sort_key_function is not None:
            lst.sort(key=sort_key_function)
        return lst

    def _sort_key_random(self, c: Chromosome):
        return random.random()
