# -*- coding: utf-8 -*-
"""
quick_test.py
Script pour tester rapidement quelques configurations de paramètres spécifiques.
"""

from __future__ import annotations
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.cvrp_data import load_cvrp_instance
from src.core.ga import genetic_algorithm
from src.core.solution import verify_solution


def run_single_ga(instance_path: str, config: dict, run_id: int):
    """
    Exécute une seule instance de l'algorithme génétique.
    
    Args:
        instance_path: Chemin vers le fichier .vrp
        config: Configuration des paramètres
        run_id: Identifiant du run
        
    Returns:
        Tuple (coût, temps_exec, nombre_véhicules) ou None si invalide
    """
    # Chargement de l'instance
    instance = load_cvrp_instance(instance_path)
    
    start_time = time.time()
    
    # Exécution de l'algorithme
    best = genetic_algorithm(
        inst=instance,
        pop_size=config['pop_size'],
        generations=config.get('generations', 30000),
        tournament_k=config['tournament_k'],
        elitism=config['elitism'],
        pc=config['pc'],
        pm=config['pm'],
        seed=42 + run_id,
        use_2opt=config['use_2opt'],
        verbose=False,
        two_opt_prob=config['two_opt_prob'],
        time_limit_sec=config.get('time_limit', 30.0)
    )
    
    exec_time = time.time() - start_time
    
    # Vérification
    is_valid, _ = verify_solution(best.routes, instance)
    
    if is_valid:
        return best.cost, exec_time, len(best.routes)
    else:
        return None


def test_configuration(instance_path: str, config: dict, num_runs: int = 3, max_workers: int = None):
    """
    Teste une configuration spécifique de paramètres (version multi-threadée).
    
    Args:
        instance_path: Chemin vers le fichier .vrp
        config: Configuration des paramètres à tester
        num_runs: Nombre d'exécutions pour la moyenne
        max_workers: Nombre de threads (None = auto)
        
    Returns:
        Dictionnaire avec les résultats du test
    """
    print(f"\nTest de configuration: {config['name']}")
    print("-" * 50)
    
    if max_workers is None:
        max_workers = min(num_runs, os.cpu_count() or 1)
    
    costs = []
    times = []
    vehicles = []
    
    # Exécution parallèle des runs
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Soumission de tous les jobs
        future_to_run = {
            executor.submit(run_single_ga, instance_path, config, run_id): run_id 
            for run_id in range(num_runs)
        }
        
        # Collecte des résultats
        for future in as_completed(future_to_run):
            run_id = future_to_run[future]
            try:
                result = future.result()
                if result is not None:
                    cost, exec_time, num_veh = result
                    costs.append(cost)
                    times.append(exec_time)
                    vehicles.append(num_veh)
                    print(f"Run {run_id + 1}/{num_runs}... Coût: {cost}, Temps: {exec_time:.1f}s")
                else:
                    print(f"Run {run_id + 1}/{num_runs}... SOLUTION INVALIDE!")
            except Exception as e:
                print(f"Run {run_id + 1}/{num_runs}... ERREUR: {e}")
    
    if costs:
        result = {
            'config_name': config['name'],
            'parameters': {k: v for k, v in config.items() if k != 'name'},
            'cost_mean': sum(costs) / len(costs),
            'cost_min': min(costs),
            'cost_max': max(costs),
            'cost_std': (sum([(c - sum(costs)/len(costs))**2 for c in costs]) / len(costs))**0.5 if len(costs) > 1 else 0,
            'vehicles_mean': sum(vehicles) / len(vehicles),
            'time_mean': sum(times) / len(times),
            'num_valid_runs': len(costs),
            'all_costs': costs,
            'all_times': times,
            'all_vehicles': vehicles
        }
        
        print(f"\nRésultats ({len(costs)} runs valides):")
        print(f"  Coût moyen: {result['cost_mean']:.1f}")
        print(f"  Meilleur coût: {result['cost_min']}")
        print(f"  Pire coût: {result['cost_max']}")
        print(f"  Véhicules moyen: {result['vehicles_mean']:.1f}")
        print(f"  Temps moyen: {result['time_mean']:.1f}s")
        
        return result
    else:
        print("Aucun résultat valide!")
        return None


def save_results_to_file(results: list, filename: str = "parameter_test_results.txt"):
    """
    Sauvegarde les résultats dans un fichier texte structuré.
    
    Args:
        results: Liste des résultats de tests
        filename: Nom du fichier de sortie
    """
    with open(filename, 'w', encoding='utf-8') as f:
        # En-tête avec timestamp
        from datetime import datetime
        f.write(f"# Résultats de tests de paramètres GA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# Format: config_name|param1:value1|param2:value2|...|cost_mean|cost_min|cost_max|cost_std|vehicles_mean|time_mean|num_runs\n")
        f.write("#\n")
        
        for result in results:
            if result is None:
                continue
                
            # Construction de la ligne avec les paramètres
            line_parts = [result['config_name']]
            
            # Ajout des paramètres
            for param, value in result['parameters'].items():
                line_parts.append(f"{param}:{value}")
            
            # Ajout des métriques
            line_parts.extend([
                f"cost_mean:{result['cost_mean']:.1f}",
                f"cost_min:{result['cost_min']}",
                f"cost_max:{result['cost_max']}",
                f"cost_std:{result['cost_std']:.2f}",
                f"vehicles_mean:{result['vehicles_mean']:.1f}",
                f"time_mean:{result['time_mean']:.1f}",
                f"num_runs:{result['num_valid_runs']}"
            ])
            
            # Ajout des coûts individuels
            costs_str = ",".join(map(str, result['all_costs']))
            line_parts.append(f"all_costs:[{costs_str}]")
            
            f.write("|".join(line_parts) + "\n")
    
    print(f"\nRésultats sauvegardés dans: {filename}")


def save_best_results_summary(results: list, filename: str = "best_results_summary.txt"):
    """
    Sauvegarde un résumé des meilleurs résultats dans un fichier séparé.
    
    Args:
        results: Liste des résultats triés par performance
        filename: Nom du fichier de résumé
    """
    if not results:
        return
    
    # Tri par coût moyen
    sorted_results = sorted([r for r in results if r is not None], key=lambda x: x['cost_mean'])
    
    with open(filename, 'w', encoding='utf-8') as f:
        from datetime import datetime
        f.write(f"# RÉSUMÉ DES MEILLEURS RÉSULTATS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# Configurations triées par performance (meilleur coût d'abord)\n")
        f.write("#\n")
        f.write("# FORMAT:\n")
        f.write("# Rang | Nom_Config | Coût_Moyen | Coût_Min | Écart-Type | Paramètres\n")
        f.write("#" + "="*80 + "\n\n")
        
        # Top 20 ou tous les résultats si moins de 20
        top_results = sorted_results[:min(20, len(sorted_results))]
        
        for i, result in enumerate(top_results, 1):
            f.write(f"RANG {i:2d}\n")
            f.write(f"Configuration: {result['config_name']}\n")
            f.write(f"Coût moyen:   {result['cost_mean']:.1f}\n")
            f.write(f"Meilleur:     {result['cost_min']}\n")
            f.write(f"Pire:         {result['cost_max']}\n")
            f.write(f"Écart-type:   {result['cost_std']:.2f}\n")
            f.write(f"Véhicules:    {result['vehicles_mean']:.1f}\n")
            f.write(f"Temps:        {result['time_mean']:.1f}s\n")
            f.write("Paramètres:\n")
            
            for param, value in result['parameters'].items():
                f.write(f"  {param:<15}: {value}\n")
            
            f.write(f"Tous les coûts: {result['all_costs']}\n")
            f.write("-" * 60 + "\n\n")
        
        # Statistiques globales
        all_costs = [r['cost_mean'] for r in sorted_results]
        f.write("STATISTIQUES GLOBALES\n")
        f.write("=" * 40 + "\n")
        f.write(f"Configurations testées: {len(sorted_results)}\n")
        f.write(f"Meilleur coût global:   {min(all_costs):.1f}\n")
        f.write(f"Pire coût global:       {max(all_costs):.1f}\n")
        f.write(f"Coût moyen global:      {sum(all_costs)/len(all_costs):.1f}\n")
        f.write(f"Amélioration possible:  {(max(all_costs) - min(all_costs)) / max(all_costs) * 100:.1f}%\n")
        
        # Recommandations
        best = sorted_results[0]
        f.write(f"\nCONFIGURATION RECOMMANDÉE\n")
        f.write("=" * 40 + "\n")
        f.write(f"Nom: {best['config_name']}\n")
        f.write("Paramètres optimaux:\n")
        for param, value in best['parameters'].items():
            f.write(f"  {param} = {value}\n")
    
    print(f"Résumé des meilleurs résultats sauvegardé dans: {filename}")


def generate_parameter_variations():
    """
    Génère différentes variations de paramètres à tester.
    
    Returns:
        Liste de configurations à tester
    """
    base_config = {
        'pop_size': 100,
        'tournament_k': 4,
        'elitism': 4,
        'pc': 0.95,
        'pm': 0.25,
        'use_2opt': True,
        'two_opt_prob': 0.35,
        'time_limit': 30.0,  # Réduit à 30s
        'generations': 50000  # Augmenté car limité par temps
    }
    
    configurations = []
    
    # 1. Variation de la taille de population (plus d'options)
    for pop_size in [40, 60, 80, 100, 120, 140, 160, 180, 200]:
        config = base_config.copy()
        config['pop_size'] = pop_size
        config['name'] = f"PopSize_{pop_size}"
        configurations.append(config)
    
    # 2. Variation du tournament (plus d'options)
    for tournament_k in [2, 3, 4, 5, 6, 7, 8]:
        config = base_config.copy()
        config['tournament_k'] = tournament_k
        config['name'] = f"Tournament_{tournament_k}"
        configurations.append(config)
    
    # 3. Variation de l'élitisme (plus d'options)
    for elitism in [1, 2, 3, 4, 5, 6, 8, 10, 12, 15]:
        config = base_config.copy()
        config['elitism'] = elitism
        config['name'] = f"Elitism_{elitism}"
        configurations.append(config)
    
    # 4. Variation de la probabilité de crossover (plus d'options)
    for pc in [0.7, 0.75, 0.8, 0.85, 0.9, 0.92, 0.95, 0.97, 0.98, 0.99]:
        config = base_config.copy()
        config['pc'] = pc
        config['name'] = f"Crossover_{pc}"
        configurations.append(config)
    
    # 5. Variation de la probabilité de mutation (plus d'options)
    for pm in [0.05, 0.1, 0.15, 0.2, 0.22, 0.25, 0.27, 0.3, 0.35, 0.4]:
        config = base_config.copy()
        config['pm'] = pm
        config['name'] = f"Mutation_{pm}"
        configurations.append(config)
    
    # 6. Variation de la probabilité 2-opt (plus d'options)
    for two_opt_prob in [0.0, 0.1, 0.2, 0.3, 0.35, 0.4, 0.5, 0.6, 0.65, 0.7, 0.8]:
        config = base_config.copy()
        config['two_opt_prob'] = two_opt_prob
        config['name'] = f"TwoOpt_{two_opt_prob}"
        configurations.append(config)
    
    # 7. Test avec/sans 2-opt
    for use_2opt in [True, False]:
        config = base_config.copy()
        config['use_2opt'] = use_2opt
        config['name'] = f"Use2Opt_{use_2opt}"
        configurations.append(config)
    
    # 8. Combinaisons prometteuses (basées sur la littérature)
    promising_combinations = [
        {'pop_size': 80, 'tournament_k': 3, 'elitism': 2, 'pc': 0.9, 'pm': 0.3, 'two_opt_prob': 0.4, 'name': 'Combo_ExplorationHigh'},
        {'pop_size': 120, 'tournament_k': 5, 'elitism': 8, 'pc': 0.95, 'pm': 0.15, 'two_opt_prob': 0.6, 'name': 'Combo_ExploitationHigh'},
        {'pop_size': 150, 'tournament_k': 4, 'elitism': 6, 'pc': 0.92, 'pm': 0.22, 'two_opt_prob': 0.35, 'name': 'Combo_Balanced'},
        {'pop_size': 60, 'tournament_k': 2, 'elitism': 1, 'pc': 0.98, 'pm': 0.35, 'two_opt_prob': 0.2, 'name': 'Combo_DiversityMax'},
        {'pop_size': 200, 'tournament_k': 6, 'elitism': 12, 'pc': 0.9, 'pm': 0.1, 'two_opt_prob': 0.7, 'name': 'Combo_IntensiveSearch'},
    ]
    
    for combo in promising_combinations:
        config = base_config.copy()
        config.update(combo)
        configurations.append(config)
    
    return configurations


def generate_extended_parameter_variations():
    """
    Génère encore plus de variations avec des combinaisons spécifiques.
    
    Returns:
        Liste étendue de configurations à tester
    """
    base_config = {
        'pop_size': 100,
        'tournament_k': 4,
        'elitism': 4,
        'pc': 0.95,
        'pm': 0.25,
        'use_2opt': True,
        'two_opt_prob': 0.35,
        'time_limit': 30.0,  # Réduit à 30s
        'generations': 50000  # Augmenté car limité par temps
    }
    
    configurations = []
    
    # Variations de base
    configurations.extend(generate_parameter_variations())
    
    # Combinaisons croisées pour les paramètres les plus importants
    # Population vs Élitisme
    for pop_size in [80, 120, 160]:
        for elitism in [2, 6, 10]:
            config = base_config.copy()
            config['pop_size'] = pop_size
            config['elitism'] = elitism
            config['name'] = f"Pop{pop_size}_Elite{elitism}"
            configurations.append(config)
    
    # Crossover vs Mutation
    for pc in [0.85, 0.95, 0.98]:
        for pm in [0.15, 0.25, 0.35]:
            config = base_config.copy()
            config['pc'] = pc
            config['pm'] = pm
            config['name'] = f"Cross{pc}_Mut{pm}"
            configurations.append(config)
    
    # Tournament vs 2-opt
    for tournament_k in [3, 5, 7]:
        for two_opt_prob in [0.2, 0.5, 0.7]:
            config = base_config.copy()
            config['tournament_k'] = tournament_k
            config['two_opt_prob'] = two_opt_prob
            config['name'] = f"Tour{tournament_k}_2opt{two_opt_prob}"
            configurations.append(config)
    
    return configurations
def main():
    """Fonction principale pour les tests de paramètres."""
    instance_path = "data/instances/data.vrp"  # Chemin vers l'instance
    
    print("TEST SYSTÉMATIQUE DE PARAMÈTRES GA")
    print("=" * 50)
    print(f"Instance: {instance_path}")
    
    # Configuration du multi-threading
    print(f"\nMulti-threading: {os.cpu_count()} CPU cores détectés")
    max_workers_input = input(f"Threads à utiliser (Enter = auto): ").strip()
    max_workers = int(max_workers_input) if max_workers_input else None
    
    # Choix du mode de test
    print("\nMode de test:")
    print("1. Test rapide (5 configurations prédéfinies)")
    print("2. Test systématique (variations de chaque paramètre)")
    print("3. Test personnalisé")
    
    choice = input("Votre choix (1-3): ").strip()
    
    if choice == "1":
        # Configurations prédéfinies rapides
        configurations = [
            {
                'name': 'Configuration Standard',
                'pop_size': 100,
                'tournament_k': 4,
                'elitism': 4,
                'pc': 0.95,
                'pm': 0.25,
                'use_2opt': True,
                'two_opt_prob': 0.35,
                'time_limit': 30.0,  # Réduit à 30s
                'generations': 50000  # Augmenté car limité par temps
            },
            {
                'name': 'Population Large',
                'pop_size': 150,
                'tournament_k': 5,
                'elitism': 6,
                'pc': 0.9,
                'pm': 0.2,
                'use_2opt': True,
                'two_opt_prob': 0.5,
                'time_limit': 30.0,  # Réduit à 30s
                'generations': 50000
            },
            {
                'name': 'Exploration Intensive',
                'pop_size': 80,
                'tournament_k': 3,
                'elitism': 2,
                'pc': 0.98,
                'pm': 0.3,
                'use_2opt': True,
                'two_opt_prob': 0.2,
                'time_limit': 30.0,  # Réduit à 30s
                'generations': 50000
            },
            {
                'name': 'Sans 2-opt (Rapide)',
                'pop_size': 120,
                'tournament_k': 4,
                'elitism': 5,
                'pc': 0.95,
                'pm': 0.25,
                'use_2opt': False,
                'two_opt_prob': 0.0,
                'time_limit': 30.0,  # Réduit à 30s
                'generations': 50000
            },
            {
                'name': 'Élitisme Fort',
                'pop_size': 100,
                'tournament_k': 4,
                'elitism': 10,
                'pc': 0.9,
                'pm': 0.15,
                'use_2opt': True,
                'two_opt_prob': 0.6,
                'time_limit': 30.0,  # Réduit à 30s
                'generations': 50000
            }
        ]
        
    elif choice == "2":
        # Génération systématique de variations
        print("\nOptions de test systématique:")
        print("a. Standard (60+ configurations)")
        print("b. Étendu (100+ configurations)")
        print("c. Complet (150+ configurations)")
        
        sub_choice = input("Votre choix (a/b/c): ").strip().lower()
        
        if sub_choice == "a":
            configurations = generate_parameter_variations()
        elif sub_choice == "b":
            configurations = generate_extended_parameter_variations()
        elif sub_choice == "c":
            # Génération complète avec toutes les combinaisons importantes
            configurations = generate_extended_parameter_variations()
            # Ajout de configurations additionnelles
            base_config = {
                'pop_size': 100, 'tournament_k': 4, 'elitism': 4, 'pc': 0.95, 'pm': 0.25,
                'use_2opt': True, 'two_opt_prob': 0.35, 'time_limit': 30.0, 'generations': 50000
            }
            
            # Variations extrêmes pour explorer les limites
            extreme_configs = [
                {'pop_size': 20, 'name': 'Extreme_SmallPop'},
                {'pop_size': 300, 'name': 'Extreme_LargePop'},
                {'tournament_k': 1, 'name': 'Extreme_NoSelection'},
                {'tournament_k': 10, 'name': 'Extreme_HighSelection'},
                {'elitism': 0, 'name': 'Extreme_NoElitism'},
                {'elitism': 20, 'name': 'Extreme_HighElitism'},
                {'pc': 0.5, 'name': 'Extreme_LowCrossover'},
                {'pm': 0.5, 'name': 'Extreme_HighMutation'},
                {'two_opt_prob': 1.0, 'name': 'Extreme_Always2Opt'},
            ]
            
            for extreme in extreme_configs:
                config = base_config.copy()
                config.update(extreme)
                configurations.append(config)
        else:
            print("Choix invalide.")
            return
        
        print(f"\nNombre total de configurations: {len(configurations)}")
        print(f"Temps estimé: ~{len(configurations) * 3 * 30 / 60:.1f} minutes (30s par run)")
        
        confirm = input("Continuer? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Test annulé.")
            return
            
    elif choice == "3":
        print("Mode personnalisé non implémenté dans cette version.")
        return
    else:
        print("Choix invalide.")
        return
    
    # Test de chaque configuration
    results = []
    total_configs = len(configurations)
    
    for i, config in enumerate(configurations):
        print(f"\n{'='*60}")
        print(f"CONFIGURATION {i+1}/{total_configs}")
        print(f"{'='*60}")
        
        result = test_configuration(instance_path, config, num_runs=3, max_workers=max_workers)
        results.append(result)
    
    # Filtrage des résultats valides
    valid_results = [r for r in results if r is not None]
    
    if valid_results:
        # Tri par coût moyen
        valid_results.sort(key=lambda x: x['cost_mean'])
        
        # Sauvegarde des résultats
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"parameter_test_results_{timestamp}.txt"
        best_summary_filename = f"best_results_summary_{timestamp}.txt"
        
        save_results_to_file(valid_results, filename)
        save_best_results_summary(valid_results, best_summary_filename)
        
        # Affichage du résumé
        print(f"\n{'='*60}")
        print("RÉSUMÉ DES RÉSULTATS")
        print(f"{'='*60}")
        print(f"Configurations testées: {total_configs}")
        print(f"Résultats valides: {len(valid_results)}")
        
        if len(valid_results) >= 3:
            print(f"\nTOP 3 MEILLEURES CONFIGURATIONS:")
            for i, result in enumerate(valid_results[:3]):
                print(f"\n--- Rang {i+1} ---")
                print(f"Nom: {result['config_name']}")
                print(f"Coût moyen: {result['cost_mean']:.1f}")
                print(f"Meilleur coût: {result['cost_min']}")
                print(f"Écart-type: {result['cost_std']:.2f}")
        
        print(f"\nDonnées sauvegardées dans: {filename}")
        print("Utilisez 'plot_parameter_results.py' pour générer des graphiques.")
    else:
        print("Aucun résultat valide obtenu!")


if __name__ == "__main__":
    main()