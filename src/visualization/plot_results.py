# -*- coding: utf-8 -*-
"""
plot_parameter_results.py
Script pour générer des graphiques à partir des résultats de tests de paramètres.
"""

from __future__ import annotations
import os
import sys
import re
from typing import Dict, List, Any, Tuple

try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("ERREUR: matplotlib requis pour générer les graphiques.")
    print("Installez-le avec: pip install matplotlib")
    sys.exit(1)


class ParameterResultsPlotter:
    """Classe pour charger et visualiser les résultats de tests de paramètres."""
    
    def __init__(self, filename: str):
        """
        Initialise le plotter avec un fichier de résultats.
        
        Args:
            filename: Chemin vers le fichier de résultats
        """
        self.filename = filename
        self.results = []
        self.load_results()
    
    def load_results(self):
        """Charge les résultats depuis le fichier texte."""
        if not os.path.exists(self.filename):
            print(f"Fichier {self.filename} introuvable.")
            sys.exit(1)
        
        with open(self.filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Filtrer les lignes de commentaires
        data_lines = [line.strip() for line in lines if not line.startswith('#') and line.strip()]
        
        for line in data_lines:
            parts = line.split('|')
            if len(parts) < 8:
                continue
            
            result = {}
            result['config_name'] = parts[0]
            
            # Parse des paramètres
            params = {}
            metrics_start = 1
            for i, part in enumerate(parts[1:], 1):
                if ':' in part and not part.startswith(('cost_', 'vehicles_', 'time_', 'num_', 'all_')):
                    key, value = part.split(':', 1)
                    # Conversion du type
                    if value.lower() == 'true':
                        params[key] = True
                    elif value.lower() == 'false':
                        params[key] = False
                    elif '.' in value:
                        try:
                            params[key] = float(value)
                        except ValueError:
                            params[key] = value
                    else:
                        try:
                            params[key] = int(value)
                        except ValueError:
                            params[key] = value
                    metrics_start = i + 1
                else:
                    break
            
            result['parameters'] = params
            
            # Parse des métriques
            for part in parts[metrics_start:]:
                if ':' in part:
                    key, value = part.split(':', 1)
                    if key.startswith('all_costs'):
                        # Parse de la liste des coûts
                        costs_match = re.search(r'\[(.*?)\]', value)
                        if costs_match:
                            costs_str = costs_match.group(1)
                            result['all_costs'] = [int(c) for c in costs_str.split(',') if c.strip()]
                    else:
                        try:
                            result[key] = float(value)
                        except ValueError:
                            result[key] = value
            
            self.results.append(result)
        
        print(f"Chargé {len(self.results)} résultats depuis {self.filename}")
    
    def get_parameter_values(self, param_name: str) -> List[Any]:
        """Retourne toutes les valeurs d'un paramètre."""
        values = []
        for result in self.results:
            if param_name in result['parameters']:
                values.append(result['parameters'][param_name])
        return values
    
    def filter_by_parameter(self, param_name: str, param_value: Any) -> List[Dict]:
        """Filtre les résultats par valeur de paramètre."""
        filtered = []
        for result in self.results:
            if result['parameters'].get(param_name) == param_value:
                filtered.append(result)
        return filtered
    
    def group_by_parameter(self, param_name: str) -> Dict[Any, List[Dict]]:
        """Groupe les résultats par valeur de paramètre."""
        groups = {}
        for result in self.results:
            value = result['parameters'].get(param_name)
            if value is not None:
                if value not in groups:
                    groups[value] = []
                groups[value].append(result)
        return groups
    
    def plot_parameter_impact(self, param_name: str, save_path: str = None):
        """
        Crée un graphique montrant l'impact d'un paramètre sur les performances.
        
        Args:
            param_name: Nom du paramètre à analyser
            save_path: Chemin pour sauvegarder le graphique (optionnel)
        """
        groups = self.group_by_parameter(param_name)
        if not groups:
            print(f"Aucune donnée trouvée pour le paramètre '{param_name}'")
            return
        
        # Préparation des données
        param_values = []
        mean_costs = []
        std_costs = []
        min_costs = []
        max_costs = []
        all_individual_costs = []
        
        for value, results in groups.items():
            costs = [r['cost_mean'] for r in results]
            # Collecte de tous les coûts individuels pour histogramme
            individual_costs = []
            for r in results:
                if 'all_costs' in r:
                    individual_costs.extend(r['all_costs'])
                else:
                    individual_costs.append(r['cost_mean'])
            
            param_values.append(value)
            mean_costs.append(np.mean(costs))
            std_costs.append(np.std(costs) if len(costs) > 1 else 0)
            min_costs.append(min(individual_costs))
            max_costs.append(max(individual_costs))
            all_individual_costs.append(individual_costs)
        
        # Tri par valeur du paramètre
        if all(isinstance(v, (int, float)) for v in param_values):
            sorted_data = sorted(zip(param_values, mean_costs, std_costs, min_costs, max_costs, all_individual_costs))
            param_values, mean_costs, std_costs, min_costs, max_costs, all_individual_costs = zip(*sorted_data)
        
        # Création du graphique avec 4 sous-graphiques
        fig = plt.figure(figsize=(20, 12))
        
        # Graphique 1: Coût moyen avec barres d'erreur et min/max
        ax1 = plt.subplot(2, 2, 1)
        x_pos = range(len(param_values))
        
        # Barres principales (coût moyen)
        bars = ax1.bar(x_pos, mean_costs, yerr=std_costs, capsize=5, alpha=0.7, 
                      color='skyblue', edgecolor='navy', label='Coût moyen ± écart-type')
        
        # Points pour min et max
        ax1.scatter(x_pos, min_costs, color='green', marker='v', s=60, 
                   label='Meilleur coût', zorder=5)
        ax1.scatter(x_pos, max_costs, color='red', marker='^', s=60, 
                   label='Pire coût', zorder=5)
        
        ax1.set_xlabel(f'{param_name}')
        ax1.set_ylabel('Coût')
        ax1.set_title(f'Impact du paramètre {param_name} - Vue d\'ensemble')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels([str(v) for v in param_values], rotation=45 if len(str(param_values[0])) > 3 else 0)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Annotation de la meilleure valeur
        best_idx = np.argmin(mean_costs)
        ax1.annotate(f'Optimal\n{mean_costs[best_idx]:.1f}', 
                    xy=(best_idx, mean_costs[best_idx]), 
                    xytext=(best_idx, mean_costs[best_idx] + (max(mean_costs) - min(mean_costs)) * 0.15),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2),
                    ha='center', color='red', fontweight='bold', fontsize=10)
        
        # Graphique 2: Points individuels avec valeur de paramètre en X
        ax2 = plt.subplot(2, 2, 2)
        
        # Créer un scatter plot avec jitter pour voir tous les points
        colors = plt.cm.Set3(np.linspace(0, 1, len(param_values)))
        
        for i, (value, costs) in enumerate(zip(param_values, all_individual_costs)):
            # Ajouter un peu de jitter horizontal pour éviter la superposition
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                x_positions = [value] * len(costs)
                jitter = np.random.normal(0, 0.01, len(costs))
                x_jittered = np.array(x_positions) + jitter
            else:
                x_positions = [i] * len(costs)
                jitter = np.random.normal(0, 0.05, len(costs))
                x_jittered = np.array(x_positions) + jitter
            
            ax2.scatter(x_jittered, costs, alpha=0.6, 
                       label=f'{param_name}={value}', color=colors[i], s=30)
        
        # Ajouter une ligne pour les moyennes
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in param_values):
            ax2.plot(param_values, mean_costs, 'o-', linewidth=2, markersize=8, 
                    label='Coût moyen', color='red', alpha=0.8)
            ax2.set_xlabel(f'{param_name}')
        else:
            # Pour les paramètres catégoriels
            ax2.plot(range(len(param_values)), mean_costs, 'o-', linewidth=2, markersize=8, 
                    label='Coût moyen', color='red', alpha=0.8)
            ax2.set_xticks(range(len(param_values)))
            ax2.set_xticklabels([str(v) for v in param_values], rotation=45)
            ax2.set_xlabel(f'{param_name}')
        
        ax2.set_ylabel('Coût')
        ax2.set_title(f'Coût en fonction de {param_name}')
        ax2.grid(True, alpha=0.3)
        if len(param_values) <= 6:  # Légende seulement si pas trop de valeurs
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Graphique 3: Box plot détaillé
        ax3 = plt.subplot(2, 2, 3)
        
        box_plot = ax3.boxplot(all_individual_costs, labels=[str(v) for v in param_values], 
                              patch_artist=True, showmeans=True)
        ax3.set_xlabel(f'{param_name}')
        ax3.set_ylabel('Coût')
        ax3.set_title(f'Distribution détaillée par {param_name}')
        ax3.grid(True, alpha=0.3)
        
        # Coloration des boxplots selon la performance
        performance_colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(box_plot['boxes'])))
        sorted_indices = np.argsort(mean_costs)
        for i, (patch, color_idx) in enumerate(zip(box_plot['boxes'], sorted_indices)):
            patch.set_facecolor(performance_colors[color_idx])
            patch.set_alpha(0.7)
        
        # Graphique 4: Tendance et corrélation (si paramètre numérique)
        ax4 = plt.subplot(2, 2, 4)
        
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in param_values):
            # Scatter plot avec ligne de tendance
            ax4.scatter(param_values, mean_costs, s=100, alpha=0.7, color='blue')
            
            # Ligne de tendance
            z = np.polyfit(param_values, mean_costs, 1)
            p = np.poly1d(z)
            ax4.plot(param_values, p(param_values), "r--", alpha=0.8, linewidth=2)
            
            # Calcul de la corrélation
            corr = np.corrcoef(param_values, mean_costs)[0, 1]
            ax4.set_title(f'Tendance {param_name} vs Performance\nCorrélation: {corr:.3f}')
            
            # Zones d'amélioration
            best_value = param_values[best_idx]
            ax4.axvline(x=best_value, color='green', linestyle=':', alpha=0.7, 
                       label=f'Valeur optimale: {best_value}')
            
        else:
            # Pour les paramètres catégoriels, afficher un graphique en barres simple
            bars4 = ax4.bar(range(len(param_values)), mean_costs, alpha=0.7)
            ax4.set_xticks(range(len(param_values)))
            ax4.set_xticklabels([str(v) for v in param_values], rotation=45)
            ax4.set_title(f'Performance par {param_name}')
            
            # Coloration selon la performance
            for bar, cost in zip(bars4, mean_costs):
                normalized_cost = (cost - min(mean_costs)) / (max(mean_costs) - min(mean_costs))
                bar.set_color(plt.cm.RdYlGn_r(normalized_cost))
        
        ax4.set_xlabel(f'{param_name}')
        ax4.set_ylabel('Coût moyen')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Graphique sauvegardé: {save_path}")
        
        plt.show()
        
        # Affichage des statistiques textuelles
        print(f"\n{'='*60}")
        print(f"ANALYSE STATISTIQUE - {param_name}")
        print(f"{'='*60}")
        
        for i, (value, costs) in enumerate(zip(param_values, all_individual_costs)):
            print(f"{param_name} = {value}:")
            print(f"  Nombre d'essais: {len(costs)}")
            print(f"  Coût moyen: {np.mean(costs):.1f}")
            print(f"  Écart-type: {np.std(costs):.2f}")
            print(f"  Min: {min(costs)}, Max: {max(costs)}")
            print(f"  Médiane: {np.median(costs):.1f}")
            if i < len(param_values) - 1:
                print()
        
        best_value = param_values[best_idx]
        worst_idx = np.argmax(mean_costs)
        worst_value = param_values[worst_idx]
        improvement = (mean_costs[worst_idx] - mean_costs[best_idx]) / mean_costs[worst_idx] * 100
        
        print(f"\nRÉSUMÉ:")
        print(f"Meilleure valeur: {best_value} (coût: {mean_costs[best_idx]:.1f})")
        print(f"Pire valeur: {worst_value} (coût: {mean_costs[worst_idx]:.1f})")
        print(f"Amélioration possible: {improvement:.1f}%")
    
    def plot_all_parameters_summary(self, save_path: str = None):
        """
        Crée un graphique de synthèse montrant l'impact de tous les paramètres.
        
        Args:
            save_path: Chemin pour sauvegarder le graphique (optionnel)
        """
        # Identification des paramètres numériques
        numeric_params = set()
        for result in self.results:
            for param, value in result['parameters'].items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    numeric_params.add(param)
        
        numeric_params = list(numeric_params)
        if not numeric_params:
            print("Aucun paramètre numérique trouvé.")
            return
        
        # Calcul des corrélations
        correlations = []
        improvements = []
        
        for param in numeric_params:
            groups = self.group_by_parameter(param)
            if len(groups) < 2:
                continue
            
            values = []
            costs = []
            for value, results in groups.items():
                mean_cost = np.mean([r['cost_mean'] for r in results])
                values.append(value)
                costs.append(mean_cost)
            
            if len(values) > 1:
                corr = np.corrcoef(values, costs)[0, 1]
                improvement = (max(costs) - min(costs)) / max(costs) * 100
                correlations.append(corr)
                improvements.append(improvement)
            else:
                correlations.append(0)
                improvements.append(0)
        
        # Création du graphique
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Graphique 1: Corrélations
        bars1 = ax1.barh(numeric_params, correlations)
        ax1.set_xlabel('Corrélation avec le coût')
        ax1.set_title('Corrélation des paramètres avec la performance')
        ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        ax1.grid(True, alpha=0.3)
        
        # Coloration des barres selon la corrélation
        for bar, corr in zip(bars1, correlations):
            if abs(corr) > 0.5:
                bar.set_color('red' if corr > 0 else 'green')
            elif abs(corr) > 0.3:
                bar.set_color('orange' if corr > 0 else 'lightgreen')
            else:
                bar.set_color('gray')
        
        # Graphique 2: Amélioration potentielle
        bars2 = ax2.barh(numeric_params, improvements)
        ax2.set_xlabel('Amélioration potentielle (%)')
        ax2.set_title('Impact potentiel de l\'optimisation par paramètre')
        ax2.grid(True, alpha=0.3)
        
        # Coloration par importance
        max_improvement = max(improvements) if improvements else 1
        colors = plt.cm.Reds([imp/max_improvement for imp in improvements])
        for bar, color in zip(bars2, colors):
            bar.set_color(color)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Graphique de synthèse sauvegardé: {save_path}")
        
        plt.show()
    
    def plot_parameter_histograms_grid(self, save_path: str = None):
        """
        Crée une grille d'histogrammes pour tous les paramètres.
        
        Args:
            save_path: Chemin pour sauvegarder le graphique (optionnel)
        """
        # Identification de tous les paramètres
        all_params = set()
        for result in self.results:
            all_params.update(result['parameters'].keys())
        
        all_params = sorted(list(all_params))
        
        if not all_params:
            print("Aucun paramètre trouvé.")
            return
        
        # Calcul de la grille optimale
        n_params = len(all_params)
        cols = min(4, n_params)
        rows = (n_params + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
        if rows == 1 and cols == 1:
            axes = [axes]
        elif rows == 1 or cols == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
        
        for i, param in enumerate(all_params):
            ax = axes[i] if i < len(axes) else None
            if ax is None:
                continue
            
            groups = self.group_by_parameter(param)
            if not groups:
                ax.text(0.5, 0.5, f'Pas de données\npour {param}', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title(param)
                continue
            
            # Collecte de tous les coûts pour ce paramètre
            all_costs_by_value = []
            param_values = []
            
            for value, results in groups.items():
                costs = []
                for r in results:
                    if 'all_costs' in r:
                        costs.extend(r['all_costs'])
                    else:
                        costs.append(r['cost_mean'])
                
                if costs:
                    all_costs_by_value.append(costs)
                    param_values.append(value)
            
            if not all_costs_by_value:
                continue
            
            # Tri par valeur de paramètre si numérique
            if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in param_values):
                sorted_data = sorted(zip(param_values, all_costs_by_value))
                param_values, all_costs_by_value = zip(*sorted_data)
            
            # Création du graphique valeur de paramètre vs coût
            colors = plt.cm.Set3(np.linspace(0, 1, len(param_values)))
            
            # Calcul des moyennes pour chaque valeur de paramètre
            means = [np.mean(costs) for costs in all_costs_by_value]
            
            # Graphique principal : paramètre en X, coût en Y
            if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in param_values):
                # Paramètre numérique : scatter plot avec ligne des moyennes
                all_x = []
                all_y = []
                for value, costs in zip(param_values, all_costs_by_value):
                    # Ajouter un peu de jitter pour éviter la superposition
                    jitter = np.random.normal(0, (max(param_values) - min(param_values)) * 0.01, len(costs))
                    x_jittered = [value] * len(costs) + jitter
                    all_x.extend(x_jittered)
                    all_y.extend(costs)
                
                # Points individuels avec jitter
                ax.scatter(all_x, all_y, alpha=0.4, s=15, color='lightblue')
                
                # Ligne des moyennes
                ax.plot(param_values, means, 'o-', linewidth=2, markersize=8, 
                       color='red', alpha=0.8, label='Coût moyen')
                
                ax.set_xlabel(f'{param}')
                
            else:
                # Paramètre catégoriel : bar plot et points
                x_positions = list(range(len(param_values)))
                
                # Barres pour les moyennes
                bars = ax.bar(x_positions, means, alpha=0.6, color=colors)
                
                # Points individuels avec jitter
                for i, (x_pos, costs) in enumerate(zip(x_positions, all_costs_by_value)):
                    jitter = np.random.normal(0, 0.1, len(costs))
                    x_jittered = [x_pos] * len(costs) + jitter
                    ax.scatter(x_jittered, costs, alpha=0.6, s=20, color=colors[i])
                
                ax.set_xticks(x_positions)
                ax.set_xticklabels([str(v) for v in param_values], rotation=45)
                ax.set_xlabel(f'{param}')
            
            ax.set_ylabel('Coût')
            ax.set_title(f'Coût en fonction de {param}')
            ax.grid(True, alpha=0.3)
            
            # Marquer la meilleure valeur
            best_idx = np.argmin(means)
            best_value = param_values[best_idx]
            best_cost = means[best_idx]
            
            if isinstance(best_value, (int, float)) and not isinstance(best_value, bool):
                ax.axvline(x=best_value, color='green', linestyle='--', alpha=0.7, 
                          label=f'Optimal: {best_value}')
            else:
                # Pour les paramètres catégoriels, encercler la barre optimale
                if all(not isinstance(v, (int, float)) or isinstance(v, bool) for v in param_values):
                    ax.axvline(x=best_idx, color='green', linestyle='--', alpha=0.7, 
                              label=f'Optimal: {best_value}')
            
            # Légende seulement si peu de valeurs
            if len(param_values) <= 5:
                ax.legend(fontsize=8)
        
        # Masquer les axes non utilisés
        for i in range(len(all_params), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('Performance en fonction des paramètres', fontsize=16, y=0.98)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Grille d'histogrammes sauvegardée: {save_path}")
        
        plt.show()
    
    def plot_performance_heatmap(self, save_path: str = None):
        """
        Crée une heatmap des performances par paramètre et valeur.
        
        Args:
            save_path: Chemin pour sauvegarder le graphique (optionnel)
        """
        # Identification des paramètres numériques principaux
        numeric_params = []
        for result in self.results:
            for param, value in result['parameters'].items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if param not in numeric_params:
                        numeric_params.append(param)
        
        if len(numeric_params) < 2:
            print("Pas assez de paramètres numériques pour une heatmap.")
            return
        
        # Création d'une matrice de performance pour les 4 paramètres les plus variables
        param_variability = []
        for param in numeric_params:
            values = [r['parameters'].get(param) for r in self.results if param in r['parameters']]
            if values and len(set(values)) > 1:
                variability = (max(values) - min(values)) / max(values) if max(values) > 0 else 0
                param_variability.append((param, variability, len(set(values))))
        
        # Tri par variabilité et nombre de valeurs différentes
        param_variability.sort(key=lambda x: (x[1], x[2]), reverse=True)
        top_params = [p[0] for p in param_variability[:4]]
        
        if len(top_params) < 2:
            print("Pas assez de variabilité dans les paramètres.")
            return
        
        # Création des heatmaps pour les paires de paramètres
        n_pairs = min(6, len(top_params) * (len(top_params) - 1) // 2)
        cols = min(3, n_pairs)
        rows = (n_pairs + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(6*cols, 5*rows))
        if rows == 1 and cols == 1:
            axes = [axes]
        elif rows == 1 or cols == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
        
        pair_idx = 0
        for i in range(len(top_params)):
            for j in range(i+1, len(top_params)):
                if pair_idx >= len(axes):
                    break
                
                param1, param2 = top_params[i], top_params[j]
                ax = axes[pair_idx]
                
                # Création de la matrice de performance
                param1_values = sorted(set(r['parameters'].get(param1) for r in self.results 
                                         if param1 in r['parameters']))
                param2_values = sorted(set(r['parameters'].get(param2) for r in self.results 
                                         if param2 in r['parameters']))
                
                if len(param1_values) > 10:
                    param1_values = param1_values[::len(param1_values)//10]
                if len(param2_values) > 10:
                    param2_values = param2_values[::len(param2_values)//10]
                
                performance_matrix = np.full((len(param2_values), len(param1_values)), np.nan)
                
                for r in self.results:
                    if param1 in r['parameters'] and param2 in r['parameters']:
                        val1 = r['parameters'][param1]
                        val2 = r['parameters'][param2]
                        
                        if val1 in param1_values and val2 in param2_values:
                            idx1 = param1_values.index(val1)
                            idx2 = param2_values.index(val2)
                            performance_matrix[idx2, idx1] = r['cost_mean']
                
                # Création de la heatmap
                im = ax.imshow(performance_matrix, cmap='RdYlGn_r', aspect='auto')
                
                ax.set_xticks(range(len(param1_values)))
                ax.set_xticklabels([str(v) for v in param1_values], rotation=45)
                ax.set_yticks(range(len(param2_values)))
                ax.set_yticklabels([str(v) for v in param2_values])
                
                ax.set_xlabel(param1)
                ax.set_ylabel(param2)
                ax.set_title(f'Performance: {param1} vs {param2}')
                
                # Barre de couleur
                plt.colorbar(im, ax=ax, label='Coût moyen')
                
                pair_idx += 1
                
                if pair_idx >= n_pairs:
                    break
            
            if pair_idx >= n_pairs:
                break
        
        # Masquer les axes non utilisés
        for i in range(pair_idx, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Heatmap de performance sauvegardée: {save_path}")
        
        plt.show()
        """
        Compare les meilleures et pires configurations.
        
        Args:
            save_path: Chemin pour sauvegarder le graphique (optionnel)
        """
        if len(self.results) < 2:
            print("Pas assez de résultats pour la comparaison.")
            return
        
        # Tri par coût moyen
        sorted_results = sorted(self.results, key=lambda x: x['cost_mean'])
        best = sorted_results[0]
        worst = sorted_results[-1]
        
        # Extraction des paramètres
        all_params = set()
        for result in [best, worst]:
            all_params.update(result['parameters'].keys())
        
        all_params = list(all_params)
        best_values = [best['parameters'].get(param, 0) for param in all_params]
        worst_values = [worst['parameters'].get(param, 0) for param in all_params]
        
        # Création du graphique radar
        angles = np.linspace(0, 2 * np.pi, len(all_params), endpoint=False).tolist()
        angles += angles[:1]  # Fermer le cercle
        
        # Normalisation des valeurs pour le radar (0-1)
        normalized_best = []
        normalized_worst = []
        
        for i, param in enumerate(all_params):
            values = [r['parameters'].get(param, 0) for r in self.results if param in r['parameters']]
            if values and max(values) != min(values):
                min_val, max_val = min(values), max(values)
                norm_best = (best_values[i] - min_val) / (max_val - min_val)
                norm_worst = (worst_values[i] - min_val) / (max_val - min_val)
            else:
                norm_best = norm_worst = 0.5
            
            normalized_best.append(norm_best)
            normalized_worst.append(norm_worst)
        
        normalized_best += normalized_best[:1]
        normalized_worst += normalized_worst[:1]
        
        # Graphique radar
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, normalized_best, 'o-', linewidth=2, label=f'Meilleure (coût: {best["cost_mean"]:.1f})', color='green')
        ax.fill(angles, normalized_best, alpha=0.25, color='green')
        
        ax.plot(angles, normalized_worst, 'o-', linewidth=2, label=f'Pire (coût: {worst["cost_mean"]:.1f})', color='red')
        ax.fill(angles, normalized_worst, alpha=0.25, color='red')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(all_params)
        ax.set_ylim(0, 1)
        ax.set_title('Comparaison des paramètres: Meilleure vs Pire configuration', y=1.08)
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        ax.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Graphique de comparaison sauvegardé: {save_path}")
        
        plt.show()
    
    def plot_best_vs_worst(self, save_path: str = None):
        """
        Crée un graphique de comparaison entre la meilleure et la pire configuration.
        
        Args:
            save_path: Chemin pour sauvegarder le graphique (optionnel)
        """
        if not self.results:
            print("Aucun résultat à comparer.")
            return
        
        # Tri par coût moyen
        sorted_results = sorted(self.results, key=lambda x: x['cost_mean'])
        best = sorted_results[0]
        worst = sorted_results[-1]
        
        print(f"\n{'='*60}")
        print("COMPARAISON MEILLEURE VS PIRE CONFIGURATION")
        print(f"{'='*60}")
        print(f"Meilleure: {best['config_name']} (coût: {best['cost_mean']:.1f})")
        print(f"Pire: {worst['config_name']} (coût: {worst['cost_mean']:.1f})")
        print(f"Amélioration: {(worst['cost_mean'] - best['cost_mean']) / worst['cost_mean'] * 100:.1f}%")
        
        # Création du graphique comparatif
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Graphique 1: Comparaison des coûts moyens
        configs = ['Meilleure', 'Pire']
        costs = [best['cost_mean'], worst['cost_mean']]
        colors = ['green', 'red']
        
        bars = ax1.bar(configs, costs, color=colors, alpha=0.7)
        ax1.set_ylabel('Coût moyen')
        ax1.set_title('Comparaison des coûts moyens')
        ax1.grid(True, alpha=0.3)
        
        # Annotation des valeurs
        for bar, cost in zip(bars, costs):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(costs)*0.01,
                    f'{cost:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Graphique 2: Comparaison des paramètres (graphique radar)
        # Collecter tous les paramètres communs
        all_params = set(best['parameters'].keys()) & set(worst['parameters'].keys())
        all_params = list(all_params)
        
        if len(all_params) >= 3:
            # Angles pour le graphique radar
            angles = np.linspace(0, 2 * np.pi, len(all_params), endpoint=False)
            
            # Normalisation des valeurs entre 0 et 1 pour le radar
            best_values = []
            worst_values = []
            
            for param in all_params:
                best_val = best['parameters'][param]
                worst_val = worst['parameters'][param]
                
                # Trouver min/max de ce paramètre dans tous les résultats
                all_vals = [r['parameters'].get(param) for r in self.results if param in r['parameters']]
                all_vals = [v for v in all_vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
                
                if all_vals and len(set(all_vals)) > 1:
                    min_val, max_val = min(all_vals), max(all_vals)
                    if max_val > min_val:
                        best_norm = (best_val - min_val) / (max_val - min_val)
                        worst_norm = (worst_val - min_val) / (max_val - min_val)
                    else:
                        best_norm = worst_norm = 0.5
                else:
                    best_norm = worst_norm = 0.5
                
                best_values.append(best_norm)
                worst_values.append(worst_norm)
            
            # Fermer le graphique radar
            best_values += best_values[:1]
            worst_values += worst_values[:1]
            angles = np.concatenate([angles, [angles[0]]])
            
            ax2 = plt.subplot(2, 2, 2, projection='polar')
            ax2.plot(angles, best_values, 'o-', linewidth=2, label='Meilleure', color='green')
            ax2.fill(angles, best_values, alpha=0.25, color='green')
            ax2.plot(angles, worst_values, 'o-', linewidth=2, label='Pire', color='red')
            ax2.fill(angles, worst_values, alpha=0.25, color='red')
            
            ax2.set_xticks(angles[:-1])
            ax2.set_xticklabels(all_params)
            ax2.set_ylim(0, 1)
            ax2.set_title('Profil des paramètres')
            ax2.legend()
        else:
            ax2.text(0.5, 0.5, 'Pas assez de\nparamètres communs\npour un radar', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Profil des paramètres')
        
        # Graphique 3: Comparaison des paramètres différents (barres côte à côte)
        # Identifier les paramètres qui diffèrent
        diff_params = []
        for param in all_params:
            best_val = best['parameters'][param]
            worst_val = worst['parameters'][param]
            if best_val != worst_val:
                # Normaliser pour la comparaison visuelle si numérique
                if isinstance(best_val, (int, float)) and not isinstance(best_val, bool):
                    diff_params.append((param, best_val, worst_val))
        
        if diff_params:
            param_names = [p[0] for p in diff_params]
            best_vals = [p[1] for p in diff_params]
            worst_vals = [p[2] for p in diff_params]
            
            x_pos = np.arange(len(param_names))
            width = 0.35
            
            bars1 = ax3.bar(x_pos - width/2, best_vals, width, label='Meilleure', 
                           color='green', alpha=0.7)
            bars2 = ax3.bar(x_pos + width/2, worst_vals, width, label='Pire', 
                           color='red', alpha=0.7)
            
            ax3.set_xlabel('Paramètres')
            ax3.set_ylabel('Valeurs')
            ax3.set_title('Comparaison des paramètres différents')
            ax3.set_xticks(x_pos)
            ax3.set_xticklabels(param_names, rotation=45, ha='right')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Annotation des valeurs sur les barres
            for bar, val in zip(bars1, best_vals):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(best_vals + worst_vals)*0.01,
                        f'{val}', ha='center', va='bottom', fontsize=8)
            for bar, val in zip(bars2, worst_vals):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(best_vals + worst_vals)*0.01,
                        f'{val}', ha='center', va='bottom', fontsize=8)
        else:
            ax3.text(0.5, 0.5, 'Aucun paramètre\nnumérique différent', 
                    ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Comparaison des paramètres différents')
        
        # Graphique 4: Tableau des paramètres différents
        ax4.axis('off')
        
        # Identifier les paramètres qui diffèrent
        diff_params = []
        for param in all_params:
            if best['parameters'][param] != worst['parameters'][param]:
                diff_params.append((
                    param, 
                    best['parameters'][param], 
                    worst['parameters'][param]
                ))
        
        if diff_params:
            table_data = [['Paramètre', 'Meilleure', 'Pire']]
            for param, best_val, worst_val in diff_params:
                table_data.append([param, str(best_val), str(worst_val)])
            
            table = ax4.table(cellText=table_data[1:], colLabels=table_data[0],
                             cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)
            
            # Coloration de l'en-tête
            for i in range(len(table_data[0])):
                table[(0, i)].set_facecolor('#40466e')
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            ax4.set_title('Paramètres différents', pad=20)
        else:
            ax4.text(0.5, 0.5, 'Aucun paramètre\ndifférent trouvé', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Paramètres différents')
        
        plt.suptitle(f'Comparaison: {best["config_name"]} vs {worst["config_name"]}', 
                    fontsize=16, y=0.98)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Graphique de comparaison sauvegardé: {save_path}")
        
        plt.show()
        
        # Affichage détaillé des différences
        print(f"\nDÉTAILS DES CONFIGURATIONS:")
        print(f"{'='*60}")
        print(f"MEILLEURE - {best['config_name']}:")
        for param, value in best['parameters'].items():
            print(f"  {param:<15}: {value}")
        print(f"  Coût moyen: {best['cost_mean']:.1f}")
        print(f"  Runs valides: {best.get('num_valid_runs', 'N/A')}")
        
        print(f"\nPIRE - {worst['config_name']}:")
        for param, value in worst['parameters'].items():
            print(f"  {param:<15}: {value}")
        print(f"  Coût moyen: {worst['cost_mean']:.1f}")
        print(f"  Runs valides: {worst.get('num_valid_runs', 'N/A')}")
    
    def print_summary_stats(self):
        """Affiche les statistiques de synthèse."""
        if not self.results:
            print("Aucun résultat à analyser.")
            return
        
        costs = [r['cost_mean'] for r in self.results]
        
        print(f"\n{'='*60}")
        print("STATISTIQUES DE SYNTHÈSE")
        print(f"{'='*60}")
        print(f"Nombre de configurations testées: {len(self.results)}")
        print(f"Coût moyen global: {np.mean(costs):.1f}")
        print(f"Écart-type global: {np.std(costs):.1f}")
        print(f"Meilleur coût: {min(costs):.1f}")
        print(f"Pire coût: {max(costs):.1f}")
        print(f"Amélioration possible: {(max(costs) - min(costs)) / max(costs) * 100:.1f}%")
        
        # Top 3
        sorted_results = sorted(self.results, key=lambda x: x['cost_mean'])
        print(f"\nTOP 3 CONFIGURATIONS:")
        for i, result in enumerate(sorted_results[:3]):
            print(f"\n{i+1}. {result['config_name']}")
            print(f"   Coût: {result['cost_mean']:.1f}")
            print(f"   Paramètres: {result['parameters']}")


def main():
    """Fonction principale pour la génération de graphiques."""
    print("GÉNÉRATEUR DE GRAPHIQUES - RÉSULTATS DE TESTS DE PARAMÈTRES")
    print("=" * 60)
    
    # Sélection du fichier de résultats
    print("\nFichiers de résultats disponibles:")
    result_files = [f for f in os.listdir('.') if f.startswith('parameter_test_results_') and f.endswith('.txt')]
    
    if not result_files:
        print("Aucun fichier de résultats trouvé.")
        filename = input("Entrez le nom du fichier manuellement: ").strip()
    else:
        for i, f in enumerate(result_files):
            print(f"{i+1}. {f}")
        
        choice = input(f"\nChoisissez un fichier (1-{len(result_files)}) ou entrez un nom: ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(result_files):
                filename = result_files[idx]
            else:
                filename = choice
        except ValueError:
            filename = choice
    
    # Création du plotter
    try:
        plotter = ParameterResultsPlotter(filename)
    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        return
    
    # Menu interactif
    while True:
        print(f"\n{'='*50}")
        print("MENU DE GÉNÉRATION DE GRAPHIQUES")
        print(f"{'='*50}")
        print("1. Statistiques de synthèse")
        print("2. Impact d'un paramètre spécifique (détaillé)")
        print("3. Synthèse de tous les paramètres")
        print("4. Comparaison meilleure vs pire configuration")
        print("5. Grille d'histogrammes par paramètre")
        print("6. Heatmap des performances")
        print("7. Générer tous les graphiques")
        print("0. Quitter")
        
        choice = input("\nVotre choix: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            plotter.print_summary_stats()
        elif choice == "2":
            # Liste des paramètres disponibles
            all_params = set()
            for result in plotter.results:
                all_params.update(result['parameters'].keys())
            
            print(f"\nParamètres disponibles: {', '.join(all_params)}")
            param = input("Entrez le nom du paramètre à analyser: ").strip()
            
            if param in all_params:
                save = input("Sauvegarder le graphique? (y/n): ").strip().lower() == 'y'
                save_path = f"impact_{param}_detailed.png" if save else None
                plotter.plot_parameter_impact(param, save_path)
            else:
                print("Paramètre non trouvé.")
        elif choice == "3":
            save = input("Sauvegarder le graphique? (y/n): ").strip().lower() == 'y'
            save_path = "synthese_parametres.png" if save else None
            plotter.plot_all_parameters_summary(save_path)
        elif choice == "4":
            save = input("Sauvegarder le graphique? (y/n): ").strip().lower() == 'y'
            save_path = "comparaison_best_worst.png" if save else None
            plotter.plot_best_vs_worst(save_path)
        elif choice == "5":
            save = input("Sauvegarder le graphique? (y/n): ").strip().lower() == 'y'
            save_path = "histogrammes_grid.png" if save else None
            plotter.plot_parameter_histograms_grid(save_path)
        elif choice == "6":
            save = input("Sauvegarder le graphique? (y/n): ").strip().lower() == 'y'
            save_path = "performance_heatmap.png" if save else None
            plotter.plot_performance_heatmap(save_path)
        elif choice == "7":
            print("Génération de tous les graphiques...")
            
            # Synthèse
            plotter.plot_all_parameters_summary("synthese_parametres.png")
            
            # Comparaison
            plotter.plot_best_vs_worst("comparaison_best_worst.png")
            
            # Grille d'histogrammes
            plotter.plot_parameter_histograms_grid("histogrammes_grid.png")
            
            # Heatmap
            plotter.plot_performance_heatmap("performance_heatmap.png")
            
            # Impact de chaque paramètre
            all_params = set()
            for result in plotter.results:
                all_params.update(result['parameters'].keys())
            
            for param in all_params:
                plotter.plot_parameter_impact(param, f"impact_{param}_detailed.png")
            
            print("Tous les graphiques ont été générés et sauvegardés.")
        else:
            print("Choix invalide.")
    
    print("Au revoir!")


if __name__ == "__main__":
    main()