# -*- coding: utf-8 -*-
"""
test_visualizations_with_gap.py
Script de test pour vérifier les visualisations avec gap vs optimal.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.optimization.ga_parameter_analyzer import GAParameterAnalyzer, ParameterTestResult, CombinationResult

def create_mock_results():
    """Crée des résultats simulés pour tester les visualisations."""
    
    # Créer un analyseur
    analyzer = GAParameterAnalyzer(
        'data/instances/data.vrp',
        target_optimum=22901,  # Optimal connu
        n_runs=5
    )
    
    # Simuler une baseline
    analyzer.baseline_result = ParameterTestResult(
        parameter_name="baseline",
        parameter_value="default",
        cost_mean=23316.0,
        cost_std=150.0,
        cost_min=23100,
        cost_max=23500,
        time_mean=30.0,
        gap_mean=1.81
    )
    
    # Simuler des résultats individuels pour quelques paramètres
    print("📊 Création de résultats simulés avec gaps vs optimal...")
    
    # pop_size
    analyzer.individual_results['pop_size'] = [
        ParameterTestResult("pop_size", 60, 23050.0, 120.0, 22900, 23200, 28.0, 0.65),
        ParameterTestResult("pop_size", 80, 23100.0, 130.0, 22950, 23250, 29.0, 0.87),
        ParameterTestResult("pop_size", 100, 23316.0, 150.0, 23100, 23500, 30.0, 1.81),
        ParameterTestResult("pop_size", 120, 23400.0, 160.0, 23200, 23600, 32.0, 2.18),
    ]
    
    # tournament_k
    analyzer.individual_results['tournament_k'] = [
        ParameterTestResult("tournament_k", 6, 23000.0, 110.0, 22850, 23150, 29.0, 0.43),
        ParameterTestResult("tournament_k", 5, 23080.0, 125.0, 22920, 23240, 29.5, 0.78),
        ParameterTestResult("tournament_k", 3, 23316.0, 150.0, 23100, 23500, 30.0, 1.81),
        ParameterTestResult("tournament_k", 7, 23350.0, 155.0, 23150, 23550, 30.5, 1.96),
    ]
    
    # pm
    analyzer.individual_results['pm'] = [
        ParameterTestResult("pm", 0.06, 22980.0, 105.0, 22800, 23120, 29.0, 0.35),
        ParameterTestResult("pm", 0.05, 23020.0, 115.0, 22850, 23180, 29.2, 0.52),
        ParameterTestResult("pm", 0.02, 23316.0, 150.0, 23100, 23500, 30.0, 1.81),
        ParameterTestResult("pm", 0.01, 23450.0, 165.0, 23250, 23650, 30.5, 2.40),
    ]
    
    # two_opt_prob
    analyzer.individual_results['two_opt_prob'] = [
        ParameterTestResult("two_opt_prob", 0.75, 22950.0, 100.0, 22780, 23080, 31.0, 0.21),
        ParameterTestResult("two_opt_prob", 0.65, 23050.0, 120.0, 22900, 23200, 30.5, 0.65),
        ParameterTestResult("two_opt_prob", 0.5, 23316.0, 150.0, 23100, 23500, 30.0, 1.81),
        ParameterTestResult("two_opt_prob", 0.35, 23550.0, 175.0, 23350, 23750, 29.0, 2.83),
    ]
    
    # Simuler quelques combinaisons
    analyzer.combination_results = [
        CombinationResult(
            parameters={'pop_size': 60, 'tournament_k': 6, 'pm': 0.06, 'two_opt_prob': 0.75},
            cost_mean=22920.0,
            cost_std=95.0,
            cost_min=22750,
            cost_max=23050,
            improvement=1.70,
            gap_mean=0.08
        ),
        CombinationResult(
            parameters={'pop_size': 60, 'tournament_k': 5, 'pm': 0.06, 'two_opt_prob': 0.75},
            cost_mean=22970.0,
            cost_std=100.0,
            cost_min=22800,
            cost_max=23100,
            improvement=1.48,
            gap_mean=0.30
        ),
        CombinationResult(
            parameters={'pop_size': 80, 'tournament_k': 6, 'pm': 0.05, 'two_opt_prob': 0.75},
            cost_mean=23010.0,
            cost_std=110.0,
            cost_min=22850,
            cost_max=23150,
            improvement=1.31,
            gap_mean=0.48
        ),
        CombinationResult(
            parameters={'pop_size': 60, 'tournament_k': 6, 'pm': 0.05, 'two_opt_prob': 0.65},
            cost_mean=23080.0,
            cost_std=120.0,
            cost_min=22900,
            cost_max=23250,
            improvement=1.01,
            gap_mean=0.78
        ),
        CombinationResult(
            parameters={'pop_size': 100, 'tournament_k': 3, 'pm': 0.02, 'two_opt_prob': 0.5},
            cost_mean=23316.0,
            cost_std=150.0,
            cost_min=23100,
            cost_max=23500,
            improvement=0.0,
            gap_mean=1.81
        ),
    ]
    
    print(f"✅ Baseline: {analyzer.baseline_result.cost_mean:.1f} (Gap: +{analyzer.baseline_result.gap_mean:.2f}%)")
    print(f"✅ Meilleur résultat individuel: 22950 (Gap: +0.21%)")
    print(f"✅ Meilleure combinaison: 22920 (Gap: +0.08%)")
    print(f"🎯 Optimal: {analyzer.target_optimum}")
    
    return analyzer


def main():
    """Test des visualisations."""
    print("\n" + "="*80)
    print("🎨 TEST DES VISUALISATIONS AVEC GAP VS OPTIMAL".center(80))
    print("="*80)
    
    # Créer des résultats simulés
    analyzer = create_mock_results()
    
    # Créer le visualiseur
    from src.optimization.ga_visualizer import GAVisualizer
    visualizer = GAVisualizer(analyzer)
    
    print("\n📊 Génération des graphiques avec gap vs optimal...")
    print("   Les graphiques vont s'afficher. Fermez-les pour continuer.\n")
    
    # Test 1: Graphiques individuels
    print("1️⃣ Graphiques individuels (4 paramètres)")
    print("   → Graphique de gauche: Coût avec ligne optimal (vert) et baseline (bleu)")
    print("   → Graphique de droite: Gap vs Optimal en %")
    print("   → Couleurs: Vert (gap<5%), Orange (5-10%), Rouge (>10%)\n")
    
    input("   Appuyez sur Entrée pour afficher les graphiques individuels...")
    visualizer.plot_individual_parameters()
    
    # Test 2: Comparaison des paramètres
    print("\n2️⃣ Comparaison globale des paramètres")
    print("   → Graphique de gauche: Gap vs optimal pour chaque paramètre")
    print("   → Graphique de droite: Meilleurs coûts avec valeurs optimales")
    print("   → Lignes: Verte (optimal), Orange (+5%), Rouge (+10%)\n")
    
    input("   Appuyez sur Entrée pour afficher la comparaison...")
    visualizer.plot_parameter_comparison()
    
    # Test 3: Résultats des combinaisons
    print("\n3️⃣ Meilleures combinaisons")
    print("   → Graphique de gauche: Coûts des top 5 combinaisons")
    print("   → Graphique de droite: Gap vs optimal pour chaque combinaison")
    print("   → La meilleure combinaison atteint Gap = +0.08%\n")
    
    input("   Appuyez sur Entrée pour afficher les combinaisons...")
    visualizer.plot_combination_results(top_n=5)
    
    print("\n" + "="*80)
    print("✅ TEST TERMINÉ".center(80))
    print("="*80)
    print("\n💡 Les visualisations affichent maintenant:")
    print("   • Gap par rapport à l'optimal (22901) au lieu de l'amélioration vs baseline")
    print("   • Ligne verte pour l'optimal sur tous les graphiques")
    print("   • Couleurs basées sur la distance à l'optimal")
    print("   • Code couleur: Vert (<5% = bon), Orange (5-10% = acceptable), Rouge (>10%)")
    print("\n🎯 Objectif: Trouver les paramètres qui donnent un Gap < 5% (coût < 24046) !")


if __name__ == "__main__":
    main()
