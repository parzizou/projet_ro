#!/usr/bin/env python3
"""
Test direct du multi-threading sur une configuration.
"""
import sys
import time
import os

sys.path.append('src')
from src.optimization.quick_test import test_configuration

print("🚀 TEST DIRECT DU MULTI-THREADING")
print("=" * 50)

# Configuration de test ultra-rapide
config = {
    'name': 'Test Multi-Threading Direct',
    'pop_size': 30,          # Population réduite
    'tournament_k': 3,
    'elitism': 2,
    'pc': 0.9,
    'pm': 0.2,
    'use_2opt': False,       # Pas de 2-opt pour aller vite
    'two_opt_prob': 0.0,
    'time_limit': 3.0,       # Seulement 3 secondes par run
    'generations': 500       # Peu de générations
}

instance_path = "data/instances/data.vrp"
num_runs = 4  # 4 runs pour voir la parallélisation

print(f"Configuration: {config['name']}")
print(f"Runs: {num_runs}")
print(f"Durée par run: {config['time_limit']}s")
print(f"CPU cores: {os.cpu_count()}")

# Test avec multi-threading
print(f"\n🔥 TEST AVEC {os.cpu_count()} THREADS:")
start_time = time.time()
result = test_configuration(instance_path, config, num_runs=num_runs, max_workers=os.cpu_count())
total_time_multi = time.time() - start_time

print(f"\n⏱️  RÉSULTAT:")
print(f"Temps total multi-threadé: {total_time_multi:.1f}s")
print(f"Temps théorique séquentiel: {num_runs * config['time_limit']:.1f}s")
print(f"Accélération: {(num_runs * config['time_limit']) / total_time_multi:.2f}x")

if result:
    print(f"Coût moyen: {result['cost_mean']:.1f}")
    print(f"Runs valides: {result['num_runs']}")
    print("✅ Multi-threading fonctionnel !")
else:
    print("❌ Aucun résultat valide")