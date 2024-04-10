from abc import ABC, abstractmethod
from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.gene import Gene
from gadapt.operations.immigration.chromosome_immigration.base_chromosome_immigrator import (
    BaseChromosomeImmigrator,
)
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_selector import (
    BaseGeneMutationSelector,
)
from gadapt.operations.gene_combination.base_gene_combination import BaseGeneCombination
import gadapt.utils.ga_utils as ga_utils


class BaseCrossover(ABC):
    """Base Crossover Class

    Args:
        gene_combination (BaseGeneCombination): the algorithm
        for how genes are to be combined
        mutator (BaseGeneMutationSelector): mutation algorithm to
        be passed to offspring chromosomes
        immigrator (BaseChromosomeImmigrator): immigration algorithm
        to be passed to offspring chromosomes
        mutation_on_both_sides (bool): indicates if offspring chromosomes
        should be mutated on both sides with the same probability
    """

    def __init__(
        self,
        gene_combination: BaseGeneCombination,
        mutator: BaseGeneMutationSelector,
        immigrator: BaseChromosomeImmigrator,
        mutation_on_both_sides: bool = True,
    ):
        self._mutation_on_both_sides = True
        self._gene_combination = gene_combination
        self._mutator = mutator
        self._immigrator = immigrator
        self._mutation_on_both_sides = mutation_on_both_sides

    def mate(self, mother: Chromosome, father: Chromosome, population_generation: int):
        """Returns two offspring chromosomes using parents' genetic material

        Args:
            mother (Chromosome): The first chromosome for mating
            father (Chromosome): The second chromosome for mating
            population_generation (int): Current generation in the population

        Returns:
            Chromosome: the first offspring chromosome
            Chromosome: the second offspring chromosome
        """

        def get_genetic_diversity(g_m: Gene, g_f: Gene) -> float:
            return abs(g_m.variable_value - g_f.variable_value) / (
                g_f.decision_variable.max_value - g_f.decision_variable.min_value
            )

        if len(mother) != len(father):
            raise Exception("Mother and father must have the same number of genes!")
        offspring1 = Chromosome(self._mutator, self._immigrator, population_generation)
        offspring2 = Chromosome(self._mutator, self._immigrator, population_generation)
        self.number_of_genes = len(father)
        genetic_diversity = []
        for self._current_gene_number in range(self.number_of_genes):
            mother_gene, father_gene = self._get_mother_father_genes(mother, father)
            decision_variable_father = father_gene.decision_variable
            decision_variable_mother = mother_gene.decision_variable
            if decision_variable_father != decision_variable_mother:
                decision_variable_mother = next(
                    (
                        item.decision_variable
                        for item in mother
                        if item.decision_variable == decision_variable_father
                    ),
                    None,
                )
            if decision_variable_mother is None:
                raise Exception(
                    "chromosomes in crossover do not have the same structure!"
                )
            genetic_diversity.append(get_genetic_diversity(mother_gene, father_gene))
            var1, var2 = self._combine(mother_gene, father_gene)
            offspring1.add_gene(decision_variable_father, var1)
            offspring2.add_gene(decision_variable_father, var2)
        parrents_diversity = round(ga_utils.average(genetic_diversity), 2)
        offspring1.parent_diversity = parrents_diversity
        offspring2.parent_diversity = parrents_diversity
        offspring1.mutation_on_both_sides = self._mutation_on_both_sides
        offspring2.mutation_on_both_sides = self._mutation_on_both_sides
        offspring1.mother_id = mother.chromosome_id
        offspring2.mother_id = mother.chromosome_id
        offspring1.father_id = father.chromosome_id
        offspring2.father_id = father.chromosome_id
        self._increase_generation(offspring1, offspring2, mother, father)
        return offspring1, offspring2

    @abstractmethod
    def _get_mother_father_genes(self, mother: Chromosome, father: Chromosome):
        pass

    @abstractmethod
    def _combine(self, mother_gene: Gene, father_gene: Gene):
        pass

    def _increase_generation(
        self,
        offspring1: Chromosome,
        offspring2: Chromosome,
        mother: Chromosome,
        father: Chromosome,
    ):
        current_generation = mother.chromosome_generation
        if current_generation == 0 or current_generation < father.chromosome_generation:
            current_generation = father.chromosome_generation
        current_generation += 1
        offspring1.chromosome_generation = current_generation
        offspring2.chromosome_generation = current_generation

        current_generation = 0
        if mother.first_mutant_generation > 0 or father.first_mutant_generation > 0:
            current_generation = mother.first_mutant_generation
            if (
                current_generation == 0
                or father.first_mutant_generation > current_generation
            ):
                current_generation = father.first_mutant_generation
            current_generation += 1
        offspring1.first_mutant_generation = current_generation
        offspring2.first_mutant_generation = current_generation

        current_generation = 0
        if mother.last_mutant_generation > 0 or father.last_mutant_generation > 0:
            current_generation = mother.last_mutant_generation
            if current_generation == 0 or (
                father.last_mutant_generation > 0
                and father.last_mutant_generation < current_generation
            ):
                current_generation = father.last_mutant_generation
            current_generation += 1
        offspring1.last_mutant_generation = current_generation
        offspring2.last_mutant_generation = current_generation

        current_generation = 0
        if (
            mother.first_immigrant_generation > 0
            or father.first_immigrant_generation > 0
        ):
            current_generation = mother.first_immigrant_generation
            if (
                current_generation == 0
                or father.first_immigrant_generation > current_generation
            ):
                current_generation = father.first_immigrant_generation
            current_generation += 1
        offspring1.first_immigrant_generation = current_generation
        offspring2.first_immigrant_generation = current_generation

        current_generation = 0
        if mother.last_immigrant_generation > 0 or father.last_immigrant_generation > 0:
            current_generation = mother.last_immigrant_generation
            if current_generation == 0 or (
                father.last_immigrant_generation > 0
                and father.last_immigrant_generation < current_generation
            ):
                current_generation = father.last_immigrant_generation
            current_generation += 1
        offspring1.last_immigrant_generation = current_generation
        offspring2.last_immigrant_generation = current_generation
