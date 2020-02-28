from functools import partial
from random import randint
from typing import (
    List,
    Callable,
    Optional,
    Any
)

from core.composer.chain import Chain, Node
from core.composer.node import NodeGenerator
from core.models.data import InputData
from core.models.model import Model
from core.composer.composer import ComposerRequirements


class RandomSearchComposer:
    def __init__(self, iter_num: int = 10):
        self.__iter_num = iter_num

    def compose_chain(self, data: InputData,
                      initial_chain: Optional[Chain],
                      composer_requirements: ComposerRequirements,
                      metrics: Optional[Callable]) -> Chain:
        metric_function_for_nodes = partial(self._metric_for_nodes,
                                            metrics, data)

        optimiser = RandomSearchOptimiser(self.__iter_num,
                                          NodeGenerator.primary_node,
                                          NodeGenerator.secondary_node)
        best_nodes_set, _ = optimiser.optimise(metric_function_for_nodes,
                                               composer_requirements.primary_requirements, composer_requirements.secondary_requirements)

        best_chain = Chain()
        [best_chain.add_node(nodes) for nodes in best_nodes_set]

        return best_chain

    @staticmethod
    def _nodes_to_chain(nodes: List[Node], data: InputData) -> Chain:
        chain = Chain()
        [chain.add_node(nodes) for nodes in nodes]
        chain.reference_data = data
        return chain

    @staticmethod
    def _metric_for_nodes(metric_function, data, nodes: List[Node]) -> float:
        chain = RandomSearchComposer._nodes_to_chain(nodes, data)
        return metric_function(chain)


class RandomSearchOptimiser:
    def __init__(self, iter_num: int, primary_node_func: Callable, secondary_node_func: Callable):
        self.__iter_num = iter_num
        self.__primary_node_func = primary_node_func
        self.__secondary_node_func = secondary_node_func

    def optimise(self, metric_function_for_nodes,
                 primary_candidates: List[Any],
                 secondary_candidates: List[Any]):
        best_metric_value = 1000
        best_set = []
        history = []
        for i in range(self.__iter_num):
            print(f'Iter {i}')
            new_nodeset = self._random_nodeset(primary_candidates, secondary_candidates)
            new_metric_value = round(metric_function_for_nodes(new_nodeset), 3)
            history.append((new_nodeset, new_metric_value))

            print(f'Try {new_metric_value} with length {len(new_nodeset)}')
            if new_metric_value < best_metric_value:
                best_metric_value = new_metric_value
                best_set = new_nodeset
                print(f'Better chain found: metric {best_metric_value}')

        return best_set, history

    def _random_nodeset(self, primary_requirements: List[Any], secondary_requirements: List[Any]) -> List[Node]:
        new_set = []

        num_of_primary = randint(1, len(primary_requirements))

        # random primary nodes
        for _ in range(num_of_primary):
            random_first_model_ind = randint(0, len(primary_requirements) - 1)
            first_node = self.__primary_node_func(primary_requirements[random_first_model_ind], None)
            new_set.append(first_node)

        # random final node
        if len(new_set) > 1:
            random_final_model_ind = randint(0, len(secondary_requirements) - 1)
            new_node = self.__secondary_node_func(secondary_requirements[random_final_model_ind])
            new_node.nodes_from = [node for node in new_set if node.nodes_from is None]
            if len(new_node.nodes_from) == 0:
                new_node.nodes_from = new_set
            new_set.append(new_node)

        return new_set
