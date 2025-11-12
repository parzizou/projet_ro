# -*- coding: utf-8 -*-
"""
multi_depot.py
Mode Multi-Dépôts Multi-Types (A,B,C,...) par-dessus le CVRP existant.

- Le dépôt d'origine (du .vrp/.vrplib) devient le dépôt A (type 'A'), position réelle.
- On génère K-1 autres dépôts aléatoires dans la bounding box.
- Types des dépôts: 'A' pour l'original, puis on boucle sur l'alphabet fourni pour les autres (B, C, D, ...).
- Types des clients: tirés aléatoirement parmi les types présents côté dépôts (garantit des candidats).
- Chaque client est affecté au dépôt du même type le plus proche (euclidien).
- On résout un CVRP par dépôt via le GA existant (inchangé).
- Plot multi: option connect_depot pour tracer dépôt->route->dépôt.

Ce module est opt-in depuis main(multi=True, ...).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import random
import math

from cvrp_data import CVRPInstance
from ga import genetic_algorithm
from solution import solution_total_cost


@dataclass
class DepotSpec:
    idx: int
    coord: Tuple[float, float]
    type_char: str


@dataclass
class MultiDepotConfig:
    k_depots: int = 4
    types_alphabet: str = "ABCD"
    seed: int = 123
    capacity_override: Optional[int] = None  # None => utilise la capacité de l'instance de base
    connect_depot_on_plot: bool = False


@dataclass
class SubInstance:
    depot: DepotSpec
    inst: CVRPInstance
    # mapping index_sub -> index_original (dans l'instance base inst_base)
    original_index_from_subindex: List[int]


@dataclass
class SubResult:
    depot: DepotSpec
    routes_subindex: List[List[int]]  # routes avec indices de la sous-instance (sans dépôt)
    routes_baseindex: List[List[int]]  # routes remappées vers indices de l'instance de base
    cost: int


@dataclass
class MultiDepotScenario:
    depots: List[DepotSpec]
    client_type: Dict[int, str]     # base_idx -> type char
    assigned_depot: Dict[int, int]  # base_idx -> depot.idx
    subinstances: List[SubInstance]


def _bbox(coords: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    xs = [x for (x, y) in coords]
    ys = [y for (x, y) in coords]
    return min(xs), max(xs), min(ys), max(ys)


def _euclid(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _build_dist_matrix(coords: List[Tuple[float, float]]) -> List[List[int]]:
    # Euclidienne arrondie façon TSPLIB
    def _round_tsplib(d: float) -> int:
        return int(d + 0.5)
    n = len(coords)
    dist = [[0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = coords[i]
        for j in range(i + 1, n):
            xj, yj = coords[j]
            d = math.hypot(xi - xj, yi - yj)
            dij = _round_tsplib(d)
            dist[i][j] = dij
            dist[j][i] = dij
    return dist


def _gen_depots_with_original_first(inst_base: CVRPInstance, cfg: MultiDepotConfig, rng: random.Random) -> List[DepotSpec]:
    """
    Construit la liste des dépôts:
    - d0 = dépôt original (coordonnée réelle) avec type 'A'
    - d1..dK-1 random dans la bbox, types attribués en bouclant sur cfg.types_alphabet à partir de B
    """
    minx, maxx, miny, maxy = _bbox(inst_base.coords)
    dx = maxx - minx
    dy = maxy - miny
    # marge 5%
    minx -= 0.05 * dx
    maxx += 0.05 * dx
    miny -= 0.05 * dy
    maxy += 0.05 * dy

    alphabet = cfg.types_alphabet or "ABCD"
    if "A" not in alphabet:
        alphabet = "A" + "".join(ch for ch in alphabet if ch != "A")

    depots: List[DepotSpec] = []

    # d0 = dépôt original en 'A'
    base_idx = inst_base.depot_index
    base_coord = inst_base.coords[base_idx]
    depots.append(DepotSpec(idx=0, coord=base_coord, type_char="A"))

    # Autres dépôts
    for i in range(1, max(1, cfg.k_depots)):
        x = rng.uniform(minx, maxx)
        y = rng.uniform(miny, maxy)
        # Type: on déroule l'alphabet à partir de l'offset 1 (B si "ABCD")
        t = alphabet[i % len(alphabet)]
        depots.append(DepotSpec(idx=i, coord=(x, y), type_char=t))

    return depots


def _assign_client_types_from_available(
    inst_base: CVRPInstance,
    depots: List[DepotSpec],
    rng: random.Random,
) -> Dict[int, str]:
    """
    Assigne un type à chaque client, aléatoire uniforme sur les types réellement présents côté dépôts.
    """
    types_present = sorted(set(d.type_char for d in depots))
    depot0 = inst_base.depot_index
    client_type: Dict[int, str] = {}
    for i in range(inst_base.dimension):
        if i == depot0:
            continue
        client_type[i] = rng.choice(types_present)
    return client_type


def _assign_clients_to_depots(
    inst_base: CVRPInstance,
    depots: List[DepotSpec],
    client_type: Dict[int, str],
) -> Dict[int, int]:
    assigned: Dict[int, int] = {}
    for c_idx, t in client_type.items():
        c_coord = inst_base.coords[c_idx]
        candidates = [d for d in depots if d.type_char == t]
        if not candidates:
            raise RuntimeError(f"Aucun dépôt pour le type {t}")
        best = min(candidates, key=lambda d: _euclid(c_coord, d.coord))
        assigned[c_idx] = best.idx
    return assigned


def _make_subinstance_for_depot(
    inst_base: CVRPInstance,
    depot: DepotSpec,
    assigned_depot: Dict[int, int],
    capacity: int,
) -> Optional[SubInstance]:
    depot0 = inst_base.depot_index
    clients_for_depot = [i for i, did in assigned_depot.items() if did == depot.idx]
    if not clients_for_depot:
        return None

    coords_sub: List[Tuple[float, float]] = [depot.coord] + [inst_base.coords[i] for i in clients_for_depot]
    demands_sub: List[int] = [0] + [inst_base.demands[i] for i in clients_for_depot]
    dist_sub = _build_dist_matrix(coords_sub)

    inst_sub = CVRPInstance(
        name=f"{inst_base.name}-MD(d{depot.idx}-{depot.type_char})",
        dimension=len(coords_sub),
        capacity=capacity,
        depot_index=0,
        coords=coords_sub,
        demands=demands_sub,
        dist=dist_sub,
    )
    original_index_from_subindex = [None] * inst_sub.dimension  # type: ignore
    # 0 = référence au dépôt "base" (pas utilisé dans les routes, juste pour info)
    original_index_from_subindex[0] = depot0
    for k, orig in enumerate(clients_for_depot, start=1):
        original_index_from_subindex[k] = orig

    return SubInstance(
        depot=depot,
        inst=inst_sub,
        original_index_from_subindex=original_index_from_subindex,  # type: ignore
    )


def build_multi_depot_scenario(inst_base: CVRPInstance, cfg: MultiDepotConfig) -> MultiDepotScenario:
    rng = random.Random(cfg.seed)
    depots = _gen_depots_with_original_first(inst_base, cfg, rng)
    client_type = _assign_client_types_from_available(inst_base, depots, rng)
    assigned = _assign_clients_to_depots(inst_base, depots, client_type)

    cap = cfg.capacity_override if (cfg.capacity_override and cfg.capacity_override > 0) else inst_base.capacity

    subinstances: List[SubInstance] = []
    for d in depots:
        si = _make_subinstance_for_depot(inst_base, d, assigned, cap)
        if si is not None:
            subinstances.append(si)

    return MultiDepotScenario(
        depots=depots,
        client_type=client_type,
        assigned_depot=assigned,
        subinstances=subinstances,
    )


def _remap_routes_to_base_indices(
    routes_sub: List[List[int]],
    subinst: SubInstance,
) -> List[List[int]]:
    mapping = subinst.original_index_from_subindex
    routes_base: List[List[int]] = []
    for r in routes_sub:
        rb = []
        for idx_sub in r:
            if idx_sub == 0:
                continue
            rb.append(mapping[idx_sub])
        routes_base.append(rb)
    return routes_base


def solve_multi_depot(
    inst_base: CVRPInstance,
    scenario: MultiDepotScenario,
    ga_pop_size: int,
    ga_pm: float,
    ga_pc: float,
    ga_two_opt_prob: float,
    init_mode: str = "nn_plus_random",
    verbose_ga: bool = True,
    ga_time_limit_sec: float | None = None,
) -> List[SubResult]:
    results: List[SubResult] = []
    for si in scenario.subinstances:
        if verbose_ga:
            print(f"[MD] Dépôt d{si.depot.idx} type={si.depot.type_char} | Nclients={si.inst.dimension - 1}")
        best = genetic_algorithm(
            si.inst,
            pop_size=ga_pop_size,
            pm=ga_pm,
            pc=ga_pc,
            two_opt_prob=ga_two_opt_prob,
            use_2opt=(ga_two_opt_prob > 0.0),
            target_optimum=None,
            init_mode=init_mode,
            verbose=verbose_ga,
            time_limit_sec=float(ga_time_limit_sec) if ga_time_limit_sec is not None else 20000.0,
        )
        routes_sub = best.routes
        cost = solution_total_cost(routes_sub, si.inst)
        routes_base = _remap_routes_to_base_indices(routes_sub, si)
        results.append(SubResult(
            depot=si.depot,
            routes_subindex=routes_sub,
            routes_baseindex=routes_base,
            cost=cost,
        ))
    return results


def write_multi_depot_solutions(
    base_label: str,
    inst_base: CVRPInstance,
    results: List[SubResult],
    original_id_from_baseindex: List[int],
) -> str:
    """
    Écrit un .sol par dépôt et un .sol agrégé. Retourne le chemin du .sol agrégé.
    """
    total = 0
    for res in results:
        total += res.cost
        dep_id = res.depot.idx
        path_dep = f"solution_{base_label}_md_d{dep_id}_{res.depot.type_char}.sol"
        lines = []
        for k, r in enumerate(res.routes_baseindex, start=1):
            seq = [str(original_id_from_baseindex[i]) for i in r]
            lines.append(f"Route #{k} (Depot d{dep_id} {res.depot.type_char}): " + " ".join(seq))
        lines.append(f"Cost {res.cost}")
        with open(path_dep, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[MD] Solution dépôt d{dep_id} écrite: {path_dep}")

    # Fichier agrégé
    agg_path = f"solution_{base_label}_multi_depots.sol"
    lines = []
    kglob = 1
    for res in results:
        lines.append(f";;; Depot d{res.depot.idx} type={res.depot.type_char} ;;;")
        for r in res.routes_baseindex:
            seq = [str(original_id_from_baseindex[i]) for i in r]
            lines.append(f"Route #{kglob}: " + " ".join(seq))
            kglob += 1
    lines.append(f"Cost {sum(res.cost for res in results)}")
    with open(agg_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[MD] Solution agrégée écrite: {agg_path}")
    return agg_path


def run_multi_depot_pipeline(
    inst_base: CVRPInstance,
    original_id_from_baseindex: List[int],
    base_label: str,
    cfg: MultiDepotConfig,
    ga_pop_size: int,
    ga_pm: float,
    ga_pc: float,
    ga_two_opt_prob: float,
    init_mode: str = "nn_plus_random",
    verbose_ga: bool = True,
    do_plot: bool = True,
    ga_time_limit_sec: float | None = None,
):
    # 1) Scénario (dépôts/clients/types/assignations)
    scenario = build_multi_depot_scenario(inst_base, cfg)

    # 2) Résolution CVRP indépendante par dépôt
    results = solve_multi_depot(
        inst_base,
        scenario,
        ga_pop_size=ga_pop_size,
        ga_pm=ga_pm,
        ga_pc=ga_pc,
        ga_two_opt_prob=ga_two_opt_prob,
        init_mode=init_mode,
        verbose_ga=verbose_ga,
        ga_time_limit_sec=ga_time_limit_sec,
    )

    # 3) Exports .sol
    agg_path = write_multi_depot_solutions(
        base_label=base_label,
        inst_base=inst_base,
        results=results,
        original_id_from_baseindex=original_id_from_baseindex,
    )

    # 4) Plot agrégé
    if do_plot:
        try:
            from plot import plot_solution_multi
            routes_by_depot: Dict[int, List[List[int]]] = {}
            for res in results:
                routes_by_depot[res.depot.idx] = res.routes_baseindex
            plot_solution_multi(
                inst=inst_base,
                depots=[(d.idx, d.coord, d.type_char) for d in scenario.depots],
                routes_by_depot=routes_by_depot,
                title=f"{inst_base.name} (multi-dépôts/types) | coût total={sum(r.cost for r in results)}",
                connect_depot=cfg.connect_depot_on_plot,
            )
        except ImportError:
            print("[MD] matplotlib non installé: pas de graphique (pip install matplotlib).")

    return {
        "total_cost": sum(r.cost for r in results),
        "per_depot": [
            {
                "depot_idx": r.depot.idx,
                "type": r.depot.type_char,
                "routes_count": len(r.routes_baseindex),
                "cost": r.cost,
            }
            for r in results
        ],
        "solution_aggregate_path": agg_path,
    }