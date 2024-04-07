from gadapt.ga_model.chromosome import Chromosome
import random
from gadapt.operations.mutation.chromosome_mutation.random_chromosome_mutator import (
    RandomChromosomeMutator,
)
from gadapt.operations.sampling.base_sampling import BaseSampling


class CrossDiversityChromosomeMutator(RandomChromosomeMutator):
    """
    Mutation of chromosome based on cross diversity of genetic\
        variables in the population.
    """

    def __init__(self, sampling: BaseSampling) -> None:
        super().__init__()
        self._sampling = sampling

    def _mutate_chromosome(self, c: Chromosome, number_of_mutation_genes: int):
        if number_of_mutation_genes == 0:
            return
        x_genes = [g for g in c]
        x_genes.sort(key=lambda g: -g.decision_variable.cross_diversity_coefficient)
        if number_of_mutation_genes > len(x_genes):
            number_of_mutation_genes = len(x_genes)
        number_of_mutation_genes = random.randint(1, number_of_mutation_genes)
        genes_for_mutation = self._sampling.get_sample(
            x_genes,
            number_of_mutation_genes,
            lambda g: g.decision_variable.cross_diversity_coefficient,
        )
        for g in genes_for_mutation:
            g.mutate()
            self._gene_mutated(g, c)
