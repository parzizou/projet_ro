

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
        self.routes = routes # liste de routes, chaque route est une liste de tuples (camion, [commandes])
        
    def afficher_solution(self):
        # affiche la liste des routes de la solution
        # puis affiche le nombre total de camions utilises dans la solution
        # les unitées de distance totales parcourues par tous les camions
        total_camions = len(self.routes)
        total_distance = 0
        for route in self.routes:
            camion, commandes = route
            print(f"Camion (Capacite: {camion.capacite_poid}kg, {camion.capacite_taille_x}x{camion.capacite_taille_y}x{camion.capacite_taille_z}cm) livre les commandes:")
            for commande in commandes:
                print(f"  Client: {commande.client}, Position: {commande.pos}, Items: {len(commande.items)}")
            # Calcul de la distance totale parcourue par le camion (exemple simplifié)
            distance = sum(((commande.pos[0] - camion.pos[0])**2 + (commande.pos[1] - camion.pos[1])**2)**0.5 for commande in commandes)
            total_distance += distance
            print(f"  Distance totale parcourue par ce camion: {distance:.2f} unités")
        print(f"\nNombre total de camions utilises: {total_camions}")
        print(f"Distance totale parcourue par tous les camions: {total_distance:.2f} unités")
        
        
    def est_valide(self,nb_commandees) -> bool:
        # verifie si la solution est valide en s'assurant que chaque commande est livree une seule fois, et que la capacité de chaque camion n'est pas depassee en terme de masse
        commandes_livrees = set()
        for route in self.routes:
            camion, commandes = route
            total_poid = 0
            for commande in commandes:
                if commande in commandes_livrees:
                    return False # commande deja livree
                commandes_livrees.add(commande)
                total_poid += sum(item.poid for item in commande.items)
            if total_poid > camion.capacite_poid:
                return False # capacite de poids depassee
        return len(commandes_livrees) == nb_commandees
    
def calculer_fitness(solution : Solution) -> float:
    # cette fonction calcule la fitness d'une solution
    # la fitness est definie comme l'inverse de la distance totale parcourue par tous les camions dans la solution
    # elle sert a evaluer la qualite d'une solution dans le cadre d'un algorithme genetique
    # plus la distance totale est faible, plus la fitness est elevee
    total_distance = 0
    for route in solution.routes:
        camion, commandes = route
        distance = sum(((commande.pos[0] - camion.pos[0])**2 + (commande.pos[1] - camion.pos[1])**2)**0.5 for commande in commandes)
        total_distance += distance
    if total_distance == 0:
        return float('inf') # eviter la division par zero
    return 1 / total_distance

