# -*- coding: utf-8 -*-
"""
localsearch.py
2-opt intra-route pour améliorer une route (sans changer l'affectation des clients aux autres tournées).
"""

from __future__ import annotations
from typing import List
from cvrp_data import CVRPInstance


def route_cost_with_depot(route: List[int], inst: CVRPInstance) -> int:
    """
    Coût d'une route (clients dans l'ordre), en incluant départ et retour dépôt.
    """
    d = inst.dist
    depot = inst.depot_index
    if not route:
        return 0
    cost = d[depot][route[0]]
    for i in range(len(route) - 1):
        cost += d[route[i]][route[i + 1]]
    cost += d[route[-1]][depot]
    return cost


def two_opt_route(route: List[int], inst: CVRPInstance) -> List[int]:
    """
    2-opt simple intra-route. Essaie d'améliorer tant qu'on trouve mieux.
    Retourne potentiellement une nouvelle liste (optimisée).
    """
    if len(route) < 4:
        return route[:]  # trop court pour 2-opt utile

    best = route[:]
    best_cost = route_cost_with_depot(best, inst)
    improved = True

    while improved:
        improved = False
        # On teste toutes les paires (i, j) avec i < j
        for i in range(0, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                # inversion du segment (i..j)
                new_route = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                new_cost = route_cost_with_depot(new_route, inst)
                if new_cost < best_cost:
                    best = new_route
                    best_cost = new_cost
                    improved = True
                    # restart recherche locale à partir de cette meilleure solution
                    break
            if improved:
                break

    return best