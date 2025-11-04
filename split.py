# -*- coding: utf-8 -*-
"""
split.py
Algorithme de split (programmation dynamique) pour transformer une permutation globale
des clients (giant tour) en routes faisables qui respectent la capacité.

Entrée: permutation des indices clients (hors dépôt)
Sortie: liste de routes (chaque route = liste d'indices clients, hors dépôt)
"""

from __future__ import annotations
from typing import List
from cvrp_data import CVRPInstance


def split_giant_tour(perm: List[int], inst: CVRPInstance) -> List[List[int]]:
    """
    Split DP standard:
    - On considère des arcs de i -> j représentant une tournée faisable
      depot -> perm[i] -> ... -> perm[j] -> depot
    - On calcule le plus court chemin de 0 à n dans ce DAG implicite.

    perm: liste des indices clients (0-based) SANS le dépôt
    Retourne: list de routes (listes d'indices clients, sans le dépôt)
    """
    n = len(perm)
    INF = 10 ** 18
    cost = [INF] * (n + 1)
    pred = [-1] * (n + 1)
    cost[0] = 0

    C = inst.capacity
    depot = inst.depot_index
    d = inst.dist
    dem = inst.demands

    for i in range(n):
        load = 0
        if i >= 0:
            # coût de démarrer la tournée au client perm[i]
            last = perm[i]
            load += dem[last]
            if load > C:
                continue
            # distance depot -> premier client
            seg_cost = d[depot][last]

            # cas j == i
            best = cost[i] + seg_cost + d[last][depot]
            if best < cost[i + 1]:
                cost[i + 1] = best
                pred[i + 1] = i

            # j > i
            for j in range(i + 1, n):
                node = perm[j]
                load += dem[node]
                if load > C:
                    break
                seg_cost += d[last][node]
                last = node
                total = cost[i] + seg_cost + d[last][depot]
                if total < cost[j + 1]:
                    cost[j + 1] = total
                    pred[j + 1] = i

    # Reconstruction
    if cost[n] >= INF:
        # Si cela arrive, c'est qu'il y a un souci de capacité globale (ne devrait pas sur une instance CVRP standard)
        raise RuntimeError("Impossible de splitter la permutation en tournées faisables (capacité trop faible ?)")

    routes: List[List[int]] = []
    t = n
    while t > 0:
        i = pred[t]
        if i == -1:
            raise RuntimeError("Échec reconstruction split (pred manquant)")
        route = perm[i:t]
        routes.append(route)
        t = i
    routes.reverse()
    return routes