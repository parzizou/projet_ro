from classes import Solution, Camion, Commande, calculer_fitness
import random
import time
from collections import Counter

def _charge_route(commandes):
    return sum(float(c.poid) for c in commandes)

def _reparer_solution(solution: Solution, commandes: list, camions: list) -> Solution:
    """
    Répare une solution potentiellement invalide pour:
      - éliminer les doublons de commandes,
      - réaffecter les commandes manquantes,
      - garantir l'unicité des camions sur les routes,
      - respecter les capacités.
    Stratégie simple et robuste.
    """
    # 1) enlever les doublons de commandes (garder 1ère occurrence)
    vues = set()
    routes_sans_doublons = []
    for camion, cmds in solution.routes:
        new_cmds = []
        for c in cmds:
            if c in vues:
                continue
            vues.add(c)
            new_cmds.append(c)
        if new_cmds:
            routes_sans_doublons.append((camion, new_cmds))

    # 2) garantir l'unicité des camions (si un camion apparait plusieurs fois, on réassigne un camion libre)
    used_trucks = set()
    free_trucks = [truck for truck in camions]
    routes_camion_uniques = []
    for camion, cmds in routes_sans_doublons:
        if camion in used_trucks:
            # trouver un camion libre
            new_camion = None
            for t in free_trucks:
                if t not in used_trucks:
                    new_camion = t
                    break
            camion = new_camion if new_camion is not None else camion
        used_trucks.add(camion)
        routes_camion_uniques.append((camion, cmds))

    # 3) trouver les commandes manquantes
    missing = [c for c in commandes if c not in vues]

    # 4) tenter de les placer dans les routes existantes (greedy) sinon ouvrir une nouvelle route
    for c in missing:
        place = False
        # essayer d'abord dans une route avec assez de capacité restante
        for idx, (camion, cmds) in enumerate(routes_camion_uniques):
            if _charge_route(cmds) + float(c.poid) <= camion.capacite_poid + 1e-9:
                cmds.append(c)
                place = True
                break
        if not place:
            # ouvrir nouvelle route si camion libre
            new_camion = None
            for t in camions:
                if t not in used_trucks:
                    new_camion = t
                    break
            if new_camion is not None:
                used_trucks.add(new_camion)
                routes_camion_uniques.append((new_camion, [c]))
            else:
                # Pas de camion libre: échec — tenter un swap simple avec la route la moins chargée
                # (comme on a 1 camion par commande dans main.py, on ne devrait jamais arriver ici)
                # fallback: mettre quand même et la validation échouera si impossible
                routes_camion_uniques.append((routes_camion_uniques[0][0], [c]))

    # 5) retirer d'éventuelles routes vides
    routes_finales = [(camion, cmds) for camion, cmds in routes_camion_uniques if cmds]

    return Solution(routes_finales)

def crossover(solution1: Solution, solution2: Solution, commandes: list, camions: list) -> Solution:
    # Crossover basique: on coupe les listes de routes et on concatène, puis on répare
    if not solution1.routes or not solution2.routes:
        base = solution1 if len(solution1.routes) >= len(solution2.routes) else solution2
        return _reparer_solution(base, commandes, camions)

    point_crossover1 = random.randint(0, len(solution1.routes)-1)
    point_crossover2 = random.randint(0, len(solution2.routes)-1)

    nouvelles_routes = solution1.routes[:point_crossover1] + solution2.routes[point_crossover2:]
    enfant = Solution(nouvelles_routes)
    enfant = _reparer_solution(enfant, commandes, camions)

    # garder un enfant valide couvrant tout
    return enfant

def mutation(solution: Solution, taux_mutation: float, commandes: list, camions: list) -> Solution:
    # Echange de commandes entre routes avec une proba donnée puis réparation
    nouvelles_routes = [ (camion, list(cmds)) for camion, cmds in solution.routes ]
    for i in range(len(nouvelles_routes)):
        if random.random() < taux_mutation and len(nouvelles_routes) > 1:
            j = random.randint(0, len(nouvelles_routes)-1)
            if i != j and nouvelles_routes[i][1] and nouvelles_routes[j][1]:
                # echanger une commande entre les deux camions
                commande_i = random.choice(nouvelles_routes[i][1])
                commande_j = random.choice(nouvelles_routes[j][1])
                nouvelles_routes[i][1].remove(commande_i)
                nouvelles_routes[j][1].remove(commande_j)
                nouvelles_routes[i][1].append(commande_j)
                nouvelles_routes[j][1].append(commande_i)

    enfant = Solution(nouvelles_routes)
    enfant = _reparer_solution(enfant, commandes, camions)
    return enfant

def selection(population: list, commandes: list, taille_selection: int) -> list:
    # Sélection des meilleurs individus (fitness déjà pénalisée si invalide)
    population_ordonnee = sorted(population, key=lambda sol: calculer_fitness(sol, toutes_commandes=commandes), reverse=True)
    return population_ordonnee[:taille_selection]

def population_initiale(taille_population: int, commandes: list, camions: list) -> list:
    """
    Génère des solutions aléatoires valides qui couvrent TOUTES les commandes.
    """
    if not commandes:
        return []

    population = []
    essais_max = taille_population * 50  # un peu plus d'essais pour la faisabilité
    essais = 0

    while len(population) < taille_population and essais < essais_max:
        essais += 1
        commandes_restantes = list(commandes)
        random.shuffle(commandes_restantes)
        routes = []
        camions_utilises = set()

        for camion in camions:
            if camion in camions_utilises:
                continue
            camions_utilises.add(camion)
            commandes_camion = []
            total_poid = 0.0

            # On tente de charger le camion
            for commande in commandes_restantes[:]:
                poids_commande = float(commande.poid)
                if total_poid + poids_commande <= camion.capacite_poid + 1e-9:
                    commandes_camion.append(commande)
                    total_poid += poids_commande
                    commandes_restantes.remove(commande)

            if commandes_camion:
                routes.append((camion, commandes_camion))

            if not commandes_restantes:
                break  # toutes les commandes placées

        nouvelle_solution = Solution(routes)
        # Réparation + validation stricte couverture complète
        nouvelle_solution = _reparer_solution(nouvelle_solution, commandes, camions)
        if nouvelle_solution.est_valide(toutes_commandes=commandes):
            population.append(nouvelle_solution)

    if len(population) < taille_population:
        raise ValueError("Impossible de générer une population initiale valide avec les contraintes données.")
    return population

def genetic_algorithm(commandes: list, camions: list,
                      taille_population: int = 100,
                      generations: int = 100,
                      taux_mutation: float = 0.1,
                      taille_selection: int = 30,
                      temps_max_secondes: float = 170.0) -> Solution:
    # Générer la population initiale
    population = population_initiale(taille_population, commandes, camions)

    debut = time.time()
    meilleur = max(population, key=lambda sol: calculer_fitness(sol, toutes_commandes=commandes))
    meilleur_f = calculer_fitness(meilleur, toutes_commandes=commandes)

    for gen in range(generations):
        if time.time() - debut > temps_max_secondes:
            print(f"Temps max atteint à la génération {gen}. On s'arrête.")
            break

        # Sélection
        population_selectionnee = selection(population, commandes, taille_selection)
        if len(population_selectionnee) < 2:
            population_selectionnee = population[:2]

        # Nouvelle génération (avec élitisme simple)
        nouvelle_population = []
        # élitisme: garder les meilleurs
        elites = selection(population, commandes, min(2, len(population)))
        nouvelle_population.extend(elites)

        # Crossover + mutation pour remplir la population
        while len(nouvelle_population) < taille_population:
            parents = random.sample(population_selectionnee, 2)
            enfant = crossover(parents[0], parents[1], commandes, camions)
            enfant_muté = mutation(enfant, taux_mutation, commandes, camions)
            nouvelle_population.append(enfant_muté)

        population = nouvelle_population
        
        # Mettre à jour le meilleur
        courant = max(population, key=lambda sol: calculer_fitness(sol, toutes_commandes=commandes))
        courant_f = calculer_fitness(courant, toutes_commandes=commandes)
        if courant_f > meilleur_f:
            meilleur, meilleur_f = courant, courant_f

        print(f"Génération {gen+1}/{generations} — meilleure fitness: {meilleur_f:.6f}")

    return meilleur