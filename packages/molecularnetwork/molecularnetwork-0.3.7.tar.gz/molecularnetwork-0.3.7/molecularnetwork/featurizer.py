"""Molecular Featurization Pipeline"""

from rdkit import Chem
from rdkit.Chem import AllChem, MACCSkeys, DataStructs
from rdkit.Chem.Fingerprints import FingerprintMols
from rdkit.Chem.AtomPairs import Pairs, Torsions

from .utils import InvalidSMILESError


class FingerprintCalculator:
    def __init__(self, descriptor="morgan2"):
        self.descriptor = descriptor
        self.descriptors = {
            "atompairs": lambda m: Pairs.GetAtomPairFingerprint(m),
            "maccs": lambda m: MACCSkeys.GenMACCSKeys(m),
            "morgan2": lambda m: AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048),
            "morgan3": lambda m: AllChem.GetMorganFingerprintAsBitVect(m, 3, 2048),
            "rdkit": lambda m: FingerprintMols.FingerprintMol(m),
            "topo": lambda m: Torsions.GetTopologicalTorsionFingerprint(m),
        }

    def calculate_fingerprint(self, smi):
        mol = Chem.MolFromSmiles(smi)
        if mol:
            fn = self.descriptors[self.descriptor]
            return fn(mol)
        raise InvalidSMILESError
