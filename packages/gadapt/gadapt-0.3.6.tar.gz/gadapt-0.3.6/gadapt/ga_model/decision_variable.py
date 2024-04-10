"""
Decision variable
"""

import random
import gadapt.ga_model.definitions as definitions


class DecisionVariable:
    def __init__(self, id: int) -> None:
        """
        Decision variable class defines genes.
        Each gene has a reference to one decision variable.
        Decision variable contains common values for genes: variable id, maximal\
            value, minimal value, step.
        Args:
            id (int): identifier of the decision variable
        """
        self.variable_id = id
        self._standard_deviation = definitions.FLOAT_NAN
        self._gene_mutator = None
        self._initial_st_dev = -1.0

    def __eq__(self, other):
        if not isinstance(other, DecisionVariable):
            return False
        return self.variable_id == other.variable_id

    def __hash__(self) -> int:
        return self.variable_id

    @property
    def variable_id(self) -> int:
        """
        Unique ID for decision variable
        """
        return self._variable_id

    @variable_id.setter
    def variable_id(self, value: int):
        self._variable_id = value

    @property
    def max_value(self) -> float:
        """
        Max gene value
        """
        return self._max_value

    @max_value.setter
    def max_value(self, value: float):
        self._max_value = value

    @property
    def min_value(self) -> float:
        """
        Min gene value
        """
        return self._min_value

    @min_value.setter
    def min_value(self, value: float):
        self._min_value = value

    @property
    def step(self) -> float:
        """
        Optimization step
        """
        return self._step

    @step.setter
    def step(self, value: float):
        self._decimal_places = self._get_decimal_places(value)
        self._step = value

    def _get_decimal_places(self, num):
        num_str = str(num)
        if "e-" in num_str:
            num_str = num_str.split("e-")[-1]
            return int(num_str)
        if "." in num_str:
            _, fractional_part = num_str.split(".")
            return len(fractional_part)
        else:
            return 0

    @property
    def decimal_places(self) -> int:
        """
        Number of decimal places of the gene value
        """
        return self._decimal_places

    @property
    def stacked(self) -> bool:
        """
        Indicates if all genes have the same value for the same decision variable
        """
        return self._stacked

    @stacked.setter
    def stacked(self, value: bool):
        self._stacked = value

    @property
    def cross_diversity_coefficient(self) -> float:
        """
        Relative standard deviation of all genes for the same decision variable
        """
        return self._standard_deviation

    @cross_diversity_coefficient.setter
    def cross_diversity_coefficient(self, value: float):
        self._standard_deviation = value

    @property
    def gene_mutator(self):
        return self._gene_mutator

    @gene_mutator.setter
    def gene_mutator(self, value):
        self._gene_mutator = value

    def make_random_value(self):
        """
        Makes random value, based on min value, max value, and step
        """
        number_of_steps = random.randint(
            0, round((self.max_value - self.min_value) / self.step)
        )
        return self.min_value + number_of_steps * self.step

    @property
    def initial_st_dev(self) -> float:
        return self._initial_st_dev

    @initial_st_dev.setter
    def initial_st_dev(self, value: float):
        self._initial_st_dev = value
