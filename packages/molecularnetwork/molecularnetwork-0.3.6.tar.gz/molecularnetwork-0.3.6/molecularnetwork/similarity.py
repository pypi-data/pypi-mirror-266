""" Similarity Functions """

from rdkit.Chem import DataStructs


class SimilarityCalculator:
    def __init__(self, sim_metric="tanimoto"):
        self.sim_metric = sim_metric
        self.metrics = {
            "asymmetric": DataStructs.AsymmetricSimilarity,
            "braunblanquet": DataStructs.BraunBlanquetSimilarity,
            "cosine": DataStructs.CosineSimilarity,
            "dice": DataStructs.DiceSimilarity,
            "kulczynski": DataStructs.KulczynskiSimilarity,
            "mcconnaughey": DataStructs.McConnaugheySimilarity,
            "onbit": DataStructs.OnBitSimilarity,
            "rogotgoldberg": DataStructs.RogotGoldbergSimilarity,
            "russel": DataStructs.RusselSimilarity,
            "sokal": DataStructs.SokalSimilarity,
            "tanimoto": DataStructs.TanimotoSimilarity,
            "tversky": lambda m1, m2: DataStructs.TverskySimilarity(
                m1, m2, a=0.2, b=0.8
            ),
        }

    def calculate_similarity(self, fp1, fp2):
        return max(
            self.metrics[self.sim_metric](fp1, fp2),
            self.metrics[self.sim_metric](fp2, fp1),
        )
