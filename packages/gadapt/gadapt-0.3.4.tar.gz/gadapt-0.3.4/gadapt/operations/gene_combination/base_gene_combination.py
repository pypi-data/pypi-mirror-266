from abc import ABC, abstractmethod
from gadapt.ga_model.gene import Gene


class BaseGeneCombination(ABC):
    """
    Base class for gene combination
    """

    def combine(self, mother_gene: Gene, father_gene: Gene):
        """
        Combines two genes and returns two offsprings.
        Args:
            mother_gene (Gene): First gene to combine
            father_gene (Gene): Second gene to combine
        """
        return self._combine_genes(mother_gene, father_gene)

    @abstractmethod
    def _combine_genes(self, mother_gene: Gene, father_gene: Gene):
        pass
