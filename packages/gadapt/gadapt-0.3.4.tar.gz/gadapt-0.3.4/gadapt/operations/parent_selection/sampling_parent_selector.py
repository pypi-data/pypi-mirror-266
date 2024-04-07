from typing import List, Tuple
from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.parent_selection.base_parent_selector import BaseParentSelector
from gadapt.operations.sampling.base_sampling import BaseSampling


class SamplingParentSelector(BaseParentSelector):
    """
    Parent Selector based on sampling.
    Sampling is the algorithm for extracting a sample from the population,
    based on specific value of the chromosme.
    In this case sampling depends on cost value.

    Selects mates for mating from the population
    """

    def __init__(self, sampling: BaseSampling) -> None:
        super().__init__()
        self._sampling = sampling

    def _select_mates_from_population(
        self, population
    ) -> List[Tuple[Chromosome, Chromosome]]:
        working_chromosomes = self._sampling.get_sample(
            population.chromosomes, len(population), lambda c: c.cost_value
        )
        list_of_mates: List[Tuple[Chromosome, Chromosome]] = []
        while len(working_chromosomes) > 1:
            c1 = working_chromosomes.pop(0)
            c2 = working_chromosomes.pop(0)
            list_of_mates.append((c1, c2))
        return list_of_mates
