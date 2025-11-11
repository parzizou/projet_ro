# -*- coding: utf-8 -*-
"""
exemple_multithreading.py
Exemples pratiques d'utilisation du multi-threading.
"""

from src.optimization.ga_parameter_analyzer import GAParameterAnalyzer

# ============================================================================
# EXEMPLE 1: Utilisation par défaut (automatique)
# ============================================================================

print("EXEMPLE 1: Mode automatique (recommandé)")
print("-" * 50)

analyzer = GAParameterAnalyzer('data/instances/data.vrp', n_runs=5)

# Par défaut, max_workers=None utilise automatiquement tous les cores
analyzer.test_individual_parameters(
    time_limit=30.0,
    generations=20000
    # max_workers=None (par défaut) → Utilise ~16 workers sur votre machine
)

print("✅ Les tests s'exécutent automatiquement en parallèle!")
print("   Python détecte automatiquement vos 12 cores")


# ============================================================================
# EXEMPLE 2: Spécifier le nombre de workers
# ============================================================================

print("\n\nEXEMPLE 2: Contrôle manuel du nombre de workers")
print("-" * 50)

# Utiliser exactement 12 workers (1 par core)
analyzer.test_individual_parameters(
    max_workers=12,
    time_limit=30.0,
    generations=20000
)

print("✅ Utilisation de 12 workers (1 par core)")


# ============================================================================
# EXEMPLE 3: Mode économique (laisser des ressources libres)
# ============================================================================

print("\n\nEXEMPLE 3: Mode économique")
print("-" * 50)

# Utiliser seulement 6 workers pour laisser 6 cores libres
analyzer.test_individual_parameters(
    max_workers=6,
    time_limit=30.0,
    generations=20000
)

print("✅ Utilisation de 6 workers seulement")
print("   Laisse 6 cores libres pour d'autres tâches")


# ============================================================================
# EXEMPLE 4: Mode agressif (maximiser l'utilisation)
# ============================================================================

print("\n\nEXEMPLE 4: Mode agressif (utilisation maximale)")
print("-" * 50)

# Augmenter n_runs pour correspondre au nombre de cores
analyzer = GAParameterAnalyzer('data/instances/data.vrp', n_runs=12)

analyzer.test_individual_parameters(
    num_runs=12,        # 12 répétitions par config
    max_workers=12,     # 12 workers en parallèle
    time_limit=30.0,
    generations=20000
)

print("✅ Utilisation maximale: 12 runs en parallèle sur 12 cores!")
print("   100% d'utilisation CPU pendant les tests")


# ============================================================================
# EXEMPLE 5: Tester différentes stratégies
# ============================================================================

print("\n\nEXEMPLE 5: Comparaison de stratégies")
print("-" * 50)

import time

strategies = [
    (1, "Séquentiel (1 worker)"),
    (4, "Modéré (4 workers)"),
    (8, "Agressif (8 workers)"),
    (12, "Maximum (12 workers)"),
]

analyzer = GAParameterAnalyzer('data/instances/data.vrp', n_runs=5)

for workers, description in strategies:
    print(f"\nTest avec {description}...")
    
    start = time.time()
    costs, _ = analyzer._run_multiple_tests(
        analyzer.default_params,
        num_runs=5,
        time_limit=10.0,
        generations=5000,
        max_workers=workers
    )
    elapsed = time.time() - start
    
    print(f"  Temps: {elapsed:.1f}s")
    print(f"  Coût moyen: {sum(costs)/len(costs):.1f}")


# ============================================================================
# EXEMPLE 6: Configuration optimale pour analyse complète
# ============================================================================

print("\n\nEXEMPLE 6: Configuration optimale pour analyse complète")
print("-" * 50)

analyzer = GAParameterAnalyzer(
    'data/instances/data.vrp',
    n_runs=10,  # Plus de runs pour plus de précision
    target_optimum=20000  # Si vous connaissez l'optimum
)

# Tests individuels avec utilisation maximale
analyzer.test_individual_parameters(
    num_runs=10,          # 10 répétitions (plus fiable)
    max_workers=12,       # Tous les cores
    time_limit=45.0,      # Plus de temps pour converger
    generations=30000     # Plus de générations
)

# Combinaisons avec plus de tests
analyzer.find_best_combinations(
    top_n_per_param=3,    # Top 3 de chaque paramètre
    n_combinations=20,    # Tester 20 combinaisons
    combination_runs=10,  # 10 runs par combinaison
    max_workers=12,       # Tous les cores
    time_limit=60.0,      # Encore plus de temps
    generations=40000     # Maximum de générations
)

print("✅ Configuration optimale pour résultats de haute qualité")
print("   Utilisation: ~3-4 heures sur 12 cores")
print("   (vs ~48 heures en séquentiel)")


# ============================================================================
# CONSEILS
# ============================================================================

print("\n\n" + "="*70)
print("💡 CONSEILS D'UTILISATION".center(70))
print("="*70)

print("""
1. Par défaut (max_workers=None): RECOMMANDÉ
   → Python gère automatiquement
   → Utilise ~16 workers sur votre machine 12 cores

2. Mode standard (max_workers=12):
   → 1 worker par core
   → Utilisation équilibrée

3. Mode économique (max_workers=4-6):
   → Laisse des ressources pour autre chose
   → Bon si vous travaillez pendant les tests

4. Mode agressif (max_workers=12, n_runs=12):
   → Utilisation maximale
   → Lancez la nuit ou quand vous ne travaillez pas

5. Monitoring:
   → Ouvrez le Gestionnaire des tâches
   → Regardez l'onglet Performance → CPU
   → Vous verrez tous les cores à 100% !

ATTENTION:
- Plus de workers = plus de RAM nécessaire
- Chaque worker charge l'instance en mémoire
- 12 workers ≈ 12 × taille de l'instance en RAM
""")

print("="*70)
