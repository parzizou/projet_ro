# -*- coding: utf-8 -*-
"""
cvrp_data.py
Parseur CVRPLIB pour instances CVRP (format TSPLIB-like).
Génère une instance prête à l'emploi: coordonnées, demandes, capacité, dépôt, matrice de distances.

Fonction principale: load_cvrp_instance(path)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict
import math
import re


@dataclass
class CVRPInstance:
    name: str
    dimension: int
    capacity: int
    depot_index: int  # index 0-based dans les tableaux coords/demands
    coords: List[Tuple[float, float]]  # coords[i] = (x, y)
    demands: List[int]                 # demands[i]
    dist: List[List[int]]              # dist[i][j] distances entières EUC_2D


def _parse_key_value(line: str) -> Tuple[str, str]:
    if ":" in line:
        k, v = line.split(":", 1)
        return k.strip().upper(), v.strip()
    else:
        parts = line.strip().split()
        if len(parts) >= 2:
            return parts[0].strip().upper(), " ".join(parts[1:]).strip()
    return line.strip().upper(), ""


def _euc2d_round(d: float) -> int:
    # TSPLIB rounding
    return int(d + 0.5)


def _build_dist_matrix(coords: List[Tuple[float, float]]) -> List[List[int]]:
    n = len(coords)
    dist = [[0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = coords[i]
        for j in range(i + 1, n):
            xj, yj = coords[j]
            d = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
            dij = _euc2d_round(d)
            dist[i][j] = dij
            dist[j][i] = dij
    return dist


def load_cvrp_instance(path: str) -> CVRPInstance:
    """
    Lit un fichier .vrp CVRPLIB et renvoie une instance CVRPInstance prête à l'emploi.
    Gère l'ordre d'indexation pour mettre le dépôt à l'index 0, les clients ensuite.
    """
    name = ""
    dimension = None
    capacity = None
    edge_weight_type = None

    coords_by_id: Dict[int, Tuple[float, float]] = {}
    demands_by_id: Dict[int, int] = {}
    depots_ids: List[int] = []

    section = None  # "NODE_COORD_SECTION", "DEMAND_SECTION", "DEPOT_SECTION"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            upper = line.upper()

            # Fin de sections
            if upper == "EOF":
                break

            # Détection de sections
            if upper.startswith("NODE_COORD_SECTION"):
                section = "NODE_COORD_SECTION"
                continue
            if upper.startswith("DEMAND_SECTION"):
                section = "DEMAND_SECTION"
                continue
            if upper.startswith("DEPOT_SECTION"):
                section = "DEPOT_SECTION"
                continue

            # En-têtes
            if section is None:
                key, val = _parse_key_value(line)
                if key == "NAME":
                    name = val
                elif key == "DIMENSION":
                    dimension = int(val)
                elif key == "CAPACITY":
                    capacity = int(val)
                elif key == "EDGE_WEIGHT_TYPE":
                    edge_weight_type = val.upper()
                # On ignore le reste des méta-données
                continue

            # Sections
            if section == "NODE_COORD_SECTION":
                # Format: id x y
                parts = re.split(r"\s+", line)
                if len(parts) >= 3:
                    idx = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    coords_by_id[idx] = (x, y)
                continue

            if section == "DEMAND_SECTION":
                # Format: id demand
                parts = re.split(r"\s+", line)
                if len(parts) >= 2:
                    idx = int(parts[0])
                    dmd = int(parts[1])
                    demands_by_id[idx] = dmd
                continue

            if section == "DEPOT_SECTION":
                # Liste d'ids du dépôt, terminée par -1
                val = int(line)
                if val == -1:
                    section = None
                else:
                    depots_ids.append(val)
                continue

    if dimension is None or capacity is None:
        raise ValueError("DIMENSION ou CAPACITY manquant dans le fichier .vrp")
    if not coords_by_id or not demands_by_id:
        raise ValueError("Sections NODE_COORD_SECTION ou DEMAND_SECTION absentes/incomplètes")
    if not depots_ids:
        raise ValueError("DEPOT_SECTION absente/incomplète")

    if edge_weight_type and edge_weight_type not in ("EUC_2D", "CEIL_2D"):
        # On gère EUC_2D; CEIL_2D est proche mais ici on applique EUC_2D round TSPLIB
        # (Pour beaucoup d'instances CVRPLIB, EUC_2D est utilisé)
        pass

    depot_id = depots_ids[0]

    # On construit un mapping pour mettre le dépôt à l'index 0
    all_ids = list(sorted(coords_by_id.keys()))
    if depot_id not in all_ids:
        raise ValueError("Depot id non trouvé dans les coordonnées")

    # Ordre: [depot] + [autres ids triés]
    other_ids = [i for i in all_ids if i != depot_id]
    ordered_ids = [depot_id] + other_ids

    index_of_id = {node_id: idx for idx, node_id in enumerate(ordered_ids)}

    coords = [None] * len(ordered_ids)
    demands = [0] * len(ordered_ids)

    for node_id in ordered_ids:
        idx = index_of_id[node_id]
        coords[idx] = coords_by_id[node_id]
        # le dépôt a généralement demande 0, par sécurité on force 0
        demands[idx] = 0 if node_id == depot_id else demands_by_id[node_id]

    dist = _build_dist_matrix(coords)

    instance = CVRPInstance(
        name=name or "CVRPInstance",
        dimension=len(ordered_ids),
        capacity=capacity,
        depot_index=0,
        coords=coords,
        demands=demands,
        dist=dist,
    )
    return instance