"""
progression_qc est un compilateur/validateur pour la production de d'exercices pour Progression. progression_qc reçoit sur l'entrée standard ou en paramètre un fichier YAML contenant la description d'une question et reproduit sur la sortie standard le résultat traité et validé.
"""

import os
from pathlib import Path

path = Path(__file__).parent / "VERSION"
with open(path) as f:
    __version__ = f.read()[8:]
__author__ = "Patrick Lafrance"
