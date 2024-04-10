from abc import ABC, abstractmethod
from gadapt.ga_model.ga_options import GAOptions
from gadapt.operations.cost_finding.base_cost_finder import BaseCostFinder
from gadapt.operations.crossover.base_crossover import BaseCrossover
from gadapt.operations.exit_check.base_exit_checker import BaseExitChecker
from gadapt.operations.immigration.chromosome_immigration.base_chromosome_immigrator import (
    BaseChromosomeImmigrator,
)
from gadapt.operations.immigration.population_immigration.base_population_immigrator import (
    BasePopulationImmigrator,
)
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_selector import (
    BaseGeneMutationSelector,
)
from gadapt.operations.mutation.gene_mutation.base_gene_mutator import BaseGeneMutator
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)
from gadapt.operations.parent_selection.base_parent_selector import BaseParentSelector
from gadapt.operations.gene_combination.base_gene_combination import BaseGeneCombination

"""
    Factory definition for creating  class instances based on GA options
"""


class BaseGAFactory(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.cost_finder = None
        self.population_immigrator = None
        self.chromosome_immigrator = None
        self.chromosome_mutator = None
        self.gene_mutator = None
        self.population_mutator = None
        self.parent_selector = None
        self.gene_combination = None
        self.exit_checker = None
        self.variable_updater = None
        self.crossover = None

    def initialize_factory(self, ga):
        self._ga = ga
        self._options = GAOptions(ga)

    def get_cost_finder(self) -> BaseCostFinder:
        """
        Cost Finder instance
        """
        if self.cost_finder is None:
            self.cost_finder = self._get_cost_finder()
        return self.cost_finder

    def get_population_immigrator(self) -> BasePopulationImmigrator:
        """
        Population Immigrator Instance
        """
        if self.population_immigrator is None:
            self.population_immigrator = self._get_population_immigrator()
        return self.population_immigrator

    def get_chromosome_immigrator(self) -> BaseChromosomeImmigrator:
        """
        Chromosome Immigrator Instance
        """
        if self.chromosome_immigrator is None:
            self.chromosome_immigrator = self._get_chromosome_immigrator()
        return self.chromosome_immigrator

    def get_chromosome_mutator(self) -> BaseGeneMutationSelector:
        """
        Chromosome Mutator Instance
        """
        if self.chromosome_mutator is None:
            self.chromosome_mutator = self._get_chromosome_mutator()
        return self.chromosome_mutator

    def get_gene_mutator(self) -> BaseGeneMutator:
        """
        Gene Mutator Instance
        """
        if self.gene_mutator is None:
            self.gene_mutator = self._get_gene_mutator()
        return self.gene_mutator

    def get_population_mutator(self) -> BaseChromosomeMutationRateDeterminator:
        """
        Population Mutator Instance
        """
        if self.population_mutator is None:
            self.population_mutator = self._get_population_mutator()
        return self.population_mutator

    def get_parent_selector(self) -> BaseParentSelector:
        """
        Parent Selector Instance
        """
        if self.parent_selector is None:
            self.parent_selector = self._get_parent_selector()
        return self.parent_selector

    def get_gene_combination(self) -> BaseGeneCombination:
        """
        Gene Combination Instance
        """
        if self.gene_combination is None:
            self.gene_combination = self._get_gene_combination()
        return self.gene_combination

    def get_exit_checker(self) -> BaseExitChecker:
        """
        Exit Checker Instance
        """
        if self.exit_checker is None:
            self.exit_checker = self._get_exit_checker()
        return self.exit_checker

    def get_variable_updater(self):
        """
        Variable Updater Instance
        """
        if self.variable_updater is None:
            self.variable_updater = self._get_variable_updater()
        return self.variable_updater

    def get_crossover(self) -> BaseCrossover:
        """
        Crossover Instance
        """
        if self.crossover is None:
            self.crossover = self._get_crossover()
        return self.crossover

    @abstractmethod
    def _get_cost_finder(self) -> BaseCostFinder:
        """
        Cost Finder instance
        """
        pass

    @abstractmethod
    def _get_population_immigrator(self) -> BasePopulationImmigrator:
        """
        Population Immigrator Instance
        """
        pass

    @abstractmethod
    def _get_chromosome_immigrator(self) -> BaseChromosomeImmigrator:
        """
        Chromosome Immigrator Instance
        """
        pass

    @abstractmethod
    def _get_chromosome_mutator(self) -> BaseGeneMutationSelector:
        """
        Chromosome Mutator Instance
        """
        pass

    @abstractmethod
    def _get_gene_mutator(self) -> BaseGeneMutator:
        """
        Gene Mutator Instance
        """
        pass

    @abstractmethod
    def _get_population_mutator(self) -> BaseChromosomeMutationRateDeterminator:
        """
        Population Mutator Instance
        """
        pass

    @abstractmethod
    def _get_parent_selector(self) -> BaseParentSelector:
        """
        Parent Selector Instance
        """
        pass

    @abstractmethod
    def _get_gene_combination(self) -> BaseGeneCombination:
        """
        Gene Combination Instance
        """
        pass

    @abstractmethod
    def _get_exit_checker(self) -> BaseExitChecker:
        """
        Exit Checker Instance
        """
        pass

    @abstractmethod
    def _get_variable_updater(self):
        """
        Variable Updater Instance
        """
        pass

    @abstractmethod
    def _get_crossover(self):
        """
        Crossover Instance
        """
        pass
