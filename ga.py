# -*- coding: utf-8 -*-
"""
ga.py
Algorithme génétique pour le CVRP:
- Représentation: permutation globale des clients (giant tour)
- Split DP pour obtenir des tournées faisables
- 2-opt intra-route optionnel (probabiliste pour gagner du temps)
- Sélection par tournoi, crossover OX, mutation swap/inversion
- Limite de temps pour garantir < ~3 minutes par défaut
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import random
import time

from cvrp_data import CVRPInstance
from split import split_giant_tour
from localsearch import two_opt_route
from solution import solution_total_cost


@dataclass
class Individual:
    perm: List[int]            # permutation des clients (hors dépôt)
    routes: List[List[int]]    # routes faisables (à partir de perm via split)
    cost: int                  # coût total des routes


def nearest_neighbor_perm(inst: CVRPInstance, rng: random.Random) -> List[int]:
    """
    Construction heuristique simple: nearest neighbor depuis le dépôt,
    en ignorant temporairement les capacités (le split fera la faisabilisation).
    """
    depot = inst.depot_index
    n = inst.dimension
    clients = [i for i in range(n) if i != depot]
    unvisited = set(clients)
    curr = depot
    perm: List[int] = []

    while unvisited:
        nxt = min(unvisited, key=lambda j: inst.dist[curr][j])
        perm.append(nxt)
        unvisited.remove(nxt)
        curr = nxt
    return perm


def order_crossover(p1: List[int], p2: List[int], rng: random.Random) -> Tuple[List[int], List[int]]:
    """
    OX (Order Crossover) standard.
    Prend deux parents permutation et renvoie deux enfants.
    """
    n = len(p1)
    if n < 2:
        return p1[:], p2[:]
    i, j = sorted(rng.sample(range(n), 2))
    seg1 = p1[i:j]
    seg2 = p2[i:j]

    def build_child(seg, donor):
        child = [None] * n
        child[i:j] = seg
        fill_vals = [x for x in donor if x not in seg]
        k = 0
        for idx in list(range(0, i)) + list(range(j, n)):
            child[idx] = fill_vals[k]
            k += 1
        return child

    c1 = build_child(seg1, p2)
    c2 = build_child(seg2, p1)
    return c1, c2


def mutate_swap(perm: List[int], rng: random.Random) -> None:
    n = len(perm)
    if n < 2:
        return
    a, b = rng.sample(range(n), 2)
    perm[a], perm[b] = perm[b], perm[a]


def mutate_inversion(perm: List[int], rng: random.Random) -> None:
    n = len(perm)
    if n < 3:
        return
    i, j = sorted(rng.sample(range(n), 2))
    perm[i:j] = reversed(perm[i:j])


def evaluate_perm(
    perm: List[int],
    inst: CVRPInstance,
    rng: random.Random,
    use_2opt: bool,
    two_opt_prob: float,
) -> Tuple[List[List[int]], int]:
    """
    Split la permutation en routes faisables, applique 2-opt (optionnel/probabiliste), calcule le coût.
    - two_opt_prob: probabilité d'appliquer 2-opt sur les routes de cet individu.
    """
    routes = split_giant_tour(perm, inst)
    if use_2opt and rng.random() < max(0.0, min(1.0, two_opt_prob)):
        # 2-opt intra-route seulement pour routes non triviales
        routes = [two_opt_route(r, inst) if len(r) >= 4 else r for r in routes]
    cost = solution_total_cost(routes, inst)
    return routes, cost


def tournament_select(pop: List[Individual], k: int, rng: random.Random) -> Individual:
    cand = rng.sample(pop, k)
    return min(cand, key=lambda ind: ind.cost)


def make_initial_population(
    inst: CVRPInstance,
    pop_size: int,
    rng: random.Random,
    use_2opt: bool,
    verbose: bool = False,
    init_two_opt_prob: float = 0.6,  # un peu de 2-opt au départ pour de bonnes bases
) -> List[Individual]:
    pop: List[Individual] = []

    if verbose:
        print(f"[Init] Construction de la population initiale (taille={pop_size})...", flush=True)

    # 1) un individu greedy nearest-neighbor (toujours 2-opt pour un bon point de départ)
    nn = nearest_neighbor_perm(inst, rng)
    routes, cost = evaluate_perm(nn[:], inst, rng, use_2opt, two_opt_prob=1.0 if use_2opt else 0.0)
    pop.append(Individual(perm=nn[:], routes=routes, cost=cost))

    # 2) le reste aléatoire
    depot = inst.depot_index
    base = [i for i in range(inst.dimension) if i != depot]
    report_every = max(1, pop_size // 10)  # ~10% de progression
    for idx in range(pop_size - 1):
        rng.shuffle(base)
        p = base[:]
        routes, cost = evaluate_perm(p, inst, rng, use_2opt, two_opt_prob=init_two_opt_prob if use_2opt else 0.0)
        pop.append(Individual(perm=p, routes=routes, cost=cost))

        if verbose and ((idx + 2) % report_every == 0 or idx == pop_size - 2):
            print(f"[Init] ... {idx + 2}/{pop_size} individus évalués", flush=True)

    if verbose:
        best_init = min(pop, key=lambda ind: ind.cost)
        print(f"[Init] OK. Meilleur coût initial: {best_init.cost} | #routes={len(best_init.routes)}", flush=True)

    return pop


def _stats(pop: List[Individual]) -> Tuple[int, float]:
    """Retourne (best_cost, avg_cost)."""
    best_cost = min(pop, key=lambda ind: ind.cost).cost
    avg_cost = sum(ind.cost for ind in pop) / len(pop)
    return best_cost, avg_cost


def genetic_algorithm(
    inst: CVRPInstance,
    pop_size: int = 110,
    generations: int = 5000,   
    tournament_k: int = 4,      
    elitism: int = 4,          
    pc: float = 0.95, # crossover probability
    pm: float = 0.25, # mutation probability
    seed: int | None = 1,
    use_2opt: bool = True,
    verbose: bool = True,
    log_interval: int = 10,
    two_opt_prob: float = 0.35,  
    time_limit_sec: float = 170.0,  # ~<3 min par défaut
) -> Individual:
    """
    Boucle principale du GA. Retourne le meilleur individu trouvé.
    Respecte une limite de temps si spécifiée (time_limit_sec > 0).
    """
    rng = random.Random(seed)

    start_time = time.time()
    pop = make_initial_population(inst, pop_size, rng, use_2opt, verbose=verbose, init_two_opt_prob=0.5)
    pop.sort(key=lambda ind: ind.cost)
    best = pop[0]

    if verbose:
        bcost, avg = _stats(pop)
        print(f"[GA] Départ: best={bcost:.0f} | avg={avg:.0f} | #routes_best={len(best.routes)}", flush=True)

    for gen in range(1, generations + 1):
        # Time limit
        if time_limit_sec and (time.time() - start_time) >= time_limit_sec:
            if verbose:
                print(f"[GA] Time limit atteinte ({time_limit_sec:.1f}s). Arrêt anticipé à gen {gen-1}.", flush=True)
            break

        new_pop: List[Individual] = []

        # Élitisme
        elites = pop[:elitism]
        new_pop.extend(elites)

        # Reproduction
        while len(new_pop) < pop_size:
            p1 = tournament_select(pop, tournament_k, rng)
            p2 = tournament_select(pop, tournament_k, rng)

            # Crossover
            if rng.random() < pc:
                c1_perm, c2_perm = order_crossover(p1.perm, p2.perm, rng)
            else:
                c1_perm, c2_perm = p1.perm[:], p2.perm[:]

            # Mutation
            if rng.random() < pm:
                if rng.random() < 0.5:
                    mutate_swap(c1_perm, rng)
                else:
                    mutate_inversion(c1_perm, rng)
            if rng.random() < pm:
                if rng.random() < 0.5:
                    mutate_swap(c2_perm, rng)
                else:
                    mutate_inversion(c2_perm, rng)

            # Évaluation
            c1_routes, c1_cost = evaluate_perm(c1_perm, inst, rng, use_2opt, two_opt_prob=two_opt_prob)
            c2_routes, c2_cost = evaluate_perm(c2_perm, inst, rng, use_2opt, two_opt_prob=two_opt_prob)

            new_pop.append(Individual(c1_perm, c1_routes, c1_cost))
            if len(new_pop) < pop_size:
                new_pop.append(Individual(c2_perm, c2_routes, c2_cost))

        pop = new_pop
        pop.sort(key=lambda ind: ind.cost)
        if pop[0].cost < best.cost:
            best = pop[0]

        if verbose and (gen % max(1, log_interval) == 0 or gen == 1):
            elapsed = time.time() - start_time
            eta = (elapsed / gen) * (generations - gen) if gen > 0 else 0.0
            bcost, avg = _stats(pop)
            print(
                f"[GA] Gen {gen}/{generations} | best={bcost:.0f} | avg={avg:.0f} | #routes_best={len(best.routes)} | "
                f"t+{elapsed:.1f}s | ETA~{eta:.1f}s",
                flush=True,
            )

    if verbose:
        total_elapsed = time.time() - start_time
        print(f"[GA] Terminé en {total_elapsed:.1f}s. Best cost={best.cost} | #routes={len(best.routes)}", flush=True)

    return best