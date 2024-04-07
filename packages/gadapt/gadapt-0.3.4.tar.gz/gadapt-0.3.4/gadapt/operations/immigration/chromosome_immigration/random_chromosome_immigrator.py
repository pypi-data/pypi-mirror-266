from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.immigration.chromosome_immigration.base_chromosome_immigrator import (
    BaseChromosomeImmigrator,
)


class RandomChromosomeImmigrator(BaseChromosomeImmigrator):
    """
    New immigrated chromosome with random genes
    """

    def _immigrate_chromosome(self, c: Chromosome):
        for g in c:
            g.set_random_value()
