import gadapt.utils.ga_utils as ga_utils

from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_rate_determinator import (
    BaseGeneMutationRateDeterminator,
)


class CrossDiversityGeneMutationRateDeterminator(BaseGeneMutationRateDeterminator):
    """
    Determines the number of mutation genes in a chromosome based on the cross diversity coefficient of the decision variables.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__()

    def _get_number_of_mutation_genes(
        self, chromosome, max_number_of_mutation_genes
    ) -> int:
        decision_variables = [g.decision_variable for g in chromosome]

        def get_mutation_rate() -> float:
            avg_rsd = ga_utils.average(
                [dv.cross_diversity_coefficient for dv in decision_variables]
            )
            if avg_rsd > 1:
                avg_rsd = 1
            if avg_rsd < 0:
                avg_rsd = 0
            return 1 - avg_rsd

        mutation_rate = get_mutation_rate()
        f_return_value = mutation_rate * float(max_number_of_mutation_genes)
        f_return_value_rounded = round(f_return_value)
        if f_return_value_rounded == 0:
            f_return_value_rounded = 1
        return f_return_value_rounded
