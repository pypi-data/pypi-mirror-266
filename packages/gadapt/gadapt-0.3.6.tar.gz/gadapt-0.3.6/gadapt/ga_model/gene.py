"""
Gene
"""

import math
from gadapt.ga_model.decision_variable import DecisionVariable
from gadapt.ga_model.ranking_model import RankingModel
import gadapt.adapters.string_operation.ga_strings as ga_strings
import gadapt.ga_model.definitions as definitions


class Gene(RankingModel):
    def __init__(self, gen_variable, var_value=None):
        """
        Gene class. Gene is a part of chromosome.
        It contains concrete values for decision variables.
        Args:
            gen_variable: Decision variable which defines the gene
            var_value: Value of the gene
        """
        super().__init__()
        self.decision_variable = gen_variable
        self.variable_value = var_value
        self._rank = -1
        self._cummulative_probability = definitions.FLOAT_NAN
        if self.variable_value is None or math.isnan(self.variable_value):
            self.set_random_value()

    def __str__(self) -> str:
        return self._to_string()

    def _to_string(self):
        return ga_strings.gene_to_string(self)

    @property
    def decision_variable(self) -> DecisionVariable:
        """
        Decision variable which defines the gene
        """
        return self._decision_variable

    @decision_variable.setter
    def decision_variable(self, value: DecisionVariable):
        if not isinstance(value, DecisionVariable):
            pass
            raise
        self._decision_variable = value

    @property
    def variable_value(self):
        """
        Value of the gene
        """
        return self._variable_value

    @variable_value.setter
    def variable_value(self, value):
        self._variable_value = value

    def mutate(self):
        self.decision_variable.gene_mutator.mutate(self)

    def set_random_value(self):
        """
        Sets a random value for the variable_value property
        """
        self.variable_value = self.decision_variable.make_random_value()
