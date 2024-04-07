from typing import Tuple
from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.crossover.base_crossover import BaseCrossover
from gadapt.ga_model.gene import Gene
from gadapt.operations.immigration.chromosome_immigration.base_chromosome_immigrator import (
    BaseChromosomeImmigrator,
)
from gadapt.operations.mutation.chromosome_mutation.base_chromosome_mutator import (
    BaseChromosomeMutator,
)
from gadapt.operations.gene_combination.base_gene_combination import BaseGeneCombination


class UniformCrossover(BaseCrossover):
    """
    Uniform Crossover.
    Genes from parents' chromosomes are combined in a uniform way
    """

    def __init__(
        self,
        var_combination: BaseGeneCombination,
        mutator: BaseChromosomeMutator,
        immigrator: BaseChromosomeImmigrator,
    ):
        super(UniformCrossover, self).__init__(var_combination, mutator, immigrator)

    def _get_mother_father_genes(
        self, mother: Chromosome, father: Chromosome
    ) -> Tuple[Gene, Gene]:
        father_gene = father[self._current_gene_number]
        mother_gene = mother[self._current_gene_number]
        return mother_gene, father_gene

    def _combine(self, mother_gene: Gene, father_gene: Gene):
        if self._gene_combination is None:
            raise Exception("gene_combination must not be null!")
        return self._gene_combination.combine(mother_gene, father_gene)
