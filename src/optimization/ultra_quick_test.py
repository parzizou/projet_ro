# -*- coding: utf-8 -*-
"""
ultra_quick_test.py
Test ultra-rapide pour validation préliminaire des paramètres (15s par run).
"""

from __future__ import annotations
import time
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.cvrp_data import load_cvrp_instance
from src.core.ga import genetic_algorithm
from src.core.solution import verify_solution


def save_ultra_quick_results(results: list, filename: str = None):
    """
    Sauvegarde les résultats ultra-rapides dans un fichier texte.
    
    Args:
        results: Liste des résultats de tests
        filename: Nom du fichier (généré automatiquement si None)
    """
    if not results:
        print("Aucun résultat à sauvegarder.")
        return
    
    if filename is None:
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"ultra_quick_results_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        from datetime import datetime
        f.write(f"# Résultats de tests ultra-rapides - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# Temps par run: 15 secondes, 2 runs par configuration\n")
        f.write("# Format: config_name|param:value|avg_cost|min_cost|all_costs\n")
        f.write("#\n")
        
        # Tri par coût moyen croissant
        sorted_results = sorted(results, key=lambda x: x['avg_cost'])
        
        for result in sorted_results:
            line_parts = [result['name']]
            
            # Ajout des paramètres modifiés
            for param, value in result['config'].items():
                if param != 'name':
                    line_parts.append(f"{param}:{value}")
            
            # Ajout des métriques
            line_parts.extend([
                f"avg_cost:{result['avg_cost']:.1f}",
                f"min_cost:{result['min_cost']}",
                f"all_costs:[{','.join(map(str, result['costs']))}]"
            ])
            
            f.write("|".join(line_parts) + "\n")
    
    print(f"\nRésultats ultra-rapides sauvegardés dans: {filename}")
    return filename


def save_ultra_quick_summary(results: list, filename: str = None):
    """
    Sauvegarde un résumé analysé des résultats ultra-rapides.
    
    Args:
        results: Liste des résultats de tests
        filename: Nom du fichier (généré automatiquement si None)
    """
    if not results:
        print("Aucun résultat à analyser.")
        return
    
    if filename is None:
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"ultra_quick_summary_{timestamp}.txt"
    
    # Tri par coût moyen
    sorted_results = sorted(results, key=lambda x: x['avg_cost'])
    
    with open(filename, 'w', encoding='utf-8') as f:
        from datetime import datetime
        f.write(f"# RÉSUMÉ ULTRA-RAPIDE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# Tests de 15 secondes pour validation rapide des tendances\n")
        f.write("#\n")
        f.write("# CLASSEMENT PAR PERFORMANCE\n")
        f.write("#" + "="*60 + "\n\n")
        
        for i, result in enumerate(sorted_results, 1):
            f.write(f"RANG {i:2d}\n")
            f.write(f"Configuration: {result['name']}\n")
            f.write(f"Coût moyen:    {result['avg_cost']:.1f}\n")
            f.write(f"Meilleur coût: {result['min_cost']}\n")
            f.write(f"Tous les coûts: {result['costs']}\n")
            f.write("Paramètres modifiés:\n")
            
            for param, value in result['config'].items():
                if param != 'name':
                    f.write(f"  {param:<15}: {value}\n")
            
            f.write("-" * 50 + "\n\n")
        
        # Analyse par paramètre
        f.write("ANALYSE PAR PARAMÈTRE\n")
        f.write("=" * 40 + "\n\n")
        
        parameter_analysis = {}
        for result in sorted_results:
            for param, value in result['config'].items():
                if param != 'name':
                    if param not in parameter_analysis:
                        parameter_analysis[param] = []
                    parameter_analysis[param].append((value, result['avg_cost']))
        
        for param, values in parameter_analysis.items():
            if len(values) > 1:
                sorted_values = sorted(values, key=lambda x: x[1])
                best_val, best_cost = sorted_values[0]
                worst_val, worst_cost = sorted_values[-1]
                improvement = (worst_cost - best_cost) / worst_cost * 100
                
                f.write(f"{param.upper()}:\n")
                f.write(f"  Meilleure valeur: {best_val} (coût: {best_cost:.1f})\n")
                f.write(f"  Pire valeur: {worst_val} (coût: {worst_cost:.1f})\n")
                f.write(f"  Amélioration: {improvement:.1f}%\n\n")
        
        # Recommandations
        best_result = sorted_results[0]
        f.write("RECOMMANDATIONS ULTRA-RAPIDES\n")
        f.write("=" * 40 + "\n")
        f.write(f"Meilleure configuration testée: {best_result['name']}\n")
        f.write(f"Coût obtenu: {best_result['avg_cost']:.1f}\n")
        f.write("Paramètres recommandés pour tests approfondis:\n")
        for param, value in best_result['config'].items():
            if param != 'name':
                f.write(f"  {param} = {value}\n")
        
        f.write(f"\nNote: Résultats basés sur des tests de 15s seulement.\n")
        f.write("Pour validation définitive, utilisez quick_parameter_test.py\n")
    
    print(f"Résumé ultra-rapide sauvegardé dans: {filename}")
    return filename


def ultra_quick_parameter_test():
    """Test ultra-rapide avec des paramètres représentatifs."""
    instance_path = "data.vrp"
    
    print("TEST ULTRA-RAPIDE DE PARAMÈTRES GA")
    print("=" * 50)
    print("Temps par run: 15 secondes")
    print("Objectif: Validation rapide des tendances")
    
    # Configurations représentatives pour test rapide
    quick_configs = [
        # Population
        {'pop_size': 60, 'name': 'Pop_Small'},
        {'pop_size': 100, 'name': 'Pop_Medium'},
        {'pop_size': 150, 'name': 'Pop_Large'},
        
        # Tournament
        {'tournament_k': 2, 'name': 'Tournament_Low'},
        {'tournament_k': 4, 'name': 'Tournament_Medium'},
        {'tournament_k': 6, 'name': 'Tournament_High'},
        
        # Élitisme
        {'elitism': 2, 'name': 'Elitism_Low'},
        {'elitism': 6, 'name': 'Elitism_Medium'},
        {'elitism': 12, 'name': 'Elitism_High'},
        
        # Crossover
        {'pc': 0.8, 'name': 'Crossover_Low'},
        {'pc': 0.95, 'name': 'Crossover_High'},
        
        # Mutation
        {'pm': 0.15, 'name': 'Mutation_Low'},
        {'pm': 0.35, 'name': 'Mutation_High'},
        
        # 2-opt
        {'two_opt_prob': 0.2, 'name': '2opt_Low'},
        {'two_opt_prob': 0.6, 'name': '2opt_High'},
        {'use_2opt': False, 'name': 'No_2opt'},
    ]
    
    base_config = {
        'pop_size': 100,
        'tournament_k': 4,
        'elitism': 4,
        'pc': 0.95,
        'pm': 0.25,
        'use_2opt': True,
        'two_opt_prob': 0.35,
        'time_limit': 15.0,  # Ultra-rapide: 15s
        'generations': 50000  # Limité par temps
    }
    
    # Chargement de l'instance
    instance = load_cvrp_instance(instance_path)
    
    results = []
    total_configs = len(quick_configs)
    
    print(f"\nTest de {total_configs} configurations...")
    
    for i, test_config in enumerate(quick_configs):
        print(f"\n--- Config {i+1}/{total_configs}: {test_config['name']} ---")
        
        # Fusion avec config de base
        config = base_config.copy()
        config.update({k: v for k, v in test_config.items() if k != 'name'})
        
        costs = []
        
        # 2 runs seulement pour le test ultra-rapide
        for run in range(2):
            print(f"Run {run+1}/2...", end=" ")
            
            start_time = time.time()
            
            best = genetic_algorithm(
                inst=instance,
                pop_size=config['pop_size'],
                generations=config['generations'],
                tournament_k=config['tournament_k'],
                elitism=config['elitism'],
                pc=config['pc'],
                pm=config['pm'],
                seed=42 + run,
                use_2opt=config['use_2opt'],
                verbose=False,
                two_opt_prob=config['two_opt_prob'],
                time_limit_sec=config['time_limit']
            )
            
            exec_time = time.time() - start_time
            
            is_valid, _ = verify_solution(best.routes, instance)
            
            if is_valid:
                costs.append(best.cost)
                print(f"Coût: {best.cost}, Temps: {exec_time:.1f}s")
            else:
                print("INVALIDE!")
        
        if costs:
            avg_cost = sum(costs) / len(costs)
            min_cost = min(costs)
            results.append({
                'name': test_config['name'],
                'config': test_config,
                'avg_cost': avg_cost,
                'min_cost': min_cost,
                'costs': costs
            })
            print(f"  → Coût moyen: {avg_cost:.1f}, Meilleur: {min_cost}")
        else:
            print("  → Aucun résultat valide")
    
    # Analyse des résultats
    if results:
        print(f"\n{'='*60}")
        print("RÉSULTATS ULTRA-RAPIDES")
        print(f"{'='*60}")
        
        # Tri par coût moyen
        results.sort(key=lambda x: x['avg_cost'])
        
        print("\nCLASSEMENT (par coût moyen):")
        for i, result in enumerate(results, 1):
            print(f"{i:2d}. {result['name']:<20} | Coût: {result['avg_cost']:7.1f} | Meilleur: {result['min_cost']}")
        
        # Analyse par type de paramètre
        parameter_analysis = {}
        
        for result in results:
            for param, value in result['config'].items():
                if param != 'name':
                    if param not in parameter_analysis:
                        parameter_analysis[param] = []
                    parameter_analysis[param].append((value, result['avg_cost']))
        
        print(f"\nANALYSE PAR PARAMÈTRE:")
        for param, values in parameter_analysis.items():
            if len(values) > 1:
                sorted_values = sorted(values, key=lambda x: x[1])
                best_val, best_cost = sorted_values[0]
                worst_val, worst_cost = sorted_values[-1]
                improvement = (worst_cost - best_cost) / worst_cost * 100
                
                print(f"\n{param}:")
                print(f"  Meilleure valeur: {best_val} (coût: {best_cost:.1f})")
                print(f"  Pire valeur: {worst_val} (coût: {worst_cost:.1f})")
                print(f"  Amélioration: {improvement:.1f}%")
        
        # Recommandations rapides
        best_result = results[0]
        print(f"\nRECOMMENDATION RAPIDE:")
        print(f"Configuration: {best_result['name']}")
        print(f"Coût obtenu: {best_result['avg_cost']:.1f}")
        print("Paramètres modifiés:")
        for param, value in best_result['config'].items():
            if param != 'name':
                print(f"  {param}: {value}")
        
        # Sauvegarde des résultats
        data_file = save_ultra_quick_results(results)
        summary_file = save_ultra_quick_summary(results)
        
        print(f"\nFichiers générés:")
        print(f"- Données: {data_file}")
        print(f"- Résumé: {summary_file}")
        
        print(f"\nNote: Ces résultats sont basés sur des tests de 15s seulement.")
        print("Pour une analyse complète, utilisez 'quick_parameter_test.py'.")
    
    else:
        print("Aucun résultat valide obtenu.")


def save_ultra_quick_summary(results: list, filename: str = None):
    """
    Sauvegarde un résumé détaillé des résultats ultra-rapides.
    
    Args:
        results: Liste des résultats triés par performance
        filename: Nom du fichier de résumé
    """
    if not results:
        return
    
    if filename is None:
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"ultra_quick_summary_{timestamp}.txt"
    
    # Tri par coût moyen
    sorted_results = sorted(results, key=lambda x: x['avg_cost'])
    
    with open(filename, 'w', encoding='utf-8') as f:
        from datetime import datetime
        f.write(f"# RÉSUMÉ ULTRA-RAPIDE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# Tests de 15 secondes pour validation rapide des tendances\n")
        f.write("#\n")
        f.write("# CLASSEMENT PAR PERFORMANCE\n")
        f.write("#" + "="*60 + "\n\n")
        
        for i, result in enumerate(sorted_results, 1):
            f.write(f"RANG {i:2d}\n")
            f.write(f"Configuration: {result['name']}\n")
            f.write(f"Coût moyen:    {result['avg_cost']:.1f}\n")
            f.write(f"Meilleur coût: {result['min_cost']}\n")
            f.write(f"Tous les coûts: {result['costs']}\n")
            f.write("Paramètres modifiés:\n")
            
            for param, value in result['config'].items():
                if param != 'name':
                    f.write(f"  {param:<15}: {value}\n")
            
            f.write("-" * 50 + "\n\n")
        
        # Analyse par paramètre
        f.write("ANALYSE PAR PARAMÈTRE\n")
        f.write("=" * 40 + "\n\n")
        
        parameter_analysis = {}
        for result in sorted_results:
            for param, value in result['config'].items():
                if param != 'name':
                    if param not in parameter_analysis:
                        parameter_analysis[param] = []
                    parameter_analysis[param].append((value, result['avg_cost']))
        
        for param, values in parameter_analysis.items():
            if len(values) > 1:
                sorted_values = sorted(values, key=lambda x: x[1])
                best_val, best_cost = sorted_values[0]
                worst_val, worst_cost = sorted_values[-1]
                improvement = (worst_cost - best_cost) / worst_cost * 100
                
                f.write(f"{param.upper()}:\n")
                f.write(f"  Meilleure valeur: {best_val} (coût: {best_cost:.1f})\n")
                f.write(f"  Pire valeur: {worst_val} (coût: {worst_cost:.1f})\n")
                f.write(f"  Amélioration: {improvement:.1f}%\n\n")
        
        # Recommandations
        best_result = sorted_results[0]
        f.write("RECOMMANDATIONS ULTRA-RAPIDES\n")
        f.write("=" * 40 + "\n")
        f.write(f"Meilleure configuration testée: {best_result['name']}\n")
        f.write(f"Coût obtenu: {best_result['avg_cost']:.1f}\n")
        f.write("Paramètres recommandés pour tests approfondis:\n")
        for param, value in best_result['config'].items():
            if param != 'name':
                f.write(f"  {param} = {value}\n")
        
        f.write(f"\nNote: Résultats basés sur des tests de 15s seulement.\n")
        f.write("Pour validation définitive, utilisez quick_parameter_test.py\n")
    
    print(f"Résumé ultra-rapide sauvegardé dans: {filename}")
    return filename


def ultra_quick_parameter_test():
    """Test ultra-rapide avec des paramètres représentatifs."""
    instance_path = "data.vrp"
    
    print("TEST ULTRA-RAPIDE DE PARAMÈTRES GA")
    print("=" * 50)
    print("Temps par run: 15 secondes")
    print("Objectif: Validation rapide des tendances")
    
    # Configurations représentatives pour test rapide
    quick_configs = [
        # Population
        {'pop_size': 60, 'name': 'Pop_Small'},
        {'pop_size': 100, 'name': 'Pop_Medium'},
        {'pop_size': 150, 'name': 'Pop_Large'},
        
        # Tournament
        {'tournament_k': 2, 'name': 'Tournament_Low'},
        {'tournament_k': 4, 'name': 'Tournament_Medium'},
        {'tournament_k': 6, 'name': 'Tournament_High'},
        
        # Élitisme
        {'elitism': 2, 'name': 'Elitism_Low'},
        {'elitism': 6, 'name': 'Elitism_Medium'},
        {'elitism': 12, 'name': 'Elitism_High'},
        
        # Crossover
        {'pc': 0.8, 'name': 'Crossover_Low'},
        {'pc': 0.95, 'name': 'Crossover_High'},
        
        # Mutation
        {'pm': 0.15, 'name': 'Mutation_Low'},
        {'pm': 0.35, 'name': 'Mutation_High'},
        
        # 2-opt
        {'two_opt_prob': 0.2, 'name': '2opt_Low'},
        {'two_opt_prob': 0.6, 'name': '2opt_High'},
        {'use_2opt': False, 'name': 'No_2opt'},
    ]
    
    base_config = {
        'pop_size': 100,
        'tournament_k': 4,
        'elitism': 4,
        'pc': 0.95,
        'pm': 0.25,
        'use_2opt': True,
        'two_opt_prob': 0.35,
        'time_limit': 15.0,  # Ultra-rapide: 15s
        'generations': 50000  # Limité par temps
    }
    
    # Chargement de l'instance
    instance = load_cvrp_instance(instance_path)
    
    results = []
    total_configs = len(quick_configs)
    
    print(f"\nTest de {total_configs} configurations...")
    
    for i, test_config in enumerate(quick_configs):
        print(f"\n--- Config {i+1}/{total_configs}: {test_config['name']} ---")
        
        # Fusion avec config de base
        config = base_config.copy()
        config.update({k: v for k, v in test_config.items() if k != 'name'})
        
        costs = []
        
        # 2 runs seulement pour le test ultra-rapide
        for run in range(2):
            print(f"Run {run+1}/2...", end=" ")
            
            start_time = time.time()
            
            best = genetic_algorithm(
                inst=instance,
                pop_size=config['pop_size'],
                generations=config['generations'],
                tournament_k=config['tournament_k'],
                elitism=config['elitism'],
                pc=config['pc'],
                pm=config['pm'],
                seed=42 + run,
                use_2opt=config['use_2opt'],
                verbose=False,
                two_opt_prob=config['two_opt_prob'],
                time_limit_sec=config['time_limit']
            )
            
            exec_time = time.time() - start_time
            
            is_valid, _ = verify_solution(best.routes, instance)
            
            if is_valid:
                costs.append(best.cost)
                print(f"Coût: {best.cost}, Temps: {exec_time:.1f}s")
            else:
                print("INVALIDE!")
        
        if costs:
            avg_cost = sum(costs) / len(costs)
            min_cost = min(costs)
            results.append({
                'name': test_config['name'],
                'config': test_config,
                'avg_cost': avg_cost,
                'min_cost': min_cost,
                'costs': costs
            })
            print(f"  → Coût moyen: {avg_cost:.1f}, Meilleur: {min_cost}")
        else:
            print("  → Aucun résultat valide")
    
    # Analyse des résultats
    if results:
        print(f"\n{'='*60}")
        print("RÉSULTATS ULTRA-RAPIDES")
        print(f"{'='*60}")
        
        # Tri par coût moyen
        results.sort(key=lambda x: x['avg_cost'])
        
        print("\nCLASSEMENT (par coût moyen):")
        for i, result in enumerate(results, 1):
            print(f"{i:2d}. {result['name']:<20} | Coût: {result['avg_cost']:7.1f} | Meilleur: {result['min_cost']}")
        
        # Analyse par type de paramètre
        parameter_analysis = {}
        
        for result in results:
            for param, value in result['config'].items():
                if param != 'name':
                    if param not in parameter_analysis:
                        parameter_analysis[param] = []
                    parameter_analysis[param].append((value, result['avg_cost']))
        
        print(f"\nANALYSE PAR PARAMÈTRE:")
        for param, values in parameter_analysis.items():
            if len(values) > 1:
                sorted_values = sorted(values, key=lambda x: x[1])
                best_val, best_cost = sorted_values[0]
                worst_val, worst_cost = sorted_values[-1]
                improvement = (worst_cost - best_cost) / worst_cost * 100
                
                print(f"\n{param}:")
                print(f"  Meilleure valeur: {best_val} (coût: {best_cost:.1f})")
                print(f"  Pire valeur: {worst_val} (coût: {worst_cost:.1f})")
                print(f"  Amélioration: {improvement:.1f}%")
        
        # Recommandations rapides
        best_result = results[0]
        print(f"\nRECOMMENDATION RAPIDE:")
        print(f"Configuration: {best_result['name']}")
        print(f"Coût obtenu: {best_result['avg_cost']:.1f}")
        print("Paramètres modifiés:")
        for param, value in best_result['config'].items():
            if param != 'name':
                print(f"  {param}: {value}")
        
        # Sauvegarde des résultats
        data_file = save_ultra_quick_results(results)
        summary_file = save_ultra_quick_summary(results)
        
        print(f"\nFichiers générés:")
        print(f"- Données: {data_file}")
        print(f"- Résumé: {summary_file}")
        
        print(f"\nNote: Ces résultats sont basés sur des tests de 15s seulement.")
        print("Pour une analyse complète, utilisez 'quick_parameter_test.py'.")
    
    else:
        print("Aucun résultat valide obtenu.")


def main():
    """Fonction principale."""
    print("VALIDATION ULTRA-RAPIDE DES PARAMÈTRES")
    print("Durée totale estimée: ~8-10 minutes")
    print("Objectif: Identifier rapidement les tendances prometteuses")
    
    confirm = input("\nLancer le test ultra-rapide? (y/n): ").strip().lower()
    if confirm == 'y':
        start_time = time.time()
        ultra_quick_parameter_test()
        total_time = time.time() - start_time
        print(f"\nTest terminé en {total_time/60:.1f} minutes")
    else:
        print("Test annulé.")


if __name__ == "__main__":
    main()