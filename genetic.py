from classes import Solution, Camion, Commande, calculer_fitness
import random

def crossover(solution1 : Solution, solution2 : Solution ) -> Solution:
    # cette fonction effectue un crossover entre deux solutions pour generer une nouvelle solution
    # le crossover consiste a echanger une partie des routes entre les deux solutions
    # on choisit un point de crossover aleatoire dans la liste des routes
    # puis on combine les routes des deux solutions pour creer une nouvelle solution
    # il est important de s'assurer que la nouvelle solution est valide sionon on retourne une copie de la solution1 ou solution2
    point_crossover1 = random.randint(0, len(solution1.routes)-1)
    point_crossover2 = random.randint(0, len(solution2.routes)-1)
    nouvelles_routes = solution1.routes[:point_crossover1] + solution2.routes[point_crossover2:]
    nouvelle_solution = Solution(nouvelles_routes)
    
    if nouvelle_solution.est_valide():
        return nouvelle_solution
    else:
        return random.choice([solution1, solution2])    
    
def mutation(solution : Solution, taux_mutation : float) -> Solution:
    # cette fonction effectue une mutation sur une solution en echangant deux commandes entre deux camions differents avec une probabilite donnee par le taux de mutation
    nouvelles_routes = solution.routes.copy()
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
    if nouvelle_solution.est_valide():
        return nouvelle_solution
    else:
        return solution

def selection(population : list) -> Solution:
    # Cette fonction classe la population par fitness et retourne les 50% des solutions les plus fit
    population_ordonnee = sorted(population, key=lambda sol: calculer_fitness(sol), reverse=True)
    taille_selection = len(population_ordonnee) // 2
    return population_ordonnee[:taille_selection]


def population_initiale(taille_population : int, commandes : list, camions : list) -> list:
    # cette fonction genere une population initiale de solutions aleatoires valides
    # il est important de s'assurer que chaque commande est livree une seule fois dans chaque solution
    # que le meme camion n'est pas utilise dans plusieurs routes
    # et que la capacite de chaque camion n'est pas depassee en terme de masse
    population = []
    while len(population) < taille_population:
        commandes_restantes = commandes.copy()
        random.shuffle(commandes_restantes)
        routes = []
        camions_utilises = set()
        for camion in camions:
            if camion in camions_utilises:
                continue
            camions_utilises.add(camion)
            commandes_camion = []
            total_poid = 0
            for commande in commandes_restantes[:]:
                poids_commande = sum(item.poid for item in commande.items)
                if total_poid + poids_commande <= camion.capacite_poid:
                    commandes_camion.append(commande)
                    total_poid += poids_commande
                    commandes_restantes.remove(commande)
            if commandes_camion:
                routes.append((camion, commandes_camion))
        nouvelle_solution = Solution(routes)
        if nouvelle_solution.est_valide(len(commandes)):
            population.append(nouvelle_solution)
    
    return population

# test de la generation de la population initiale

if __name__ == "__main__":
    #creation de commandes et camions pour le test
    commandes = []
    # commande(client, pos, poid, taille_x, taille_y, taille_z)
    
        
    camions = []
    # camion(capacite_poid, capacite_taille_x, capacite_taille_y, capacite_taille_z)
    # creation de 10 camions aléatoires
    for i in range(10):
        camion = Camion(random.randint(200,500), 0,0,0)

        camions.append(camion)
        
    population = population_initiale(100, commandes, camions)
    print(f"Population initiale generee avec {len(population)} solutions valides.")
    for i, solution in enumerate(population):
        print(f"\nSolution {i+1}:")
        solution.afficher_solution()