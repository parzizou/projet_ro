import numpy as np
import random
import time
import logging
from typing import List, Dict

from models import Client, ProblemVRP, Tournee, Solution
from genetic_algorithm import AlgorithmeGenetique

# début main.py

def generer_probleme_aleatoire(n_villes: int, capacite_vehicule: float = 100) -> ProblemVRP:
    """Génère un problème aléatoire de tournées de véhicules"""
    # Générer les coordonnées des villes
    coords = np.random.rand(n_villes, 2) * 100
    
    # Calculer la matrice des distances
    matrice_distances = np.zeros((n_villes, n_villes))
    for i in range(n_villes):
        for j in range(n_villes):
            if i != j:
                matrice_distances[i, j] = np.sqrt(
                    (coords[i, 0] - coords[j, 0]) ** 2 + 
                    (coords[i, 1] - coords[j, 1]) ** 2
                )
    
    # Générer les clients (sans le dépôt)
    clients = []
    for i in range(1, n_villes):  # Le dépôt est à l'index 0
        taille_commande = random.uniform(10, 30)  # Entre 10 et 30 unités
        clients.append(Client(id=i, taille_commande=taille_commande))
    
    return ProblemVRP(
        n_villes=n_villes,
        matrice_distances=matrice_distances,
        capacite_vehicule=capacite_vehicule,
        clients=clients
    )


def afficher_solution(solution, probleme: ProblemVRP):
    """Affiche une solution de manière lisible"""
    print("\nSolution détaillée:")
    print(f"Nombre de tournées: {len(solution.tournees)}")
    print(f"Fitness totale: {solution.fitness:.2f}")
    
    temps_total = 0
    charge_totale = 0
    clients_total = 0
    temps_max = 0
    temps_min = float('inf')
    
    for idx, tournee in enumerate(solution.tournees):
        print(f"\nTournée {idx+1}:")
        print(f"  Charge: {tournee.charge_totale():.1f}/{probleme.capacite_vehicule}")
        
        temps_tournee = 0
        position = probleme.depot
        heure_actuelle = probleme.heure_debut  # 8h du matin
        
        print(f"  Trajet: Dépôt (0)", end="")
        
        for client in tournee.clients:
            temps_trajet = probleme.matrice_distances[position][client.id]
            temps_tournee += temps_trajet
            heure_actuelle += temps_trajet
            position = client.id
            
            # Convertir les minutes en heures et minutes
            h = int(heure_actuelle // 60)
            m = int(heure_actuelle % 60)
            print(f" -> {client.id} ({temps_trajet:.1f}min, {h:02}:{m:02})", end="")
            
            # Ajouter un temps de service (10 min par client)
            temps_service = 10
            temps_tournee += temps_service
            heure_actuelle += temps_service
        
        # Retour au dépôt
        temps_retour = probleme.matrice_distances[position][probleme.depot]
        temps_tournee += temps_retour
        heure_actuelle += temps_retour
        h = int(heure_actuelle // 60)
        m = int(heure_actuelle % 60)
        print(f" -> Dépôt ({temps_retour:.1f}min, {h:02}:{m:02})")
        
        print(f"  Temps total de la tournée: {temps_tournee:.1f} minutes ({temps_tournee/60:.2f}h)")
        print(f"  Nombre de clients: {len(tournee.clients)}")
        
        # Vérification de la fenêtre de temps
        heure_fin = probleme.heure_debut + temps_tournee
        if heure_fin > probleme.heure_fin:
            heures_depassement = (heure_fin - probleme.heure_fin) / 60
            print(f"  ⚠️ ATTENTION: Dépassement de {heures_depassement:.2f} heures par rapport à la fenêtre de temps")
        
        temps_total += temps_tournee
        charge_totale += tournee.charge_totale()
        clients_total += len(tournee.clients)
        temps_max = max(temps_max, temps_tournee)
        temps_min = min(temps_min, temps_tournee)
    
    print("\nRésumé de la solution:")
    print(f"Temps total de toutes les tournées: {temps_total:.1f} minutes ({temps_total/60:.2f}h)")
    print(f"Moyenne par tournée: {temps_total / len(solution.tournees):.1f} minutes ({temps_total/60/len(solution.tournees):.2f}h)")
    print(f"Tournée la plus longue: {temps_max:.1f} minutes ({temps_max/60:.2f}h)")
    print(f"Tournée la plus courte: {temps_min:.1f} minutes ({temps_min/60:.2f}h)")
    print(f"Écart-type des durées: {np.std([calcul_temps_tournee(t, probleme) for t in solution.tournees]):.1f} minutes")
    print(f"Charge moyenne par tournée: {charge_totale / len(solution.tournees):.1f} / {probleme.capacite_vehicule}")
    print(f"Clients par tournée en moyenne: {clients_total / len(solution.tournees):.1f}")


def calcul_temps_tournee(tournee: Tournee, probleme: ProblemVRP) -> float:
    """Calcule le temps total d'une tournée (trajet + service)"""
    temps_total = 0
    position_actuelle = probleme.depot
    
    for client in tournee.clients:
        # Temps de trajet
        temps_total += probleme.matrice_distances[position_actuelle][client.id]
        position_actuelle = client.id
        
        # Temps de service (10 minutes par client)
        temps_total += 10
    
    # Retour au dépôt
    temps_total += probleme.matrice_distances[position_actuelle][probleme.depot]
    
    return temps_total


def main():
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Paramètres du problème
    n_villes = 30  # Nombre total de villes (incluant le dépôt)
    capacite_vehicule = 100
    
    # Générer un problème aléatoire
    print("Génération du problème...")
    probleme = generer_probleme_aleatoire(n_villes, capacite_vehicule)
    print(f"Problème généré avec {n_villes} villes et {len(probleme.clients)} clients")
    
    # Paramètres de l'algorithme génétique
    taille_population = 150
    max_generations = 500
    temps_max = 180  # 3 minutes maximum
    
    # Créer et exécuter l'algorithme génétique
    print("Démarrage de l'algorithme génétique...")
    algo = AlgorithmeGenetique(
        probleme=probleme,
        taille_population=taille_population,
        max_generations=max_generations,
        taux_mutation=0.3,
        taux_croisement=0.85,
        elitisme=0.15,
        temps_max=temps_max
    )
    
    solution = algo.executer()
    
    # Afficher la solution
    afficher_solution(solution, probleme)


if __name__ == "__main__":
    main()