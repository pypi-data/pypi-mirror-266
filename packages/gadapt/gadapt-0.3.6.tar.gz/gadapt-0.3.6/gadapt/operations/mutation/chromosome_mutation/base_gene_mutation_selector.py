from abc import ABC, abstractmethod

from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_rate_determinator import (
    BaseGeneMutationRateDeterminator,
)


class BaseGeneMutationSelector(ABC):
    """
    Provides a framework for selecting and mutating genes in a chromosome.
    """

    def __init__(
        self, gene_mutation_rate_determinator: BaseGeneMutationRateDeterminator
    ):
        """
        Initializes an instance of the class by setting the gene_mutation_rate_determinator attribute.
        """
        self._gene_mutation_rate_determinator = gene_mutation_rate_determinator

    def mutate(self, c, number_of_mutation_genes: int):
        """
        Selects and mutates genes in the chromosome
        Args:
            c: Chromosome to mutate
            number_of_mutation_genes: Number of mutation genes
        """
        self._before_mutated(c)
        self._mutate_chromosome(c, number_of_mutation_genes)
        self._chromosome_mutated(c)

    @abstractmethod
    def _mutate_chromosome(self, c, number_of_mutation_genes: int):
        pass

    def _gene_mutated(self, g, c):
        c.mutated_variables_id_list.append(g.decision_variable.variable_id)

    def _chromosome_mutated(self, c):
        c.is_mutated = True
        if c.first_mutant_generation == 0:
            c.first_mutant_generation += 1
        c.last_mutant_generation = 1

    def _before_mutated(self, c):
        c.mutated_variables_id_list.clear()
