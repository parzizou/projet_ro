import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class Client:
    id: int  # ID du client (numéro de ville)
    taille_commande: float  # Taille de la commande
    
    def __eq__(self, other):
        if isinstance(other, Client):
            return self.id == other.id
        return False
    
    def __hash__(self):
        return hash(self.id)


@dataclass
class Tournee:
    clients: List[Client]  # Liste ordonnée des clients à visiter
    
    def __init__(self, clients=None):
        self.clients = clients if clients is not None else []
    
    def charge_totale(self) -> float:
        """Calcule la charge totale de la tournée"""
        return sum(client.taille_commande for client in self.clients)
    
    def ajouter_client(self, client: Client):
        """Ajoute un client à la tournée"""
        self.clients.append(client)
    
    def supprimer_client(self, index: int) -> Client:
        """Supprime un client de la tournée et le retourne"""
        return self.clients.pop(index)
    
    def est_vide(self) -> bool:
        """Vérifie si la tournée est vide"""
        return len(self.clients) == 0


@dataclass
class Solution:
    tournees: List[Tournee]
    fitness: float = float('inf')
    
    def __init__(self, tournees=None):
        self.tournees = tournees if tournees is not None else []
        self.fitness = float('inf')
    
    def nombre_clients(self) -> int:
        """Retourne le nombre total de clients dans la solution"""
        return sum(len(tournee.clients) for tournee in self.tournees)
    
    def clone(self):
        """Crée une copie profonde de la solution"""
        nouvelle_solution = Solution()
        for tournee in self.tournees:
            nouvelle_tournee = Tournee(clients=list(tournee.clients))
            nouvelle_solution.tournees.append(nouvelle_tournee)
        nouvelle_solution.fitness = self.fitness
        return nouvelle_solution


class ProblemVRP:
    """Classe représentant le problème de tournées de véhicules"""
    
    def __init__(self, n_villes: int, matrice_distances: np.ndarray, 
                 capacite_vehicule: float, clients: List[Client], coords: np.ndarray):
        self.n_villes = n_villes
        # matrice_distances = matrice des TEMPS de trajet (en minutes) entre villes i->j
        self.matrice_distances = matrice_distances
        self.capacite_vehicule = capacite_vehicule
        self.clients = clients
        self.depot = 0  # Le dépôt est toujours la ville 0
        # Coordonnées des villes (pour la visualisation)
        # np.ndarray shape (n_villes, 2) [x, y]
        self.coords = coords
        
        # Heures de début et fin des livraisons (en minutes depuis minuit)
        self.heure_debut = 8 * 60  # 8h00
        self.heure_fin = 18 * 60    # 18h00