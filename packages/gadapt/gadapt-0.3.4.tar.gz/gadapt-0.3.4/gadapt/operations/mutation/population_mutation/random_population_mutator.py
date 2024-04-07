from gadapt.operations.mutation.population_mutation.base_population_mutator import (
    BasePopulationMutator,
)


class RandomPopulationMutator(BasePopulationMutator):
    """
    Random population mutator
    """

    def __init__(self) -> None:
        super().__init__()

    def _mutate_population(self, population, number_of_mutation_chromosomes):
        if population is None:
            raise Exception("population must not be None")
        number_of_mutation_genes = population.options.number_of_mutation_genes
        unallocated_chromosomes = self._get_unallocated_chromosomes(
            population, self._sort_key_random
        )
        chromosomes_for_mutation = unallocated_chromosomes[
            :number_of_mutation_chromosomes
        ]
        for c in chromosomes_for_mutation:
            c.mutate(number_of_mutation_genes)
        return number_of_mutation_chromosomes

    def requires_continuous_execution_in_composed_mutation(self) -> bool:
        return True