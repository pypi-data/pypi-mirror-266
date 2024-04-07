import math
from gadapt.operations.mutation.population_mutation.base_population_mutator import (
    BasePopulationMutator,
)
import gadapt.utils.ga_utils as ga_utils
import statistics as stat


class CostDiversityPopulationMutator(BasePopulationMutator):
    """
    Population mutator based on cost diversity
    """

    def __init__(
        self,
        population_mutator_for_execution: BasePopulationMutator,
    ) -> None:
        super().__init__()
        self._population_mutator_for_execution = population_mutator_for_execution

    def _get_number_of_mutation_cromosomes(
        self, population, number_of_mutation_chromosomes
    ) -> int:
        def get_mutation_rate() -> float:            
            if not population.average_cost_step_in_first_population or math.isnan(population.average_cost_step_in_first_population):
                return 1
            cost_step_ratio = population.calculate_average_cost_step() / population.average_cost_step_in_first_population
            if cost_step_ratio > 1:
                cost_step_ratio = 1
            return  1 - cost_step_ratio

        mutation_rate = get_mutation_rate()
        f_return_value = mutation_rate * float(number_of_mutation_chromosomes)
        return round(f_return_value)

    def _mutate_population(self, population, number_of_mutation_chromosomes):
        if population is None:
            raise Exception("Population must not be null")
        current_number_of_mutation_chromosomes = (
            self._get_number_of_mutation_cromosomes(
                population, number_of_mutation_chromosomes
            )
        )
        return self._population_mutator_for_execution._mutate_population(
            population, current_number_of_mutation_chromosomes
        )
