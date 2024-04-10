import random
from typing import List

from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_rate_determinator import (
    BaseGeneMutationRateDeterminator,
)


class ComposedGeneMutationRateDeterminator(BaseGeneMutationRateDeterminator):
    """
    Provides a way to combine multiple gene mutation rate determinators into a single determinator. It randomly selects one of the determinators to determine the number of mutation genes in a chromosome.
    """

    def __init__(self) -> None:
        super().__init__()
        self.determinators: List[BaseGeneMutationRateDeterminator] = []

    def append(self, determinator: BaseGeneMutationRateDeterminator):
        """
        Adds a gene mutation rate determinator to the list of determinators.
        Args:
            determinator: A BaseGeneMutationRateDeterminator object representing a gene mutation rate determinator.
        """
        self.determinators.append(determinator)

    def _get_number_of_mutation_genes(self, chromosome, max_number_of_mutation_genes):
        if chromosome is None:
            raise Exception("Chromosome must not be null")
        if len(self.determinators) == 0:
            raise Exception("at least one mutator must be added")
        if len(self.determinators) > 1:
            random.shuffle(self.determinators)
        current_determinator = self.determinators[0]
        return current_determinator.get_number_of_mutation_genes(
            chromosome, max_number_of_mutation_genes
        )
