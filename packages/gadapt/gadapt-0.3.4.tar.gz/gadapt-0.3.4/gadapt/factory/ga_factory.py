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
from gadapt.operations.mutation.chromosome_mutation.base_chromosome_mutator import (
    BaseChromosomeMutator,
)
from gadapt.operations.mutation.chromosome_mutation.cross_diversity_chromosome_mutator import (
    CrossDiversityChromosomeMutator,
)
from gadapt.operations.mutation.chromosome_mutation.random_chromosome_mutator import (
    RandomChromosomeMutator,
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
from gadapt.operations.mutation.population_mutation.base_population_mutator import (
    BasePopulationMutator,
)
from gadapt.operations.mutation.population_mutation.composed_population_mutator import (
    ComposedPopulationMutator,
)
from gadapt.operations.mutation.population_mutation.cost_diversity_population_mutator import (
    CostDiversityPopulationMutator,
)
from gadapt.operations.mutation.population_mutation.cross_diversity_population_mutator import CrossDiversityPopulationMutator
from gadapt.operations.mutation.population_mutation.parent_diversity_population_mutator import (
    ParentDiversityPopulationMutator,
)
from gadapt.operations.mutation.population_mutation.random_population_mutator import (
    RandomPopulationMutator,
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

    def _get_chromosome_mutator(self) -> BaseChromosomeMutator:
        """
        Chromosome Mutator Instance
        """
        if self._ga.chromosome_mutation.strip() == definitions.CROSS_DIVERSITY:
            return CrossDiversityChromosomeMutator(
                self._get_sampling_method(
                    self._ga.cross_diversity_mutation_gene_selection
                )
            )
        elif self._ga.chromosome_mutation.strip() == definitions.RANDOM:
            return RandomChromosomeMutator()
        else:
            raise Exception("unknown chromosome mutation")

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
    ) -> BasePopulationMutator:
        """
        Population Mutator Instance
        """
        self._population_mutator_options_validation()
        if population_mutator_string is None:
            population_mutator_string = self._ga.population_mutation.strip()
        if population_mutator_string.find(definitions.PARAM_SEPARATOR) > -1:
            return self._get_population_mutator_combined()
        elif population_mutator_string == definitions.COST_DIVERSITY:
            return CostDiversityPopulationMutator(
                ParentDiversityPopulationMutator(
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_chromosome_selection
                    ),
                ),
            )
        elif population_mutator_string == definitions.PARENT_DIVERSITY:
            return ParentDiversityPopulationMutator(
                self._get_sampling_method(
                    self._ga.parent_diversity_mutation_chromosome_selection
                ),
            )
        elif population_mutator_string == definitions.CROSS_DIVERSITY:
            return CrossDiversityPopulationMutator(
                ParentDiversityPopulationMutator(
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_chromosome_selection
                    ),
                ),
            )
        elif population_mutator_string == definitions.RANDOM:
            return RandomPopulationMutator()
        else:
            raise Exception("unknown population mutation")

    def _get_population_mutator(self) -> BasePopulationMutator:
        """
        Population Mutator Instance
        """
        return self._make_population_mutator()

    def _get_population_mutator_combined(self) -> BasePopulationMutator:
        """
        Population Mutator Instance - combined
        """
        mutator_strings = [
            ms.strip()
            for ms in self._ga.population_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        if self._is_cost_diversity_random(mutator_strings):
            return CostDiversityPopulationMutator(RandomPopulationMutator())
        if self._is_cost_diversity_parent_diversity(mutator_strings):
            return CostDiversityPopulationMutator(
                ParentDiversityPopulationMutator(
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_chromosome_selection
                    ),
                ),
            )
        if self._is_cost_diversity_parent_diversity_random(mutator_strings):
            composedPopulationMutator = ComposedPopulationMutator()
            composedPopulationMutator.append(
                ParentDiversityPopulationMutator(
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_chromosome_selection
                    ),
                )
            )
            composedPopulationMutator.append(RandomPopulationMutator())
            return CostDiversityPopulationMutator(composedPopulationMutator)
        if self._is_cross_diversity_random(mutator_strings):
            return CrossDiversityPopulationMutator(RandomPopulationMutator())
        if self._is_cross_diversity_parent_diversity(mutator_strings):
            return CrossDiversityPopulationMutator(
                ParentDiversityPopulationMutator(
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_chromosome_selection
                    ),
                ),
            ) 
        if self._is_cross_diversity_parent_diversity_random(mutator_strings):
            composedPopulationMutator = ComposedPopulationMutator()
            composedPopulationMutator.append(
                ParentDiversityPopulationMutator(
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_chromosome_selection
                    ),
                )
            )
            composedPopulationMutator.append(RandomPopulationMutator())
            return CrossDiversityPopulationMutator(composedPopulationMutator)
        if self._is_cross_diversity_cost_diversity_parent_diversity(mutator_strings):
            composedPopulationMutator = ComposedPopulationMutator()
            parent_diversity_population_mutator = ParentDiversityPopulationMutator(
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_chromosome_selection
                    ),
                )
            composedPopulationMutator.append(CrossDiversityPopulationMutator(parent_diversity_population_mutator))
            composedPopulationMutator.append(CostDiversityPopulationMutator(parent_diversity_population_mutator))
            return composedPopulationMutator
        if self._is_cross_diversity_cost_diversity_parent_diversity_random(mutator_strings):
            composedPopulationMutator1 = ComposedPopulationMutator()
            composedPopulationMutator1.append(RandomPopulationMutator())
            composedPopulationMutator1.append(
                ParentDiversityPopulationMutator(
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_chromosome_selection
                    ),
                )
            )
            composedPopulationMutator2 = ComposedPopulationMutator()
            composedPopulationMutator2.append(CrossDiversityPopulationMutator(composedPopulationMutator1))
            composedPopulationMutator2.append(CostDiversityPopulationMutator(composedPopulationMutator1))
            return composedPopulationMutator2
        composedPopulationMutator = ComposedPopulationMutator()
        for ms in mutator_strings:
            composedPopulationMutator.append(self._make_population_mutator(ms))
        return composedPopulationMutator

    def _is_cost_diversity_random(self, mutator_strings: list):
        """
        Is population mutator cost diversity and random
        """
        if (
            len(mutator_strings) == 2
            and definitions.COST_DIVERSITY in mutator_strings
            and definitions.RANDOM in mutator_strings
        ):
            return True
        return False

    def _is_cost_diversity_parent_diversity(self, mutator_strings: list):
        """
        Is population mutator cost diversity and parent diversity
        """
        if (
            len(mutator_strings) == 2
            and definitions.COST_DIVERSITY in mutator_strings
            and definitions.PARENT_DIVERSITY in mutator_strings
        ):
            return True
        return False
        

    def _is_cost_diversity_parent_diversity_random(self, mutator_strings: list):
        """
        Is population mutator cost diversity, parent diversity and random
        """
        if (
            len(mutator_strings) == 3
            and definitions.COST_DIVERSITY in mutator_strings
            and definitions.PARENT_DIVERSITY in mutator_strings
            and definitions.RANDOM in mutator_strings
        ):
            return True
        return False    
    
    def _is_cross_diversity_parent_diversity(self, mutator_strings: list):
        """
        Is population mutator cost diversity and parent diversity
        """
        if (
            len(mutator_strings) == 2
            and definitions.CROSS_DIVERSITY in mutator_strings
            and definitions.PARENT_DIVERSITY in mutator_strings
        ):
            return True
        return False
    
    def _is_cross_diversity_random(self, mutator_strings: list):
        """
        Is population mutator cost diversity and parent diversity
        """
        if (
            len(mutator_strings) == 2
            and definitions.CROSS_DIVERSITY in mutator_strings
            and definitions.RANDOM in mutator_strings
        ):
            return True
        return False
    
    def _is_cross_diversity_cost_diversity_parent_diversity(self, mutator_strings: list):
        """
        Is population mutator cost diversity and parent diversity
        """
        if (
            len(mutator_strings) == 3
            and definitions.CROSS_DIVERSITY in mutator_strings
            and definitions.PARENT_DIVERSITY in mutator_strings
            and definitions.COST_DIVERSITY in mutator_strings
        ):
            return True
        return False
    
    def _is_cross_diversity_parent_diversity_random(self, mutator_strings: list):
        """
        Is population mutator cost diversity, parent diversity and random
        """
        if (
            len(mutator_strings) == 3
            and definitions.CROSS_DIVERSITY in mutator_strings
            and definitions.PARENT_DIVERSITY in mutator_strings
            and definitions.RANDOM in mutator_strings
        ):
            return True
        return False
    
    def _is_cross_diversity_cost_diversity_parent_diversity_random(self, mutator_strings: list):
        """
        Is population mutator cost diversity and parent diversity
        """
        if (
            len(mutator_strings) == 4
            and definitions.CROSS_DIVERSITY in mutator_strings
            and definitions.PARENT_DIVERSITY in mutator_strings
            and definitions.COST_DIVERSITY in mutator_strings
            and definitions.RANDOM in mutator_strings
        ):
            return True
        return False

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
