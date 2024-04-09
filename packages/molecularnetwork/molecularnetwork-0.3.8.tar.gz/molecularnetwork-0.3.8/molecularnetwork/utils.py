"""Utils for molecularnetwork"""


class InvalidSMILESError(Exception):
    """
    Exception raised when an invalid SMILES string is encountered.

    Attributes:

        message (str): Explanation of the error.
    """
