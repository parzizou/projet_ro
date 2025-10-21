import random
import time
import copy
import numpy as np
from typing import List, Tuple, Callable, Dict, Set
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

from models import Client, Tournee, Solution, ProblemVRP

try:
    from sklearn.cluster import KMeans
    sklearn_available = True
except ImportError:
    sklearn_available = False
    logging.warning("sklearn non disponible. Le clustering K-means ne sera pas utilisé.")


class AlgorithmeGenetique:
    def __init__(self, 
                 probleme: ProblemVRP, 
                 taille_population: int = 150,
                 max_generations: int = 500,
                 taux_mutation: float = 0.3,
                 taux_croisement: float = 0.85,
                 taille_tournoi: int = 5,
                 elitisme: float = 0.15,
                 temps_max: float = 180):  # Temps max en secondes (3 minutes)
        
        self.probleme = probleme
        self.taille_population = taille_population
        self.max_generations = max_generations
        self.taux_mutation = taux_mutation
        self.taux_croisement = taux_croisement
        self.taille_tournoi = taille_tournoi
        self.elitisme = elitisme
        self.temps_max = temps_max
        
        self.population = []
        self.meilleure_solution = None
        self.generation_courante = 0
    
    def initialiser_population(self):
        """Initialise la population avec des solutions aléatoires et intelligentes"""
        self.population = []
        
        # 70% de solutions avec l'algorithme du sac à dos
        nb_solutions_knapsack = int(0.7 * self.taille_population)
        for _ in range(nb_solutions_knapsack):
            solution = self.creer_solution_knapsack()
            self.evaluer_fitness(solution)
            self.population.append(solution)
        
        # 30% de solutions aléatoires pour maintenir la diversité
        clients_dispo = copy.deepcopy(self.probleme.clients)
        for _ in range(self.taille_population - nb_solutions_knapsack):
            random.shuffle(clients_dispo)
            
            solution = Solution()
            tournee_courante = Tournee()
            
            charge_courante = 0.0
            
            for client in clients_dispo:
                if charge_courante + client.taille_commande > self.probleme.capacite_vehicule:
                    if not tournee_courante.est_vide():
                        solution.tournees.append(tournee_courante)
                    tournee_courante = Tournee()
                    charge_courante = 0.0
                
                tournee_courante.ajouter_client(client)
                charge_courante += client.taille_commande
            
            if not tournee_courante.est_vide():
                solution.tournees.append(tournee_courante)
            
            self.evaluer_fitness(solution)
            self.population.append(solution)
            
        logging.info(f"Population initialisée avec {len(self.population)} solutions")
    
    def creer_solution_knapsack(self) -> Solution:
        """Crée une solution avec l'approche du sac à dos"""
        solution = Solution()
        clients_non_assignes = copy.deepcopy(self.probleme.clients)
        
        while clients_non_assignes:
            # Créer une nouvelle tournée
            tournee = Tournee()
            capacite_restante = self.probleme.capacite_vehicule
            position_actuelle = self.probleme.depot
            
            # Tant qu'il reste de la capacité et des clients à assigner
            while clients_non_assignes and capacite_restante > 0:
                # Calculer les valeurs pour chaque client non assigné
                valeurs = {}
                for client in clients_non_assignes:
                    # Valeur inversement proportionnelle à la distance
                    distance = self.probleme.matrice_distances[position_actuelle][client.id]
                    valeurs[client] = 1000 / (distance + 1)
                
                # Utiliser l'algorithme du sac à dos pour sélectionner les clients
                clients_selectionnes = self.knapsack_glouton(
                    clients_non_assignes,
                    capacite_restante,
                    valeurs,
                    lambda c: c.taille_commande
                )
                
                # Si aucun client ne peut être ajouté, sortir de la boucle
                if not clients_selectionnes:
                    break
                
                # Ajouter les clients sélectionnés à la tournée dans l'ordre du plus proche
                clients_selectionnes.sort(
                    key=lambda c: self.probleme.matrice_distances[position_actuelle][c.id]
                )
                
                for client in clients_selectionnes:
                    tournee.ajouter_client(client)
                    clients_non_assignes.remove(client)
                    capacite_restante -= client.taille_commande
                    position_actuelle = client.id
            
            # Optimiser l'ordre des clients dans la tournée
            self.optimiser_ordre_tournee(tournee)
            
            # Ajouter la tournée à la solution
            if not tournee.est_vide():
                solution.tournees.append(tournee)
        
        return solution
    
    def knapsack_glouton(self, clients: List[Client], capacite: float, 
                          valeurs: Dict[Client, float], fonction_poids) -> List[Client]:
        """
        Version gloutonne du problème du sac à dos
        Retourne une liste de clients qui maximisent la valeur totale sans dépasser la capacité
        """
        # Trier les clients par ratio valeur/poids décroissant
        clients_tries = sorted(
            clients, 
            key=lambda c: valeurs[c]/fonction_poids(c) if fonction_poids(c) > 0 else float('inf'),
            reverse=True
        )
        
        selectionnes = []
        poids_total = 0
        
        for client in clients_tries:
            poids = fonction_poids(client)
            if poids_total + poids <= capacite:
                selectionnes.append(client)
                poids_total += poids
                
                # Si on a pris trop de clients, on s'arrête
                if len(selectionnes) >= 10:  # Limite arbitraire pour éviter des tournées trop longues
                    break
        
        return selectionnes
    
    def evaluer_fitness(self, solution: Solution):
        """Évalue la qualité d'une solution avec des pénalités ajustées"""
        temps_total = 0
        temps_max_tournee = 0
        depassements_horaires = 0
        
        for tournee in solution.tournees:
            charge_actuelle = 0
            temps_tournee = 0
            position_actuelle = self.probleme.depot
            heure_actuelle = self.probleme.heure_debut  # Commencer à 8h00
            
            for client in tournee.clients:
                # Ajouter temps de trajet
                temps_trajet = self.probleme.matrice_distances[position_actuelle][client.id]
                temps_tournee += temps_trajet
                heure_actuelle += temps_trajet
                position_actuelle = client.id
                
                # Temps de service (estimation: 10 minutes par client)
                temps_service = 10
                temps_tournee += temps_service
                heure_actuelle += temps_service
                
                # Vérifier capacité
                charge_actuelle += client.taille_commande
            
            # Retour au dépôt
            temps_retour = self.probleme.matrice_distances[position_actuelle][self.probleme.depot]
            temps_tournee += temps_retour
            heure_actuelle += temps_retour
            
            temps_total += temps_tournee
            temps_max_tournee = max(temps_max_tournee, temps_tournee)
            
            # Vérifier dépassement horaire
            if heure_actuelle > self.probleme.heure_fin:
                depassement = heure_actuelle - self.probleme.heure_fin
                depassements_horaires += depassement
        
        # Calcul des pénalités
        penalites = 0
        
        # Pénalité pour le nombre de véhicules (moins forte)
        penalites += 50 * len(solution.tournees)
        
        # Pénalité pour déséquilibre entre les tournées
        tournees_non_vides = [t for t in solution.tournees if not t.est_vide()]
        if tournees_non_vides:
            temps_moyen = temps_total / len(tournees_non_vides)
            variance = sum((self.calculer_temps_tournee(t) - temps_moyen)**2 
                          for t in tournees_non_vides) / len(tournees_non_vides)
            penalites += 0.5 * variance**0.5  # Écart-type comme pénalité
        
        # Forte pénalité pour dépassement horaire
        penalites += 1000 * depassements_horaires
        
        # Pénalité pour dépassement de capacité
        for tournee in solution.tournees:
            if tournee.charge_totale() > self.probleme.capacite_vehicule:
                penalites += 5000 * (tournee.charge_totale() - self.probleme.capacite_vehicule)
        
        solution.fitness = temps_total + penalites
        return solution.fitness
    
    def calculer_temps_tournee(self, tournee: Tournee) -> float:
        """Calcule le temps total d'une tournée (trajet + service)"""
        temps_total = 0
        position_actuelle = self.probleme.depot
        
        for client in tournee.clients:
            # Temps de trajet
            temps_total += self.probleme.matrice_distances[position_actuelle][client.id]
            position_actuelle = client.id
            
            # Temps de service (10 minutes par client)
            temps_total += 10
        
        # Retour au dépôt
        temps_total += self.probleme.matrice_distances[position_actuelle][self.probleme.depot]
        
        return temps_total
    
    def selection_tournoi(self) -> Solution:
        """Sélectionne une solution par tournoi"""
        candidats = random.sample(self.population, min(self.taille_tournoi, len(self.population)))
        return min(candidats, key=lambda s: s.fitness)
    
    def croisement(self, parent1: Solution, parent2: Solution) -> Solution:
        """Croise deux solutions parents pour en créer une nouvelle"""
        if random.random() > self.taux_croisement:
            return parent1.clone()
        
        # Obtenir tous les clients du parent1
        clients_p1 = []
        for tournee in parent1.tournees:
            clients_p1.extend(tournee.clients)
        
        # Obtenir l'ordre des clients dans parent2
        ordre_p2 = []
        for tournee in parent2.tournees:
            ordre_p2.extend(tournee.clients)
        
        # Sélectionner un segment aléatoire du parent1
        taille = len(clients_p1)
        point1 = random.randint(0, taille - 1)
        point2 = random.randint(point1, taille - 1)
        
        segment = clients_p1[point1:point2+1]
        segment_set = set(segment)
        
        # Créer la liste des clients pour l'enfant
        enfant_clients = [None] * taille
        
        # Copier le segment sélectionné
        for i in range(point1, point2 + 1):
            enfant_clients[i] = clients_p1[i]
        
        # Remplir les positions restantes avec les clients de parent2 dans l'ordre
        idx_p2 = 0
        for i in range(taille):
            if enfant_clients[i] is None:
                while idx_p2 < taille and ordre_p2[idx_p2] in segment_set:
                    idx_p2 += 1
                
                if idx_p2 < taille:
                    enfant_clients[i] = ordre_p2[idx_p2]
                    idx_p2 += 1
        
        # Convertir la liste de clients en une solution avec l'algorithme du sac à dos
        enfant = self.clients_to_solution_knapsack(enfant_clients)
        
        return enfant
    
    def clients_to_solution_knapsack(self, clients: List[Client]) -> Solution:
        """
        Convertit une liste ordonnée de clients en solution en utilisant l'approche du sac à dos
        pour respecter les contraintes de capacité
        """
        solution = Solution()
        clients_restants = list(clients)  # Copie pour ne pas modifier l'original
        
        while clients_restants:
            tournee = Tournee()
            capacite_restante = self.probleme.capacite_vehicule
            position_actuelle = self.probleme.depot
            
            # Parcourir les clients dans l'ordre
            i = 0
            while i < len(clients_restants):
                client = clients_restants[i]
                
                if client.taille_commande <= capacite_restante:
                    # Ajouter le client à la tournée
                    tournee.ajouter_client(client)
                    capacite_restante -= client.taille_commande
                    position_actuelle = client.id
                    clients_restants.pop(i)  # Retirer le client de la liste
                else:
                    i += 1  # Passer au client suivant
            
            # Si on a créé une tournée, l'ajouter à la solution
            if not tournee.est_vide():
                solution.tournees.append(tournee)
                
            # Si on ne peut plus ajouter de clients, mais qu'il en reste, forcer l'ajout
            if clients_restants and all(c.taille_commande > self.probleme.capacite_vehicule for c in clients_restants):
                # Placer chaque client restant dans une tournée séparée
                for client in clients_restants:
                    solution.tournees.append(Tournee([client]))
                clients_restants = []
        
        return solution
    
    def mutation(self, solution: Solution) -> Solution:
        """Applique une mutation à une solution"""
        if random.random() > self.taux_mutation:
            return solution
        
        nouvelle_solution = solution.clone()
        
        # Choisir aléatoirement le type de mutation
        type_mutation = random.choice(["swap", "deplacement", "inversion", "redistribution"])
        
        if type_mutation == "swap" and len(nouvelle_solution.tournees) >= 2:
            # Échanger deux clients entre deux tournées différentes
            tournee1_idx = random.randint(0, len(nouvelle_solution.tournees) - 1)
            tournee1 = nouvelle_solution.tournees[tournee1_idx]
            
            if len(tournee1.clients) > 0:
                tournee2_idx = random.randint(0, len(nouvelle_solution.tournees) - 1)
                while tournee2_idx == tournee1_idx:
                    tournee2_idx = random.randint(0, len(nouvelle_solution.tournees) - 1)
                
                tournee2 = nouvelle_solution.tournees[tournee2_idx]
                
                if len(tournee2.clients) > 0:
                    client1_idx = random.randint(0, len(tournee1.clients) - 1)
                    client2_idx = random.randint(0, len(tournee2.clients) - 1)
                    
                    tournee1.clients[client1_idx], tournee2.clients[client2_idx] = \
                        tournee2.clients[client2_idx], tournee1.clients[client1_idx]
        
        elif type_mutation == "deplacement":
            # Déplacer un client aléatoirement
            if len(nouvelle_solution.tournees) > 0:
                tournee_src_idx = random.randint(0, len(nouvelle_solution.tournees) - 1)
                tournee_src = nouvelle_solution.tournees[tournee_src_idx]
                
                if len(tournee_src.clients) > 0:
                    client_idx = random.randint(0, len(tournee_src.clients) - 1)
                    client = tournee_src.supprimer_client(client_idx)
                    
                    tournee_dest_idx = random.randint(0, len(nouvelle_solution.tournees) - 1)
                    tournee_dest = nouvelle_solution.tournees[tournee_dest_idx]
                    
                    position_insertion = random.randint(0, len(tournee_dest.clients))
                    tournee_dest.clients.insert(position_insertion, client)
                    
                    # Supprimer les tournées vides
                    nouvelle_solution.tournees = [t for t in nouvelle_solution.tournees if not t.est_vide()]
        
        elif type_mutation == "inversion":
            # Inverser une sous-séquence dans une tournée
            if len(nouvelle_solution.tournees) > 0:
                tournee_idx = random.randint(0, len(nouvelle_solution.tournees) - 1)
                tournee = nouvelle_solution.tournees[tournee_idx]
                
                if len(tournee.clients) >= 2:
                    start = random.randint(0, len(tournee.clients) - 2)
                    end = random.randint(start + 1, len(tournee.clients) - 1)
                    
                    tournee.clients[start:end+1] = reversed(tournee.clients[start:end+1])
        
        elif type_mutation == "redistribution" and len(nouvelle_solution.tournees) >= 2:
            # Redistribuer les clients entre tournées en utilisant le sac à dos
            
            # Sélectionner deux tournées aléatoires
            tournee1_idx = random.randint(0, len(nouvelle_solution.tournees) - 1)
            tournee2_idx = random.randint(0, len(nouvelle_solution.tournees) - 1)
            while tournee2_idx == tournee1_idx:
                tournee2_idx = random.randint(0, len(nouvelle_solution.tournees) - 1)
            
            # Regrouper les clients des deux tournées
            clients_communs = []
            clients_communs.extend(nouvelle_solution.tournees[tournee1_idx].clients)
            clients_communs.extend(nouvelle_solution.tournees[tournee2_idx].clients)
            
            if clients_communs:
                # Supprimer les tournées originales
                t1 = nouvelle_solution.tournees.pop(max(tournee1_idx, tournee2_idx))
                t2 = nouvelle_solution.tournees.pop(min(tournee1_idx, tournee2_idx))
                
                # Créer de nouvelles tournées avec l'algorithme du sac à dos
                position_actuelle = self.probleme.depot
                restants = list(clients_communs)
                
                while restants:
                    nouvelle_tournee = Tournee()
                    capacite_restante = self.probleme.capacite_vehicule
                    
                    # Calculer les valeurs
                    valeurs = {}
                    for client in restants:
                        distance = self.probleme.matrice_distances[position_actuelle][client.id]
                        valeurs[client] = 1000 / (distance + 1)
                    
                    # Sélectionner les clients
                    selectionnes = self.knapsack_glouton(
                        restants,
                        capacite_restante,
                        valeurs,
                        lambda c: c.taille_commande
                    )
                    
                    if not selectionnes:
                        # Si aucun client ne peut être ajouté, prendre le plus petit
                        client_min = min(restants, key=lambda c: c.taille_commande)
                        selectionnes = [client_min]
                    
                    # Optimiser l'ordre
                    selectionnes.sort(key=lambda c: self.probleme.matrice_distances[position_actuelle][c.id])
                    
                    # Ajouter à la tournée
                    for client in selectionnes:
                        nouvelle_tournee.ajouter_client(client)
                        position_actuelle = client.id
                        restants.remove(client)
                    
                    # Ajouter la tournée à la solution
                    nouvelle_solution.tournees.append(nouvelle_tournee)
        
        # Optimiser l'ordre dans toutes les tournées
        for tournee in nouvelle_solution.tournees:
            if not tournee.est_vide():
                self.optimiser_ordre_tournee(tournee)
        
        return nouvelle_solution
    
    def reparer_solution(self, solution: Solution) -> Solution:
        """Répare une solution en utilisant l'algorithme du sac à dos"""
        # Collecter tous les clients
        tous_clients = []
        for tournee in solution.tournees:
            tous_clients.extend(tournee.clients)
        
        # Créer une nouvelle solution à partir de ces clients
        nouvelle_solution = self.clients_to_solution_knapsack(tous_clients)
        
        # Optimiser chaque tournée
        for tournee in nouvelle_solution.tournees:
            self.optimiser_ordre_tournee(tournee)
        
        return nouvelle_solution
    
    def optimiser_ordre_tournee(self, tournee: Tournee):
        """Optimise l'ordre des clients dans une tournée avec l'heuristique du plus proche voisin"""
        if len(tournee.clients) <= 1:
            return
        
        clients_non_visites = set(tournee.clients)
        clients_ordonnes = []
        
        # Partir du dépôt
        position_courante = self.probleme.depot
        
        while clients_non_visites:
            # Trouver le client non visité le plus proche
            client_le_plus_proche = min(
                clients_non_visites,
                key=lambda c: self.probleme.matrice_distances[position_courante][c.id]
            )
            
            # Ajouter le client à la liste ordonnée
            clients_ordonnes.append(client_le_plus_proche)
            position_courante = client_le_plus_proche.id
            
            # Marquer le client comme visité
            clients_non_visites.remove(client_le_plus_proche)
        
        # Mettre à jour la tournée avec l'ordre optimisé
        tournee.clients = clients_ordonnes
    
    def creer_clusters(self, clients: List[Client], nb_clusters: int) -> List[List[Client]]:
        """Crée des clusters de clients en utilisant K-means si disponible, sinon utilise une approche basique"""
        if not clients:
            return []
        
        if len(clients) <= nb_clusters:
            return [[client] for client in clients]
        
        if sklearn_available:
            # Utiliser K-means avec la matrice des distances
            X = np.array([[
                self.probleme.matrice_distances[0][c.id], 
                self.probleme.matrice_distances[c.id][0]
            ] for c in clients])
            
            kmeans = KMeans(n_clusters=min(nb_clusters, len(clients)), random_state=0, n_init=10).fit(X)
            
            # Grouper les clients par cluster
            clusters = [[] for _ in range(kmeans.n_clusters)]
            for i, label in enumerate(kmeans.labels_):
                clusters[label].append(clients[i])
            
            return [c for c in clusters if c]
        else:
            # Approche basique: grouper par proximité au dépôt
            clients_tries = sorted(clients, key=lambda c: self.probleme.matrice_distances[0][c.id])
            taille_cluster = max(1, len(clients) // nb_clusters)
            
            clusters = []
            for i in range(0, len(clients), taille_cluster):
                cluster = clients_tries[i:i+taille_cluster]
                if cluster:
                    clusters.append(cluster)
            
            return clusters
    
    def recherche_locale(self, solution: Solution) -> Solution:
        """Applique une recherche locale pour améliorer une solution"""
        solution_amelioree = solution.clone()
        amelioration = True
        iterations = 0
        max_iterations = 5  # Limiter le nombre d'itérations pour éviter de prendre trop de temps
        
        while amelioration and iterations < max_iterations:
            iterations += 1
            fitness_avant = solution_amelioree.fitness
            
            # 1. Amélioration intra-tournée avec 2-opt
            for tournee in solution_amelioree.tournees:
                self.deux_opt(tournee)
            
            # 2. Amélioration inter-tournées (échange de clients)
            if len(solution_amelioree.tournees) >= 2:
                self.optimiser_echanges_entre_tournees(solution_amelioree)
            
            # 3. Équilibrage des tournées
            if iterations == 1:  # Une seule fois pour éviter de boucler
                solution_amelioree = self.reequilibrer_tournees(solution_amelioree)
            
            # Évaluer la solution améliorée
            self.evaluer_fitness(solution_amelioree)
            
            # Vérifier s'il y a eu une amélioration
            if solution_amelioree.fitness >= fitness_avant:
                amelioration = False
        
        return solution_amelioree
    
    def deux_opt(self, tournee: Tournee):
        """Amélioration 2-opt pour une tournée"""
        if len(tournee.clients) < 4:
            return
        
        amelioration = True
        iterations = 0
        max_iterations = 20  # Limiter pour éviter des boucles trop longues
        
        while amelioration and iterations < max_iterations:
            iterations += 1
            amelioration = False
            
            for i in range(len(tournee.clients) - 2):
                for j in range(i + 2, min(i + 10, len(tournee.clients))):  # Limiter la fenêtre pour plus de rapidité
                    if j - i == 1:
                        continue  # Pas besoin d'inverser des segments adjacents
                    
                    # Calculer le gain potentiel
                    a, b = tournee.clients[i].id, tournee.clients[i+1].id
                    c, d = tournee.clients[j].id, tournee.clients[(j+1) % len(tournee.clients)].id if j < len(tournee.clients) - 1 else self.probleme.depot
                    
                    # Distance actuelle
                    dist_actuelle = (
                        self.probleme.matrice_distances[a][b] +
                        self.probleme.matrice_distances[c][d]
                    )
                    
                    # Distance après échange
                    dist_nouvelle = (
                        self.probleme.matrice_distances[a][c] +
                        self.probleme.matrice_distances[b][d]
                    )
                    
                    # S'il y a une amélioration, on fait l'échange
                    if dist_nouvelle < dist_actuelle:
                        # Inverser le segment
                        tournee.clients[i+1:j+1] = reversed(tournee.clients[i+1:j+1])
                        amelioration = True
    
    def optimiser_echanges_entre_tournees(self, solution: Solution):
        """Optimise les échanges entre toutes les paires de tournées"""
        for i in range(len(solution.tournees)):
            for j in range(i + 1, len(solution.tournees)):
                self.echanger_clients_entre_tournees(solution, i, j)
    
    def echanger_clients_entre_tournees(self, solution: Solution, tournee1_idx: int, tournee2_idx: int):
        """Essaie d'améliorer la solution en échangeant des clients entre deux tournées"""
        tournee1 = solution.tournees[tournee1_idx]
        tournee2 = solution.tournees[tournee2_idx]
        
        # Limiter le nombre d'échanges à tester pour les grandes tournées
        max_essais = min(len(tournee1.clients) * len(tournee2.clients), 100)
        essais = 0
        
        # Utiliser un ensemble pour éviter de tester plusieurs fois les mêmes échanges
        echanges_testes = set()
        
        while essais < max_essais:
            # Choisir deux clients aléatoires
            i = random.randint(0, len(tournee1.clients) - 1)
            j = random.randint(0, len(tournee2.clients) - 1)
            
            # Vérifier si cet échange a déjà été testé
            echange = (tournee1.clients[i].id, tournee2.clients[j].id)
            if echange in echanges_testes:
                continue
            
            echanges_testes.add(echange)
            essais += 1
            
            client1 = tournee1.clients[i]
            client2 = tournee2.clients[j]
            
            # Vérifier si l'échange est possible en termes de capacité
            charge_t1 = tournee1.charge_totale() - client1.taille_commande + client2.taille_commande
            charge_t2 = tournee2.charge_totale() - client2.taille_commande + client1.taille_commande
            
            if (charge_t1 <= self.probleme.capacite_vehicule and 
                charge_t2 <= self.probleme.capacite_vehicule):
                
                # Calculer le coût avant échange
                fitness_avant = self.evaluer_fitness(solution)
                
                # Effectuer l'échange
                tournee1.clients[i], tournee2.clients[j] = tournee2.clients[j], tournee1.clients[i]
                
                # Réoptimiser l'ordre des tournées
                self.optimiser_ordre_tournee(tournee1)
                self.optimiser_ordre_tournee(tournee2)
                
                # Calculer le coût après échange
                fitness_apres = self.evaluer_fitness(solution)
                
                # Si l'échange n'améliore pas, annuler
                if fitness_apres >= fitness_avant:
                    tournee1.clients = list(tournee1.clients)  # Recréer une nouvelle liste
                    tournee2.clients = list(tournee2.clients)
                    self.optimiser_ordre_tournee(tournee1)
                    self.optimiser_ordre_tournee(tournee2)
    
    def reequilibrer_tournees(self, solution: Solution) -> Solution:
        """Rééquilibre les tournées pour éviter des tournées trop longues"""
        solution_clone = solution.clone()
        
        # Calculer le temps de chaque tournée
        temps_tournees = [self.calculer_temps_tournee(t) for t in solution_clone.tournees]
        
        # Si aucune tournée n'est trop longue, on ne fait rien
        if max(temps_tournees) <= 240:  # 4 heures max
            return solution_clone
        
        # Identifier les tournées trop longues
        tournees_longues = [i for i, temps in enumerate(temps_tournees) if temps > 240]
        
        for idx_tournee_longue in tournees_longues:
            tournee_longue = solution_clone.tournees[idx_tournee_longue]
            
            # Essayer de déplacer les clients les plus éloignés
            clients_tries = sorted(
                tournee_longue.clients,
                key=lambda c: max(
                    self.probleme.matrice_distances[c.id][autre.id]
                    for autre in tournee_longue.clients if autre != c
                ),
                reverse=True
            )
            
            # Prendre les 3 clients les plus éloignés
            for client in clients_tries[:3]:
                # Chercher la tournée avec la meilleure insertion possible
                meilleure_tournee_idx = -1
                meilleur_cout = float('inf')
                
                for i, autre_tournee in enumerate(solution_clone.tournees):
                    if i == idx_tournee_longue:
                        continue
                    
                    # Vérifier si le client peut être ajouté à cette tournée
                    if autre_tournee.charge_totale() + client.taille_commande <= self.probleme.capacite_vehicule:
                        # Calculer le coût d'insertion
                        position_courante = self.probleme.depot if not autre_tournee.clients else autre_tournee.clients[-1].id
                        cout = self.probleme.matrice_distances[position_courante][client.id]
                        
                        if cout < meilleur_cout:
                            meilleur_cout = cout
                            meilleure_tournee_idx = i
                
                if meilleure_tournee_idx != -1:
                    # Déplacer le client
                    idx_client = tournee_longue.clients.index(client)
                    client_deplace = tournee_longue.clients.pop(idx_client)
                    solution_clone.tournees[meilleure_tournee_idx].clients.append(client_deplace)
                    
                    # Réoptimiser les tournées
                    self.optimiser_ordre_tournee(tournee_longue)
                    self.optimiser_ordre_tournee(solution_clone.tournees[meilleure_tournee_idx])
                    
                    # Recalculer les temps
                    temps_tournees[idx_tournee_longue] = self.calculer_temps_tournee(tournee_longue)
                    temps_tournees[meilleure_tournee_idx] = self.calculer_temps_tournee(solution_clone.tournees[meilleure_tournee_idx])
                    
                    # Si la tournée n'est plus trop longue, on arrête
                    if temps_tournees[idx_tournee_longue] <= 240:
                        break
        
        # Si certaines tournées sont encore trop longues, on peut essayer de les scinder
        temps_tournees = [self.calculer_temps_tournee(t) for t in solution_clone.tournees]
        tournees_longues = [i for i, temps in enumerate(temps_tournees) if temps > 240]
        
        if tournees_longues:
            # Recréer une solution à partir de tous les clients
            tous_clients = []
            for tournee in solution_clone.tournees:
                tous_clients.extend(tournee.clients)
            
            # Recréer la solution avec l'algorithme du sac à dos
            solution_clone = self.clients_to_solution_knapsack(tous_clients)
        
        return solution_clone
    
    def executer(self):
        """Exécute l'algorithme génétique"""
        temps_debut = time.time()
        
        # Initialiser la population
        self.initialiser_population()
        
        # Trouver la meilleure solution initiale
        self.meilleure_solution = min(self.population, key=lambda s: s.fitness).clone()
        
        # Boucle principale de l'algorithme génétique
        for generation in range(self.max_generations):
            self.generation_courante = generation
            
            # Vérifier si le temps est écoulé
            if time.time() - temps_debut > self.temps_max:
                logging.info(f"Temps écoulé après {generation} générations")
                break
            
            # Créer une nouvelle population
            nouvelle_population = []
            
            # Élitisme: conserver les meilleures solutions
            nombre_elites = int(self.elitisme * self.taille_population)
            elites = sorted(self.population, key=lambda s: s.fitness)[:nombre_elites]
            nouvelle_population.extend([elite.clone() for elite in elites])
            
            # Remplir le reste de la population avec de nouvelles solutions
            while len(nouvelle_population) < self.taille_population:
                # Sélection
                parent1 = self.selection_tournoi()
                parent2 = self.selection_tournoi()
                
                # Croisement
                enfant = self.croisement(parent1, parent2)
                
                # Mutation
                enfant = self.mutation(enfant)
                
                # Réparation intelligente si nécessaire (10% des individus)
                if random.random() < 0.1:
                    enfant = self.reparer_solution(enfant)
                
                # Recherche locale (30% des individus)
                if random.random() < 0.3:
                    enfant = self.recherche_locale(enfant)
                
                # Évaluer la fitness
                self.evaluer_fitness(enfant)
                
                # Ajouter à la nouvelle population
                nouvelle_population.append(enfant)
            
            # Mettre à jour la population
            self.population = nouvelle_population
            
            # Mettre à jour la meilleure solution
            meilleure_solution_gen = min(self.population, key=lambda s: s.fitness)
            if meilleure_solution_gen.fitness < self.meilleure_solution.fitness:
                self.meilleure_solution = meilleure_solution_gen.clone()
                logging.info(f"Génération {generation}: Fitness = {self.meilleure_solution.fitness:.2f}, "
                      f"Nombre de tournées = {len(self.meilleure_solution.tournees)}")
            
            # Appliquer une recherche locale aux 5 meilleures solutions toutes les 10 générations
            if generation % 10 == 0:
                top_solutions = sorted(self.population, key=lambda s: s.fitness)[:5]
                for i, solution in enumerate(top_solutions):
                    amelioree = self.recherche_locale(solution)
                    self.evaluer_fitness(amelioree)
                    if amelioree.fitness < solution.fitness:
                        self.population[self.population.index(solution)] = amelioree
                        logging.info(f"Amélioration de la solution {i+1} par recherche locale: "
                                    f"{solution.fitness:.2f} -> {amelioree.fitness:.2f}")
        
        # Appliquer une dernière recherche locale à la meilleure solution
        self.meilleure_solution = self.recherche_locale(self.meilleure_solution)
        self.evaluer_fitness(self.meilleure_solution)
        
        temps_execution = time.time() - temps_debut
        logging.info(f"Exécution terminée en {temps_execution:.2f} secondes")
        logging.info(f"Meilleure fitness: {self.meilleure_solution.fitness:.2f}")
        logging.info(f"Nombre de tournées: {len(self.meilleure_solution.tournees)}")
        
        return self.meilleure_solution