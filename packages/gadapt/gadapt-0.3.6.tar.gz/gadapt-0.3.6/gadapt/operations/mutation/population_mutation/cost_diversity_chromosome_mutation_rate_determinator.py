import math
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)


class CostDiversityChromosomeMutationRateDeterminator(
    BaseChromosomeMutationRateDeterminator
):
    """
    Determines the number of chromosomes to be mutated in a population based on the cost diversity of the population.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__()

    def _get_number_of_mutation_chromosomes(
        self, population, max_number_of_mutation_chromosomes
    ) -> int:
        def get_mutation_rate() -> float:
            if not population.average_cost_step_in_first_population or math.isnan(
                population.average_cost_step_in_first_population
            ):
                return 1
            cost_step_ratio = (
                population.calculate_average_cost_step()
                / population.average_cost_step_in_first_population
            )
            if cost_step_ratio > 1:
                cost_step_ratio = 1
            return 1 - cost_step_ratio

        mutation_rate = get_mutation_rate()
        f_return_value = mutation_rate * float(max_number_of_mutation_chromosomes)
        return round(f_return_value)
