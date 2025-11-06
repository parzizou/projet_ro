"""
Module core : Algorithmes de base pour CVRP.
Contient l'algorithme génétique, le chargement d'instances, 
la gestion des solutions et les algorithmes de recherche locale.
"""

from .cvrp_data import CVRPInstance, load_cvrp_instance
from .ga import genetic_algorithm
from .solution import verify_solution, solution_total_cost

__all__ = [
    'CVRPInstance',
    'load_cvrp_instance',
    'genetic_algorithm', 
    'verify_solution',
    'solution_total_cost'
]