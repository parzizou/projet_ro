# -*- coding: utf-8 -*-
"""
solution.py
Outils autour des solutions VRP:
- calcul du coût total
- vérification des contraintes
- texte lisible (proche CVRPLIB)
- lecture d'un .sol texte et calcul du coût
"""

from __future__ import annotations
from typing import List, Tuple, Optional
from .cvrp_data import CVRPInstance


def solution_total_cost(routes: List[List[int]], inst: CVRPInstance) -> int:
    d = inst.dist
    depot = inst.depot_index
    total = 0
    for r in routes:
        if not r:
            continue
        total += d[depot][r[0]]
        for i in range(len(r) - 1):
            total += d[r[i]][r[i + 1]]
        total += d[r[-1]][depot]
    return total


def verify_solution(routes: List[List[int]], inst: CVRPInstance) -> Tuple[bool, List[str]]:
    """
    Vérifie contraintes:
    - chaque client visité exactement une fois
    - chaque route respecte la capacité
    - départ/retour dépôt implicites
    """
    n = inst.dimension
    depot = inst.depot_index
    dem = inst.demands

    visited = [False] * n
    visited[depot] = True  # on ignore le dépôt
    msgs: List[str] = []

    for idx, r in enumerate(routes, start=1):
        load = 0
        for c in r:
            if c == depot:
                msgs.append(f"Route #{idx}: client == depot trouvé (à ignorer)")
                continue
            if visited[c]:
                msgs.append(f"Client {c} visité plus d'une fois (route #{idx}).")
            visited[c] = True
            load += dem[c]
        if load > inst.capacity:
            msgs.append(f"Route #{idx}: capacité dépassée ({load} > {inst.capacity}).")

    # Tous clients sauf depot doivent être visités
    for c in range(n):
        if c == depot:
            continue
        if not visited[c]:
            msgs.append(f"Client {c} non visité.")

    return (len(msgs) == 0), msgs


def write_solution_text(
    routes: List[List[int]],
    inst: CVRPInstance,
    path: str,
    include_depot: bool = False,
    original_id_from_index: Optional[List[int]] = None,
) -> None:
    """
    Écrit un fichier solution lisible.
    - Par défaut on affiche les IDs "internes" (0-based, depot=0). Tu peux passer original_id_from_index
      pour mapper vers les IDs originaux du fichier .vrp (1-based en général).
    - include_depot: si True, on affiche dépôt au début/fin des routes.
    """
    def fmt_idx(i: int) -> str:
        if original_id_from_index:
            return str(original_id_from_index[i])
        return str(i)

    lines = []
    for k, r in enumerate(routes, start=1):
        seq = []
        if include_depot:
            seq.append(fmt_idx(inst.depot_index))
        seq += [fmt_idx(i) for i in r]
        if include_depot:
            seq.append(fmt_idx(inst.depot_index))
        lines.append(f"Route #{k}: " + " ".join(seq))

    total = solution_total_cost(routes, inst)
    lines.append(f"Cost {total}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def read_simple_sol_and_cost(
    sol_path: str,
    inst: CVRPInstance,
    assume_includes_depot: bool = False,
    index_from_original_id: Optional[dict] = None,
) -> int:
    """
    Lit un fichier .sol texte simple contenant des lignes "Route #i: <ids>" et une ligne "Cost <val>" optionnelle.
    Calcule le coût avec la métrique de l'instance 'inst'.
    - if index_from_original_id est fourni, on mappe les IDs du .sol vers les indices internes.
    - assume_includes_depot: si True, les numéros incluent le dépôt au début/fin de chaque route.
    Retourne le coût total selon la matrice de distance de l'instance.
    """
    routes: List[List[int]] = []
    with open(sol_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.upper().startswith("ROUTE"):
                # Format: "Route #k: a b c ..."
                if ":" not in line:
                    continue
                parts = line.split(":", 1)[1].strip().split()
                seq = []
                for tok in parts:
                    try:
                        nid = int(tok)
                    except:
                        continue
                    if index_from_original_id:
                        if nid not in index_from_original_id:
                            raise ValueError(f"ID {nid} absent du mapping original -> index interne")
                        idx = index_from_original_id[nid]
                    else:
                        idx = nid
                    seq.append(idx)
                if assume_includes_depot:
                    # retirer depot au début/fin si présent
                    dep = inst.depot_index
                    if seq and seq[0] == dep:
                        seq = seq[1:]
                    if seq and seq[-1] == dep:
                        seq = seq[:-1]
                routes.append(seq)

    return solution_total_cost(routes, inst)