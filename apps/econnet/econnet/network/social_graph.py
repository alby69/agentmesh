import random
from typing import Dict, List, Tuple

import networkx as nx


class SocialGraph:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.graph = nx.Graph()

    def build_random(self, node_ids: List[int], edge_probability: float = 0.1) -> None:
        self.graph.add_nodes_from(node_ids)
        for i in node_ids:
            for j in node_ids:
                if i < j and self.rng.random() < edge_probability:
                    weight = self.rng.uniform(0.1, 1.0)
                    self.graph.add_edge(i, j, weight=weight)

    def build_small_world(self, node_ids: List[int], k: int = 4, p: float = 0.1) -> None:
        n = len(node_ids)
        if n < k + 1:
            self.build_random(node_ids, edge_probability=0.3)
            return
        self.graph = nx.watts_strogatz_graph(n, k, p, seed=self.rng.randint(0, 2**31))
        mapping = {i: node_ids[i] for i in range(n)}
        self.graph = nx.relabel_nodes(self.graph, mapping)
        for u, v in self.graph.edges():
            self.graph[u][v]["weight"] = self.rng.uniform(0.1, 1.0)

    def build_scale_free(self, node_ids: List[int], m: int = 3) -> None:
        n = len(node_ids)
        if n < m + 1:
            self.build_random(node_ids, edge_probability=0.3)
            return
        self.graph = nx.barabasi_albert_graph(n, m, seed=self.rng.randint(0, 2**31))
        mapping = {i: node_ids[i] for i in range(n)}
        self.graph = nx.relabel_nodes(self.graph, mapping)
        for u, v in self.graph.edges():
            self.graph[u][v]["weight"] = self.rng.uniform(0.1, 1.0)

    def get_neighbors(self, node_id: int) -> List[int]:
        return list(self.graph.neighbors(node_id))

    def get_weighted_neighbors(self, node_id: int) -> List[Tuple[int, float]]:
        return [
            (neighbor, self.graph[node_id][neighbor].get("weight", 0.5))
            for neighbor in self.graph.neighbors(node_id)
        ]

    def get_influence_score(self, node_id: int) -> float:
        if not self.graph.has_node(node_id) or self.graph.degree(node_id) == 0:
            return 0.0
        neighbors = self.get_neighbors(node_id)
        if not neighbors:
            return 0.0
        weights = [self.graph[node_id][n].get("weight", 0.5) for n in neighbors]
        return sum(weights) / len(weights)

    def add_edge(self, u: int, v: int, weight: float = 0.5) -> None:
        self.graph.add_edge(u, v, weight=weight)

    def remove_edge(self, u: int, v: int) -> None:
        if self.graph.has_edge(u, v):
            self.graph.remove_edge(u, v)

    def evolve(self, creation_rate: float = 0.01, removal_rate: float = 0.005) -> None:
        nodes = list(self.graph.nodes())
        if len(nodes) < 2:
            return

        if self.rng.random() < creation_rate:
            u, v = self.rng.sample(nodes, 2)
            if not self.graph.has_edge(u, v):
                self.graph.add_edge(u, v, weight=self.rng.uniform(0.1, 1.0))

        if self.rng.random() < removal_rate:
            edges = list(self.graph.edges())
            if edges:
                u, v = self.rng.choice(edges)
                self.graph.remove_edge(u, v)

    def get_all_neighbor_satisfactions(
        self, agent_states: Dict[int, float]
    ) -> Dict[int, float]:
        result = {}
        for node_id in self.graph.nodes():
            neighbors = self.get_neighbors(node_id)
            if not neighbors:
                result[node_id] = 0.5
                continue
            scores = [agent_states.get(n, 0.5) for n in neighbors]
            result[node_id] = sum(scores) / len(scores)
        return result

    def node_count(self) -> int:
        return self.graph.number_of_nodes()

    def edge_count(self) -> int:
        return self.graph.number_of_edges()

    def density(self) -> float:
        return nx.density(self.graph) if self.graph.number_of_nodes() > 1 else 0.0

    def avg_clustering(self) -> float:
        return nx.average_clustering(self.graph) if self.graph.number_of_nodes() > 2 else 0.0
