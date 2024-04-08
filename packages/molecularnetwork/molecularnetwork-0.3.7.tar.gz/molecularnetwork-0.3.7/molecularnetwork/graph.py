"""Generate Molecular Network"""

import networkx
import numpy as np
from joblib import dump, load
from .featurizer import FingerprintCalculator
from .similarity import SimilarityCalculator


class MolecularNetwork:
    def __init__(self, descriptor="morgan2", sim_metric="tanimoto", sim_threshold=0.7):
        self.sim_threshold = sim_threshold
        self.fingerprint_calculator = FingerprintCalculator(descriptor)
        self.similarity_calculator = SimilarityCalculator(sim_metric)
        self.graph = networkx.Graph()

    def _create_graph(self, smiles_list, classes):
        if classes is None:
            classes = np.full(len(smiles_list), 0)
        unique_classes, categorical_labels = self._convert_classes(classes)
        fps = self._calculate_fingerprints(smiles_list)
        self._add_nodes(smiles_list, fps, unique_classes, categorical_labels)
        self._add_edges(fps)

    def _calculate_fingerprints(self, smiles_list):
        return [
            self.fingerprint_calculator.calculate_fingerprint(smi)
            for smi in smiles_list
        ]

    def _convert_classes(self, classes):
        unique_classes = np.unique(classes)
        categorical_labels = np.arange(len(unique_classes))
        class_labels = np.array(
            [categorical_labels[np.where(unique_classes == c)[0][0]] for c in classes]
        )
        return unique_classes, class_labels

    def _add_nodes(self, smiles_list, fps, unique_classes, categorical_labels):
        num_nodes = len(smiles_list)
        nodes = range(num_nodes)
        weighted_nodes = [
            (
                node,
                {
                    "smiles": smiles_list[node],
                    "categorical_label": str(unique_classes[value]),
                    "fp": np.array(fps[node])
                },
            )
            for node, value in zip(nodes, categorical_labels)
        ]
        self.graph.add_nodes_from(weighted_nodes)

    def _add_edges(self, fps):
        num_nodes = len(fps)
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                sim_val = self._calculate_similarity(fps[i], fps[j])
                if sim_val > self.sim_threshold:
                    self.graph.add_edge(i, j, weight=sim_val)

    def _calculate_similarity(self, fp1, fp2):
        return self.similarity_calculator.calculate_similarity(fp1, fp2)

    def create_graph(self, smiles_list, classes=None):
        self._create_graph(smiles_list, classes)
        return self.graph

    def get_network(self):
        return self.graph

    def save_graph(self, graph_filename: str):
        dump(self.graph, graph_filename)

    def read_graph(self, graph_filename: str):
        self.graph = load(graph_filename)
        return self.graph
