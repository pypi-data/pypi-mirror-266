import random
from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)
from gadapt.operations.sampling.base_sampling import BaseSampling
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_selector import (
    BaseChromosomeMutationSelector,
)


class ParentDiversityChromosomeMutationSelector(BaseChromosomeMutationSelector):
    """
    Selects and mutates chromosomes in a population based on their parent diversity.
    """

    def __init__(
        self,
        chromosome_mutation_rate_determinator: BaseChromosomeMutationRateDeterminator,
        sampling: BaseSampling,
    ) -> None:
        super().__init__(chromosome_mutation_rate_determinator)
        self._sampling = sampling

    def _sort_key_parent_diversity_random(self, c: Chromosome):
        return (c.parent_diversity, random.random())

    def _mutate_population(self, population, max_number_of_mutation_chromosomes):
        if population is None:
            raise Exception("Population must not be null")
        number_of_mutation_chromosomes = self._chromosome_mutation_rate_determinator.get_number_of_mutation_chromosomes(
            population, max_number_of_mutation_chromosomes
        )
        unallocated_chromosomes: list[Chromosome] = self._get_unallocated_chromosomes(
            population, self._sort_key_parent_diversity_random
        )
        chromosomes_for_mutation: list[Chromosome] = []
        if population.options.must_mutate_for_same_parents:
            chromosomes_for_mutation = [
                c for c in unallocated_chromosomes if c.parent_diversity == 0
            ]
        chromosomes_for_mutation_count = len(chromosomes_for_mutation)
        rest_number = number_of_mutation_chromosomes - chromosomes_for_mutation_count
        if rest_number > 0:
            if population.options.must_mutate_for_same_parents:
                chromosomes_for_mutation = [
                    c for c in unallocated_chromosomes if (not c.parent_diversity == 0)
                ]
            else:
                chromosomes_for_mutation = [c for c in unallocated_chromosomes]
            chromosomes_for_mutation = self._sampling.get_sample(
                chromosomes_for_mutation, rest_number, lambda c: c.parent_diversity
            )
        for c in chromosomes_for_mutation:
            c.mutate(population.options.number_of_mutation_genes)
        return len(chromosomes_for_mutation)
