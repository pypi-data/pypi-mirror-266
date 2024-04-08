"""test"""

import pandas as pd
from molecularnetwork import MolecularNetwork


df = pd.read_csv("test.csv")
molnet = MolecularNetwork()
molnet.create_graph(df["canonical_smiles"].values, df["active"].values)
molnet.save_graph("test")
net = molnet.read_graph("test")
print(net)
