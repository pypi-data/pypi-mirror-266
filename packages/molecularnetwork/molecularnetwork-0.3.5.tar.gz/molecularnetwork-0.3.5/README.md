# MolecularNetwork

`MolecularNetwork` is a Python package that facilitates the creation of molecular networks based on molecular similarities. It leverages RDKit for molecular operations, and NetworkX for graph operations.

## Features

- **Molecular Descriptors:** Calculate molecular fingerprints using descriptor types (e.g., Morgan fingerprints, MACCS keys, AtomPairs).

- **Similarity Metrics:** Choose from a variety of similarity metrics (e.g., Tanimoto, Cosine, Dice) to quantify molecular similarities.

- **Modularity:** The code is organized into modular components, promoting easy extension and customization.

## Installation

To install the MolecularNetwork package, you can use `pip`. Ensure you have Python and pip installed on your system.

```bash
pip install molecularnetwork
```

## Usage
Here's a simple example of how to use the MolecularNetwork package:

``` python
from molecularnetwork import MolecularNetwork

# Define SMILES strings and classes
smiles_list = ["CCO", "CCN", "CCC", "CCF"]
classes = ["alcohol", "amine", "alkane", "fluoride"]

# Create MolecularNetwork instance
network = MolecularNetwork(descriptor="morgan2", sim_metric="tanimoto", sim_threshold=0.5)

# Generate the molecular network graph
graph = network.create_graph(smiles_list, classes) # network.get_graph() also returns graph

# Save the graph to a file
network.save_graph("test_molecular_network.joblib")

# Read graph from a file
graph = network.read_graph("test_molecular_network.joblib")
```

## Contributing
If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request. I welcome contributions from the community.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
