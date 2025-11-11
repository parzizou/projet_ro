# -*- coding: utf-8 -*-
"""
ga_visualizer.py
Module de visualisation pour l'analyse des paramètres GA.

Génère des graphiques pour :
1. Impact de chaque paramètre individuellement
2. Comparaison des améliorations par paramètre
3. Visualisation des meilleures combinaisons
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Backend pour affichage interactif
from typing import Dict, List, Optional
import seaborn as sns

# Gestion des imports relatifs/absolus
try:
    from .ga_parameter_analyzer import GAParameterAnalyzer, ParameterTestResult, CombinationResult
except ImportError:
    # Import absolu si exécution directe
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.optimization.ga_parameter_analyzer import GAParameterAnalyzer, ParameterTestResult, CombinationResult

# Configuration matplotlib
plt.style.use('default')
sns.set_palette("husl")


class GAVisualizer:
    """Visualiseur pour les résultats d'analyse des paramètres GA."""
    
    def __init__(self, analyzer: GAParameterAnalyzer):
        """
        Initialise le visualiseur.
        
        Args:
            analyzer: Instance de GAParameterAnalyzer avec résultats
        """
        self.analyzer = analyzer
        
        if not analyzer.individual_results:
            print("⚠️  Aucun résultat à visualiser. Lancez d'abord l'analyse des paramètres.")
    
    def plot_individual_parameters(self, save_dir: Optional[str] = None):
        """
        Crée des graphiques pour chaque paramètre testé individuellement.
        
        Args:
            save_dir: Répertoire où sauvegarder les graphiques (None = affichage seulement)
        """
        if not self.analyzer.individual_results:
            print("❌ Aucun résultat à visualiser")
            return
        
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        
        baseline_cost = self.analyzer.baseline_result.cost_mean if self.analyzer.baseline_result else None
        optimal_cost = self.analyzer.target_optimum
        
        for param_name, results in self.analyzer.individual_results.items():
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Titre avec info optimum
            title = f'Analyse du paramètre: {param_name} - {self.analyzer.instance.name}'
            if optimal_cost:
                title += f' (Optimal: {optimal_cost})'
            fig.suptitle(title, fontsize=14, fontweight='bold')
            
            # Extraire les données
            values = [str(r.parameter_value) for r in results]
            costs = [r.cost_mean for r in results]
            stds = [r.cost_std for r in results]
            
            # Graphique 1: Coût moyen
            if optimal_cost:
                # Couleurs basées sur la distance à l'optimal (gap < 5% = bon)
                colors = []
                for c in costs:
                    gap = ((c - optimal_cost) / optimal_cost) * 100
                    if gap < 5.0:
                        colors.append('green')      # Bon
                    elif gap < 10.0:
                        colors.append('orange')     # Acceptable
                    else:
                        colors.append('red')        # À améliorer
            else:
                colors = ['green' if c < baseline_cost else 'red' for c in costs] if baseline_cost else 'blue'
            
            ax1.bar(values, costs, yerr=stds, capsize=5, color=colors, alpha=0.7, edgecolor='black')
            ax1.set_xlabel(param_name, fontsize=12)
            ax1.set_ylabel('Coût moyen', fontsize=12)
            ax1.set_title('Coût en fonction du paramètre')
            ax1.grid(axis='y', alpha=0.3)
            
            # Ajouter lignes de référence
            if optimal_cost:
                ax1.axhline(y=optimal_cost, color='green', linestyle='--', 
                           label=f'Optimal: {optimal_cost}', linewidth=2)
            if baseline_cost:
                ax1.axhline(y=baseline_cost, color='blue', linestyle='--', 
                           label=f'Baseline: {baseline_cost:.1f}', linewidth=2)
            ax1.legend()
            
            # Rotation des labels si nombreux
            if len(values) > 5:
                ax1.tick_params(axis='x', rotation=45)
            
            # Graphique 2: Gap par rapport à l'optimal
            if optimal_cost:
                gaps = [((c - optimal_cost) / optimal_cost) * 100 for c in costs]
                colors_gap = []
                for g in gaps:
                    if g < 5.0:
                        colors_gap.append('green')      # Bon
                    elif g < 10.0:
                        colors_gap.append('orange')     # Acceptable
                    else:
                        colors_gap.append('red')        # À améliorer
                
                ax2.bar(values, gaps, color=colors_gap, alpha=0.7, edgecolor='black')
                ax2.set_xlabel(param_name, fontsize=12)
                ax2.set_ylabel('Gap vs Optimal (%)', fontsize=12)
                ax2.set_title('Distance à la solution optimale')
                ax2.axhline(y=0, color='green', linestyle='-', linewidth=2, label='Optimal')
                ax2.axhline(y=5, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='Gap +5% (bon)')
                ax2.axhline(y=10, color='red', linestyle='--', linewidth=1, alpha=0.3, label='Gap +10%')
                ax2.legend()
            else:
                # Fallback: amélioration vs baseline si pas d'optimal
                improvements = [((baseline_cost - c) / baseline_cost) * 100 for c in costs]
                colors_imp = ['green' if i > 0 else 'red' for i in improvements]
                ax2.bar(values, improvements, color=colors_imp, alpha=0.7, edgecolor='black')
                ax2.set_xlabel(param_name, fontsize=12)
                ax2.set_ylabel('Amélioration (%)', fontsize=12)
                ax2.set_title('Amélioration vs Baseline')
                ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
            
            ax2.grid(axis='y', alpha=0.3)
            
            if len(values) > 5:
                ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            if save_dir:
                filepath = os.path.join(save_dir, f"param_{param_name}.png")
                plt.savefig(filepath, dpi=150, bbox_inches='tight')
                print(f"✅ Sauvegardé: {filepath}")
            
            plt.show()
    
    def plot_parameter_comparison(self, save_path: Optional[str] = None):
        """
        Crée un graphique comparant l'impact de tous les paramètres.
        
        Args:
            save_path: Chemin où sauvegarder le graphique (None = affichage seulement)
        """
        if not self.analyzer.individual_results or not self.analyzer.baseline_result:
            print("❌ Résultats insuffisants pour la comparaison")
            return
        
        # Calculer le gap vs optimal pour chaque paramètre
        param_gaps = {}
        param_best_values = {}
        param_best_costs = {}
        
        optimal_cost = self.analyzer.target_optimum
        
        for param_name, results in self.analyzer.individual_results.items():
            best_result = results[0]  # Déjà trié par coût
            param_best_costs[param_name] = best_result.cost_mean
            param_best_values[param_name] = best_result.parameter_value
            
            if optimal_cost:
                gap = ((best_result.cost_mean - optimal_cost) / optimal_cost) * 100
                param_gaps[param_name] = gap
            else:
                # Fallback: amélioration vs baseline
                baseline_cost = self.analyzer.baseline_result.cost_mean
                improvement = ((baseline_cost - best_result.cost_mean) / baseline_cost) * 100
                param_gaps[param_name] = -improvement  # Négatif = amélioration
        
        # Créer le graphique
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        title = f'Comparaison de l\'Impact des Paramètres - {self.analyzer.instance.name}'
        if optimal_cost:
            title += f' (Optimal: {optimal_cost})'
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Graphique 1: Gap vs optimal par paramètre
        params = list(param_gaps.keys())
        gaps = list(param_gaps.values())
        
        if optimal_cost:
            colors = []
            for g in gaps:
                if g < 5.0:
                    colors.append('green')      # Bon
                elif g < 10.0:
                    colors.append('orange')     # Acceptable
                else:
                    colors.append('red')        # À améliorer
            xlabel = 'Gap vs Optimal (%)'
            title1 = 'Distance à l\'optimal pour chaque paramètre'
        else:
            colors = ['green' if g < 0 else 'red' for g in gaps]
            xlabel = 'Amélioration vs Baseline (%)'
            title1 = 'Amélioration vs Baseline'
        
        ax1.barh(params, gaps, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_xlabel(xlabel, fontsize=12)
        ax1.set_title(title1)
        ax1.axvline(x=0, color='green', linestyle='-', linewidth=2)
        if optimal_cost:
            ax1.axvline(x=5, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='Gap +5% (bon)')
            ax1.axvline(x=10, color='red', linestyle='--', linewidth=1, alpha=0.3, label='Gap +10%')
            ax1.legend()
        ax1.grid(axis='x', alpha=0.3)
        
        # Graphique 2: Coûts avec meilleures valeurs
        costs = list(param_best_costs.values())
        colors2 = ['green' if c < self.analyzer.baseline_result.cost_mean else 'red' for c in costs]
        
        bars = ax2.barh(params, costs, color=colors2, alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Meilleur coût obtenu', fontsize=12)
        ax2.set_title('Meilleur résultat par paramètre')
        
        # Ajouter les valeurs des paramètres sur les barres
        for i, (param, cost) in enumerate(zip(params, costs)):
            value = param_best_values[param]
            ax2.text(cost + 20, i, f"{param}={value}", va='center', fontsize=9)
        
        # Lignes de référence
        if optimal_cost:
            ax2.axvline(x=optimal_cost, color='green', linestyle='--', 
                       label=f'Optimal: {optimal_cost}', linewidth=2)
        ax2.axvline(x=self.analyzer.baseline_result.cost_mean, color='blue', 
                   linestyle='--', label=f'Baseline: {self.analyzer.baseline_result.cost_mean:.1f}', 
                   linewidth=2)
        ax2.legend()
        ax2.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ Sauvegardé: {save_path}")
        
        plt.show()
    
    def plot_combination_results(self, top_n: int = 10, save_path: Optional[str] = None):
        """
        Visualise les résultats des meilleures combinaisons.
        
        Args:
            top_n: Nombre de meilleures combinaisons à afficher
            save_path: Chemin où sauvegarder le graphique
        """
        if not self.analyzer.combination_results:
            print("❌ Aucune combinaison testée")
            return
        
        # Prendre les top-N
        top_combos = self.analyzer.combination_results[:top_n]
        optimal_cost = self.analyzer.target_optimum
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        title = 'Analyse des Meilleures Combinaisons de Paramètres'
        if optimal_cost:
            title += f' (Optimal: {optimal_cost})'
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Graphique 1: Coûts des meilleures combinaisons
        combo_labels = [f"Combo {i+1}" for i in range(len(top_combos))]
        costs = [c.cost_mean for c in top_combos]
        stds = [c.cost_std for c in top_combos]
        
        # Calculer gaps si optimal disponible
        if optimal_cost:
            gaps = [((c - optimal_cost) / optimal_cost) * 100 for c in costs]
            # Gradient de couleur basé sur le gap (normalisé entre 0% et 15%)
            colors = plt.cm.RdYlGn_r([min(1.0, max(0.0, g / 15.0)) for g in gaps])
        else:
            colors = plt.cm.RdYlGn([0.3 + (i / len(top_combos)) * 0.7 for i in range(len(top_combos))])
        
        ax1.bar(combo_labels, costs, yerr=stds, capsize=5, color=colors, 
               alpha=0.8, edgecolor='black')
        ax1.set_xlabel('Combinaisons', fontsize=12)
        ax1.set_ylabel('Coût moyen', fontsize=12)
        ax1.set_title(f'Top {len(top_combos)} Meilleures Combinaisons')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y', alpha=0.3)
        
        # Lignes de référence
        if optimal_cost:
            ax1.axhline(y=optimal_cost, color='green', linestyle='--', 
                       label=f'Optimal: {optimal_cost}', linewidth=2)
        if self.analyzer.baseline_result:
            ax1.axhline(y=self.analyzer.baseline_result.cost_mean, color='blue', 
                       linestyle='--', label=f'Baseline: {self.analyzer.baseline_result.cost_mean:.1f}', 
                       linewidth=2)
        ax1.legend()
        
        # Graphique 2: Gap par rapport à l'optimal
        if optimal_cost:
            ax2.barh(combo_labels, gaps, color=colors, alpha=0.8, edgecolor='black')
            ax2.set_xlabel('Gap vs Optimal (%)', fontsize=12)
            ax2.set_title('Distance à la solution optimale')
            ax2.axvline(x=0, color='green', linestyle='-', linewidth=2, label='Optimal')
            ax2.axvline(x=5, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='Gap +5% (bon)')
            ax2.axvline(x=10, color='red', linestyle='--', linewidth=1, alpha=0.3, label='Gap +10%')
            ax2.legend()
            
            # Ajouter les valeurs sur les barres
            for i, gap in enumerate(gaps):
                ax2.text(gap + 0.2, i, f"{gap:.2f}%", va='center', fontsize=9)
        else:
            # Fallback: amélioration vs baseline
            improvements = [c.improvement for c in top_combos]
            ax2.barh(combo_labels, improvements, color=colors, alpha=0.8, edgecolor='black')
            ax2.set_xlabel('Amélioration (%)', fontsize=12)
            ax2.set_title('Amélioration par rapport à la Baseline')
            ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
            
            # Ajouter les valeurs sur les barres
            for i, improvement in enumerate(improvements):
                ax2.text(improvement + 0.1, i, f"{improvement:.2f}%", va='center', fontsize=9)
        
        ax2.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ Sauvegardé: {save_path}")
        
        plt.show()
    
    def create_summary_report(self, output_dir: str = "results/visualization"):
        """
        Crée un rapport complet avec tous les graphiques.
        
        Args:
            output_dir: Répertoire où sauvegarder les graphiques
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📊 Génération du rapport de visualisation...")
        print(f"Répertoire: {output_dir}")
        
        # 1. Graphiques individuels pour chaque paramètre
        print("\n1️⃣ Génération des graphiques individuels...")
        self.plot_individual_parameters(save_dir=output_dir)
        
        # 2. Graphique de comparaison
        print("\n2️⃣ Génération du graphique de comparaison...")
        comparison_path = os.path.join(output_dir, "parameter_comparison.png")
        self.plot_parameter_comparison(save_path=comparison_path)
        
        # 3. Graphique des combinaisons
        if self.analyzer.combination_results:
            print("\n3️⃣ Génération du graphique des combinaisons...")
            combination_path = os.path.join(output_dir, "combination_results.png")
            self.plot_combination_results(save_path=combination_path)
        
        print(f"\n✅ Rapport complet généré dans: {output_dir}")


if __name__ == "__main__":
    # Test avec des résultats simulés
    print("Pour utiliser ce module, créez d'abord un GAParameterAnalyzer et exécutez les tests.")
    print("Exemple:")
    print("  analyzer = GAParameterAnalyzer('data/instances/data.vrp')")
    print("  analyzer.test_individual_parameters()")
    print("  visualizer = GAVisualizer(analyzer)")
    print("  visualizer.plot_individual_parameters()")
