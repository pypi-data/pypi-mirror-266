"""
Population
"""

import math
from typing import List, Tuple
from gadapt.operations.exit_check.base_exit_checker import BaseExitChecker
from gadapt.operations.cost_finding.base_cost_finder import BaseCostFinder
from gadapt.operations.crossover.base_crossover import BaseCrossover
from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.ga_options import GAOptions
from gadapt.ga_model.gene import Gene
from gadapt.operations.immigration.chromosome_immigration.base_chromosome_immigrator import (
    BaseChromosomeImmigrator,
)
from gadapt.operations.immigration.population_immigration.base_population_immigrator import (
    BasePopulationImmigrator,
)
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_selector import (
    BaseGeneMutationSelector,
)
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)
from gadapt.operations.parent_selection.base_parent_selector import BaseParentSelector
from gadapt.operations.variable_update.base_variable_updater import BaseVariableUpdater
import gadapt.adapters.string_operation.ga_strings as ga_strings
from datetime import datetime
import gadapt.ga_model.definitions as definitions
import gadapt.utils.ga_utils as ga_utils


class Population:
    def __init__(
        self,
        options: GAOptions,
        chromosome_mutator: BaseGeneMutationSelector,
        population_mutator: BaseChromosomeMutationRateDeterminator,
        exit_checker: BaseExitChecker,
        cost_finder: BaseCostFinder,
        population_immigrator: BasePopulationImmigrator,
        chromosome_immigrator: BaseChromosomeImmigrator,
        parent_selector: BaseParentSelector,
        crossover: BaseCrossover,
        variable_updater: BaseVariableUpdater,
    ):
        """Population for the genetic algorithm. It contains a collection of\
            chromosomes, as well as additional parameters

        Args:

            options (GAOptions): Genetic Algorithm Options
            chromosome_mutator (BaseGeneMutationSelector): Chromosome Mutator Instance
            population_mutator (BaseChromosomeMutationRateDeterminator): Population Mutator Instance
            exit_checker (BaseExitChecker): Exit Checker Instance
            cost_finder (BaseCostFinder): Cost Finder Instance
            population_immigrator (BasePopulationImmigrator):
            Population Immigrator Instance
            chromosome_immigrator (BaseChromosomeImmigrator):
            Chromosome Immigrator Instance
            parent_selector (BaseParentSelector): Parent Selector Instance
            crossover (BaseCrossover): Crossover Instance
            variable_updater (BaseVariableUpdater): Variable Updater Instance
        """
        if options.population_size < 4:
            raise Exception("Population size 4 must be higher than 3")
        self.options = options
        self.chromosome_mutator = chromosome_mutator
        self.population_mutator = population_mutator
        self.exit_checker = exit_checker
        self.cost_finder = cost_finder
        self.population_immigrator = population_immigrator
        self.chromosome_immigrator = chromosome_immigrator
        self.parent_selector = parent_selector
        self.crossover = crossover
        self.variable_updater = variable_updater
        self._set_init_values()
        self.last_chromosome_id = 1
        self._population_generation = 0
        self.options = options
        self.chromosomes: List[Chromosome] = []
        self.generate_initial_population()
        self.start_time = datetime.now()
        self.timeout_expired = False
        self.average_cost_step_in_first_population = float("NaN")

    def __iter__(self):
        return PopulationIterator(self)

    def __getitem__(self, index):
        return self.chromosomes[index]

    def __next__(self):
        return next(self.chromosomes)

    def __len__(self):
        return len(self.chromosomes)

    def __str__(self):
        return self._to_string()

    def get_sorted(self, key=None, reverse: bool = False):
        """Sorted list of chromosomes
        Args:
            key: Sorted key
            reverse (bool=False): is reversed
        """
        return sorted(self.chromosomes, key=key, reverse=reverse)

    def append(self, c: Chromosome):
        self.chromosomes.append(c)

    def generate_initial_population(self):
        for i in range(self.options.population_size):
            self.add_new_chromosome()

    def _to_string(self):
        return ga_strings.population_to_string(self)

    def _set_init_values(self):
        float_init_value = definitions.FLOAT_NAN
        self.avg_cost = float_init_value
        self.previous_avg_cost = float_init_value
        self.min_cost = float_init_value
        self.previous_min_cost = float_init_value

    @property
    def options(self) -> GAOptions:
        """
        Genetic algorithm options
        """
        return self._options

    @options.setter
    def options(self, value: GAOptions):
        self._options = value

    @property
    def avg_cost(self) -> float:
        """
        Average cost of the population
        """
        return self._avg_cost

    @avg_cost.setter
    def avg_cost(self, value: float):
        self._avg_cost = value

    @property
    def previous_avg_cost(self) -> float:
        """
        Previous average cost
        """
        return self._previous_avg_cost

    @previous_avg_cost.setter
    def previous_avg_cost(self, value: float):
        self._previous_avg_cost = value

    @property
    def min_cost(self):
        """
        Minimum cost
        """
        return self._min_cost

    @min_cost.setter
    def min_cost(self, value: float):
        self._min_cost = value

    @property
    def previous_min_cost(self):
        """
        Previous minimum cost
        """
        return self._previous_min_cost

    @previous_min_cost.setter
    def previous_min_cost(self, value: float):
        self._previous_min_cost = value

    @property
    def best_individual(self) -> Chromosome:
        """
        Best individual chromosome
        """
        return self._best_individual

    @best_individual.setter
    def best_individual(self, value: Chromosome):
        self._best_individual = value

    @property
    def population_generation(self):
        """
        Current generation of the population
        """
        return self._population_generation

    @population_generation.setter
    def population_generation(self, value):
        self._population_generation = value

    @property
    def chromosome_mutator(self) -> BaseGeneMutationSelector:
        """
        Chromosome mutator algorithm
        """
        return self._chromosome_mutator

    @chromosome_mutator.setter
    def chromosome_mutator(self, value: BaseGeneMutationSelector):
        self._chromosome_mutator = value

    @property
    def population_mutator(self) -> BaseChromosomeMutationRateDeterminator:
        """
        Population mutator algorithm
        """
        return self._population_mutator

    @population_mutator.setter
    def population_mutator(self, value: BaseChromosomeMutationRateDeterminator):
        self._population_mutator = value

    @property
    def cost_finder(self) -> BaseCostFinder:
        """
        Cost finding algorithm
        """
        return self._cost_finder

    @cost_finder.setter
    def cost_finder(self, value: BaseCostFinder):
        self._cost_finder = value

    @property
    def parent_selector(self):
        """
        Parent selection algorithm
        """
        return self._parent_selector

    @parent_selector.setter
    def parent_selector(self, value):
        self._parent_selector = value

    @property
    def population_immigrator(self) -> BasePopulationImmigrator:
        """
        Population immigration algorithm
        """
        return self._population_immigrator

    @population_immigrator.setter
    def population_immigrator(self, value: BasePopulationImmigrator):
        self._population_immigrator = value

    @property
    def chromosome_immigrator(self) -> BaseChromosomeImmigrator:
        """
        Chromosome immigration algorithm
        """
        return self._chromosome_immigrator

    @chromosome_immigrator.setter
    def chromosome_immigrator(self, value: BaseChromosomeImmigrator):
        self._chromosome_immigrator = value

    @property
    def crossover(self) -> BaseCrossover:
        """
        Crossover algorithm
        """
        return self._crossover

    @crossover.setter
    def crossover(self, value: BaseCrossover):
        self._crossover = value

    @property
    def variable_updater(self) -> BaseVariableUpdater:
        """
        Variable update algorithm
        """
        return self._variable_updater

    @variable_updater.setter
    def variable_updater(self, value: BaseVariableUpdater):
        self._variable_updater = value

    @property
    def exit_checker(self) -> BaseExitChecker:
        """
        Exit checking algorithm
        """
        return self._exit_checker

    @exit_checker.setter
    def exit_checker(self, value: BaseExitChecker):
        self._exit_checker = value

    def exit(self) -> bool:
        """
        Check exit from the GA
        """
        self.population_generation += 1
        return self.exit_checker.check(self)

    def immigrate(self):
        """
        Immigrates new chromosomes
        """
        self.population_immigrator.immigrate(self)

    def select_mates(self) -> List[Tuple[Chromosome, Chromosome]]:
        """
        Selects mates for pairing
        """
        return self.parent_selector.select_mates(self)

    def mate(self):
        """
        Mates chromosomes
        """
        chromosome_pairs = self.select_mates()
        for chromosome1, chromosome2 in chromosome_pairs:
            offspring1, offspring2 = self.crossover.mate(
                chromosome1, chromosome2, self.population_generation
            )
            self.add_chromosomes((offspring1, offspring2))

    def mutate(self):
        """
        Mutates chromosomes in the population
        """
        self.population_mutator.mutate(self)

    def find_costs(self):
        """
        Finds costs for chromosomes
        """
        self.previous_avg_cost = self.avg_cost
        self.previous_min_cost = self.min_cost
        self.cost_finder.find_costs(self)

    def clear(self):
        """
        Clears all chromosomes
        """
        self.chromosomes.clear()

    def clear_and_add_chromosomes(self, chromosomes: List[Chromosome]):
        """
        Clears chromosomes and adds new ones
        Args:
            chromosomes (List[Chromosome]): chromosomes to add
        """
        self.chromosomes.clear()
        self.add_chromosomes(chromosomes)

    def add_chromosomes(self, chromosomes):
        """
        Adds chromosomes to population
        Args:
            chromosomes (List[Chromosome]): chromosomes to add
        """
        for c in chromosomes:
            self.add_chromosome(c)

    def add_new_chromosome(self):
        """
        Adds new chromosomes to the population
        """
        chromosome = Chromosome(
            self.chromosome_mutator,
            self.chromosome_immigrator,
            self.population_generation,
        )
        chromosome.chromosome_generation = 1
        self.add_chromosome(chromosome)

    def add_chromosome(self, chromosome):
        """
        Adds chromosome to the population
        Args:
            chromosome: chromosome to add
        """
        if len(self) >= self.options.population_size:
            return
        if chromosome.chromosome_id is None or chromosome.chromosome_id == -1:
            chromosome.chromosome_id = self.last_chromosome_id
            self.last_chromosome_id += 1
        if len(chromosome) == 0:
            for dv in self.options.decision_variables:
                g = Gene(dv)
                chromosome.append(g)
        self.append(chromosome)

    def update_variables(self):
        """
        Updates decision variables
        """
        self.variable_updater.update_variables(self)

    def calculate_average_cost_step(self):
        allocated_values = [
            c.cost_value
            for c in self.chromosomes
            if c.cost_value is not None and not math.isnan(c.cost_value)
        ]
        if allocated_values:
            return ga_utils.average_difference(allocated_values)
        return float("NaN")


class PopulationIterator:
    def __init__(self, population):
        self.population = population
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.population.chromosomes):
            result = self.population.chromosomes[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration
