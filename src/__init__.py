"""
Package principal du projet CVRP.
Contient les modules de base et les outils d'optimisation.
"""

__version__ = "1.0.0"
__author__ = "Projet RO"

# Imports des modules principaux
from .core.cvrp_data import CVRPInstance, load_cvrp_instance
from .core.ga import genetic_algorithm
from .core.solution import verify_solution

__all__ = [
    'CVRPInstance',
    'load_cvrp_instance', 
    'genetic_algorithm',
    'verify_solution'
]