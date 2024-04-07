from gadapt.ga_model.gene import Gene
from gadapt.operations.mutation.gene_mutation.base_gene_mutator import BaseGeneMutator


class RandomGeneMutator(BaseGeneMutator):

    def _make_mutated_value(self, g: Gene):
        return round(
            g.decision_variable.make_random_value(), g.decision_variable.decimal_places
        )
