import math
from gadapt.ga_model.gene import Gene
from gadapt.operations.mutation.gene_mutation.random_gene_mutator import (
    RandomGeneMutator,
)
from gadapt.utils.ga_utils import (
    get_rand_bool,
    normally_distributed_random,
)
import numpy as np


class NormalDistributionGeneMutator(RandomGeneMutator):
    """
    Generates random or normally distributed values.
    """

    def _make_mutated_value(self, g: Gene):
        return self._make_random_or_normally_distributed_random_value(g)

    def _execute_function_until_value_changed(self, f, g: Gene):
        current_gene_value = g.variable_value
        new_gene_value = current_gene_value
        number_of_attempts = 5
        i = 0
        while True:
            new_gene_value = f(g)
            i += 1
            if new_gene_value != current_gene_value or i >= number_of_attempts:
                break
        return new_gene_value

    def _make_random_or_normally_distributed_random_value(self, g: Gene):
        if get_rand_bool():
            return self._execute_function_until_value_changed(
                super()._make_mutated_value, g
            )
        else:
            return self._execute_function_until_value_changed(
                self._make_normally_distributed_random_value, g
            )

    def _calculate_nd_standard_deviation(self, g: Gene):
        min_std_dev = 0.05
        max_std_dev = 0.5
        std_dev_range = max_std_dev - min_std_dev
        dv_rsd = np.clip(g.decision_variable.cross_diversity_coefficient, 0, 1)
        return min_std_dev + (std_dev_range * dv_rsd)

    def _make_normally_distributed_random_value(self, g: Gene):
        curr_value = g.variable_value
        if math.isnan(curr_value):
            curr_value = g.decision_variable.make_random_value()
        range = g.decision_variable.max_value - g.decision_variable.min_value
        mean = (curr_value - g.decision_variable.min_value) / (range)
        normal_distribution_random_value = normally_distributed_random(
            mean, self._calculate_nd_standard_deviation(g), 0, 1
        )
        number_of_steps = round(
            (normal_distribution_random_value * range) / g.decision_variable.step
        )
        return (
            g.decision_variable.min_value + number_of_steps * g.decision_variable.step
        )
