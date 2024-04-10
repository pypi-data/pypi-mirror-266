from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_rate_determinator import (
    BaseGeneMutationRateDeterminator,
)


class StrictGeneMutationRateDeterminator(BaseGeneMutationRateDeterminator):
    """
    Determines the strict number of mutation genes in a chromosome.
    """

    def __init__(self) -> None:
        super().__init__()

    def _get_number_of_mutation_genes(
        self, chromosome: Chromosome, max_number_of_mutation_genes
    ) -> int:
        return max_number_of_mutation_genes
