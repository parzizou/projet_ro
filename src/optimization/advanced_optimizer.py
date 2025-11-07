# -*- coding: utf-8 -*-
"""
optimize_ga_parameters.py
Script pour optimiser les paramètres de l'algorithme génétique pour le CVRP.

Ce script teste différentes combinaisons de paramètres pour trouver la configuration
optimale qui donne les meilleurs résultats sur l'instance CVRP donnée.
"""

from __future__ import annotations
import json
import time
import os
import sys
from typing import Dict, List, Tuple, Any
from itertools import product
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.cvrp_data import load_cvrp_instance, CVRPInstance
from src.core.ga import genetic_algorithm
from src.core.solution import verify_solution, solution_total_cost


class ParameterOptimizer:
    """Classe pour optimiser les paramètres de l'algorithme génétique."""
    
    def __init__(self, instance_path: str, target_optimum: int | None = None):
        """
        Initialise l'optimiseur de paramètres.
        
        Args:
            instance_path: Chemin vers le fichier .vrp
            target_optimum: Valeur optimale connue pour calculer le gap (optionnel)
        """
        self.instance_path = instance_path
        self.target_optimum = target_optimum
        self.instance: CVRPInstance = load_cvrp_instance(instance_path)
        self.results: List[Dict[str, Any]] = []
        
        print(f"Instance chargée: {self.instance.name}")
        print(f"Dimension: {self.instance.dimension}, Capacité: {self.instance.capacity}")
        if target_optimum:
            print(f"Optimum cible: {target_optimum}")
    
    def define_parameter_space(self) -> Dict[str, List[Any]]:
        """
        Définit l'espace des paramètres à tester.
        
        Returns:
            Dictionnaire contenant les différentes valeurs à tester pour chaque paramètre
        """
        return {
            'pop_size': [50, 80, 110, 150],
            'tournament_k': [2, 3, 4, 5],
            'elitism': [2, 4, 6, 8],
            'pc': [0.8, 0.9, 0.95, 0.98],  # probabilité de crossover
            'pm': [0.15, 0.2, 0.25, 0.3],  # probabilité de mutation
            'two_opt_prob': [0.2, 0.35, 0.5, 0.65],
            'use_2opt': [True, False]
        }
    
    def define_quick_parameter_space(self) -> Dict[str, List[Any]]:
        """
        Définit un espace réduit pour des tests rapides.
        
        Returns:
            Dictionnaire contenant un sous-ensemble de paramètres à tester
        """
        return {
            'pop_size': [80, 110],
            'tournament_k': [3, 4],
            'elitism': [4, 6],
            'pc': [0.9, 0.95],
            'pm': [0.2, 0.25],
            'two_opt_prob': [0.35, 0.5],
            'use_2opt': [True]
        }
    
    def run_single_ga_instance(
        self,
        params: Dict[str, Any],
        run_id: int,
        time_limit: float = 60.0,
        generations: int = 50000
    ) -> Tuple[int, int, float]:
        """
        Exécute une seule instance de l'algorithme génétique.
        
        Args:
            params: Dictionnaire des paramètres à tester
            run_id: Identifiant du run
            time_limit: Limite de temps en secondes
            generations: Nombre maximum de générations
            
        Returns:
            Tuple (coût, nombre_véhicules, temps_exécution)
        """
        start_time = time.time()
        
        # Exécution de l'algorithme génétique
        best_individual = genetic_algorithm(
            inst=self.instance,
            pop_size=params['pop_size'],
            generations=generations,
            tournament_k=params['tournament_k'],
            elitism=params['elitism'],
            pc=params['pc'],
            pm=params['pm'],
            use_2opt=params.get('use_2opt', False),
            two_opt_prob=params.get('two_opt_prob', 1.0),
            time_limit_sec=time_limit,
            verbose=False,  # Désactiver verbose en mode multi-thread
            seed=run_id * 1000  # Seed différent pour chaque run
        )
        
        exec_time = time.time() - start_time
        cost = best_individual.cost
        num_veh = len(best_individual.routes)
        
        return cost, num_veh, exec_time

    def run_single_test(
        self, 
        params: Dict[str, Any], 
        num_runs: int = 3,
        time_limit: float = 60.0,
        generations: int = 50000,
        max_workers: int = None
    ) -> Dict[str, Any]:
        """
        Exécute un test avec des paramètres donnés (version multi-threadée).
        
        Args:
            params: Dictionnaire des paramètres à tester
            num_runs: Nombre d'exécutions pour obtenir une moyenne
            time_limit: Limite de temps en secondes pour chaque run
            generations: Nombre maximum de générations
            max_workers: Nombre de threads (None = auto)
            
        Returns:
            Résultats du test avec statistiques
        """
        print(f"\nTest avec paramètres: {params}")
        
        if max_workers is None:
            max_workers = min(num_runs, os.cpu_count() or 1)
        
        costs = []
        num_vehicles = []
        exec_times = []
        
        # Exécution parallèle des runs
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Soumission de tous les jobs
            future_to_run = {
                executor.submit(
                    self.run_single_ga_instance,
                    params, run_id, time_limit, generations
                ): run_id for run_id in range(num_runs)
            }
            
            # Collecte des résultats
            for future in as_completed(future_to_run):
                run_id = future_to_run[future]
                try:
                    cost, num_veh, exec_time = future.result()
                    costs.append(cost)
                    num_vehicles.append(num_veh)
                    exec_times.append(exec_time)
                    
                    print(f"  Run {run_id + 1}/{num_runs}... Coût: {cost}, Véhicules: {num_veh}, Temps: {exec_time:.1f}s")
                    
                except Exception as e:
                    print(f"  Run {run_id + 1}/{num_runs}... ERREUR: {e}")
        
        if not costs:
            return None  # Aucun résultat valide
        
        # Calcul des statistiques
        result = {
            'parameters': params.copy(),
            'cost_mean': statistics.mean(costs),
            'cost_std': statistics.stdev(costs) if len(costs) > 1 else 0,
            'cost_min': min(costs),
            'cost_max': max(costs),
            'vehicles_mean': statistics.mean(num_vehicles),
            'time_mean': statistics.mean(exec_times),
            'num_runs': len(costs),
            'all_costs': costs
        }
        
        # Calcul du gap si optimum connu
        if self.target_optimum and self.target_optimum > 0:
            result['gap_mean'] = 100.0 * (result['cost_mean'] - self.target_optimum) / self.target_optimum
            result['gap_min'] = 100.0 * (result['cost_min'] - self.target_optimum) / self.target_optimum
        
        return result
    
    def grid_search(
        self, 
        parameter_space: Dict[str, List[Any]] = None,
        num_runs: int = 3,
        time_limit: float = 60.0,
        generations: int = 50000,
        max_combinations: int = None,
        max_workers: int = None
    ) -> List[Dict[str, Any]]:
        """
        Effectue une recherche en grille sur l'espace des paramètres.
        
        Args:
            parameter_space: Espace des paramètres (utilise l'espace par défaut si None)
            num_runs: Nombre d'exécutions par combinaison
            time_limit: Limite de temps par run
            generations: Nombre maximum de générations
            max_combinations: Limite du nombre de combinaisons à tester
            max_workers: Nombre de threads pour parallelisation (None = auto)
            
        Returns:
            Liste des résultats triés par performance
        """
        if parameter_space is None:
            parameter_space = self.define_parameter_space()
        
        # Génération de toutes les combinaisons
        param_names = list(parameter_space.keys())
        param_values = list(parameter_space.values())
        combinations = list(product(*param_values))
        
        # Limitation du nombre de combinaisons si demandé
        if max_combinations and len(combinations) > max_combinations:
            import random
            random.shuffle(combinations)
            combinations = combinations[:max_combinations]
            print(f"Limitation à {max_combinations} combinaisons sur {len(list(product(*param_values)))} possibles")
        
        print(f"Test de {len(combinations)} combinaisons de paramètres...")
        print(f"Temps estimé: ~{len(combinations) * num_runs * time_limit / 60:.1f} minutes")
        
        results = []
        
        for i, combination in enumerate(combinations):
            params = dict(zip(param_names, combination))
            
            print(f"\n--- Combinaison {i + 1}/{len(combinations)} ---")
            result = self.run_single_test(params, num_runs, time_limit, generations, max_workers)
            
            if result is not None:
                results.append(result)
                print(f"Résultat: Coût moyen = {result['cost_mean']:.1f}")
                if 'gap_mean' in result:
                    print(f"          Gap moyen = {result['gap_mean']:.2f}%")
        
        # Tri par coût moyen croissant
        results.sort(key=lambda x: x['cost_mean'])
        self.results = results
        
        return results
    
    def random_search(
        self,
        parameter_space: Dict[str, List[Any]] = None,
        num_tests: int = 20,
        num_runs: int = 3,
        time_limit: float = 60.0,
        generations: int = 50000,
        max_workers: int = None
    ) -> List[Dict[str, Any]]:
        """
        Effectue une recherche aléatoire sur l'espace des paramètres.
        
        Args:
            parameter_space: Espace des paramètres
            num_tests: Nombre de combinaisons aléatoires à tester
            num_runs: Nombre d'exécutions par combinaison
            time_limit: Limite de temps par run
            generations: Nombre maximum de générations
            max_workers: Nombre de threads pour parallelisation (None = auto)
            
        Returns:
            Liste des résultats triés par performance
        """
        import random
        
        if parameter_space is None:
            parameter_space = self.define_parameter_space()
        
        print(f"Recherche aléatoire avec {num_tests} combinaisons...")
        print(f"Temps estimé: ~{num_tests * num_runs * time_limit / 60:.1f} minutes")
        
        results = []
        
        for i in range(num_tests):
            # Génération aléatoire des paramètres
            params = {}
            for param_name, param_values in parameter_space.items():
                params[param_name] = random.choice(param_values)
            
            print(f"\n--- Test aléatoire {i + 1}/{num_tests} ---")
            result = self.run_single_test(params, num_runs, time_limit, generations, max_workers)
            
            if result is not None:
                results.append(result)
                print(f"Résultat: Coût moyen = {result['cost_mean']:.1f}")
                if 'gap_mean' in result:
                    print(f"          Gap moyen = {result['gap_mean']:.2f}%")
        
        # Tri par coût moyen croissant
        results.sort(key=lambda x: x['cost_mean'])
        self.results = results
        
        return results
    
    def print_best_results(self, top_n: int = 5):
        """Affiche les meilleurs résultats."""
        if not self.results:
            print("Aucun résultat disponible.")
            return
        
        print(f"\n{'='*80}")
        print(f"TOP {min(top_n, len(self.results))} MEILLEURS RÉSULTATS")
        print(f"{'='*80}")
        
        for i, result in enumerate(self.results[:top_n]):
            print(f"\n--- Rang {i + 1} ---")
            print(f"Coût moyen: {result['cost_mean']:.1f} ± {result['cost_std']:.1f}")
            print(f"Meilleur coût: {result['cost_min']}")
            print(f"Véhicules moyen: {result['vehicles_mean']:.1f}")
            print(f"Temps moyen: {result['time_mean']:.1f}s")
            
            if 'gap_mean' in result:
                print(f"Gap moyen: {result['gap_mean']:.2f}%")
                print(f"Meilleur gap: {result['gap_min']:.2f}%")
            
            print("Paramètres:")
            for param, value in result['parameters'].items():
                print(f"  {param}: {value}")
    
    def save_results(self, filename: str = "optimization_results.json"):
        """Sauvegarde les résultats dans un fichier JSON."""
        if not self.results:
            print("Aucun résultat à sauvegarder.")
            return
        
        data = {
            'instance_info': {
                'name': self.instance.name,
                'dimension': self.instance.dimension,
                'capacity': self.instance.capacity,
                'target_optimum': self.target_optimum
            },
            'results': self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Résultats sauvegardés dans: {filename}")
    
    def load_results(self, filename: str = "optimization_results.json"):
        """Charge les résultats depuis un fichier JSON."""
        if not os.path.exists(filename):
            print(f"Fichier {filename} introuvable.")
            return
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.results = data['results']
        print(f"Résultats chargés depuis: {filename}")
        print(f"Nombre de résultats: {len(self.results)}")


def main():
    """Fonction principale pour lancer l'optimisation."""
    # Configuration
    instance_path = "data/instances/data.vrp"  # Modifiez selon votre fichier
    target_optimum = 21220      # Modifiez selon votre instance (optionnel)
    
    # Vérification de l'existence du fichier
    if not os.path.exists(instance_path):
        print(f"Fichier {instance_path} introuvable.")
        print("Modifiez la variable 'instance_path' dans la fonction main().")
        sys.exit(1)
    
    # Création de l'optimiseur
    optimizer = ParameterOptimizer(instance_path, target_optimum)
    
    # Configuration du multi-threading
    print(f"\nMulti-threading disponible: {os.cpu_count()} CPU cores détectés")
    max_workers_input = input(f"Nombre de threads à utiliser (Enter pour auto-detect): ").strip()
    max_workers = int(max_workers_input) if max_workers_input else None
    
    if max_workers:
        print(f"Utilisation de {max_workers} threads")
    else:
        print(f"Auto-détection: {os.cpu_count()} threads")
    
    # Choix du type de recherche
    print("\nType de recherche:")
    print("1. Recherche rapide (espace réduit)")
    print("2. Recherche complète (toutes combinaisons)")
    print("3. Recherche aléatoire")
    print("4. Charger résultats précédents")
    
    choice = input("Votre choix (1-4): ").strip()
    
    if choice == "1":
        # Recherche rapide
        param_space = optimizer.define_quick_parameter_space()
        results = optimizer.grid_search(
            parameter_space=param_space,
            num_runs=3,
            time_limit=45.0,
            generations=30000,
            max_combinations=20,
            max_workers=max_workers
        )
    
    elif choice == "2":
        # Recherche complète (attention: peut être très long!)
        param_space = optimizer.define_parameter_space()
        max_comb = int(input("Nombre max de combinaisons (recommandé: 50): ") or "50")
        results = optimizer.grid_search(
            parameter_space=param_space,
            num_runs=2,
            time_limit=60.0,
            generations=40000,
            max_combinations=max_comb,
            max_workers=max_workers
        )
    
    elif choice == "3":
        # Recherche aléatoire
        num_tests = int(input("Nombre de tests aléatoires (recommandé: 20): ") or "20")
        results = optimizer.random_search(
            num_tests=num_tests,
            num_runs=3,
            time_limit=60.0,
            generations=40000,
            max_workers=max_workers
        )
    
    elif choice == "4":
        # Chargement de résultats existants
        filename = input("Nom du fichier (par défaut: optimization_results.json): ").strip()
        if not filename:
            filename = "optimization_results.json"
        optimizer.load_results(filename)
    
    else:
        print("Choix invalide.")
        sys.exit(1)
    
    # Affichage et sauvegarde des résultats
    if choice != "4":
        # Génération d'un nom de fichier unique avec timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"optimization_results_{timestamp}.json"
        optimizer.save_results(results_filename)
    
    optimizer.print_best_results(top_n=5)
    
    # Suggestion de meilleurs paramètres
    if optimizer.results:
        best_params = optimizer.results[0]['parameters']
        print(f"\n{'='*50}")
        print("MEILLEURS PARAMÈTRES RECOMMANDÉS:")
        print(f"{'='*50}")
        for param, value in best_params.items():
            print(f"{param} = {value}")


if __name__ == "__main__":
    main()