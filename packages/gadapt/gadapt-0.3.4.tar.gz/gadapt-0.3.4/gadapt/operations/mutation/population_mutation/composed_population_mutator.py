import random
from typing import List
from gadapt.operations.mutation.population_mutation.base_population_mutator import (
    BasePopulationMutator,
)


class ComposedPopulationMutator(BasePopulationMutator):
    def __init__(self) -> None:
        """
        Population mutator that consists of more different population mutators
        Args:
            options: genetic algorithm options
        """
        super().__init__()
        self.mutators: List[BasePopulationMutator] = []

    def append(self, mutator: BasePopulationMutator):
        """
        Appends mutator to the composition of mutators
        """
        self.mutators.append(mutator)

    def _mutate_population(self, population, number_of_mutation_chromosomes):
        if population is None:
            raise Exception("Population must not be null")
        if len(self.mutators) == 0:
            raise Exception("at least one mutator must be added")
        random.shuffle(self.mutators)
        nmc = 0
        if not self.requires_continuous_execution_in_composed_mutation():
            nmc = self.mutators[0]._mutate_population(
                    population, number_of_mutation_chromosomes - nmc
                )
        else:
            for m in self.mutators:            
                if nmc < number_of_mutation_chromosomes:
                    mc = m._mutate_population(
                        population, number_of_mutation_chromosomes - nmc
                    )
                    nmc += mc
        return nmc
    
    def requires_continuous_execution_in_composed_mutation(self):
        return all([m.requires_continuous_execution_in_composed_mutation() for m in self.mutators])
