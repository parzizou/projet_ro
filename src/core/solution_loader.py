# -*- coding: utf-8 -*-
"""
solution_loader.py
Charge les solutions de référence depuis les fichiers .sol
"""

import os
import re
from typing import Optional, Tuple, List


def load_solution_from_file(solution_path: str) -> Tuple[Optional[int], Optional[List[List[int]]]]:
    """
    Charge une solution depuis un fichier .sol
    
    Args:
        solution_path: Chemin vers le fichier .sol
        
    Returns:
        Tuple (cost, routes) où:
        - cost: Coût de la solution (None si non trouvé)
        - routes: Liste de routes (None si non trouvées)
    """
    if not os.path.exists(solution_path):
        return None, None
    
    cost = None
    routes = []
    
    try:
        with open(solution_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Chercher le coût
                if line.lower().startswith('cost'):
                    # Format: "Cost 22901" ou "Cost: 22901"
                    match = re.search(r'cost\s*:?\s*(\d+)', line, re.IGNORECASE)
                    if match:
                        cost = int(match.group(1))
                
                # Chercher les routes
                elif line.lower().startswith('route'):
                    # Format: "Route #1: 96 43 83 18 116 58 54"
                    match = re.search(r'route\s*#?\d+\s*:\s*([\d\s]+)', line, re.IGNORECASE)
                    if match:
                        route_str = match.group(1).strip()
                        if route_str:
                            route = [int(x) for x in route_str.split()]
                            routes.append(route)
    
    except Exception as e:
        print(f"⚠️  Erreur lors de la lecture de {solution_path}: {e}")
        return None, None
    
    return cost, routes if routes else None


def find_solution_for_instance(instance_path: str, solutions_dir: str = "data/solutions") -> Optional[int]:
    """
    Trouve la solution de référence pour une instance donnée.
    
    Args:
        instance_path: Chemin vers le fichier .vrp
        solutions_dir: Répertoire contenant les solutions
        
    Returns:
        Coût de la solution de référence (None si non trouvé)
    """
    # Extraire le nom de l'instance
    instance_name = os.path.splitext(os.path.basename(instance_path))[0]
    
    # Chercher le fichier solution correspondant
    solution_candidates = [
        os.path.join(solutions_dir, f"solution_{instance_name}.sol"),
        os.path.join(solutions_dir, f"{instance_name}.sol"),
        os.path.join(solutions_dir, f"solution_data.sol"),  # Solution par défaut
    ]
    
    for sol_path in solution_candidates:
        if os.path.exists(sol_path):
            cost, _ = load_solution_from_file(sol_path)
            if cost is not None:
                print(f"✅ Solution de référence trouvée: {sol_path}")
                print(f"   Coût optimal: {cost}")
                return cost
    
    print(f"⚠️  Aucune solution de référence trouvée pour {instance_name}")
    return None


if __name__ == "__main__":
    # Test
    print("Test du chargement de solution:\n")
    
    cost, routes = load_solution_from_file("data/solutions/solution_data.sol")
    
    if cost:
        print(f"✅ Coût: {cost}")
        print(f"✅ Nombre de routes: {len(routes) if routes else 0}")
        if routes:
            print(f"\nExemple de routes:")
            for i, route in enumerate(routes[:3], 1):
                print(f"  Route #{i}: {route}")
    else:
        print("❌ Échec du chargement")
