# -*- coding: utf-8 -*-
"""
run_parameter_analysis.py
Script principal pour l'analyse complète des paramètres GA.

Permet de :
1. Tester les paramètres individuellement
2. Trouver les meilleures combinaisons
3. Visualiser les résultats graphiquement
"""

import os
import sys
from datetime import datetime

# Gestion des imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.optimization.ga_parameter_analyzer import GAParameterAnalyzer
from src.optimization.ga_visualizer import GAVisualizer
from src.core.solution_loader import find_solution_for_instance


def print_menu():
    """Affiche le menu principal."""
    print("\n" + "="*80)
    print("🧬 ANALYSE DES PARAMÈTRES DE L'ALGORITHME GÉNÉTIQUE 🧬".center(80))
    print("="*80)
    print("\n📋 MENU PRINCIPAL:")
    print("  1️⃣  - Tester les paramètres individuellement")
    print("  2️⃣  - Trouver les meilleures combinaisons")
    print("  3️⃣  - Visualiser les résultats (graphiques)")
    print("  4️⃣  - Générer un rapport complet")
    print("  5️⃣  - Afficher la configuration actuelle")
    print("  6️⃣  - Charger des résultats existants")
    print("  7️⃣  - Analyse complète (1+2+3+4)")
    print("  8️⃣  - Modifier le nombre de runs par test")
    print("  0️⃣  - Quitter")
    print("="*80)


def print_config(analyzer: GAParameterAnalyzer):
    """Affiche la configuration actuelle."""
    print("\n⚙️  CONFIGURATION ACTUELLE:")
    print(f"  Instance: {analyzer.instance.name}")
    print(f"  Clients: {analyzer.instance.dimension}")
    print(f"  Capacité véhicule: {analyzer.instance.capacity}")
    print(f"  Dépôt: index {analyzer.instance.depot_index}")
    print(f"  🔁 Répétitions par test (n_runs): {analyzer.n_runs}")
    print(f"     → Chaque configuration est testée {analyzer.n_runs} fois pour calculer la moyenne")
    
    if analyzer.target_optimum:
        print(f"\n  🎯 Solution de référence:")
        print(f"     Coût optimal: {analyzer.target_optimum}")
    
    # Afficher les paramètres par défaut
    print(f"\n  🔧 Paramètres par défaut (baseline):")
    for param, value in analyzer.default_params.items():
        print(f"     {param}: {value}")
    
    if analyzer.baseline_result:
        print(f"\n  📊 Baseline établie:")
        print(f"     Coût moyen: {analyzer.baseline_result.cost_mean:.2f}")
        print(f"     Écart-type: {analyzer.baseline_result.cost_std:.2f}")
        print(f"     Temps moyen: {analyzer.baseline_result.time_mean:.2f}s")
        
        # Calculer le gap par rapport à l'optimum
        if analyzer.target_optimum:
            gap = ((analyzer.baseline_result.cost_mean - analyzer.target_optimum) / 
                   analyzer.target_optimum) * 100
            print(f"     Gap vs optimal: {gap:+.2f}%")
    
    # Afficher le statut des tests
    if analyzer.individual_results:
        print(f"\n  ✅ Tests individuels: {len(analyzer.individual_results)} paramètres testés")
        total_configs = sum(len(results) for results in analyzer.individual_results.values())
        print(f"     Total configurations: {total_configs}")
        
        # Trouver le meilleur résultat
        best_cost = float('inf')
        best_param = None
        for param_name, results in analyzer.individual_results.items():
            if results[0].cost_mean < best_cost:
                best_cost = results[0].cost_mean
                best_param = (param_name, results[0].parameter_value)
        
        if best_param:
            print(f"     Meilleur résultat: {best_param[0]}={best_param[1]} → {best_cost:.1f}")
            if analyzer.target_optimum:
                best_gap = ((best_cost - analyzer.target_optimum) / analyzer.target_optimum) * 100
                print(f"     Gap vs optimal: {best_gap:+.2f}%")
    
    if analyzer.combination_results:
        print(f"\n  ✅ Tests de combinaisons: {len(analyzer.combination_results)} combinaisons testées")
        
        # Meilleure combinaison
        best_combo = analyzer.combination_results[0]
        print(f"     Meilleure combinaison: {best_combo.cost_mean:.1f}")
        if analyzer.target_optimum:
            combo_gap = ((best_combo.cost_mean - analyzer.target_optimum) / 
                        analyzer.target_optimum) * 100
            print(f"     Gap vs optimal: {combo_gap:+.2f}%")


def run_individual_tests(analyzer: GAParameterAnalyzer):
    """Lance les tests individuels des paramètres."""
    print("\n" + "="*80)
    print("🔬 TESTS INDIVIDUELS DES PARAMÈTRES".center(80))
    print("="*80)
    
    total_configs = sum(len(values) for values in analyzer.parameter_spaces.values())
    total_runs = total_configs * analyzer.n_runs
    
    print(f"\n📊 Configurations à tester: {total_configs}")
    print(f"🔁 Runs par configuration: {analyzer.n_runs}")
    print(f"📈 Total d'exécutions GA: {total_runs}")
    print(f"💡 Chaque configuration sera testée {analyzer.n_runs} fois pour obtenir une moyenne stable")
    
    confirm = input("\n⚠️  Cette opération peut prendre plusieurs minutes. Continuer ? (o/n): ")
    if confirm.lower() != 'o':
        print("❌ Opération annulée")
        return
    
    print("\n🚀 Lancement des tests individuels...")
    print(f"⏱️  Début: {datetime.now().strftime('%H:%M:%S')}\n")
    
    try:
        analyzer.test_individual_parameters()
        print(f"\n✅ Tests terminés à {datetime.now().strftime('%H:%M:%S')}")
        
        # Résumé avec gap vs optimal
        if analyzer.individual_results:
            print(f"\n📈 RÉSUMÉ DES TESTS:")
            if analyzer.target_optimum:
                print(f"   🎯 Objectif: {analyzer.target_optimum}")
            
            for param_name, results in analyzer.individual_results.items():
                best = results[0]
                improvement = ((analyzer.baseline_result.cost_mean - best.cost_mean) 
                              / analyzer.baseline_result.cost_mean) * 100
                
                gap_text = ""
                if analyzer.target_optimum:
                    gap = ((best.cost_mean - analyzer.target_optimum) / analyzer.target_optimum) * 100
                    gap_text = f", Gap vs optimal = {gap:+.2f}%"
                
                print(f"  {param_name}: Meilleure valeur = {best.parameter_value}, "
                      f"Coût = {best.cost_mean:.1f}, Amélioration = {improvement:+.2f}%{gap_text}")
    
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")


def run_combination_tests(analyzer: GAParameterAnalyzer):
    """Lance les tests de combinaisons."""
    print("\n" + "="*80)
    print("🎯 RECHERCHE DES MEILLEURES COMBINAISONS".center(80))
    print("="*80)
    
    if not analyzer.individual_results:
        print("\n⚠️  Vous devez d'abord effectuer les tests individuels (option 1)")
        return
    
    print("\n📊 Méthode: Grid Search sur les meilleures valeurs de chaque paramètre")
    print(f"🔁 Runs par combinaison: {analyzer.n_runs}")
    
    # Demander le nombre de combinaisons
    try:
        n_combos = input("\nNombre de combinaisons à tester (défaut=10, max=50): ")
        n_combos = int(n_combos) if n_combos else 10
        n_combos = min(max(1, n_combos), 50)
    except ValueError:
        n_combos = 10
    
    total_runs = n_combos * analyzer.n_runs
    print(f"\n📈 Total d'exécutions GA: {total_runs}")
    print(f"💡 Chaque combinaison sera testée {analyzer.n_runs} fois pour obtenir une moyenne stable")
    
    confirm = input(f"\n⚠️  Tester {n_combos} combinaisons ? (o/n): ")
    if confirm.lower() != 'o':
        print("❌ Opération annulée")
        return
    
    print(f"\n🚀 Lancement des tests de combinaisons...")
    print(f"⏱️  Début: {datetime.now().strftime('%H:%M:%S')}\n")
    
    try:
        analyzer.find_best_combinations(n_combinations=n_combos)
        print(f"\n✅ Tests terminés à {datetime.now().strftime('%H:%M:%S')}")
        
        # Afficher les meilleures avec gap
        if analyzer.combination_results:
            print(f"\n🏆 TOP 5 MEILLEURES COMBINAISONS:")
            if analyzer.target_optimum:
                print(f"   🎯 Objectif: {analyzer.target_optimum}\n")
            
            for i, combo in enumerate(analyzer.combination_results[:5], 1):
                gap_text = ""
                if analyzer.target_optimum:
                    gap = ((combo.cost_mean - analyzer.target_optimum) / analyzer.target_optimum) * 100
                    gap_text = f", Gap vs optimal: {gap:+.2f}%"
                
                print(f"  {i}. Coût moyen: {combo.cost_mean:.2f} "
                      f"(±{combo.cost_std:.2f}), "
                      f"Amélioration: {combo.improvement:+.2f}%{gap_text}")
                print(f"     Paramètres: {combo.parameters}")
    
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")


def visualize_results(analyzer: GAParameterAnalyzer):
    """Visualise les résultats."""
    print("\n" + "="*80)
    print("📊 VISUALISATION DES RÉSULTATS".center(80))
    print("="*80)
    
    if not analyzer.individual_results:
        print("\n⚠️  Aucun résultat à visualiser. Lancez d'abord les tests (option 1)")
        return
    
    visualizer = GAVisualizer(analyzer)
    
    print("\n📈 Types de visualisation disponibles:")
    print("  1 - Graphiques individuels par paramètre")
    print("  2 - Comparaison de l'impact des paramètres")
    print("  3 - Résultats des combinaisons")
    print("  4 - Tout afficher")
    
    choice = input("\nVotre choix (1-4): ")
    
    try:
        if choice == '1':
            visualizer.plot_individual_parameters()
        elif choice == '2':
            visualizer.plot_parameter_comparison()
        elif choice == '3':
            if not analyzer.combination_results:
                print("⚠️  Aucune combinaison testée. Lancez l'option 2 d'abord.")
            else:
                visualizer.plot_combination_results()
        elif choice == '4':
            visualizer.plot_individual_parameters()
            visualizer.plot_parameter_comparison()
            if analyzer.combination_results:
                visualizer.plot_combination_results()
        else:
            print("❌ Choix invalide")
    
    except Exception as e:
        print(f"❌ Erreur lors de la visualisation: {e}")


def generate_full_report(analyzer: GAParameterAnalyzer):
    """Génère un rapport complet."""
    print("\n" + "="*80)
    print("📑 GÉNÉRATION DU RAPPORT COMPLET".center(80))
    print("="*80)
    
    if not analyzer.individual_results:
        print("\n⚠️  Aucun résultat à inclure dans le rapport")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sauvegarder les résultats JSON
    results_dir = "results/parameter_analysis"
    os.makedirs(results_dir, exist_ok=True)
    json_path = os.path.join(results_dir, f"analysis_{timestamp}.json")
    
    print(f"\n💾 Sauvegarde des résultats JSON...")
    analyzer.save_results(json_path)
    
    # Créer les visualisations
    vis_dir = os.path.join(results_dir, f"visualizations_{timestamp}")
    visualizer = GAVisualizer(analyzer)
    
    print(f"\n📊 Génération des graphiques...")
    visualizer.create_summary_report(output_dir=vis_dir)
    
    print(f"\n✅ Rapport complet généré:")
    print(f"  📄 Données JSON: {json_path}")
    print(f"  📊 Graphiques: {vis_dir}")


def load_results(analyzer: GAParameterAnalyzer):
    """Charge des résultats existants."""
    print("\n" + "="*80)
    print("📂 CHARGEMENT DE RÉSULTATS EXISTANTS".center(80))
    print("="*80)
    
    results_dir = "results/parameter_analysis"
    if not os.path.exists(results_dir):
        print(f"\n❌ Répertoire {results_dir} introuvable")
        return
    
    # Lister les fichiers JSON
    json_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"\n⚠️  Aucun fichier de résultats trouvé dans {results_dir}")
        return
    
    print(f"\n📁 Fichiers disponibles:")
    for i, file in enumerate(json_files, 1):
        filepath = os.path.join(results_dir, file)
        size = os.path.getsize(filepath) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        print(f"  {i}. {file} ({size:.1f} KB) - {mtime.strftime('%Y-%m-%d %H:%M')}")
    
    try:
        choice = int(input(f"\nChoisir un fichier (1-{len(json_files)}): "))
        if 1 <= choice <= len(json_files):
            filepath = os.path.join(results_dir, json_files[choice-1])
            analyzer.load_results(filepath)
            print(f"✅ Résultats chargés avec succès")
        else:
            print("❌ Choix invalide")
    except (ValueError, Exception) as e:
        print(f"❌ Erreur: {e}")


def change_n_runs(analyzer: GAParameterAnalyzer):
    """Modifie le nombre de runs par test."""
    print("\n" + "="*80)
    print("🔁 CONFIGURATION DU NOMBRE DE RUNS".center(80))
    print("="*80)
    
    print(f"\n📊 Configuration actuelle: {analyzer.n_runs} runs par test")
    print("\n💡 Recommandations:")
    print("  • 3-5 runs : Tests rapides, moins précis")
    print("  • 10-15 runs : Bon équilibre (recommandé)")
    print("  • 20-30 runs : Très précis, plus long")
    
    try:
        new_n_runs = input(f"\nNouveau nombre de runs (1-50, actuel={analyzer.n_runs}): ")
        new_n_runs = int(new_n_runs)
        
        if 1 <= new_n_runs <= 50:
            analyzer.n_runs = new_n_runs
            print(f"\n✅ Nombre de runs modifié: {new_n_runs}")
            print(f"💡 Chaque configuration sera maintenant testée {new_n_runs} fois")
        else:
            print("❌ Valeur invalide (doit être entre 1 et 50)")
    except ValueError:
        print("❌ Entrée invalide")



def run_full_analysis(analyzer: GAParameterAnalyzer):
    """Lance une analyse complète."""
    print("\n" + "="*80)
    print("🚀 ANALYSE COMPLÈTE".center(80))
    print("="*80)
    
    print("\nCette opération va:")
    print("  1️⃣  Tester les paramètres individuellement")
    print("  2️⃣  Trouver les meilleures combinaisons")
    print("  3️⃣  Générer toutes les visualisations")
    print("  4️⃣  Créer un rapport complet")
    
    confirm = input("\n⚠️  Cela peut prendre 15-30 minutes. Continuer ? (o/n): ")
    if confirm.lower() != 'o':
        print("❌ Opération annulée")
        return
    
    print(f"\n🚀 DÉMARRAGE DE L'ANALYSE COMPLÈTE")
    print(f"⏱️  Début: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Étape 1: Tests individuels
    print("\n" + "─"*80)
    print("ÉTAPE 1/4: Tests individuels".center(80))
    print("─"*80)
    try:
        analyzer.test_individual_parameters()
        print("✅ Tests individuels terminés")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # Étape 2: Combinaisons
    print("\n" + "─"*80)
    print("ÉTAPE 2/4: Tests de combinaisons".center(80))
    print("─"*80)
    try:
        analyzer.find_best_combinations(n_combinations=20)
        print("✅ Tests de combinaisons terminés")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # Étape 3: Visualisations
    print("\n" + "─"*80)
    print("ÉTAPE 3/4: Génération des visualisations".center(80))
    print("─"*80)
    try:
        visualizer = GAVisualizer(analyzer)
        visualizer.plot_individual_parameters()
        visualizer.plot_parameter_comparison()
        if analyzer.combination_results:
            visualizer.plot_combination_results()
        print("✅ Visualisations générées")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Étape 4: Rapport
    print("\n" + "─"*80)
    print("ÉTAPE 4/4: Génération du rapport".center(80))
    print("─"*80)
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = "results/parameter_analysis"
        os.makedirs(results_dir, exist_ok=True)
        
        json_path = os.path.join(results_dir, f"full_analysis_{timestamp}.json")
        analyzer.save_results(json_path)
        
        vis_dir = os.path.join(results_dir, f"visualizations_{timestamp}")
        visualizer.create_summary_report(output_dir=vis_dir)
        
        print(f"✅ Rapport complet sauvegardé:")
        print(f"   📄 {json_path}")
        print(f"   📊 {vis_dir}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print(f"\n🎉 ANALYSE COMPLÈTE TERMINÉE à {datetime.now().strftime('%H:%M:%S')}")


def main():
    """Fonction principale."""
    # Chemin vers l'instance
    instance_path = "data/instances/data.vrp"
    
    if not os.path.exists(instance_path):
        print(f"❌ Instance introuvable: {instance_path}")
        print("Assurez-vous que le fichier existe.")
        return
    
    # Créer l'analyseur
    print("\n🔧 Initialisation de l'analyseur...")
    
    # Charger l'optimum de référence depuis la solution
    print("\n📊 Recherche de la solution de référence...")
    target_optimum = find_solution_for_instance(instance_path)
    
    # Nombre de runs par test (augmenté à 10 pour plus de stabilité)
    n_runs = 10
    
    try:
        analyzer = GAParameterAnalyzer(instance_path, target_optimum=target_optimum, n_runs=n_runs)
        print(f"✅ Analyseur initialisé avec l'instance: {analyzer.instance.name}")
        print(f"🔁 Runs par test configurés: {n_runs} (pour obtenir des moyennes stables)")
        
        if target_optimum:
            print(f"🎯 Objectif: Se rapprocher du coût optimal {target_optimum}")
        else:
            print("⚠️  Aucun optimum de référence disponible")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return
    
    # Boucle principale
    while True:
        print_menu()
        choice = input("\n👉 Votre choix: ")
        
        if choice == '0':
            print("\n👋 Au revoir !")
            break
        elif choice == '1':
            run_individual_tests(analyzer)
        elif choice == '2':
            run_combination_tests(analyzer)
        elif choice == '3':
            visualize_results(analyzer)
        elif choice == '4':
            generate_full_report(analyzer)
        elif choice == '5':
            print_config(analyzer)
        elif choice == '6':
            load_results(analyzer)
        elif choice == '7':
            run_full_analysis(analyzer)
        elif choice == '8':
            change_n_runs(analyzer)
        else:
            print("\n❌ Choix invalide. Veuillez choisir un numéro entre 0 et 8.")
        
        if choice != '0':
            input("\n⏸️  Appuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    main()
