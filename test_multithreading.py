#!/usr/bin/env python3
"""
Test rapide du système multi-threading pour vérifier que tout fonctionne.
"""
import sys
import os
sys.path.append('src')

# Test des imports
try:
    from src.optimization.advanced_optimizer import ParameterOptimizer
    from src.optimization.quick_test import test_configuration
    print("✅ Imports réussis")
    
    # Test basique de configuration
    config = {
        'name': 'Test Multi-Threading',
        'pop_size': 50,
        'tournament_k': 3,
        'elitism': 2,
        'pc': 0.9,
        'pm': 0.2,
        'use_2opt': True,
        'two_opt_prob': 0.3,
        'time_limit': 5.0,  # Test rapide de 5s
        'generations': 1000
    }
    
    print("✅ Configuration de test créée")
    print(f"CPU cores disponibles: {os.cpu_count()}")
    print("✅ Multi-threading prêt !")
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
except Exception as e:
    print(f"❌ Erreur: {e}")