import math
from gadapt.ga_model.population import Population
from gadapt.operations.mutation.population_mutation.base_population_mutator import (
    BasePopulationMutator,
)
import gadapt.utils.ga_utils as ga_utils
import statistics as stat


class CrossDiversityPopulationMutator(BasePopulationMutator):
    """
    Population mutator based on cross diversity
    """

    def __init__(
        self,
        population_mutator_for_execution: BasePopulationMutator,
    ) -> None:
        super().__init__()
        self._population_mutator_for_execution = population_mutator_for_execution

    def _get_number_of_mutation_cromosomes(
        self, population: Population, number_of_mutation_chromosomes
    ) -> int:
        def get_mutation_rate() -> float:
            avg_rsd = ga_utils.average([dv.cross_diversity_coefficient for dv in population.options.decision_variables])
            if avg_rsd > 1:
                avg_rsd = 1
            if avg_rsd < 0:
                avg_rsd = 0
            return 1 - avg_rsd

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
