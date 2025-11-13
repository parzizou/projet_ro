#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Benchmark Complet pour Algorithme Génétique CVRP
=================================================

Script de benchmark professionnel pour évaluer les performances de l'AG
sur l'instance X-n153-k22 avec différentes configurations de paramètres.

Features:
- Test de 69 configurations de paramètres
- Multi-threading pour performance maximale
- Calcul automatique du baseline
- Génération de 7 visualisations professionnelles
- Export JSON et CSV des résultats
- Statistiques détaillées (gap, amélioration, temps)

Usage:
    python benchmarks/benchmark.py
    
Durée estimée: ~15 minutes (avec multi-threading)

Author: CVRP Optimization System
Date: Novembre 2025
"""

import os
import sys
import time
import json
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.cvrp_data import load_cvrp_instance
from src.optimization.exploration_helpers import run_ga_with_params


def find_solution_for_instance(instance_path):
    """
    Recherche la solution optimale connue pour une instance.
    
    Args:
        instance_path: Chemin vers le fichier .vrp
        
    Returns:
        int: Coût optimal si trouvé, None sinon
    """
    # Dictionnaire des solutions connues
    known_solutions = {
        'data.vrp': 27591,
        'X-n101-k25': 27591,
        'X-n153-k22': 22901,
    }
    
    # Extraire le nom du fichier
    filename = os.path.basename(instance_path)
    
    # Chercher dans les solutions connues
    if filename in known_solutions:
        return known_solutions[filename]
    
    # Chercher un fichier .sol correspondant
    sol_path = instance_path.replace('.vrp', '.sol')
    if os.path.exists(sol_path):
        try:
            with open(sol_path, 'r') as f:
                for line in f:
                    if 'Cost' in line or 'cost' in line:
                        parts = line.strip().split()
                        for part in parts:
                            if part.isdigit():
                                return int(part)
        except:
            pass
    
    return None


def run_ga_single(instance, params, time_limit=60):
    """
    Exécute un run GA avec les paramètres donnés.
    
    Args:
        instance: Instance CVRP chargée
        params: Dict des paramètres GA
        time_limit: Limite de temps en secondes
        
    Returns:
        tuple: (cost, time, n_routes)
    """
    # run_ga_with_params retourne un tuple (cost, time, n_routes)
    cost, elapsed, n_routes = run_ga_with_params(instance, params, time_limit)
    return cost, elapsed, n_routes


def compare_init_modes(instance, default_params, n_runs=5, time_limit=60):
    """
    Compare les deux modes d'initialisation de la population.
    
    Args:
        instance: Instance CVRP
        default_params: Paramètres par défaut
        n_runs: Nombre d'exécutions pour chaque mode
        time_limit: Temps limite par run
        
    Returns:
        tuple: (results_dict, stats_dict)
    """
    from src.core.ga import genetic_algorithm
    import time as time_module
    
    results = {
        'nn_plus_random': [],  # Mode par défaut (1 NN + reste aléatoire)
        'all_random': []        # Tout aléatoire
    }
    
    print(f"\n🔬 Comparaison des modes d'initialisation ({n_runs} runs chacun)...")
    
    for mode in ['nn_plus_random', 'all_random']:
        mode_label = "NN + Random" if mode == 'nn_plus_random' else "All Random"
        print(f"\n   Testing mode: {mode_label}")
        
        for run in range(n_runs):
            start = time_module.time()
            
            best_solution = genetic_algorithm(
                inst=instance,
                pop_size=default_params.get('population_size', 50),
                tournament_k=default_params.get('tournament_size', 3),
                elitism=default_params.get('n_elite', 5),
                pc=0.8,
                pm=default_params.get('mutation_rate', 0.1),
                use_2opt=True,
                two_opt_prob=0.5,
                time_limit_sec=time_limit,
                verbose=False,
                seed=None,
                init_mode=mode  # <-- Paramètre clé
            )
            
            elapsed = time_module.time() - start
            
            results[mode].append({
                'cost': best_solution.cost,
                'time': elapsed,
                'routes': len(best_solution.routes)
            })
            
            print(f"      Run {run+1}/{n_runs}: Cost={best_solution.cost:.0f}, Time={elapsed:.1f}s")
    
    # Calculer les statistiques
    stats = {}
    for mode in ['nn_plus_random', 'all_random']:
        costs = [r['cost'] for r in results[mode]]
        times = [r['time'] for r in results[mode]]
        
        stats[mode] = {
            'mean_cost': sum(costs) / len(costs),
            'min_cost': min(costs),
            'max_cost': max(costs),
            'mean_time': sum(times) / len(times),
            'all_costs': costs
        }
    
    return results, stats


def print_banner():
    """Affiche la bannière du benchmark."""
    print("\n" + "="*80)
    print("🚀 BENCHMARK PROFESSIONNEL - ALGORITHME GÉNÉTIQUE CVRP".center(80))
    print("="*80)
    print()


def print_section(title):
    """Affiche un titre de section."""
    print(f"\n{'─'*80}")
    print(f"📊 {title}")
    print('─'*80)


def generate_visualizations(all_results, baseline_cost, target_optimum, 
                           timestamp, results_dir, init_comparison=None, combined_config=None):
    """
    Génère les visualisations du benchmark (7 à 9 selon les options).
    
    Args:
        all_results: Liste des résultats par paramètre
        baseline_cost: Coût du baseline
        target_optimum: Coût optimal connu (ou None)
        timestamp: Timestamp pour nommage des fichiers
        results_dir: Répertoire de sortie
        init_comparison: Tuple (results, stats) de comparaison des modes init (optionnel)
        combined_config: Dict avec les résultats de la config optimale combinée (optionnel)
    """
    print_section("Génération des Visualisations")
    
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        plot_dir = os.path.join(results_dir, f"benchmark_{timestamp}_plots")
        os.makedirs(plot_dir, exist_ok=True)
        
        print(f"📁 Dossier de visualisations: {plot_dir}")
        
        # 1. Histogrammes individuels (5 graphiques)
        print("\n🎨 Génération des histogrammes individuels...")
        for idx, param_data in enumerate(all_results, 1):
            param_name = param_data['param_name']
            results = param_data['results']
            
            # Trier par valeur de paramètre pour avoir un ordre logique sur l'axe X
            sorted_results = sorted(results, key=lambda x: x['value'])
            values = [r['value'] for r in sorted_results]
            costs = [r['cost'] for r in sorted_results]
            
            # Gradient de couleurs du meilleur au moins bon
            sorted_indices = np.argsort(costs)
            colors_array = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(costs)))
            colors_ordered = [None] * len(costs)
            for rank, idx_color in enumerate(sorted_indices):
                colors_ordered[idx_color] = colors_array[rank]
            
            plt.figure(figsize=(12, 6))
            bars = plt.bar(range(len(values)), costs, color=colors_ordered, alpha=0.8, 
                          edgecolor='black', linewidth=1.2)
            
            # Ajuster l'échelle Y pour zoomer sur la zone d'intérêt
            min_cost = min(costs)
            max_cost = max(costs)
            cost_range = max_cost - min_cost
            
            # Définir les limites avec une marge
            if target_optimum:
                # Inclure l'optimum dans le calcul
                y_min = min(min_cost, target_optimum) - cost_range * 0.15
                y_max = max_cost + cost_range * 0.1
            else:
                y_min = min_cost - cost_range * 0.15
                y_max = max_cost + cost_range * 0.1
            
            plt.ylim(y_min, y_max)
            
            plt.axhline(y=baseline_cost, color='r', linestyle='--',
                       label=f'Baseline ({baseline_cost:.0f})', linewidth=2, alpha=0.7)
            if target_optimum:
                plt.axhline(y=target_optimum, color='g', linestyle='--',
                           label=f'Optimal ({target_optimum})', linewidth=2, alpha=0.7)
            
            plt.xticks(range(len(values)), [str(v) for v in values], 
                      fontsize=10, rotation=45, ha='right')
            plt.xlabel(param_name, fontsize=12, fontweight='bold')
            plt.ylabel('Coût total', fontsize=12, fontweight='bold')
            plt.title(f'📊 Impact de {param_name} sur le coût', 
                     fontsize=14, fontweight='bold', pad=15)
            plt.grid(True, axis='y', alpha=0.3, linestyle='--')
            plt.legend(fontsize=10, loc='upper right', framealpha=0.9)
            plt.tight_layout()
            
            plot_path = os.path.join(plot_dir, f'{param_name}.png')
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"   ✓ [{idx}/5] {param_name}.png créé")
        
        # 2. Graphique comparatif 2x3
        print("\n🎨 Génération du graphique comparatif...")
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for idx, param_data in enumerate(all_results):
            if idx >= len(axes):
                break
                
            param_name = param_data['param_name']
            results = param_data['results']
            
            # Trier par valeur de paramètre pour avoir un ordre logique sur l'axe X
            sorted_results = sorted(results, key=lambda x: x['value'])
            values = [r['value'] for r in sorted_results]
            costs = [r['cost'] for r in sorted_results]
            
            # Trouver le meilleur coût
            min_cost = min(costs)
            best_idx = costs.index(min_cost)
            
            # Couleurs: vert pour le meilleur, gradient pour les autres
            colors = []
            for i, cost in enumerate(costs):
                if i == best_idx:
                    colors.append('limegreen')
                else:
                    ratio = (cost - min_cost) / (max(costs) - min_cost) if max(costs) > min_cost else 0
                    colors.append(plt.cm.RdYlGn_r(0.3 + ratio * 0.5))
            
            ax = axes[idx]
            x_pos = range(len(values))
            bars = ax.bar(x_pos, costs, color=colors, alpha=0.85, 
                         edgecolor='black', linewidth=1.2)
            
            # Ajuster l'échelle Y pour zoomer sur la zone d'intérêt
            max_cost = max(costs)
            cost_range = max_cost - min_cost
            
            # Définir les limites avec une marge
            if target_optimum:
                y_min = min(min_cost, target_optimum) - cost_range * 0.15
                y_max = max_cost + cost_range * 0.1
            else:
                y_min = min_cost - cost_range * 0.15
                y_max = max_cost + cost_range * 0.1
            
            ax.set_ylim(y_min, y_max)
            
            # Ligne de baseline
            ax.axhline(y=baseline_cost, color='red', linestyle='--', alpha=0.7, 
                      linewidth=2, label=f'Baseline: {baseline_cost:.0f}')
            
            # Marquer le meilleur avec une étoile
            ax.plot(best_idx, min_cost, marker='*', markersize=20, 
                   color='gold', markeredgecolor='black', markeredgewidth=2, zorder=10)
            
            # Configuration de l'axe
            ax.set_xticks(x_pos)
            ax.set_xticklabels([str(v) for v in values], fontsize=9, rotation=45, ha='right')
            ax.set_xlabel(param_name, fontsize=11, fontweight='bold')
            ax.set_ylabel('Coût total', fontsize=10, fontweight='bold')
            ax.set_title(f'📊 {param_name}', fontsize=12, fontweight='bold', pad=10)
            ax.grid(True, axis='y', alpha=0.3, linestyle='--')
            ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
            
            # Annoter le meilleur résultat
            improvement = ((baseline_cost - min_cost) / baseline_cost * 100)
            ax.text(best_idx, min_cost + 50, 
                   f'Meilleur\n{min_cost:.0f}\n({improvement:+.1f}%)',
                   ha='center', va='bottom', fontsize=8, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
        
        # Masquer les axes inutilisés
        for idx in range(len(all_results), len(axes)):
            axes[idx].set_visible(False)
        
        plt.suptitle('🔬 Benchmark - Comparaison des Paramètres\n' + 
                    '(Vert = Meilleur | ⭐ = Configuration optimale | Rouge = Moins bon)',
                    fontsize=15, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        comparison_path = os.path.join(plot_dir, 'parameter_comparison.png')
        plt.savefig(comparison_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print("   ✓ parameter_comparison.png créé")
        
        # 3. Top 10 avec médailles
        print("\n🎨 Génération du Top 10...")
        all_configs = []
        for param_data in all_results:
            param_name = param_data['param_name']
            for res in param_data['results']:
                all_configs.append({
                    'param': param_name,
                    'value': res['value'],
                    'cost': res['cost']
                })
        
        all_configs.sort(key=lambda x: x['cost'])
        top10 = all_configs[:min(10, len(all_configs))]
        
        plt.figure(figsize=(14, 8))
        labels = [f"{c['param']}=\n{c['value']}" for c in top10]
        costs = [c['cost'] for c in top10]
        
        # Gradient de couleurs du meilleur (vert) au moins bon (rouge)
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(top10)))
        
        # Créer l'histogramme vertical
        bars = plt.bar(range(len(top10)), costs, color=colors, alpha=0.8, 
                      edgecolor='black', linewidth=1.5)
        
        # Ajuster l'échelle Y pour zoomer sur la zone d'intérêt
        min_cost = min(costs)
        max_cost = max(costs)
        cost_range = max_cost - min_cost
        
        # Définir les limites avec une marge (plus large pour le Top 10)
        if target_optimum:
            y_min = min(min_cost, target_optimum) - cost_range * 0.2
            y_max = max_cost + cost_range * 0.15
        else:
            y_min = min_cost - cost_range * 0.2
            y_max = max_cost + cost_range * 0.15
        
        plt.ylim(y_min, y_max)
        
        plt.xticks(range(len(top10)), labels, fontsize=9, rotation=45, ha='right')
        plt.ylabel('Coût total', fontsize=12, fontweight='bold')
        plt.title('🏆 Top 10 des Meilleures Configurations', 
                 fontsize=14, fontweight='bold', pad=20)
        
        # Lignes de référence
        plt.axhline(y=baseline_cost, color='red', linestyle='--', linewidth=2, alpha=0.7,
                   label=f'Baseline: {baseline_cost:.0f}')
        if target_optimum:
            plt.axhline(y=target_optimum, color='green', linestyle='--', linewidth=2, alpha=0.7,
                       label=f'Optimal: {target_optimum}')
        
        # Annotations au-dessus des barres
        for i, (bar, cost) in enumerate(zip(bars, costs)):
            height = bar.get_height()
            if target_optimum:
                gap = ((cost - target_optimum) / target_optimum * 100)
                label = f'{cost:.0f}\n({gap:+.1f}%)'
            else:
                label = f'{cost:.0f}'
            
            plt.text(bar.get_x() + bar.get_width()/2., height + 100,
                    label, ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Ajouter des médailles pour le top 3
        if len(top10) > 0:
            plt.text(0, costs[0] - 200, '🥇', ha='center', va='top', fontsize=20)
        if len(top10) > 1:
            plt.text(1, costs[1] - 200, '🥈', ha='center', va='top', fontsize=20)
        if len(top10) > 2:
            plt.text(2, costs[2] - 200, '🥉', ha='center', va='top', fontsize=20)
        
        plt.legend(loc='upper right', fontsize=10, framealpha=0.9)
        plt.grid(True, axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        top10_path = os.path.join(plot_dir, 'top10_best_configs.png')
        plt.savefig(top10_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print("   ✓ top10_best_configs.png créé")
        
        print(f"\n✅ 7 visualisations créées dans: {plot_dir}")
        
        # 8. NOUVELLE: Comparaison modes d'initialisation (si disponible)
        if init_comparison:
            print("\n🎨 Génération de la comparaison des modes d'initialisation...")
            results_init, stats_init = init_comparison
            
            fig, axes = plt.subplots(1, 2, figsize=(16, 7))
            
            # Sous-graphe 1: Box plots des coûts
            ax1 = axes[0]
            data_to_plot = [
                stats_init['nn_plus_random']['all_costs'],
                stats_init['all_random']['all_costs']
            ]
            labels_box = ['NN + Random\n(Code actuel)', 'All Random\n(Aléatoire pur)']
            
            bp = ax1.boxplot(data_to_plot, labels=labels_box, patch_artist=True,
                            widths=0.6, showmeans=True)
            
            # Coloration des box plots
            colors_box = ['#4CAF50', '#FF9800']
            for patch, color in zip(bp['boxes'], colors_box):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
                patch.set_linewidth(2)
            
            for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
                plt.setp(bp[element], linewidth=2)
            
            ax1.set_ylabel('Coût de la Solution', fontsize=12, fontweight='bold')
            ax1.set_title('🎯 Distribution des Coûts par Mode d\'Initialisation', 
                         fontsize=14, fontweight='bold', pad=20)
            ax1.grid(True, axis='y', alpha=0.3, linestyle='--')
            
            # Ajouter l'optimum si disponible
            if target_optimum:
                ax1.axhline(y=target_optimum, color='red', linestyle='--', 
                           linewidth=2, alpha=0.7, label=f'★ Optimal: {target_optimum:.0f}')
                ax1.legend(loc='upper right', fontsize=10)
            
            # Annoter les moyennes
            for i, mode in enumerate(['nn_plus_random', 'all_random']):
                mean_cost = stats_init[mode]['mean_cost']
                ax1.text(i+1, mean_cost, f'\nMoyenne:\n{mean_cost:.0f}', 
                        ha='center', va='center', fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
            
            # Sous-graphe 2: Barres comparatives des statistiques
            ax2 = axes[1]
            
            modes = ['NN + Random', 'All Random']
            means = [stats_init['nn_plus_random']['mean_cost'], 
                    stats_init['all_random']['mean_cost']]
            mins = [stats_init['nn_plus_random']['min_cost'], 
                   stats_init['all_random']['min_cost']]
            maxs = [stats_init['nn_plus_random']['max_cost'], 
                   stats_init['all_random']['max_cost']]
            
            x_pos = np.arange(len(modes))
            width = 0.25
            
            bars1 = ax2.bar(x_pos - width, means, width, label='Moyenne', 
                           color='#2196F3', alpha=0.8, edgecolor='black', linewidth=1.5)
            bars2 = ax2.bar(x_pos, mins, width, label='Minimum', 
                           color='#4CAF50', alpha=0.8, edgecolor='black', linewidth=1.5)
            bars3 = ax2.bar(x_pos + width, maxs, width, label='Maximum', 
                           color='#F44336', alpha=0.8, edgecolor='black', linewidth=1.5)
            
            # Annoter les valeurs sur les barres
            for bars in [bars1, bars2, bars3]:
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.0f}',
                            ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            ax2.set_ylabel('Coût', fontsize=12, fontweight='bold')
            ax2.set_title('📊 Statistiques Comparatives', fontsize=14, fontweight='bold', pad=20)
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(modes)
            ax2.legend(loc='upper right', fontsize=10)
            ax2.grid(True, axis='y', alpha=0.3, linestyle='--')
            
            # Ajouter l'optimum si disponible
            if target_optimum:
                ax2.axhline(y=target_optimum, color='red', linestyle='--', 
                           linewidth=2, alpha=0.7)
            
            # Calculer et afficher la différence
            diff = stats_init['nn_plus_random']['mean_cost'] - stats_init['all_random']['mean_cost']
            diff_pct = (diff / stats_init['all_random']['mean_cost']) * 100
            
            winner = "NN + Random" if diff < 0 else "All Random"
            winner_emoji = "🥇" if diff < 0 else "🥈"
            
            fig.suptitle(f'🔬 Comparaison: Multi-Dépôt Aléatoire vs Multi-Dépôt Code\n' +
                        f'{winner_emoji} Gagnant: {winner} (différence: {abs(diff):.0f} coût, {abs(diff_pct):.2f}%)', 
                        fontsize=16, fontweight='bold', y=0.98)
            
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            
            init_comparison_path = os.path.join(plot_dir, 'init_modes_comparison.png')
            plt.savefig(init_comparison_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print("   ✓ init_modes_comparison.png créé")
            
            # 9. NOUVELLE: Graphique des GAPs (All Random vs Code Actuel vs Best Config/Combined)
            print("\n🎨 Génération du graphique comparatif des gaps...")
            
            # Utiliser soit la config combinée, soit la meilleure config individuelle
            if combined_config:
                # Utiliser la configuration optimale combinée
                best_overall_cost = combined_config['mean_cost']
                best_overall = {
                    'param': 'combined',
                    'value': 'optimized',
                    'cost': best_overall_cost,
                    'label': 'Best Combined\n(Meilleurs params)'
                }
                print(f"   Utilisation de la configuration optimale combinée: {best_overall_cost:.1f}")
            else:
                # Fallback: trouver la meilleure configuration individuelle
                best_overall_cost = float('inf')
                for param_data in all_results:
                    for res in param_data['results']:
                        if res['cost'] < best_overall_cost:
                            best_overall_cost = res['cost']
                            best_overall = {
                                'param': param_data['param_name'],
                                'value': res['value'],
                                'cost': res['cost'],
                                'label': f"Best Config\n({param_data['param_name']}={res['value']})"
                            }
                print(f"   Utilisation de la meilleure config individuelle: {best_overall_cost:.1f}")
            
            # Calculer les gaps par rapport à l'optimum
            gaps_data = {
                'method': ['All Random\n(Aléatoire pur)', 'NN + Random\n(Code actuel)', 
                          best_overall['label']],
                'costs': [
                    stats_init['all_random']['mean_cost'],
                    stats_init['nn_plus_random']['mean_cost'],
                    best_overall_cost
                ],
                'gaps': []
            }
            
            # Calculer les gaps en %
            if target_optimum:
                for cost in gaps_data['costs']:
                    gap = ((cost - target_optimum) / target_optimum) * 100
                    gaps_data['gaps'].append(gap)
            else:
                # Si pas d'optimum, utiliser le meilleur comme référence
                ref = best_overall_cost
                for cost in gaps_data['costs']:
                    gap = ((cost - ref) / ref) * 100
                    gaps_data['gaps'].append(gap)
            
            # Créer la visualisation
            fig, axes = plt.subplots(1, 2, figsize=(16, 7))
            
            # Sous-graphe 1: Barres des coûts
            ax1 = axes[0]
            x_pos = np.arange(len(gaps_data['method']))
            colors_cost = ['#FF9800', '#4CAF50', '#2196F3']  # Orange, Vert, Bleu
            
            bars = ax1.bar(x_pos, gaps_data['costs'], color=colors_cost, 
                          alpha=0.8, edgecolor='black', linewidth=2, width=0.6)
            
            # Annoter les valeurs sur les barres
            for i, (bar, cost) in enumerate(zip(bars, gaps_data['costs'])):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{cost:.0f}',
                        ha='center', va='bottom', fontsize=12, fontweight='bold')
                
                # Ajouter une étoile sur la meilleure
                if cost == best_overall_cost:
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 200,
                            '⭐', ha='center', va='bottom', fontsize=30)
            
            # Ligne d'optimum
            if target_optimum:
                ax1.axhline(y=target_optimum, color='red', linestyle='--', 
                           linewidth=2.5, alpha=0.8, label=f'★ Optimal: {target_optimum:.0f}')
                ax1.legend(loc='upper right', fontsize=11, framealpha=0.9)
            
            ax1.set_ylabel('Coût de la Solution', fontsize=13, fontweight='bold')
            ax1.set_title('💰 Coûts Absolus', fontsize=15, fontweight='bold', pad=20)
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(gaps_data['method'], fontsize=10)
            ax1.grid(True, axis='y', alpha=0.3, linestyle='--')
            
            # Ajuster Y pour zoomer sur la zone pertinente
            if target_optimum:
                min_cost = min(gaps_data['costs'] + [target_optimum])
                max_cost = max(gaps_data['costs'])
                cost_range = max_cost - min_cost
                ax1.set_ylim(min_cost - cost_range * 0.15, max_cost + cost_range * 0.15)
            
            # Sous-graphe 2: Barres des gaps
            ax2 = axes[1]
            colors_gap = []
            for gap in gaps_data['gaps']:
                if gap < 1.0:
                    colors_gap.append('#4CAF50')  # Vert: excellent
                elif gap < 3.0:
                    colors_gap.append('#8BC34A')  # Vert clair: bon
                elif gap < 5.0:
                    colors_gap.append('#FFC107')  # Jaune: moyen
                elif gap < 10.0:
                    colors_gap.append('#FF9800')  # Orange: faible
                else:
                    colors_gap.append('#F44336')  # Rouge: mauvais
            
            bars2 = ax2.bar(x_pos, gaps_data['gaps'], color=colors_gap, 
                           alpha=0.8, edgecolor='black', linewidth=2, width=0.6)
            
            # Annoter les valeurs des gaps
            for i, (bar, gap) in enumerate(zip(bars2, gaps_data['gaps'])):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{gap:+.2f}%',
                        ha='center', va='bottom', fontsize=12, fontweight='bold')
                
                # Ajouter médaille pour le meilleur
                if gap == min(gaps_data['gaps']):
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                            '🥇', ha='center', va='bottom', fontsize=25)
            
            ax2.axhline(y=0, color='red', linestyle='-', linewidth=2.5, alpha=0.8, 
                       label='Optimum (Gap = 0%)')
            ax2.set_ylabel('Gap vs Optimal (%)', fontsize=13, fontweight='bold')
            ax2.set_title('📊 Gaps Relatifs', fontsize=15, fontweight='bold', pad=20)
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(gaps_data['method'], fontsize=10)
            ax2.legend(loc='upper right', fontsize=11, framealpha=0.9)
            ax2.grid(True, axis='y', alpha=0.3, linestyle='--')
            
            # Calculer l'amélioration de Best Config vs All Random
            improvement_vs_random = stats_init['all_random']['mean_cost'] - best_overall_cost
            improvement_pct = (improvement_vs_random / stats_init['all_random']['mean_cost']) * 100
            
            # Calculer l'amélioration de Best Config vs NN+Random
            improvement_vs_nn = stats_init['nn_plus_random']['mean_cost'] - best_overall_cost
            improvement_pct_nn = (improvement_vs_nn / stats_init['nn_plus_random']['mean_cost']) * 100
            
            fig.suptitle(
                f'📈 Comparaison des Gaps: All Random vs Code Actuel vs Best Config\n' +
                f'🎯 Best Config améliore de {improvement_pct:.2f}% vs All Random | ' +
                f'{improvement_pct_nn:.2f}% vs NN+Random | Gap final: {gaps_data["gaps"][2]:+.2f}%',
                fontsize=15, fontweight='bold', y=0.98
            )
            
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            
            gaps_comparison_path = os.path.join(plot_dir, 'gaps_comparison.png')
            plt.savefig(gaps_comparison_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print("   ✓ gaps_comparison.png créé")
            print(f"\n✅ 9 visualisations créées dans: {plot_dir}")
        else:
            print(f"\n✅ 7 visualisations créées dans: {plot_dir}")
        
    except Exception as e:
        print(f"\n⚠️  Erreur lors de la génération des visualisations: {e}")
        import traceback
        traceback.print_exc()


def save_results(all_results, baseline_cost, target_optimum, instance, 
                default_params, extended_spaces, timestamp, results_dir):
    """
    Sauvegarde les résultats en JSON et CSV.
    
    Args:
        all_results: Liste des résultats par paramètre
        baseline_cost: Coût du baseline
        target_optimum: Coût optimal connu
        instance: Instance CVRP
        default_params: Paramètres par défaut
        extended_spaces: Grille de paramètres testés
        timestamp: Timestamp pour nommage
        results_dir: Répertoire de sortie
    """
    print_section("Sauvegarde des Résultats")
    
    # JSON
    json_path = os.path.join(results_dir, f"benchmark_{timestamp}.json")
    save_data = {
        'timestamp': timestamp,
        'instance': instance.name,
        'dimension': instance.dimension,
        'capacity': instance.capacity,
        'n_runs': 1,
        'baseline_cost': baseline_cost,
        'target_optimum': target_optimum,
        'default_params': default_params,
        'parameter_spaces': extended_spaces,
        'total_configs': sum(len(results['results']) for results in all_results),
        'results': all_results
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON sauvegardé: {json_path}")
    
    # CSV
    csv_path = os.path.join(results_dir, f"benchmark_{timestamp}.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['parameter', 'value', 'cost', 'time_sec', 'routes', 
                        'improvement_%', 'gap_%'])
        
        for param_data in all_results:
            param_name = param_data['param_name']
            for res in param_data['results']:
                improvement = ((baseline_cost - res['cost']) / baseline_cost) * 100
                gap = ((res['cost'] - target_optimum) / target_optimum) * 100 if target_optimum else None
                writer.writerow([
                    param_name, res['value'], res['cost'], 
                    res['time'], res['routes'], 
                    f"{improvement:.2f}", f"{gap:.2f}" if gap is not None else ""
                ])
    
    print(f"✅ CSV sauvegardé: {csv_path}")


def print_summary(all_results, baseline_cost, target_optimum, total_time, combined_config_cost=None):
    """
    Affiche le résumé final du benchmark.
    
    Args:
        all_results: Liste des résultats par paramètre
        baseline_cost: Coût du baseline
        target_optimum: Coût optimal connu
        total_time: Temps total d'exécution
        combined_config_cost: Coût de la configuration optimale combinée (optionnel)
    """
    print("\n" + "="*80)
    print("📊 RÉSUMÉ FINAL DU BENCHMARK".center(80))
    print("="*80)
    
    print(f"\n🎯 Baseline: {baseline_cost:.1f}")
    if target_optimum:
        baseline_gap = ((baseline_cost - target_optimum) / target_optimum) * 100
        print(f"🎯 Optimal connu: {target_optimum} (Gap baseline: {baseline_gap:+.2f}%)")
    
    print(f"\n⏱️  Temps total: {total_time/60:.1f} minutes")
    
    print(f"\n📈 Meilleurs résultats par paramètre:\n")
    
    for param_data in all_results:
        param_name = param_data['param_name']
        results = param_data['results']
        
        # Trouver le meilleur
        best = min(results, key=lambda x: x['cost'])
        improvement = ((baseline_cost - best['cost']) / baseline_cost) * 100
        
        gap_str = ""
        if target_optimum:
            gap = ((best['cost'] - target_optimum) / target_optimum) * 100
            gap_str = f" | Gap: {gap:+.2f}%"
        
        print(f"  • {param_name:20s} = {best['value']:6} → "
              f"Coût: {best['cost']:7.1f} | "
              f"Amélioration: {improvement:+.2f}%{gap_str}")
    
    # Top 3 global
    print(f"\n🏆 TOP 3 CONFIGURATIONS GLOBALES:\n")
    
    all_configs = []
    for param_data in all_results:
        param_name = param_data['param_name']
        for res in param_data['results']:
            all_configs.append({
                'param': param_name,
                'value': res['value'],
                'cost': res['cost'],
                'time': res['time']
            })
    
    all_configs.sort(key=lambda x: x['cost'])
    top3 = all_configs[:3]
    
    medals = ['🥇', '🥈', '🥉']
    for i, config in enumerate(top3):
        improvement = ((baseline_cost - config['cost']) / baseline_cost) * 100
        gap_str = ""
        if target_optimum:
            gap = ((config['cost'] - target_optimum) / target_optimum) * 100
            gap_str = f" | Gap: {gap:+.2f}%"
        
        print(f"  {medals[i]} #{i+1}: {config['param']}={config['value']} → "
              f"Coût: {config['cost']:.1f} | "
              f"Amélioration: {improvement:+.2f}%{gap_str}")
    
    # Afficher la config optimale combinée si disponible
    if combined_config_cost:
        print(f"\n🌟 CONFIGURATION OPTIMALE COMBINÉE:\n")
        improvement_combined = ((baseline_cost - combined_config_cost) / baseline_cost) * 100
        gap_str_combined = ""
        if target_optimum:
            gap_combined = ((combined_config_cost - target_optimum) / target_optimum) * 100
            gap_str_combined = f" | Gap: {gap_combined:+.2f}%"
        
        print(f"  ⭐ Meilleurs paramètres combinés → "
              f"Coût: {combined_config_cost:.1f} | "
              f"Amélioration: {improvement_combined:+.2f}%{gap_str_combined}")
        
        # Comparer avec le meilleur individuel
        best_individual = all_configs[0]['cost']
        diff = best_individual - combined_config_cost
        if diff > 0:
            print(f"  📈 {diff:.1f} coût de mieux que la meilleure config individuelle!")
        elif diff < 0:
            print(f"  📉 {abs(diff):.1f} coût de moins bien que la meilleure config individuelle")
        else:
            print(f"  ➡️  Identique à la meilleure config individuelle")
    
    print("\n" + "="*80)


def run_benchmark():
    """Fonction principale du benchmark."""
    start_total = time.time()
    
    print_banner()
    
    # Configuration
    instance_path = "data/instances/data.vrp"
    
    if not os.path.exists(instance_path):
        print(f"❌ Instance introuvable: {instance_path}")
        return
    
    # Charger l'instance
    print_section("Configuration")
    print(f"📂 Chargement de l'instance: {instance_path}")
    instance = load_cvrp_instance(instance_path)
    print(f"   Nom: {instance.name}")
    print(f"   Clients: {instance.dimension - 1}")
    print(f"   Capacité: {instance.capacity}")
    
    # Trouver l'optimum
    target_optimum = find_solution_for_instance(instance_path)
    if target_optimum:
        print(f"   🎯 Optimum connu: {target_optimum}")
    else:
        print(f"   ⚠️  Optimum inconnu (pas de comparaison de gap)")
    
    # Définir la grille ULTRA ÉTENDUE (150+ configurations)
    extended_spaces = {
        'population_size': [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100,
                           110, 120, 130, 140, 150, 160, 170, 180, 200, 220, 250, 280, 300, 350, 400],
        'n_elite': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 25, 28, 30, 35, 40],
        'mutation_rate': [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 
                         0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 
                         0.16, 0.17, 0.18, 0.19, 0.2, 0.22, 0.24, 0.26, 0.28, 0.3, 
                         0.32, 0.35, 0.38, 0.4, 0.45, 0.5],
        'tournament_size': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 25, 28, 30],
        'n_close': [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 25, 28, 30, 32, 35, 38, 40, 45, 50, 55, 60, 70, 80, 100]
    }
    
    # Paramètres par défaut (baseline)
    default_params = {
        'population_size': 50,
        'n_elite': 5,
        'mutation_rate': 0.1,
        'tournament_size': 3,
        'n_close': 10
    }
    
    # Calculer le baseline
    print_section("Calcul du Baseline")
    print(f"🔧 Paramètres par défaut: {default_params}")
    baseline_cost, baseline_time, baseline_routes = run_ga_single(
        instance, default_params, time_limit=60
    )
    print(f"   ✅ Coût baseline: {baseline_cost:.1f}")
    print(f"   ⏱️  Temps: {baseline_time:.1f}s")
    print(f"   🚛 Routes: {baseline_routes}")
    
    if target_optimum:
        gap = ((baseline_cost - target_optimum) / target_optimum) * 100
        print(f"   📊 Gap vs optimal: {gap:+.2f}%")
    
    # NOUVEAU: Comparaison des modes d'initialisation
    print_section("Comparaison des Modes d'Initialisation")
    print("🔬 Test: NN + Random (actuel) vs All Random (aléatoire pur)")
    init_results, init_stats = compare_init_modes(
        instance, default_params, n_runs=5, time_limit=60
    )
    
    # Afficher résumé de la comparaison
    print("\n📊 Résultats de la comparaison:")
    for mode in ['nn_plus_random', 'all_random']:
        mode_label = "NN + Random (actuel)" if mode == 'nn_plus_random' else "All Random"
        print(f"\n   {mode_label}:")
        print(f"      Moyenne: {init_stats[mode]['mean_cost']:.1f}")
        print(f"      Minimum: {init_stats[mode]['min_cost']:.0f}")
        print(f"      Maximum: {init_stats[mode]['max_cost']:.0f}")
        print(f"      Temps moyen: {init_stats[mode]['mean_time']:.1f}s")
    
    diff = init_stats['nn_plus_random']['mean_cost'] - init_stats['all_random']['mean_cost']
    diff_pct = (diff / init_stats['all_random']['mean_cost']) * 100
    winner = "NN + Random" if diff < 0 else "All Random"
    print(f"\n   🏆 Gagnant: {winner}")
    print(f"      Différence: {abs(diff):.1f} coût ({abs(diff_pct):.2f}%)")
    
    # Statistiques
    total_configs = sum(len(values) for values in extended_spaces.values())
    n_workers = multiprocessing.cpu_count()
    
    print_section("Configuration du Benchmark")
    print(f"  • Configurations à tester: {total_configs}")
    print(f"  • Runs par configuration: 1")
    print(f"  • Total d'exécutions GA: {total_configs}")
    print(f"  • Threads: {n_workers}")
    print(f"  • Temps limite par run: 60s")
    print(f"  • Durée estimée: ~{(total_configs * 60 / n_workers) / 60:.0f} minutes")
    
    confirm = input("\n⚠️  Lancer le benchmark ? (o/n): ")
    if confirm.lower() != 'o':
        print("\n❌ Benchmark annulé.")
        return
    
    # Lancer les tests
    all_results = []
    
    for param_name, values in extended_spaces.items():
        print_section(f"Test du paramètre: {param_name}")
        print(f"Valeurs à tester: {values}")
        
        param_results = []
        start_param = time.time()
        
        def test_single_value(value):
            """Teste une seule valeur de paramètre."""
            params = default_params.copy()
            params[param_name] = value
            
            cost, time_taken, n_routes = run_ga_single(instance, params, time_limit=60)
            
            return {
                'param': param_name,
                'value': value,
                'cost': cost,
                'time': time_taken,
                'routes': n_routes,
                'params': params
            }
        
        # Exécution parallèle
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = {executor.submit(test_single_value, val): val for val in values}
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                try:
                    result = future.result()
                    param_results.append(result)
                    
                    improvement = ((baseline_cost - result['cost']) / baseline_cost) * 100
                    
                    gap_str = ""
                    if target_optimum:
                        gap = ((result['cost'] - target_optimum) / target_optimum) * 100
                        gap_str = f" | Gap: {gap:+.2f}%"
                    
                    print(f"✓ [{completed}/{len(values)}] {param_name}={result['value']}: "
                          f"Coût={result['cost']:.0f} | "
                          f"Amélioration={improvement:+.2f}%{gap_str}")
                except Exception as e:
                    print(f"✗ Erreur pour {param_name}={futures[future]}: {e}")
        
        # Trier par coût
        param_results.sort(key=lambda x: x['cost'])
        all_results.append({
            'param_name': param_name,
            'results': param_results
        })
        
        # Afficher le meilleur
        best = param_results[0]
        improvement = ((baseline_cost - best['cost']) / baseline_cost) * 100
        
        elapsed = time.time() - start_param
        
        print(f"\n🏆 Meilleur pour {param_name}:")
        print(f"   Valeur: {best['value']}")
        print(f"   Coût: {best['cost']:.1f}")
        print(f"   Amélioration vs baseline: {improvement:+.2f}%")
        if target_optimum:
            gap = ((best['cost'] - target_optimum) / target_optimum) * 100
            print(f"   Gap vs optimal: {gap:+.2f}%")
        print(f"   ⏱️  Temps de test: {elapsed:.1f}s")
    
    # NOUVEAU: Tester la configuration optimale combinée
    print_section("Test de la Configuration Optimale Combinée")
    print("🔬 Création de la configuration avec les meilleurs paramètres trouvés...")
    
    # Extraire le meilleur de chaque paramètre
    optimal_combined_params = default_params.copy()
    
    for param_data in all_results:
        param_name = param_data['param_name']
        best_for_param = min(param_data['results'], key=lambda x: x['cost'])
        optimal_combined_params[param_name] = best_for_param['value']
        print(f"   • {param_name:20s} = {best_for_param['value']:6} (coût: {best_for_param['cost']:.1f})")
    
    print(f"\n🔧 Configuration optimale combinée: {optimal_combined_params}")
    print("🚀 Lancement de 5 runs pour validation...")
    
    # Tester la config combinée avec 5 runs pour robustesse
    combined_runs = []
    for run in range(5):
        print(f"   Run {run+1}/5...", end=" ", flush=True)
        cost, elapsed, routes = run_ga_single(instance, optimal_combined_params, time_limit=60)
        combined_runs.append({
            'cost': cost,
            'time': elapsed,
            'routes': routes
        })
        print(f"Coût={cost:.0f}, Temps={elapsed:.1f}s")
    
    # Calculer stats de la config combinée
    combined_costs = [r['cost'] for r in combined_runs]
    combined_best_cost = min(combined_costs)
    combined_mean_cost = sum(combined_costs) / len(combined_costs)
    combined_worst_cost = max(combined_costs)
    
    improvement_vs_baseline = ((baseline_cost - combined_mean_cost) / baseline_cost) * 100
    
    print(f"\n📊 Résultats de la configuration optimale combinée:")
    print(f"   Meilleur: {combined_best_cost:.1f}")
    print(f"   Moyenne:  {combined_mean_cost:.1f}")
    print(f"   Pire:     {combined_worst_cost:.1f}")
    print(f"   Amélioration vs baseline: {improvement_vs_baseline:+.2f}%")
    
    if target_optimum:
        combined_gap = ((combined_mean_cost - target_optimum) / target_optimum) * 100
        print(f"   Gap vs optimal (moyenne): {combined_gap:+.2f}%")
        combined_best_gap = ((combined_best_cost - target_optimum) / target_optimum) * 100
        print(f"   Gap vs optimal (meilleur): {combined_best_gap:+.2f}%")
    
    # Sauvegarder et visualiser
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = "results/benchmarks"
    os.makedirs(results_dir, exist_ok=True)
    
    save_results(all_results, baseline_cost, target_optimum, instance,
                default_params, extended_spaces, timestamp, results_dir)
    
    # Passer init_comparison ET combined_config aux visualisations
    generate_visualizations(all_results, baseline_cost, target_optimum,
                          timestamp, results_dir, 
                          init_comparison=(init_results, init_stats),
                          combined_config={
                              'params': optimal_combined_params,
                              'best_cost': combined_best_cost,
                              'mean_cost': combined_mean_cost,
                              'worst_cost': combined_worst_cost,
                              'all_costs': combined_costs
                          })
    
    # Résumé final
    total_time = time.time() - start_total
    print_summary(all_results, baseline_cost, target_optimum, total_time, 
                 combined_config_cost=combined_mean_cost)
    
    print(f"\n💾 Tous les résultats sauvegardés dans: {results_dir}/")
    print(f"📊 Visualisations disponibles dans: {results_dir}/benchmark_{timestamp}_plots/")
    print("\n✅ Benchmark terminé avec succès!")


if __name__ == "__main__":
    try:
        run_benchmark()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrompu par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
