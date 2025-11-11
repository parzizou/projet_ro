# -*- coding: utf-8 -*-
"""
ga_parameter_analyzer.py
Analyseur complet des paramètres de l'algorithme génétique.

Ce module permet de :
1. Tester chaque paramètre individuellement
2. Trouver les meilleures combinaisons de paramètres
3. Utiliser le multi-threading pour accélérer les tests
4. Sauvegarder les résultats pour analyse
"""

import os
import sys
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import statistics

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.cvrp_data import load_cvrp_instance, CVRPInstance
from src.core.ga import genetic_algorithm
from src.core.solution import solution_total_cost


@dataclass
class ParameterTestResult:
    """Résultat d'un test de paramètre."""
    parameter_name: str
    parameter_value: Any
    cost_mean: float
    cost_std: float
    cost_min: int
    cost_max: int
    time_mean: float = 0.0
    gap_mean: Optional[float] = None
    gap_std: Optional[float] = None


@dataclass
class CombinationResult:
    """Résultat d'un test de combinaison de paramètres."""
    parameters: Dict[str, Any]
    cost_mean: float
    cost_std: float
    cost_min: int
    cost_max: int
    improvement: float  # Pourcentage d'amélioration vs baseline
    gap_mean: Optional[float] = None


def _run_ga_single(instance_path: str, params: Dict[str, Any], 
                   time_limit: float, generations: int) -> int:
    """
    Exécute l'AG une fois avec les paramètres donnés.
    Fonction worker pour le multi-threading.
    """
    instance = load_cvrp_instance(instance_path)
    
    result = genetic_algorithm(
        instance,
        pop_size=params.get('pop_size', 100),
        tournament_k=params.get('tournament_k', 3),
        elitism=params.get('elitism', 3),
        pc=params.get('pc', 0.8),
        pm=params.get('pm', 0.02),
        use_2opt=params.get('use_2opt', True),
        two_opt_prob=params.get('two_opt_prob', 0.5),
        time_limit_sec=time_limit,
        generations=generations,
        verbose=False
    )
    
    return result.cost


class GAParameterAnalyzer:
    """Analyseur de paramètres pour l'algorithme génétique."""
    
    def __init__(self, instance_path: str, target_optimum: Optional[float] = None, n_runs: int = 5):
        """
        Initialise l'analyseur.
        
        Args:
            instance_path: Chemin vers le fichier .vrp
            target_optimum: Optimum connu pour calculer le gap (optionnel)
            n_runs: Nombre de répétitions par test (défaut: 5)
        """
        self.instance_path = instance_path
        self.target_optimum = target_optimum
        self.n_runs = n_runs
        self.instance: CVRPInstance = load_cvrp_instance(instance_path)
        
        # Résultats
        self.baseline_result: Optional[ParameterTestResult] = None
        self.individual_results: Dict[str, List[ParameterTestResult]] = {}
        self.combination_results: List[CombinationResult] = []
        
        print(f"Instance chargée: {self.instance.name}")
        print(f"Dimension: {self.instance.dimension}, Capacité: {self.instance.capacity}")
        
        # Définir les espaces de paramètres à tester
        self.parameter_spaces = {
            'pop_size': [30, 50, 80, 100, 120, 150, 200, 250, 300],
            'tournament_k': [2, 3, 4, 5, 6, 7, 8],
            'elitism': [0, 2, 4, 6, 8, 10, 12, 15, 20, 25, 30],
            'pc': [0.6, 0.7, 0.8, 0.85, 0.9, 0.92, 0.95, 0.98],
            'pm': [0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35],
            'two_opt_prob': [0.0, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8, 1.0],
            'use_2opt': [True, False]
        }
        
        # Paramètres par défaut (baseline)
        self.default_params = {
            'pop_size': 100,
            'tournament_k': 3,
            'elitism': 10,
            'pc': 0.9,
            'pm': 0.02,
            'two_opt_prob': 0.5,
            'use_2opt': True
        }
    
    def _calculate_gap(self, cost: float) -> Optional[float]:
        """Calcule le gap par rapport à l'optimum."""
        if self.target_optimum and self.target_optimum > 0:
            return 100.0 * (cost - self.target_optimum) / self.target_optimum
        return None
    
    def _run_multiple_tests(self, params: Dict[str, Any], num_runs: int,
                           time_limit: float, generations: int,
                           max_workers: Optional[int] = None) -> Tuple[List[int], float]:
        """
        Exécute plusieurs tests en parallèle.
        
        Returns:
            Tuple (liste des coûts, temps d'exécution)
        """
        start_time = time.time()
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(_run_ga_single, self.instance_path, params, 
                              time_limit, generations)
                for _ in range(num_runs)
            ]
            
            costs = [future.result() for future in as_completed(futures)]
        
        elapsed = time.time() - start_time
        return costs, elapsed
    
    def test_individual_parameters(self, num_runs: Optional[int] = None, time_limit: float = 30.0,
                                  generations: int = 20000, max_workers: Optional[int] = None):
        """
        Teste chaque paramètre individuellement.
        
        Args:
            num_runs: Nombre d'exécutions par configuration (None = utilise self.n_runs)
            time_limit: Limite de temps par exécution (secondes)
            generations: Nombre max de générations
            max_workers: Nombre de processus parallèles (None = auto)
        """
        if num_runs is None:
            num_runs = self.n_runs
            
        print("\n" + "="*60)
        print("ANALYSE DES PARAMÈTRES INDIVIDUELS")
        print("="*60)
        
        # 1. Établir la baseline
        print("\nÉtablissement de la baseline...")
        costs, elapsed = self._run_multiple_tests(self.default_params, num_runs, 
                                           time_limit, generations, max_workers)
        
        self.baseline_result = ParameterTestResult(
            parameter_name="baseline",
            parameter_value="default",
            cost_mean=statistics.mean(costs),
            cost_std=statistics.stdev(costs) if len(costs) > 1 else 0.0,
            cost_min=min(costs),
            cost_max=max(costs),
            time_mean=elapsed / num_runs,
            gap_mean=self._calculate_gap(statistics.mean(costs))
        )
        
        print(f"Baseline établie: Coût moyen = {self.baseline_result.cost_mean:.1f}")
        
        # 2. Tester chaque paramètre
        total_configs = sum(len(values) for values in self.parameter_spaces.values())
        print(f"\nTests individuels: {total_configs} configurations à tester")
        
        config_count = 0
        for param_name, param_values in self.parameter_spaces.items():
            print(f"\n--- Test du paramètre: {param_name} ---")
            print(f"Valeurs à tester: {param_values}")
            
            param_results = []
            
            for value in param_values:
                config_count += 1
                
                # Créer les paramètres de test
                test_params = self.default_params.copy()
                test_params[param_name] = value
                
                # Exécuter les tests
                costs, elapsed = self._run_multiple_tests(test_params, num_runs,
                                                          time_limit, generations, max_workers)
                
                # Calculer les statistiques
                mean_cost = statistics.mean(costs)
                std_cost = statistics.stdev(costs) if len(costs) > 1 else 0.0
                
                result = ParameterTestResult(
                    parameter_name=param_name,
                    parameter_value=value,
                    cost_mean=mean_cost,
                    cost_std=std_cost,
                    cost_min=min(costs),
                    cost_max=max(costs),
                    time_mean=elapsed / num_runs,
                    gap_mean=self._calculate_gap(mean_cost)
                )
                
                param_results.append(result)
                
                # Afficher le progrès
                improvement = ((self.baseline_result.cost_mean - mean_cost) / 
                             self.baseline_result.cost_mean) * 100
                print(f"  {param_name}={value}: Coût={mean_cost:.1f} "
                      f"({improvement:+.1f}%) [{config_count}/{total_configs}]")
            
            # Trier par coût et stocker
            param_results.sort(key=lambda x: x.cost_mean)
            self.individual_results[param_name] = param_results
            
            # Afficher le meilleur
            best = param_results[0]
            improvement = ((self.baseline_result.cost_mean - best.cost_mean) / 
                         self.baseline_result.cost_mean) * 100
            print(f"  >>> MEILLEUR {param_name}: {best.parameter_value} "
                  f"(Coût: {best.cost_mean:.1f}, Amélioration: {improvement:+.1f}%)")
    
    def find_best_combinations(self, top_n_per_param: int = 3, n_combinations: int = 10,
                              combination_runs: Optional[int] = None,
                              time_limit: float = 45.0, generations: int = 25000,
                              max_workers: Optional[int] = None):
        """
        Trouve les meilleures combinaisons en testant les top paramètres de chaque catégorie.
        
        Args:
            top_n_per_param: Nombre de meilleures valeurs à prendre par paramètre
            n_combinations: Nombre de combinaisons à tester
            combination_runs: Nombre d'exécutions par combinaison (None = utilise self.n_runs)
            time_limit: Limite de temps par exécution
            generations: Nombre max de générations
            max_workers: Nombre de processus parallèles
        """
        if combination_runs is None:
            combination_runs = self.n_runs
            
        if not self.individual_results:
            print("❌ Erreur: Exécutez d'abord test_individual_parameters()")
            return
        
        print("\n" + "="*60)
        print("RECHERCHE DES MEILLEURES COMBINAISONS")
        print("="*60)
        
        # Sélectionner les top-N de chaque paramètre
        best_values = {}
        for param_name, results in self.individual_results.items():
            top_results = results[:top_n_per_param]
            best_values[param_name] = [r.parameter_value for r in top_results]
            print(f"{param_name}: {best_values[param_name]}")
        
        # Générer les combinaisons candidates
        combinations_to_test = []
        
        # Combinaison 1: Tous les meilleurs
        best_combo = {param: values[0] for param, values in best_values.items()}
        combinations_to_test.append(best_combo)
        
        # Combinaisons 2-N: Varier intelligemment
        import random
        random.seed(42)
        
        while len(combinations_to_test) < min(n_combinations, 50):
            combo = {param: random.choice(values) 
                    for param, values in best_values.items()}
            if combo not in combinations_to_test:
                combinations_to_test.append(combo)
        
        print(f"\nTest de {len(combinations_to_test)} combinaisons candidates...")
        
        # Tester chaque combinaison
        for i, combo in enumerate(combinations_to_test, 1):
            costs, _ = self._run_multiple_tests(combo, combination_runs,
                                               time_limit, generations, max_workers)
            
            mean_cost = statistics.mean(costs)
            std_cost = statistics.stdev(costs) if len(costs) > 1 else 0.0
            improvement = ((self.baseline_result.cost_mean - mean_cost) / 
                          self.baseline_result.cost_mean) * 100
            
            result = CombinationResult(
                parameters=combo,
                cost_mean=mean_cost,
                cost_std=std_cost,
                cost_min=min(costs),
                cost_max=max(costs),
                improvement=improvement,
                gap_mean=self._calculate_gap(mean_cost)
            )
            
            self.combination_results.append(result)
            print(f"Combinaison {i}: Coût={mean_cost:.1f} ({improvement:+.1f}%)")
        
        # Trier par coût
        self.combination_results.sort(key=lambda x: x.cost_mean)
        
        # Afficher le top 5
        print(f"\n🏆 TOP 5 MEILLEURES COMBINAISONS:")
        for i, result in enumerate(self.combination_results[:5], 1):
            print(f"\n{i}. Coût: {result.cost_mean:.1f} (Amélioration: {result.improvement:+.1f}%)")
            for param, value in result.parameters.items():
                print(f"   {param}: {value}")
    
    def save_results(self, filepath: str):
        """
        Sauvegarde les résultats au format JSON.
        
        Args:
            filepath: Chemin du fichier de sauvegarde
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "instance_name": self.instance.name,
                "target_optimum": self.target_optimum,
                "n_runs": self.n_runs
            },
            "baseline_result": asdict(self.baseline_result) if self.baseline_result else None,
            "individual_results": {
                param: [asdict(r) for r in results]
                for param, results in self.individual_results.items()
            },
            "combination_results": [asdict(r) for r in self.combination_results]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Résultats sauvegardés: {filepath}")
    
    def load_results(self, filepath: str):
        """
        Charge des résultats depuis un fichier JSON.
        
        Args:
            filepath: Chemin du fichier à charger
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Charger baseline
        if data.get("baseline_result"):
            self.baseline_result = ParameterTestResult(**data["baseline_result"])
        
        # Charger résultats individuels
        self.individual_results = {}
        for param, results in data.get("individual_results", {}).items():
            self.individual_results[param] = [
                ParameterTestResult(**r) for r in results
            ]
        
        # Charger combinaisons
        self.combination_results = [
            CombinationResult(**r) for r in data.get("combination_results", [])
        ]
        
        print(f"✅ Résultats chargés depuis: {filepath}")


if __name__ == "__main__":
    # Test rapide
    analyzer = GAParameterAnalyzer("data/instances/data.vrp", n_runs=2)
    analyzer.test_individual_parameters(time_limit=10.0, generations=5000)
    analyzer.find_best_combinations(top_n_per_param=2)
    analyzer.save_results("results/parameter_analysis/quick_test.json")
