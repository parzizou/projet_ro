from classes import Solution, Camion, Commande, calculer_fitness
import random

def crossover(solution1 : Solution, solution2 : Solution ) -> Solution:
    # Crossover basique: on coupe les listes de routes et on concatène
    if not solution1.routes or not solution2.routes:
        # si l'une est vide, on renvoie l'autre (éviter de produire du vide)
        return solution1 if len(solution1.routes) >= len(solution2.routes) else solution2
    point_crossover1 = random.randint(0, len(solution1.routes)-1)
    point_crossover2 = random.randint(0, len(solution2.routes)-1)
    nouvelles_routes = solution1.routes[:point_crossover1] + solution2.routes[point_crossover2:]
    nouvelle_solution = Solution(nouvelles_routes)
    # Validation "structurelle" (pas de dépassement, pas de doublons si applicable)
    if nouvelle_solution.est_valide():
        return nouvelle_solution
    else:
        return random.choice([solution1, solution2])    
    
def mutation(solution : Solution, taux_mutation : float) -> Solution:
    # Echange de commandes entre routes avec une proba donnée
    nouvelles_routes = [ (camion, list(cmds)) for camion, cmds in solution.routes ]
    for i in range(len(nouvelles_routes)):
        if random.random() < taux_mutation:
            j = random.randint(0, len(nouvelles_routes)-1)
            if i != j and nouvelles_routes[i][1] and nouvelles_routes[j][1]:
                # echanger une commande entre les deux camions
                commande_i = random.choice(nouvelles_routes[i][1])
                commande_j = random.choice(nouvelles_routes[j][1])
                nouvelles_routes[i][1].remove(commande_i)
                nouvelles_routes[j][1].remove(commande_j)
                nouvelles_routes[i][1].append(commande_j)
                nouvelles_routes[j][1].append(commande_i)
    nouvelle_solution = Solution(nouvelles_routes)
    # Validation "structurelle"
    if nouvelle_solution.est_valide():
        return nouvelle_solution
    else:
        return solution

def selection(population : list, taille_selection : int) -> list:
    # Sélection des % meilleurs individus
    population_ordonnee = sorted(population, key=lambda sol: calculer_fitness(sol), reverse=True)
    return population_ordonnee[:taille_selection]



def population_initiale(taille_population : int, commandes : list, camions : list) -> list:
    """
    Génère des solutions aléatoires valides qui couvrent TOUTES les commandes.
    """
    if not commandes:
        return []

    population = []
    essais_max = taille_population * 20  # éviter boucles infinies si pas faisable
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
                if total_poid + poids_commande <= camion.capacite_poid:
                    commandes_camion.append(commande)
                    total_poid += poids_commande
                    commandes_restantes.remove(commande)

            if commandes_camion:
                routes.append((camion, commandes_camion))

            if not commandes_restantes:
                break  # toutes les commandes placées

        nouvelle_solution = Solution(routes)
        # Important: on valide la couverture COMPLETE ici
        if nouvelle_solution.est_valide(toutes_commandes=commandes):
            population.append(nouvelle_solution)

    # Si on n'a pas pu générer assez de solutions, on renvoie une erreur
    if len(population) < taille_population:
        raise ValueError("Impossible de générer une population initiale valide avec les contraintes données.")
    return population



