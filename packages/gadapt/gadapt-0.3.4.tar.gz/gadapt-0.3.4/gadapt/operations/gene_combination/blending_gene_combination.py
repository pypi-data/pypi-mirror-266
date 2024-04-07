import random
from gadapt.ga_model.gene import Gene
from gadapt.operations.gene_combination.base_gene_combination import BaseGeneCombination


class BlendingGeneCombination(BaseGeneCombination):
    """
    Blending gene combination combines
    gene values from the two parents into new variable values in offsprings.
    One value of the offspring variable comes from a combination of the two
    corresponding values of the parental genes
    """

    def _combine_genes(self, mother_gene: Gene, father_gene: Gene):
        decision_variable = father_gene.decision_variable
        val_father = father_gene.variable_value
        val_mother = mother_gene.variable_value
        x = 1
        if val_mother > val_father:
            x = -1
        beta_steps = random.randint(
            0, round(abs((val_father - val_mother) / decision_variable.step))
        )
        val1 = round(
            val_father - (beta_steps * x) * decision_variable.step,
            decision_variable.decimal_places,
        )
        val2 = round(
            val_mother + (beta_steps * x) * decision_variable.step,
            decision_variable.decimal_places,
        )
        return val1, val2
