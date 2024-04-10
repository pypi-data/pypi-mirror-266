from gadapt.ga_model.chromosome import Chromosome
import random
from gadapt.operations.mutation.chromosome_mutation.random_gene_mutation_selector import (
    RandomGeneMutationSelector,
)
from gadapt.operations.sampling.base_sampling import BaseSampling
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_rate_determinator import (
    BaseGeneMutationRateDeterminator,
)


class CrossDiversityGeneMutationSelector(RandomGeneMutationSelector):
    """
    Selects and mutates a chromosome based on the cross diversity of decision variables in the population.
    """

    def __init__(
        self,
        gene_mutation_rate_determinator: BaseGeneMutationRateDeterminator,
        sampling: BaseSampling,
    ) -> None:
        super().__init__(gene_mutation_rate_determinator)
        self._sampling = sampling

    def _mutate_chromosome(self, c: Chromosome, max_number_of_mutation_genes: int):
        if max_number_of_mutation_genes == 0:
            return
        x_genes = [g for g in c]
        x_genes.sort(key=lambda g: -g.decision_variable.cross_diversity_coefficient)
        number_of_mutation_genes = (
            self._gene_mutation_rate_determinator.get_number_of_mutation_genes(
                c, max_number_of_mutation_genes
            )
        )
        if number_of_mutation_genes > len(x_genes):
            number_of_mutation_genes = len(x_genes)
        if number_of_mutation_genes == 0:
            max_number_of_mutation_genes = 0
        else:
            max_number_of_mutation_genes = random.randint(1, number_of_mutation_genes)
        genes_for_mutation = self._sampling.get_sample(
            x_genes,
            max_number_of_mutation_genes,
            lambda g: g.decision_variable.cross_diversity_coefficient,
        )
        for g in genes_for_mutation:
            g.mutate()
            self._gene_mutated(g, c)
        return len(genes_for_mutation)
