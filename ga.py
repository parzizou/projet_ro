# -*- coding: utf-8 -*-
"""
ga.py
Algorithme génétique pour le CVRP:
- Représentation: permutation globale des clients (giant tour)
- Split DP pour obtenir des tournées faisables
- 2-opt intra-route optionnel (probabiliste pour gagner du temps)
- Sélection par tournoi, crossover OX, mutation swap/inversion
- Limite de temps pour garantir < ~3 minutes par défaut

Améliorations:
- Arrêt propre à la demande (Ctrl+C ou fichier sentinelle)
- Affichage du gap (%) si une valeur optimale cible est fournie

Diversification (nouveau):
- Random immigrants à chaque génération (fraction configurable)
- Détection/éviction des doublons (sur la structure des routes)
- Heavy mutation et shake si stagnation
- Restart partiel si forte stagnation prolongée
- Mutations supplémentaires: insertion et scramble
- Mutation adaptative optionnelle (augmente pm si stagnation)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Set
import random
import time
import os

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


def mutate_insertion(perm: List[int], rng: random.Random) -> None:
    n = len(perm)
    if n < 2:
        return
    i, j = rng.randrange(n), rng.randrange(n)
    if i == j:
        return
    node = perm.pop(i)
    perm.insert(j, node)


def mutate_scramble(perm: List[int], rng: random.Random) -> None:
    n = len(perm)
    if n < 4:
        return
    i, j = sorted(rng.sample(range(n), 2))
    if j - i <= 1:
        return
    segment = perm[i:j]
    rng.shuffle(segment)
    perm[i:j] = segment


def heavy_mutate(perm: List[int], rng: random.Random, steps: int | None = None) -> None:
    """
    Applique plusieurs mutations aléatoires pour une grosse secousse.
    """
    ops = [mutate_swap, mutate_inversion, mutate_insertion, mutate_scramble]
    k = steps if steps is not None else rng.randint(3, 6)
    for _ in range(k):
        rng.choice(ops)(perm, rng)


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


def _route_signature(routes: List[List[int]]) -> Tuple[Tuple[int, ...], ...]:
    """
    Signature hashable d'une solution basée sur la structure des routes.
    (ordre des clients par route; ignorer dépôt inutile ici)
    """
    return tuple(tuple(r) for r in routes)


def _new_random_individual(
    inst: CVRPInstance,
    rng: random.Random,
    use_2opt: bool,
    two_opt_prob: float,
) -> Individual:
    depot = inst.depot_index
    base = [i for i in range(inst.dimension) if i != depot]
    rng.shuffle(base)
    perm = base[:]
    routes, cost = evaluate_perm(perm, inst, rng, use_2opt, two_opt_prob)
    return Individual(perm=perm, routes=routes, cost=cost)


def make_initial_population(
    inst: CVRPInstance,
    pop_size: int,
    rng: random.Random,
    use_2opt: bool,
    verbose: bool = False,
    init_two_opt_prob: float = 0.6,  # un peu de 2-opt au départ pour de bonnes bases
    init_mode: str = "nn_plus_random",  # "nn_plus_random" (défaut) ou "all_random"
) -> List[Individual]:
    """
    Construit la population initiale.
    - nn_plus_random: 1 individu nearest-neighbor puis le reste aléatoire
    - all_random: toute la population est générée par permutations aléatoires
    """
    pop: List[Individual] = []

    if verbose:
        print(f"[Init] Construction de la population initiale (taille={pop_size}, mode={init_mode})...", flush=True)

    depot = inst.depot_index
    base = [i for i in range(inst.dimension) if i != depot]
    report_every = max(1, pop_size // 10)  # ~10% de progression

    if init_mode == "all_random":
        for idx in range(pop_size):
            rng.shuffle(base)
            p = base[:]
            routes, cost = evaluate_perm(p, inst, rng, use_2opt, two_opt_prob=init_two_opt_prob if use_2opt else 0.0)
            pop.append(Individual(perm=p, routes=routes, cost=cost))
            if verbose and ((idx + 1) % report_every == 0 or idx == pop_size - 1):
                print(f"[Init] ... {idx + 1}/{pop_size} individus évalués", flush=True)
    else:
        # 1) un individu greedy nearest-neighbor (toujours 2-opt pour un bon point de départ)
        nn = nearest_neighbor_perm(inst, rng)
        routes, cost = evaluate_perm(nn[:], inst, rng, use_2opt, two_opt_prob=1.0 if use_2opt else 0.0)
        pop.append(Individual(perm=nn[:], routes=routes, cost=cost))

        # 2) le reste aléatoire
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
    pop_size: int = 50,
    generations: int = 100000,
    tournament_k: int = 3,           # -1 par défaut (moins de pression de sélection)
    elitism: int = 3,                # un peu plus bas pour garder de la place à la diversité
    pc: float = 0.50,                # crossover probability
    pm: float = 0.30,                # mutation probability de base
    seed: int | None = 1,
    use_2opt: bool = True,
    verbose: bool = True,
    log_interval: int = 10,
    two_opt_prob: float = 0.35,
    time_limit_sec: float = 20000.0,  # limite de temps en secondes (0 = pas de limite)
    target_optimum: int | None = None,  # valeur optimale connue (pour gap%)
    stop_on_file: str | None = None,    # chemin d'un fichier sentinelle pour arrêt propre
    init_mode: str = "nn_plus_random",  # "nn_plus_random" ou "all_random"

    # Diversification (nouveaux paramètres)
    immigrants_frac: float = 0.1,      # fraction d'immigrants aléatoires ajoutés à chaque génération
    duplicate_avoidance: bool = True,   # éviter d'ajouter 2x la même structure de routes
    stagnation_shake_gens: int = 60,    # après X générations sans amélioration -> shake
    stagnation_restart_gens: int = 180, # après Y générations sans amélioration -> restart partiel
    adaptive_mutation: bool = True,     # pm augmente avec la stagnation
) -> Individual:
    """
    Boucle principale du GA. Retourne le meilleur individu trouvé.

    Diversification:
      - Random immigrants: remplace une fraction des pires individus à chaque génération.
      - Duplicate avoidance: évite d'empiler des solutions identiques (par routes).
      - Shake: si stagnation, heavy mutate une partie de la pop (hors élites).
      - Restart partiel: si longue stagnation, on garde le meilleur et on réensemence le reste.
      - Mutation adaptative: pm légèrement augmenté avec la stagnation; 2-opt un peu réduit pour laisser explorer.

    init_mode:
      - "nn_plus_random": 1 individu nearest-neighbor puis le reste aléatoire
      - "all_random": population entièrement aléatoire
    """
    rng = random.Random(seed)

    def fmt_gap(cost: int) -> str:
        if target_optimum is None or target_optimum <= 0:
            return ""
        gap = 100.0 * (cost - target_optimum) / target_optimum
        return f" | gap={gap:.2f}% (opt={target_optimum})"

    start_time = time.time()
    pop = make_initial_population(
        inst,
        pop_size,
        rng,
        use_2opt,
        verbose=verbose,
        init_two_opt_prob=0.5,
        init_mode=init_mode,
        
    )
    pop.sort(key=lambda ind: ind.cost)
    best = pop[0]
    last_improve_gen = 0

    if verbose:
        bcost, avg = _stats(pop)
        print(f"[GA] Départ: best={bcost:.0f} | avg={avg:.0f} | #routes_best={len(best.routes)} | init_mode={init_mode}{fmt_gap(bcost)}", flush=True)

    stopped_by = None  # "time", "file", "keyboard", or None

    # Aides: pour éviter les doublons de routes
    route_signatures: Set[Tuple[Tuple[int, ...], ...]] = set(_route_signature(ind.routes) for ind in pop)

    try:
        for gen in range(1, generations + 1):
            # Time limit
            if time_limit_sec and (time.time() - start_time) >= time_limit_sec:
                stopped_by = "time"
                if verbose:
                    print(f"[GA] Time limit atteinte ({time_limit_sec:.1f}s). Arrêt anticipé à gen {gen-1}.", flush=True)
                break

            # Stop-on-file
            if stop_on_file and os.path.exists(stop_on_file):
                stopped_by = "file"
                if verbose:
                    print(f"[GA] Fichier sentinelle détecté ({stop_on_file}). Arrêt propre à gen {gen-1}.", flush=True)
                break

            stale = gen - last_improve_gen
            stale_ratio = min(1.0, stale / max(1, stagnation_restart_gens))
            # Mutation adaptative + 2-opt plus léger si stagnation
            pm_eff = pm * (1.0 + 0.6 * stale_ratio) if adaptive_mutation else pm
            pm_eff = max(0.01, min(0.95, pm_eff))
            two_opt_prob_eff = two_opt_prob * (1.0 - 0.30 * stale_ratio) if adaptive_mutation else two_opt_prob
            two_opt_prob_eff = max(0.0, min(1.0, two_opt_prob_eff))

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

                # Mutation (adaptative)
                if rng.random() < pm_eff:
                    if rng.random() < 0.25:
                        mutate_insertion(c1_perm, rng)
                    elif rng.random() < 0.5:
                        mutate_scramble(c1_perm, rng)
                    elif rng.random() < 0.75:
                        mutate_swap(c1_perm, rng)
                    else:
                        mutate_inversion(c1_perm, rng)
                if rng.random() < pm_eff:
                    if rng.random() < 0.25:
                        mutate_insertion(c2_perm, rng)
                    elif rng.random() < 0.5:
                        mutate_scramble(c2_perm, rng)
                    elif rng.random() < 0.75:
                        mutate_swap(c2_perm, rng)
                    else:
                        mutate_inversion(c2_perm, rng)

                # Évaluation
                c1_routes, c1_cost = evaluate_perm(c1_perm, inst, rng, use_2opt, two_opt_prob=two_opt_prob_eff)
                c2_routes, c2_cost = evaluate_perm(c2_perm, inst, rng, use_2opt, two_opt_prob=two_opt_prob_eff)

                # Anti-duplicates: réessayer via heavy mutate quelques fois
                if duplicate_avoidance:
                    tries = 0
                    sig1 = _route_signature(c1_routes)
                    while sig1 in route_signatures and tries < 2:
                        heavy_mutate(c1_perm, rng)
                        c1_routes, c1_cost = evaluate_perm(c1_perm, inst, rng, use_2opt, two_opt_prob=two_opt_prob_eff)
                        sig1 = _route_signature(c1_routes)
                        tries += 1

                new_pop.append(Individual(c1_perm, c1_routes, c1_cost))
                route_signatures.add(_route_signature(c1_routes))

                if len(new_pop) < pop_size:
                    if duplicate_avoidance:
                        tries = 0
                        sig2 = _route_signature(c2_routes)
                        while sig2 in route_signatures and tries < 2:
                            heavy_mutate(c2_perm, rng)
                            c2_routes, c2_cost = evaluate_perm(c2_perm, inst, rng, use_2opt, two_opt_prob=two_opt_prob_eff)
                            sig2 = _route_signature(c2_routes)
                            tries += 1
                    new_pop.append(Individual(c2_perm, c2_routes, c2_cost))
                    route_signatures.add(_route_signature(c2_routes))

            # Diversification: random immigrants (remplace les pires)
            if immigrants_frac > 0.0:
                m = int(pop_size * max(0.0, min(0.5, immigrants_frac)))
                if m > 0:
                    # tri avant remplacement
                    new_pop.sort(key=lambda ind: ind.cost)
                    replaced = 0
                    for _ in range(m):
                        immigrant = _new_random_individual(inst, rng, use_2opt, two_opt_prob_eff * 0.5)
                        # éviter doublons
                        if duplicate_avoidance:
                            sig = _route_signature(immigrant.routes)
                            tries = 0
                            while sig in route_signatures and tries < 3:
                                immigrant = _new_random_individual(inst, rng, use_2opt, two_opt_prob_eff * 0.5)
                                sig = _route_signature(immigrant.routes)
                                tries += 1
                            route_signatures.add(sig)
                        new_pop[-(1 + replaced)] = immigrant
                        replaced += 1
                    if verbose and (gen % max(1, log_interval) == 0):
                        print(f"[GA] Gen {gen}: immigrants={m}", flush=True)

            pop = new_pop
            pop.sort(key=lambda ind: ind.cost)
            if pop[0].cost < best.cost:
                best = pop[0]
                last_improve_gen = gen

            # Stagnation: shake / restart
            stale = gen - last_improve_gen
            if stale > 0 and stale % max(1, stagnation_shake_gens) == 0 and stale < stagnation_restart_gens:
                # shake: heavy mutate une partie de la pop (hors élites), puis réévaluer
                start = elitism
                end = min(pop_size, elitism + max(1, pop_size // 3))
                for idx in range(start, end):
                    ind = pop[idx]
                    heavy_mutate(ind.perm, rng)
                    ind.routes, ind.cost = evaluate_perm(ind.perm, inst, rng, use_2opt, two_opt_prob=two_opt_prob_eff)
                pop.sort(key=lambda ind: ind.cost)
                if verbose:
                    print(f"[GA] Gen {gen}: shake population (stale={stale})", flush=True)
                # reset signatures (recalcul rapide)
                route_signatures = set(_route_signature(ind.routes) for ind in pop)

            if stale >= stagnation_restart_gens:
                # restart partiel: garder le meilleur, réensemencer le reste
                keep = 1
                survivors = pop[:keep]
                new_pop = survivors[:]
                route_signatures = set(_route_signature(ind.routes) for ind in survivors)
                while len(new_pop) < pop_size:
                    immigrant = _new_random_individual(inst, rng, use_2opt, two_opt_prob_eff * 0.4)
                    if duplicate_avoidance:
                        sig = _route_signature(immigrant.routes)
                        tries = 0
                        while sig in route_signatures and tries < 3:
                            heavy_mutate(immigrant.perm, rng)
                            immigrant.routes, immigrant.cost = evaluate_perm(immigrant.perm, inst, rng, use_2opt, two_opt_prob=two_opt_prob_eff * 0.4)
                            sig = _route_signature(immigrant.routes)
                            tries += 1
                        route_signatures.add(sig)
                    new_pop.append(immigrant)
                pop = new_pop
                pop.sort(key=lambda ind: ind.cost)
                last_improve_gen = gen  # on repart
                if verbose:
                    print(f"[GA] Gen {gen}: RESTART partiel (stale={stale})", flush=True)

            if verbose and (gen % max(1, log_interval) == 0 or gen == 1):
                elapsed = time.time() - start_time
                eta = (elapsed / gen) * (generations - gen) if gen > 0 else 0.0
                bcost, avg = _stats(pop)
                print(
                    f"[GA] Gen {gen}/{generations} | best={bcost:.0f} | avg={avg:.0f} | #routes_best={len(best.routes)}"
                    f"{fmt_gap(bcost)} | t+{elapsed:.1f}s | ETA~{eta:.1f}s | pm_eff={pm_eff:.2f} | 2opt={two_opt_prob_eff:.2f}",
                    flush=True,
                )
    except KeyboardInterrupt:
        stopped_by = "keyboard"
        if verbose:
            elapsed = time.time() - start_time
            print(f"[GA] Arrêt par utilisateur (Ctrl+C) après {elapsed:.1f}s à gen {gen-1}.", flush=True)

    if verbose:
        total_elapsed = time.time() - start_time
        print(f"[GA] Terminé après {total_elapsed:.1f}s. Meilleur coût trouvé: {best.cost} | #routes={len(best.routes)}", flush=True)

    return best