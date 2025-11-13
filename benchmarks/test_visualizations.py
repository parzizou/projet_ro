#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de Génération de Visualisations
=====================================

Teste la génération des 7 types de graphiques du benchmark avec des données simulées.
"""

import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def test_visualizations():
    """Génère des exemples de visualisations pour validation."""
    
    print("\n" + "="*80)
    print("🎨 TEST DES VISUALISATIONS".center(80))
    print("="*80)
    
    # Données simulées
    baseline_cost = 28500
    target_optimum = 27591  # Optimum réel pour X-n101-k25
    
    # Simuler des résultats pour 5 paramètres
    all_results = [
        {
            'param_name': 'population_size',
            'results': [
                {'value': 20, 'cost': 29500, 'time': 60, 'gap': 28.8},
                {'value': 50, 'cost': 28200, 'time': 60, 'gap': 23.1},
                {'value': 100, 'cost': 27800, 'time': 60, 'gap': 21.4},
                {'value': 200, 'cost': 28900, 'time': 60, 'gap': 26.2},
            ]
        },
        {
            'param_name': 'n_elite',
            'results': [
                {'value': 2, 'cost': 29200, 'time': 60, 'gap': 27.5},
                {'value': 5, 'cost': 28100, 'time': 60, 'gap': 22.7},
                {'value': 10, 'cost': 27900, 'time': 60, 'gap': 21.8},
                {'value': 20, 'cost': 28600, 'time': 60, 'gap': 24.9},
            ]
        },
        {
            'param_name': 'mutation_rate',
            'results': [
                {'value': 0.01, 'cost': 29100, 'time': 60, 'gap': 27.1},
                {'value': 0.05, 'cost': 28300, 'time': 60, 'gap': 23.6},
                {'value': 0.1, 'cost': 27600, 'time': 60, 'gap': 20.5},
                {'value': 0.2, 'cost': 28400, 'time': 60, 'gap': 24.0},
                {'value': 0.3, 'cost': 29000, 'time': 60, 'gap': 26.6},
            ]
        },
        {
            'param_name': 'tournament_size',
            'results': [
                {'value': 2, 'cost': 29300, 'time': 60, 'gap': 27.9},
                {'value': 3, 'cost': 28200, 'time': 60, 'gap': 23.1},
                {'value': 5, 'cost': 27700, 'time': 60, 'gap': 20.9},
                {'value': 10, 'cost': 28500, 'time': 60, 'gap': 24.4},
            ]
        },
        {
            'param_name': 'n_close',
            'results': [
                {'value': 5, 'cost': 28900, 'time': 60, 'gap': 26.2},
                {'value': 10, 'cost': 28100, 'time': 60, 'gap': 22.7},
                {'value': 20, 'cost': 27500, 'time': 60, 'gap': 20.1},
                {'value': 40, 'cost': 28300, 'time': 60, 'gap': 23.6},
            ]
        },
    ]
    
    # Créer dossier de test
    test_dir = "test_visualizations"
    os.makedirs(test_dir, exist_ok=True)
    print(f"\n📁 Dossier de test: {test_dir}/")
    
    # 1. Histogrammes individuels
    print("\n🎨 Génération des histogrammes individuels...")
    for idx, param_data in enumerate(all_results, 1):
        param_name = param_data['param_name']
        results = param_data['results']
        
        # Trier par valeur de paramètre pour avoir un ordre logique sur l'axe X
        sorted_results = sorted(results, key=lambda x: x['value'])
        values = [r['value'] for r in sorted_results]
        costs = [r['cost'] for r in sorted_results]
        
        # Gradient de couleurs
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
            y_min = min(min_cost, target_optimum) - cost_range * 0.15
            y_max = max_cost + cost_range * 0.1
        else:
            y_min = min_cost - cost_range * 0.15
            y_max = max_cost + cost_range * 0.1
        
        plt.ylim(y_min, y_max)
        
        plt.axhline(y=baseline_cost, color='r', linestyle='--',
                   label=f'Baseline ({baseline_cost:.0f})', linewidth=2, alpha=0.7)
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
        
        plot_path = os.path.join(test_dir, f'{param_name}.png')
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
        
        min_cost = min(costs)
        best_idx = costs.index(min_cost)
        
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
        y_min = min(min_cost, target_optimum) - cost_range * 0.15
        y_max = max_cost + cost_range * 0.1
        ax.set_ylim(y_min, y_max)
        
        ax.axhline(y=baseline_cost, color='red', linestyle='--', alpha=0.7, 
                  linewidth=2, label=f'Baseline: {baseline_cost:.0f}')
        
        # Marquer le meilleur avec une étoile
        ax.plot(best_idx, min_cost, marker='*', markersize=20, 
               color='gold', markeredgecolor='black', markeredgewidth=2, zorder=10)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels([str(v) for v in values], fontsize=9, rotation=45, ha='right')
        ax.set_xlabel(param_name, fontsize=11, fontweight='bold')
        ax.set_ylabel('Coût total', fontsize=10, fontweight='bold')
        ax.set_title(f'📊 {param_name}', fontsize=12, fontweight='bold', pad=10)
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
        
        improvement = ((baseline_cost - min_cost) / baseline_cost * 100)
        ax.text(best_idx, min_cost + 200, 
               f'Meilleur\n{min_cost:.0f}\n({improvement:+.1f}%)',
               ha='center', va='bottom', fontsize=8, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
    
    axes[5].set_visible(False)
    
    plt.suptitle('🔬 Benchmark - Comparaison des Paramètres\n' + 
                '(Vert = Meilleur | ⭐ = Configuration optimale | Rouge = Moins bon)',
                fontsize=15, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    comparison_path = os.path.join(test_dir, 'parameter_comparison.png')
    plt.savefig(comparison_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print("   ✓ parameter_comparison.png créé")
    
    # 3. Top 10
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
    
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(top10)))
    
    bars = plt.bar(range(len(top10)), costs, color=colors, alpha=0.8, 
                  edgecolor='black', linewidth=1.5)
    
    # Ajuster l'échelle Y pour zoomer sur la zone d'intérêt
    min_cost = min(costs)
    max_cost = max(costs)
    cost_range = max_cost - min_cost
    
    # Définir les limites avec une marge (plus large pour le Top 10)
    y_min = min(min_cost, target_optimum) - cost_range * 0.2
    y_max = max_cost + cost_range * 0.15
    plt.ylim(y_min, y_max)
    
    plt.xticks(range(len(top10)), labels, fontsize=9, rotation=45, ha='right')
    plt.ylabel('Coût total', fontsize=12, fontweight='bold')
    plt.title('🏆 Top 10 des Meilleures Configurations', 
             fontsize=14, fontweight='bold', pad=20)
    
    plt.axhline(y=baseline_cost, color='red', linestyle='--', linewidth=2, alpha=0.7,
               label=f'Baseline: {baseline_cost:.0f}')
    plt.axhline(y=target_optimum, color='green', linestyle='--', linewidth=2, alpha=0.7,
               label=f'Optimal: {target_optimum}')
    
    for i, (bar, cost) in enumerate(zip(bars, costs)):
        height = bar.get_height()
        gap = ((cost - target_optimum) / target_optimum * 100)
        label = f'{cost:.0f}\n({gap:+.1f}%)'
        
        plt.text(bar.get_x() + bar.get_width()/2., height + 100,
                label, ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Médailles
    if len(top10) > 0:
        plt.text(0, costs[0] - 200, '🥇', ha='center', va='top', fontsize=20)
    if len(top10) > 1:
        plt.text(1, costs[1] - 200, '🥈', ha='center', va='top', fontsize=20)
    if len(top10) > 2:
        plt.text(2, costs[2] - 200, '🥉', ha='center', va='top', fontsize=20)
    
    plt.legend(loc='upper right', fontsize=10, framealpha=0.9)
    plt.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    top10_path = os.path.join(test_dir, 'top10_best_configs.png')
    plt.savefig(top10_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print("   ✓ top10_best_configs.png créé")
    
    # 8. NOUVEAU: Test de comparaison des modes d'initialisation
    print("\n🎨 Génération de la comparaison des modes d'initialisation...")
    
    # Simuler des résultats de comparaison
    init_results = {
        'nn_plus_random': [
            {'cost': 27800, 'time': 58.5, 'routes': 25},
            {'cost': 27950, 'time': 59.2, 'routes': 25},
            {'cost': 27720, 'time': 57.8, 'routes': 25},
            {'cost': 27890, 'time': 58.9, 'routes': 25},
            {'cost': 27840, 'time': 58.3, 'routes': 25},
        ],
        'all_random': [
            {'cost': 28100, 'time': 59.5, 'routes': 25},
            {'cost': 28250, 'time': 60.1, 'routes': 26},
            {'cost': 28030, 'time': 59.8, 'routes': 25},
            {'cost': 28180, 'time': 59.7, 'routes': 26},
            {'cost': 28090, 'time': 60.0, 'routes': 25},
        ]
    }
    
    # Calculer les statistiques
    init_stats = {}
    for mode in ['nn_plus_random', 'all_random']:
        costs = [r['cost'] for r in init_results[mode]]
        times = [r['time'] for r in init_results[mode]]
        
        init_stats[mode] = {
            'mean_cost': sum(costs) / len(costs),
            'min_cost': min(costs),
            'max_cost': max(costs),
            'mean_time': sum(times) / len(times),
            'all_costs': costs
        }
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Sous-graphe 1: Box plots des coûts
    ax1 = axes[0]
    data_to_plot = [
        init_stats['nn_plus_random']['all_costs'],
        init_stats['all_random']['all_costs']
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
    
    # Ajouter l'optimum
    ax1.axhline(y=target_optimum, color='red', linestyle='--', 
               linewidth=2, alpha=0.7, label=f'★ Optimal: {target_optimum:.0f}')
    ax1.legend(loc='upper right', fontsize=10)
    
    # Annoter les moyennes
    for i, mode in enumerate(['nn_plus_random', 'all_random']):
        mean_cost = init_stats[mode]['mean_cost']
        ax1.text(i+1, mean_cost, f'\nMoyenne:\n{mean_cost:.0f}', 
                ha='center', va='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    # Sous-graphe 2: Barres comparatives des statistiques
    ax2 = axes[1]
    
    modes = ['NN + Random', 'All Random']
    means = [init_stats['nn_plus_random']['mean_cost'], 
            init_stats['all_random']['mean_cost']]
    mins = [init_stats['nn_plus_random']['min_cost'], 
           init_stats['all_random']['min_cost']]
    maxs = [init_stats['nn_plus_random']['max_cost'], 
           init_stats['all_random']['max_cost']]
    
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
    
    # Ajouter l'optimum
    ax2.axhline(y=target_optimum, color='red', linestyle='--', 
               linewidth=2, alpha=0.7)
    
    # Calculer et afficher la différence
    diff = init_stats['nn_plus_random']['mean_cost'] - init_stats['all_random']['mean_cost']
    diff_pct = (diff / init_stats['all_random']['mean_cost']) * 100
    
    winner = "NN + Random" if diff < 0 else "All Random"
    winner_emoji = "🥇" if diff < 0 else "🥈"
    
    fig.suptitle(f'🔬 Comparaison: Multi-Dépôt Aléatoire vs Multi-Dépôt Code\n' +
                f'{winner_emoji} Gagnant: {winner} (différence: {abs(diff):.0f} coût, {abs(diff_pct):.2f}%)', 
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    init_comparison_path = os.path.join(test_dir, 'init_modes_comparison.png')
    plt.savefig(init_comparison_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print("   ✓ init_modes_comparison.png créé")
    
    # 9. NOUVEAU: Graphique des GAPs (All Random vs Code Actuel vs Best Config)
    print("\n🎨 Génération du graphique comparatif des gaps...")
    
    # Simuler la meilleure configuration trouvée
    best_overall = {
        'param': 'mutation_rate',
        'value': 0.08,
        'cost': 27650
    }
    
    # Calculer les gaps par rapport à l'optimum
    gaps_data = {
        'method': ['All Random\n(Aléatoire pur)', 'NN + Random\n(Code actuel)', 
                  f"Best Config\n({best_overall['param']}={best_overall['value']})"],
        'costs': [
            init_stats['all_random']['mean_cost'],
            init_stats['nn_plus_random']['mean_cost'],
            best_overall['cost']
        ],
        'gaps': []
    }
    
    # Calculer les gaps en %
    for cost in gaps_data['costs']:
        gap = ((cost - target_optimum) / target_optimum) * 100
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
        if cost == best_overall['cost']:
            ax1.text(bar.get_x() + bar.get_width()/2., height + 200,
                    '⭐', ha='center', va='bottom', fontsize=30)
    
    # Ligne d'optimum
    ax1.axhline(y=target_optimum, color='red', linestyle='--', 
               linewidth=2.5, alpha=0.8, label=f'★ Optimal: {target_optimum:.0f}')
    ax1.legend(loc='upper right', fontsize=11, framealpha=0.9)
    
    ax1.set_ylabel('Coût de la Solution', fontsize=13, fontweight='bold')
    ax1.set_title('💰 Coûts Absolus', fontsize=15, fontweight='bold', pad=20)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(gaps_data['method'], fontsize=10)
    ax1.grid(True, axis='y', alpha=0.3, linestyle='--')
    
    # Ajuster Y pour zoomer sur la zone pertinente
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
    improvement_vs_random = init_stats['all_random']['mean_cost'] - best_overall['cost']
    improvement_pct = (improvement_vs_random / init_stats['all_random']['mean_cost']) * 100
    
    # Calculer l'amélioration de Best Config vs NN+Random
    improvement_vs_nn = init_stats['nn_plus_random']['mean_cost'] - best_overall['cost']
    improvement_pct_nn = (improvement_vs_nn / init_stats['nn_plus_random']['mean_cost']) * 100
    
    fig.suptitle(
        f'📈 Comparaison des Gaps: All Random vs Code Actuel vs Best Config\n' +
        f'🎯 Best Config améliore de {improvement_pct:.2f}% vs All Random | ' +
        f'{improvement_pct_nn:.2f}% vs NN+Random | Gap final: {gaps_data["gaps"][2]:+.2f}%',
        fontsize=15, fontweight='bold', y=0.98
    )
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    gaps_comparison_path = os.path.join(test_dir, 'gaps_comparison.png')
    plt.savefig(gaps_comparison_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print("   ✓ gaps_comparison.png créé")
    
    print("\n" + "="*80)
    print(f"✅ 9 visualisations de test créées dans: {test_dir}/")
    print("="*80)
    print("\n📂 Fichiers générés:")
    for filename in sorted(os.listdir(test_dir)):
        if filename.endswith('.png'):
            filepath = os.path.join(test_dir, filename)
            size = os.path.getsize(filepath)
            print(f"   ✓ {filename} ({size/1024:.1f} KB)")
    print()

if __name__ == "__main__":
    try:
        test_visualizations()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
