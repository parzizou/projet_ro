from classes import Solution, Camion, Commande, DEPOT_POS
import random
import time
import math
from typing import List, Tuple, Dict

# =========================
# Utils distance
# =========================

def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# =========================
# Préparation des données
# =========================

def _build_data(commandes: List[Commande], camions: List[Camion]):
    """
    Prépare:
      - positions des clients,
      - demandes,
      - capacité (supposée identique pour tous les camions),
      - matrices de distances (client-client, dépôt-client).
    """
    n = len(commandes)
    pos = [(c.pos[0], c.pos[1]) for c in commandes]
    dem = [float(c.poid) for c in commandes]
    cap = float(camions[0].capacite_poid) if camions else float('inf')

    # distances entre clients
    dist_cc = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            d = _dist(pos[i], pos[j])
            dist_cc[i][j] = d
            dist_cc[j][i] = d

    # distances dépôt <-> clients
    dist_depot_to = [_dist(DEPOT_POS, pos[i]) for i in range(n)]
    dist_to_depot = [dist_depot_to[i] for i in range(n)]  # euclidien symétrique

    return {
        "n": n,
        "pos": pos,
        "dem": dem,
        "cap": cap,
        "dist_cc": dist_cc,
        "dist_depot_to": dist_depot_to,
        "dist_to_depot": dist_to_depot,
    }

# =========================
# Split DP: meilleure découpe d'une permutation en routes faisables
# =========================

def _evaluate_permutation(perm: List[int], data) -> Tuple[float, List[Tuple[int, int]]]:
    """
    Retourne:
      - coût total minimal après split (somme des distances des routes),
      - liste des segments [i, j] (indices dans la permutation) représentant chaque route.
    DP O(n^2) avec vérification de capacité.
    """
    n = data["n"]
    dem = data["dem"]
    cap = data["cap"]
    dist_cc = data["dist_cc"]
    d0 = data["dist_depot_to"]
    d1 = data["dist_to_depot"]

    if n == 0:
        return 0.0, []

    # Préfixes pour somme des demandes et coût du chemin le long de la permutation
    pref_dem = [0.0] * (n + 1)
    pref_path = [0.0] * n  # pref_path[k] = coût des arcs perm[0]->perm[1] ... jusqu'à atteindre l'index k
    for k in range(n):
        pref_dem[k+1] = pref_dem[k] + dem[perm[k]]
        if k == 0:
            pref_path[k] = 0.0
        else:
            pref_path[k] = pref_path[k-1] + dist_cc[perm[k-1]][perm[k]]

    def path_cost(i, j):
        if i == j:
            return 0.0
        # somme des arcs perm[i]->perm[i+1] ... -> perm[j]
        return pref_path[j] - (pref_path[i] if i > 0 else 0.0)

    INF = float('inf')
    dp = [INF] * (n + 1)   # dp[k] = coût min pour couvrir perm[0..k-1]
    pred = [-1] * (n + 1)  # prédécesseur pour reconstruction
    dp[0] = 0.0

    # Transition: pour j inclus, on cherche i..j tel que capacité OK, et minimise dp[i] + coût_route(i..j)
    for j in range(n):
        # tester i en remontant tant que la capacité n'explose pas
        i = j
        while i >= 0:
            load = pref_dem[j+1] - pref_dem[i]
            if load > cap + 1e-9:
                break
            # coût de la route i..j: dépôt->i + arcs internes + j->dépôt
            c = d0[perm[i]] + path_cost(i, j) + d1[perm[j]]
            cand = dp[i] + c
            if cand < dp[j+1]:
                dp[j+1] = cand
                pred[j+1] = i
            i -= 1

    # Reconstruction des segments [i, j]
    segments = []
    k = n
    while k > 0:
        i = pred[k]
        if i < 0:
            # fallback, ne devrait pas arriver si cap suffisante
            i = k - 1
        segments.append((i, k - 1))
        k = i
    segments.reverse()

    return dp[n], segments

# =========================
# Construction Solution à partir d'une permutation + split
# =========================

def _build_solution_from_perm(perm: List[int], data, commandes: List[Commande], camions: List[Camion]) -> Tuple[Solution, float]:
    total_cost, segments = _evaluate_permutation(perm, data)
    routes = []
    used_trucks = 0
    for (i, j) in segments:
        route_cmds = [commandes[idx] for idx in perm[i:j+1]]
        if route_cmds:
            camion = camions[min(used_trucks, len(camions)-1)]
            routes.append((camion, route_cmds))
            used_trucks += 1
    return Solution(routes), total_cost

# =========================
# Heuristiques d'init (sweep, nearest neighbor)
# =========================

def _sweep_perm(commandes: List[Commande]) -> List[int]:
    cx, cy = DEPOT_POS
    def angle(c):
        return math.atan2(c.pos[1] - cy, c.pos[0] - cx)
    order = sorted(range(len(commandes)), key=lambda i: angle(commandes[i]))
    return order

def _nearest_neighbor_perm(commandes: List[Commande]) -> List[int]:
    n = len(commandes)
    if n == 0:
        return []
    remaining = set(range(n))
    # start: client le plus proche du dépôt
    start = min(remaining, key=lambda i: _dist(DEPOT_POS, commandes[i].pos))
    perm = [start]
    remaining.remove(start)
    cur = start
    while remaining:
        nxt = min(remaining, key=lambda j: _dist(commandes[cur].pos, commandes[j].pos))
        perm.append(nxt)
        remaining.remove(nxt)
        cur = nxt
    return perm

# =========================
# Crossover OX (Order Crossover)
# =========================

def _ox(p1: List[int], p2: List[int]) -> List[int]:
    n = len(p1)
    a, b = sorted(random.sample(range(n), 2))
    child = [-1] * n
    # copier segment de p1
    child[a:b+1] = p1[a:b+1]
    used = set(child[a:b+1])
    # remplir avec p2 en ordre
    idx = (b + 1) % n
    for x in p2:
        if x in used:
            continue
        child[idx] = x
        idx = (idx + 1) % n
    return child

# =========================
# Mutations sur permutation
# =========================

def _mutate(perm: List[int], p_swap=0.4, p_insert=0.3, p_reverse=0.3) -> List[int]:
    n = len(perm)
    res = perm[:]
    r = random.random()
    if r < p_swap:
        i, j = random.sample(range(n), 2)
        res[i], res[j] = res[j], res[i]
    elif r < p_swap + p_insert:
        i, j = random.sample(range(n), 2)
        x = res.pop(i)
        res.insert(j, x)
    else:
        i, j = sorted(random.sample(range(n), 2))
        res[i:j+1] = reversed(res[i:j+1])
    return res

# =========================
# Local search légère (2-opt tentatives)
# =========================

def _local_search_2opt(perm: List[int], data, max_tries=20) -> List[int]:
    """
    Essaye quelques inversions de segments; accepte seulement si le coût split s'améliore.
    max_tries limité pour rester rapide.
    """
    best_perm = perm[:]
    best_cost, _ = _evaluate_permutation(best_perm, data)
    n = len(perm)
    tries = 0
    while tries < max_tries:
        i, j = sorted(random.sample(range(n), 2))
        if j - i < 2:
            tries += 1
            continue
        cand = best_perm[:]
        cand[i:j+1] = reversed(cand[i:j+1])
        cand_cost, _ = _evaluate_permutation(cand, data)
        if cand_cost + 1e-9 < best_cost:
            best_perm = cand
            best_cost = cand_cost
            # on reset quelques essais après amélioration
            tries = 0
        else:
            tries += 1
    return best_perm

# =========================
# Population et sélection
# =========================

def _init_population(pop_size: int, commandes: List[Commande], data) -> List[List[int]]:
    n = len(commandes)
    pop = []
    if n == 0:
        return pop
    # seeds utiles
    pop.append(_sweep_perm(commandes))
    pop.append(_nearest_neighbor_perm(commandes))
    # complétion aléatoire
    while len(pop) < pop_size:
        p = list(range(n))
        random.shuffle(p)
        pop.append(p)
    return pop

def _evaluate_population(pop: List[List[int]], data) -> List[Tuple[float, List[int]]]:
    scored = []
    for perm in pop:
        cost, _ = _evaluate_permutation(perm, data)
        scored.append((cost, perm))
    scored.sort(key=lambda x: x[0])
    return scored

# =========================
# Algorithme génétique Giant Tour + Split
# =========================

def genetic_algorithm(commandes: list, camions: list,
                      taille_population: int = 100,
                      generations: int = 200,
                      taux_mutation: float = 0.2,
                      taille_selection: int = 30,
                      temps_max_secondes: float = 170.0,
                      proba_local_search: float = 0.3,
                      immigrants_ratio: float = 0.1) -> Solution:
    """
    GA sur permutations (Giant Tour) + Split DP pour construire les routes:
    - Objectif: minimiser la distance totale (aucune pénalité sur le nb de camions).
    - Anti-stagnation: immigrants aléatoires et local search 2-opt.
    - Respecte la capacité; nombre de routes libre.
    """
    debut = time.time()
    data = _build_data(commandes, camions)
    n = data["n"]
    if n == 0:
        return Solution([])

    # Init
    population = _init_population(taille_population, commandes, data)
    evaluated = _evaluate_population(population, data)
    best_cost, best_perm = evaluated[0]
    no_improve = 0

    for gen in range(generations):
        if time.time() - debut > temps_max_secondes:
            print(f"Temps max atteint à la génération {gen}. On s'arrête.")
            break

        # Sélection (élitisme + top sélection)
        elites_count = min(2, len(evaluated))
        elites = [perm for (_, perm) in evaluated[:elites_count]]
        parents_pool = [perm for (_, perm) in evaluated[:max(taille_selection, elites_count)]]

        # Nouvelle génération
        nouvelle_population = []
        nouvelle_population.extend(elites)

        # enfants par crossover + mutation
        while len(nouvelle_population) < taille_population:
            p1, p2 = random.sample(parents_pool, 2)
            child = _ox(p1, p2)
            if random.random() < taux_mutation:
                child = _mutate(child)
            if random.random() < proba_local_search:
                # petite intensification
                child = _local_search_2opt(child, data, max_tries=max(5, min(20, n // 10)))
            nouvelle_population.append(child)

            # check temps dans la boucle
            if time.time() - debut > temps_max_secondes:
                break

        # Immigrants aléatoires pour casser la stagnation
        immigrants = int(immigrants_ratio * taille_population)
        for _ in range(immigrants):
            if len(nouvelle_population) >= taille_population:
                break
            randp = list(range(n))
            random.shuffle(randp)
            nouvelle_population.append(randp)

        # Eval
        evaluated = _evaluate_population(nouvelle_population, data)
        cur_cost, cur_perm = evaluated[0]
        if cur_cost + 1e-9 < best_cost:
            best_cost, best_perm = cur_cost, cur_perm
            no_improve = 0
        else:
            no_improve += 1

        print(f"Génération {gen+1}/{generations} — meilleur coût: {best_cost:.3f}")

        # Diversification si stagnation prolongée
        if no_improve >= 15:
            no_improve = 0
            # remélange fort la moitié basse de la pop
            half = len(evaluated) // 2
            for i in range(half, len(evaluated)):
                p = evaluated[i][1][:]
                random.shuffle(p)
                evaluated[i] = (float('inf'), p)
            # reconstruire population à partir de evaluated “cassé”
            population = [perm for (_, perm) in evaluated]
            evaluated = _evaluate_population(population, data)

    # Construire la meilleure solution trouvée
    best_solution, _ = _build_solution_from_perm(best_perm, data, commandes, camions)
    return best_solution