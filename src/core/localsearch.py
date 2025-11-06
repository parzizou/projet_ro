# -*- coding: utf-8 -*-
"""
localsearch.py
2-opt intra-route pour améliorer une route (sans changer l'affectation des clients aux autres tournées).

Optimisation:
- Calcul de delta-coût O(1) pour chaque mouvement 2-opt
- Application in-place des inversions, "first improvement" avec redémarrage
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


def _two_opt_delta(route: List[int], i: int, j: int, inst: CVRPInstance) -> int:
    """
    Delta de coût pour inversion du segment [i..j] (inclus), avec retour au dépôt implicite.
    Delta = (a-c) + (b-d) - (a-b) - (c-d) où
      a = route[i-1] ou dépôt si i==0
      b = route[i]
      c = route[j]
      d = route[j+1] ou dépôt si j==len(route)-1
    Retourne un entier (peut être négatif si amélioration).
    """
    dmat = inst.dist
    depot = inst.depot_index
    n = len(route)

    a = depot if i == 0 else route[i - 1]
    b = route[i]
    c = route[j]
    d = depot if j == n - 1 else route[j + 1]

    before = dmat[a][b] + dmat[c][d]
    after = dmat[a][c] + dmat[b][d]
    return after - before


def two_opt_route(route: List[int], inst: CVRPInstance) -> List[int]:
    """
    2-opt rapide intra-route. First-improvement:
    - on parcourt des paires (i, j)
    - si delta < 0, on applique l'inversion in-place, on met à jour le coût courant et on redémarre
    """
    n = len(route)
    if n < 4:
        return route[:]  # trop court pour 2-opt utile

    r = route[:]  # on travaille sur une copie
    best_cost = route_cost_with_depot(r, inst)

    improved = True
    while improved:
        improved = False
        # Parcours des paires; on peut éviter j = i (inutile)
        for i in range(0, n - 2):
            ai = r[i]
            for j in range(i + 1, n - 1):
                # Éviter les inversions adjacentes strictes qui apportent rarement un gain
                # (le delta les gère de toute façon)
                delta = _two_opt_delta(r, i, j, inst)
                if delta < 0:
                    # Appliquer l'inversion in-place
                    r[i : j + 1] = reversed(r[i : j + 1])
                    best_cost += delta
                    improved = True
                    break
            if improved:
                break

    return r