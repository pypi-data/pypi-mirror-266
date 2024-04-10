from gadapt.factory.ga_base_factory import BaseGAFactory
from gadapt.operations.exit_check.avg_cost_exit_checker import AvgCostExitChecker
from gadapt.operations.exit_check.base_exit_checker import BaseExitChecker
from gadapt.operations.exit_check.min_cost_exit_checker import MinCostExitChecker
from gadapt.operations.exit_check.requested_cost_exit_checker import (
    RequestedCostExitChecker,
)
from gadapt.operations.cost_finding.base_cost_finder import BaseCostFinder
from gadapt.operations.cost_finding.elitism_cost_finder import ElitismCostFinder
from gadapt.operations.crossover.base_crossover import BaseCrossover
from gadapt.operations.crossover.uniform_crossover import UniformCrossover
from gadapt.operations.immigration.chromosome_immigration.base_chromosome_immigrator import (
    BaseChromosomeImmigrator,
)
from gadapt.operations.immigration.chromosome_immigration.random_chromosome_immigrator import (
    RandomChromosomeImmigrator,
)
from gadapt.operations.immigration.population_immigration.base_population_immigrator import (
    BasePopulationImmigrator,
)
from gadapt.operations.immigration.population_immigration.common_population_immigrator import (
    CommonPopulationImmigrator,
)
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_selector import (
    BaseGeneMutationSelector,
)
from gadapt.operations.mutation.chromosome_mutation.cross_diversity_gene_mutation_selector import (
    CrossDiversityGeneMutationSelector,
)
from gadapt.operations.mutation.chromosome_mutation.random_gene_mutation_selector import (
    RandomGeneMutationSelector,
)
from gadapt.operations.mutation.gene_mutation.base_gene_mutator import BaseGeneMutator
from gadapt.operations.mutation.gene_mutation.extreme_pointed_gene_mutator import (
    ExtremePointedGeneMutator,
)
from gadapt.operations.mutation.gene_mutation.normal_distribution_gene_mutator import (
    NormalDistributionGeneMutator,
)
from gadapt.operations.mutation.gene_mutation.random_gene_mutator import (
    RandomGeneMutator,
)
from gadapt.operations.mutation.population_mutation.composed_chromosome_mutation_selector import (
    ComposedChromosomeMutationSelector,
)
from gadapt.operations.mutation.population_mutation.cost_diversity_chromosome_mutation_rate_determinator import (
    CostDiversityChromosomeMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.cross_diversity_chromosome_mutation_rate_determinator import (
    CrossDiversityChromosomeMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.parent_diversity_chromosome_mutation_selector import (
    ParentDiversityChromosomeMutationSelector,
)
from gadapt.operations.mutation.population_mutation.random_chromosome_mutation_selector import (
    RandomChromosomeMutationSelector,
)
from gadapt.operations.parent_selection.base_parent_selector import BaseParentSelector
from gadapt.operations.parent_selection.sampling_parent_selector import (
    SamplingParentSelector,
)
from gadapt.operations.sampling.base_sampling import BaseSampling
from gadapt.operations.sampling.from_top_to_bottom_sampling import (
    FromTopToBottomSampling,
)
from gadapt.operations.sampling.random_sampling import RandomSampling
from gadapt.operations.sampling.roulette_wheel_sampling import RouletteWheelSampling
from gadapt.operations.sampling.tournament_sampling import TournamentSampling
from gadapt.operations.gene_combination.base_gene_combination import BaseGeneCombination
from gadapt.operations.gene_combination.blending_gene_combination import (
    BlendingGeneCombination,
)
from gadapt.operations.variable_update.common_variable_updater import (
    CommonVariableUpdater,
)
import gadapt.ga_model.definitions as definitions
from gadapt.operations.mutation.chromosome_mutation.composed_gene_mutation_rate_determinator import (
    ComposedGeneMutationRateDeterminator,
)
from gadapt.operations.mutation.chromosome_mutation.composed_gene_mutation_selector import (
    ComposedGeneMutationSelector,
)
from gadapt.operations.mutation.chromosome_mutation.cross_diversity_gene_mutation_rate_determinator import (
    CrossDiversityGeneMutationRateDeterminator,
)
from gadapt.operations.mutation.chromosome_mutation.random_gene_mutation_rate_determinator import (
    RandomGeneMutationRateDeterminator,
)
from gadapt.operations.mutation.chromosome_mutation.strict_gene_mutation_rate_determinator import (
    StrictGeneMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_selector import (
    BaseChromosomeMutationSelector,
)
from gadapt.operations.mutation.population_mutation.composed_chromosome_mutation_rate_determinator import (
    ComposedChromosomeMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.random_chromosome_mutation_rate_determinator import (
    RandomChromosomeMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.strict_chromosome_mutation_rate_determinator import (
    StrictChromosomeMutationRateDeterminator,
)


class GAFactory(BaseGAFactory):
    """
    Factory implementatiopn for creating  class instances based on GA options
    """

    def _get_cost_finder(self) -> BaseCostFinder:
        """
        Cost Finder instance
        """
        return ElitismCostFinder()

    def _get_population_immigrator(self) -> BasePopulationImmigrator:
        """
        Population Immigrator Instance
        """
        return CommonPopulationImmigrator()

    def _get_chromosome_immigrator(self) -> BaseChromosomeImmigrator:
        """
        Chromosome Immigrator Instance
        """
        return RandomChromosomeImmigrator()

    def _get_chromosome_mutator(self) -> BaseGeneMutationSelector:
        """
        Chromosome Mutator Instance
        """
        return self._get_chromosome_mutator_combined()

    def _get_gene_mutator(self) -> BaseGeneMutator:
        """
        Chromosome Mutator Instance
        """
        if self._ga.gene_mutation.strip() == definitions.EXTREME_POINTED:
            return ExtremePointedGeneMutator()
        elif self._ga.gene_mutation.strip() == definitions.RANDOM:
            return RandomGeneMutator()
        elif self._ga.gene_mutation.strip() == definitions.NORMAL_DISTRIBUTION:
            return NormalDistributionGeneMutator()
        else:
            raise Exception("unknown gene mutation")

    def _population_mutator_options_validation(self):
        """
        Validates population mutator options
        """
        mutator_strings = self._ga.population_mutation.split(
            definitions.PARAM_SEPARATOR
        )
        for s in mutator_strings:
            if s.strip() not in definitions.POPULATION_MUTATOR_STRINGS:
                raise Exception(s + " is not defined as option for population mutation")

    def _make_population_mutator(
        self, population_mutator_string=None
    ) -> BaseChromosomeMutationSelector:
        """
        Population Mutator Instance
        """
        self._population_mutator_options_validation()
        return self._get_population_mutator_combined()

    def _get_population_mutator(self) -> BaseChromosomeMutationSelector:
        """
        Population Mutator Instance
        """
        return self._make_population_mutator()

    def _get_population_mutator_combined(self) -> BaseChromosomeMutationSelector:
        """
        Population Mutator Instance - combined
        """
        mutator_strings = [
            ms.strip()
            for ms in self._ga.population_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        chromosome_mutation_rate_determinators = []
        chromosome_mutation_selectors = []
        if definitions.RANDOM in mutator_strings:
            chromosome_mutation_rate_determinators.append(
                RandomChromosomeMutationRateDeterminator()
            )
        if definitions.CROSS_DIVERSITY in mutator_strings:
            chromosome_mutation_rate_determinators.append(
                CrossDiversityChromosomeMutationRateDeterminator()
            )
        if definitions.COST_DIVERSITY in mutator_strings:
            chromosome_mutation_rate_determinators.append(
                CostDiversityChromosomeMutationRateDeterminator()
            )
        if len(chromosome_mutation_rate_determinators) == 0:
            chromosome_mutation_rate_determinators.append(
                CostDiversityChromosomeMutationRateDeterminator()
            )
        if len(chromosome_mutation_rate_determinators) == 1:
            main_chromosome_mutation_rate_determinator = (
                chromosome_mutation_rate_determinators[0]
            )
        else:
            main_chromosome_mutation_rate_determinator = (
                ComposedChromosomeMutationRateDeterminator()
            )
            for determinator in chromosome_mutation_rate_determinators:
                main_chromosome_mutation_rate_determinator.append(determinator)
        if (
            definitions.RANDOM in mutator_strings
            and definitions.PARENT_DIVERSITY in mutator_strings
        ):
            helper_chromosome_mutation_rate_determinator = (
                StrictChromosomeMutationRateDeterminator()
            )
        else:
            helper_chromosome_mutation_rate_determinator = (
                main_chromosome_mutation_rate_determinator
            )
        if definitions.RANDOM in mutator_strings:
            chromosome_mutation_selectors.append(
                RandomChromosomeMutationSelector(
                    helper_chromosome_mutation_rate_determinator
                )
            )
        if definitions.PARENT_DIVERSITY in mutator_strings:
            chromosome_mutation_selectors.append(
                ParentDiversityChromosomeMutationSelector(
                    helper_chromosome_mutation_rate_determinator,
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_chromosome_selection
                    ),
                )
            )
        if len(chromosome_mutation_selectors) == 0:
            chromosome_mutation_selectors.append(
                ParentDiversityChromosomeMutationSelector(
                    helper_chromosome_mutation_rate_determinator,
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_chromosome_selection
                    ),
                )
            )
        if len(chromosome_mutation_selectors) == 1:
            chromosome_mutation_selector = chromosome_mutation_selectors[0]
        else:
            chromosome_mutation_selector = ComposedChromosomeMutationSelector(
                main_chromosome_mutation_rate_determinator
            )
            for selector in chromosome_mutation_selectors:
                chromosome_mutation_selector.append(selector)
        return chromosome_mutation_selector

    def _get_chromosome_mutator_combined(self) -> BaseGeneMutationSelector:
        """
        Chromosome Mutator Instance - combined
        """
        mutator_strings = [
            ms.strip()
            for ms in self._ga.chromosome_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        gene_mutation_rate_determinators = []
        gene_mutation_selectors = []
        if definitions.RANDOM in mutator_strings:
            gene_mutation_rate_determinators.append(
                RandomGeneMutationRateDeterminator()
            )
        if definitions.CROSS_DIVERSITY in mutator_strings:
            gene_mutation_rate_determinators.append(
                CrossDiversityGeneMutationRateDeterminator()
            )
        if len(gene_mutation_rate_determinators) == 0:
            gene_mutation_rate_determinators.append(
                RandomGeneMutationRateDeterminator()
            )
            gene_mutation_rate_determinators.append(
                CrossDiversityGeneMutationRateDeterminator()
            )
        if len(gene_mutation_rate_determinators) == 1:
            main_gene_mutation_rate_determinator = gene_mutation_rate_determinators[0]
        else:
            main_gene_mutation_rate_determinator = (
                ComposedGeneMutationRateDeterminator()
            )
            for determinator in gene_mutation_rate_determinators:
                main_gene_mutation_rate_determinator.append(determinator)
        if (
            definitions.RANDOM in mutator_strings
            and definitions.COST_DIVERSITY in mutator_strings
        ):
            helper_gene_mutation_rate_determinator = (
                StrictGeneMutationRateDeterminator()
            )
        else:
            helper_gene_mutation_rate_determinator = (
                main_gene_mutation_rate_determinator
            )
        if definitions.RANDOM in mutator_strings:
            gene_mutation_selectors.append(
                RandomGeneMutationSelector(helper_gene_mutation_rate_determinator)
            )
        if definitions.CROSS_DIVERSITY in mutator_strings:
            gene_mutation_selectors.append(
                CrossDiversityGeneMutationSelector(
                    helper_gene_mutation_rate_determinator,
                    self._get_sampling_method(
                        self._ga.cross_diversity_mutation_gene_selection
                    ),
                )
            )
        if len(gene_mutation_selectors) == 0:
            gene_mutation_selectors.append(
                CrossDiversityGeneMutationSelector(
                    helper_gene_mutation_rate_determinator,
                    self._get_sampling_method(
                        self._ga.cross_diversity_mutation_gene_selection
                    ),
                )
            )
        if len(gene_mutation_selectors) == 1:
            gene_mutation_selector = gene_mutation_selectors[0]
        else:
            gene_mutation_selector = self.get_composed_gene_mutation_selector(
                main_gene_mutation_rate_determinator,
                gene_mutation_selectors,
                helper_gene_mutation_rate_determinator,
            )
        return gene_mutation_selector

    def get_composed_gene_mutation_selector(
        self,
        main_gene_mutation_rate_determinator,
        gene_mutation_selectors,
        helper_gene_mutation_rate_determinator,
    ):
        if not gene_mutation_selectors:
            gene_mutation_selectors.append(
                CrossDiversityGeneMutationSelector(
                    helper_gene_mutation_rate_determinator,
                    self._get_sampling_method(
                        self._ga.cross_diversity_mutation_gene_selection
                    ),
                )
            )
            gene_mutation_selectors.append(
                RandomGeneMutationSelector(helper_gene_mutation_rate_determinator)
            )
        gene_mutation_selector = ComposedGeneMutationSelector(
            main_gene_mutation_rate_determinator
        )
        for selector in gene_mutation_selectors:
            gene_mutation_selector.append(selector)
        return gene_mutation_selector

    def _get_parent_selector(self) -> BaseParentSelector:
        """
        Parent Selector Instance
        """
        return SamplingParentSelector(
            self._get_sampling_method(self._ga.parent_selection)
        )

    def _get_sampling_method(self, str) -> BaseSampling:
        """
        Sampling Methos Instance
        """
        str_value = str
        sampling_method_strings = str.split(definitions.PARAM_SEPARATOR)
        other_value = None
        if len(sampling_method_strings) > 1:
            str_value = sampling_method_strings[0]
            try:
                other_value = int(sampling_method_strings[1])
            except Exception:
                pass
        if str_value == definitions.TOURNAMENT:
            return TournamentSampling(other_value)
        elif str_value == definitions.FROM_TOP_TO_BOTTOM:
            return FromTopToBottomSampling()
        elif str_value == definitions.RANDOM:
            return RandomSampling()
        return RouletteWheelSampling()

    def _get_gene_combination(self) -> BaseGeneCombination:
        """
        Gene Combination Instance
        """
        return BlendingGeneCombination()

    def _get_exit_checker(self) -> BaseExitChecker:
        """
        Exit Checker Instance
        """
        if self._ga.exit_check == definitions.AVG_COST:
            return AvgCostExitChecker(self._ga.max_attempt_no)
        if self._ga.exit_check == definitions.MIN_COST:
            return MinCostExitChecker(self._ga.max_attempt_no)
        return RequestedCostExitChecker(self._ga.requested_cost)

    def _get_crossover(self) -> BaseCrossover:
        """
        Crossover Instance
        """
        return UniformCrossover(
            self.get_gene_combination(),
            self.get_chromosome_mutator(),
            self.get_chromosome_immigrator(),
        )

    def _get_variable_updater(self):
        """
        Variable Updater Instance
        """
        return CommonVariableUpdater()
