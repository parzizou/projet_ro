import math

DEPOT_POS = (0.0, 0.0)

def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

class Commande:
    def __init__(self, client,  pos, poid, taille_x, taille_y, taille_z):
        self.client = client
        self.pos = pos # position de livraison de la commande (x , y)
        self.poid = poid
        self.taille_x = taille_x
        self.taille_y = taille_y
        self.taille_z = taille_z
    
class Camion:
    def __init__(self, capacite_poid, capacite_taille_x, capacite_taille_y, capacite_taille_z):
        self.capacite_poid = capacite_poid
        self.capacite_taille_x = capacite_taille_x
        self.capacite_taille_y = capacite_taille_y
        self.capacite_taille_z = capacite_taille_z
        
class Solution:
    # cette classe represente une solution au probleme de livraison VRP ( Vehicle Routing Problem)
    # une solution est composee de plusieurs routes effectuees par des camions pour livrer des commandes a des clients
    def __init__(self, routes):
        # routes: liste de tuples (camion, [commandes])
        self.routes = routes
        
    def afficher_solution(self):
        # affiche la liste des routes de la solution
        # puis affiche le nombre total de camions utilises dans la solution
        # les unitées de distance totales parcourues par tous les camions
        total_camions = len(self.routes)
        total_distance = 0.0
        for idx, route in enumerate(self.routes, start=1):
            camion, commandes = route
            print(f"Route #{idx} — Camion (Capacité: {camion.capacite_poid}kg, "
                  f"{camion.capacite_taille_x}x{camion.capacite_taille_y}x{camion.capacite_taille_z}cm)")
            for commande in commandes:
                print(f"  - Client: {commande.client}, Position: {commande.pos}, Poids: {commande.poid}kg")
            # Distance dépôt -> clients -> dépôt
            distance = 0.0
            cur = DEPOT_POS
            for commande in commandes:
                distance += _dist(cur, commande.pos)
                cur = commande.pos
            distance += _dist(cur, DEPOT_POS)
            total_distance += distance
            print(f"  Distance totale parcourue par ce camion: {distance:.2f} unités")
        print(f"\nNombre total de camions utilises: {total_camions}")
        print(f"Distance totale parcourue par tous les camions: {total_distance:.2f} unités")
        
        
    def est_valide(self, toutes_commandes=None) -> bool:
        """
        Verifie:
        - chaque commande apparait au plus une fois (pas de doublon),
        - la capacité de chaque camion n'est pas depassee en terme de masse,
        - si toutes_commandes est fourni, la solution couvre exactement cet ensemble de commandes.
        """
        commandes_livrees = []
        for route in self.routes:
            camion, commandes = route
            total_poid = 0.0
            for commande in commandes:
                commandes_livrees.append(commande)
                total_poid += float(commande.poid)
            if total_poid > camion.capacite_poid:
                return False  # capacite de poids depassee
        # doublons ?
        if len(commandes_livrees) != len(set(commandes_livrees)):
            return False
        if toutes_commandes is not None:
            # couvrir exactement toutes les commandes demandées
            return set(commandes_livrees) == set(toutes_commandes) and len(commandes_livrees) > 0
        # sinon, simple validité structurelle
        return True
    
def calculer_fitness(solution : Solution) -> float:
    # Fitness = 1 / distance totale (dépôt -> tournées -> retour)
    total_distance = 0.0
    for route in solution.routes:
        camion, commandes = route
        cur = DEPOT_POS
        for commande in commandes:
            total_distance += _dist(cur, commande.pos)
            cur = commande.pos
        total_distance += _dist(cur, DEPOT_POS)
    if total_distance == 0:
        return 0.0
    return 1.0 / total_distance