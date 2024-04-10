from gadapt.ga_model.population import Population
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)
import gadapt.utils.ga_utils as ga_utils


class CrossDiversityChromosomeMutationRateDeterminator(
    BaseChromosomeMutationRateDeterminator
):
    """
    Determining the number of chromosomes to be mutated in a population based on the cross-diversity coefficient of the decision variables.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__()

    def _get_number_of_mutation_chromosomes(
        self, population: Population, max_number_of_mutation_chromosomes
    ) -> int:
        def get_mutation_rate() -> float:
            avg_rsd = ga_utils.average(
                [
                    dv.cross_diversity_coefficient
                    for dv in population.options.decision_variables
                ]
            )
            if avg_rsd > 1:
                avg_rsd = 1
            if avg_rsd < 0:
                avg_rsd = 0
            return 1 - avg_rsd

        mutation_rate = get_mutation_rate()
        f_return_value = mutation_rate * float(max_number_of_mutation_chromosomes)
        return round(f_return_value)
