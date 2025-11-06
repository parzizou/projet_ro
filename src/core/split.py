# -*- coding: utf-8 -*-
"""
split.py
Algorithme de split (programmation dynamique) pour transformer une permutation globale
des clients (giant tour) en routes faisables qui respectent la capacité.

Entrée: permutation des indices clients (hors dépôt)
Sortie: liste de routes (chaque route = liste d'indices clients, hors dépôt)

Accélération:
- Si Numba est disponible, on JIT-compile le coeur DP pour accélérer fortement le split.
- Sinon, on utilise le fallback Python inchangé.
"""

from __future__ import annotations
from typing import List
from .cvrp_data import CVRPInstance

# ======== Option accélérée via Numba (auto si dispo) ========
_NUMBA_AVAILABLE = False
try:
    import numpy as np
    from numba import njit

    @njit(cache=True)
    def _split_dp_numba(
        perm: np.ndarray,           # int64 [n]
        dist: np.ndarray,           # int64 [N, N]
        demands: np.ndarray,        # int64 [N]
        depot: int,                 # scalaire
        capacity: int               # scalaire
    ):
        """
        Calcule le DP du split:
        - Retourne (pred, last_cost) où pred est int64 [n+1], last_cost = cost[n]
        - Reconstruction des routes faite côté Python.
        """
        n = perm.shape[0]
        INF = 10**15
        cost = np.empty(n + 1, dtype=np.int64)
        pred = np.empty(n + 1, dtype=np.int64)
        for i in range(n + 1):
            cost[i] = INF
            pred[i] = -1
        cost[0] = 0

        for i in range(n):
            load = 0
            last = perm[i]
            load += demands[last]
            if load > capacity:
                continue
            seg_cost = dist[depot, last]

            # cas j == i
            total = cost[i] + seg_cost + dist[last, depot]
            if total < cost[i + 1]:
                cost[i + 1] = total
                pred[i + 1] = i

            # cas j > i
            for j in range(i + 1, n):
                node = perm[j]
                load += demands[node]
                if load > capacity:
                    break
                seg_cost += dist[last, node]
                last = node
                total = cost[i] + seg_cost + dist[last, depot]
                if total < cost[j + 1]:
                    cost[j + 1] = total
                    pred[j + 1] = i

        return pred, cost[n]

    _NUMBA_AVAILABLE = True
except Exception:
    _NUMBA_AVAILABLE = False


def _ensure_np_arrays(inst: CVRPInstance):
    """
    Prépare et cache des versions numpy int64 de dist/demands pour le fast path Numba.
    """
    import numpy as _np
    if not hasattr(inst, "_dist_np"):
        inst._dist_np = _np.asarray(inst.dist, dtype=_np.int64)
    if not hasattr(inst, "_demands_np"):
        inst._demands_np = _np.asarray(inst.demands, dtype=_np.int64)


def split_giant_tour(perm: List[int], inst: CVRPInstance) -> List[List[int]]:
    """
    Split DP standard:
    - On considère des arcs de i -> j représentant une tournée faisable
      depot -> perm[i] -> ... -> perm[j] -> depot
    - On calcule le plus court chemin de 0 à n dans ce DAG implicite.

    perm: liste des indices clients (0-based) SANS le dépôt
    Retourne: list de routes (listes d'indices clients, sans le dépôt)
    """
    # Fast path Numba si dispo
    if _NUMBA_AVAILABLE:
        _ensure_np_arrays(inst)
        import numpy as _np
        perm_arr = _np.asarray(perm, dtype=_np.int64)
        pred, last_cost = _split_dp_numba(
            perm_arr,
            inst._dist_np,     # type: ignore[attr-defined]
            inst._demands_np,  # type: ignore[attr-defined]
            int(inst.depot_index),
            int(inst.capacity),
        )
        INF = 10**15
        if last_cost >= INF:
            raise RuntimeError("Impossible de splitter la permutation en tournées faisables (capacité trop faible ?)")
        # Reconstruction en Python
        routes: List[List[int]] = []
        t = len(perm)
        while t > 0:
            i = int(pred[t])
            if i == -1:
                raise RuntimeError("Échec reconstruction split (pred manquant)")
            route = perm[i:t]
            routes.append(route)
            t = i
        routes.reverse()
        return routes

    # ======== Fallback pur Python (ancien code) ========
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